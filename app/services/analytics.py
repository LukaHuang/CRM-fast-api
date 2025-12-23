from sqlalchemy import func, distinct
from sqlalchemy.orm import Session
from app.models import Customer, Event, EventRegistration, Product, Purchase
from app.schemas.analytics import OverviewStats, ConversionAnalysis, EventConversion, EventPerformance


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_overview_stats(self) -> OverviewStats:
        """Get overall CRM statistics."""
        total_customers = self.db.query(func.count(Customer.id)).scalar()
        total_events = self.db.query(func.count(Event.id)).scalar()
        total_registrations = self.db.query(func.count(EventRegistration.id)).scalar()
        total_purchases = self.db.query(func.count(Purchase.id)).scalar()
        total_revenue = self.db.query(func.sum(Purchase.amount)).scalar() or 0

        # Customers with purchases
        customers_with_purchases = self.db.query(
            func.count(distinct(Purchase.customer_id))
        ).scalar()

        # Customers with events but no purchases
        customers_with_events = self.db.query(
            func.count(distinct(EventRegistration.customer_id))
        ).scalar()

        # Customers who attended events and also purchased
        customers_events_and_purchases = self.db.query(
            func.count(distinct(EventRegistration.customer_id))
        ).filter(
            EventRegistration.customer_id.in_(
                self.db.query(Purchase.customer_id)
            )
        ).scalar()

        customers_with_events_only = customers_with_events - customers_events_and_purchases

        conversion_rate = (
            (customers_events_and_purchases / customers_with_events * 100)
            if customers_with_events > 0 else 0
        )

        return OverviewStats(
            total_customers=total_customers,
            total_events=total_events,
            total_event_registrations=total_registrations,
            total_purchases=total_purchases,
            total_revenue=float(total_revenue),
            customers_with_purchases=customers_with_purchases,
            customers_with_events_only=customers_with_events_only,
            conversion_rate=round(conversion_rate, 2)
        )

    def get_conversion_analysis(self) -> ConversionAnalysis:
        """Analyze conversion from event attendance to purchase."""
        # All unique event attendees
        event_attendees = self.db.query(
            distinct(EventRegistration.customer_id)
        ).all()
        attendee_ids = {a[0] for a in event_attendees}

        # Purchasers
        purchasers = self.db.query(
            distinct(Purchase.customer_id)
        ).all()
        purchaser_ids = {p[0] for p in purchasers}

        # Converted (attended events AND purchased)
        converted_ids = attendee_ids & purchaser_ids

        # Purchased without attending events
        purchased_without_events = purchaser_ids - attendee_ids

        conversion_rate = (
            (len(converted_ids) / len(attendee_ids) * 100)
            if attendee_ids else 0
        )

        # Get top converting events
        top_events = self._get_top_converting_events(purchaser_ids)

        return ConversionAnalysis(
            total_event_attendees=len(attendee_ids),
            converted_to_purchase=len(converted_ids),
            conversion_rate=round(conversion_rate, 2),
            purchased_without_events=len(purchased_without_events),
            top_converting_events=top_events
        )

    def _get_top_converting_events(self, purchaser_ids: set, limit: int = 10) -> list[EventConversion]:
        """Get events with highest conversion rates."""
        events = self.db.query(Event).all()
        results = []

        for event in events:
            registrations = self.db.query(EventRegistration).filter(
                EventRegistration.event_id == event.id
            ).all()

            total_regs = len(registrations)
            if total_regs == 0:
                continue

            converted = sum(1 for r in registrations if r.customer_id in purchaser_ids)
            conv_rate = (converted / total_regs * 100) if total_regs > 0 else 0

            results.append(EventConversion(
                event_name=event.name,
                total_registrations=total_regs,
                converted_to_purchase=converted,
                conversion_rate=round(conv_rate, 2)
            ))

        # Sort by conversion rate descending
        results.sort(key=lambda x: x.conversion_rate, reverse=True)
        return results[:limit]

    def get_event_performance(self) -> list[EventPerformance]:
        """Get performance metrics for all events."""
        events = self.db.query(Event).order_by(Event.event_date.desc()).all()
        results = []

        for event in events:
            registrations = self.db.query(EventRegistration).filter(
                EventRegistration.event_id == event.id
            ).all()

            total_regs = len(registrations)
            checked_in = sum(1 for r in registrations if r.checked_in)
            check_in_rate = (checked_in / total_regs * 100) if total_regs > 0 else 0

            results.append(EventPerformance(
                event_name=event.name,
                event_date=str(event.event_date) if event.event_date else None,
                total_registrations=total_regs,
                checked_in_count=checked_in,
                check_in_rate=round(check_in_rate, 2)
            ))

        return results
