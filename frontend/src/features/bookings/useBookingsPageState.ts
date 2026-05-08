import { useDeferredValue, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { type BookingSortField } from './BookingsTableSection';
import { type BookingSummaryRecord, type BookingCancellationPayload } from './api';

export function useBookingsPageState() {
  const [searchParams] = useSearchParams();
  const urlEditId = searchParams.get('edit');

  const [error, setError] = useState<string | null>(null);
  const [editingBookingId, setEditingBookingId] = useState<string | null>(urlEditId);
  const [creatingNew, setCreatingNew] = useState(false);
  const [searchInput, setSearchInput] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [sortBy, setSortBy] = useState<BookingSortField>('booking_date');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [reverseOverrideLineId, setReverseOverrideLineId] = useState<string | null>(null);
  const [cancellingBooking, setCancellingBooking] = useState<BookingSummaryRecord | null>(null);
  const [cancellingLineId, setCancellingLineId] = useState<string | null>(null);
  const [editorMode, setEditorMode] = useState<'edit' | 'cancel'>('edit');
  const [pendingCancelPayload, setPendingCancelPayload] = useState<{ bookingId: string; lineId?: string; payload: BookingCancellationPayload } | null>(null);
  
  const deferredSearch = useDeferredValue(searchInput.trim());

  return {
    error, setError,
    editingBookingId, setEditingBookingId,
    creatingNew, setCreatingNew,
    searchInput, setSearchInput,
    statusFilter, setStatusFilter,
    dateFrom, setDateFrom,
    dateTo, setDateTo,
    page, setPage,
    pageSize, setPageSize,
    sortBy, setSortBy,
    sortDir, setSortDir,
    reverseOverrideLineId, setReverseOverrideLineId,
    cancellingBooking, setCancellingBooking,
    cancellingLineId, setCancellingLineId,
    editorMode, setEditorMode,
    pendingCancelPayload, setPendingCancelPayload,
    deferredSearch,
  };
}
