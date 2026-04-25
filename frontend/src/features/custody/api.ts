import { apiRequest } from '../../lib/api';

export type CustodyCaseView = 'open' | 'settled' | 'all';

export type CustodyCaseRecord = {
  id: string;
  company_id: string;
  branch_id: string;
  booking_id: string | null;
  booking_line_id: string | null;
  customer_id: string | null;
  dress_id: string | null;
  created_by_user_id: string | null;
  updated_by_user_id: string | null;
  entity_version: number;
  case_number: string;
  custody_date: string;
  status: string;
  case_type: string;
  notes: string | null;
  product_condition: string | null;
  return_outcome: string | null;
  security_deposit_amount: number | null;
  security_deposit_document_text: string | null;
  security_deposit_payment_document_id: string | null;
  security_deposit_refund_payment_document_id: string | null;
  compensation_amount: number | null;
  compensation_collected_on: string | null;
  compensation_payment_document_id: string | null;
  customer_name: string | null;
  booking_number: string | null;
  dress_code: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type CustodyCaseCreatePayload = {
  booking_line_id: string;
  custody_date: string;
  case_type?: string;
  notes?: string | null;
  product_condition?: string | null;
  security_deposit_amount?: number | null;
  security_deposit_document_text?: string | null;
  payment_method_id?: string | null;
};

export type CustodyCaseActionPayload = {
  action: string;
  action_date: string;
  note?: string | null;
  product_condition?: string | null;
  return_outcome?: string | null;
  compensation_amount?: number | null;
  payment_method_id?: string | null;
};

export type CustodyCompensationCollectPayload = {
  amount: number;
  payment_date: string;
  note?: string | null;
  payment_method_id?: string | null;
  override_lock?: boolean;
  override_reason?: string | null;
};

export function listCustodyCases(view: CustodyCaseView): Promise<CustodyCaseRecord[]> {
  return apiRequest<CustodyCaseRecord[]>(`/api/custody?view=${view}`, { method: 'GET' });
}

export function getCustodyCase(caseId: string): Promise<CustodyCaseRecord> {
  return apiRequest<CustodyCaseRecord>(`/api/custody/${caseId}`, { method: 'GET' });
}

export function createCustodyCase(payload: CustodyCaseCreatePayload): Promise<CustodyCaseRecord> {
  return apiRequest<CustodyCaseRecord>('/api/custody', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function applyCustodyAction(caseId: string, payload: CustodyCaseActionPayload): Promise<CustodyCaseRecord> {
  return apiRequest<CustodyCaseRecord>(`/api/custody/${caseId}/actions`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function collectCustodyCompensation(caseId: string, payload: CustodyCompensationCollectPayload): Promise<CustodyCaseRecord> {
  return apiRequest<CustodyCaseRecord>(`/api/custody/${caseId}/compensation`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
