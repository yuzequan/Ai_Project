"""综合评分引擎。

职责：
- 从数据库读取权重配置（先查询 AlertConfig/BehaviorRule，若无则使用默认值）
- 按 session_id 依次调用四个评分器
- 加权计算 overall_score
- 将结果写入 evaluation_results 表
- 返回完整的 EvaluationResult 对象
"""

import logging
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LiveSession, BehaviorRule, EvaluationResult
from app.services.attendance_scorer import calculate_attendance_score
from app.services.professionalism_scorer import calculate_professionalism_score
from app.services.engagement_scorer import calculate_engagement_score
from app.services.software_scorer import calculate_software_score

logger = logging.getLogger(__name__)

# 默认权重（当数据库中无配置时使用）
DEFAULT_WEIGHTS = {
    "attendance": 0.20,
    "professionalism": 0.40,
    "engagement": 0.20,
    "software_skill": 0.20,
}


def _normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """对权重进行归一化，确保总和为 1.0。"""
    total = sum(weights.values())
    if total <= 0:
        return DEFAULT_WEIGHTS.copy()
    return {k: v / total for k, v in weights.items()}


async def _get_weights_from_db(db: AsyncSession) -> Dict[str, float]:
    """从数据库读取权重配置。

    优先读取 BehaviorRule 表中各维度规则的 weight 字段。
    若某维度缺失，则使用 DEFAULT_WEIGHTS 补充。
    最后进行归一化。
    """
    result = await db.execute(select(BehaviorRule))
    rules = result.scalars().all()

    weights: Dict[str, float] = {}
    for rule in rules:
        if rule.weight is None:
            continue
        rule_type_val = (
            rule.rule_type.value
            if hasattr(rule.rule_type, "value")
            else str(rule.rule_type)
        )
        # 支持 weight 以百分比（如 20）或小数（如 0.2）存储
        w = float(rule.weight)
        if w > 1:
            w = w / 100.0
        weights[rule_type_val] = w

    # 映射 software_usage -> software_skill
    if "software_usage" in weights and "software_skill" not in weights:
        weights["software_skill"] = weights.pop("software_usage")

    # 补充缺失维度的默认值
    for key, default_value in DEFAULT_WEIGHTS.items():
        if key not in weights:
            weights[key] = default_value

    return _normalize_weights(weights)


class EvaluationEngine:
    """综合评分引擎，负责编排各维度评分并持久化结果。"""

    @staticmethod
    async def evaluate_session(
        db: AsyncSession, session_id: int
    ) -> EvaluationResult:
        """对指定直播会话进行综合评分并写入/更新数据库。

        Args:
            db: 异步 SQLAlchemy 会话。
            session_id: 直播会话 ID。

        Returns:
            写入数据库后的 EvaluationResult 对象。

        Raises:
            ValueError: 当 session_id 对应的 LiveSession 不存在时。
        """
        # 校验 session 存在性
        result = await db.execute(
            select(LiveSession).where(LiveSession.id == session_id)
        )
        live_session = result.scalar_one_or_none()
        if not live_session:
            raise ValueError(f"LiveSession not found: {session_id}")

        # 读取权重配置
        weights = await _get_weights_from_db(db)

        # 依次调用四个评分器
        attendance_score, attendance_details = await calculate_attendance_score(
            db, session_id
        )
        professionalism_score, professionalism_details = await calculate_professionalism_score(
            db, session_id
        )
        engagement_score, engagement_details = await calculate_engagement_score(
            db, session_id
        )
        software_score, software_details = await calculate_software_score(
            db, session_id
        )

        # 加权计算综合得分
        overall_score = (
            attendance_score * weights.get("attendance", 0.20)
            + professionalism_score * weights.get("professionalism", 0.40)
            + engagement_score * weights.get("engagement", 0.20)
            + software_score * weights.get("software_skill", 0.20)
        )
        overall_score = round(max(0.0, min(100.0, overall_score)), 2)

        # 组装 details JSON
        details: Dict[str, Any] = {
            "weights": weights,
            "attendance": {
                "score": attendance_score,
                "details": attendance_details,
            },
            "professionalism": {
                "score": professionalism_score,
                "details": professionalism_details,
            },
            "engagement": {
                "score": engagement_score,
                "details": engagement_details,
            },
            "software_skill": {
                "score": software_score,
                "details": software_details,
            },
        }

        # 查询是否已存在评分记录
        result = await db.execute(
            select(EvaluationResult).where(EvaluationResult.session_id == session_id)
        )
        eval_result = result.scalar_one_or_none()

        now = datetime.utcnow()
        if eval_result:
            # 更新已有记录
            eval_result.overall_score = overall_score
            eval_result.attendance_score = attendance_score
            eval_result.professionalism_score = professionalism_score
            eval_result.engagement_score = engagement_score
            eval_result.software_skill_score = software_score
            eval_result.details = details
            eval_result.evaluated_at = now
            eval_result.status = "completed"
        else:
            # 新建记录
            eval_result = EvaluationResult(
                session_id=session_id,
                overall_score=overall_score,
                attendance_score=attendance_score,
                professionalism_score=professionalism_score,
                engagement_score=engagement_score,
                software_skill_score=software_score,
                details=details,
                evaluated_at=now,
                status="completed",
            )
            db.add(eval_result)

        await db.commit()
        await db.refresh(eval_result)

        logger.info(
            "Evaluation completed for session %s: overall_score=%s, "
            "attendance=%s, professionalism=%s, engagement=%s, software=%s",
            session_id,
            overall_score,
            attendance_score,
            professionalism_score,
            engagement_score,
            software_score,
        )

        return eval_result
