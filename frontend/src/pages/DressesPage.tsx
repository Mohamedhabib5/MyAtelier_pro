import CheckroomOutlinedIcon from '@mui/icons-material/CheckroomOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import { Alert, Box, Button, Chip, Dialog, DialogActions, DialogContent, DialogTitle, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { SectionCard } from '../components/SectionCard';
import { createDress, listDresses, updateDress, type DressRecord } from '../features/dresses/api';
import { useLanguage } from '../features/language/LanguageProvider';
import { queryClient } from '../lib/queryClient';
import { useCommonText } from '../text/common';
import { dressStatusLabel, useDressesText } from '../text/dresses';

function emptyForm() {
  return { code: '', dress_type: '', purchase_date: '', status: 'available', description: '', image_path: '', is_active: true };
}

export function DressesPage() {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const dressesText = useDressesText();
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingDress, setEditingDress] = useState<DressRecord | null>(null);
  const [form, setForm] = useState(emptyForm());
  const dressesQuery = useQuery({ queryKey: ['dresses'], queryFn: listDresses });

  const createMutation = useMutation({
    mutationFn: createDress,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['dresses'] });
      closeDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const updateMutation = useMutation({
    mutationFn: ({ dressId, payload }: { dressId: string; payload: Parameters<typeof updateDress>[1] }) => updateDress(dressId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['dresses'] });
      closeDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  function closeDialog() {
    setDialogOpen(false);
    setEditingDress(null);
    setForm(emptyForm());
  }

  function openCreateDialog() {
    setError(null);
    setEditingDress(null);
    setForm(emptyForm());
    setDialogOpen(true);
  }

  function openEditDialog(dress: DressRecord) {
    setError(null);
    setEditingDress(dress);
    setForm({
      code: dress.code,
      dress_type: dress.dress_type,
      purchase_date: dress.purchase_date ?? '',
      status: dress.status,
      description: dress.description,
      image_path: dress.image_path ?? '',
      is_active: dress.is_active,
    });
    setDialogOpen(true);
  }

  async function saveDress() {
    setError(null);
    const payload = {
      code: form.code,
      dress_type: form.dress_type,
      purchase_date: form.purchase_date || null,
      status: form.status,
      description: form.description,
      image_path: form.image_path || null,
      is_active: form.is_active,
    };
    if (editingDress) {
      await updateMutation.mutateAsync({ dressId: editingDress.id, payload });
      return;
    }
    await createMutation.mutateAsync(payload);
  }

  return (
    <Stack spacing={3}>
      <Stack direction='row' justifyContent='space-between' alignItems='center'>
        <Box>
          <Typography variant='h4'>{dressesText.page.title}</Typography>
          <Typography color='text.secondary'>{dressesText.page.description}</Typography>
        </Box>
        <Button variant='contained' startIcon={<CheckroomOutlinedIcon />} onClick={openCreateDialog}>
          {dressesText.page.create}
        </Button>
      </Stack>

      {error ? <Alert severity='error'>{error}</Alert> : null}

      <SectionCard title={dressesText.page.listTitle} subtitle={dressesText.page.listSubtitle}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{dressesText.table.code}</TableCell>
              <TableCell>{dressesText.table.type}</TableCell>
              <TableCell>{dressesText.table.status}</TableCell>
              <TableCell>{dressesText.table.purchaseDate}</TableCell>
              <TableCell>{dressesText.table.imageRef}</TableCell>
              <TableCell>{dressesText.table.action}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(dressesQuery.data ?? []).map((dress) => (
              <TableRow key={dress.id}>
                <TableCell>{dress.code}</TableCell>
                <TableCell>{dress.dress_type}</TableCell>
                <TableCell>
                  <Chip label={dressStatusLabel(language, dress.status)} size='small' color={dress.status === 'available' ? 'success' : dress.status === 'reserved' ? 'warning' : 'default'} />
                </TableCell>
                <TableCell>{dress.purchase_date ?? '—'}</TableCell>
                <TableCell>{dress.image_path ?? '—'}</TableCell>
                <TableCell>
                  <Button startIcon={<EditOutlinedIcon />} onClick={() => openEditDialog(dress)}>
                    {commonText.edit}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </SectionCard>

      <Dialog open={dialogOpen} onClose={closeDialog} fullWidth maxWidth='sm'>
        <DialogTitle>{editingDress ? dressesText.dialog.edit : dressesText.dialog.create}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <TextField label={dressesText.dialog.code} value={form.code} onChange={(event) => setForm({ ...form, code: event.target.value })} />
            <TextField label={dressesText.dialog.type} value={form.dress_type} onChange={(event) => setForm({ ...form, dress_type: event.target.value })} />
            <TextField label={dressesText.dialog.purchaseDate} type='date' InputLabelProps={{ shrink: true }} value={form.purchase_date} onChange={(event) => setForm({ ...form, purchase_date: event.target.value })} />
            <TextField select SelectProps={{ native: true }} label={dressesText.dialog.status} value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })}>
              <option value='available'>{dressStatusLabel(language, 'available')}</option>
              <option value='reserved'>{dressStatusLabel(language, 'reserved')}</option>
              <option value='maintenance'>{dressStatusLabel(language, 'maintenance')}</option>
            </TextField>
            <TextField label={dressesText.dialog.description} value={form.description} multiline minRows={3} onChange={(event) => setForm({ ...form, description: event.target.value })} />
            <TextField label={dressesText.dialog.imageRef} value={form.image_path} onChange={(event) => setForm({ ...form, image_path: event.target.value })} helperText={dressesText.dialog.imageHint} />
            {editingDress ? (
              <TextField select SelectProps={{ native: true }} label={dressesText.dialog.operationalStatus} value={form.is_active ? 'active' : 'inactive'} onChange={(event) => setForm({ ...form, is_active: event.target.value === 'active' })}>
                <option value='active'>{dressesText.status.active}</option>
                <option value='inactive'>{dressesText.status.inactive}</option>
              </TextField>
            ) : null}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDialog}>{commonText.cancel}</Button>
          <Button variant='contained' onClick={() => void saveDress()}>
            {commonText.save}
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
