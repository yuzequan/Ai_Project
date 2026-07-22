from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_pagination_params(skip: int = 0, limit: int = 20) -> dict:
    """Return pagination parameters with validation."""
    return {"skip": max(skip, 0), "limit": min(max(limit, 1), 100)}
