from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date

from app.modules.exports.models import DailyEmailReportConfig
from app.core.security import encrypt_secret
from app.modules.payments.models import PaymentDocument, DisbursementVoucher
from app.modules.payments.serializers import document_total
from .test_bookings import seed_customer, seed_service_bundle, seed_dress
from .test_branch_scope import create_booking_in_current_branch
from .test_foundation import login

def create_active_notification_config(db: Session, company_id: str) -> DailyEmailReportConfig:
    config = DailyEmailReportConfig(
        company_id=company_id,
        name="Test Operations Notification Config",
        sender_email="sender@gmail.com",
        sender_password=encrypt_secret("supersecretapppassword123"),
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        recipient_email="recipient@gmail.com,recipient2@gmail.com",
        send_hour=18,
        is_active=True,
        notify_payment_captured=True,
        notify_payment_refunded=True
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config

def test_dispatch_payment_notification_safely_handles_both_types(db_session: Session, setup_company_and_admin: dict, monkeypatch) -> None:
    company = setup_company_and_admin["company"]
    admin = setup_company_and_admin["admin_user"]
    config = create_active_notification_config(db_session, company.id)
    
    # Mock send_email_async
    sent_emails = []
    def mock_send_email_async(**kwargs):
        sent_emails.append(kwargs)
    
    import app.modules.exports.notification_service as ns
    monkeypatch.setattr(ns, "send_email_async", mock_send_email_async)
    
    # 1. Test dispatch_payment_notification with PaymentDocument (Collection / Receipt)
    from app.modules.payments.models import PaymentDocument, PaymentMethod
    from app.modules.customers.models import Customer
    from app.modules.organization.models import Branch
    
    branch = db_session.query(Branch).filter(Branch.company_id == company.id).first()
    customer = Customer(company_id=company.id, full_name="زبونة تجريبية", phone="0501111111", address="العنوان")
    db_session.add(customer)
    
    pm = PaymentMethod(company_id=company.id, code="cash", name="نقدي")
    db_session.add(pm)
    db_session.flush()
    
    payment = PaymentDocument(
        company_id=company.id,
        branch_id=branch.id,
        customer_id=customer.id,
        payment_method_id=pm.id,
        payment_number="REC-TEST-001",
        payment_date=date.today(),
        document_kind="collection",
        direct_amount=1250.00
    )
    db_session.add(payment)
    db_session.commit()
    
    # Call notification dispatcher directly
    ns.dispatch_payment_notification(db_session, payment, is_refund=False)
    
    assert len(sent_emails) == 1
    assert sent_emails[0]["sender_email"] == "sender@gmail.com"
    assert "سند قبض REC-TEST-001" in sent_emails[0]["subject"]
    assert "1,250.00" in sent_emails[0]["html_content"]
    assert "زبونة تجريبية" in sent_emails[0]["html_content"]
    
    # 2. Test dispatch_payment_notification with DisbursementVoucher (Disbursement / Spend)
    sent_emails.clear()
    
    disbursement = DisbursementVoucher(
        company_id=company.id,
        branch_id=branch.id,
        payment_method_id=pm.id,
        voucher_number="VCH-TEST-001",
        voucher_date=date.today(),
        amount=750.50,
        payee_type="supplier",
        payee_name="مورد الفساتين",
        status="active"
    )
    db_session.add(disbursement)
    db_session.commit()
    
    ns.dispatch_payment_notification(db_session, disbursement, is_refund=True)
    
    assert len(sent_emails) == 1
    assert "سند صرف VCH-TEST-001" in sent_emails[0]["subject"]
    assert "750.50" in sent_emails[0]["html_content"]
    assert "مورد الفساتين" in sent_emails[0]["html_content"]


def test_api_calls_trigger_notifications_based_on_settings(app_client: TestClient, db_session: Session, setup_company_and_admin: dict, monkeypatch) -> None:
    login(app_client)
    company = setup_company_and_admin["company"]
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-NOTIF-01', '2026-08-10')
    
    # Mock send_email_async
    sent_emails = []
    def mock_send_email_async(**kwargs):
        sent_emails.append(kwargs)
    
    import app.modules.exports.notification_service as ns
    monkeypatch.setattr(ns, "send_email_async", mock_send_email_async)
    
    # Scenario A: No active config -> No emails sent
    payment_resp = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-01',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 200}],
        },
    )
    assert payment_resp.status_code == 201
    assert len(sent_emails) == 0
    
    # Scenario B: Active config with notify_payment_captured = False -> No emails sent
    config = create_active_notification_config(db_session, company.id)
    config.notify_payment_captured = False
    db_session.commit()
    
    payment_resp2 = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-01',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 300}],
        },
    )
    assert payment_resp2.status_code == 201
    assert len(sent_emails) == 0
    
    # Scenario C: Active config with notify_payment_captured = True -> Email sent!
    config.notify_payment_captured = True
    db_session.commit()
    
    payment_resp3 = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-01',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 400}],
        },
    )
    assert payment_resp3.status_code == 201
    assert len(sent_emails) == 1
    assert "سند قبض REC" in sent_emails[0]["subject"]
    assert "400.00" in sent_emails[0]["html_content"]
    assert "Bride One" in sent_emails[0]["html_content"]
