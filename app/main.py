from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    try:
        # Optionally create tables or run migrations here
        # from app.models.base import Base
        # async with engine.begin() as conn:
        #     await conn.run_sync(Base.metadata.create_all)
        print("AI Monitor API started successfully.")
    except Exception as e:
        print(f"Startup error: {e}")

    yield

    # Shutdown
    try:
        await engine.dispose()
        print("AI Monitor API shutdown complete. Database connections closed.")
    except Exception as e:
        print(f"Shutdown error: {e}")


# Create FastAPI application instance
app = FastAPI(
    title="AI Monitor System API",
    description="API for AI-powered live session monitoring and evaluation.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, "CORS_ORIGINS", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register v1 API routes
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={"status": "healthy", "service": "ai-monitor-api"},
        status_code=status.HTTP_200_OK,
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Monitor System API",
        "version": "1.0.0",
        "docs": "/docs",
    }
