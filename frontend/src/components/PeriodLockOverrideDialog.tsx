import { Button, Stack, TextField, Typography } from '@mui/material';
import { useMemo, useState } from 'react';

import { useLanguage } from '../features/language/LanguageProvider';
import { AppDialogShell } from './AppDialogShell';

type PeriodLockOverrideDialogProps = {
  open: boolean;
  titleAr: string;
  titleEn: string;
  descriptionAr: string;
  descriptionEn: string;
  confirmAr?: string;
  confirmEn?: string;
  onClose: () => void;
  onConfirm: (reason: string) => Promise<void> | void;
};

export function PeriodLockOverrideDialog({
  open,
  titleAr,
  titleEn,
  descriptionAr,
  descriptionEn,
  confirmAr = 'طھط£ظƒظٹط¯ Override',
  confirmEn = 'Confirm override',
  onClose,
  onConfirm,
}: PeriodLockOverrideDialogProps) {
  const { language } = useLanguage();
  const [reason, setReason] = useState('');
  const [saving, setSaving] = useState(false);

  const ui = useMemo(
    () =>
      language === 'ar'
        ? {
            title: titleAr,
            description: descriptionAr,
            reasonLabel: 'ط³ط¨ط¨ Override',
            confirm: confirmAr,
            cancel: 'ط¥ظ„ط؛ط§ط،',
          }
        : {
            title: titleEn,
            description: descriptionEn,
            reasonLabel: 'Override reason',
            confirm: confirmEn,
            cancel: 'Cancel',
          },
    [confirmAr, confirmEn, descriptionAr, descriptionEn, language, titleAr, titleEn],
  );

  async function handleConfirm() {
    const trimmed = reason.trim();
    if (!trimmed || saving) return;
    setSaving(true);
    try {
      await onConfirm(trimmed);
      setReason('');
      onClose();
    } finally {
      setSaving(false);
    }
  }

  function handleClose() {
    if (saving) return;
    setReason('');
    onClose();
  }

  return (
    <AppDialogShell
      open={open}
      onClose={handleClose}
      title={ui.title}
      maxWidth='sm'
      fullScreenOnMobile
      actions={
        <>
          <Button onClick={handleClose} disabled={saving}>
            {ui.cancel}
          </Button>
          <Button variant='contained' color='warning' onClick={() => void handleConfirm()} disabled={saving || !reason.trim()}>
            {ui.confirm}
          </Button>
        </>
      }
    >
      <Stack spacing={2}>
        <Typography color='text.secondary'>{ui.description}</Typography>
        <TextField
          label={ui.reasonLabel}
          value={reason}
          onChange={(event) => setReason(event.target.value)}
          multiline
          minRows={3}
          disabled={saving}
        />
      </Stack>
    </AppDialogShell>
  );
}
