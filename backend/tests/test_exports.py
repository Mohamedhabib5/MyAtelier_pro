from __future__ import annotations

from fastapi.testclient import TestClient

from .test_bookings import build_booking_line_payload, create_booking_document, seed_customer, seed_dress, seed_service_bundle
from .test_branch_scope import create_booking_in_current_branch, create_second_branch
from .test_foundation import login


def test_admin_can_download_customers_booking_and_payment_exports(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-001', '2026-08-10')
    payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-01',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 700}],
        },
    )
    assert payment.status_code == 201, payment.text

    customers_export = app_client.get('/api/exports/customers.csv')
    bookings_export = app_client.get('/api/exports/bookings.csv')
    booking_lines_export = app_client.get('/api/exports/booking-lines.csv')
    payments_export = app_client.get('/api/exports/payments.csv')
    payment_allocations_export = app_client.get('/api/exports/payment-allocations.csv')
    custody_export = app_client.get('/api/exports/custody.csv')
    customers_xlsx = app_client.get('/api/exports/customers.xlsx')
    bookings_xlsx = app_client.get('/api/exports/bookings.xlsx')
    payments_xlsx = app_client.get('/api/exports/payment-documents.xlsx')
    custody_xlsx = app_client.get('/api/exports/custody.xlsx')

    assert customers_export.status_code == 200
    disposition = customers_export.headers['content-disposition']
    assert 'attachment; filename="customers_' in disposition
    assert '; filename*=UTF-8\'\'customers_' in disposition
    assert 'الاسم الكامل,الهاتف' in customers_export.text
    assert 'Bride One' in customers_export.text

    assert bookings_export.status_code == 200
    assert 'رقم الحجز' in bookings_export.text
    assert 'اسم الفرع' in bookings_export.text
    assert 'BK' in bookings_export.text

    assert booking_lines_export.status_code == 200
    assert 'رقم الحجز' in booking_lines_export.text
    assert 'اسم الفرع' in booking_lines_export.text
    assert 'اسم العميلة' in booking_lines_export.text
    assert 'رقم الهاتف' in booking_lines_export.text
    assert 'تجربة فستان' in booking_lines_export.text

    assert payments_export.status_code == 200
    assert 'رقم الدفع' in payments_export.text
    assert 'اسم الفرع' in payments_export.text
    assert 'اسم العميلة' in payments_export.text
    assert 'REC' in payments_export.text
    assert 'JV' in payments_export.text

    assert payment_allocations_export.status_code == 200
    assert 'رقم الدفع' in payment_allocations_export.text
    assert 'اسم الفرع' in payment_allocations_export.text
    assert 'اسم العميلة' in payment_allocations_export.text
    assert booking['booking_number'] in payment_allocations_export.text
    assert customers_xlsx.status_code == 200
    assert customers_xlsx.headers['content-type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert customers_xlsx.content[:2] == b'PK'
    assert bookings_xlsx.status_code == 200
    assert bookings_xlsx.content[:2] == b'PK'
    assert payments_xlsx.status_code == 200
    assert payments_xlsx.content[:2] == b'PK'
    assert custody_export.status_code == 200
    assert 'رقم الحالة,الحالة' in custody_export.text
    assert custody_xlsx.status_code == 200
    assert custody_xlsx.content[:2] == b'PK'


def test_branch_switch_scopes_booking_and_payment_exports(app_client: TestClient) -> None:
    login(app_client)
    second_branch_id = create_second_branch(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-002', '2026-08-15')
    payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-03',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 500}],
        },
    )
    assert payment.status_code == 201, payment.text
    default_booking_number = app_client.get('/api/bookings').json()[0]['booking_number']
    default_payment_number = app_client.get('/api/payments').json()[0]['payment_number']

    switch_response = app_client.post('/api/settings/branches/active', json={'branch_id': second_branch_id})
    assert switch_response.status_code == 200, switch_response.text

    bookings_export = app_client.get('/api/exports/bookings.csv')
    payments_export = app_client.get('/api/exports/payments.csv')
    customers_export = app_client.get('/api/exports/customers.csv')

    assert default_booking_number not in bookings_export.text
    assert default_payment_number not in payments_export.text
    assert 'Bride One' in customers_export.text


