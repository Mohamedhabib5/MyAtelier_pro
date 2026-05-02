import { apiRequest } from '../../lib/api';

export type BookingLineRecord = {
  id: string;
  booking_id: string;
  line_number: number;
  department_id: string;
  department_name: string;
  service_id: string;
  service_name: string;
  dress_id: string | null;
  dress_code: string | null;
  service_date: string;
  suggested_price: number;
  line_price: number;
  paid_total: number;
  remaining_amount: number;
  payment_state: string;
  status: string;
  revenue_journal_entry_id: string | null;
  revenue_journal_entry_number: string | null;
  revenue_journal_entry_status: string | null;
  revenue_recognized_at: string | null;
  notes: string | null;
  is_locked: boolean;
};

export type BookingSummaryRecord = {
  id: string;
  company_id: string;
  branch_id: string;
  branch_name: string;
  booking_number: string;
  customer_id: string;
  customer_name: string;
  booking_date: string;
  status: string;
  line_count: number;
  service_summary: string;
  next_service_date: string | null;
  total_amount: number;
  paid_total: number;
  remaining_amount: number;
  notes: string | null;
  external_code: string | null;
};

export type BookingDocumentRecord = BookingSummaryRecord & {
  lines: BookingLineRecord[];
};

export type BookingTablePage = {
  items: BookingSummaryRecord[];
  total: number;
  page: number;
  page_size: number;
};

export type BookingTableQuery = {
  search?: string;
  status?: string;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortDir?: 'asc' | 'desc';
};

export type CalendarEventRecord = {
  id: string;
  booking_id: string;
  title: string;
  start: string;
  end: string;
  status: string;
  department_name: string;
  service_name: string;
  customer_name: string;
  booking_number: string;
};

export type CalendarQuery = {
  dateFrom?: string;
  dateTo?: string;
  departmentIds?: string[];
  serviceIds?: string[];
  dateMode?: 'service' | 'reservation';
};

export type BookingLinePayload = {
  id?: string | null;
  department_id: string;
  service_id: string;
  service_date: string;
  dress_id?: string | null;
  suggested_price?: number | null;
  line_price: number;
  initial_payment_amount?: number | null;
  status: string;
  notes?: string | null;
};

export type BookingDocumentPayload = {
  customer_id: string;
  initial_payment_method_id: string | null;
  booking_date: string | null;
  notes: string | null;
  external_code: string | null;
  lines: BookingLinePayload[];
};

export type BookingCompensationRequest = {
  department_id: string;
  service_id: string;
  amount: number;
  notes?: string;
};

export function listBookings(): Promise<BookingSummaryRecord[]> {
  return apiRequest<BookingSummaryRecord[]>('/api/bookings', { method: 'GET' });
}

export function listBookingsPage(query: BookingTableQuery): Promise<BookingTablePage> {
  const params = new URLSearchParams();
  if (query.search?.trim()) params.set('search', query.search.trim());
  if (query.status?.trim()) params.set('status', query.status.trim());
  if (query.dateFrom) params.set('date_from', query.dateFrom);
  if (query.dateTo) params.set('date_to', query.dateTo);
  if (query.page) params.set('page', String(query.page));
  if (query.pageSize) params.set('page_size', String(query.pageSize));
  if (query.sortBy) params.set('sort_by', query.sortBy);
  if (query.sortDir) params.set('sort_dir', query.sortDir);
  const suffix = params.toString() ? `?${params.toString()}` : '';
  return apiRequest<BookingTablePage>(`/api/bookings/table${suffix}`, { method: 'GET' });
}

export function getBooking(bookingId: string): Promise<BookingDocumentRecord> {
  return apiRequest<BookingDocumentRecord>(`/api/bookings/${bookingId}`, { method: 'GET' });
}

export function createBooking(payload: BookingDocumentPayload): Promise<BookingDocumentRecord> {
  return apiRequest<BookingDocumentRecord>('/api/bookings', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateBooking(bookingId: string, payload: BookingDocumentPayload): Promise<BookingDocumentRecord> {
  return apiRequest<BookingDocumentRecord>(`/api/bookings/${bookingId}`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function completeBookingLine(bookingId: string, lineId: string): Promise<BookingDocumentRecord> {
  return apiRequest<BookingDocumentRecord>(`/api/bookings/${bookingId}/lines/${lineId}/complete`, { method: 'POST' });
}

export function cancelBookingLine(bookingId: string, lineId: string): Promise<BookingDocumentRecord> {
  return apiRequest<BookingDocumentRecord>(`/api/bookings/${bookingId}/lines/${lineId}/cancel`, { method: 'POST' });
}

export function createCompensationBooking(bookingId: string, payload: BookingCompensationRequest): Promise<BookingDocumentRecord> {
  return apiRequest<BookingDocumentRecord>(`/api/bookings/${bookingId}/compensate`, { method: 'POST', body: JSON.stringify(payload) });
}

export function reverseBookingLineRevenue(
  bookingId: string,
  lineId: string,
  options?: { overrideLock?: boolean; overrideReason?: string | null },
): Promise<BookingDocumentRecord> {
  const params = new URLSearchParams();
  if (options?.overrideLock) params.set('override_lock', 'true');
  if (options?.overrideReason?.trim()) params.set('override_reason', options.overrideReason.trim());
  const suffix = params.toString() ? `?${params.toString()}` : '';
  return apiRequest<BookingDocumentRecord>(`/api/bookings/${bookingId}/lines/${lineId}/reverse-revenue${suffix}`, { method: 'POST' });
}

export function listCalendarEvents(query: CalendarQuery): Promise<CalendarEventRecord[]> {
  const params = new URLSearchParams();
  if (query.dateFrom) params.set('date_from', query.dateFrom);
  if (query.dateTo) params.set('date_to', query.dateTo);
  if (query.departmentIds?.length) {
    query.departmentIds.forEach(id => params.append('department_id', id));
  }
  if (query.serviceIds?.length) {
    query.serviceIds.forEach(id => params.append('service_id', id));
  }
  if (query.dateMode) params.set('date_mode', query.dateMode);
  const suffix = params.toString() ? `?${params.toString()}` : '';
  return apiRequest<CalendarEventRecord[]>(`/api/bookings/calendar/events${suffix}`, { method: 'GET' });
}
