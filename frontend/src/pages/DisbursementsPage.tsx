import { Alert, Stack } from '@mui/material';
import { useCallback } from 'react';

import { DisbursementsPageHeader } from '../features/disbursements/DisbursementsPageHeader';
import { DisbursementsTableSection } from '../features/disbursements/DisbursementsTableSection';
import { DisbursementEditorDialog } from '../features/disbursements/DisbursementEditorDialog';
import { DisbursementVoidDialog } from '../features/disbursements/DisbursementVoidDialog';
import { PeriodLockOverrideDialog } from '../components/PeriodLockOverrideDialog';
import { useDisbursementsPageState, type DisbursementSortField } from '../features/disbursements/useDisbursementsPageState';
import { useDisbursementActions } from '../features/disbursements/useDisbursementActions';
import { useDisbursementsText } from '../text/disbursements';

// Imports for Customer Refunds (Tab 2)
import { PaymentEditorDialog } from '../features/payments/PaymentEditorDialog';
import { PaymentVoidDialog } from '../features/payments/PaymentVoidDialog';
import { PaymentUpdateOverrideDialog } from '../features/payments/PaymentUpdateOverrideDialog';
import { usePaymentActions } from '../features/payments/usePaymentActions';
import { usePaymentsPageState } from '../features/payments/usePaymentsPageState';
import { usePaymentsText } from '../text/payments';
import { useAuth } from '../features/auth/AuthProvider';
import { useLanguage } from '../features/language/LanguageProvider';

