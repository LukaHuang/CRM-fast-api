from datetime import datetime, date
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class EventBase(BaseModel):
    name: str
    event_date: Optional[date] = None
    source: str = "accupass"


class EventResponse(EventBase):
    id: UUID
    created_at: datetime
    registration_count: int = 0

    class Config:
        from_attributes = True


class EventRegistrationResponse(BaseModel):
    id: UUID
    customer_name: Optional[str] = None
    customer_email: str
    ticket_type: Optional[str] = None
    registration_time: Optional[datetime] = None
    checked_in: bool = False

    class Config:
        from_attributes = True
