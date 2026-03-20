import BlockOutlinedIcon from '@mui/icons-material/BlockOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import PaymentsOutlinedIcon from '@mui/icons-material/PaymentsOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
import { Alert, Box, Button, Chip, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import { SectionCard } from '../components/SectionCard';
import { useLanguage } from '../features/language/LanguageProvider';
import { PaymentDocumentBuilder } from '../features/payments/PaymentDocumentBuilder';
import { PaymentVoidDialog } from '../features/payments/PaymentVoidDialog';
import {
  createPayment,
  getBookingPaymentTarget,
  getCustomerPaymentTarget,
  getPaymentDocument,
  listPayments,
  searchPaymentTargets,
  updatePayment,
  voidPayment,
  type PaymentDocumentPayload,
  type PaymentDocumentSummaryRecord,
  type PaymentTargetSearchRecord,
} from '../features/payments/api';
import { queryClient } from '../lib/queryClient';
import { EMPTY_VALUE, joinLocalizedList, paymentDocumentStatusLabel, paymentKindLabel, useCommonText } from '../text/common';
import { usePaymentsText } from '../text/payments';

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

async function invalidatePaymentViews() {
  await Promise.all([
    queryClient.invalidateQueries({ queryKey: ['payments'] }),
    queryClient.invalidateQueries({ queryKey: ['bookings'] }),
    queryClient.invalidateQueries({ queryKey: ['dashboard'] }),
    queryClient.invalidateQueries({ queryKey: ['reports'] }),
    queryClient.invalidateQueries({ queryKey: ['accounting'] }),
    queryClient.invalidateQueries({ queryKey: ['exports'] }),
  ]);
}

export function PaymentsPage() {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const paymentsText = usePaymentsText();
  const [error, setError] = useState<string | null>(null);
  const [searchText, setSearchText] = useState('');
  const [selectedTarget, setSelectedTarget] = useState<PaymentTargetSearchRecord | null>(null);
  const [editingPaymentId, setEditingPaymentId] = useState<string | null>(null);
  const [voidingPayment, setVoidingPayment] = useState<PaymentDocumentSummaryRecord | null>(null);
  const [voidDate, setVoidDate] = useState(todayIso());
  const [voidReason, setVoidReason] = useState('');

  const paymentsQuery = useQuery({ queryKey: ['payments'], queryFn: listPayments });
  const searchQuery = useQuery({
    queryKey: ['payment-targets', 'search', searchText],
    queryFn: () => searchPaymentTargets(searchText),
    enabled: searchText.trim().length >= 2,
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

  const createMutation = useMutation({
    mutationFn: createPayment,
    onSuccess: async () => {
      await invalidatePaymentViews();
      closeBuilder();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const updateMutation = useMutation({
    mutationFn: ({ paymentDocumentId, payload }: { paymentDocumentId: string; payload: PaymentDocumentPayload }) => updatePayment(paymentDocumentId, payload),
    onSuccess: async () => {
      await invalidatePaymentViews();
      closeBuilder();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const voidMutation = useMutation({
    mutationFn: ({ paymentDocumentId, payload }: { paymentDocumentId: string; payload: { void_date: string; reason: string } }) => voidPayment(paymentDocumentId, payload),
    onSuccess: async () => {
      await invalidatePaymentViews();
      closeVoidDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  const searchResults = useMemo(() => searchQuery.data ?? [], [searchQuery.data]);

  function closeBuilder() {
    setSelectedTarget(null);
    setEditingPaymentId(null);
    setSearchText('');
  }

  function closeVoidDialog() {
    setVoidingPayment(null);
    setVoidDate(todayIso());
    setVoidReason('');
  }

  function startNewFromTarget(target: PaymentTargetSearchRecord) {
    setError(null);
    setEditingPaymentId(null);
    setSelectedTarget(target);
  }

  function openEditDocument(payment: PaymentDocumentSummaryRecord) {
    setError(null);
    setEditingPaymentId(payment.id);
    setSelectedTarget({
      kind: 'customer',
      id: payment.customer_id,
      label: payment.customer_name,
      customer_id: payment.customer_id,
      customer_name: payment.customer_name,
    });
  }

  async function handleSave(payload: PaymentDocumentPayload) {
    setError(null);
    if (editingPaymentId) {
      await updateMutation.mutateAsync({ paymentDocumentId: editingPaymentId, payload });
      return;
    }
    await createMutation.mutateAsync(payload);
  }

  async function submitVoid() {
    if (!voidingPayment) return;
    await voidMutation.mutateAsync({ paymentDocumentId: voidingPayment.id, payload: { void_date: voidDate, reason: voidReason } });
  }

  return (
    <Stack spacing={3}>
      <Stack direction='row' justifyContent='space-between' alignItems='center'>
        <Box>
          <Typography variant='h4'>{paymentsText.page.title}</Typography>
          <Typography color='text.secondary'>{paymentsText.page.subtitle}</Typography>
        </Box>
        <Chip icon={<PaymentsOutlinedIcon />} label={paymentsText.page.accountingChip} color='primary' />
      </Stack>

      {error ? <Alert severity='error'>{error}</Alert> : null}

      <SectionCard title={paymentsText.page.searchTitle} subtitle={paymentsText.page.searchSubtitle}>
        <Stack spacing={2}>
          <TextField
            label={paymentsText.page.searchLabel}
            value={searchText}
            onChange={(event) => setSearchText(event.target.value)}
            InputProps={{ startAdornment: <SearchOutlinedIcon sx={{ ml: 1, color: 'text.secondary' }} /> }}
          />
          {searchText.trim().length < 2 ? <Alert severity='info'>{paymentsText.page.searchHint}</Alert> : null}
          {searchResults.map((result) => (
            <Button key={`${result.kind}-${result.id}`} variant='outlined' onClick={() => startNewFromTarget(result)}>
              {result.label}
            </Button>
          ))}
        </Stack>
      </SectionCard>

      {selectedTarget && targetQuery.data ? (
        <SectionCard title={paymentsText.page.targetTitle} subtitle={paymentsText.page.targetSubtitle}>
          <PaymentDocumentBuilder target={targetQuery.data} document={paymentDocumentQuery.data ?? null} saving={createMutation.isPending || updateMutation.isPending} onSave={handleSave} onCancel={closeBuilder} />
        </SectionCard>
      ) : null}

      <SectionCard title={paymentsText.page.listTitle} subtitle={paymentsText.page.listSubtitle}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{paymentsText.table.number}</TableCell>
              <TableCell>{paymentsText.table.customer}</TableCell>
              <TableCell>{paymentsText.table.bookings}</TableCell>
              <TableCell>{paymentsText.table.date}</TableCell>
              <TableCell>{paymentsText.table.type}</TableCell>
              <TableCell>{paymentsText.table.status}</TableCell>
              <TableCell>{paymentsText.table.total}</TableCell>
              <TableCell>{paymentsText.table.journal}</TableCell>
              <TableCell>{commonText.actions}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(paymentsQuery.data ?? []).map((payment) => (
              <TableRow key={payment.id}>
                <TableCell>{payment.payment_number}</TableCell>
                <TableCell>{payment.customer_name}</TableCell>
                <TableCell>{joinLocalizedList(language, payment.booking_numbers)}</TableCell>
                <TableCell>{payment.payment_date}</TableCell>
                <TableCell>
                  <Chip size='small' label={paymentKindLabel(language, payment.document_kind)} />
                </TableCell>
                <TableCell>
                  <Chip size='small' color={payment.status === 'voided' ? 'warning' : 'primary'} label={paymentDocumentStatusLabel(language, payment.status)} />
                </TableCell>
                <TableCell>{payment.total_amount}</TableCell>
                <TableCell>
                  {payment.journal_entry_number ? (
                    <Stack spacing={0.5}>
                      <Stack direction='row' spacing={1} alignItems='center'>
                        <ReceiptLongOutlinedIcon fontSize='small' color='action' />
                        <Typography variant='body2'>{payment.journal_entry_number}</Typography>
                      </Stack>
                      <Typography variant='caption'>{payment.journal_entry_status ?? EMPTY_VALUE}</Typography>
                    </Stack>
                  ) : (
                    EMPTY_VALUE
                  )}
                </TableCell>
                <TableCell>
                  {payment.status === 'voided' ? (
                    <Typography variant='body2' color='text.secondary'>
                      {paymentsText.page.voidedState}
                    </Typography>
                  ) : (
                    <Stack direction='row' spacing={1}>
                      <Button startIcon={<EditOutlinedIcon />} disabled={payment.document_kind !== 'collection'} onClick={() => openEditDocument(payment)}>
                        {paymentsText.page.edit}
                      </Button>
                      <Button color='warning' startIcon={<BlockOutlinedIcon />} onClick={() => setVoidingPayment(payment)}>
                        {paymentsText.page.void}
                      </Button>
                    </Stack>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </SectionCard>

      <PaymentVoidDialog open={Boolean(voidingPayment)} payment={voidingPayment} voidDate={voidDate} voidReason={voidReason} onClose={closeVoidDialog} onVoidDateChange={setVoidDate} onVoidReasonChange={setVoidReason} onSubmit={() => void submitVoid()} />
    </Stack>
  );
}
