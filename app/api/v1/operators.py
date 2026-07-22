from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_pagination_params
from app.models.operator import Operator
from app.schemas.operator import OperatorCreate, OperatorUpdate, OperatorResponse
from app.schemas.common import PageResponse

router = APIRouter()


@router.get("", response_model=PageResponse[OperatorResponse])
async def list_operators(
    is_active: Optional[bool] = Query(None),
    department: Optional[str] = Query(None),
    pagination: dict = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
):
    """List operators with optional filters."""
    try:
        query = select(Operator)
        filters = []

        if is_active is not None:
            filters.append(Operator.is_active == is_active)
        if department is not None:
            filters.append(Operator.department == department)

        if filters:
            query = query.where(and_(*filters))

        total_result = await db.execute(select(Operator.id).where(query.whereclause) if filters else select(Operator.id))
        total = len(total_result.scalars().all())

        query = query.offset(pagination["skip"]).limit(pagination["limit"]).order_by(Operator.created_at.desc())
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


@router.get("/{operator_id}", response_model=OperatorResponse)
async def get_operator(
    operator_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get operator detail."""
    try:
        result = await db.execute(select(Operator).where(Operator.id == operator_id))
        op_obj = result.scalar_one_or_none()
        if not op_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operator not found")
        return op_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", response_model=OperatorResponse, status_code=status.HTTP_201_CREATED)
async def create_operator(
    data: OperatorCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new operator."""
    try:
        op_obj = Operator(**data.model_dump())
        db.add(op_obj)
        await db.flush()
        await db.refresh(op_obj)
        return op_obj
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{operator_id}", response_model=OperatorResponse)
async def update_operator(
    operator_id: int,
    data: OperatorUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an operator."""
    try:
        result = await db.execute(select(Operator).where(Operator.id == operator_id))
        op_obj = result.scalar_one_or_none()
        if not op_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operator not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(op_obj, field, value)

        await db.flush()
        await db.refresh(op_obj)
        return op_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{operator_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_operator(
    operator_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an operator."""
    try:
        result = await db.execute(select(Operator).where(Operator.id == operator_id))
        op_obj = result.scalar_one_or_none()
        if not op_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operator not found")

        await db.delete(op_obj)
        await db.flush()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
