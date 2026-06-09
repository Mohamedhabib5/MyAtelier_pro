import { Alert, Button, Checkbox, FormControlLabel, Stack, TextField } from '@mui/material';

import { AppDialogShell } from '../../components/AppDialogShell';
import { useCommonText } from '../../text/common';
import { useDisbursementsText } from '../../text/disbursements';
import type { DisbursementVoucherRecord } from './api';
import { AppDateField } from '../../components/inputs/AppDateField';

type DisbursementVoidDialogProps = {
  open: boolean;
  voucher: DisbursementVoucherRecord | null;
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

export function DisbursementVoidDialog({
  open,
  voucher,
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
}: DisbursementVoidDialogProps) {
  const commonText = useCommonText();
  const text = useDisbursementsText();
  const isArabic = /[\u0600-\u06FF]/.test(text.voidDialog.title);
  const overrideLabel = isArabic ? 'استخدام Override لقفل الفترة' : 'Use period-lock override';
  const overrideReasonLabel = isArabic ? 'سبب Override' : 'Override reason';
  const warningSuffix = isArabic 
    ? 'وسيتم عكس قيده المحاسبي بالكامل بدل حذفه.' 
    : 'and its linked journal entry will be fully reversed instead of deleted.';

  return (
    <AppDialogShell
      open={open}
      onClose={onClose}
      title={text.voidDialog.title}
      maxWidth='sm'
      fullScreenOnMobile
      actions={
        <>
          <Button onClick={onClose}>{commonText.cancel}</Button>
          <Button color='warning' variant='contained' onClick={onSubmit}>
            {text.voidDialog.confirm}
          </Button>
        </>
      }
    >
      <Stack spacing={2}>
        {voucher ? <Alert severity='warning'>{`${voucher.voucher_number} ${warningSuffix}`}</Alert> : null}
        <AppDateField label={text.voidDialog.date} value={voidDate} onChange={(val) => onVoidDateChange(val)} />
        <TextField label={text.voidDialog.reason} value={voidReason} multiline minRows={3} onChange={(event) => onVoidReasonChange(event.target.value)} />
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
