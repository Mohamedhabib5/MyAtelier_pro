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
};

export type BookingDocumentRecord = BookingSummaryRecord & {
  lines: BookingLineRecord[];
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
  booking_date?: string | null;
  notes?: string | null;
  lines: BookingLinePayload[];
};

export function listBookings(): Promise<BookingSummaryRecord[]> {
  return apiRequest<BookingSummaryRecord[]>('/api/bookings', { method: 'GET' });
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
