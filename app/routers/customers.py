from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Customer, EventRegistration, Purchase, Event, Product
from app.schemas.customer import CustomerResponse, CustomerDetail, EventSummary, PurchaseSummary

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=list[CustomerResponse])
def get_customers(
    search: Optional[str] = Query(None, description="Search by name or email"),
    has_purchased: Optional[bool] = Query(None, description="Filter by purchase status"),
    has_events: Optional[bool] = Query(None, description="Filter by event attendance"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of customers with filters."""
    query = db.query(Customer)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Customer.name.ilike(search_term),
                Customer.email.ilike(search_term)
            )
        )

    if has_purchased is not None:
        purchaser_ids = db.query(Purchase.customer_id).distinct()
        if has_purchased:
            query = query.filter(Customer.id.in_(purchaser_ids))
        else:
            query = query.filter(~Customer.id.in_(purchaser_ids))

    if has_events is not None:
        attendee_ids = db.query(EventRegistration.customer_id).distinct()
        if has_events:
            query = query.filter(Customer.id.in_(attendee_ids))
        else:
            query = query.filter(~Customer.id.in_(attendee_ids))

    customers = query.offset(skip).limit(limit).all()

    results = []
    for customer in customers:
        event_count = db.query(func.count(EventRegistration.id)).filter(
            EventRegistration.customer_id == customer.id
        ).scalar()
        purchase_count = db.query(func.count(Purchase.id)).filter(
            Purchase.customer_id == customer.id
        ).scalar()

        results.append(CustomerResponse(
            id=customer.id,
            email=customer.email,
            name=customer.name,
            phone=customer.phone,
            industry=customer.industry,
            job_title=customer.job_title,
            age_range=customer.age_range,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
            event_count=event_count,
            purchase_count=purchase_count,
            has_purchased=purchase_count > 0
        ))

    return results


@router.get("/count")
def get_customer_count(
    search: Optional[str] = Query(None),
    has_purchased: Optional[bool] = Query(None),
    has_events: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get total customer count with filters."""
    query = db.query(func.count(Customer.id))

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Customer.name.ilike(search_term),
                Customer.email.ilike(search_term)
            )
        )

    if has_purchased is not None:
        purchaser_ids = db.query(Purchase.customer_id).distinct()
        if has_purchased:
            query = query.filter(Customer.id.in_(purchaser_ids))
        else:
            query = query.filter(~Customer.id.in_(purchaser_ids))

    if has_events is not None:
        attendee_ids = db.query(EventRegistration.customer_id).distinct()
        if has_events:
            query = query.filter(Customer.id.in_(attendee_ids))
        else:
            query = query.filter(~Customer.id.in_(attendee_ids))

    return {"count": query.scalar()}


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer(customer_id: UUID, db: Session = Depends(get_db)):
    """Get customer details with events and purchases."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get events
    registrations = db.query(EventRegistration, Event).join(
        Event, EventRegistration.event_id == Event.id
    ).filter(EventRegistration.customer_id == customer_id).all()

    events = [
        EventSummary(
            id=event.id,
            name=event.name,
            event_date=event.event_date,
            registration_time=reg.registration_time,
            checked_in=reg.checked_in
        )
        for reg, event in registrations
    ]

    # Get purchases
    purchases_data = db.query(Purchase, Product).join(
        Product, Purchase.product_id == Product.id
    ).filter(Purchase.customer_id == customer_id).all()

    purchases = [
        PurchaseSummary(
            id=purchase.id,
            product_name=product.name,
            amount=float(purchase.amount) if purchase.amount else 0,
            purchased_at=purchase.purchased_at
        )
        for purchase, product in purchases_data
    ]

    return CustomerDetail(
        id=customer.id,
        email=customer.email,
        name=customer.name,
        phone=customer.phone,
        industry=customer.industry,
        job_title=customer.job_title,
        age_range=customer.age_range,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
        event_count=len(events),
        purchase_count=len(purchases),
        has_purchased=len(purchases) > 0,
        events=events,
        purchases=purchases
    )
