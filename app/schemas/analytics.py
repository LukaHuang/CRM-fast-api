from pydantic import BaseModel
from typing import Optional


class OverviewStats(BaseModel):
    total_customers: int
    total_events: int
    total_event_registrations: int
    total_purchases: int
    total_revenue: float
    customers_with_purchases: int
    customers_with_events_only: int
    conversion_rate: float


class ConversionAnalysis(BaseModel):
    total_event_attendees: int
    converted_to_purchase: int
    conversion_rate: float
    purchased_without_events: int
    top_converting_events: list["EventConversion"]


class EventConversion(BaseModel):
    event_name: str
    total_registrations: int
    converted_to_purchase: int
    conversion_rate: float


class EventPerformance(BaseModel):
    event_name: str
    event_date: Optional[str] = None
    total_registrations: int
    checked_in_count: int
    check_in_rate: float


ConversionAnalysis.model_rebuild()
