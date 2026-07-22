"""活跃度评分引擎。

评分规则：
- 学生评论数：>=20 条得 30 分，不足按比例计算
- 学生发言数：>=30 条得 30 分，不足按比例计算
- 老师提问次数：逐字稿中统计问句数量，每问加 2 分，上限 20 分
- 互动频次：学生 join/leave 次数估算连麦互动，>=5 次得 20 分，不足按比例计算
"""

import logging
from typing import Tuple, Dict, Any, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LiveSession, Comment, Transcript, MemberEvent, UserRole, SpeakerRole, EventType

logger = logging.getLogger(__name__)

# 问句检测标记词
QUESTION_MARKERS = [
    "?", "？", "吗", "呢", "什么", "怎么", "为什么", "多少", "几",
    "哪里", "谁", "何时", "怎样", "如何", "是不是", "能不能", "可以吗",
]

# 阈值常量
COMMENT_THRESHOLD = 20
SPEAK_THRESHOLD = 30
QUESTION_MAX_SCORE = 20
QUESTION_BONUS_PER_QUESTION = 2
INTERACTION_THRESHOLD = 5


async def calculate_engagement_score(
    db: AsyncSession, session_id: int
) -> Tuple[int, Dict[str, Any]]:
    """计算活跃度评分。

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

    # 1. 学生评论数得分（满分 30）
    result = await db.execute(
        select(func.count(Comment.id)).where(
            and_(
                Comment.session_id == session_id,
                Comment.user_role == UserRole.student,
            )
        )
    )
    student_comment_count = result.scalar() or 0
    comment_score = min(student_comment_count / COMMENT_THRESHOLD, 1.0) * 30

    # 2. 学生发言数得分（满分 30）
    result = await db.execute(
        select(func.count(Transcript.id)).where(
            and_(
                Transcript.session_id == session_id,
                Transcript.speaker_role == SpeakerRole.student,
            )
        )
    )
    student_speak_count = result.scalar() or 0
    speak_score = min(student_speak_count / SPEAK_THRESHOLD, 1.0) * 30

    # 3. 老师提问次数得分（满分 20）
    result = await db.execute(
        select(Transcript).where(
            and_(
                Transcript.session_id == session_id,
                Transcript.speaker_role == SpeakerRole.teacher,
            )
        )
    )
    teacher_transcripts = result.scalars().all()

    question_count = 0
    for t in teacher_transcripts:
        content = t.content or ""
        # 若内容中包含任一问句标记，则该条发言计为一次提问
        for marker in QUESTION_MARKERS:
            if marker in content:
                question_count += 1
                break

    question_score = min(question_count * QUESTION_BONUS_PER_QUESTION, QUESTION_MAX_SCORE)

    # 4. 互动频次得分（学生 join/leave 事件，满分 20）
    result = await db.execute(
        select(func.count(MemberEvent.id)).where(
            and_(
                MemberEvent.session_id == session_id,
                MemberEvent.user_role == UserRole.student,
                MemberEvent.event_type.in_([EventType.join, EventType.leave]),
            )
        )
    )
    student_interaction_count = result.scalar() or 0
    interaction_score = min(student_interaction_count / INTERACTION_THRESHOLD, 1.0) * 20

    total_score = comment_score + speak_score + question_score + interaction_score
    score = int(max(0, min(100, total_score)))

    details: Dict[str, Any] = {
        "student_comment_count": student_comment_count,
        "comment_score": round(comment_score, 2),
        "student_speak_count": student_speak_count,
        "speak_score": round(speak_score, 2),
        "teacher_question_count": question_count,
        "question_score": question_score,
        "student_interaction_count": student_interaction_count,
        "interaction_score": round(interaction_score, 2),
    }

    return score, details
