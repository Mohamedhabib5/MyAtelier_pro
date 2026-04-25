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
  const title = language === 'ar' ? (isArchive ? 'طھط£ظƒظٹط¯ ط§ظ„ط£ط±ط´ظپط©' : 'طھط£ظƒظٹط¯ ط§ظ„ط§ط³طھط¹ط§ط¯ط©') : isArchive ? 'Confirm archive' : 'Confirm restore';
  const description =
    language === 'ar'
      ? isArchive
        ? `ط³ظٹطھظ… ط£ط±ط´ظپط© ${entityLabel}. ظٹظ…ظƒظ†ظƒ ط¥ط¶ط§ظپط© ط³ط¨ط¨ ط§ط®طھظٹط§ط±ظٹ.`
        : `ط³ظٹطھظ… ط§ط³طھط¹ط§ط¯ط© ${entityLabel}. ظٹظ…ظƒظ†ظƒ ط¥ط¶ط§ظپط© ط³ط¨ط¨ ط§ط®طھظٹط§ط±ظٹ.`
      : isArchive
        ? `This will archive ${entityLabel}. You can add an optional reason.`
        : `This will restore ${entityLabel}. You can add an optional reason.`;
  const reasonLabel = language === 'ar' ? 'ط§ظ„ط³ط¨ط¨ (ط§ط®طھظٹط§ط±ظٹ)' : 'Reason (optional)';
  const confirmLabel = language === 'ar' ? (isArchive ? 'ط£ط±ط´ظپط©' : 'ط§ط³طھط¹ط§ط¯ط©') : isArchive ? 'Archive' : 'Restore';
  const cancelLabel = language === 'ar' ? 'ط¥ظ„ط؛ط§ط،' : 'Cancel';

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
