import { Alert, Button, Checkbox, FormControlLabel, MenuItem, Stack, TextField, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';

import { useLanguage } from '../features/language/LanguageProvider';
import { executeDestructiveDelete, listDestructiveReasons, previewDestructiveDelete, type DestructiveDeleteRecord, type DestructivePreviewRecord } from '../features/settings/api';
import { AppDialogShell } from './AppDialogShell';

type DestructiveDeleteDialogProps = {
  open: boolean;
  entityType: 'dress' | 'customer' | 'service' | 'department';
  entityId: string | null;
  entityLabel: string;
  onClose: () => void;
  onDeleted: (result: DestructiveDeleteRecord) => void;
  onError: (message: string) => void;
};

export function DestructiveDeleteDialog({ open, entityType, entityId, entityLabel, onClose, onDeleted, onError }: DestructiveDeleteDialogProps) {
  const { language } = useLanguage();
  const [reasonCode, setReasonCode] = useState('entry_mistake');
  const [reasonText, setReasonText] = useState('');
  const [overrideLock, setOverrideLock] = useState(false);
  const [overrideReason, setOverrideReason] = useState('');
  const [preview, setPreview] = useState<DestructivePreviewRecord | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);

  const reasonsQuery = useQuery({
    queryKey: ['destructive-reasons', 'hard_delete'],
    queryFn: () => listDestructiveReasons('hard_delete'),
    enabled: open,
  });

  const previewMutation = useMutation({
    mutationFn: previewDestructiveDelete,
    onSuccess: (result) => {
      setLocalError(null);
      setPreview(result);
    },
    onError: (error: Error) => {
      setPreview(null);
      setLocalError(error.message);
      onError(error.message);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: executeDestructiveDelete,
    onSuccess: (result) => {
      setLocalError(null);
      onDeleted(result);
      onClose();
    },
    onError: (error: Error) => {
      setLocalError(error.message);
      onError(error.message);
    },
  });

  const reasonOptions = useMemo(() => reasonsQuery.data ?? [], [reasonsQuery.data]);
  const impactEntries = useMemo(() => Object.entries(preview?.impact ?? {}), [preview?.impact]);

  useEffect(() => {
    if (!open) return;
    setPreview(null);
    setLocalError(null);
    setReasonText('');
    setReasonCode('entry_mistake');
    setOverrideLock(false);
    setOverrideReason('');
  }, [open, entityId]);

  async function handlePreview() {
    if (!entityId) return;
    await previewMutation.mutateAsync({ entity_type: entityType, entity_id: entityId, reason_code: reasonCode, reason_text: reasonText || null });
  }

  async function handleDelete() {
    if (!entityId || !preview?.eligible_for_hard_delete) return;
    await deleteMutation.mutateAsync({
      entity_type: entityType,
      entity_id: entityId,
      reason_code: reasonCode,
      reason_text: reasonText || null,
      override_lock: overrideLock || undefined,
      override_reason: overrideLock ? overrideReason || null : undefined,
    });
  }

  const previewReady = Boolean(preview);
  const canDelete = Boolean(preview?.eligible_for_hard_delete);
  const title = language === 'ar' ? 'ط­ط°ظپ طھطµط­ظٹط­ظٹ' : 'Corrective delete';
  const reasonLabel = language === 'ar' ? 'ط³ط¨ط¨ ط§ظ„ط­ط°ظپ' : 'Delete reason';
  const notesLabel = language === 'ar' ? 'ظ…ظ„ط§ط­ط¸ط§طھ ط¥ط¶ط§ظپظٹط© (ط§ط®طھظٹط§ط±ظٹ)' : 'Additional notes (optional)';
  const previewButton = language === 'ar' ? 'ظ…ط¹ط§ظٹظ†ط© ط§ظ„طھط£ط«ظٹط±' : 'Preview impact';
  const deleteButton = language === 'ar' ? 'طھظ†ظپظٹط° ط§ظ„ط­ط°ظپ' : 'Delete';
  const cancelButton = language === 'ar' ? 'ط¥ظ„ط؛ط§ط،' : 'Cancel';
  const overrideLabel = language === 'ar' ? 'ط§ط³طھط®ط¯ط§ظ… Override ظ„ظ‚ظپظ„ ط§ظ„ظپطھط±ط©' : 'Use period-lock override';
  const overrideReasonLabel = language === 'ar' ? 'ط³ط¨ط¨ Override' : 'Override reason';
  const busy = previewMutation.isPending || deleteMutation.isPending;

  return (
    <AppDialogShell
      open={open}
      onClose={onClose}
      title={title}
      maxWidth='sm'
      fullScreenOnMobile
      actions={
        <>
          <Button onClick={onClose} disabled={busy}>
            {cancelButton}
          </Button>
          <Button variant='outlined' onClick={() => void handlePreview()} disabled={!entityId || busy}>
            {previewButton}
          </Button>
          <Button variant='contained' color='error' onClick={() => void handleDelete()} disabled={!canDelete || deleteMutation.isPending}>
            {deleteButton}
          </Button>
        </>
      }
    >
      <Stack spacing={2}>
        <Typography color='text.secondary'>
          {language === 'ar' ? `ط³طھطھظ… ظ…ط±ط§ط¬ط¹ط© طھط£ط«ظٹط± ط­ط°ظپ ${entityLabel} ظ‚ط¨ظ„ ط§ظ„طھظ†ظپظٹط°.` : `Delete impact for ${entityLabel} will be checked before execution.`}
        </Typography>
        {localError || reasonsQuery.error ? <Alert severity='error'>{localError ?? (reasonsQuery.error as Error).message}</Alert> : null}
        <TextField
          select
          label={reasonLabel}
          value={reasonCode}
          onChange={(event) => setReasonCode(event.target.value)}
          disabled={reasonsQuery.isLoading || busy}
        >
          {reasonOptions.map((reason) => (
            <MenuItem key={reason.code} value={reason.code}>
              {language === 'ar' ? reason.label_ar : reason.label_en}
            </MenuItem>
          ))}
        </TextField>
        <TextField label={notesLabel} value={reasonText} onChange={(event) => setReasonText(event.target.value)} multiline minRows={3} disabled={busy} />
        <FormControlLabel control={<Checkbox checked={overrideLock} onChange={(event) => setOverrideLock(event.target.checked)} />} label={overrideLabel} />
        {overrideLock ? <TextField label={overrideReasonLabel} value={overrideReason} onChange={(event) => setOverrideReason(event.target.value)} multiline minRows={2} disabled={busy} /> : null}
        {previewReady ? (
          <Alert severity={canDelete ? 'success' : 'warning'}>
            <Typography>{canDelete ? (language === 'ar' ? 'ط§ظ„ط­ط°ظپ ظ…ط³ظ…ظˆط­ ط¨ط¹ط¯ ط§ظ„ظپط­طµ.' : 'Delete is eligible after checks.') : language === 'ar' ? 'ط§ظ„ط­ط°ظپ ط؛ظٹط± ظ…ط³ظ…ظˆط­ ط¨ط³ط¨ط¨ ط±ظˆط§ط¨ط· طھط´ط؛ظٹظ„ظٹط©.' : 'Delete is blocked due to operational links.'}</Typography>
            {impactEntries.length ? (
              <Typography sx={{ mt: 1 }}>
                {language === 'ar' ? 'ظ…ظ„ط®طµ ط§ظ„طھط£ط«ظٹط±' : 'Impact summary'}: {impactEntries.map(([key, value]) => `${key.replaceAll('_', ' ')}=${value}`).join(', ')}
              </Typography>
            ) : null}
            {preview?.blockers?.length ? <Typography sx={{ mt: 1 }}>{preview.blockers.join(' | ')}</Typography> : null}
          </Alert>
        ) : null}
      </Stack>
    </AppDialogShell>
  );
}
