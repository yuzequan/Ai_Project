from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_pagination_params
from app.models.evaluation_result import EvaluationResult
from app.models.live_session import LiveSession
from app.models.alert_config import AlertConfig
from app.models.alert import Alert
from app.schemas.evaluation_result import EvaluationResultResponse, EvaluationResultCreate
from app.schemas.common import PageResponse
from app.services import EvaluationEngine, FeishuNotifier

router = APIRouter()


@router.get("", response_model=PageResponse[EvaluationResultResponse])
async def list_evaluations(
    session_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    max_score: Optional[float] = Query(None, ge=0, le=100),
    pagination: dict = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List evaluation results with optional filters."""
    try:
        query = select(EvaluationResult)
        filters = []

        if session_id is not None:
            filters.append(EvaluationResult.session_id == session_id)
        if start_date is not None:
            filters.append(EvaluationResult.evaluated_at >= datetime.combine(start_date, datetime.min.time()))
        if end_date is not None:
            filters.append(EvaluationResult.evaluated_at <= datetime.combine(end_date, datetime.max.time()))
        if min_score is not None:
            filters.append(EvaluationResult.overall_score >= min_score)
        if max_score is not None:
            filters.append(EvaluationResult.overall_score <= max_score)

        if filters:
            query = query.where(and_(*filters))

        total_result = await db.execute(select(EvaluationResult.id).where(query.whereclause) if filters else select(EvaluationResult.id))
        total = len(total_result.scalars().all())

        query = query.offset(pagination["skip"]).limit(pagination["limit"]).order_by(EvaluationResult.evaluated_at.desc())
        result = await db.execute(query)
        items = result.scalars().all()

        return PageResponse(
            total=total,
            skip=pagination["skip"],
            limit=pagination["limit"],
            items=items,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{evaluation_id}", response_model=EvaluationResultResponse)
async def get_evaluation(
    evaluation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get evaluation result detail."""
    try:
        result = await db.execute(select(EvaluationResult).where(EvaluationResult.id == evaluation_id))
        eval_obj = result.scalar_one_or_none()
        if not eval_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation result not found")
        return eval_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{session_id}/run", response_model=EvaluationResultResponse)
async def run_evaluation(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger evaluation for a session and send alert if needed."""
    try:
        # 1. Check session exists
        session_result = await db.execute(select(LiveSession).where(LiveSession.id == session_id))
        session_obj = session_result.scalar_one_or_none()
        if not session_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")

        # 2. Call evaluation engine
        eval_result = await EvaluationEngine.evaluate_session(db, session_id)
        if not eval_result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Evaluation failed")

        # 3. Check score against threshold and send alert if needed
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
        alert_configs = alert_config_result.scalars().all()

        for alert_config in alert_configs:
            threshold = alert_config.threshold
            if eval_result.overall_score < threshold:
                try:
                    notify_result = await FeishuNotifier.send_low_score_alert(session_obj, eval_result, alert_config)
                    alert = Alert(
                        session_id=session_id,
                        alert_type="low_score",
                        threshold=threshold,
                        actual_score=eval_result.overall_score,
                        notified_group=alert_config.feishu_group_name,
                        notified_at=datetime.utcnow(),
                        status="sent" if notify_result.get("success") else "failed",
                    )
                    db.add(alert)
                    await db.flush()
                except Exception:
                    alert = Alert(
                        session_id=session_id,
                        alert_type="low_score",
                        threshold=threshold,
                        actual_score=eval_result.overall_score,
                        notified_group=alert_config.feishu_group_name,
                        status="failed",
                    )
                    db.add(alert)
                    await db.flush()
            break  # Only trigger the first matching config

        await db.commit()
        await db.refresh(eval_result)
        return eval_result
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/stats")
async def get_evaluation_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get evaluation statistics."""
    try:
        filters = []
        if start_date is not None:
            filters.append(EvaluationResult.evaluated_at >= datetime.combine(start_date, datetime.min.time()))
        if end_date is not None:
            filters.append(EvaluationResult.evaluated_at <= datetime.combine(end_date, datetime.max.time()))

        query = select(
            func.avg(EvaluationResult.overall_score).label("avg_overall"),
            func.max(EvaluationResult.overall_score).label("max_overall"),
            func.min(EvaluationResult.overall_score).label("min_overall"),
            func.avg(EvaluationResult.attendance_score).label("avg_attendance"),
            func.avg(EvaluationResult.professionalism_score).label("avg_professionalism"),
            func.avg(EvaluationResult.engagement_score).label("avg_engagement"),
            func.avg(EvaluationResult.software_skill_score).label("avg_software_skill"),
            func.count(EvaluationResult.id).label("count"),
        )
        if filters:
            query = query.where(and_(*filters))

        result = await db.execute(query)
        row = result.one()

        return {
            "average_score": round(row.avg_overall, 2) if row.avg_overall else 0,
            "highest_score": round(row.max_overall, 2) if row.max_overall else 0,
            "lowest_score": round(row.min_overall, 2) if row.min_overall else 0,
            "dimension_averages": {
                "attendance": round(row.avg_attendance, 2) if row.avg_attendance else 0,
                "professionalism": round(row.avg_professionalism, 2) if row.avg_professionalism else 0,
                "engagement": round(row.avg_engagement, 2) if row.avg_engagement else 0,
                "software_skill": round(row.avg_software_skill, 2) if row.avg_software_skill else 0,
            },
            "total_count": row.count or 0,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
