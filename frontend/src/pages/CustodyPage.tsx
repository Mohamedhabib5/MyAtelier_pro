import AddCircleOutlineOutlinedIcon from '@mui/icons-material/AddCircleOutlineOutlined';
import PaidOutlinedIcon from '@mui/icons-material/PaidOutlined';
import PublishedWithChangesOutlinedIcon from '@mui/icons-material/PublishedWithChangesOutlined';
import { Alert, Button, Stack, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';
import { AppDialogShell } from '../components/AppDialogShell';
import { applyCustodyAction, createCustodyCase, listCustodyCases, type CustodyCaseCreatePayload, type CustodyCaseView } from '../features/custody/api';
import { CustodyActionForm } from '../features/custody/CustodyActionForm';
import { CustodyCaseCreateSection } from '../features/custody/CustodyCaseCreateSection';
import { CustodyCasesTableSection } from '../features/custody/CustodyCasesTableSection';
import { CustodyCompensationSection } from '../features/custody/CustodyCompensationSection';
import { useLanguage } from '../features/language/LanguageProvider';
import { listPaymentMethods } from '../features/paymentMethods/api';
import { queryClient } from '../lib/queryClient';
import { useCustodyText } from '../text/custody';
function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export function CustodyPage() {
  const { language } = useLanguage();
  const custodyText = useCustodyText();
  const isArabic = language === 'ar';
  const selectedLanguage = isArabic ? 'ar' : 'en';

  const [caseView, setCaseView] = useState<CustodyCaseView>('open');
  const [targetCaseId, setTargetCaseId] = useState('');
  const [action, setAction] = useState('handover');
  const [actionDate, setActionDate] = useState(todayIso());
  const [actionNote, setActionNote] = useState('');
  const [actionCondition, setActionCondition] = useState('');
  const [returnOutcome, setReturnOutcome] = useState('good');
  const [compensationAmount, setCompensationAmount] = useState('');
  const [actionPaymentMethodId, setActionPaymentMethodId] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [actionDialogOpen, setActionDialogOpen] = useState(false);
  const [compensationDialogOpen, setCompensationDialogOpen] = useState(false);

  const casesQuery = useQuery({ queryKey: ['custody', 'cases', caseView], queryFn: () => listCustodyCases(caseView) });
  const allCasesQuery = useQuery({ queryKey: ['custody', 'cases', 'all'], queryFn: () => listCustodyCases('all') });
  const paymentMethodsQuery = useQuery({ queryKey: ['payment-methods', 'active'], queryFn: () => listPaymentMethods('active') });

  const caseOptions = useMemo(() => allCasesQuery.data ?? [], [allCasesQuery.data]);
  const selectedCase = useMemo(() => caseOptions.find((item) => item.id === targetCaseId) ?? null, [caseOptions, targetCaseId]);
  const existingCaseLineIds = useMemo(() => caseOptions.map((item) => item.booking_line_id).filter((value): value is string => Boolean(value)), [caseOptions]);

  useEffect(() => {
    if (action !== 'customer_return') {
      setReturnOutcome('good');
      setCompensationAmount('');
      return;
    }
    if (returnOutcome === 'damaged' && !compensationAmount.trim() && selectedCase?.security_deposit_amount) {
      setCompensationAmount(String(selectedCase.security_deposit_amount));
    }
  }, [action, returnOutcome, compensationAmount, selectedCase]);

  useEffect(() => {
    const methods = paymentMethodsQuery.data ?? [];
    if (!methods.length) return;
    if (actionPaymentMethodId && methods.some((item) => item.id === actionPaymentMethodId)) return;
    setActionPaymentMethodId(methods[0].id);
  }, [actionPaymentMethodId, paymentMethodsQuery.data]);

  const createMutation = useMutation({
    mutationFn: async (payloads: CustodyCaseCreatePayload[]) => {
      for (const payload of payloads) await createCustodyCase(payload);
    },
    onSuccess: async () => {
      setMessage(custodyText.page.created);
      setError(null);
      await queryClient.invalidateQueries({ queryKey: ['custody', 'cases'] });
      setCreateDialogOpen(false);
    },
    onError: (mutationError: Error) => {
      setError(mutationError.message);
      setMessage(null);
    },
  });

  const actionMutation = useMutation({
    mutationFn: ({ caseId, actionValue, actionDateValue, noteValue, conditionValue, returnOutcomeValue, compensationAmountValue }: {
      caseId: string; actionValue: string; actionDateValue: string; noteValue: string; conditionValue: string; returnOutcomeValue: string | null; compensationAmountValue: string;
    }) =>
      applyCustodyAction(caseId, {
        action: actionValue,
        action_date: actionDateValue,
        note: noteValue || null,
        product_condition: conditionValue || null,
        return_outcome: returnOutcomeValue,
        compensation_amount: compensationAmountValue.trim() ? Number(compensationAmountValue) : null,
        payment_method_id: actionValue === 'customer_return' ? actionPaymentMethodId || null : null,
      }),
    onSuccess: async () => {
      setMessage(isArabic ? 'تم تحديث حالة الحيازة بنجاح.' : 'Custody case updated successfully.');
      setError(null);
      setActionDate(todayIso());
      setActionNote('');
      setActionCondition('');
      setReturnOutcome('good');
      setCompensationAmount('');
      await queryClient.invalidateQueries({ queryKey: ['custody', 'cases'] });
      await queryClient.invalidateQueries({ queryKey: ['payments'] });
      setActionDialogOpen(false);
    },
    onError: (mutationError: Error) => {
      setError(mutationError.message);
      setMessage(null);
    },
  });

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
        <Button variant='contained' startIcon={<AddCircleOutlineOutlinedIcon />} onClick={() => setCreateDialogOpen(true)}>{custodyText.page.createTitle}</Button>
        <Button variant='outlined' startIcon={<PublishedWithChangesOutlinedIcon />} disabled={!caseOptions.length} onClick={() => setActionDialogOpen(true)}>{custodyText.page.actionTitle}</Button>
        <Button variant='outlined' startIcon={<PaidOutlinedIcon />} disabled={!caseOptions.length} onClick={() => setCompensationDialogOpen(true)}>{custodyText.page.compensationTitle}</Button>
      </Stack>

      {message ? <Alert severity='success'>{message}</Alert> : null}
      {error ? <Alert severity='error'>{error}</Alert> : null}
      {paymentMethodsQuery.error instanceof Error ? <Alert severity='error'>{paymentMethodsQuery.error.message}</Alert> : null}

      <CustodyCasesTableSection
        rows={casesQuery.data ?? []}
        view={caseView}
        onViewChange={setCaseView}
        language={selectedLanguage}
        title={custodyText.page.listTitle}
        subtitle={custodyText.page.listSubtitle}
        viewOpenLabel={custodyText.page.viewOpen}
        viewSettledLabel={custodyText.page.viewSettled}
        viewAllLabel={custodyText.page.viewAll}
        labels={{
          caseNumber: custodyText.page.caseNumber,
          custodyDate: custodyText.page.custodyDate,
          customerName: custodyText.page.customerName,
          bookingNumber: custodyText.page.bookingNumber,
          dressCode: custodyText.page.dressCode,
          statement: custodyText.page.statement,
          depositAmount: custodyText.page.depositAmount,
          compensationAmount: custodyText.page.compensationValue,
          status: custodyText.page.status,
          search: labels.search,
          searchPlaceholder: labels.searchPlaceholder,
          reset: labels.reset,
          noRows: labels.noRows,
          filters: labels.filters,
          columns: labels.columns,
          export: labels.export,
          rowsPerPage: labels.rowsPerPage,
          close: labels.close,
          emptyValue: custodyText.page.emptyValue,
        }}
      />

      <AppDialogShell open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} title={custodyText.page.createTitle} subtitle={custodyText.page.createSubtitle} maxWidth='md'>
        <CustodyCaseCreateSection
          language={selectedLanguage}
          title={custodyText.page.createTitle}
          subtitle={custodyText.page.createSubtitle}
          custodyDateLabel={custodyText.page.custodyDate}
          createLabel={custodyText.page.create}
          notesLabel={custodyText.page.notes}
          conditionLabel={custodyText.page.productCondition}
          depositAmountLabel={custodyText.page.depositAmount}
          depositDocumentLabel={isArabic ? 'بيان الوثيقة المستلمة من العميل' : 'Received customer document'}
          paymentMethodLabel={custodyText.page.paymentMethod}
          bookingSearchLabel={labels.bookingSearch}
          bookingSearchHint={labels.bookingSearchHint}
          bookingLineLabel={labels.bookingLine}
          lineAlreadyUsedLabel={labels.lineUsed}
          noLinesLabel={labels.noLines}
          lineNoDressLabel={labels.noDressLine}
          existingCaseLineIds={existingCaseLineIds}
          paymentMethods={paymentMethodsQuery.data ?? []}
          isSubmitting={createMutation.isPending}
          showCard={false}
          onCreateMany={async (payloads) => { await createMutation.mutateAsync(payloads); }}
        />
      </AppDialogShell>

      <AppDialogShell open={actionDialogOpen} onClose={() => setActionDialogOpen(false)} title={custodyText.page.actionTitle} subtitle={custodyText.page.actionSubtitle}>
        <CustodyActionForm
          caseOptions={caseOptions}
          selectedLanguage={selectedLanguage}
          targetCaseId={targetCaseId}
          action={action}
          actionDate={actionDate}
          actionCondition={actionCondition}
          actionNote={actionNote}
          returnOutcome={returnOutcome}
          compensationAmount={compensationAmount}
          paymentMethodId={actionPaymentMethodId}
          paymentMethods={paymentMethodsQuery.data ?? []}
          actionLabel={custodyText.page.action}
          actionDateLabel={custodyText.page.actionDate}
          targetCaseLabel={custodyText.page.targetCase}
          conditionLabel={custodyText.page.productCondition}
          noteLabel={custodyText.page.actionNote}
          returnOutcomeLabel={labels.returnOutcome}
          returnGoodLabel={labels.returnGood}
          returnDamagedLabel={labels.returnDamaged}
          compensationAmountLabel={custodyText.page.compensationAmount}
          paymentMethodLabel={custodyText.page.paymentMethod}
          applyLabel={custodyText.page.applyAction}
          isSubmitting={actionMutation.isPending}
          onTargetCaseChange={setTargetCaseId}
          onActionChange={setAction}
          onActionDateChange={setActionDate}
          onConditionChange={setActionCondition}
          onNoteChange={setActionNote}
          onReturnOutcomeChange={setReturnOutcome}
          onCompensationAmountChange={setCompensationAmount}
          onPaymentMethodChange={setActionPaymentMethodId}
          onApply={() => {
            if (!targetCaseId || !actionDate) return;
            void actionMutation.mutateAsync({ caseId: targetCaseId, actionValue: action, actionDateValue: actionDate, noteValue: actionNote, conditionValue: actionCondition, returnOutcomeValue: action === 'customer_return' ? returnOutcome : null, compensationAmountValue: action === 'customer_return' && returnOutcome === 'damaged' ? compensationAmount : '' });
          }}
        />
      </AppDialogShell>

      <AppDialogShell open={compensationDialogOpen} onClose={() => setCompensationDialogOpen(false)} title={custodyText.page.compensationTitle} subtitle={custodyText.page.compensationSubtitle}>
        <CustodyCompensationSection
          caseOptions={caseOptions}
          language={language}
          selectedLanguage={selectedLanguage}
          setMessage={setMessage}
          setError={setError}
          paymentMethods={paymentMethodsQuery.data ?? []}
          showCard={false}
          onCollected={() => setCompensationDialogOpen(false)}
          text={{ title: custodyText.page.compensationTitle, subtitle: custodyText.page.compensationSubtitle, targetCase: custodyText.page.targetCase, amount: custodyText.page.compensationAmount, paymentMethod: custodyText.page.paymentMethod, date: custodyText.page.compensationDate, note: custodyText.page.compensationNote, apply: custodyText.page.compensationApply }}
        />
      </AppDialogShell>
    </Stack>
  );
}
