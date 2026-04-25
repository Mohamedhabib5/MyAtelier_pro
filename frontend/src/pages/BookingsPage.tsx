import { Alert, Stack } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useDeferredValue, useState } from 'react';

import { BookingEditorDialog } from '../features/bookings/BookingEditorDialog';
import { BookingsPageHeader } from '../features/bookings/BookingsPageHeader';
import { BookingRevenueOverrideDialog } from '../features/bookings/BookingRevenueOverrideDialog';
import { BookingsTableSection, type BookingSortField } from '../features/bookings/BookingsTableSection';
import { useBookingActions } from '../features/bookings/useBookingActions';
import {
  getBooking,
  listBookingsPage,
} from '../features/bookings/api';
import { listDepartments, listServices } from '../features/catalog/api';
import { listCustomers } from '../features/customers/api';
import { listDresses } from '../features/dresses/api';
import { useLanguage } from '../features/language/LanguageProvider';
import { listPaymentMethods } from '../features/paymentMethods/api';
import { useBookingsText } from '../text/bookings';

export function BookingsPage() {
  const { language } = useLanguage();
  const bookingsText = useBookingsText();
  const [error, setError] = useState<string | null>(null);
  const [editingBookingId, setEditingBookingId] = useState<string | null>(null);
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
  const deferredSearch = useDeferredValue(searchInput.trim());

  const customersQuery = useQuery({ queryKey: ['customers'], queryFn: listCustomers });
  const departmentsQuery = useQuery({ queryKey: ['catalog', 'departments'], queryFn: listDepartments });
  const servicesQuery = useQuery({ queryKey: ['catalog', 'services'], queryFn: listServices });
  const dressesQuery = useQuery({ queryKey: ['dresses'], queryFn: listDresses });
  const paymentMethodsQuery = useQuery({ queryKey: ['payment-methods', 'active'], queryFn: () => listPaymentMethods('active') });
  const bookingsQuery = useQuery({
    queryKey: ['bookings', 'table', deferredSearch, statusFilter, dateFrom, dateTo, page, pageSize, sortBy, sortDir],
    queryFn: () =>
      listBookingsPage({
        search: deferredSearch || undefined,
        status: statusFilter || undefined,
        dateFrom: dateFrom || undefined,
        dateTo: dateTo || undefined,
        page: page + 1,
        pageSize,
        sortBy,
        sortDir,
      }),
  });
  const bookingDocumentQuery = useQuery({
    queryKey: ['bookings', editingBookingId],
    queryFn: () => getBooking(editingBookingId!),
    enabled: Boolean(editingBookingId),
  });

  function closeEditor() {
    setCreatingNew(false);
    setEditingBookingId(null);
  }
  const {
    handleSave,
    handleCreateCustomer,
    handleCompleteLine,
    handleCancelLine,
    handleReverseRevenueLine,
    handleConfirmRevenueOverride,
    saving,
  } = useBookingActions({
    creatingNew,
    editingBookingId,
    reverseOverrideLineId,
    setError,
    setReverseOverrideLineId,
    closeEditor,
  });

  const document = creatingNew ? null : bookingDocumentQuery.data ?? null;
  const editorOpen = creatingNew || Boolean(editingBookingId);
  const bookingRows = bookingsQuery.data?.items ?? [];
  const bookingTotal = bookingsQuery.data?.total ?? 0;

  return (
    <Stack spacing={3}>
      <BookingsPageHeader
        title={bookingsText.page.title}
        subtitle={bookingsText.page.subtitle}
        createLabel={bookingsText.page.createDocument}
        onCreate={() => {
          setCreatingNew(true);
          setEditingBookingId(null);
        }}
      />

      {error ? <Alert severity='error'>{error}</Alert> : null}
      {paymentMethodsQuery.error instanceof Error ? <Alert severity='error'>{paymentMethodsQuery.error.message}</Alert> : null}

      <BookingsTableSection
        language={language}
        rows={bookingRows}
        total={bookingTotal}
        loading={bookingsQuery.isLoading}
        searchInput={searchInput}
        onSearchChange={(value) => {
          setSearchInput(value);
          setPage(0);
        }}
        statusFilter={statusFilter}
        onStatusFilterChange={(value) => {
          setStatusFilter(value);
          setPage(0);
        }}
        dateFrom={dateFrom}
        onDateFromChange={(value) => {
          setDateFrom(value);
          setPage(0);
        }}
        dateTo={dateTo}
        onDateToChange={(value) => {
          setDateTo(value);
          setPage(0);
        }}
        page={page}
        pageSize={pageSize}
        onPageChange={setPage}
        onPageSizeChange={(nextPageSize) => {
          setPageSize(nextPageSize);
          setPage(0);
        }}
        sortBy={sortBy}
        sortDir={sortDir}
        onSortChange={(nextSortBy, nextSortDir) => {
          setSortBy(nextSortBy);
          setSortDir(nextSortDir);
          setPage(0);
        }}
        exportFilters={{
          search: deferredSearch || undefined,
          status: statusFilter || undefined,
          dateFrom: dateFrom || undefined,
          dateTo: dateTo || undefined,
          sortBy,
          sortDir,
        }}
        onOpenEdit={(record) => {
          setCreatingNew(false);
          setEditingBookingId(record.id);
        }}
      />

      <BookingEditorDialog
        open={editorOpen}
        title={bookingsText.page.editorTitle}
        subtitle={bookingsText.page.editorSubtitle}
        loading={bookingDocumentQuery.isLoading}
        creatingNew={creatingNew}
        document={document}
        customers={customersQuery.data ?? []}
        departments={departmentsQuery.data ?? []}
        services={servicesQuery.data ?? []}
        dresses={dressesQuery.data ?? []}
        paymentMethods={paymentMethodsQuery.data ?? []}
        saving={saving}
        onClose={closeEditor}
        onSave={handleSave}
        onCreateCustomer={handleCreateCustomer}
        onCompleteLine={handleCompleteLine}
        onCancelLine={handleCancelLine}
        onReverseRevenueLine={handleReverseRevenueLine}
      />

      <BookingRevenueOverrideDialog
        open={Boolean(reverseOverrideLineId)}
        onClose={() => setReverseOverrideLineId(null)}
        onConfirm={handleConfirmRevenueOverride}
      />
    </Stack>
  );
}
