import DesignServicesOutlinedIcon from '@mui/icons-material/DesignServicesOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import { Alert, Button, Chip, Stack, TextField, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import { DestructiveDeleteDialog } from '../../components/DestructiveDeleteDialog';
import { LifecycleReasonDialog } from '../../components/LifecycleReasonDialog';
import { AppDataTable } from '../../components/data-table/AppDataTable';
import { SectionCard } from '../../components/SectionCard';
import { useLanguage } from '../language/LanguageProvider';
import { queryClient } from '../../lib/queryClient';
import { useCommonText } from '../../text/common';
import { useCatalogText } from '../../text/catalog';
import { archiveService, createService, listServices, restoreService, updateService, type DepartmentRecord, type ServiceRecord } from './api';
import { ServiceFormDialog, type ServiceFormState } from './ServiceFormDialog';

function emptyForm(departmentId = '') {
  return { department_id: departmentId, name: '', default_price: '', duration_minutes: '', notes: '', is_active: true, display_order: 0 } satisfies ServiceFormState;
}

export function ServicesSection({ departments }: { departments: DepartmentRecord[] }) {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const catalogText = useCatalogText();
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingService, setEditingService] = useState<ServiceRecord | null>(null);
  const [form, setForm] = useState<ServiceFormState>(emptyForm(departments[0]?.id ?? ''));
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [departmentFilter, setDepartmentFilter] = useState('all');
  const [lifecycleTarget, setLifecycleTarget] = useState<ServiceRecord | null>(null);
  const [lifecycleMode, setLifecycleMode] = useState<'archive' | 'restore'>('archive');
  const [lifecycleReason, setLifecycleReason] = useState('');
  const [deleteTarget, setDeleteTarget] = useState<ServiceRecord | null>(null);
  const servicesQuery = useQuery({ queryKey: ['catalog', 'services', statusFilter], queryFn: () => listServices(statusFilter) });

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
  const lifecycleMutation = useMutation({
    mutationFn: ({ service, archive, reason }: { service: ServiceRecord; archive: boolean; reason?: string }) =>
      archive ? archiveService(service.id, reason) : restoreService(service.id, reason),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['catalog'] });
      closeLifecycleDialog();
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
      display_order: service.display_order,
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
      display_order: form.display_order,
    };
    if (editingService) {
      await updateMutation.mutateAsync({ serviceId: editingService.id, payload });
      return;
    }
    await createMutation.mutateAsync(payload);
  }

  function openLifecycleDialog(service: ServiceRecord, archive: boolean) {
    setError(null);
    setLifecycleTarget(service);
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
      service: lifecycleTarget,
      archive: lifecycleMode === 'archive',
      reason: lifecycleReason || undefined,
    });
  }

  const rows = useMemo(
    () =>
      (servicesQuery.data ?? []).filter((service) => {
        const matchesDepartment = departmentFilter === 'all' ? true : service.department_id === departmentFilter;
        return matchesDepartment;
      }),
    [departmentFilter, servicesQuery.data],
  );

  const labels =
    language === 'ar'
      ? { search: 'بحث', searchPlaceholder: 'ابحث باسم الخدمة أو القسم أو الملاحظات', filters: 'الفلاتر', columns: 'الأعمدة', export: 'تصدير', reset: 'إعادة الضبط', noRows: 'لا توجد بيانات مطابقة' }
      : { search: 'Search', searchPlaceholder: 'Search by service, department, or notes', filters: 'Filters', columns: 'Columns', export: 'Export', reset: 'Reset', noRows: 'No matching rows' };

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
        <AppDataTable
          tableKey='services-list'
          rows={rows}
          columns={[
            { key: 'name', header: catalogText.services.tableName, searchValue: (row) => row.name, render: (row) => row.name },
            { key: 'department', header: catalogText.services.tableDepartment, searchValue: (row) => row.department_name, render: (row) => row.department_name },
            { key: 'display_order', header: catalogText.services.displayOrder, render: (row) => row.display_order },
            { key: 'price', header: catalogText.services.tablePrice, sortValue: (row) => row.default_price, exportValue: (row) => row.default_price, render: (row) => row.default_price },
            {
              key: 'duration',
              header: catalogText.services.tableDuration,
              sortValue: (row) => row.duration_minutes ?? 0,
              searchValue: (row) => (row.duration_minutes ? String(row.duration_minutes) : ''),
              render: (row) => (row.duration_minutes ? `${row.duration_minutes} ${catalogText.services.durationSuffix}` : catalogText.services.durationEmpty),
            },
            {
              key: 'status',
              header: catalogText.services.tableStatus,
              searchValue: (row) => (row.is_active ? catalogText.status.active : catalogText.status.inactive),
              render: (row) => <Chip label={row.is_active ? catalogText.status.active : catalogText.status.inactive} size='small' color={row.is_active ? 'success' : 'default'} />,
            },
            {
              key: 'action',
              header: catalogText.services.tableAction,
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
          searchFields={[(row) => row.name, (row) => row.department_name, (row) => row.notes ?? '']}
          filterContent={
            <Stack spacing={2}>
              <TextField select SelectProps={{ native: true }} fullWidth label={catalogText.services.tableDepartment} value={departmentFilter} onChange={(event) => setDepartmentFilter(event.target.value)}>
                <option value='all'>{language === 'ar' ? 'كل الأقسام' : 'All departments'}</option>
                {departments.map((department) => (
                  <option key={department.id} value={department.id}>
                    {department.name}
                  </option>
                ))}
              </TextField>
              <TextField select SelectProps={{ native: true }} fullWidth label={catalogText.services.tableStatus} value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as typeof statusFilter)}>
                <option value='all'>{language === 'ar' ? 'الكل' : 'All'}</option>
                <option value='active'>{catalogText.status.active}</option>
                <option value='inactive'>{catalogText.status.inactive}</option>
              </TextField>
            </Stack>
          }
        />
      </Stack>

      <ServiceFormDialog open={dialogOpen} editing={Boolean(editingService)} form={form} departments={departments} onChange={setForm} onClose={closeDialog} onSave={() => void saveService()} />

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
        entityType='service'
        entityId={deleteTarget?.id ?? null}
        entityLabel={deleteTarget?.name ?? ''}
        onClose={closeDeleteDialog}
        onDeleted={() => void queryClient.invalidateQueries({ queryKey: ['catalog'] })}
        onError={(message) => setError(message)}
      />
    </SectionCard>
  );
}
