import { apiRequest } from "../../lib/api";

export type ReconciliationItemRecord = {
  id: string;
  payment_document_id: string;
  payment_number: string | null;
  expected_amount: number;
  actual_amount: number;
  is_reconciled: boolean;
};

export type ReconciliationRecord = {
  id: string;
  company_id: string;
  branch_id: string;
  reconciliation_date: string;
  start_date: string | null;
  end_date: string | null;
  payment_method_id: string;
  payment_method_name: string | null;
  receiver_name: string | null;
  total_expected_amount: number;
  total_actual_amount: number;
  difference_amount: number;
  status: string;
  notes: string | null;
  created_at: string;
  is_latest: boolean;
  items: ReconciliationItemRecord[];
};

export type PendingPaymentRecord = {
  id: string;
  payment_number: string;
  payment_date: string;
  customer_name: string;
  direct_amount: number;
  notes: string | null;
};

export type ReconciliationCreatePayload = {
  payment_method_id: string;
  start_date: string;
  end_date: string;
  receiver_name?: string | null;
  notes?: string | null;
  items: {
    payment_document_id: string;
    actual_amount: number;
  }[];
};

export type ReconciliationUpdatePayload = {
  receiver_name?: string | null;
  notes?: string | null;
};

export function listReconciliations(): Promise<ReconciliationRecord[]> {
  return apiRequest<ReconciliationRecord[]>("/api/reconciliations", { method: "GET" });
}

export function getPendingPayments(
  paymentMethodId: string,
  startDate: string,
  endDate: string
): Promise<PendingPaymentRecord[]> {
  const params = new URLSearchParams({
    payment_method_id: paymentMethodId,
    start_date: startDate,
    end_date: endDate,
  });
  return apiRequest<PendingPaymentRecord[]>(`/api/reconciliations/pending?${params.toString()}`, {
    method: "GET",
  });
}

export function createReconciliation(payload: ReconciliationCreatePayload): Promise<ReconciliationRecord> {
  return apiRequest<ReconciliationRecord>("/api/reconciliations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateReconciliation(
  id: string,
  payload: ReconciliationUpdatePayload
): Promise<ReconciliationRecord> {
  return apiRequest<ReconciliationRecord>(`/api/reconciliations/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteReconciliation(id: string): Promise<void> {
  return apiRequest<void>(`/api/reconciliations/${id}`, {
    method: "DELETE",
  });
}
