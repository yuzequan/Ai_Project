from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_pagination_params
from app.models.live_session import LiveSession
from app.models.evaluation_result import EvaluationResult
from app.schemas.live_session import LiveSessionCreate, LiveSessionUpdate, LiveSessionResponse, LiveSessionList
from app.schemas.evaluation_result import EvaluationResultDetail
from app.schemas.common import PageResponse

router = APIRouter()


@router.get("", response_model=PageResponse[LiveSessionList])
async def list_live_sessions(
    course_id: Optional[int] = Query(None),
    teacher_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    pagination: dict = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List live sessions with optional filters."""
    try:
        query = select(LiveSession)
        filters = []

        if course_id is not None:
            filters.append(LiveSession.course_id == course_id)
        if teacher_id is not None:
            filters.append(LiveSession.teacher_id == teacher_id)
        if start_date is not None:
            filters.append(LiveSession.start_time >= datetime.combine(start_date, datetime.min.time()))
        if end_date is not None:
            filters.append(LiveSession.start_time <= datetime.combine(end_date, datetime.max.time()))

        if filters:
            query = query.where(and_(*filters))

        count_query = select(LiveSession).where(and_(*filters)) if filters else select(LiveSession)
        total_result = await db.execute(select(LiveSession.id).where(count_query.whereclause) if filters else select(LiveSession.id))
        total = len(total_result.scalars().all())

        query = query.offset(pagination["skip"]).limit(pagination["limit"]).order_by(LiveSession.created_at.desc())
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


@router.get("/{session_id}", response_model=LiveSessionResponse)
async def get_live_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get live session detail including evaluation result."""
    try:
        result = await db.execute(
            select(LiveSession)
            .options(selectinload(LiveSession.evaluation_result))
            .where(LiveSession.id == session_id)
        )
        session_obj = result.scalar_one_or_none()
        if not session_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")
        return session_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", response_model=LiveSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_live_session(
    data: LiveSessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new live session."""
    try:
        session_obj = LiveSession(**data.model_dump())
        db.add(session_obj)
        await db.flush()
        await db.refresh(session_obj)
        return session_obj
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{session_id}", response_model=LiveSessionResponse)
async def update_live_session(
    session_id: int,
    data: LiveSessionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a live session."""
    try:
        result = await db.execute(select(LiveSession).where(LiveSession.id == session_id))
        session_obj = result.scalar_one_or_none()
        if not session_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session_obj, field, value)

        await db.flush()
        await db.refresh(session_obj)
        return session_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_live_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a live session."""
    try:
        result = await db.execute(select(LiveSession).where(LiveSession.id == session_id))
        session_obj = result.scalar_one_or_none()
        if not session_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")

        await db.delete(session_obj)
        await db.flush()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{session_id}/details", response_model=EvaluationResultDetail)
async def get_live_session_details(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get four-dimension evaluation details for a live session."""
    try:
        result = await db.execute(
            select(EvaluationResult).where(EvaluationResult.session_id == session_id)
        )
        eval_result = result.scalar_one_or_none()
        if not eval_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation result not found for this session")

        details = eval_result.details if eval_result.details else {}
        return EvaluationResultDetail(
            attendance_score=eval_result.attendance_score,
            professionalism_score=eval_result.professionalism_score,
            engagement_score=eval_result.engagement_score,
            software_skill_score=eval_result.software_skill_score,
            overall_score=eval_result.overall_score,
            details=details,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
