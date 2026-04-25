import { Button, Stack, TextField } from '@mui/material';

import { AppDialogShell } from '../../components/AppDialogShell';
import { StableNumericField } from '../../components/inputs/StableNumericField';
import { useCommonText } from '../../text/common';
import { useCatalogText } from '../../text/catalog';
import type { DepartmentRecord } from './api';

export type ServiceFormState = {
  department_id: string;
  name: string;
  default_price: string;
  duration_minutes: string;
  notes: string;
  is_active: boolean;
};

type ServiceFormDialogProps = {
  open: boolean;
  editing: boolean;
  form: ServiceFormState;
  departments: DepartmentRecord[];
  onChange: (next: ServiceFormState) => void;
  onClose: () => void;
  onSave: () => void;
};

export function ServiceFormDialog({ open, editing, form, departments, onChange, onClose, onSave }: ServiceFormDialogProps) {
  const commonText = useCommonText();
  const catalogText = useCatalogText();

  return (
    <AppDialogShell
      open={open}
      onClose={onClose}
      title={editing ? catalogText.services.dialogEdit : catalogText.services.dialogCreate}
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
        <TextField select SelectProps={{ native: true }} label={catalogText.services.tableDepartment} value={form.department_id} onChange={(event) => onChange({ ...form, department_id: event.target.value })}>
          {departments.map((department) => (
            <option key={department.id} value={department.id}>
              {department.name}
            </option>
          ))}
        </TextField>
        <TextField label={catalogText.services.name} value={form.name} onChange={(event) => onChange({ ...form, name: event.target.value })} />
        <StableNumericField
          label={catalogText.services.price}
          value={form.default_price}
          onValueChange={(value) => onChange({ ...form, default_price: value })}
        />
        <StableNumericField
          label={catalogText.services.duration}
          value={form.duration_minutes}
          onValueChange={(value) => onChange({ ...form, duration_minutes: value })}
          allowDecimal={false}
        />
        <TextField label={catalogText.services.notes} value={form.notes} multiline minRows={3} onChange={(event) => onChange({ ...form, notes: event.target.value })} />
        {editing ? (
          <TextField select SelectProps={{ native: true }} label={catalogText.departments.status} value={form.is_active ? 'active' : 'inactive'} onChange={(event) => onChange({ ...form, is_active: event.target.value === 'active' })}>
            <option value='active'>{catalogText.status.active}</option>
            <option value='inactive'>{catalogText.status.inactive}</option>
          </TextField>
        ) : null}
      </Stack>
    </AppDialogShell>
  );
}
