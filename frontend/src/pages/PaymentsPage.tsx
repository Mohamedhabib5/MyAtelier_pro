import { Alert, Stack } from '@mui/material';
import { useMemo, useCallback } from 'react';

import { PaymentEditorDialog } from '../features/payments/PaymentEditorDialog';
import { PaymentsOverviewSection } from '../features/payments/PaymentsOverviewSection';
import { PaymentsPageHeader } from '../features/payments/PaymentsPageHeader';
import { PaymentsTableSection } from '../features/payments/PaymentsTableSection';
import { PaymentUpdateOverrideDialog } from '../features/payments/PaymentUpdateOverrideDialog';
import { PaymentVoidDialog } from '../features/payments/PaymentVoidDialog';
import { usePaymentActions } from '../features/payments/usePaymentActions';
import { usePaymentsPageState, type PaymentSortField } from '../features/payments/usePaymentsPageState';
import { usePaymentsText } from '../text/payments';
import { getPaymentsExcelUrl, getPaymentsExportUrl, type PaymentExportFilters } from '../features/exports/api';
import { downloadFile } from '../lib/api';
import { useAuth } from '../features/auth/AuthProvider';

export function PaymentsPage() {
  const paymentsText = usePaymentsText();
  const { user } = useAuth();
  const state = usePaymentsPageState();
  const {
    error, setError,
    creatingNew, setCreatingNew,
    searchText, setSearchText,
    selectedTarget, setSelectedTarget,
    editingPaymentId, setEditingPaymentId,
    voidingPayment, setVoidingPayment,
    voidDate, setVoidDate,
    voidReason, setVoidReason,
    voidOverrideLock, setVoidOverrideLock,
    voidOverrideReason, setVoidOverrideReason,
    tableSearchInput, setTableSearchInput,
    statusFilter, setStatusFilter,
    documentKindFilter, setDocumentKindFilter,
    dateFrom, setDateFrom,
    dateTo, setDateTo,
    page, setPage,
    pageSize, setPageSize,
    sortBy, setSortBy,
    sortDir, setSortDir,
    pendingUpdateOverridePayload, setPendingUpdateOverridePayload,
    initialKind, setInitialKind,
    deferredTableSearch,
    editorOpen,
    paymentsQuery,
    searchQuery,
    paymentMethodsQuery,
    paymentDocumentQuery,
    targetQuery,
    todayIso,
  } = state;

  function closeVoidDialog() {
    setVoidingPayment(null);
    setVoidDate(todayIso());
    setVoidReason('');
    setVoidOverrideLock(false);
    setVoidOverrideReason('');
  }

  function closePaymentEditor() {
    setCreatingNew(false);
    setSelectedTarget(null);
    setEditingPaymentId(null);
    setSearchText('');
    setPendingUpdateOverridePayload(null);
  }

  const { startNewFromTarget, openEditDocument, handleSave, submitVoid, confirmUpdateOverride, handleDeletePayment, saving } = usePaymentActions({
    editingPaymentId,
    voidingPayment,
    voidDate,
    voidReason,
    voidOverrideLock,
    voidOverrideReason,
    setError,
    closeBuilder: closePaymentEditor,
    closeVoidDialog,
    setPendingUpdateOverridePayload,
    setSelectedTarget,
    setEditingPaymentId,
  });

  const searchResults = useMemo(() => searchQuery.data ?? [], [searchQuery.data]);
  const paymentRows = paymentsQuery.data?.items ?? [];
  const paymentTotal = paymentsQuery.data?.total ?? 0;
  const editorLoading = targetQuery.isLoading || paymentMethodsQuery.isLoading || (Boolean(editingPaymentId) && paymentDocumentQuery.isLoading);
  
  const activeExportFilters: PaymentExportFilters = {
    search: deferredTableSearch || undefined,
    status: statusFilter || undefined,
    documentKind: documentKindFilter || undefined,
    dateFrom: dateFrom || undefined,
    dateTo: dateTo || undefined,
    sortBy,
    sortDir,
  };

  return (
    <Stack spacing={3}>
      <PaymentsPageHeader
        title={paymentsText.page.title}
        subtitle={paymentsText.page.subtitle}
        createLabel={paymentsText.page.addMultiAction}
        onCreate={() => {
          setError(null);
          setCreatingNew(true);
          setSelectedTarget(null);
          setEditingPaymentId(null);
          setSearchText('');
          setInitialKind('collection');
          setPendingUpdateOverridePayload(null);
          setTimeout(() => document.querySelector<HTMLInputElement>('input[data-payment-target-search-input="true"]')?.focus(), 0);
        }}
        secondCreateLabel={paymentsText.page.addRefundAction}
        onSecondCreate={() => {
          setError(null);
          setCreatingNew(true);
          setSelectedTarget(null);
          setEditingPaymentId(null);
          setSearchText('');
          setInitialKind('refund');
          setPendingUpdateOverridePayload(null);
          setTimeout(() => document.querySelector<HTMLInputElement>('input[data-payment-target-search-input="true"]')?.focus(), 0);
        }}
      />

      <PaymentsPageErrors state={state} />

      <PaymentsOverviewSection rows={paymentRows} total={paymentTotal} loading={paymentsQuery.isLoading} />

      <PaymentEditorDialog
        open={editorOpen}
        title={paymentsText.page.targetTitle}
        subtitle={paymentsText.page.targetSubtitle}
        loading={editorLoading}
        target={targetQuery.data ?? null}
        document={paymentDocumentQuery.data ?? null}
        paymentMethods={paymentMethodsQuery.data ?? []}
        saving={saving}
        searchTitle={paymentsText.page.searchTitle}
        searchSubtitle={paymentsText.page.searchSubtitle}
        searchLabel={paymentsText.page.searchLabel}
        searchHint={paymentsText.page.searchHint}
        searchText={searchText}
        searchResults={searchResults}
        searchLoading={searchQuery.isFetching}
        hasTargetSearch={searchText.trim().length > 0}
        searchLoadingLabel={paymentsText.page.searchLoading}
        searchNoResultsLabel={paymentsText.page.searchNoResults}
        customerKindLabel={paymentsText.page.searchCustomerTag}
        bookingKindLabel={paymentsText.page.searchBookingTag}
        onSearchTextChange={setSearchText}
        onSelectTarget={startNewFromTarget}
        onClose={closePaymentEditor}
        onSave={handleSave}
        initialKind={state.initialKind}
      />

      <PaymentsTableSection
        rows={paymentRows}
        total={paymentTotal}
        loading={paymentsQuery.isLoading}
        tableSearchInput={tableSearchInput}
        onTableSearchChange={useCallback((v) => { setTableSearchInput(v); setPage(0); }, [setTableSearchInput, setPage])}
        statusFilter={statusFilter}
        onStatusFilterChange={useCallback((v) => { setStatusFilter(v); setPage(0); }, [setStatusFilter, setPage])}
        documentKindFilter={documentKindFilter}
        onDocumentKindFilterChange={useCallback((v) => { setDocumentKindFilter(v); setPage(0); }, [setDocumentKindFilter, setPage])}
        dateFrom={dateFrom}
        onDateFromChange={useCallback((v) => { setDateFrom(v); setPage(0); }, [setDateFrom, setPage])}
        dateTo={dateTo}
        onDateToChange={useCallback((v) => { setDateTo(v); setPage(0); }, [setDateTo, setPage])}
        page={page}
        pageSize={pageSize}
        onPageChange={setPage}
        onPageSizeChange={useCallback((v) => { setPageSize(v); setPage(0); }, [setPageSize, setPage])}
        sortBy={sortBy}
        sortDir={sortDir}
        exportFilters={activeExportFilters}
        onSortChange={useCallback((b, d) => { setSortBy(b as PaymentSortField); setSortDir(d); setPage(0); }, [setSortBy, setSortDir, setPage])}
        onOpenEdit={useCallback((row) => { setCreatingNew(false); openEditDocument(row); }, [setCreatingNew, openEditDocument])}
        onOpenVoid={useCallback((row) => { setVoidingPayment(row); }, [setVoidingPayment])}
        onDelete={useCallback(async (row) => {
          if (window.confirm(`هل أنت متأكد من حذف السند ${row.payment_number} نهائياً؟ سيتم إلغاء القيود المحاسبية المرتبطة أيضاً.`)) {
            await handleDeletePayment(row.id);
          }
        }, [handleDeletePayment])}
        onExport={useCallback((format: 'csv' | 'xlsx', scope: 'page' | 'all') => {
          const isXlsx = format === 'xlsx';
          const urlFn = isXlsx ? getPaymentsExcelUrl : getPaymentsExportUrl;
          const exportPage = scope === 'page' ? page + 1 : undefined;
          const exportPageSize = scope === 'page' ? pageSize : undefined;
          
          downloadFile(urlFn(user?.active_branch_id, activeExportFilters, exportPage, exportPageSize));
        }, [user?.active_branch_id, page, pageSize, activeExportFilters])}
      />

      <PaymentVoidDialog
        open={Boolean(voidingPayment)}
        payment={voidingPayment}
        voidDate={voidDate}
        voidReason={voidReason}
        overrideLock={voidOverrideLock}
        overrideReason={voidOverrideReason}
        onClose={closeVoidDialog}
        onVoidDateChange={setVoidDate}
        onVoidReasonChange={setVoidReason}
        onOverrideLockChange={setVoidOverrideLock}
        onOverrideReasonChange={setVoidOverrideReason}
        onSubmit={() => void submitVoid()}
      />

      <PaymentUpdateOverrideDialog
        open={Boolean(pendingUpdateOverridePayload)}
        onClose={() => setPendingUpdateOverridePayload(null)}
        onConfirm={async (reason) => { await confirmUpdateOverride(reason, pendingUpdateOverridePayload); }}
      />
    </Stack>
  );
}

function PaymentsPageErrors({ state }: { state: any }) {
  const errors = [
    state.error,
    state.paymentsQuery.error?.message,
    state.searchQuery.error?.message,
    state.targetQuery.error?.message,
    state.paymentDocumentQuery.error?.message,
    state.paymentMethodsQuery.error?.message,
  ].filter(Boolean);

  if (errors.length === 0) return null;

  return (
    <Stack spacing={1}>
      {errors.map((err, i) => <Alert key={i} severity='error'>{err}</Alert>)}
    </Stack>
  );
}
