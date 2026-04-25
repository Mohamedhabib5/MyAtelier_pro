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

export type BookingExportFilters = {
  search?: string;
  status?: string;
  dateFrom?: string;
  dateTo?: string;
  sortBy?: string;
  sortDir?: 'asc' | 'desc';
};

export type PaymentExportFilters = {
  search?: string;
  status?: string;
  documentKind?: string;
  dateFrom?: string;
  dateTo?: string;
  sortBy?: string;
  sortDir?: 'asc' | 'desc';
};

function buildQuery(entries: Array<[string, string | undefined | null]>): string {
  const params = new URLSearchParams();
  for (const [key, value] of entries) {
    if (!value?.trim()) continue;
    params.set(key, value.trim());
  }
  const query = params.toString();
  return query ? `?${query}` : '';
}

function withBranch(baseUrl: string, branchId?: string | null): string {
  if (!branchId) return baseUrl;
  return `${baseUrl}?branch_id=${encodeURIComponent(branchId)}`;
}

function withSingleQuery(baseUrl: string, key: string, value?: string | null): string {
  if (!value) return baseUrl;
  return `${baseUrl}?${key}=${encodeURIComponent(value)}`;
}

export function getCustomersExportUrl(): string {
  return '/api/exports/customers.csv';
}

export function getCustomersExcelUrl(): string {
  return '/api/exports/customers.xlsx';
}

export function getBookingsExportUrl(branchId?: string | null, filters?: BookingExportFilters): string {
  const base = withBranch('/api/exports/bookings.csv', branchId);
  if (!filters) return base;
  const query = buildQuery([
    ['search', filters.search],
    ['status', filters.status],
    ['date_from', filters.dateFrom],
    ['date_to', filters.dateTo],
    ['sort_by', filters.sortBy],
    ['sort_dir', filters.sortDir],
  ]);
  if (!query) return base;
  const separator = base.includes('?') ? '&' : '?';
  return `${base}${separator}${query.slice(1)}`;
}

export function getBookingsExcelUrl(branchId?: string | null, filters?: BookingExportFilters): string {
  const base = withBranch('/api/exports/bookings.xlsx', branchId);
  if (!filters) return base;
  const query = buildQuery([
    ['search', filters.search],
    ['status', filters.status],
    ['date_from', filters.dateFrom],
    ['date_to', filters.dateTo],
    ['sort_by', filters.sortBy],
    ['sort_dir', filters.sortDir],
  ]);
  if (!query) return base;
  const separator = base.includes('?') ? '&' : '?';
  return `${base}${separator}${query.slice(1)}`;
}

export function getBookingLinesExportUrl(branchId?: string | null, filters?: BookingExportFilters): string {
  const base = withBranch('/api/exports/booking-lines.csv', branchId);
  if (!filters) return base;
  const query = buildQuery([
    ['search', filters.search],
    ['status', filters.status],
    ['date_from', filters.dateFrom],
    ['date_to', filters.dateTo],
    ['sort_by', filters.sortBy],
    ['sort_dir', filters.sortDir],
  ]);
  if (!query) return base;
  const separator = base.includes('?') ? '&' : '?';
  return `${base}${separator}${query.slice(1)}`;
}

export function getBookingLinesExcelUrl(branchId?: string | null, filters?: BookingExportFilters): string {
  const base = withBranch('/api/exports/booking-lines.xlsx', branchId);
  if (!filters) return base;
  const query = buildQuery([
    ['search', filters.search],
    ['status', filters.status],
    ['date_from', filters.dateFrom],
    ['date_to', filters.dateTo],
    ['sort_by', filters.sortBy],
    ['sort_dir', filters.sortDir],
  ]);
  if (!query) return base;
  const separator = base.includes('?') ? '&' : '?';
  return `${base}${separator}${query.slice(1)}`;
}

export function getPaymentsExportUrl(branchId?: string | null, filters?: PaymentExportFilters): string {
  const base = withBranch('/api/exports/payment-documents.csv', branchId);
  if (!filters) return base;
  const query = buildQuery([
    ['search', filters.search],
    ['status', filters.status],
    ['document_kind', filters.documentKind],
    ['date_from', filters.dateFrom],
    ['date_to', filters.dateTo],
    ['sort_by', filters.sortBy],
    ['sort_dir', filters.sortDir],
  ]);
  if (!query) return base;
  const separator = base.includes('?') ? '&' : '?';
  return `${base}${separator}${query.slice(1)}`;
}

export function getPaymentsExcelUrl(branchId?: string | null, filters?: PaymentExportFilters): string {
  const base = withBranch('/api/exports/payment-documents.xlsx', branchId);
  if (!filters) return base;
  const query = buildQuery([
    ['search', filters.search],
    ['status', filters.status],
    ['document_kind', filters.documentKind],
    ['date_from', filters.dateFrom],
    ['date_to', filters.dateTo],
    ['sort_by', filters.sortBy],
    ['sort_dir', filters.sortDir],
  ]);
  if (!query) return base;
  const separator = base.includes('?') ? '&' : '?';
  return `${base}${separator}${query.slice(1)}`;
}

export function getPaymentAllocationsExportUrl(branchId?: string | null, filters?: PaymentExportFilters): string {
  const base = withBranch('/api/exports/payment-allocations.csv', branchId);
  if (!filters) return base;
  const query = buildQuery([
    ['search', filters.search],
    ['status', filters.status],
    ['document_kind', filters.documentKind],
    ['date_from', filters.dateFrom],
    ['date_to', filters.dateTo],
    ['sort_by', filters.sortBy],
    ['sort_dir', filters.sortDir],
  ]);
  if (!query) return base;
  const separator = base.includes('?') ? '&' : '?';
  return `${base}${separator}${query.slice(1)}`;
}

export function getPaymentAllocationsExcelUrl(branchId?: string | null, filters?: PaymentExportFilters): string {
  const base = withBranch('/api/exports/payment-allocations.xlsx', branchId);
  if (!filters) return base;
  const query = buildQuery([
    ['search', filters.search],
    ['status', filters.status],
    ['document_kind', filters.documentKind],
    ['date_from', filters.dateFrom],
    ['date_to', filters.dateTo],
    ['sort_by', filters.sortBy],
    ['sort_dir', filters.sortDir],
  ]);
  if (!query) return base;
  const separator = base.includes('?') ? '&' : '?';
  return `${base}${separator}${query.slice(1)}`;
}

export function getCustodyExportUrl(): string {
  return '/api/exports/custody.csv';
}

export function getCustodyExcelUrl(): string {
  return '/api/exports/custody.xlsx';
}

export function getFinancePrintUrl(branchId?: string | null): string {
  return withSingleQuery('/print/finance', 'branchId', branchId);
}

export function getReportsPrintUrl(branchId?: string | null): string {
  return withSingleQuery('/print/reports', 'branchId', branchId);
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
