import { apiRequest } from '../../lib/api';

export type CustomerRecord = {
  id: string;
  company_id: string;
  full_name: string;
  registration_date: string | null;
  groom_name: string | null;
  bride_name: string | null;
  phone: string;
  phone_2: string | null;
  email: string | null;
  address: string | null;
  notes: string | null;
  is_active: boolean;
};

export type CustomerPayload = {
  full_name: string;
  registration_date?: string | null;
  groom_name?: string | null;
  bride_name?: string | null;
  phone: string;
  phone_2?: string | null;
  email?: string | null;
  address?: string | null;
  notes?: string | null;
};

export type CustomerUpdatePayload = CustomerPayload & {
  is_active: boolean;
};

export type RecordStatusFilter = 'all' | 'active' | 'inactive';

function resolveStatus(status: unknown): RecordStatusFilter {
  return status === 'active' || status === 'inactive' || status === 'all' ? status : 'all';
}

export function listCustomers(status: RecordStatusFilter | unknown = 'all'): Promise<CustomerRecord[]> {
  const resolved = resolveStatus(status);
  return apiRequest<CustomerRecord[]>(`/api/customers?status=${resolved}`, { method: 'GET' });
}

export function createCustomer(payload: CustomerPayload): Promise<CustomerRecord> {
  return apiRequest<CustomerRecord>('/api/customers', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateCustomer(customerId: string, payload: CustomerUpdatePayload): Promise<CustomerRecord> {
  return apiRequest<CustomerRecord>(`/api/customers/${customerId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function archiveCustomer(customerId: string, reason?: string): Promise<CustomerRecord> {
  return apiRequest<CustomerRecord>(`/api/customers/${customerId}/archive`, {
    method: 'POST',
    body: JSON.stringify({ reason: reason ?? null }),
  });
}

export function restoreCustomer(customerId: string, reason?: string): Promise<CustomerRecord> {
  return apiRequest<CustomerRecord>(`/api/customers/${customerId}/restore`, {
    method: 'POST',
    body: JSON.stringify({ reason: reason ?? null }),
  });
}

export type CustomerStatementSummary = {
  total_bookings_amount: number;
  total_collections_amount: number;
  total_refunds_amount: number;
  remaining_balance: number;
  accounting_ledger_balance: number;
};

export type CustomerBookingLineMovement = {
  line_id: string;
  line_number: number;
  service_name: string;
  department_name: string;
  dress_code: string | null;
  dress_name: string | null;
  service_date: string;
  status: string;
  line_price: number;
  revenue_recognized_at: string | null;
  cancelled_at: string | null;
  cancellation_reason: string | null;
};

export type CustomerBookingMovement = {
  booking_id: string;
  booking_number: string;
  booking_date: string;
  status: string;
  branch_name: string;
  total_amount: number;
  paid_total: number;
  remaining_amount: number;
  cancelled_at: string | null;
  cancellation_reason: string | null;
  lines: CustomerBookingLineMovement[];
};

export type CustomerPaymentMovement = {
  payment_id: string;
  payment_number: string;
  payment_date: string;
  payment_method_name: string;
  document_kind: string;
  amount: number;
  status: string;
  voided_at: string | null;
  void_reason: string | null;
  notes: string | null;
};

export type CustomerLedgerMovement = {
  entry_date: string;
  entry_number: string;
  reference: string | null;
  description: string | null;
  debit_amount: number;
  credit_amount: number;
  running_balance: number;
};

export type CustomerStatementResponse = {
  customer: CustomerRecord;
  summary: CustomerStatementSummary;
  bookings: CustomerBookingMovement[];
  payments: CustomerPaymentMovement[];
  ledger_movements: CustomerLedgerMovement[];
};

export function getCustomerStatement(customerId: string, fromDate?: string, toDate?: string): Promise<CustomerStatementResponse> {
  const params = new URLSearchParams();
  if (fromDate) params.append('from_date', fromDate);
  if (toDate) params.append('to_date', toDate);
  const queryStr = params.toString() ? `?${params.toString()}` : '';
  return apiRequest<CustomerStatementResponse>(`/api/customers/${customerId}/statement${queryStr}`, { method: 'GET' });
}