def test_admin_can_download_finance_and_reports_pdf_exports(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    _ = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-PDF-001', '2026-09-01')

    finance_pdf = app_client.get('/api/exports/finance.pdf')
    reports_pdf = app_client.get('/api/exports/reports.pdf')

    assert finance_pdf.status_code == 200, finance_pdf.text
    assert finance_pdf.headers['content-type'] == 'application/pdf'
    assert 'attachment; filename=' in finance_pdf.headers['content-disposition']
    assert finance_pdf.content.startswith(b'%PDF-1.4')

    assert reports_pdf.status_code == 200, reports_pdf.text
    assert reports_pdf.headers['content-type'] == 'application/pdf'
    assert 'attachment; filename=' in reports_pdf.headers['content-disposition']
    assert reports_pdf.content.startswith(b'%PDF-1.4')


def test_bookings_export_honors_table_filters(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    keep_dress = seed_dress(app_client, code='EXP-FLT-KEEP')
    drop_dress = seed_dress(app_client, code='EXP-FLT-DROP')
    keep_booking = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-08-20', dress_id=keep_dress, line_price=2500)],
        booking_date='2026-08-20',
    )
    drop_booking = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-08-25', dress_id=drop_dress, line_price=2500)],
        booking_date='2026-08-25',
    )
    cancel_response = app_client.post(
        f"/api/bookings/{drop_booking['id']}/lines/{drop_booking['lines'][0]['id']}/cancel",
        json={'reason': 'Test Cancellation'}
    )
    assert cancel_response.status_code == 200, cancel_response.text

    status_export = app_client.get('/api/exports/bookings.csv?status=cancelled')
    assert status_export.status_code == 200, status_export.text
    assert drop_booking['booking_number'] in status_export.text
    assert keep_booking['booking_number'] not in status_export.text

    ranged_export = app_client.get('/api/exports/bookings.csv?date_from=2026-08-24&date_to=2026-08-31')
    assert ranged_export.status_code == 200, ranged_export.text
    assert drop_booking['booking_number'] in ranged_export.text
    assert keep_booking['booking_number'] not in ranged_export.text


def test_payments_export_honors_table_filters(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-PAY-001', '2026-08-10')

    keep_payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-10',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 200}],
        },
    )
    assert keep_payment.status_code == 201, keep_payment.text
    keep_payment_id = keep_payment.json()['id']
    keep_payment_number = keep_payment.json()['payment_number']

    drop_payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-11',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 100}],
        },
    )
    assert drop_payment.status_code == 201, drop_payment.text
    drop_payment_number = drop_payment.json()['payment_number']

    void_response = app_client.post(
        f'/api/payments/{keep_payment_id}/void',
        json={'void_date': '2026-07-12', 'reason': 'تصحيح إدخال'},
    )
    assert void_response.status_code == 200, void_response.text

    status_export = app_client.get('/api/exports/payments.csv?status=voided')
    assert status_export.status_code == 200, status_export.text
    assert keep_payment_number in status_export.text
    assert drop_payment_number not in status_export.text

    ranged_export = app_client.get('/api/exports/payments.csv?date_from=2026-07-11&date_to=2026-07-11')
    assert ranged_export.status_code == 200, ranged_export.text
    assert drop_payment_number in ranged_export.text
    assert keep_payment_number not in ranged_export.text

    alias_export = app_client.get('/api/exports/payment-documents.csv?status=voided')
    assert alias_export.status_code == 200, alias_export.text
    assert keep_payment_number in alias_export.text
    assert drop_payment_number not in alias_export.text


def test_bookings_export_honors_sort_direction(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    first_dress = seed_dress(app_client, code='EXP-SORT-001')
    second_dress = seed_dress(app_client, code='EXP-SORT-002')
    first_booking = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-04-10', dress_id=first_dress, line_price=2000)],
        booking_date='2026-04-10',
    )
    second_booking = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-04-11', dress_id=second_dress, line_price=2000)],
        booking_date='2026-04-11',
    )

    asc_export = app_client.get('/api/exports/bookings.csv?sort_by=booking_date&sort_dir=asc')
    assert asc_export.status_code == 200, asc_export.text
    lines = [line for line in asc_export.text.splitlines() if line.strip()]
    assert len(lines) >= 3
    assert first_booking['booking_number'] in lines[1]
    assert second_booking['booking_number'] in lines[2]


