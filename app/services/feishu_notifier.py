"""飞书通知服务。

通过飞书机器人 Webhook 发送低分预警消息卡片。
支持指数退避重试机制。
"""

import asyncio
import logging
from typing import Dict, Any, Optional

import httpx

from app.models import LiveSession, EvaluationResult, AlertConfig

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 2  # 指数退避基数


class FeishuNotifier:
    """飞书通知服务，负责构造并发送 AI 监课预警卡片。"""

    @staticmethod
    async def send_low_score_alert(
        session: LiveSession,
        evaluation_result: EvaluationResult,
        alert_config: AlertConfig,
    ) -> Dict[str, Any]:
        """发送低分预警到飞书群。

        Args:
            session: 直播会话对象，需包含 course_id / teacher_id，
                     可选 course_name / teacher_name。
            evaluation_result: 评分结果对象。
            alert_config: 告警配置对象，需包含 feishu_webhook。

        Returns:
            {"success": bool, "response": Any, "attempts": int}
        """
        webhook_url = alert_config.feishu_webhook
        if not webhook_url:
            logger.warning(
                "Feishu webhook URL is empty for alert_config id=%s", alert_config.id
            )
            return {
                "success": False,
                "response": "Webhook URL is empty",
                "attempts": 0,
            }

        # 获取课程名称和老师姓名（优先从对象属性读取，否则使用占位符）
        course_name = getattr(session, "course_name", None) or f"课程-{session.course_id}"
        teacher_name = getattr(session, "teacher_name", None) or f"老师-{session.teacher_id}"

        # 生成低分原因简述
        low_score_reasons: list[str] = []
        thresholds = {
            "出勤": (evaluation_result.attendance_score, 60),
            "专业度": (evaluation_result.professionalism_score, 60),
            "活跃度": (evaluation_result.engagement_score, 60),
            "软件熟练度": (evaluation_result.software_skill_score, 60),
        }
        for dim_name, (score, threshold) in thresholds.items():
            if score is not None and score < threshold:
                low_score_reasons.append(f"{dim_name}得分较低（{score}分）")

        reason_text = (
            "；".join(low_score_reasons)
            if low_score_reasons
            else f"综合得分（{evaluation_result.overall_score}）低于预警阈值（{alert_config.threshold}）"
        )

        # 构造飞书消息卡片（interactive 类型）
        card_payload = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "AI监课预警",
                    },
                    "template": "red",
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": (
                                f"**课程名称：** {course_name}\n"
                                f"**老师姓名：** {teacher_name}\n"
                                f"**综合得分：** {evaluation_result.overall_score}"
                            ),
                        },
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": (
                                "**各维度得分：**\n"
                                f"- 出勤：{evaluation_result.attendance_score}\n"
                                f"- 专业度：{evaluation_result.professionalism_score}\n"
                                f"- 活跃度：{evaluation_result.engagement_score}\n"
                                f"- 软件熟练度：{evaluation_result.software_skill_score}"
                            ),
                        },
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**低分原因：** {reason_text}",
                        },
                    },
                ],
            },
        }

        last_exception: Optional[Exception] = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(webhook_url, json=card_payload)
                    response.raise_for_status()
                    resp_data = response.json()

                # 飞书 webhook 返回体通常包含 code 字段，code == 0 表示成功
                success = True
                if isinstance(resp_data, dict) and resp_data.get("code") != 0:
                    success = False
                    logger.warning(
                        "Feishu API returned error code: %s, msg: %s",
                        resp_data.get("code"),
                        resp_data.get("msg"),
                    )

                return {
                    "success": success,
                    "response": resp_data,
                    "attempts": attempt,
                }

            except Exception as exc:
                last_exception = exc
                logger.warning(
                    "Feishu alert send failed (attempt %s/%s): %s",
                    attempt,
                    MAX_RETRIES,
                    exc,
                )
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(BACKOFF_BASE_SECONDS ** attempt)

        logger.error(
            "Feishu alert send failed after %s attempts: %s",
            MAX_RETRIES,
            last_exception,
        )
        return {
            "success": False,
            "response": str(last_exception) if last_exception else "Unknown error",
            "attempts": MAX_RETRIES,
        }
