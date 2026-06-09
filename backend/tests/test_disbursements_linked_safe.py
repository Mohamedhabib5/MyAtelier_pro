from __future__ import annotations

from fastapi.testclient import TestClient
from .test_foundation import login

def test_linked_payment_method_accounting(app_client: TestClient) -> None:
    login(app_client)

    # 1. Get posting-eligible accounts (CoA) to find a bank or asset account
    coa_res = app_client.get('/api/accounting/chart-of-accounts')
    assert coa_res.status_code == 200, coa_res.text
    coa_accounts = coa_res.json()
    
    # Let's find Bank account (1112001) and an expense account (e.g. Rent 5110)
    bank_account = next((a for a in coa_accounts if a['code'] == '1112001'), None)
    rent_account = next((a for a in coa_accounts if a['code'] == '5110'), None)
    
    assert bank_account is not None, "Bank account 1112001 should exist"
    assert rent_account is not None, "Rent expense account 5110 should exist"

    # 2. Create a new PaymentMethod linked to the Bank account
    pm_res = app_client.post(
        '/api/payment-methods',
        json={
            'name': 'البنك التجاري الدولي CIB',
            'code': 'cib_bank',
            'is_active': True,
            'linked_account_id': bank_account['id']
        }
    )
    assert pm_res.status_code == 201, pm_res.text
    payment_method = pm_res.json()
    assert payment_method['linked_account_id'] == bank_account['id']

    # 3. Create a disbursement voucher using this payment method for an expense (Rent)
    disb_res = app_client.post(
        '/api/disbursements',
        json={
            'payment_method_id': payment_method['id'],
            'voucher_date': '2026-06-08',
            'amount': 2500.0,
            'payee_type': 'expense',
            'payee_name': 'إيجار المقر الرئيسي',
            'expense_account_id': rent_account['id'],
            'notes': 'دفع إيجار شهر يونيو 2026'
        }
    )
    assert disb_res.status_code == 201, disb_res.text
    voucher = disb_res.json()
    assert voucher['expense_account_id'] == rent_account['id']
    assert voucher['journal_entry_id'] is not None

    # 4. Fetch the linked journal entry and check the lines
    je_id = voucher['journal_entry_id']
    je_res = app_client.get('/api/accounting/journal-entries')
    assert je_res.status_code == 200
    entries = je_res.json()
    
    # Find the specific entry
    entry = next((e for e in entries if e['id'] == je_id), None)
    assert entry is not None
    assert len(entry['lines']) == 2
    
    # Verifying credit and debit sides
    # Line 1 should be Debit to Rent (5110)
    # Line 2 should be Credit to Bank (1112001)
    debit_line = next((l for l in entry['lines'] if l['account_code'] == '5110'), None)
    credit_line = next((l for l in entry['lines'] if l['account_code'] == '1112001'), None)
    
    assert debit_line is not None
    assert credit_line is not None
    assert float(debit_line['debit_amount']) == 2500.0
    assert float(credit_line['credit_amount']) == 2500.0

    # 5. Void the disbursement voucher and check reversal
    void_res = app_client.post(
        f'/api/disbursements/{voucher["id"]}/void',
        json={
            'void_date': '2026-06-08',
            'reason': 'تراجع عن العملية للتجربة'
        }
    )
    assert void_res.status_code == 200, void_res.text
    voided_voucher = void_res.json()
    assert voided_voucher['status'] == 'voided'
