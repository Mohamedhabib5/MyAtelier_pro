from __future__ import annotations

from fastapi.testclient import TestClient
from .test_bookings import seed_customer, seed_dress, seed_service_bundle, create_booking_document, build_booking_line_payload
from .test_foundation import login


def test_cash_reconciliation_flow(app_client: TestClient) -> None:
    auth_user = login(app_client)

    # 1. Create a payment method for "Cash" if not exist, or fetch active
    pm_res = app_client.post('/api/payment-methods', json={'name': 'نقدي', 'code': 'cash'})
    assert pm_res.status_code in (201, 400), pm_res.text
    if pm_res.status_code == 201:
        payment_method = pm_res.json()
    else:
        methods = app_client.get('/api/payment-methods').json()
        payment_method = next(m for m in methods if m['code'] == 'cash')

    pm_id = payment_method['id']

    # 2. Seed a booking and make a payment using cash method
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    dress_id = seed_dress(app_client, code='CASH-RECON-DR')
    booking = create_booking_document(
        app_client,
        customer_id,
        [
            build_booking_line_payload(
                service_bundle,
                service_date='2026-08-01',
                dress_id=dress_id,
                line_price=1000.0,
            )
        ],
    )
    
    payment_res = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_method_id': pm_id,
            'payment_date': '2026-08-01',
            'notes': 'دفع نقدي كاشير',
            'allocations': [
                {
                    'booking_id': booking['id'],
                    'booking_line_id': booking['lines'][0]['id'],
                    'allocated_amount': 500.0,
                }
            ],
        },
    )
    assert payment_res.status_code == 201, payment_res.text
    payment = payment_res.json()

    # Make a second payment on 2026-08-02
    payment_res_2 = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_method_id': pm_id,
            'payment_date': '2026-08-02',
            'notes': 'دفع نقدي كاشير 2',
            'allocations': [
                {
                    'booking_id': booking['id'],
                    'booking_line_id': booking['lines'][0]['id'],
                    'allocated_amount': 300.0,
                }
            ],
        },
    )
    assert payment_res_2.status_code == 201
    payment_2 = payment_res_2.json()

    # 3. Query pending payments using Date Range
    pending_res = app_client.get(
        '/api/reconciliations/pending',
        params={'payment_method_id': pm_id, 'start_date': '2026-08-01', 'end_date': '2026-08-02'}
    )
    assert pending_res.status_code == 200, pending_res.text
    pending = pending_res.json()
    assert len(pending) == 2
    assert pending[0]['id'] == payment['id']
    assert pending[1]['id'] == payment_2['id']

    # 4. Attempt reconciliation without receiver_name (should fail)
    recon_fail = app_client.post(
        '/api/reconciliations',
        json={
            'payment_method_id': pm_id,
            'start_date': '2026-08-01',
            'end_date': '2026-08-02',
            'notes': 'تسوية تجريبية',
            'items': [{'payment_document_id': payment['id'], 'actual_amount': 500.0}]
        }
    )
    assert recon_fail.status_code == 400
    assert 'استلم النقدية' in recon_fail.json()['detail']

    # 5. Perform valid reconciliation with receiver_name for first payment (2026-08-01 to 2026-08-01)
    recon_success = app_client.post(
        '/api/reconciliations',
        json={
            'payment_method_id': pm_id,
            'start_date': '2026-08-01',
            'end_date': '2026-08-01',
            'receiver_name': 'أحمد المدير المالي',
            'notes': 'التسوية الأولى',
            'items': [{'payment_document_id': payment['id'], 'actual_amount': 500.0}]
        }
    )
    assert recon_success.status_code == 201, recon_success.text
    recon1 = recon_success.json()
    assert recon1['is_latest'] is True

    # 6. Attempt second reconciliation that overlaps with the first period (should fail sequential constraint)
    recon_overlap = app_client.post(
        '/api/reconciliations',
        json={
            'payment_method_id': pm_id,
            'start_date': '2026-08-01',
            'end_date': '2026-08-02',
            'receiver_name': 'أحمد المدير المالي',
            'items': [{'payment_document_id': payment_2['id'], 'actual_amount': 300.0}]
        }
    )
    assert recon_overlap.status_code == 400
    assert 'يجب أن تبدأ بعد انتهاء التسوية السابقة' in recon_overlap.json()['detail']

    # 7. Perform valid sequential reconciliation starting after the first ends (2026-08-02 to 2026-08-02)
    recon2_success = app_client.post(
        '/api/reconciliations',
        json={
            'payment_method_id': pm_id,
            'start_date': '2026-08-02',
            'end_date': '2026-08-02',
            'receiver_name': 'أحمد المدير المالي',
            'notes': 'التسوية الثانية',
            'items': [{'payment_document_id': payment_2['id'], 'actual_amount': 300.0}]
        }
    )
    assert recon2_success.status_code == 201
    recon2 = recon2_success.json()
    assert recon2['is_latest'] is True

    # Verify that the first reconciliation is no longer marked as the latest
    list_recon = app_client.get('/api/reconciliations')
    assert list_recon.status_code == 200
    recons = list_recon.json()
    assert len(recons) >= 2
    r2 = next(r for r in recons if r['id'] == recon2['id'])
    r1 = next(r for r in recons if r['id'] == recon1['id'])
    assert r2['is_latest'] is True
    assert r1['is_latest'] is False

    # 8. Try to delete or edit the first (historical) reconciliation (should fail)
    del_fail = app_client.delete(f'/api/reconciliations/{recon1["id"]}')
    assert del_fail.status_code == 400
    assert 'ليست التسوية الأحدث' in del_fail.json()['detail']

    put_fail = app_client.put(f'/api/reconciliations/{recon1["id"]}', json={'notes': 'تعديل ممنوع'})
    assert put_fail.status_code == 400
    assert 'ليست التسوية الأحدث' in put_fail.json()['detail']

    # 9. Edit the second (latest) reconciliation (should succeed)
    put_success = app_client.put(f'/api/reconciliations/{recon2["id"]}', json={'notes': 'ملاحظات معدلة'})
    assert put_success.status_code == 200
    assert put_success.json()['notes'] == 'ملاحظات معدلة'

    # 10. Delete the second (latest) reconciliation (should succeed)
    del_success = app_client.delete(f'/api/reconciliations/{recon2["id"]}')
    assert del_success.status_code == 204

    # Verify that the first reconciliation becomes the latest one again!
    list_recon_after = app_client.get('/api/reconciliations')
    assert list_recon_after.status_code == 200
    recons_after = list_recon_after.json()
    r1_after = next(r for r in recons_after if r['id'] == recon1['id'])
    assert r1_after['is_latest'] is True
