import { Button, Stack, TextField } from '@mui/material';

import { AppDialogShell } from '../../components/AppDialogShell';
import { useLanguage } from '../language/LanguageProvider';
import { useCommonText } from '../../text/common';
import { dressStatusLabel, useDressesText } from '../../text/dresses';

export type DressFormState = {
  code: string;
  dress_type: string;
  purchase_date: string;
  status: string;
  description: string;
  image_path: string;
  is_active: boolean;
};

type DressFormDialogProps = {
  open: boolean;
  editing: boolean;
  form: DressFormState;
  onChange: (next: DressFormState) => void;
  onClose: () => void;
  onSave: () => void;
};

export function DressFormDialog({ open, editing, form, onChange, onClose, onSave }: DressFormDialogProps) {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const dressesText = useDressesText();

  return (
    <AppDialogShell
      open={open}
      onClose={onClose}
      title={editing ? dressesText.dialog.edit : dressesText.dialog.create}
      actions={
        <>
          <Button onClick={onClose}>{commonText.cancel}</Button>
          <Button variant='contained' onClick={onSave}>
            {commonText.save}
          </Button>
        </>
      }
    >
      <Stack spacing={2}>
        <TextField label={dressesText.dialog.code} value={form.code} onChange={(event) => onChange({ ...form, code: event.target.value })} />
        <TextField label={dressesText.dialog.type} value={form.dress_type} onChange={(event) => onChange({ ...form, dress_type: event.target.value })} />
        <TextField label={dressesText.dialog.purchaseDate} type='date' InputLabelProps={{ shrink: true }} value={form.purchase_date} onChange={(event) => onChange({ ...form, purchase_date: event.target.value })} />
        <TextField select SelectProps={{ native: true }} label={dressesText.dialog.status} value={form.status} onChange={(event) => onChange({ ...form, status: event.target.value })}>
          <option value='available'>{dressStatusLabel(language, 'available')}</option>
          <option value='reserved'>{dressStatusLabel(language, 'reserved')}</option>
          <option value='with_customer'>{dressStatusLabel(language, 'with_customer')}</option>
          <option value='maintenance'>{dressStatusLabel(language, 'maintenance')}</option>
        </TextField>
        <TextField label={dressesText.dialog.description} value={form.description} multiline minRows={3} onChange={(event) => onChange({ ...form, description: event.target.value })} />
        <TextField label={dressesText.dialog.imageRef} value={form.image_path} onChange={(event) => onChange({ ...form, image_path: event.target.value })} helperText={dressesText.dialog.imageHint} />
        {editing ? (
          <TextField select SelectProps={{ native: true }} label={dressesText.dialog.operationalStatus} value={form.is_active ? 'active' : 'inactive'} onChange={(event) => onChange({ ...form, is_active: event.target.value === 'active' })}>
            <option value='active'>{dressesText.status.active}</option>
            <option value='inactive'>{dressesText.status.inactive}</option>
          </TextField>
        ) : null}
      </Stack>
    </AppDialogShell>
  );
}
