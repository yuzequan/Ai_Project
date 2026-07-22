from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_pagination_params
from app.models.member_event import MemberEvent
from app.schemas.member_event import MemberEventCreate, MemberEventResponse
from app.schemas.common import PageResponse

router = APIRouter()


@router.get("", response_model=PageResponse[MemberEventResponse])
async def list_member_events(
    session_id: Optional[int] = Query(None),
    user_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    pagination: dict = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List member events with optional filters."""
    try:
        query = select(MemberEvent)
        filters = []

        if session_id is not None:
            filters.append(MemberEvent.session_id == session_id)
        if user_id is not None:
            filters.append(MemberEvent.user_id == user_id)
        if event_type is not None:
            filters.append(MemberEvent.event_type == event_type)

        if filters:
            query = query.where(and_(*filters))

        total_result = await db.execute(select(MemberEvent.id).where(query.whereclause) if filters else select(MemberEvent.id))
        total = len(total_result.scalars().all())

        query = query.offset(pagination["skip"]).limit(pagination["limit"]).order_by(MemberEvent.event_time.desc())
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


@router.post("/batch", response_model=List[MemberEventResponse], status_code=status.HTTP_201_CREATED)
async def batch_create_member_events(
    items: List[MemberEventCreate],
    db: AsyncSession = Depends(get_db),
):
    """Batch create member events."""
    try:
        event_objs = [MemberEvent(**item.model_dump()) for item in items]
        db.add_all(event_objs)
        await db.flush()
        for obj in event_objs:
            await db.refresh(obj)
        return event_objs
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
