import { apiRequest } from '../../lib/api';

export type FinanceMetricItem = {
  label: string;
  value: number;
};

export type FinanceCountItem = {
  label: string;
  count: number;
};

export type FinanceDashboardResponse = {
  total_income: number;
  total_remaining: number;
  total_bookings: number;
  daily_income: FinanceMetricItem[];
  department_income: FinanceMetricItem[];
  top_services: FinanceCountItem[];
};

export function getFinanceDashboard(branchId?: string | null): Promise<FinanceDashboardResponse> {
  const url = branchId ? `/api/dashboard/finance?branch_id=${encodeURIComponent(branchId)}` : '/api/dashboard/finance';
  return apiRequest<FinanceDashboardResponse>(url, { method: 'GET' });
}
