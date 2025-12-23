import os
import re
from datetime import datetime
from typing import Optional
import pandas as pd
from sqlalchemy.orm import Session
from app.models import Customer, Event, EventRegistration, Product, Purchase


class DataImportService:
    def __init__(self, db: Session):
        self.db = db

    def import_accupass_data(self, data_dir: str) -> dict:
        """Import all Accupass CSV files from a directory."""
        stats = {"events": 0, "registrations": 0, "customers_created": 0}

        for filename in os.listdir(data_dir):
            if not filename.endswith('.csv'):
                continue

            filepath = os.path.join(data_dir, filename)
            event_stats = self._import_single_event(filepath, filename)
            stats["events"] += 1
            stats["registrations"] += event_stats["registrations"]
            stats["customers_created"] += event_stats["customers_created"]

        self.db.commit()
        return stats

    def _import_single_event(self, filepath: str, filename: str) -> dict:
        """Import a single Accupass event CSV."""
        stats = {"registrations": 0, "customers_created": 0}

        # Extract event name and date from filename
        event_name, event_date = self._parse_filename(filename)

        # Create or get event
        event = self.db.query(Event).filter(Event.name == event_name).first()
        if not event:
            event = Event(name=event_name, event_date=event_date, source="accupass")
            self.db.add(event)
            self.db.flush()

        # Read CSV (skip first row which contains indices)
        df = pd.read_csv(filepath, skiprows=1)

        for _, row in df.iterrows():
            email = str(row.get('參加人Email', '')).strip().lower()
            if not email or email == 'nan':
                continue

            # Get or create customer
            customer = self.db.query(Customer).filter(Customer.email == email).first()
            if not customer:
                customer = Customer(
                    email=email,
                    name=str(row.get('參加人姓名', '')).strip() or None,
                    phone=self._clean_phone(row.get('參加人電話')),
                    industry=str(row.get('產業', '')).strip() or None,
                    job_title=str(row.get('職稱 & 工作內容', row.get('職稱', ''))).strip() or None,
                    age_range=str(row.get('年齡', '')).strip() or None,
                )
                self.db.add(customer)
                self.db.flush()
                stats["customers_created"] += 1

            # Check if registration already exists
            existing = self.db.query(EventRegistration).filter(
                EventRegistration.customer_id == customer.id,
                EventRegistration.event_id == event.id
            ).first()

            if not existing:
                registration = EventRegistration(
                    customer_id=customer.id,
                    event_id=event.id,
                    order_no=str(row.get('訂單編號', '')),
                    ticket_type=str(row.get('票券名稱', '')).strip() or None,
                    registration_time=self._parse_datetime(row.get('報名時間(GTM+8)')),
                    checked_in=bool(row.get('驗票次數', 0)),
                )
                self.db.add(registration)
                stats["registrations"] += 1

        return stats

    def import_portaly_data(self, filepath: str) -> dict:
        """Import Portaly Excel file."""
        stats = {"products": 0, "purchases": 0, "customers_created": 0}

        df = pd.read_excel(filepath)

        # Create products from unique project names
        product_map = {}
        for project_name in df['專案'].unique():
            if pd.isna(project_name):
                continue
            product = self.db.query(Product).filter(Product.name == project_name).first()
            if not product:
                # Get typical price for this product
                price = float(df[df['專案'] == project_name]['交易金額'].iloc[0])
                product = Product(name=project_name, price=price)
                self.db.add(product)
                self.db.flush()
                stats["products"] += 1
            product_map[project_name] = product

        for _, row in df.iterrows():
            email = str(row.get('E-mail', '')).strip().lower()
            if not email or email == 'nan':
                continue

            # Skip non-paid transactions
            if row.get('交易狀態') != '已入帳':
                continue

            # Get or create customer
            customer = self.db.query(Customer).filter(Customer.email == email).first()
            if not customer:
                customer = Customer(
                    email=email,
                    name=str(row.get('姓名.1', row.get('姓名', ''))).strip() or None,
                    phone=self._clean_phone(row.get('電話')),
                    job_title=str(row.get('職業', '')).strip() or None,
                )
                self.db.add(customer)
                self.db.flush()
                stats["customers_created"] += 1

            # Create purchase
            project_name = row.get('專案')
            if pd.isna(project_name) or project_name not in product_map:
                continue

            product = product_map[project_name]

            # Check if purchase already exists
            existing = self.db.query(Purchase).filter(
                Purchase.order_no == str(row.get('訂單編號', ''))
            ).first()

            if not existing:
                amount_val = row.get('交易金額', 0)
                purchase = Purchase(
                    customer_id=customer.id,
                    product_id=product.id,
                    order_no=str(row.get('訂單編號', '')),
                    amount=float(amount_val) if not pd.isna(amount_val) else 0,
                    payment_method=str(row.get('付款方式', '')).strip() or None,
                    purchased_at=self._parse_datetime(row.get('交易時間')),
                )
                self.db.add(purchase)
                stats["purchases"] += 1

        self.db.commit()
        return stats

    def _parse_filename(self, filename: str) -> tuple[str, Optional[datetime]]:
        """Extract event name and date from filename."""
        # Remove .csv extension
        name = filename.replace('.csv', '')

        # Try to extract date (YYYYMMDD pattern)
        date_match = re.match(r'^(\d{8})\s*(.+)$', name)
        if date_match:
            date_str = date_match.group(1)
            event_name = date_match.group(2).strip()
            # Clean up event name
            event_name = re.sub(r'^參加名單\s*-?\s*', '', event_name).strip()
            try:
                event_date = datetime.strptime(date_str, '%Y%m%d').date()
                return event_name, event_date
            except ValueError:
                pass

        return name, None

    def _parse_datetime(self, value) -> Optional[datetime]:
        """Parse datetime from various formats."""
        if pd.isna(value):
            return None

        value_str = str(value).strip()
        formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M:%S']

        for fmt in formats:
            try:
                return datetime.strptime(value_str, fmt)
            except ValueError:
                continue

        return None

    def _clean_phone(self, value) -> Optional[str]:
        """Clean phone number."""
        if pd.isna(value):
            return None

        phone = str(value).strip()
        # Remove .0 from float conversion
        if phone.endswith('.0'):
            phone = phone[:-2]

        return phone if phone and phone != 'nan' else None
