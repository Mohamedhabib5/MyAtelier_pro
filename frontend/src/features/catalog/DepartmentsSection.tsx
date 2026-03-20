import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import PlaylistAddOutlinedIcon from '@mui/icons-material/PlaylistAddOutlined';
import { Alert, Button, Chip, Dialog, DialogActions, DialogContent, DialogTitle, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField } from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';

import { SectionCard } from '../../components/SectionCard';
import { queryClient } from '../../lib/queryClient';
import { useCommonText } from '../../text/common';
import { useCatalogText } from '../../text/catalog';
import { createDepartment, updateDepartment, type DepartmentRecord } from './api';

function emptyForm() {
  return { code: '', name: '', is_active: true };
}

export function DepartmentsSection({ departments }: { departments: DepartmentRecord[] }) {
  const commonText = useCommonText();
  const catalogText = useCatalogText();
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingDepartment, setEditingDepartment] = useState<DepartmentRecord | null>(null);
  const [form, setForm] = useState(emptyForm());

  const createMutation = useMutation({
    mutationFn: createDepartment,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['catalog'] });
      closeDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const updateMutation = useMutation({
    mutationFn: ({ departmentId, payload }: { departmentId: string; payload: Parameters<typeof updateDepartment>[1] }) => updateDepartment(departmentId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['catalog'] });
      closeDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  function closeDialog() {
    setDialogOpen(false);
    setEditingDepartment(null);
    setForm(emptyForm());
  }

  function openCreateDialog() {
    setError(null);
    setEditingDepartment(null);
    setForm(emptyForm());
    setDialogOpen(true);
  }

  function openEditDialog(department: DepartmentRecord) {
    setError(null);
    setEditingDepartment(department);
    setForm({ code: department.code, name: department.name, is_active: department.is_active });
    setDialogOpen(true);
  }

  async function saveDepartment() {
    setError(null);
    if (editingDepartment) {
      await updateMutation.mutateAsync({ departmentId: editingDepartment.id, payload: form });
      return;
    }
    await createMutation.mutateAsync({ code: form.code, name: form.name });
  }

  return (
    <SectionCard title={catalogText.departments.sectionTitle} subtitle={catalogText.departments.sectionSubtitle}>
      <Stack spacing={2}>
        {error ? <Alert severity='error'>{error}</Alert> : null}
        <Stack direction='row' justifyContent='flex-start'>
          <Button variant='contained' startIcon={<PlaylistAddOutlinedIcon />} onClick={openCreateDialog}>
            {catalogText.departments.create}
          </Button>
        </Stack>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{catalogText.departments.tableCode}</TableCell>
              <TableCell>{catalogText.departments.tableName}</TableCell>
              <TableCell>{catalogText.departments.tableStatus}</TableCell>
              <TableCell>{catalogText.departments.tableAction}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {departments.map((department) => (
              <TableRow key={department.id}>
                <TableCell>{department.code}</TableCell>
                <TableCell>{department.name}</TableCell>
                <TableCell>
                  <Chip label={department.is_active ? catalogText.status.active : catalogText.status.inactive} size='small' color={department.is_active ? 'success' : 'default'} />
                </TableCell>
                <TableCell>
                  <Button startIcon={<EditOutlinedIcon />} onClick={() => openEditDialog(department)}>
                    {commonText.edit}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Stack>

      <Dialog open={dialogOpen} onClose={closeDialog} fullWidth maxWidth='sm'>
        <DialogTitle>{editingDepartment ? catalogText.departments.dialogEdit : catalogText.departments.dialogCreate}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <TextField label={catalogText.departments.code} value={form.code} onChange={(event) => setForm({ ...form, code: event.target.value })} />
            <TextField label={catalogText.departments.name} value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
            {editingDepartment ? (
              <TextField select SelectProps={{ native: true }} label={catalogText.departments.status} value={form.is_active ? 'active' : 'inactive'} onChange={(event) => setForm({ ...form, is_active: event.target.value === 'active' })}>
                <option value='active'>{catalogText.status.active}</option>
                <option value='inactive'>{catalogText.status.inactive}</option>
              </TextField>
            ) : null}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDialog}>{commonText.cancel}</Button>
          <Button variant='contained' onClick={() => void saveDepartment()}>
            {commonText.save}
          </Button>
        </DialogActions>
      </Dialog>
    </SectionCard>
  );
}