def test_booking_lines_export_honors_booking_filters(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    keep_booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-LINE-KEEP', '2026-08-10')
    drop_booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-LINE-DROP', '2026-08-12')
    cancel_response = app_client.post(
        f"/api/bookings/{drop_booking['id']}/lines/{drop_booking['lines'][0]['id']}/cancel",
        json={'reason': 'Test Filter Cancellation'}
    )
    assert cancel_response.status_code == 200, cancel_response.text

    filtered_export = app_client.get('/api/exports/booking-lines.csv?status=cancelled')
    assert filtered_export.status_code == 200, filtered_export.text
    assert drop_booking['booking_number'] in filtered_export.text
    assert keep_booking['booking_number'] not in filtered_export.text


def test_payment_allocations_export_honors_payment_filters(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-ALLOC-001', '2026-08-10')

    keep_payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-10',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 200}],
        },
    )
    assert keep_payment.status_code == 201, keep_payment.text
    keep_payment_number = keep_payment.json()['payment_number']

    drop_payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-11',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 100}],
        },
    )
    assert drop_payment.status_code == 201, drop_payment.text
    drop_payment_number = drop_payment.json()['payment_number']

    filtered_export = app_client.get('/api/exports/payment-allocations.csv?date_from=2026-07-11&date_to=2026-07-11')
    assert filtered_export.status_code == 200, filtered_export.text
    assert drop_payment_number in filtered_export.text
    assert keep_payment_number not in filtered_export.text


def test_daily_email_report_configs_crud(app_client: TestClient, monkeypatch) -> None:
    login(app_client)
    
    # List configs (should be empty initially or have some defaults)
    resp = app_client.get('/api/exports/daily-reports')
    assert resp.status_code == 200
    initial_count = len(resp.json())
    
    # Create config
    create_payload = {
        "name": "Test Config",
        "sender_email": "sender@gmail.com",
        "sender_password": "supersecretpassword123",
        "recipient_email": "recipient@gmail.com",
        "send_hour": 18,
        "is_active": True
    }
    resp = app_client.post('/api/exports/daily-reports', json=create_payload)
    assert resp.status_code == 200, resp.text
    created = resp.json()
    assert created["name"] == "Test Config"
    assert created["sender_email"] == "sender@gmail.com"
    # Password must be masked!
    assert created["sender_password"] == "********"
    assert created["recipient_email"] == "recipient@gmail.com"
    assert created["send_hour"] == 18
    assert created["is_active"] is True
    assert "id" in created
    
    config_id = created["id"]
    
    # List again to verify it is present
    resp = app_client.get('/api/exports/daily-reports')
    assert resp.status_code == 200
    assert len(resp.json()) == initial_count + 1
    
    # Update config (change name and hour, keep password masked)
    update_payload = {
        "name": "Updated Test Config",
        "send_hour": 20,
        "sender_password": "********" # should keep the existing password
    }
    resp = app_client.patch(f'/api/exports/daily-reports/{config_id}', json=update_payload)
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["name"] == "Updated Test Config"
    assert updated["send_hour"] == 20
    assert updated["sender_password"] == "********"
    
    # Mock send_email_report to prevent SMTP connection error
    sent_reports = []
    def mock_send_email_report(*args, **kwargs):
        sent_reports.append((args, kwargs))
        return True
    
    import app.modules.exports.daily_report_runner as drr
    import app.modules.exports.daily_report_scheduler as drs
    monkeypatch.setattr(drr, "send_email_report", mock_send_email_report)
    monkeypatch.setattr(drs, "send_email_report", mock_send_email_report)
    
    # Test dispatch
    resp = app_client.post(f'/api/exports/daily-reports/{config_id}/test')
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert len(sent_reports) == 1
    assert sent_reports[0][1]["sender_password"] == "supersecretpassword123" # Decrypted!
    
    # Run due reports schedule
    resp = app_client.post('/api/exports/schedules/run-due-reports')
    assert resp.status_code == 200
    assert resp.json()["status"] in ("completed", "skipped")
    
    # Delete config
    resp = app_client.delete(f'/api/exports/daily-reports/{config_id}')
    assert resp.status_code == 200
    assert resp.json() == {"success": True}
    
    # Verify deleted
    resp = app_client.get('/api/exports/daily-reports')
    assert resp.status_code == 200
    assert len(resp.json()) == initial_count


