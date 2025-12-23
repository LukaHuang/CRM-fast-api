from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.analytics import AnalyticsService
from app.schemas.analytics import OverviewStats, ConversionAnalysis, EventPerformance

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview", response_model=OverviewStats)
def get_overview(db: Session = Depends(get_db)):
    """Get overall CRM statistics."""
    service = AnalyticsService(db)
    return service.get_overview_stats()


@router.get("/conversion", response_model=ConversionAnalysis)
def get_conversion_analysis(db: Session = Depends(get_db)):
    """Get conversion analysis from events to purchases."""
    service = AnalyticsService(db)
    return service.get_conversion_analysis()


@router.get("/events/performance", response_model=list[EventPerformance])
def get_event_performance(db: Session = Depends(get_db)):
    """Get performance metrics for all events."""
    service = AnalyticsService(db)
    return service.get_event_performance()
