from app.routers.customers import router as customers_router
from app.routers.events import router as events_router
from app.routers.analytics import router as analytics_router

__all__ = ["customers_router", "events_router", "analytics_router"]
