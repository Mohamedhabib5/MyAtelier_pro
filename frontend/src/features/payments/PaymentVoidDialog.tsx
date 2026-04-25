import { Alert, Button, Checkbox, FormControlLabel, Stack, TextField } from '@mui/material';

import { AppDialogShell } from '../../components/AppDialogShell';
import { useCommonText } from '../../text/common';
import { usePaymentsText } from '../../text/payments';
import type { PaymentDocumentSummaryRecord } from './api';

type PaymentVoidDialogProps = {
  open: boolean;
  payment: PaymentDocumentSummaryRecord | null;
  voidDate: string;
  voidReason: string;
  overrideLock: boolean;
  overrideReason: string;
  onClose: () => void;
  onVoidDateChange: (value: string) => void;
  onVoidReasonChange: (value: string) => void;
  onOverrideLockChange: (value: boolean) => void;
  onOverrideReasonChange: (value: string) => void;
  onSubmit: () => void;
};

export function PaymentVoidDialog({
  open,
  payment,
  voidDate,
  voidReason,
  overrideLock,
  overrideReason,
  onClose,
  onVoidDateChange,
  onVoidReasonChange,
  onOverrideLockChange,
  onOverrideReasonChange,
  onSubmit,
}: PaymentVoidDialogProps) {
  const commonText = useCommonText();
  const paymentsText = usePaymentsText();
  const isArabic = /[\u0600-\u06FF]/.test(paymentsText.voidDialog.title);
  const overrideLabel = isArabic ? 'ط§ط³طھط®ط¯ط§ظ… Override ظ„ظ‚ظپظ„ ط§ظ„ظپطھط±ط©' : 'Use period-lock override';
  const overrideReasonLabel = isArabic ? 'ط³ط¨ط¨ Override' : 'Override reason';

  return (
    <AppDialogShell
      open={open}
      onClose={onClose}
      title={paymentsText.voidDialog.title}
      maxWidth='sm'
      fullScreenOnMobile
      actions={
        <>
          <Button onClick={onClose}>{commonText.cancel}</Button>
          <Button color='warning' variant='contained' onClick={onSubmit}>
            {paymentsText.voidDialog.confirm}
          </Button>
        </>
      }
    >
      <Stack spacing={2}>
        {payment ? <Alert severity='warning'>{`${payment.payment_number} ${paymentsText.voidDialog.warningSuffix}`}</Alert> : null}
        <TextField label={paymentsText.voidDialog.date} type='date' InputLabelProps={{ shrink: true }} value={voidDate} onChange={(event) => onVoidDateChange(event.target.value)} />
        <TextField label={paymentsText.voidDialog.reason} value={voidReason} multiline minRows={3} onChange={(event) => onVoidReasonChange(event.target.value)} />
        <FormControlLabel
          control={<Checkbox checked={overrideLock} onChange={(event) => onOverrideLockChange(event.target.checked)} />}
          label={overrideLabel}
        />
        {overrideLock ? (
          <TextField
            label={overrideReasonLabel}
            value={overrideReason}
            multiline
            minRows={2}
            onChange={(event) => onOverrideReasonChange(event.target.value)}
          />
        ) : null}
      </Stack>
    </AppDialogShell>
  );
}
