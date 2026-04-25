import { Alert, Stack } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useDeferredValue, useMemo, useState } from 'react';

import type { PaymentExportFilters } from '../features/exports/api';
import { PaymentEditorDialog } from '../features/payments/PaymentEditorDialog';
import { PaymentsOverviewSection } from '../features/payments/PaymentsOverviewSection';
import { PaymentsPageHeader } from '../features/payments/PaymentsPageHeader';
import { PaymentsTableSection } from '../features/payments/PaymentsTableSection';
import { PaymentUpdateOverrideDialog } from '../features/payments/PaymentUpdateOverrideDialog';
import { PaymentVoidDialog } from '../features/payments/PaymentVoidDialog';
import { listPaymentMethods } from '../features/paymentMethods/api';
import { usePaymentActions } from '../features/payments/usePaymentActions';
import {
  getBookingPaymentTarget,
  getCustomerPaymentTarget,
  getPaymentDocument,
  listPaymentsPage,
  searchPaymentTargets,
  type PaymentDocumentPayload,
  type PaymentDocumentSummaryRecord,
  type PaymentTargetSearchRecord,
} from '../features/payments/api';
import { usePaymentsText } from '../text/payments';

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

type PaymentSortField = 'payment_date' | 'payment_number' | 'customer_name' | 'status' | 'document_kind';

