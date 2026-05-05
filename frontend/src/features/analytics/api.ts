import { apiRequest } from '../../lib/api';

export interface AdvancedBISummary {
  total_sales: number;
  total_paid: number;
  total_remaining: number;
  record_count: number;
  department_breakdown: Array<{
    label: string;
    sales: number;
    count: number;
  }>;
}

export interface AdvancedBIRecord {
  booking_id: string;
  booking_line_id: string;
  booking_number: string;
  booking_date: string;
  customer_name: string;
  customer_phone: string;
  department_name: string;
  service_name: string;
  service_date: string;
  line_price: number;
  paid_amount: number;
  remaining_amount: number;
  booking_status: string;
  line_status: string;
  payment_method?: string;
  dress_name?: string | null;
  dress_code?: string | null;
  customer_address?: string | null;
}

export interface AdvancedBIResponse {
  summary: AdvancedBISummary;
  records: AdvancedBIRecord[];
}

export const getAdvancedBIReport = async (
  dateFrom: string,
  dateTo: string,
  branchId?: string
): Promise<AdvancedBIResponse> => {
  const params = new URLSearchParams({
    date_from: dateFrom,
    date_to: dateTo,
  });
  if (branchId) params.append('branch_id', branchId);

  return apiRequest<AdvancedBIResponse>(`/api/reports/advanced-bi?${params.toString()}`);
};
