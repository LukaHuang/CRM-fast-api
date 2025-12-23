from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr


class CustomerBase(BaseModel):
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    industry: Optional[str] = None
    job_title: Optional[str] = None
    age_range: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    event_count: int = 0
    purchase_count: int = 0
    has_purchased: bool = False

    class Config:
        from_attributes = True


class CustomerDetail(CustomerResponse):
    events: list["EventSummary"] = []
    purchases: list["PurchaseSummary"] = []


class EventSummary(BaseModel):
    id: UUID
    name: str
    event_date: Optional[datetime] = None
    registration_time: Optional[datetime] = None
    checked_in: bool = False

    class Config:
        from_attributes = True


class PurchaseSummary(BaseModel):
    id: UUID
    product_name: str
    amount: float
    purchased_at: Optional[datetime] = None

    class Config:
        from_attributes = True


CustomerDetail.model_rebuild()
