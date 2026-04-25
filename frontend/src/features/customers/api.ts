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
