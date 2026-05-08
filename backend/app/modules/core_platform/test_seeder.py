from __future__ import annotations

import uuid
from sqlalchemy.orm import Session
from app.modules.identity.models import User, Role, Permission
from app.modules.organization.models import Company, Branch, FiscalPeriod, DocumentSequence
from app.modules.catalog.models import Department, ServiceCatalogItem
from app.modules.customers.models import Customer
from app.modules.bookings.models import Booking, BookingLine
from app.modules.payments.models import PaymentDocument, PaymentAllocation, PaymentMethod
from app.modules.core_platform.models import AuditLog, AppSetting, BackupRecord
from app.modules.accounting.models import ChartOfAccount, JournalEntry, JournalEntryLine
from app.modules.dresses.models import DressResource
from app.modules.custody.models import CustodyCase

from app.modules.organization.service import ensure_organization_foundation

def seed_test_baseline(db: Session):
    """
    Ensures a consistent set of reference data exists for E2E tests.
    If the data already exists (matched by name/code), it skips creation.
    """
    # 1. Foundation
    company = ensure_organization_foundation(db, "MyAtelier Pro")
    branch = db.query(Branch).filter_by(company_id=company.id, code="MAIN").first()
    
    # 2. Catalog
    dept = db.query(Department).filter_by(company_id=company.id, name="الفساتين").first()
    if not dept:
        dept = Department(
            company_id=company.id,
            name="الفساتين",
            code="DRS",
            is_active=True
        )
        db.add(dept)
        db.flush()
        print(f"Seeded Department: {dept.name}")

    service = db.query(ServiceCatalogItem).filter_by(company_id=company.id, name="فستان زفاف").first()
    if not service:
        service = ServiceCatalogItem(
            company_id=company.id,
            department_id=dept.id,
            name="فستان زفاف",
            suggested_price=1000,
            is_active=True
        )
        db.add(service)
        db.flush()
        print(f"Seeded Service: {service.name}")

    # 3. Customer
    customer = db.query(Customer).filter_by(company_id=company.id, full_name="Stress Test Customer 0").first()
    if not customer:
        customer = Customer(
            company_id=company.id,
            full_name="Stress Test Customer 0",
            phone="01000000000",
            address="Stress Test Address",
            is_active=True
        )
        db.add(customer)
        db.flush()
        print(f"Seeded Customer: {customer.full_name}")

    db.commit()
    print("Test baseline seeding completed.")

if __name__ == "__main__":
    import os
    from app.db.session import build_engine, build_session_factory
    from app.core.config import get_settings
    
    settings = get_settings()
    engine = build_engine(settings.database_url)
    
    from app.db.base import Base
    Base.metadata.create_all(engine)
    
    session_factory = build_session_factory(engine)
    
    with session_factory() as db_session:
        seed_test_baseline(db_session)
