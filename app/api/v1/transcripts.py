from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_pagination_params
from app.models.transcript import Transcript
from app.schemas.transcript import TranscriptCreate, TranscriptResponse
from app.schemas.common import PageResponse

router = APIRouter()


@router.get("", response_model=PageResponse[TranscriptResponse])
async def list_transcripts(
    session_id: Optional[int] = Query(None),
    speaker_id: Optional[str] = Query(None),
    is_teacher: Optional[bool] = Query(None),
    pagination: dict = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List transcripts with optional filters."""
    try:
        query = select(Transcript)
        filters = []

        if session_id is not None:
            filters.append(Transcript.session_id == session_id)
        if speaker_id is not None:
            filters.append(Transcript.speaker_id == speaker_id)
        if is_teacher is not None:
            filters.append(Transcript.is_teacher == is_teacher)

        if filters:
            query = query.where(and_(*filters))

        total_result = await db.execute(select(Transcript.id).where(query.whereclause) if filters else select(Transcript.id))
        total = len(total_result.scalars().all())

        query = query.offset(pagination["skip"]).limit(pagination["limit"]).order_by(Transcript.start_time.asc())
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


@router.post("/batch", response_model=List[TranscriptResponse], status_code=status.HTTP_201_CREATED)
async def batch_create_transcripts(
    items: List[TranscriptCreate],
    db: AsyncSession = Depends(get_db),
):
    """Batch create transcripts."""
    try:
        transcript_objs = [Transcript(**item.model_dump()) for item in items]
        db.add_all(transcript_objs)
        await db.flush()
        for obj in transcript_objs:
            await db.refresh(obj)
        return transcript_objs
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
