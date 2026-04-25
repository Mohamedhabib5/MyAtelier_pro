import { apiRequest } from '../../lib/api';

export type PaymentAllocationRecord = {
  id: string;
  payment_document_id: string;
  booking_id: string;
  booking_number: string;
  booking_status: string;
  booking_line_id: string;
  booking_line_number: number;
  service_name: string;
  department_name: string;
  dress_code: string | null;
  service_date: string;
  line_status: string;
  line_price: number;
  allocated_amount: number;
};

export type PaymentDocumentSummaryRecord = {
  id: string;
  company_id: string;
  branch_id: string;
  branch_name: string;
  customer_id: string;
  customer_name: string;
  payment_method_id: string | null;
  payment_method_name: string | null;
  payment_number: string;
  payment_date: string;
  document_kind: string;
  status: string;
  total_amount: number;
  allocation_count: number;
  booking_numbers: string[];
  journal_entry_id: string | null;
  journal_entry_number: string | null;
  journal_entry_status: string | null;
  voided_at: string | null;
  void_reason: string | null;
  notes: string | null;
};

export type PaymentDocumentRecord = PaymentDocumentSummaryRecord & {
  allocations: PaymentAllocationRecord[];
};

export type PaymentTablePage = {
  items: PaymentDocumentSummaryRecord[];
  total: number;
  page: number;
  page_size: number;
};

export type PaymentTableQuery = {
  search?: string;
  status?: string;
  documentKind?: string;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortDir?: 'asc' | 'desc';
};

export type PaymentAllocationPayload = {
  booking_id: string;
  booking_line_id: string;
  allocated_amount: number;
};

export type PaymentDocumentPayload = {
  customer_id: string;
  payment_method_id?: string | null;
  payment_date: string;
  notes?: string | null;
  allocations: PaymentAllocationPayload[];
  override_lock?: boolean;
  override_reason?: string | null;
};

export type PaymentTargetSearchRecord = {
  kind: 'customer' | 'booking';
  id: string;
  label: string;
  customer_id: string;
  customer_name: string;
  booking_id?: string | null;
  booking_number?: string | null;
};

export type PaymentTargetLineRecord = {
  line_id: string;
  line_number: number;
  service_name: string;
  department_name: string;
  dress_code: string | null;
  service_date: string;
  line_status: string;
  line_price: number;
  paid_total: number;
  remaining_amount: number;
  payment_state: string;
};

export type PaymentTargetBookingRecord = {
  booking_id: string;
  booking_number: string;
  booking_date: string;
  booking_status: string;
  total_amount: number;
  paid_total: number;
  remaining_amount: number;
  lines: PaymentTargetLineRecord[];
};

export type PaymentTargetDetailRecord = {
  scope_kind: string;
  scope_id: string;
  customer_id: string;
  customer_name: string;
  branch_id: string;
  branch_name: string;
  total_remaining: number;
  bookings: PaymentTargetBookingRecord[];
};

export type PaymentVoidPayload = {
  void_date: string;
  reason: string;
  override_lock?: boolean;
  override_reason?: string | null;
};

export function listPayments(): Promise<PaymentDocumentSummaryRecord[]> {
  return apiRequest<PaymentDocumentSummaryRecord[]>('/api/payments', { method: 'GET' });
}

export function listPaymentsPage(query: PaymentTableQuery): Promise<PaymentTablePage> {
  const params = new URLSearchParams();
  if (query.search?.trim()) params.set('search', query.search.trim());
  if (query.status?.trim()) params.set('status', query.status.trim());
  if (query.documentKind?.trim()) params.set('document_kind', query.documentKind.trim());
  if (query.dateFrom) params.set('date_from', query.dateFrom);
  if (query.dateTo) params.set('date_to', query.dateTo);
  if (query.page) params.set('page', String(query.page));
  if (query.pageSize) params.set('page_size', String(query.pageSize));
  if (query.sortBy) params.set('sort_by', query.sortBy);
  if (query.sortDir) params.set('sort_dir', query.sortDir);
  const suffix = params.toString() ? `?${params.toString()}` : '';
  return apiRequest<PaymentTablePage>(`/api/payments/table${suffix}`, { method: 'GET' });
}

export function getPaymentDocument(paymentDocumentId: string): Promise<PaymentDocumentRecord> {
  return apiRequest<PaymentDocumentRecord>(`/api/payments/${paymentDocumentId}`, { method: 'GET' });
}

export function createPayment(payload: PaymentDocumentPayload): Promise<PaymentDocumentRecord> {
  return apiRequest<PaymentDocumentRecord>('/api/payments', { method: 'POST', body: JSON.stringify(payload) });
}

export function updatePayment(paymentDocumentId: string, payload: PaymentDocumentPayload): Promise<PaymentDocumentRecord> {
  return apiRequest<PaymentDocumentRecord>(`/api/payments/${paymentDocumentId}`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function voidPayment(paymentDocumentId: string, payload: PaymentVoidPayload): Promise<PaymentDocumentRecord> {
  return apiRequest<PaymentDocumentRecord>(`/api/payments/${paymentDocumentId}/void`, { method: 'POST', body: JSON.stringify(payload) });
}

export function searchPaymentTargets(query: string): Promise<PaymentTargetSearchRecord[]> {
  return apiRequest<PaymentTargetSearchRecord[]>(`/api/payment-targets/search?q=${encodeURIComponent(query)}`, { method: 'GET' });
}

export function getCustomerPaymentTarget(customerId: string, ignorePaymentDocumentId?: string | null): Promise<PaymentTargetDetailRecord> {
  const suffix = ignorePaymentDocumentId ? `?ignore_payment_document_id=${encodeURIComponent(ignorePaymentDocumentId)}` : '';
  return apiRequest<PaymentTargetDetailRecord>(`/api/payment-targets/customer/${customerId}${suffix}`, { method: 'GET' });
}

export function getBookingPaymentTarget(bookingId: string, ignorePaymentDocumentId?: string | null): Promise<PaymentTargetDetailRecord> {
  const suffix = ignorePaymentDocumentId ? `?ignore_payment_document_id=${encodeURIComponent(ignorePaymentDocumentId)}` : '';
  return apiRequest<PaymentTargetDetailRecord>(`/api/payment-targets/booking/${bookingId}${suffix}`, { method: 'GET' });
}
