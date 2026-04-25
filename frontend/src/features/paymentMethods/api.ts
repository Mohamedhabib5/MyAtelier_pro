import { apiRequest } from '../../lib/api';

export type PaymentMethodRecord = {
  id: string;
  company_id: string;
  created_by_user_id: string | null;
  updated_by_user_id: string | null;
  entity_version: number;
  code: string;
  name: string;
  is_active: boolean;
  display_order: number;
};

export type PaymentMethodStatusFilter = 'all' | 'active' | 'inactive';

export type PaymentMethodCreatePayload = {
  name: string;
  code?: string | null;
  is_active?: boolean;
};

export type PaymentMethodUpdatePayload = {
  name?: string | null;
  is_active?: boolean;
  display_order?: number;
};

export function listPaymentMethods(status: PaymentMethodStatusFilter = 'active'): Promise<PaymentMethodRecord[]> {
  return apiRequest<PaymentMethodRecord[]>(`/api/payment-methods?status=${status}`, { method: 'GET' });
}

export function createPaymentMethod(payload: PaymentMethodCreatePayload): Promise<PaymentMethodRecord> {
  return apiRequest<PaymentMethodRecord>('/api/payment-methods', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updatePaymentMethod(paymentMethodId: string, payload: PaymentMethodUpdatePayload): Promise<PaymentMethodRecord> {
  return apiRequest<PaymentMethodRecord>(`/api/payment-methods/${paymentMethodId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

