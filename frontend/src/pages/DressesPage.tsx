import CheckroomOutlinedIcon from '@mui/icons-material/CheckroomOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import { Alert, Box, Button, Chip, Stack, TextField, Typography, Dialog, DialogContent, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import { DestructiveDeleteDialog } from '../components/DestructiveDeleteDialog';
import { LifecycleReasonDialog } from '../components/LifecycleReasonDialog';
import { AppDataTable } from '../components/data-table/AppDataTable';
import { SectionCard } from '../components/SectionCard';
import { archiveDress, createDress, listDresses, restoreDress, updateDress, type DressRecord } from '../features/dresses/api';
import { DressFormDialog, type DressFormState } from '../features/dresses/DressFormDialog';
import { useLanguage } from '../features/language/LanguageProvider';
import { queryClient } from '../lib/queryClient';
import { EMPTY_VALUE, useCommonText } from '../text/common';
import { dressStatusLabel, useDressesText } from '../text/dresses';
function emptyForm() {
  return { code: '', dress_type: '', purchase_date: '', status: 'available', description: '', image_path: '', is_active: true } satisfies DressFormState;
}
export function DressesPage() {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const dressesText = useDressesText();
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingDress, setEditingDress] = useState<DressRecord | null>(null);
  const [form, setForm] = useState<DressFormState>(emptyForm());
  const [statusFilter, setStatusFilter] = useState<'all' | 'available' | 'reserved' | 'with_customer' | 'maintenance'>('all');
  const [activeFilter, setActiveFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [lifecycleTarget, setLifecycleTarget] = useState<DressRecord | null>(null);
  const [lifecycleMode, setLifecycleMode] = useState<'archive' | 'restore'>('archive');
  const [lifecycleReason, setLifecycleReason] = useState('');
  const [deleteTarget, setDeleteTarget] = useState<DressRecord | null>(null);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const dressesQuery = useQuery({ queryKey: ['dresses', activeFilter], queryFn: () => listDresses(activeFilter) });

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
  const lifecycleMutation = useMutation({
    mutationFn: ({ dress, archive, reason }: { dress: DressRecord; archive: boolean; reason?: string }) =>
      archive ? archiveDress(dress.id, reason) : restoreDress(dress.id, reason),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['dresses'] });
      closeLifecycleDialog();
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
      description: dress.description ?? '',
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

  function openLifecycleDialog(dress: DressRecord, archive: boolean) {
    setError(null);
    setLifecycleTarget(dress);
    setLifecycleMode(archive ? 'archive' : 'restore');
    setLifecycleReason('');
  }

  function closeLifecycleDialog() {
    setLifecycleTarget(null);
    setLifecycleReason('');
  }

  async function confirmLifecycle() {
    if (!lifecycleTarget) return;
    await lifecycleMutation.mutateAsync({
      dress: lifecycleTarget,
      archive: lifecycleMode === 'archive',
      reason: lifecycleReason || undefined,
    });
  }

  function closeDeleteDialog() {
    setDeleteTarget(null);
  }

  const rows = useMemo(
    () => (dressesQuery.data ?? []).filter((dress) => (statusFilter === 'all' ? true : dress.status === statusFilter)),
    [dressesQuery.data, statusFilter],
  );

  const labels =
    language === 'ar'
      ? { search: 'بحث', searchPlaceholder: 'ابحث بالكود أو النوع أو الوصف', filters: 'الفلاتر', columns: 'الأعمدة', export: 'تصدير', reset: 'إعادة الضبط', noRows: 'لا توجد بيانات مطابقة' }
      : { search: 'Search', searchPlaceholder: 'Search by code, type, or description', filters: 'Filters', columns: 'Columns', export: 'Export', reset: 'Reset', noRows: 'No matching rows' };

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
        <AppDataTable
          tableKey='dresses-list'
          rows={rows}
          columns={[
            { key: 'code', header: dressesText.table.code, searchValue: (row) => row.code, render: (row) => row.code },
            { key: 'type', header: dressesText.table.type, searchValue: (row) => row.dress_type, render: (row) => row.dress_type },
            { key: 'description', header: dressesText.table.description, searchValue: (row) => row.description ?? '', render: (row) => row.description ?? EMPTY_VALUE },
            {
              key: 'status',
              header: dressesText.table.status,
              searchValue: (row) => dressStatusLabel(language, row.status),
              render: (row) => <Chip label={dressStatusLabel(language, row.status)} size='small' color={row.status === 'available' ? 'success' : row.status === 'reserved' ? 'warning' : row.status === 'with_customer' ? 'info' : 'default'} />,
            },
            {
              key: 'operational_status',
              header: language === 'ar' ? 'الحالة التشغيلية' : 'Operational status',
              searchValue: (row) => (row.is_active ? dressesText.status.active : dressesText.status.inactive),
              render: (row) => <Chip label={row.is_active ? dressesText.status.active : dressesText.status.inactive} size='small' color={row.is_active ? 'success' : 'default'} />,
            },
            { key: 'purchase_date', header: dressesText.table.purchaseDate, searchValue: (row) => row.purchase_date ?? '', render: (row) => row.purchase_date ?? EMPTY_VALUE },
            {
              key: 'image_path',
              header: dressesText.table.imageRef,
              searchValue: (row) => row.image_path ?? '',
              render: (row) => {
                if (!row.image_path) return EMPTY_VALUE;
                // Temporary fix: point directly to the backend port (8000) for development
                const backendUrl = `${window.location.protocol}//${window.location.hostname}:8000`;
                const imageUrl = row.image_path.startsWith('http') ? row.image_path : `${backendUrl}/attachments/${row.image_path}`;
                return (
                  <Box
                    component='img'
                    src={imageUrl}
                    alt={row.code}
                    onClick={() => setPreviewImage(imageUrl)}
                    sx={{
                      width: 48,
                      height: 48,
                      objectFit: 'cover',
                      borderRadius: 1.5,
                      border: '1px solid',
                      borderColor: 'divider',
                      transition: 'all 0.2s ease-in-out',
                      cursor: 'zoom-in',
                      '&:hover': {
                        transform: 'scale(1.1)',
                        zIndex: 10,
                        boxShadow: 2,
                      },
                    }}
                  />
                );
              },
            },
            {
              key: 'action',
              header: dressesText.table.action,
              render: (row) => (
                <Stack direction='row' spacing={1}>
                  <Button size='small' startIcon={<EditOutlinedIcon />} onClick={() => openEditDialog(row)}>
                    {commonText.edit}
                  </Button>
                  <Button size='small' color={row.is_active ? 'warning' : 'success'} onClick={() => openLifecycleDialog(row, row.is_active)}>
                    {row.is_active ? (language === 'ar' ? 'أرشفة' : 'Archive') : language === 'ar' ? 'استعادة' : 'Restore'}
                  </Button>
                  <Button size='small' color='error' startIcon={<DeleteOutlineOutlinedIcon />} onClick={() => setDeleteTarget(row)}>
                    {language === 'ar' ? 'حذف تصحيحي' : 'Corrective delete'}
                  </Button>
                </Stack>
              ),
            },
          ]}
          searchLabel={labels.search}
          searchPlaceholder={labels.searchPlaceholder}
          resetColumnsLabel={labels.reset}
          noRowsLabel={labels.noRows}
          filtersLabel={labels.filters}
          columnsLabel={labels.columns}
          exportLabel={labels.export}
          rowsPerPageLabel={language === 'ar' ? 'عدد الصفوف' : 'Rows per page'}
          closeLabel={language === 'ar' ? 'إغلاق' : 'Close'}
          searchFields={[(row) => row.code, (row) => row.dress_type, (row) => row.description ?? '', (row) => row.image_path ?? '']}
          filterContent={
            <Stack spacing={2}>
              <TextField select SelectProps={{ native: true }} fullWidth label={language === 'ar' ? 'الحالة التشغيلية' : 'Operational status'} value={activeFilter} onChange={(event) => setActiveFilter(event.target.value as typeof activeFilter)}>
                <option value='all'>{language === 'ar' ? 'الكل' : 'All'}</option>
                <option value='active'>{dressesText.status.active}</option>
                <option value='inactive'>{dressesText.status.inactive}</option>
              </TextField>
              <TextField select SelectProps={{ native: true }} fullWidth label={dressesText.table.status} value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as typeof statusFilter)}>
                <option value='all'>{language === 'ar' ? 'الكل' : 'All'}</option>
                <option value='available'>{dressStatusLabel(language, 'available')}</option>
                <option value='reserved'>{dressStatusLabel(language, 'reserved')}</option>
                <option value='with_customer'>{dressStatusLabel(language, 'with_customer')}</option>
                <option value='maintenance'>{dressStatusLabel(language, 'maintenance')}</option>
              </TextField>
            </Stack>
          }
        />
      </SectionCard>

      <DressFormDialog open={dialogOpen} editing={Boolean(editingDress)} form={form} onChange={setForm} onClose={closeDialog} onSave={() => void saveDress()} />

      <LifecycleReasonDialog
        open={Boolean(lifecycleTarget)}
        mode={lifecycleMode}
        entityLabel={lifecycleTarget?.code ?? ''}
        reason={lifecycleReason}
        language={language}
        onReasonChange={setLifecycleReason}
        onCancel={closeLifecycleDialog}
        onConfirm={() => void confirmLifecycle()}
        loading={lifecycleMutation.isPending}
      />
      <DestructiveDeleteDialog
        open={Boolean(deleteTarget)}
        entityType='dress'
        entityId={deleteTarget?.id ?? null}
        entityLabel={deleteTarget?.code ?? ''}
        onClose={closeDeleteDialog}
        onDeleted={() => {
          void queryClient.invalidateQueries({ queryKey: ['dresses'] });
        }}
        onError={(message) => setError(message)}
      />

      <Dialog open={Boolean(previewImage)} onClose={() => setPreviewImage(null)} maxWidth='lg'>
        <DialogContent sx={{ p: 0, position: 'relative', bgcolor: 'black', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <IconButton onClick={() => setPreviewImage(null)} sx={{ position: 'absolute', top: 8, right: 8, color: 'white', bgcolor: 'rgba(0,0,0,0.5)', '&:hover': { bgcolor: 'rgba(0,0,0,0.7)' } }}>
            <CloseIcon />
          </IconButton>
          {previewImage && (
            <Box
              component='img'
              src={previewImage}
              alt='Preview'
              sx={{
                maxWidth: '100%',
                maxHeight: '90vh',
                display: 'block',
                boxShadow: 24,
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Stack>
  );
}