export function PaymentsPage() {
  const paymentsText = usePaymentsText();
  const [error, setError] = useState<string | null>(null);
  const [creatingNew, setCreatingNew] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [selectedTarget, setSelectedTarget] = useState<PaymentTargetSearchRecord | null>(null);
  const [editingPaymentId, setEditingPaymentId] = useState<string | null>(null);
  const [voidingPayment, setVoidingPayment] = useState<PaymentDocumentSummaryRecord | null>(null);
  const [voidDate, setVoidDate] = useState(todayIso());
  const [voidReason, setVoidReason] = useState('');
  const [voidOverrideLock, setVoidOverrideLock] = useState(false);
  const [voidOverrideReason, setVoidOverrideReason] = useState('');
  const [tableSearchInput, setTableSearchInput] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [documentKindFilter, setDocumentKindFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [sortBy, setSortBy] = useState<PaymentSortField>('payment_date');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [pendingUpdateOverridePayload, setPendingUpdateOverridePayload] = useState<PaymentDocumentPayload | null>(null);
  const deferredTargetSearch = useDeferredValue(searchText);
  const deferredTableSearch = useDeferredValue(tableSearchInput.trim());
  const editorOpen = creatingNew || Boolean(editingPaymentId);

  const paymentsQuery = useQuery({
    queryKey: ['payments', 'table', deferredTableSearch, statusFilter, documentKindFilter, dateFrom, dateTo, page, pageSize, sortBy, sortDir],
    queryFn: () =>
      listPaymentsPage({
        search: deferredTableSearch || undefined,
        status: statusFilter || undefined,
        documentKind: documentKindFilter || undefined,
        dateFrom: dateFrom || undefined,
        dateTo: dateTo || undefined,
        page: page + 1,
        pageSize,
        sortBy,
        sortDir,
      }),
  });
  const searchQuery = useQuery({
    queryKey: ['payment-targets', 'search', deferredTargetSearch],
    queryFn: () => searchPaymentTargets(deferredTargetSearch),
    enabled: editorOpen && !selectedTarget,
  });
  const paymentMethodsQuery = useQuery({
    queryKey: ['payment-methods', 'active'],
    queryFn: () => listPaymentMethods('active'),
  });
  const paymentDocumentQuery = useQuery({
    queryKey: ['payments', editingPaymentId],
    queryFn: () => getPaymentDocument(editingPaymentId!),
    enabled: Boolean(editingPaymentId),
  });
  const targetQuery = useQuery({
    queryKey: ['payment-target', selectedTarget?.kind, selectedTarget?.id, editingPaymentId],
    queryFn: () => (selectedTarget?.kind === 'booking' ? getBookingPaymentTarget(selectedTarget.id, editingPaymentId) : getCustomerPaymentTarget(selectedTarget!.id, editingPaymentId)),
    enabled: Boolean(selectedTarget),
  });

  function closeVoidDialog() {
    setVoidingPayment(null);
    setVoidDate(todayIso());
    setVoidReason('');
    setVoidOverrideLock(false);
    setVoidOverrideReason('');
  }

  const { startNewFromTarget, openEditDocument, handleSave, submitVoid, confirmUpdateOverride, saving } = usePaymentActions({
    editingPaymentId,
    voidingPayment,
    voidDate,
    voidReason,
    voidOverrideLock,
    voidOverrideReason,
    setError,
    closeBuilder,
    closeVoidDialog,
    setPendingUpdateOverridePayload,
    setSelectedTarget,
    setEditingPaymentId,
  });

  const searchResults = useMemo(() => searchQuery.data ?? [], [searchQuery.data]);
  const paymentRows = paymentsQuery.data?.items ?? [];
  const paymentTotal = paymentsQuery.data?.total ?? 0;
  const hasTargetSearch = deferredTargetSearch.trim().length > 0;
  const editorLoading =
    targetQuery.isLoading || paymentMethodsQuery.isLoading || (Boolean(editingPaymentId) && paymentDocumentQuery.isLoading);
  const activeExportFilters: PaymentExportFilters = {
    search: deferredTableSearch || undefined,
    status: statusFilter || undefined,
    documentKind: documentKindFilter || undefined,
    dateFrom: dateFrom || undefined,
    dateTo: dateTo || undefined,
    sortBy,
    sortDir,
  };

  function focusPaymentTargetSearch() {
    setTimeout(() => {
      const input = document.querySelector<HTMLInputElement>('input[data-payment-target-search-input="true"]');
      input?.focus();
    }, 0);
  }

  function resetEditorState() {
    setSelectedTarget(null);
    setEditingPaymentId(null);
    setSearchText('');
    setPendingUpdateOverridePayload(null);
  }

  function closePaymentEditor() {
    setCreatingNew(false);
    resetEditorState();
  }

  function closeBuilder() {
    closePaymentEditor();
  }

  function handleCreateMultiPayment() {
    setError(null);
    setCreatingNew(true);
    resetEditorState();
    focusPaymentTargetSearch();
  }

  return (
    <Stack spacing={3}>
      <PaymentsPageHeader
        title={paymentsText.page.title}
        subtitle={paymentsText.page.subtitle}
        createLabel={paymentsText.page.addMultiAction}
        onCreate={handleCreateMultiPayment}
      />

      {error ? <Alert severity='error'>{error}</Alert> : null}
      {paymentsQuery.error instanceof Error ? <Alert severity='error'>{paymentsQuery.error.message}</Alert> : null}
      {searchQuery.error instanceof Error ? <Alert severity='error'>{searchQuery.error.message}</Alert> : null}
      {targetQuery.error instanceof Error ? <Alert severity='error'>{targetQuery.error.message}</Alert> : null}
      {paymentDocumentQuery.error instanceof Error ? <Alert severity='error'>{paymentDocumentQuery.error.message}</Alert> : null}
      {paymentMethodsQuery.error instanceof Error ? <Alert severity='error'>{paymentMethodsQuery.error.message}</Alert> : null}

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
        hasTargetSearch={hasTargetSearch}
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
        onTableSearchChange={(value) => {
          setTableSearchInput(value);
          setPage(0);
        }}
        statusFilter={statusFilter}
        onStatusFilterChange={(value) => {
          setStatusFilter(value);
          setPage(0);
        }}
        documentKindFilter={documentKindFilter}
        onDocumentKindFilterChange={(value) => {
          setDocumentKindFilter(value);
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
        exportFilters={activeExportFilters}
        onSortChange={(nextSortBy, nextSortDir) => {
          setSortBy(nextSortBy);
          setSortDir(nextSortDir);
          setPage(0);
        }}
        onOpenEdit={(row) => {
          setCreatingNew(false);
          openEditDocument(row);
        }}
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
        onConfirm={async (reason) => {
          await confirmUpdateOverride(reason, pendingUpdateOverridePayload);
        }}
      />
    </Stack>
  );
}
