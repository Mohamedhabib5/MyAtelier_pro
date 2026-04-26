import { Alert, Stack } from '@mui/material';
import { useMemo } from 'react';

import { PaymentEditorDialog } from '../features/payments/PaymentEditorDialog';
import { PaymentsOverviewSection } from '../features/payments/PaymentsOverviewSection';
import { PaymentsPageHeader } from '../features/payments/PaymentsPageHeader';
import { PaymentsTableSection } from '../features/payments/PaymentsTableSection';
import { PaymentUpdateOverrideDialog } from '../features/payments/PaymentUpdateOverrideDialog';
import { PaymentVoidDialog } from '../features/payments/PaymentVoidDialog';
import { usePaymentActions } from '../features/payments/usePaymentActions';
import { usePaymentsPageState, type PaymentSortField } from '../features/payments/usePaymentsPageState';
import { usePaymentsText } from '../text/payments';
import type { PaymentExportFilters } from '../features/exports/api';

export function PaymentsPage() {
  const paymentsText = usePaymentsText();
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

  const { startNewFromTarget, openEditDocument, handleSave, submitVoid, confirmUpdateOverride, saving } = usePaymentActions({
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
      />

      <PaymentsTableSection
        rows={paymentRows}
        total={paymentTotal}
        loading={paymentsQuery.isLoading}
        tableSearchInput={tableSearchInput}
        onTableSearchChange={(v) => { setTableSearchInput(v); setPage(0); }}
        statusFilter={statusFilter}
        onStatusFilterChange={(v) => { setStatusFilter(v); setPage(0); }}
        documentKindFilter={documentKindFilter}
        onDocumentKindFilterChange={(v) => { setDocumentKindFilter(v); setPage(0); }}
        dateFrom={dateFrom}
        onDateFromChange={(v) => { setDateFrom(v); setPage(0); }}
        dateTo={dateTo}
        onDateToChange={(v) => { setDateTo(v); setPage(0); }}
        page={page}
        pageSize={pageSize}
        onPageChange={setPage}
        onPageSizeChange={(v) => { setPageSize(v); setPage(0); }}
        sortBy={sortBy}
        sortDir={sortDir}
        exportFilters={activeExportFilters}
        onSortChange={(b, d) => { setSortBy(b as PaymentSortField); setSortDir(d); setPage(0); }}
        onOpenEdit={(row) => { setCreatingNew(false); openEditDocument(row); }}
        onOpenVoid={setVoidingPayment}
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
