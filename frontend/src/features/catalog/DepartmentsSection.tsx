import CheckroomIcon from '@mui/icons-material/Checkroom';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import PlaylistAddOutlinedIcon from '@mui/icons-material/PlaylistAddOutlined';
import { Alert, Box, Button, Checkbox, Chip, FormControlLabel, Stack, TextField, Tooltip, Typography } from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import { StableNumericField } from '../../components/inputs/StableNumericField';
import { AppDialogShell } from '../../components/AppDialogShell';
import { DestructiveDeleteDialog } from '../../components/DestructiveDeleteDialog';
import { LifecycleReasonDialog } from '../../components/LifecycleReasonDialog';
import { AppDataTable } from '../../components/data-table/AppDataTable';
import { SectionCard } from '../../components/SectionCard';
import { useLanguage } from '../language/LanguageProvider';
import { queryClient } from '../../lib/queryClient';
import { useCommonText } from '../../text/common';
import { useCatalogText } from '../../text/catalog';
import { archiveDepartment, createDepartment, restoreDepartment, updateDepartment, type DepartmentRecord } from './api';

function emptyForm() {
  return { code: '', name: '', is_active: true, display_order: 0 };
}

export function DepartmentsSection({ departments }: { departments: DepartmentRecord[] }) {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const catalogText = useCatalogText();
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingDepartment, setEditingDepartment] = useState<DepartmentRecord | null>(null);
  const [form, setForm] = useState(emptyForm());
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [lifecycleTarget, setLifecycleTarget] = useState<DepartmentRecord | null>(null);
  const [lifecycleMode, setLifecycleMode] = useState<'archive' | 'restore'>('archive');
  const [lifecycleReason, setLifecycleReason] = useState('');
  const [deleteTarget, setDeleteTarget] = useState<DepartmentRecord | null>(null);

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
  const lifecycleMutation = useMutation({
    mutationFn: ({ department, archive, reason }: { department: DepartmentRecord; archive: boolean; reason?: string }) =>
      archive ? archiveDepartment(department.id, reason) : restoreDepartment(department.id, reason),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['catalog'] });
      closeLifecycleDialog();
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
    setForm({ 
      code: department.code, 
      name: department.name, 
      is_active: department.is_active,
      display_order: department.display_order,
    });
    setDialogOpen(true);
  }

  async function saveDepartment() {
    setError(null);
    if (editingDepartment) {
      await updateMutation.mutateAsync({ departmentId: editingDepartment.id, payload: form });
      return;
    }
    await createMutation.mutateAsync(form);
  }

  function openLifecycleDialog(department: DepartmentRecord, archive: boolean) {
    setError(null);
    setLifecycleTarget(department);
    setLifecycleMode(archive ? 'archive' : 'restore');
    setLifecycleReason('');
  }

  function closeLifecycleDialog() {
    setLifecycleTarget(null);
    setLifecycleReason('');
  }

  function closeDeleteDialog() {
    setDeleteTarget(null);
  }

  async function confirmLifecycle() {
    if (!lifecycleTarget) return;
    await lifecycleMutation.mutateAsync({
      department: lifecycleTarget,
      archive: lifecycleMode === 'archive',
      reason: lifecycleReason || undefined,
    });
  }

  const rows = useMemo(
    () => departments.filter((department) => (statusFilter === 'all' ? true : statusFilter === 'active' ? department.is_active : !department.is_active)),
    [departments, statusFilter],
  );

  const labels =
    language === 'ar'
      ? { search: 'بحث', searchPlaceholder: 'ابحث بالكود أو الاسم', filters: 'الفلاتر', columns: 'الأعمدة', export: 'تصدير', reset: 'إعادة الضبط', noRows: 'لا توجد بيانات مطابقة' }
      : { search: 'Search', searchPlaceholder: 'Search by code or name', filters: 'Filters', columns: 'Columns', export: 'Export', reset: 'Reset', noRows: 'No matching rows' };

  return (
    <SectionCard title={catalogText.departments.sectionTitle} subtitle={catalogText.departments.sectionSubtitle}>
      <Stack spacing={2}>
        {error ? <Alert severity='error'>{error}</Alert> : null}
        <Stack direction='row' justifyContent='flex-start'>
          <Button variant='contained' startIcon={<PlaylistAddOutlinedIcon />} onClick={openCreateDialog}>
            {catalogText.departments.create}
          </Button>
        </Stack>
        <AppDataTable
          tableKey='departments-list'
          rows={rows}
          columns={[
            { key: 'code', header: catalogText.departments.tableCode, searchValue: (row) => row.code, render: (row) => row.code },
            { 
              key: 'name', 
              header: catalogText.departments.tableName, 
              searchValue: (row) => row.name, 
              render: (row) => (
                <Stack direction='row' alignItems='center' spacing={1}>
                  <Typography variant='body2'>{row.name}</Typography>
                  {row.is_dress_department && (
                    <Tooltip title={catalogText.departments.isDressDepartment}>
                      <CheckroomIcon fontSize='small' color='primary' />
                    </Tooltip>
                  )}
                </Stack>
              )
            },
            { key: 'display_order', header: catalogText.departments.displayOrder, render: (row) => row.display_order },
            {
              key: 'status',
              header: catalogText.departments.tableStatus,
              searchValue: (row) => (row.is_active ? catalogText.status.active : catalogText.status.inactive),
              render: (row) => <Chip label={row.is_active ? catalogText.status.active : catalogText.status.inactive} size='small' color={row.is_active ? 'success' : 'default'} />,
            },
            {
              key: 'action',
              header: catalogText.departments.tableAction,
              render: (row) => (
                <Stack direction='row' spacing={1}>
                  <Button size='small' startIcon={<EditOutlinedIcon />} onClick={() => openEditDialog(row)}>
                    {commonText.edit}
                  </Button>
                  <Button size='small' color={row.is_active ? 'warning' : 'success'} onClick={() => openLifecycleDialog(row, row.is_active)}>
                    {row.is_active ? (language === 'ar' ? 'أرشفة' : 'Archive') : language === 'ar' ? 'استعادة' : 'Restore'}
                  </Button>
                  <Button size='small' color='error' onClick={() => setDeleteTarget(row)}>
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
          searchFields={[(row) => row.code, (row) => row.name]}
          filterContent={
            <TextField select SelectProps={{ native: true }} fullWidth label={catalogText.departments.tableStatus} value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as typeof statusFilter)}>
              <option value='all'>{language === 'ar' ? 'الكل' : 'All'}</option>
              <option value='active'>{catalogText.status.active}</option>
              <option value='inactive'>{catalogText.status.inactive}</option>
            </TextField>
          }
        />
      </Stack>

      <AppDialogShell
        open={dialogOpen}
        onClose={closeDialog}
        title={editingDepartment ? catalogText.departments.dialogEdit : catalogText.departments.dialogCreate}
        actions={
          <>
            <Button onClick={closeDialog}>{commonText.cancel}</Button>
            <Button variant='contained' onClick={() => void saveDepartment()}>
              {commonText.save}
            </Button>
          </>
        }
      >
        <Stack spacing={2}>
          <TextField label={catalogText.departments.code} value={form.code} onChange={(event) => setForm({ ...form, code: event.target.value })} />
          <TextField label={catalogText.departments.name} value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
          <StableNumericField 
            label={catalogText.departments.displayOrder} 
            value={String(form.display_order)} 
            onValueChange={(value) => setForm({ ...form, display_order: parseInt(value) || 0 })} 
            allowDecimal={false}
          />
          {editingDepartment ? (
            <TextField select SelectProps={{ native: true }} label={catalogText.departments.status} value={form.is_active ? 'active' : 'inactive'} onChange={(event) => setForm({ ...form, is_active: event.target.value === 'active' })}>
              <option value='active'>{catalogText.status.active}</option>
              <option value='inactive'>{catalogText.status.inactive}</option>
            </TextField>
          ) : null}
        </Stack>
      </AppDialogShell>

      <LifecycleReasonDialog
        open={Boolean(lifecycleTarget)}
        mode={lifecycleMode}
        entityLabel={lifecycleTarget?.name ?? ''}
        reason={lifecycleReason}
        language={language}
        onReasonChange={setLifecycleReason}
        onCancel={closeLifecycleDialog}
        onConfirm={() => void confirmLifecycle()}
        loading={lifecycleMutation.isPending}
      />
      <DestructiveDeleteDialog
        open={Boolean(deleteTarget)}
        entityType='department'
        entityId={deleteTarget?.id ?? null}
        entityLabel={deleteTarget?.name ?? ''}
        onClose={closeDeleteDialog}
        onDeleted={() => {
          void queryClient.invalidateQueries({ queryKey: ['catalog'] });
        }}
        onError={(message) => setError(message)}
      />
    </SectionCard>
  );
}
