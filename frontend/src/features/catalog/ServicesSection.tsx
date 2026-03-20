import DesignServicesOutlinedIcon from '@mui/icons-material/DesignServicesOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import { Alert, Button, Chip, Dialog, DialogActions, DialogContent, DialogTitle, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { SectionCard } from '../../components/SectionCard';
import { queryClient } from '../../lib/queryClient';
import { useCommonText } from '../../text/common';
import { useCatalogText } from '../../text/catalog';
import { createService, listServices, updateService, type DepartmentRecord, type ServiceRecord } from './api';

function emptyForm(departmentId = '') {
  return { department_id: departmentId, name: '', default_price: '', duration_minutes: '', notes: '', is_active: true };
}

export function ServicesSection({ departments }: { departments: DepartmentRecord[] }) {
  const commonText = useCommonText();
  const catalogText = useCatalogText();
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingService, setEditingService] = useState<ServiceRecord | null>(null);
  const [form, setForm] = useState(emptyForm(departments[0]?.id ?? ''));
  const servicesQuery = useQuery({ queryKey: ['catalog', 'services'], queryFn: listServices });

  const createMutation = useMutation({
    mutationFn: createService,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['catalog'] });
      closeDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const updateMutation = useMutation({
    mutationFn: ({ serviceId, payload }: { serviceId: string; payload: Parameters<typeof updateService>[1] }) => updateService(serviceId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['catalog'] });
      closeDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  function closeDialog() {
    setDialogOpen(false);
    setEditingService(null);
    setForm(emptyForm(departments[0]?.id ?? ''));
  }

  function openCreateDialog() {
    setError(null);
    setEditingService(null);
    setForm(emptyForm(departments[0]?.id ?? ''));
    setDialogOpen(true);
  }

  function openEditDialog(service: ServiceRecord) {
    setError(null);
    setEditingService(service);
    setForm({
      department_id: service.department_id,
      name: service.name,
      default_price: String(service.default_price),
      duration_minutes: service.duration_minutes ? String(service.duration_minutes) : '',
      notes: service.notes ?? '',
      is_active: service.is_active,
    });
    setDialogOpen(true);
  }

  async function saveService() {
    setError(null);
    const payload = {
      department_id: form.department_id,
      name: form.name,
      default_price: Number(form.default_price || 0),
      duration_minutes: form.duration_minutes ? Number(form.duration_minutes) : null,
      notes: form.notes || null,
      is_active: form.is_active,
    };
    if (editingService) {
      await updateMutation.mutateAsync({ serviceId: editingService.id, payload });
      return;
    }
    await createMutation.mutateAsync(payload);
  }

  return (
    <SectionCard title={catalogText.services.sectionTitle} subtitle={catalogText.services.sectionSubtitle}>
      <Stack spacing={2}>
        {error ? <Alert severity='error'>{error}</Alert> : null}
        {!departments.length ? <Alert severity='info'>{catalogText.services.emptyDepartments}</Alert> : null}
        <Stack direction='row' justifyContent='space-between' alignItems='center'>
          <Typography color='text.secondary'>{catalogText.services.smallNote}</Typography>
          <Button variant='contained' startIcon={<DesignServicesOutlinedIcon />} onClick={openCreateDialog} disabled={!departments.length}>
            {catalogText.services.create}
          </Button>
        </Stack>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{catalogText.services.tableName}</TableCell>
              <TableCell>{catalogText.services.tableDepartment}</TableCell>
              <TableCell>{catalogText.services.tablePrice}</TableCell>
              <TableCell>{catalogText.services.tableDuration}</TableCell>
              <TableCell>{catalogText.services.tableStatus}</TableCell>
              <TableCell>{catalogText.services.tableAction}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(servicesQuery.data ?? []).map((service) => (
              <TableRow key={service.id}>
                <TableCell>{service.name}</TableCell>
                <TableCell>{service.department_name}</TableCell>
                <TableCell>{service.default_price}</TableCell>
                <TableCell>{service.duration_minutes ? `${service.duration_minutes} ${catalogText.services.durationSuffix}` : catalogText.services.durationEmpty}</TableCell>
                <TableCell>
                  <Chip label={service.is_active ? catalogText.status.active : catalogText.status.inactive} size='small' color={service.is_active ? 'success' : 'default'} />
                </TableCell>
                <TableCell>
                  <Button startIcon={<EditOutlinedIcon />} onClick={() => openEditDialog(service)}>
                    {commonText.edit}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Stack>

      <Dialog open={dialogOpen} onClose={closeDialog} fullWidth maxWidth='sm'>
        <DialogTitle>{editingService ? catalogText.services.dialogEdit : catalogText.services.dialogCreate}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <TextField select SelectProps={{ native: true }} label={catalogText.services.tableDepartment} value={form.department_id} onChange={(event) => setForm({ ...form, department_id: event.target.value })}>
              {departments.map((department) => (
                <option key={department.id} value={department.id}>
                  {department.name}
                </option>
              ))}
            </TextField>
            <TextField label={catalogText.services.name} value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
            <TextField label={catalogText.services.price} type='number' value={form.default_price} onChange={(event) => setForm({ ...form, default_price: event.target.value })} />
            <TextField label={catalogText.services.duration} type='number' value={form.duration_minutes} onChange={(event) => setForm({ ...form, duration_minutes: event.target.value })} />
            <TextField label={catalogText.services.notes} value={form.notes} multiline minRows={3} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
            {editingService ? (
              <TextField select SelectProps={{ native: true }} label={catalogText.departments.status} value={form.is_active ? 'active' : 'inactive'} onChange={(event) => setForm({ ...form, is_active: event.target.value === 'active' })}>
                <option value='active'>{catalogText.status.active}</option>
                <option value='inactive'>{catalogText.status.inactive}</option>
              </TextField>
            ) : null}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDialog}>{commonText.cancel}</Button>
          <Button variant='contained' onClick={() => void saveService()}>
            {commonText.save}
          </Button>
        </DialogActions>
      </Dialog>
    </SectionCard>
  );
}
