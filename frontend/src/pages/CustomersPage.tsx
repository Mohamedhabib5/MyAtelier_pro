import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import PersonAddOutlinedIcon from '@mui/icons-material/PersonAddOutlined';
import { Alert, Box, Button, Chip, Dialog, DialogActions, DialogContent, DialogTitle, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { SectionCard } from '../components/SectionCard';
import { createCustomer, listCustomers, updateCustomer, type CustomerRecord } from '../features/customers/api';
import { queryClient } from '../lib/queryClient';
import { useCommonText } from '../text/common';
import { useCustomersText } from '../text/customers';

function emptyForm() {
  return { full_name: '', phone: '', email: '', address: '', notes: '', is_active: true };
}

export function CustomersPage() {
  const commonText = useCommonText();
  const customersText = useCustomersText();
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<CustomerRecord | null>(null);
  const [form, setForm] = useState(emptyForm());
  const customersQuery = useQuery({ queryKey: ['customers'], queryFn: listCustomers });

  const createMutation = useMutation({
    mutationFn: createCustomer,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['customers'] });
      closeDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const updateMutation = useMutation({
    mutationFn: ({ customerId, payload }: { customerId: string; payload: Parameters<typeof updateCustomer>[1] }) => updateCustomer(customerId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['customers'] });
      closeDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  function closeDialog() {
    setDialogOpen(false);
    setEditingCustomer(null);
    setForm(emptyForm());
  }

  function openCreateDialog() {
    setError(null);
    setEditingCustomer(null);
    setForm(emptyForm());
    setDialogOpen(true);
  }

  function openEditDialog(customer: CustomerRecord) {
    setError(null);
    setEditingCustomer(customer);
    setForm({
      full_name: customer.full_name,
      phone: customer.phone,
      email: customer.email ?? '',
      address: customer.address ?? '',
      notes: customer.notes ?? '',
      is_active: customer.is_active,
    });
    setDialogOpen(true);
  }

  async function saveCustomer() {
    setError(null);
    if (editingCustomer) {
      await updateMutation.mutateAsync({
        customerId: editingCustomer.id,
        payload: { ...form, email: form.email || null, address: form.address || null, notes: form.notes || null },
      });
      return;
    }
    await createMutation.mutateAsync({
      full_name: form.full_name,
      phone: form.phone,
      email: form.email || null,
      address: form.address || null,
      notes: form.notes || null,
    });
  }

  return (
    <Stack spacing={3}>
      <Stack direction='row' justifyContent='space-between' alignItems='center'>
        <Box>
          <Typography variant='h4'>{customersText.page.title}</Typography>
          <Typography color='text.secondary'>{customersText.page.description}</Typography>
        </Box>
        <Button variant='contained' startIcon={<PersonAddOutlinedIcon />} onClick={openCreateDialog}>
          {customersText.page.create}
        </Button>
      </Stack>

      {error ? <Alert severity='error'>{error}</Alert> : null}

      <SectionCard title={customersText.page.listTitle} subtitle={customersText.page.listSubtitle}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{customersText.table.fullName}</TableCell>
              <TableCell>{customersText.table.phone}</TableCell>
              <TableCell>{customersText.table.email}</TableCell>
              <TableCell>{customersText.table.status}</TableCell>
              <TableCell>{customersText.table.action}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(customersQuery.data ?? []).map((customer) => (
              <TableRow key={customer.id}>
                <TableCell>{customer.full_name}</TableCell>
                <TableCell>{customer.phone}</TableCell>
                <TableCell>{customer.email ?? '—'}</TableCell>
                <TableCell>
                  <Chip label={customer.is_active ? customersText.status.active : customersText.status.inactive} size='small' color={customer.is_active ? 'success' : 'default'} />
                </TableCell>
                <TableCell>
                  <Button startIcon={<EditOutlinedIcon />} onClick={() => openEditDialog(customer)}>
                    {commonText.edit}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </SectionCard>

      <Dialog open={dialogOpen} onClose={closeDialog} fullWidth maxWidth='sm'>
        <DialogTitle>{editingCustomer ? customersText.dialog.edit : customersText.dialog.create}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <TextField label={customersText.dialog.fullName} value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} />
            <TextField label={customersText.dialog.phone} value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} />
            <TextField label={customersText.dialog.email} value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} />
            <TextField label={customersText.dialog.address} value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} />
            <TextField label={customersText.dialog.notes} value={form.notes} multiline minRows={3} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
            {editingCustomer ? (
              <TextField select SelectProps={{ native: true }} label={customersText.dialog.status} value={form.is_active ? 'active' : 'inactive'} onChange={(event) => setForm({ ...form, is_active: event.target.value === 'active' })}>
                <option value='active'>{customersText.status.active}</option>
                <option value='inactive'>{customersText.status.inactive}</option>
              </TextField>
            ) : null}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDialog}>{commonText.cancel}</Button>
          <Button variant='contained' onClick={() => void saveCustomer()}>
            {commonText.save}
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
