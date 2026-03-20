import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined';
import { Alert, Box, Button, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material';
import { useEffect, useMemo, useState } from 'react';

import { useLanguage } from '../../features/language/LanguageProvider';
import { EMPTY_VALUE, bookingStatusLabel, linePaymentStateLabel, useCommonText } from '../../text/common';
import { usePaymentsText } from '../../text/payments';
import type { PaymentDocumentPayload, PaymentDocumentRecord, PaymentTargetDetailRecord } from './api';

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export function PaymentDocumentBuilder({
  target,
  document,
  saving,
  onSave,
  onCancel,
}: {
  target: PaymentTargetDetailRecord;
  document: PaymentDocumentRecord | null;
  saving: boolean;
  onSave: (payload: PaymentDocumentPayload) => Promise<void>;
  onCancel: () => void;
}) {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const paymentsText = usePaymentsText();
  const [paymentDate, setPaymentDate] = useState(todayIso());
  const [notes, setNotes] = useState('');
  const [allocationValues, setAllocationValues] = useState<Record<string, string>>({});

  useEffect(() => {
    setPaymentDate(document?.payment_date ?? todayIso());
    setNotes(document?.notes ?? '');
    const seeded: Record<string, string> = {};
    for (const allocation of document?.allocations ?? []) {
      seeded[allocation.booking_line_id] = String(allocation.allocated_amount);
    }
    setAllocationValues(seeded);
  }, [document, target]);

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
      payment_date: paymentDate,
      notes: notes || null,
      allocations,
    });
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
        <TextField label={paymentsText.builder.selectedTotal} value={selectedTotal} InputProps={{ readOnly: true }} />
      </Stack>

      <TextField label={paymentsText.builder.notes} value={notes} multiline minRows={3} onChange={(event) => setNotes(event.target.value)} />

      {target.bookings.map((booking) => (
        <Stack key={booking.booking_id} spacing={1}>
          <Typography variant='h6'>{`${booking.booking_number} • ${paymentsText.summary.status}: ${bookingStatusLabel(language, booking.booking_status)}`}</Typography>
          <Typography color='text.secondary'>{`${paymentsText.summary.documentTotal} ${booking.total_amount} | ${paymentsText.summary.paid} ${booking.paid_total} | ${paymentsText.summary.remaining} ${booking.remaining_amount}`}</Typography>
          <Table size='small'>
            <TableHead>
              <TableRow>
                <TableCell>{paymentsText.allocationTable.lineNumber}</TableCell>
                <TableCell>{paymentsText.allocationTable.department}</TableCell>
                <TableCell>{paymentsText.allocationTable.service}</TableCell>
                <TableCell>{paymentsText.allocationTable.serviceDate}</TableCell>
                <TableCell>{paymentsText.allocationTable.dress}</TableCell>
                <TableCell>{paymentsText.allocationTable.price}</TableCell>
                <TableCell>{paymentsText.allocationTable.paymentState}</TableCell>
                <TableCell>{paymentsText.allocationTable.remaining}</TableCell>
                <TableCell>{paymentsText.allocationTable.allocationAmount}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {booking.lines.map((line) => (
                <TableRow key={line.line_id}>
                  <TableCell>{line.line_number}</TableCell>
                  <TableCell>{line.department_name}</TableCell>
                  <TableCell>{line.service_name}</TableCell>
                  <TableCell>{line.service_date}</TableCell>
                  <TableCell>{line.dress_code ?? EMPTY_VALUE}</TableCell>
                  <TableCell>{line.line_price}</TableCell>
                  <TableCell>{linePaymentStateLabel(language, line.payment_state)}</TableCell>
                  <TableCell>{line.remaining_amount}</TableCell>
                  <TableCell>
                    <TextField type='number' value={allocationValues[line.line_id] ?? ''} onChange={(event) => setAllocationValues((current) => ({ ...current, [line.line_id]: event.target.value }))} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Stack>
      ))}

      <Stack direction='row' spacing={1} justifyContent='flex-end'>
        <Button onClick={onCancel}>{commonText.cancel}</Button>
        <Button variant='contained' startIcon={<SaveOutlinedIcon />} disabled={saving || selectedTotal <= 0} onClick={() => void handleSave()}>
          {paymentsText.builder.save}
        </Button>
      </Stack>
    </Stack>
  );
}
