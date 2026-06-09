import { apiRequest } from '../../lib/api';

export type DisbursementVoucherRecord = {
  id: string;
  company_id: string;
  branch_id: string;
  branch_name: string | null;
  payment_method_id: string;
  payment_method_name: string | null;
  voucher_number: string;
  voucher_date: string;
  amount: number;
  payee_type: 'customer' | 'supplier' | 'employee' | 'expense';
  payee_id: string | null;
  payee_name: string | null;
  expense_account_id: string | null;
  expense_account_code: string | null;
  expense_account_name: string | null;
  status: string;
  journal_entry_id: string | null;
  journal_entry_number: string | null;
  journal_entry_status: string | null;
  voided_at: string | null;
  void_reason: string | null;
  notes: string | null;
};

export type DisbursementTablePage = {
  items: DisbursementVoucherRecord[];
  total: number;
  page: number;
  page_size: number;
};

export type DisbursementTableQuery = {
  search?: string;
  status?: string;
  payeeType?: string;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortDir?: 'asc' | 'desc';
};

export type DisbursementCreatePayload = {
  payment_method_id: string;
  voucher_date: string;
  amount: number;
  payee_type: string;
  payee_id?: string | null;
  payee_name?: string | null;
  expense_account_id?: string | null;
  notes?: string | null;
};

export type DisbursementUpdatePayload = {
  payment_method_id?: string;
  voucher_date?: string;
  amount?: number;
  payee_type?: string;
  payee_id?: string | null;
  payee_name?: string | null;
  expense_account_id?: string | null;
  notes?: string | null;
  override_lock?: boolean;
  override_reason?: string | null;
};

export type DisbursementVoidPayload = {
  void_date: string;
  reason: string;
  override_lock?: boolean;
  override_reason?: string | null;
};

export function listDisbursementsPage(query: DisbursementTableQuery): Promise<DisbursementTablePage> {
  const params = new URLSearchParams();
  if (query.search?.trim()) params.set('search', query.search.trim());
  if (query.status?.trim()) params.set('status', query.status.trim());
  if (query.payeeType?.trim()) params.set('payee_type', query.payeeType.trim());
  if (query.dateFrom) params.set('date_from', query.dateFrom);
  if (query.dateTo) params.set('date_to', query.dateTo);
  if (query.page) params.set('page', String(query.page));
  if (query.pageSize) params.set('page_size', String(query.pageSize));
  if (query.sortBy) params.set('sort_by', query.sortBy);
  if (query.sortDir) params.set('sort_dir', query.sortDir);
  const suffix = params.toString() ? `?${params.toString()}` : '';
  return apiRequest<DisbursementTablePage>(`/api/disbursements/table${suffix}`, { method: 'GET' });
}

export function getDisbursementVoucher(id: string): Promise<DisbursementVoucherRecord> {
  return apiRequest<DisbursementVoucherRecord>(`/api/disbursements/${id}`, { method: 'GET' });
}

export function createDisbursement(payload: DisbursementCreatePayload): Promise<DisbursementVoucherRecord> {
  return apiRequest<DisbursementVoucherRecord>('/api/disbursements', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateDisbursement(id: string, payload: DisbursementUpdatePayload): Promise<DisbursementVoucherRecord> {
  return apiRequest<DisbursementVoucherRecord>(`/api/disbursements/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function voidDisbursement(id: string, payload: DisbursementVoidPayload): Promise<DisbursementVoucherRecord> {
  return apiRequest<DisbursementVoucherRecord>(`/api/disbursements/${id}/void`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function deleteDisbursement(id: string): Promise<void> {
  return apiRequest<void>(`/api/disbursements/${id}`, { method: 'DELETE' });
}
