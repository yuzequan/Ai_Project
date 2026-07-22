"""出勤评分引擎。

评分规则：
- 基础分 60 分（有出勤记录）
- 准时到达：20 分（在 scheduled_start 前或准时加入）
- 完整出席：20 分（无离开事件或离开时间在 scheduled_end 之后）
- 迟到扣分：每迟到 1 分钟扣 2 分，最多扣 20 分
- 早退扣分：每早退 1 分钟扣 2 分，最多扣 20 分
- 缺勤（无加入记录）：0 分
"""

import logging
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LiveSession, MemberEvent, UserRole, EventType

logger = logging.getLogger(__name__)

# 允许在 scheduled_start 前多久加入仍算准时（分钟）
GRACE_PERIOD_MINUTES = 5


async def calculate_attendance_score(
    db: AsyncSession, session_id: int
) -> Tuple[int, Dict[str, Any]]:
    """计算出勤评分。

    Args:
        db: 异步 SQLAlchemy 会话。
        session_id: 直播会话 ID。

    Returns:
        (score, details)
        - score: 0-100 的整数。
        - details: 包含 join_time, leave_time, late_minutes,
                   early_leave_minutes, deductions 等字段的字典。
    """
    # 获取直播 session
    result = await db.execute(select(LiveSession).where(LiveSession.id == session_id))
    live_session: Optional[LiveSession] = result.scalar_one_or_none()
    if not live_session:
        logger.warning("LiveSession not found: %s", session_id)
        return 0, {"error": "Session not found"}

    # 获取老师的 member_events，按时间排序
    result = await db.execute(
        select(MemberEvent)
        .where(
            and_(
                MemberEvent.session_id == session_id,
                MemberEvent.user_role == UserRole.teacher,
            )
        )
        .order_by(MemberEvent.event_time)
    )
    teacher_events = result.scalars().all()

    # 缺勤判断：无老师加入记录直接 0 分
    join_events = [e for e in teacher_events if e.event_type == EventType.join]
    if not join_events:
        return 0, {
            "join_time": None,
            "leave_time": None,
            "late_minutes": 0,
            "early_leave_minutes": 0,
            "deductions": 100,
            "reason": "缺勤：无老师加入记录",
        }

    join_time: datetime = join_events[0].event_time
    leave_events = [e for e in teacher_events if e.event_type == EventType.leave]
    leave_time: Optional[datetime] = leave_events[-1].event_time if leave_events else None

    scheduled_start: datetime = live_session.scheduled_start
    scheduled_end: datetime = live_session.scheduled_end

    # 计算迟到分钟数
    # 在 scheduled_start 前 5 分钟内或更早加入均不算迟到
    grace_start = scheduled_start - timedelta(minutes=GRACE_PERIOD_MINUTES)
    if join_time < grace_start:
        # 提前太久加入（如提前 30 分钟），视为正常，late_minutes = 0
        late_minutes = 0
    elif join_time <= scheduled_start:
        # 在允许缓冲期内加入，不算迟到
        late_minutes = 0
    else:
        # join_time > scheduled_start，计算迟到分钟数
        late_minutes = int((join_time - scheduled_start).total_seconds() / 60)

    late_deduction = min(late_minutes * 2, 20)

    # 计算早退分钟数
    early_leave_minutes = 0
    if leave_time and scheduled_end:
        if leave_time < scheduled_end:
            early_leave_minutes = int((scheduled_end - leave_time).total_seconds() / 60)
    # 若无离开事件，则不算早退
    early_leave_deduction = min(early_leave_minutes * 2, 20)

    total_deduction = late_deduction + early_leave_deduction
    score = max(0, 100 - total_deduction)

    details: Dict[str, Any] = {
        "join_time": join_time.isoformat() if join_time else None,
        "leave_time": leave_time.isoformat() if leave_time else None,
        "scheduled_start": scheduled_start.isoformat() if scheduled_start else None,
        "scheduled_end": scheduled_end.isoformat() if scheduled_end else None,
        "late_minutes": late_minutes,
        "early_leave_minutes": early_leave_minutes,
        "deductions": total_deduction,
        "late_deduction": late_deduction,
        "early_leave_deduction": early_leave_deduction,
        "on_time": late_minutes == 0,
        "completed_full": early_leave_minutes == 0,
    }

    return score, details
