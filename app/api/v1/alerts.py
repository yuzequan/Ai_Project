from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_pagination_params
from app.models.alert import Alert
from app.models.alert_config import AlertConfig
from app.models.live_session import LiveSession
from app.schemas.alert import AlertResponse
from app.schemas.common import PageResponse
from app.services import FeishuNotifier

router = APIRouter()


@router.get("", response_model=PageResponse[AlertResponse])
async def list_alerts(
    session_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    pagination: dict = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List alert records with optional filters."""
    try:
        query = select(Alert)
        filters = []

        if session_id is not None:
            filters.append(Alert.session_id == session_id)
        if status is not None:
            filters.append(Alert.status == status)
        if alert_type is not None:
            filters.append(Alert.alert_type == alert_type)

        if filters:
            query = query.where(and_(*filters))

        total_result = await db.execute(select(Alert.id).where(query.whereclause) if filters else select(Alert.id))
        total = len(total_result.scalars().all())

        query = query.offset(pagination["skip"]).limit(pagination["limit"]).order_by(Alert.notified_at.desc().nullsfirst())
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


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get alert detail."""
    try:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert_obj = result.scalar_one_or_none()
        if not alert_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
        return alert_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{alert_id}/retry", response_model=AlertResponse)
async def retry_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retry sending a failed alert notification."""
    from datetime import datetime
    try:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert_obj = result.scalar_one_or_none()
        if not alert_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

        if alert_obj.status == "sent":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alert already sent")

        # Fetch session and evaluation info
        session_result = await db.execute(
            select(LiveSession).where(LiveSession.id == alert_obj.session_id)
        )
        session_obj = session_result.scalar_one_or_none()
        if not session_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated session not found")

        from app.models.evaluation_result import EvaluationResult
        eval_result = await db.execute(
            select(EvaluationResult).where(EvaluationResult.session_id == alert_obj.session_id)
        )
        eval_obj = eval_result.scalar_one_or_none()

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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active alert config found")

        try:
            notify_result = await FeishuNotifier.send_low_score_alert(session_obj, eval_obj, alert_config)
            alert_obj.status = "sent" if notify_result.get("success") else "failed"
            alert_obj.notified_at = datetime.utcnow()
            alert_obj.notified_group = alert_config.feishu_group_name
        except Exception:
            alert_obj.status = "failed"

        await db.flush()
        await db.refresh(alert_obj)
        return alert_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
