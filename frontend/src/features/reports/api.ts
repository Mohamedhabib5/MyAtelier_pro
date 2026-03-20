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
