import { Alert, Button, Dialog, DialogActions, DialogContent, DialogTitle, Stack, TextField } from '@mui/material';

import { useCommonText } from '../../text/common';
import { usePaymentsText } from '../../text/payments';
import type { PaymentDocumentSummaryRecord } from './api';

type PaymentVoidDialogProps = {
  open: boolean;
  payment: PaymentDocumentSummaryRecord | null;
  voidDate: string;
  voidReason: string;
  onClose: () => void;
  onVoidDateChange: (value: string) => void;
  onVoidReasonChange: (value: string) => void;
  onSubmit: () => void;
};

export function PaymentVoidDialog({
  open,
  payment,
  voidDate,
  voidReason,
  onClose,
  onVoidDateChange,
  onVoidReasonChange,
  onSubmit,
}: PaymentVoidDialogProps) {
  const commonText = useCommonText();
  const paymentsText = usePaymentsText();

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth='sm'>
      <DialogTitle>{paymentsText.voidDialog.title}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ pt: 1 }}>
          {payment ? <Alert severity='warning'>{`${payment.payment_number} ${paymentsText.voidDialog.warningSuffix}`}</Alert> : null}
          <TextField label={paymentsText.voidDialog.date} type='date' InputLabelProps={{ shrink: true }} value={voidDate} onChange={(event) => onVoidDateChange(event.target.value)} />
          <TextField label={paymentsText.voidDialog.reason} value={voidReason} multiline minRows={3} onChange={(event) => onVoidReasonChange(event.target.value)} />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{commonText.cancel}</Button>
        <Button color='warning' variant='contained' onClick={onSubmit}>
          {paymentsText.voidDialog.confirm}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
