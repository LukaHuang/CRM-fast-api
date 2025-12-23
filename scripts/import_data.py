#!/usr/bin/env python3
"""
Data import script for CRM system.
Imports data from Accupass CSV files and Portaly Excel file.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.services.data_import import DataImportService

# Data paths
ACCUPASS_DIR = "my_data/accupass"
PORTALY_FILE = "my_data/portaly/傳送門商品管理-202512231819.xlsx"


def main():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    print("\nStarting data import...")
    db = SessionLocal()

    try:
        import_service = DataImportService(db)

        # Import Accupass data
        print(f"\nImporting Accupass data from: {ACCUPASS_DIR}")
        accupass_stats = import_service.import_accupass_data(ACCUPASS_DIR)
        print(f"  Events imported: {accupass_stats['events']}")
        print(f"  Registrations imported: {accupass_stats['registrations']}")
        print(f"  New customers created: {accupass_stats['customers_created']}")

        # Import Portaly data
        print(f"\nImporting Portaly data from: {PORTALY_FILE}")
        portaly_stats = import_service.import_portaly_data(PORTALY_FILE)
        print(f"  Products imported: {portaly_stats['products']}")
        print(f"  Purchases imported: {portaly_stats['purchases']}")
        print(f"  New customers created: {portaly_stats['customers_created']}")

        print("\n" + "=" * 50)
        print("Data import completed successfully!")
        print("=" * 50)

    except Exception as e:
        print(f"\nError during import: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
