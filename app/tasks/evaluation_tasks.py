from datetime import datetime
from typing import Optional

from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.live_session import LiveSession
from app.models.evaluation_result import EvaluationResult
from app.models.alert import Alert
from app.models.alert_config import AlertConfig
from app.services import EvaluationEngine, FeishuNotifier


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_evaluation_task(self, session_id: int):
    """Asynchronously run evaluation for a live session.

    This task creates its own DB session since Celery tasks run outside
    the FastAPI request/response cycle.
    """
    import asyncio

    async def _run():
        async with AsyncSessionLocal() as db:
            try:
                # Verify session exists
                from sqlalchemy import select
                result = await db.execute(select(LiveSession).where(LiveSession.id == session_id))
                session_obj = result.scalar_one_or_none()
                if not session_obj:
                    return {"status": "failed", "error": "Session not found"}

                # Run evaluation engine
                eval_result = await EvaluationEngine.evaluate_session(db, session_id)
                if not eval_result:
                    return {"status": "failed", "error": "Evaluation engine returned None"}

                await db.commit()
                return {
                    "status": "success",
                    "evaluation_id": eval_result.id,
                    "overall_score": eval_result.overall_score,
                }
            except Exception as exc:
                await db.rollback()
                raise self.retry(exc=exc)

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def check_and_alert_task(self, evaluation_result_id: int):
    """Check evaluation score against thresholds and send alerts if needed."""
    import asyncio
    from sqlalchemy import select

    async def _check():
        async with AsyncSessionLocal() as db:
            try:
                # Fetch evaluation result
                eval_result = await db.execute(
                    select(EvaluationResult).where(EvaluationResult.id == evaluation_result_id)
                )
                eval_obj = eval_result.scalar_one_or_none()
                if not eval_obj:
                    return {"status": "failed", "error": "Evaluation result not found"}

                # Fetch associated session
                session_result = await db.execute(
                    select(LiveSession).where(LiveSession.id == eval_obj.session_id)
                )
                session_obj = session_result.scalar_one_or_none()
                if not session_obj:
                    return {"status": "failed", "error": "Associated session not found"}

                # Find matching alert config
                alert_config_result = await db.execute(
                    select(AlertConfig)
                    .where(AlertConfig.is_active == True)
                    .where(
                        (AlertConfig.course_id == session_obj.course_id) |
                        (AlertConfig.teacher_id == session_obj.teacher_id) |
                        ((AlertConfig.course_id == None) & (AlertConfig.teacher_id == None))
                    )
                    .order_by(AlertConfig.course_id.desc().nullslast(), AlertConfig.teacher_id.desc().nullslast())
                )
                alert_config = alert_config_result.scalars().first()

                if not alert_config:
                    return {"status": "skipped", "reason": "No matching alert config"}

                threshold = alert_config.threshold
                if eval_obj.overall_score >= threshold:
                    return {
                        "status": "skipped",
                        "reason": "Score above threshold",
                        "score": eval_obj.overall_score,
                        "threshold": threshold,
                    }

                # Send notification
                try:
                    notify_result = await FeishuNotifier.send_low_score_alert(session_obj, eval_obj, alert_config)
                    alert = Alert(
                        session_id=session_obj.id,
                        alert_type="low_score",
                        threshold=threshold,
                        actual_score=eval_obj.overall_score,
                        notified_group=alert_config.feishu_group_name,
                        notified_at=datetime.utcnow(),
                        status="sent" if notify_result.get("success") else "failed",
                    )
                    db.add(alert)
                    await db.commit()
                    return {
                        "status": "alert_sent" if notify_result.get("success") else "alert_failed",
                        "score": eval_obj.overall_score,
                        "threshold": threshold,
                    }
                except Exception as exc:
                    alert = Alert(
                        session_id=session_obj.id,
                        alert_type="low_score",
                        threshold=threshold,
                        actual_score=eval_obj.overall_score,
                        notified_group=alert_config.feishu_group_name,
                        status="failed",
                    )
                    db.add(alert)
                    await db.commit()
                    raise self.retry(exc=exc)

            except Exception as exc:
                await db.rollback()
                raise self.retry(exc=exc)

    return asyncio.run(_check())
