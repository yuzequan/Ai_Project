from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_pagination_params
from app.models.alert_config import AlertConfig
from app.schemas.alert_config import AlertConfigCreate, AlertConfigUpdate, AlertConfigResponse
from app.schemas.common import PageResponse

router = APIRouter()


@router.get("", response_model=PageResponse[AlertConfigResponse])
async def list_alert_configs(
    course_id: Optional[int] = Query(None),
    teacher_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    pagination: dict = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List alert configs with optional filters."""
    try:
        query = select(AlertConfig)
        filters = []

        if course_id is not None:
            filters.append(AlertConfig.course_id == course_id)
        if teacher_id is not None:
            filters.append(AlertConfig.teacher_id == teacher_id)
        if is_active is not None:
            filters.append(AlertConfig.is_active == is_active)

        if filters:
            query = query.where(and_(*filters))

        total_result = await db.execute(select(AlertConfig.id).where(query.whereclause) if filters else select(AlertConfig.id))
        total = len(total_result.scalars().all())

        query = query.offset(pagination["skip"]).limit(pagination["limit"]).order_by(AlertConfig.created_at.desc())
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


@router.get("/{config_id}", response_model=AlertConfigResponse)
async def get_alert_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get alert config detail."""
    try:
        result = await db.execute(select(AlertConfig).where(AlertConfig.id == config_id))
        config_obj = result.scalar_one_or_none()
        if not config_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert config not found")
        return config_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", response_model=AlertConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_config(
    data: AlertConfigCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new alert config."""
    try:
        config_obj = AlertConfig(**data.model_dump())
        db.add(config_obj)
        await db.flush()
        await db.refresh(config_obj)
        return config_obj
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{config_id}", response_model=AlertConfigResponse)
async def update_alert_config(
    config_id: int,
    data: AlertConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an alert config."""
    try:
        result = await db.execute(select(AlertConfig).where(AlertConfig.id == config_id))
        config_obj = result.scalar_one_or_none()
        if not config_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert config not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config_obj, field, value)

        await db.flush()
        await db.refresh(config_obj)
        return config_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an alert config."""
    try:
        result = await db.execute(select(AlertConfig).where(AlertConfig.id == config_id))
        config_obj = result.scalar_one_or_none()
        if not config_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert config not found")

        await db.delete(config_obj)
        await db.flush()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
