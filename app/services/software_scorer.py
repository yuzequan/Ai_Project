"""软件熟练度评分引擎。

评分规则：
- 屏幕共享时长：从 behavior_rules condition 读取 min_share_time（默认 5 分钟），
  若实际共享时长 >= 课程时长 * 80% 得 40 分，否则按比例
- 拉人上麦：学生 join 事件 >= 1 次得 20 分
- 异常事件：若共享时长为 0 或极短（<1 分钟）扣 30 分；
  若学生无法加入（无学生 join 事件）扣 10 分
- 若无相关数据，默认给 70 分并标记"数据不足"
"""

import logging
from typing import Tuple, Dict, Any, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LiveSession, MemberEvent, BehaviorRule, RuleType, UserRole, EventType

logger = logging.getLogger(__name__)

DEFAULT_MIN_SHARE_TIME = 5.0  # 分钟


async def calculate_software_score(
    db: AsyncSession, session_id: int
) -> Tuple[int, Dict[str, Any]]:
    """计算软件熟练度评分。

    Args:
        db: 异步 SQLAlchemy 会话。
        session_id: 直播会话 ID。

    Returns:
        (score, details)
        - score: 0-100 的整数。
        - details: 包含各子项得分的详细信息。
    """
    # 获取直播 session
    result = await db.execute(select(LiveSession).where(LiveSession.id == session_id))
    live_session: Optional[LiveSession] = result.scalar_one_or_none()
    if not live_session:
        logger.warning("LiveSession not found: %s", session_id)
        return 0, {"error": "Session not found"}

    # 读取 software_usage 规则配置
    result = await db.execute(
        select(BehaviorRule).where(BehaviorRule.rule_type == RuleType.software_usage)
    )
    software_rules = result.scalars().all()

    min_share_time = DEFAULT_MIN_SHARE_TIME
    for rule in software_rules:
        condition = rule.condition or {}
        if "min_share_time" in condition:
            try:
                min_share_time = float(condition["min_share_time"])
            except (TypeError, ValueError):
                min_share_time = DEFAULT_MIN_SHARE_TIME
            break

    # 计算课程时长（分钟）
    course_duration_minutes = 0.0
    if live_session.scheduled_start and live_session.scheduled_end:
        course_duration_minutes = (
            live_session.scheduled_end - live_session.scheduled_start
        ).total_seconds() / 60

    # 尝试获取屏幕共享时长（分钟）
    # 当前模型未定义该字段，优先从 session 动态属性或 extra_data 获取
    screen_share_duration: Optional[float] = None
    if hasattr(live_session, "screen_share_duration"):
        raw = getattr(live_session, "screen_share_duration")
        if raw is not None:
            try:
                screen_share_duration = float(raw)
            except (TypeError, ValueError):
                screen_share_duration = None

    if screen_share_duration is None and hasattr(live_session, "extra_data"):
        extra_data = getattr(live_session, "extra_data")
        if isinstance(extra_data, dict):
            raw = extra_data.get("screen_share_duration")
            if raw is not None:
                try:
                    screen_share_duration = float(raw)
                except (TypeError, ValueError):
                    screen_share_duration = None

    # 统计学生 join 事件数
    result = await db.execute(
        select(func.count(MemberEvent.id)).where(
            and_(
                MemberEvent.session_id == session_id,
                MemberEvent.user_role == UserRole.student,
                MemberEvent.event_type == EventType.join,
            )
        )
    )
    student_join_count = result.scalar() or 0

    # 若无屏幕共享数据，返回默认分数
    if screen_share_duration is None:
        score = 70
        details: Dict[str, Any] = {
            "screen_share_duration": None,
            "course_duration_minutes": round(course_duration_minutes, 2),
            "min_share_time": min_share_time,
            "student_join_count": student_join_count,
            "share_score": 0,
            "invite_score": 0,
            "penalty": 0,
            "total_score": score,
            "reason": "数据不足：无法获取屏幕共享时长",
        }
        return score, details

    # 屏幕共享得分（满分 40）
    threshold_duration = course_duration_minutes * 0.8 if course_duration_minutes > 0 else min_share_time
    if threshold_duration > 0:
        share_score = min(screen_share_duration / threshold_duration, 1.0) * 40
    else:
        share_score = 0.0

    # 拉人上麦得分（满分 20）
    invite_score = 20.0 if student_join_count >= 1 else 0.0

    # 异常扣分
    penalty = 0.0
    if screen_share_duration < 1:
        penalty += 30
    if student_join_count == 0:
        penalty += 10

    total_score = share_score + invite_score - penalty
    score = int(max(0, min(100, total_score)))

    details = {
        "screen_share_duration": round(screen_share_duration, 2),
        "course_duration_minutes": round(course_duration_minutes, 2),
        "min_share_time": min_share_time,
        "student_join_count": student_join_count,
        "share_score": round(share_score, 2),
        "invite_score": invite_score,
        "penalty": penalty,
        "threshold_duration": round(threshold_duration, 2),
        "total_score": round(total_score, 2),
    }

    return score, details
