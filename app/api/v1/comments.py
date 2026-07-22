from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_pagination_params
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.common import PageResponse

router = APIRouter()


@router.get("", response_model=PageResponse[CommentResponse])
async def list_comments(
    session_id: Optional[int] = Query(None),
    user_id: Optional[str] = Query(None),
    parent_id: Optional[int] = Query(None),
    pagination: dict = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List comments with optional filters."""
    try:
        query = select(Comment)
        filters = []

        if session_id is not None:
            filters.append(Comment.session_id == session_id)
        if user_id is not None:
            filters.append(Comment.user_id == user_id)
        if parent_id is not None:
            filters.append(Comment.parent_id == parent_id)

        if filters:
            query = query.where(and_(*filters))

        total_result = await db.execute(select(Comment.id).where(query.whereclause) if filters else select(Comment.id))
        total = len(total_result.scalars().all())

        query = query.offset(pagination["skip"]).limit(pagination["limit"]).order_by(Comment.timestamp.desc())
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


@router.post("/batch", response_model=List[CommentResponse], status_code=status.HTTP_201_CREATED)
async def batch_create_comments(
    items: List[CommentCreate],
    db: AsyncSession = Depends(get_db),
):
    """Batch create comments."""
    try:
        comment_objs = [Comment(**item.model_dump()) for item in items]
        db.add_all(comment_objs)
        await db.flush()
        for obj in comment_objs:
            await db.refresh(obj)
        return comment_objs
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