def test_daily_email_report_html_generation_values(app_client: TestClient) -> None:
    from datetime import date, timedelta
    from app.modules.exports.daily_report_service import generate_daily_report_html
    from app.modules.organization.service import get_company_settings
    from app.modules.customers.models import Customer
    from app.modules.bookings.models import Booking
    
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    
    # 1. Update customer with groom/bride names and phone_2 directly in DB
    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        cust = db.query(Customer).filter(Customer.id == customer_id).first()
        cust.groom_name = "العريس علي"
        cust.bride_name = "العروسة سارة"
        cust.phone_2 = "01099999999"
        db.commit()
    
    # 2. Create bookings:
    today_date = date.today()
    tomorrow_date = today_date + timedelta(days=1)
    after_tomorrow_date = today_date + timedelta(days=2)
    
    # Booking 1: Today
    b1 = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date=today_date.isoformat(), line_price=1500, initial_payment_amount=500)],
        booking_date=today_date.isoformat()
    )
    
    # Booking 2: Tomorrow (scheduled on tomorrow_date)
    b2 = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date=tomorrow_date.isoformat(), line_price=2000, initial_payment_amount=800)],
        booking_date=today_date.isoformat()
    )
    
    # Booking 3: After Tomorrow (scheduled on after_tomorrow_date)
    b3 = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date=after_tomorrow_date.isoformat(), line_price=3000, initial_payment_amount=1000)],
        booking_date=today_date.isoformat()
    )
    
    # Generate HTML report for today
    with session_factory() as db:
        company = get_company_settings(db)
        html = generate_daily_report_html(db, company, today_date)
        
    # Assert MTD/YTD sections exist
    assert "ملخص مبيعات وتحصيلات الشهر والسنة" in html
    assert "منذ بداية الشهر (MTD)" in html
    assert "منذ بداية السنة (YTD)" in html
    
    # Assert next two days section exists
    assert "حجوزات ومواعيد اليومين التاليين" in html
    assert f"مواعيد يوم {tomorrow_date.strftime('%Y-%m-%d')}" in html
    assert f"مواعيد يوم {after_tomorrow_date.strftime('%Y-%m-%d')}" in html
    
    # Assert groom and bride details exist in the tomorrow/after tomorrow lists
    assert "العروسة: العروسة سارة" in html
    assert "العريس: العريس علي" in html
    assert "01099999999" in html
    assert "01010010010" in html # seed_customer phone


def test_daily_report_test_endpoint_custom_date(app_client: TestClient, monkeypatch) -> None:
    login(app_client)
    
    # 1. Create a config first
    create_payload = {
        "name": "Custom Date Config",
        "sender_email": "sender@gmail.com",
        "sender_password": "supersecretpassword123",
        "recipient_email": "recipient@gmail.com",
        "send_hour": 18,
        "is_active": True
    }
    resp = app_client.post('/api/exports/daily-reports', json=create_payload)
    assert resp.status_code == 200
    config_id = resp.json()["id"]
    
    # Mock send_email_report to inspect parameters
    sent_reports = []
    def mock_send_email_report(*args, **kwargs):
        sent_reports.append((args, kwargs))
        return True
    
    import app.modules.exports.daily_report_runner as drr
    monkeypatch.setattr(drr, "send_email_report", mock_send_email_report)
    
    # 2. Test successful dispatch with custom date
    resp = app_client.post(f'/api/exports/daily-reports/{config_id}/test?report_date=2026-06-05')
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert len(sent_reports) == 1
    
    # Check that the subject/html reflects the custom date
    kwargs = sent_reports[0][1]
    assert "2026-06-05" in kwargs["subject"]
    assert "2026-06-05" in kwargs["html_content"]
    
    # 3. Test invalid date formats
    resp = app_client.post(f'/api/exports/daily-reports/{config_id}/test?report_date=invalid-date')
    assert resp.status_code == 422
    assert "تنسيق التاريخ غير صحيح" in resp.json()["detail"]
    
    resp = app_client.post(f'/api/exports/daily-reports/{config_id}/test?report_date=2026-13-45')
    assert resp.status_code == 422
    assert "تنسيق التاريخ غير صحيح" in resp.json()["detail"]



