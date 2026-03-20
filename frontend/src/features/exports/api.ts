import { apiRequest } from '../../lib/api';

export type ExportScheduleRecord = {
  id: string;
  name: string;
  export_type: string;
  cadence: string;
  branch_id: string | null;
  branch_name: string | null;
  next_run_on: string;
  last_run_at: string | null;
  is_active: boolean;
};

export type CreateExportSchedulePayload = {
  name: string;
  export_type: string;
  cadence: string;
  start_on?: string | null;
};

export type ExportScheduleRunResult = {
  schedule: ExportScheduleRecord;
  run_url: string;
};

function withQuery(url: string, key: string, value?: string | null): string {
  if (!value) return url;
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}${key}=${encodeURIComponent(value)}`;
}

export function getCustomersExportUrl(): string {
  return '/api/exports/customers.csv';
}

export function getBookingsExportUrl(branchId?: string | null): string {
  return withQuery('/api/exports/bookings.csv', 'branch_id', branchId);
}

export function getBookingLinesExportUrl(branchId?: string | null): string {
  return withQuery('/api/exports/booking-lines.csv', 'branch_id', branchId);
}

export function getPaymentsExportUrl(branchId?: string | null): string {
  return withQuery('/api/exports/payment-documents.csv', 'branch_id', branchId);
}

export function getPaymentAllocationsExportUrl(branchId?: string | null): string {
  return withQuery('/api/exports/payment-allocations.csv', 'branch_id', branchId);
}

export function getFinancePrintUrl(branchId?: string | null): string {
  return withQuery('/print/finance', 'branchId', branchId);
}

export function getReportsPrintUrl(branchId?: string | null): string {
  return withQuery('/print/reports', 'branchId', branchId);
}

export function listExportSchedules(): Promise<ExportScheduleRecord[]> {
  return apiRequest<ExportScheduleRecord[]>('/api/exports/schedules', { method: 'GET' });
}

export function createExportSchedule(payload: CreateExportSchedulePayload): Promise<ExportScheduleRecord> {
  return apiRequest<ExportScheduleRecord>('/api/exports/schedules', { method: 'POST', body: JSON.stringify(payload) });
}

export function runExportSchedule(scheduleId: string): Promise<ExportScheduleRunResult> {
  return apiRequest<ExportScheduleRunResult>(`/api/exports/schedules/${scheduleId}/run`, { method: 'POST' });
}

export function toggleExportSchedule(scheduleId: string): Promise<{ schedule: ExportScheduleRecord }> {
  return apiRequest<{ schedule: ExportScheduleRecord }>(`/api/exports/schedules/${scheduleId}/toggle`, { method: 'POST' });
}
