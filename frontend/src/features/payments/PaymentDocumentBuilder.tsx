import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined';
import { Alert, Box, Button, MenuItem, Stack, TextField, Typography } from '@mui/material';
import type { ICellRendererParams, SuppressKeyboardEventParams } from 'ag-grid-community';
import { useEffect, useMemo, useState } from 'react';

import { AppAgGrid, type AppAgGridColumn } from '../../components/ag-grid';
import { StableNumericCell } from '../../components/inputs/StableNumericCell';
import { useLanguage } from '../../features/language/LanguageProvider';
import { EMPTY_VALUE, bookingStatusLabel, linePaymentStateLabel, useCommonText } from '../../text/common';
import { usePaymentsText } from '../../text/payments';
import type { PaymentMethodRecord } from '../paymentMethods/api';
import type { PaymentDocumentPayload, PaymentDocumentRecord, PaymentTargetBookingRecord, PaymentTargetDetailRecord, PaymentTargetLineRecord } from './api';

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export function PaymentDocumentBuilder({
  target,
  document,
  paymentMethods,
  saving,
  onSave,
  onCancel,
}: {
  target: PaymentTargetDetailRecord;
  document: PaymentDocumentRecord | null;
  paymentMethods: PaymentMethodRecord[];
  saving: boolean;
  onSave: (payload: PaymentDocumentPayload) => Promise<void>;
  onCancel: () => void;
}) {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const paymentsText = usePaymentsText();
  const [paymentDate, setPaymentDate] = useState(todayIso());
  const [paymentMethodId, setPaymentMethodId] = useState('');
  const [notes, setNotes] = useState('');
  const [allocationValues, setAllocationValues] = useState<Record<string, string>>({});

  useEffect(() => {
    setPaymentDate(document?.payment_date ?? todayIso());
    setPaymentMethodId(document?.payment_method_id ?? paymentMethods[0]?.id ?? '');
    setNotes(document?.notes ?? '');
    const seeded: Record<string, string> = {};
    for (const allocation of document?.allocations ?? []) {
      seeded[allocation.booking_line_id] = String(allocation.allocated_amount);
    }
    setAllocationValues(seeded);
  }, [document, paymentMethods, target]);

  const selectedTotal = useMemo(
    () => Object.values(allocationValues).reduce((sum, value) => sum + Number(value || 0), 0),
    [allocationValues],
  );

  async function handleSave() {
    const allocations = target.bookings.flatMap((booking) =>
      booking.lines
        .filter((line) => Number(allocationValues[line.line_id] || 0) > 0)
        .map((line) => ({
          booking_id: booking.booking_id,
          booking_line_id: line.line_id,
          allocated_amount: Number(allocationValues[line.line_id] || 0),
        })),
    );

    await onSave({
      customer_id: target.customer_id,
      payment_method_id: paymentMethodId || null,
      payment_date: paymentDate,
      notes: notes || null,
      allocations,
    });
  }

  function suppressGridKeyboardEvent(params: SuppressKeyboardEventParams<PaymentTargetLineRecord>) {
    const targetElement = params.event?.target;
    return targetElement instanceof HTMLElement && Boolean(targetElement.closest('input, textarea, select'));
  }

  const allocationColumns = useMemo<AppAgGridColumn<PaymentTargetLineRecord>[]>(
    () => [
      {
        colId: 'line_number',
        headerName: paymentsText.allocationTable.lineNumber,
        minWidth: 88,
        maxWidth: 100,
        valueGetter: (params) => params.data?.line_number ?? '',
      },
      {
        colId: 'department_name',
        headerName: paymentsText.allocationTable.department,
        minWidth: 150,
      },
      {
        colId: 'service_name',
        headerName: paymentsText.allocationTable.service,
        minWidth: 170,
      },
      {
        colId: 'service_date',
        headerName: paymentsText.allocationTable.serviceDate,
        minWidth: 145,
      },
      {
        colId: 'dress_code',
        headerName: paymentsText.allocationTable.dress,
        minWidth: 120,
        valueGetter: (params) => params.data?.dress_code ?? EMPTY_VALUE,
      },
      {
        colId: 'line_price',
        headerName: paymentsText.allocationTable.price,
        minWidth: 115,
      },
      {
        colId: 'payment_state',
        headerName: paymentsText.allocationTable.paymentState,
        minWidth: 145,
        valueGetter: (params) => (params.data ? linePaymentStateLabel(language, params.data.payment_state) : ''),
      },
      {
        colId: 'remaining_amount',
        headerName: paymentsText.allocationTable.remaining,
        minWidth: 115,
      },
      {
        colId: 'allocation_amount',
        headerName: paymentsText.allocationTable.allocationAmount,
        minWidth: 150,
        pinned: language === 'ar' ? 'left' : 'right',
        sortable: false,
        filter: false,
        suppressKeyboardEvent: suppressGridKeyboardEvent,
        cellRenderer: ({ data }: ICellRendererParams<PaymentTargetLineRecord>) =>
          data ? (
            <StableNumericCell
              value={allocationValues[data.line_id] ?? ''}
              onFlush={(value) => setAllocationValues((current) => ({ ...current, [data.line_id]: value }))}
            />
          ) : null,
      },
    ],
    [allocationValues, language, paymentsText.allocationTable],
  );

  function gridHeightFor(booking: PaymentTargetBookingRecord) {
    return Math.min(420, Math.max(220, booking.lines.length * 58 + 92));
  }

  return (
    <Stack spacing={2}>
      <Box>
        <Typography variant='h5'>
          {document ? `${paymentsText.builder.updateTitlePrefix} ${document.payment_number}` : paymentsText.builder.title}
        </Typography>
        <Typography color='text.secondary'>{paymentsText.builder.subtitle}</Typography>
      </Box>

      <Alert severity='info'>
        {`${paymentsText.builder.scopeSummaryPrefix}: ${target.customer_name} | ${paymentsText.summary.branch}: ${target.branch_name} | ${paymentsText.summary.totalOpen}: ${target.total_remaining}`}
      </Alert>
      {document ? <Alert severity='info'>{paymentsText.builder.editNotice}</Alert> : null}

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
        <TextField label={paymentsText.builder.paymentDate} type='date' InputLabelProps={{ shrink: true }} value={paymentDate} onChange={(event) => setPaymentDate(event.target.value)} />
        <TextField select label={paymentsText.builder.paymentMethod} value={paymentMethodId} onChange={(event) => setPaymentMethodId(event.target.value)} sx={{ minWidth: 220 }}>
          {paymentMethods.map((item) => (
            <MenuItem key={item.id} value={item.id}>
              {item.name}
            </MenuItem>
          ))}
        </TextField>
        <TextField label={paymentsText.builder.selectedTotal} value={selectedTotal} InputProps={{ readOnly: true }} />
      </Stack>

      <TextField label={paymentsText.builder.notes} value={notes} multiline minRows={3} onChange={(event) => setNotes(event.target.value)} />

      {target.bookings.map((booking) => (
        <Stack key={booking.booking_id} spacing={1.25}>
          <Typography variant='h6'>{`${booking.booking_number} • ${paymentsText.summary.status}: ${bookingStatusLabel(language, booking.booking_status)}`}</Typography>
          <Typography color='text.secondary'>{`${paymentsText.summary.documentTotal} ${booking.total_amount} | ${paymentsText.summary.paid} ${booking.paid_total} | ${paymentsText.summary.remaining} ${booking.remaining_amount}`}</Typography>

          <AppAgGrid
            tableKey={`payment-document-builder-${booking.booking_id}`}
            rows={booking.lines}
            columns={allocationColumns}
            language={language}
            searchLabel={paymentsText.page.searchLabel}
            searchPlaceholder={paymentsText.page.searchLabel}
            columnsLabel={commonText.actions}
            exportLabel='Export'
            resetLabel='Reset'
            closeLabel='Close'
            noRowsLabel={language === 'ar' ? 'لا توجد سطور مفتوحة' : 'No open lines'}
            rowsPerPageLabel={language === 'ar' ? 'عدد الصفوف' : 'Rows per page'}
            getRowId={(params) => params.data.line_id}
            hideToolbar
            pagination={false}
            height={gridHeightFor(booking)}
          />
        </Stack>
      ))}

      <Stack direction='row' spacing={1} justifyContent='flex-end'>
        <Button onClick={onCancel}>{commonText.cancel}</Button>
        <Button
          variant='contained'
          startIcon={<SaveOutlinedIcon />}
          disabled={saving || selectedTotal <= 0 || !paymentMethodId}
          onClick={() => void handleSave()}
        >
          {paymentsText.builder.save}
        </Button>
      </Stack>
    </Stack>
  );
}
