import { Button, Stack, TextField } from '@mui/material';

import { AppDialogShell } from '../../components/AppDialogShell';
import { useLanguage } from '../language/LanguageProvider';
import { useCommonText } from '../../text/common';
import { useCustomersText } from '../../text/customers';

export type CustomerFormState = {
  full_name: string;
  registration_date: string;
  groom_name: string;
  bride_name: string;
  phone: string;
  phone_2: string;
  email: string;
  address: string;
  notes: string;
  is_active: boolean;
};

type CustomerFormDialogProps = {
  open: boolean;
  editing: boolean;
  form: CustomerFormState;
  onChange: (next: CustomerFormState) => void;
  onClose: () => void;
  onSave: () => void;
};

export function CustomerFormDialog({ open, editing, form, onChange, onClose, onSave }: CustomerFormDialogProps) {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const customersText = useCustomersText();

  const registrationDateLabel = language === 'ar' ? 'تاريخ التسجيل' : 'Registration date';

  return (
    <AppDialogShell
      open={open}
      onClose={onClose}
      title={editing ? customersText.dialog.edit : customersText.dialog.create}
      maxWidth='sm'
      actions={
        <>
          <Button onClick={onClose}>{commonText.cancel}</Button>
          <Button variant='contained' onClick={onSave}>
            {commonText.save}
          </Button>
        </>
      }
    >
      <Stack spacing={2.25}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          <TextField
            fullWidth
            label={customersText.dialog.brideName}
            value={form.bride_name}
            onChange={(event) => onChange({ ...form, bride_name: event.target.value })}
          />
          <TextField
            fullWidth
            label={customersText.dialog.groomName}
            value={form.groom_name}
            onChange={(event) => onChange({ ...form, groom_name: event.target.value })}
          />
        </Stack>

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          <TextField
            fullWidth
            label={customersText.dialog.phone}
            value={form.phone}
            onChange={(event) => onChange({ ...form, phone: event.target.value })}
          />
          <TextField
            fullWidth
            label={customersText.dialog.phone2}
            value={form.phone_2}
            onChange={(event) => onChange({ ...form, phone_2: event.target.value })}
          />
        </Stack>

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          <TextField
            fullWidth
            label={customersText.dialog.address}
            value={form.address}
            onChange={(event) => onChange({ ...form, address: event.target.value })}
          />
          <TextField
            fullWidth
            label={registrationDateLabel}
            type='date'
            InputLabelProps={{ shrink: true }}
            value={form.registration_date}
            onChange={(event) => onChange({ ...form, registration_date: event.target.value })}
          />
        </Stack>

        <TextField
          fullWidth
          label={customersText.dialog.notes}
          multiline
          minRows={3}
          value={form.notes}
          onChange={(event) => onChange({ ...form, notes: event.target.value })}
        />

        {editing ? (
          <TextField
            select
            fullWidth
            SelectProps={{ native: true }}
            label={customersText.dialog.status}
            value={form.is_active ? 'active' : 'inactive'}
            onChange={(event) => onChange({ ...form, is_active: event.target.value === 'active' })}
          >
            <option value='active'>{customersText.status.active}</option>
            <option value='inactive'>{customersText.status.inactive}</option>
          </TextField>
        ) : null}
      </Stack>
    </AppDialogShell>
  );
}
