from celery import Celery
from app.core.config import settings

REDIS_URL = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")

# Create Celery app instance
celery_app = Celery(
    "ai_monitor",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.evaluation_tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    result_expires=86400,  # Results expire after 24 hours
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Optional: Celery beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # "periodic-evaluation-check": {
    #     "task": "app.tasks.evaluation_tasks.check_pending_evaluations",
    #     "schedule": 300.0,  # every 5 minutes
    # },
}
