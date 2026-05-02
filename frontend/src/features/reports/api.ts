import { apiRequest } from '../../lib/api';

export type SummaryMetric = {
  key: string;
  count: number;
};

export type ValueMetric = {
  key: string;
  value: number;
};

export type DepartmentCountMetric = {
  label: string;
  count: number;
};

export type UpcomingBookingItem = {
  booking_number: string;
  customer_name: string;
  service_name: string;
  service_date: string;
  status: string;
};

export type ReportsOverviewResponse = {
  active_customers: number;
  active_services: number;
  available_dresses: number;
  upcoming_bookings: number;
  booking_status_counts: SummaryMetric[];
  payment_type_totals: ValueMetric[];
  dress_status_counts: SummaryMetric[];
  department_service_counts: DepartmentCountMetric[];
  upcoming_booking_items: UpcomingBookingItem[];
};

export function getReportsOverview(branchId?: string | null): Promise<ReportsOverviewResponse> {
  const url = branchId ? `/api/reports/overview?branch_id=${encodeURIComponent(branchId)}` : '/api/reports/overview';
  return apiRequest<ReportsOverviewResponse>(url, { method: 'GET' });
}

// ---------------------------------------------------------------------------
// Comprehensive report
// ---------------------------------------------------------------------------

export type DailyIncomeItem = {
  date: string;
  amount: number;
};

export type TopClientItem = {
  customer_name: string;
  total_paid: number;
  booking_count: number;
};

export type ChartItem = {
  label: string;
  value: number;
};

export type CountItem = {
  label: string;
  count: number;
};

export type ComprehensiveReportFilters = {
  date_from: string;
  date_to: string;
  branch_id?: string | null;
};

export type ComprehensiveReportResponse = {
  date_from: string;
  date_to: string;
  total_collected: number;
  total_recognized: number;
  total_remaining: number;
  total_bookings: number;
  cancelled_bookings: number;
  cancellation_rate: number;
  daily_income: DailyIncomeItem[];
  department_income: ChartItem[];
  top_services: CountItem[];
  top_clients: TopClientItem[];
  booking_status_counts: SummaryMetric[];
};

export function getComprehensiveReport(
  filters: ComprehensiveReportFilters
): Promise<ComprehensiveReportResponse> {
  const params = new URLSearchParams({
    date_from: filters.date_from,
    date_to: filters.date_to,
  });
  if (filters.branch_id) params.set('branch_id', filters.branch_id);
  return apiRequest<ComprehensiveReportResponse>(`/api/reports/comprehensive?${params.toString()}`, {
    method: 'GET',
  });
}

// ---------------------------------------------------------------------------
// Detailed Lines report
// ---------------------------------------------------------------------------

export type DetailedReportRowResponse = {
  booking_id: string;
  booking_line_id: string;
  booking_number: string;
  external_code: string | null;
  booking_date: string;
  customer_name: string;
  customer_phone: string | null;
  customer_phone_2: string | null;
  department_name: string;
  service_name: string;
  dress_code: string | null;
  dress_name: string | null;
  service_date: string;
  line_price: number;
  paid_amount: number;
  remaining_amount: number;
  payment_method: string | null;
  payment_reference: string | null;
  payment_type: string | null;
  booking_status: string;
  line_status: string;
  custody_status: string | null;
  notes: string | null;
  created_by: string | null;
};

export function getDetailedLinesReport(
  filters: ComprehensiveReportFilters
): Promise<DetailedReportRowResponse[]> {
  const params = new URLSearchParams({
    date_from: filters.date_from,
    date_to: filters.date_to,
  });
  if (filters.branch_id) params.set('branch_id', filters.branch_id);
  return apiRequest<DetailedReportRowResponse[]>(`/api/reports/detailed-lines?${params.toString()}`, {
    method: 'GET',
  });
}
