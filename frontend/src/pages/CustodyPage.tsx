import AddCircleOutlineOutlinedIcon from '@mui/icons-material/AddCircleOutlineOutlined';
import PaidOutlinedIcon from '@mui/icons-material/PaidOutlined';
import PublishedWithChangesOutlinedIcon from '@mui/icons-material/PublishedWithChangesOutlined';
import { Alert, Button, Stack, Typography } from '@mui/material';
import { useEffect, useMemo, useCallback } from 'react';
import { AppDialogShell } from '../components/AppDialogShell';
import { getCustodyExcelUrl, getCustodyExportUrl } from '../features/exports/api';
import { downloadFile } from '../lib/api';
import { CustodyActionForm } from '../features/custody/CustodyActionForm';
import { CustodyCaseCreateSection } from '../features/custody/CustodyCaseCreateSection';
import { CustodyCasesTableSection } from '../features/custody/CustodyCasesTableSection';
import { CustodyCompensationSection } from '../features/custody/CustodyCompensationSection';
import { useLanguage } from '../features/language/LanguageProvider';
import { useAuth } from '../features/auth/AuthProvider';
import { useCustodyText } from '../text/custody';
import { useCustodyLogic } from '../features/custody/useCustodyLogic';

export function CustodyPage() {
  const { language } = useLanguage();
  const { user } = useAuth();
  const custodyText = useCustodyText();
  const isArabic = language === 'ar';
  const selectedLanguage = isArabic ? 'ar' : 'en';

  const { state, queries, mutations } = useCustodyLogic(isArabic);

  const caseRows = queries.casesQuery.data?.items ?? [];
  const caseTotal = queries.casesQuery.data?.total ?? 0;
  const caseOptions = useMemo(() => queries.allCasesQuery.data?.items ?? [], [queries.allCasesQuery.data]);
  const selectedCase = useMemo(() => caseOptions.find((item: any) => item.id === state.targetCaseId) ?? null, [caseOptions, state.targetCaseId]);
  const existingCaseLineIds = useMemo(() => caseOptions.map((item: any) => item.booking_line_id).filter((value: any): value is string => Boolean(value)), [caseOptions]);

  useEffect(() => {
    if (state.action !== 'customer_return') {
      state.setReturnOutcome('good');
      state.setCompensationAmount('');
      return;
    }
    if (state.returnOutcome === 'damaged' && !state.compensationAmount.trim() && selectedCase?.security_deposit_amount) {
      state.setCompensationAmount(String(selectedCase.security_deposit_amount));
    }
  }, [state, selectedCase]);

  useEffect(() => {
    const methods = queries.paymentMethodsQuery.data ?? [];
    if (!methods.length) return;
    if (state.actionPaymentMethodId && methods.some((item) => item.id === state.actionPaymentMethodId)) return;
    state.setActionPaymentMethodId(methods[0].id);
  }, [state.actionPaymentMethodId, queries.paymentMethodsQuery.data, state]);

  const labels = isArabic
    ? { search: 'بحث', searchPlaceholder: 'بحث بالعميل أو الحجز أو الفستان أو رقم الحالة', filters: 'الفلاتر', columns: 'الأعمدة', export: 'تصدير', reset: 'إعادة الضبط', noRows: 'لا توجد حالات حيازة.', rowsPerPage: 'عدد الصفوف', close: 'إغلاق', bookingSearch: 'ابحث عن الحجز', bookingSearchHint: 'ابحث باسم العميل أو رقم الحجز.', bookingLine: 'سطر الحجز', lineUsed: 'تم إنشاء حيازة لهذا السطر', noLines: 'لا توجد سطور متاحة في هذا الحجز.', noDressLine: 'بدون فستان (اكتب البيان في الملاحظات)', returnOutcome: 'حالة الاستلام من العميل', returnGood: 'استلام بحالة جيدة (رد التأمين)', returnDamaged: 'استلام مع تلفيات (تحصيل تعويض)' }
    : { search: 'Search', searchPlaceholder: 'Search by customer, booking, dress, or case number', filters: 'Filters', columns: 'Columns', export: 'Export', reset: 'Reset', noRows: 'No custody cases.', rowsPerPage: 'Rows per page', close: 'Close', bookingSearch: 'Search booking', bookingSearchHint: 'Search by customer name or booking number.', bookingLine: 'Booking line', lineUsed: 'Case already exists for this line', noLines: 'No available lines in this booking.', noDressLine: 'No dress line (describe in notes)', returnOutcome: 'Customer return outcome', returnGood: 'Good condition (refund deposit)', returnDamaged: 'Damaged (collect compensation)' };

  return (
    <Stack spacing={3}>
      <Stack spacing={0.5}>
        <Typography variant='h4'>{isArabic ? 'استلام وتسليم الفساتين' : custodyText.page.title}</Typography>
        <Typography color='text.secondary'>{custodyText.page.subtitle}</Typography>
      </Stack>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
        <Button variant='contained' startIcon={<AddCircleOutlineOutlinedIcon />} onClick={() => state.setCreateDialogOpen(true)}>{custodyText.page.createTitle}</Button>
        <Button variant='outlined' startIcon={<PublishedWithChangesOutlinedIcon />} disabled={!caseOptions.length} onClick={() => state.setActionDialogOpen(true)}>{custodyText.page.actionTitle}</Button>
        <Button variant='outlined' startIcon={<PaidOutlinedIcon />} disabled={!caseOptions.length} onClick={() => state.setCompensationDialogOpen(true)}>{custodyText.page.compensationTitle}</Button>
      </Stack>
      {state.message ? <Alert severity='success'>{state.message}</Alert> : null}
      {state.error ? <Alert severity='error'>{state.error}</Alert> : null}
      {queries.paymentMethodsQuery.error instanceof Error ? <Alert severity='error'>{queries.paymentMethodsQuery.error.message}</Alert> : null}
      <CustodyCasesTableSection
        rows={caseRows} total={caseTotal} loading={queries.casesQuery.isLoading} page={state.page} pageSize={state.pageSize} onPageChange={state.setPage}
        onPageSizeChange={useCallback((v) => { state.setPageSize(v); state.setPage(0); }, [state.setPageSize, state.setPage])} 
        view={state.caseView} onViewChange={useCallback((v) => { state.setCaseView(v); state.setPage(0); }, [state.setCaseView, state.setPage])}
        language={selectedLanguage} title={custodyText.page.listTitle} subtitle={custodyText.page.listSubtitle} viewOpenLabel={custodyText.page.viewOpen}
        viewSettledLabel={custodyText.page.viewSettled} viewAllLabel={custodyText.page.viewAll}
        labels={{
          caseNumber: custodyText.page.caseNumber, custodyDate: custodyText.page.custodyDate, customerName: custodyText.page.customerName, bookingNumber: custodyText.page.bookingNumber,
          dressCode: custodyText.page.dressCode, statement: custodyText.page.statement, depositAmount: custodyText.page.depositAmount, compensationAmount: custodyText.page.compensationValue,
          status: custodyText.page.status, search: labels.search, searchPlaceholder: labels.searchPlaceholder, reset: labels.reset, noRows: labels.noRows, filters: labels.filters,
          columns: labels.columns, export: labels.export, rowsPerPage: labels.rowsPerPage, close: labels.close, emptyValue: custodyText.page.emptyValue,
        }}
        onExport={useCallback((format: 'csv' | 'xlsx', scope: 'page' | 'all') => {
          const isXlsx = format === 'xlsx';
          const urlFn = isXlsx ? getCustodyExcelUrl : getCustodyExportUrl;
          const exportPage = scope === 'page' ? state.page + 1 : undefined;
          const exportPageSize = scope === 'page' ? state.pageSize : undefined;
          downloadFile(urlFn(user?.active_branch_id, exportPage, exportPageSize));
        }, [user?.active_branch_id, state.page, state.pageSize])}
      />
      <AppDialogShell open={state.createDialogOpen} onClose={() => state.setCreateDialogOpen(false)} title={custodyText.page.createTitle} subtitle={custodyText.page.createSubtitle} maxWidth='md'>
        <CustodyCaseCreateSection
          language={selectedLanguage} title={custodyText.page.createTitle} subtitle={custodyText.page.createSubtitle} custodyDateLabel={custodyText.page.custodyDate}
          createLabel={custodyText.page.create} notesLabel={custodyText.page.notes} conditionLabel={custodyText.page.productCondition} depositAmountLabel={custodyText.page.depositAmount}
          depositDocumentLabel={isArabic ? 'بيان الوثيقة المستلمة من العميل' : 'Received customer document'} paymentMethodLabel={custodyText.page.paymentMethod}
          bookingSearchLabel={labels.bookingSearch} bookingSearchHint={labels.bookingSearchHint} bookingLineLabel={labels.bookingLine} lineAlreadyUsedLabel={labels.lineUsed}
          noLinesLabel={labels.noLines} lineNoDressLabel={labels.noDressLine} existingCaseLineIds={existingCaseLineIds} paymentMethods={queries.paymentMethodsQuery.data ?? []}
          isSubmitting={mutations.createMutation.isPending} showCard={false} onCreateMany={async (payloads) => { await mutations.createMutation.mutateAsync(payloads); }}
        />
      </AppDialogShell>
      <AppDialogShell open={state.actionDialogOpen} onClose={() => state.setActionDialogOpen(false)} title={custodyText.page.actionTitle} subtitle={custodyText.page.actionSubtitle}>
        <CustodyActionForm
          caseOptions={caseOptions} selectedLanguage={selectedLanguage} targetCaseId={state.targetCaseId} action={state.action} actionDate={state.actionDate}
          actionCondition={state.actionCondition} actionNote={state.actionNote} returnOutcome={state.returnOutcome} compensationAmount={state.compensationAmount}
          paymentMethodId={state.actionPaymentMethodId} paymentMethods={queries.paymentMethodsQuery.data ?? []} actionLabel={custodyText.page.action}
          actionDateLabel={custodyText.page.actionDate} targetCaseLabel={custodyText.page.targetCase} conditionLabel={custodyText.page.productCondition}
          noteLabel={custodyText.page.actionNote} returnOutcomeLabel={labels.returnOutcome} returnGoodLabel={labels.returnGood} returnDamagedLabel={labels.returnDamaged}
          compensationAmountLabel={custodyText.page.compensationAmount} paymentMethodLabel={custodyText.page.paymentMethod} applyLabel={custodyText.page.applyAction}
          isSubmitting={mutations.actionMutation.isPending} onTargetCaseChange={state.setTargetCaseId} onActionChange={state.setAction} onActionDateChange={state.setActionDate}
          onConditionChange={state.setActionCondition} onNoteChange={state.setActionNote} onReturnOutcomeChange={state.setReturnOutcome} onCompensationAmountChange={state.setCompensationAmount}
          onPaymentMethodChange={state.setActionPaymentMethodId}
          onApply={() => {
            if (!state.targetCaseId || !state.actionDate) return;
            void mutations.actionMutation.mutateAsync({ caseId: state.targetCaseId, actionValue: state.action, actionDateValue: state.actionDate, noteValue: state.actionNote, conditionValue: state.actionCondition, returnOutcomeValue: state.action === 'customer_return' ? state.returnOutcome : null, compensationAmountValue: state.action === 'customer_return' && state.returnOutcome === 'damaged' ? state.compensationAmount : '' });
          }}
        />
      </AppDialogShell>
      <AppDialogShell open={state.compensationDialogOpen} onClose={() => state.setCompensationDialogOpen(false)} title={custodyText.page.compensationTitle} subtitle={custodyText.page.compensationSubtitle}>
        <CustodyCompensationSection
          caseOptions={caseOptions} language={language} selectedLanguage={selectedLanguage} setMessage={state.setMessage} setError={state.setError}
          paymentMethods={queries.paymentMethodsQuery.data ?? []} showCard={false} onCollected={() => state.setCompensationDialogOpen(false)}
          text={{ title: custodyText.page.compensationTitle, subtitle: custodyText.page.compensationSubtitle, targetCase: custodyText.page.targetCase, amount: custodyText.page.compensationAmount, paymentMethod: custodyText.page.paymentMethod, date: custodyText.page.compensationDate, note: custodyText.page.compensationNote, apply: custodyText.page.compensationApply }}
        />
      </AppDialogShell>
    </Stack>
  );
}
