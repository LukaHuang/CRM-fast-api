from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Event, EventRegistration, Customer
from app.schemas.event import EventResponse, EventRegistrationResponse

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of events."""
    events = db.query(Event).order_by(Event.event_date.desc()).offset(skip).limit(limit).all()

    results = []
    for event in events:
        registration_count = db.query(func.count(EventRegistration.id)).filter(
            EventRegistration.event_id == event.id
        ).scalar()

        results.append(EventResponse(
            id=event.id,
            name=event.name,
            event_date=event.event_date,
            source=event.source,
            created_at=event.created_at,
            registration_count=registration_count
        ))

    return results


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: UUID, db: Session = Depends(get_db)):
    """Get event details."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    registration_count = db.query(func.count(EventRegistration.id)).filter(
        EventRegistration.event_id == event.id
    ).scalar()

    return EventResponse(
        id=event.id,
        name=event.name,
        event_date=event.event_date,
        source=event.source,
        created_at=event.created_at,
        registration_count=registration_count
    )


@router.get("/{event_id}/registrations", response_model=list[EventRegistrationResponse])
def get_event_registrations(
    event_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get registrations for an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    registrations = db.query(EventRegistration, Customer).join(
        Customer, EventRegistration.customer_id == Customer.id
    ).filter(
        EventRegistration.event_id == event_id
    ).offset(skip).limit(limit).all()

    return [
        EventRegistrationResponse(
            id=reg.id,
            customer_name=customer.name,
            customer_email=customer.email,
            ticket_type=reg.ticket_type,
            registration_time=reg.registration_time,
            checked_in=reg.checked_in
        )
        for reg, customer in registrations
    ]
