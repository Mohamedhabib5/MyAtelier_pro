import { useCallback } from 'react';
import { Alert, Stack } from '@mui/material';
import { PeriodLockOverrideDialog } from '../components/PeriodLockOverrideDialog';
import { BookingCancellationDialog } from '../features/bookings/BookingCancellationDialog';
import { BookingEditorDialog } from '../features/bookings/BookingEditorDialog';
import { BookingsPageHeader } from '../features/bookings/BookingsPageHeader';
import { BookingRevenueOverrideDialog } from '../features/bookings/BookingRevenueOverrideDialog';
import { BookingsTableSection } from '../features/bookings/BookingsTableSection';
import { useBookingActions } from '../features/bookings/useBookingActions';
import { getBookingsExcelUrl, getBookingsExportUrl } from '../features/exports/api';
import { useLanguage } from '../features/language/LanguageProvider';
import { downloadFile } from '../lib/api';
import { useBookingsText } from '../text/bookings';
import { useBookingsPageState } from '../features/bookings/useBookingsPageState';
import { useBookingsQueries } from '../features/bookings/useBookingsQueries';
import { useAuth } from '../features/auth/AuthProvider';

export function BookingsPage() {
  const { language } = useLanguage();
  const bookingsText = useBookingsText();
  
  const state = useBookingsPageState();
  const { user } = useAuth();
  const queries = useBookingsQueries({
    deferredSearch: state.deferredSearch,
    statusFilter: state.statusFilter,
    dateFrom: state.dateFrom,
    dateTo: state.dateTo,
    page: state.page,
    pageSize: state.pageSize,
    sortBy: state.sortBy,
    sortDir: state.sortDir,
    editingBookingId: state.editingBookingId,
  });

  function closeEditor() {
    state.setCreatingNew(false);
    state.setEditingBookingId(null);
    state.setEditorMode('edit');
  }

  const {
    handleSave,
    handleCreateCustomer,
    handleCompleteLine,
    handleCancelLine,
    handleReverseRevenueLine,
    handleConfirmRevenueOverride,
    handleCancelWorkflow,
    handleConfirmCancelOverride,
    handleDeleteBooking,
    handleDeleteLine,
    handleUndoCancellation,
    saving,
  } = useBookingActions({
    creatingNew: state.creatingNew,
    editingBookingId: state.editingBookingId,
    reverseOverrideLineId: state.reverseOverrideLineId,
    setError: state.setError,
    setReverseOverrideLineId: state.setReverseOverrideLineId,
    setPendingCancelPayload: state.setPendingCancelPayload,
    closeEditor,
  });

  const document = state.creatingNew ? null : queries.bookingDocumentQuery.data ?? null;
  const editorOpen = state.creatingNew || Boolean(state.editingBookingId);
  const bookingRows = queries.bookingsQuery.data?.items ?? [];
  const bookingTotal = queries.bookingsQuery.data?.total ?? 0;

  return (
    <Stack spacing={3}>
      <BookingsPageHeader
        title={bookingsText.page.title}
        subtitle={bookingsText.page.subtitle}
        createLabel={bookingsText.page.createDocument}
        onCreate={() => {
          state.setCreatingNew(true);
          state.setEditingBookingId(null);
          state.setEditorMode('edit');
        }}
      />
      {state.error ? <Alert severity='error'>{state.error}</Alert> : null}
      {queries.paymentMethodsQuery.error instanceof Error ? <Alert severity='error'>{queries.paymentMethodsQuery.error.message}</Alert> : null}

      <BookingsTableSection
        language={language}
        rows={bookingRows}
        total={bookingTotal}
        loading={queries.bookingsQuery.isLoading}
        searchInput={state.searchInput}
        onSearchChange={useCallback((value) => {
          state.setSearchInput(value);
          state.setPage(0);
        }, [state.setSearchInput, state.setPage])}
        statusFilter={state.statusFilter}
        onStatusFilterChange={useCallback((value) => {
          state.setStatusFilter(value);
          state.setPage(0);
        }, [state.setStatusFilter, state.setPage])}
        dateFrom={state.dateFrom}
        onDateFromChange={useCallback((value) => {
          state.setDateFrom(value);
          state.setPage(0);
        }, [state.setDateFrom, state.setPage])}
        dateTo={state.dateTo}
        onDateToChange={useCallback((value) => {
          state.setDateTo(value);
          state.setPage(0);
        }, [state.setDateTo, state.setPage])}
        page={state.page}
        pageSize={state.pageSize}
        onPageChange={state.setPage}
        onPageSizeChange={useCallback((nextPageSize) => {
          state.setPageSize(nextPageSize);
          state.setPage(0);
        }, [state.setPageSize, state.setPage])}
        sortBy={state.sortBy}
        sortDir={state.sortDir}
        onSortChange={useCallback((nextSortBy, nextSortDir) => {
          state.setSortBy(nextSortBy);
          state.setSortDir(nextSortDir);
          state.setPage(0);
        }, [state.setSortBy, state.setSortDir, state.setPage])}
        exportFilters={{ search: state.deferredSearch || undefined, status: state.statusFilter || undefined, dateFrom: state.dateFrom || undefined, dateTo: state.dateTo || undefined, sortBy: state.sortBy, sortDir: state.sortDir }}
        onOpenEdit={useCallback((record) => {
          state.setCreatingNew(false);
          state.setEditingBookingId(record.id);
          state.setEditorMode('edit');
        }, [state.setCreatingNew, state.setEditingBookingId, state.setEditorMode])}
        onOpenCancel={useCallback((record) => {
          state.setCreatingNew(false);
          state.setEditingBookingId(record.id);
          state.setEditorMode('cancel');
        }, [state.setCreatingNew, state.setEditingBookingId, state.setEditorMode])}
        onDelete={useCallback(async (record: any) => {
          if (window.confirm(`هل أنت متأكد من حذف الحجز ${record.booking_number} نهائياً؟ لا يمكن التراجع عن هذه العملية.`)) {
            await handleDeleteBooking(record.id);
          }
        }, [handleDeleteBooking])}
        onExport={useCallback((format: 'csv' | 'xlsx', scope: 'page' | 'all') => {
          const isXlsx = format === 'xlsx';
          const urlFn = isXlsx ? getBookingsExcelUrl : getBookingsExportUrl;
          const exportPage = scope === 'page' ? state.page + 1 : undefined;
          const exportPageSize = scope === 'page' ? state.pageSize : undefined;
          
          downloadFile(urlFn(user?.active_branch_id, {
            search: state.deferredSearch || undefined,
            status: state.statusFilter || undefined,
            dateFrom: state.dateFrom || undefined,
            dateTo: state.dateTo || undefined,
            sortBy: state.sortBy,
            sortDir: state.sortDir,
          }, exportPage, exportPageSize));
        }, [user?.active_branch_id, state.page, state.pageSize, state.deferredSearch, state.statusFilter, state.dateFrom, state.dateTo, state.sortBy, state.sortDir])}
      />

      <BookingEditorDialog
        open={editorOpen}
        title={bookingsText.page.editorTitle}
        subtitle={bookingsText.page.editorSubtitle}
        loading={queries.bookingDocumentQuery.isLoading}
        creatingNew={state.creatingNew}
        document={document}
        customers={queries.customersQuery.data ?? []}
        departments={queries.departmentsQuery.data ?? []}
        services={queries.servicesQuery.data ?? []}
        dresses={queries.dressesQuery.data ?? []}
        paymentMethods={queries.paymentMethodsQuery.data ?? []}
        error={state.error}
        saving={saving}
        onClose={closeEditor}
        onSave={handleSave}
        onCreateCustomer={handleCreateCustomer}
        onCompleteLine={handleCompleteLine}
        onCancelLine={async (lineId) => {
          const bookingSummary = bookingRows.find(b => b.id === state.editingBookingId);
          if (bookingSummary) {
            state.setCancellingBooking(bookingSummary);
            state.setCancellingLineId(lineId);
          }
        }}
        onReverseRevenueLine={handleReverseRevenueLine}
        onDeleteLine={async (lineId) => {
          if (window.confirm('هل أنت متأكد من حذف هذا السطر نهائياً؟')) {
            await handleDeleteLine(lineId);
          }
        }}
        onUndoCancellation={async (lineIds) => {
          if (window.confirm('هل أنت متأكد من التراجع عن إلغاء هذه السطور؟ سيتم حذف سندات الرد المرتبطة آلياً.')) {
            await handleUndoCancellation(lineIds);
          }
        }}
        mode={state.editorMode}
        onCancelFull={() => {
          const bookingSummary = bookingRows.find(b => b.id === state.editingBookingId);
          if (bookingSummary) {
            state.setCancellingBooking(bookingSummary);
            state.setCancellingLineId(null);
          }
        }}
      />

      <BookingRevenueOverrideDialog
        open={Boolean(state.reverseOverrideLineId)}
        onClose={() => state.setReverseOverrideLineId(null)}
        onConfirm={handleConfirmRevenueOverride}
      />

      <PeriodLockOverrideDialog
        open={Boolean(state.pendingCancelPayload)}
        titleAr='Override لإلغاء حجز'
        titleEn='Override booking cancellation'
        descriptionAr='تاريخ الإلغاء يقع في فترة محاسبية مقفولة. أدخل سبب Override للتنفيذ.'
        descriptionEn='Cancellation date is in a locked period. Enter override reason to proceed.'
        onClose={() => state.setPendingCancelPayload(null)}
        onConfirm={async (reason) => { await handleConfirmCancelOverride(reason, state.pendingCancelPayload); }}
      />

      <BookingCancellationDialog
        open={Boolean(state.cancellingBooking)}
        booking={state.cancellingBooking}
        detailedDocument={state.editingBookingId === state.cancellingBooking?.id ? queries.bookingDocumentQuery.data : undefined}
        lineId={state.cancellingLineId ?? undefined}
        paymentMethods={queries.paymentMethodsQuery.data ?? []}
        saving={saving}
        onClose={() => {
          state.setCancellingBooking(null);
          state.setCancellingLineId(null);
        }}
        onConfirm={async (payload) => {
          if (!state.cancellingBooking) return;
          let success = false;
          if (state.cancellingLineId) {
            await handleCancelLine(state.cancellingLineId, payload);
            success = true;
          } else {
            success = await handleCancelWorkflow(state.cancellingBooking.id, payload);
          }
          if (success) {
            state.setCancellingBooking(null);
            state.setCancellingLineId(null);
          }
        }}
      />
    </Stack>
  );
}
