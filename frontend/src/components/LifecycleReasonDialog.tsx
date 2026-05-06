import { Button, Stack, TextField, Typography } from '@mui/material';

import { AppDialogShell } from './AppDialogShell';

type LifecycleReasonDialogProps = {
  open: boolean;
  mode: 'archive' | 'restore';
  entityLabel: string;
  reason: string;
  language: 'ar' | 'en';
  onReasonChange: (value: string) => void;
  onCancel: () => void;
  onConfirm: () => void;
  loading?: boolean;
};

export function LifecycleReasonDialog({
  open,
  mode,
  entityLabel,
  reason,
  language,
  onReasonChange,
  onCancel,
  onConfirm,
  loading = false,
}: LifecycleReasonDialogProps) {
  const isArchive = mode === 'archive';
  const title = language === 'ar' ? (isArchive ? 'تأكيد الأرشفة' : 'تأكيد الاستعادة') : isArchive ? 'Confirm archive' : 'Confirm restore';
  const description =
    language === 'ar'
      ? isArchive
        ? `سيتم أرشفة ${entityLabel}. يمكنك إضافة سبب اختياري.`
        : `سيتم استعادة ${entityLabel}. يمكنك إضافة سبب اختياري.`
      : isArchive
        ? `This will archive ${entityLabel}. You can add an optional reason.`
        : `This will restore ${entityLabel}. You can add an optional reason.`;
  const reasonLabel = language === 'ar' ? 'السبب (اختياري)' : 'Reason (optional)';
  const confirmLabel = language === 'ar' ? (isArchive ? 'أرشفة' : 'استعادة') : isArchive ? 'Archive' : 'Restore';
  const cancelLabel = language === 'ar' ? 'إلغاء' : 'Cancel';

  return (
    <AppDialogShell
      open={open}
      onClose={onCancel}
      title={title}
      maxWidth='sm'
      fullScreenOnMobile
      actions={
        <>
          <Button onClick={onCancel} disabled={loading}>
            {cancelLabel}
          </Button>
          <Button variant='contained' color={isArchive ? 'warning' : 'success'} onClick={onConfirm} disabled={loading}>
            {confirmLabel}
          </Button>
        </>
      }
    >
      <Stack spacing={2}>
        <Typography color='text.secondary'>{description}</Typography>
        <TextField
          label={reasonLabel}
          value={reason}
          onChange={(event) => onReasonChange(event.target.value)}
          multiline
          minRows={3}
        />
      </Stack>
    </AppDialogShell>
  );
}