export function DisbursementsPage() {
  const { language } = useLanguage();
  const { user } = useAuth();
  const disText = useDisbursementsText();
  const payText = usePaymentsText();
  
  // States
  const disState = useDisbursementsPageState();
  const payState = usePaymentsPageState('refund', 'refund');
  
  // Disbursement Actions (Tab 1)
  function closeDisbursementEditor() {
    disState.setCreatingNew(false);
    disState.setEditingVoucherId(null);
    disState.setPendingUpdateOverridePayload(null);
  }

  function closeDisbursementVoidDialog() {
    disState.setVoidingVoucher(null);
    disState.setVoidDate(disState.todayIso());
    disState.setVoidReason('');
    disState.setVoidOverrideLock(false);
    disState.setVoidOverrideReason('');
  }

  const { 
    handleSave: handleDisbursementSave, 
    submitVoid: submitDisbursementVoid, 
    confirmUpdateOverride: confirmDisbursementUpdateOverride, 
    handleDeleteDisbursement, 
    saving: disSaving 
  } = useDisbursementActions({
    editingVoucherId: disState.editingVoucherId,
    voidingVoucher: disState.voidingVoucher,
    voidDate: disState.voidDate,
    voidReason: disState.voidReason,
    voidOverrideLock: disState.voidOverrideLock,
    voidOverrideReason: disState.voidOverrideReason,
    setError: disState.setError,
    closeEditor: closeDisbursementEditor,
    closeVoidDialog: closeDisbursementVoidDialog,
    setPendingUpdateOverridePayload: disState.setPendingUpdateOverridePayload,
  });

  // Payment/Refund Actions (Tab 2)
  function closePaymentEditor() {
    payState.setCreatingNew(false);
    payState.setSelectedTarget(null);
    payState.setEditingPaymentId(null);
    payState.setSearchText('');
    payState.setPendingUpdateOverridePayload(null);
  }

  function closePaymentVoidDialog() {
    payState.setVoidingPayment(null);
    payState.setVoidDate(payState.todayIso());
    payState.setVoidReason('');
    payState.setVoidOverrideLock(false);
    payState.setVoidOverrideReason('');
  }

  const { 
    startNewFromTarget, 
    openEditDocument: openEditPaymentDocument, 
    handleSave: handlePaymentSave, 
    submitVoid: submitPaymentVoid, 
    confirmUpdateOverride: confirmPaymentUpdateOverride, 
    handleDeletePayment, 
    saving: paySaving 
  } = usePaymentActions({
    editingPaymentId: payState.editingPaymentId,
    voidingPayment: payState.voidingPayment,
    voidDate: payState.voidDate,
    voidReason: payState.voidReason,
    voidOverrideLock: payState.voidOverrideLock,
    voidOverrideReason: payState.voidOverrideReason,
    setError: payState.setError,
    closeBuilder: closePaymentEditor,
    closeVoidDialog: closePaymentVoidDialog,
    setPendingUpdateOverridePayload: payState.setPendingUpdateOverridePayload,
    setSelectedTarget: payState.setSelectedTarget,
    setEditingPaymentId: payState.setEditingPaymentId,
  });

  const disbursementRows = disState.disbursementsQuery.data?.items ?? [];
  const disbursementTotal = disState.disbursementsQuery.data?.total ?? 0;
  const paymentMethods = disState.paymentMethodsQuery.data ?? [];
  const editingVoucher = disState.editingVoucherId ? disState.disbursementVoucherQuery.data ?? null : null;
  const disEditorLoading = disState.paymentMethodsQuery.isLoading || (Boolean(disState.editingVoucherId) && disState.disbursementVoucherQuery.isLoading);

  const payEditorLoading = payState.targetQuery.isLoading || payState.paymentMethodsQuery.isLoading || (Boolean(payState.editingPaymentId) && payState.paymentDocumentQuery.isLoading);
  const searchResults = payState.searchQuery.data ?? [];

  return (
    <Stack spacing={3}>
      <DisbursementsPageHeader
        title={disText.page.title}
        subtitle={disText.page.subtitle}
        createLabel={disText.page.addDisbursement}
        onCreate={() => {
          disState.setError(null);
          disState.setCreatingNew(true);
          disState.setEditingVoucherId(null);
          disState.setPendingUpdateOverridePayload(null);
        }}
        secondCreateLabel={payText.page.addRefundAction}
        onSecondCreate={() => {
          payState.setError(null);
          payState.setCreatingNew(true);
          payState.setSelectedTarget(null);
          payState.setEditingPaymentId(null);
          payState.setSearchText('');
          payState.setInitialKind('refund');
          payState.setPendingUpdateOverridePayload(null);
          setTimeout(() => document.querySelector<HTMLInputElement>('input[data-payment-target-search-input="true"]')?.focus(), 0);
        }}
      />

      <DisbursementsPageErrors disState={disState} payState={payState} />

      <DisbursementsTableSection
        rows={disbursementRows}
        total={disbursementTotal}
        loading={disState.disbursementsQuery.isLoading}
        tableSearchInput={disState.tableSearchInput}
        onTableSearchChange={useCallback((v) => { disState.setTableSearchInput(v); disState.setPage(0); }, [disState])}
        statusFilter={disState.statusFilter}
        onStatusFilterChange={useCallback((v) => { disState.setStatusFilter(v); disState.setPage(0); }, [disState])}
        payeeTypeFilter={disState.payeeTypeFilter}
        onPayeeTypeFilterChange={useCallback((v) => { disState.setPayeeTypeFilter(v); disState.setPage(0); }, [disState])}
        activePreset={disState.activePreset}
        customFrom={disState.customFrom}
        customTo={disState.customTo}
        onSelectPreset={useCallback((preset) => { disState.selectPreset(preset); disState.setPage(0); }, [disState])}
        onCustomFromChange={useCallback((v) => { disState.setCustomFrom(v); disState.setPage(0); }, [disState])}
        onCustomToChange={useCallback((v) => { disState.setCustomTo(v); disState.setPage(0); }, [disState])}
        page={disState.page}
        pageSize={disState.pageSize}
        onPageChange={disState.setPage}
        onPageSizeChange={useCallback((v) => { disState.setPageSize(v); disState.setPage(0); }, [disState])}
        sortBy={disState.sortBy}
        sortDir={disState.sortDir}
        onSortChange={useCallback((b, d) => { disState.setSortBy(b as DisbursementSortField); disState.setSortDir(d); disState.setPage(0); }, [disState])}
        onOpenEdit={useCallback((row: any) => {
          if (row.source_table === 'payment_documents') {
            payState.setCreatingNew(false);
            openEditPaymentDocument(row);
          } else {
            disState.setCreatingNew(false);
            disState.setEditingVoucherId(row.id);
          }
        }, [disState, payState, openEditPaymentDocument])}
        onOpenVoid={useCallback((row: any) => {
          if (row.source_table === 'payment_documents') {
            payState.setVoidingPayment(row);
          } else {
            disState.setVoidingVoucher(row);
          }
        }, [disState, payState])}
        onDelete={useCallback(async (row: any) => {
          if (row.source_table === 'payment_documents') {
            if (window.confirm(`هل أنت متأكد من حذف السند ${row.voucher_number} نهائياً؟ سيتم إلغاء القيود المحاسبية المرتبطة أيضاً.`)) {
              await handleDeletePayment(row.id);
            }
          } else {
            const confirmMsg = disText.page.confirmDelete.replace('{number}', row.voucher_number);
            if (window.confirm(confirmMsg)) {
              await handleDeleteDisbursement(row.id);
            }
          }
        }, [handleDeleteDisbursement, handleDeletePayment, disText])}
      />

      {/* Disbursement Dialogs */}
      <DisbursementEditorDialog
        open={disState.editorOpen}
        voucher={editingVoucher}
        paymentMethods={paymentMethods}
        saving={disSaving || disEditorLoading}
        onClose={closeDisbursementEditor}
        onSave={handleDisbursementSave}
      />

      <DisbursementVoidDialog
        open={Boolean(disState.voidingVoucher)}
        voucher={disState.voidingVoucher}
        voidDate={disState.voidDate}
        voidReason={disState.voidReason}
        overrideLock={disState.voidOverrideLock}
        overrideReason={disState.voidOverrideReason}
        onClose={closeDisbursementVoidDialog}
        onVoidDateChange={disState.setVoidDate}
        onVoidReasonChange={disState.setVoidReason}
        onOverrideLockChange={disState.setVoidOverrideLock}
        onOverrideReasonChange={disState.setVoidOverrideReason}
        onSubmit={() => void submitDisbursementVoid()}
      />

      <PeriodLockOverrideDialog
        open={Boolean(disState.pendingUpdateOverridePayload)}
        titleAr='Override لتعديل سند الصرف'
        titleEn='Override disbursement update'
        descriptionAr='الفترة مقفولة. أدخل سبب Override لإتمام تعديل سند الصرف.'
        descriptionEn='Period is locked. Enter override reason to continue disbursement update.'
        onClose={() => disState.setPendingUpdateOverridePayload(null)}
        onConfirm={async (reason) => { await confirmDisbursementUpdateOverride(reason, disState.pendingUpdateOverridePayload); }}
      />

      {/* Customer Refund (Payment) Dialogs */}
      <PaymentEditorDialog
        open={payState.editorOpen}
        title={payText.page.targetTitle}
        subtitle={payText.page.targetSubtitle}
        loading={payEditorLoading}
        target={payState.targetQuery.data ?? null}
        document={payState.paymentDocumentQuery.data ?? null}
        paymentMethods={payState.paymentMethodsQuery.data ?? []}
        saving={paySaving}
        searchTitle={payText.page.searchTitle}
        searchSubtitle={payText.page.searchSubtitle}
        searchLabel={payText.page.searchLabel}
        searchHint={payText.page.searchHint}
        searchText={payState.searchText}
        searchResults={searchResults}
        searchLoading={payState.searchQuery.isFetching}
        hasTargetSearch={payState.searchText.trim().length > 0}
        searchLoadingLabel={payText.page.searchLoading}
        searchNoResultsLabel={payText.page.searchNoResults}
        customerKindLabel={payText.page.searchCustomerTag}
        bookingKindLabel={payText.page.searchBookingTag}
        onSearchTextChange={payState.setSearchText}
        onSelectTarget={startNewFromTarget}
        onClose={closePaymentEditor}
        onSave={handlePaymentSave}
        initialKind={payState.initialKind}
      />

      <PaymentVoidDialog
        open={Boolean(payState.voidingPayment)}
        payment={payState.voidingPayment}
        voidDate={payState.voidDate}
        voidReason={payState.voidReason}
        overrideLock={payState.voidOverrideLock}
        overrideReason={payState.voidOverrideReason}
        onClose={closePaymentVoidDialog}
        onVoidDateChange={payState.setVoidDate}
        onVoidReasonChange={payState.setVoidReason}
        onOverrideLockChange={payState.setVoidOverrideLock}
        onOverrideReasonChange={payState.setVoidOverrideReason}
        onSubmit={() => void submitPaymentVoid()}
      />

      <PaymentUpdateOverrideDialog
        open={Boolean(payState.pendingUpdateOverridePayload)}
        onClose={() => payState.setPendingUpdateOverridePayload(null)}
        onConfirm={async (reason) => { await confirmPaymentUpdateOverride(reason, payState.pendingUpdateOverridePayload); }}
      />
    </Stack>
  );
}

function DisbursementsPageErrors({ disState, payState }: { disState: any; payState: any }) {
  const errors = [
    disState.error,
    disState.disbursementsQuery.error?.message,
    disState.paymentMethodsQuery.error?.message,
    disState.disbursementVoucherQuery.error?.message,
    payState.error,
    payState.paymentsQuery.error?.message,
    payState.searchQuery.error?.message,
    payState.targetQuery.error?.message,
    payState.paymentDocumentQuery.error?.message,
  ].filter(Boolean);

  if (errors.length === 0) return null;

  return (
    <Stack spacing={1}>
      {errors.map((err, i) => <Alert key={i} severity='error'>{err}</Alert>)}
    </Stack>
  );
}
