"""专业度评分引擎。

评分规则：
- 关键词匹配：将逐字稿中老师发言与 syllabus.key_points 做文本匹配
- 覆盖率 = 匹配到的知识点数 / 总知识点数 * 60 分
- 违规词检测：从 behavior_rules 中读取 rule_type='professionalism' 的敏感词列表，
  命中每词扣 5 分，最多扣 30 分
- 额外加分：老师发言时长占比（老师发言总时长 / 课程总时长）* 10 分
"""

import logging
from typing import Tuple, Dict, Any, List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LiveSession, Transcript, Syllabus, BehaviorRule, RuleType, SpeakerRole

logger = logging.getLogger(__name__)


async def calculate_professionalism_score(
    db: AsyncSession, session_id: int
) -> Tuple[int, Dict[str, Any]]:
    """计算专业度评分。

    Args:
        db: 异步 SQLAlchemy 会话。
        session_id: 直播会话 ID。

    Returns:
        (score, details)
        - score: 0-100 的整数。
        - details: 包含 coverage_rate, matched_keywords, violations, teacher_speak_ratio 等。
    """
    # 获取直播 session
    result = await db.execute(select(LiveSession).where(LiveSession.id == session_id))
    live_session: Optional[LiveSession] = result.scalar_one_or_none()
    if not live_session:
        logger.warning("LiveSession not found: %s", session_id)
        return 0, {"error": "Session not found"}

    course_id = live_session.course_id

    # 获取课程大纲知识点
    result = await db.execute(
        select(Syllabus)
        .where(Syllabus.course_id == course_id)
        .order_by(Syllabus.order)
    )
    syllabi = result.scalars().all()

    all_key_points: List[str] = []
    for s in syllabi:
        key_points = s.key_points or []
        if isinstance(key_points, list):
            all_key_points.extend([str(kp).strip() for kp in key_points if str(kp).strip()])

    total_key_points = len(all_key_points)

    # 获取老师逐字稿
    result = await db.execute(
        select(Transcript)
        .where(
            and_(
                Transcript.session_id == session_id,
                Transcript.speaker_role == SpeakerRole.teacher,
            )
        )
        .order_by(Transcript.start_time)
    )
    teacher_transcripts = result.scalars().all()

    # 合并老师发言内容用于关键词匹配
    teacher_contents = [t.content or "" for t in teacher_transcripts]
    combined_content = " ".join(teacher_contents).lower()

    # 知识点覆盖率匹配（简单包含匹配）
    matched_keywords: List[str] = []
    for kp in all_key_points:
        if kp.lower() in combined_content:
            matched_keywords.append(kp)

    coverage_rate = len(matched_keywords) / total_key_points if total_key_points > 0 else 1.0
    coverage_score = coverage_rate * 60

    # 违规词检测
    result = await db.execute(
        select(BehaviorRule).where(BehaviorRule.rule_type == RuleType.professionalism)
    )
    prof_rules = result.scalars().all()

    violations: List[str] = []
    total_violation_deduction = 0
    for rule in prof_rules:
        condition = rule.condition or {}
        sensitive_words = condition.get("sensitive_words", [])
        if not isinstance(sensitive_words, list):
            sensitive_words = [sensitive_words] if sensitive_words else []

        for word in sensitive_words:
            word_str = str(word).strip().lower()
            if not word_str:
                continue
            if word_str in combined_content:
                # 统计命中次数，每次命中扣 5 分，累计最多扣 30 分
                count = combined_content.count(word_str)
                for _ in range(count):
                    if total_violation_deduction < 30:
                        total_violation_deduction += 5
                        violations.append(word_str)
                    else:
                        break

    violation_deduction = min(total_violation_deduction, 30)

    # 老师发言时长占比
    teacher_speak_duration = 0.0
    for t in teacher_transcripts:
        if t.start_time and t.end_time:
            duration = (t.end_time - t.start_time).total_seconds()
            teacher_speak_duration += max(0.0, duration)

    course_duration = 0.0
    if live_session.scheduled_start and live_session.scheduled_end:
        course_duration = (live_session.scheduled_end - live_session.scheduled_start).total_seconds()

    teacher_speak_ratio = teacher_speak_duration / course_duration if course_duration > 0 else 0.0
    # 发言占比上限为 100%，超出按 100% 计算
    teacher_speak_ratio = min(teacher_speak_ratio, 1.0)
    speak_bonus = teacher_speak_ratio * 10

    score = coverage_score - violation_deduction + speak_bonus
    score = int(max(0, min(100, score)))

    details: Dict[str, Any] = {
        "coverage_rate": round(coverage_rate, 4),
        "matched_keywords": matched_keywords,
        "total_key_points": total_key_points,
        "violations": violations,
        "violation_deduction": violation_deduction,
        "teacher_speak_ratio": round(teacher_speak_ratio, 4),
        "teacher_speak_duration_seconds": int(teacher_speak_duration),
        "course_duration_seconds": int(course_duration),
        "speak_bonus": round(speak_bonus, 2),
        "coverage_score": round(coverage_score, 2),
    }

    return score, details
