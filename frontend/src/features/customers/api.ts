import { apiRequest } from '../../lib/api';

export type CustomerRecord = {
  id: string;
  company_id: string;
  full_name: string;
  phone: string;
  email: string | null;
  address: string | null;
  notes: string | null;
  is_active: boolean;
};

export type CustomerPayload = {
  full_name: string;
  phone: string;
  email?: string | null;
  address?: string | null;
  notes?: string | null;
};

export type CustomerUpdatePayload = CustomerPayload & {
  is_active: boolean;
};

export function listCustomers(): Promise<CustomerRecord[]> {
  return apiRequest<CustomerRecord[]>('/api/customers', { method: 'GET' });
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
