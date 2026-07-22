from fastapi import APIRouter

from app.api.v1 import live_sessions, evaluations, alerts, alert_configs, member_events, transcripts, comments, operators

api_router = APIRouter(prefix="/v1")

api_router.include_router(live_sessions.router, prefix="/live-sessions", tags=["live-sessions"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["evaluations"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(alert_configs.router, prefix="/alert-configs", tags=["alert-configs"])
api_router.include_router(member_events.router, prefix="/member-events", tags=["member-events"])
api_router.include_router(transcripts.router, prefix="/transcripts", tags=["transcripts"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(operators.router, prefix="/operators", tags=["operators"])
