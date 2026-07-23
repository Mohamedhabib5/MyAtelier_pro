import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import PersonAddOutlinedIcon from '@mui/icons-material/PersonAddOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import ArchiveOutlinedIcon from '@mui/icons-material/ArchiveOutlined';
import UnarchiveOutlinedIcon from '@mui/icons-material/UnarchiveOutlined';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import { Alert, Box, Button, Chip, IconButton, Stack, TextField, Tooltip, Typography } from '@mui/material';
import type { ColDef } from 'ag-grid-community';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState, useCallback } from 'react';

import { AppAgGrid } from '../components/ag-grid';
import { DestructiveDeleteDialog } from '../components/DestructiveDeleteDialog';
import { LifecycleReasonDialog } from '../components/LifecycleReasonDialog';
import { SectionCard } from '../components/SectionCard';
import { archiveCustomer, createCustomer, listCustomers, restoreCustomer, updateCustomer, type CustomerRecord } from '../features/customers/api';
import { CustomerFormDialog, type CustomerFormState } from '../features/customers/CustomerFormDialog';
import { CustomerStatementDialog } from '../features/customers/CustomerStatementDialog';
import { useLanguage } from '../features/language/LanguageProvider';
import { queryClient } from '../lib/queryClient';
import { EMPTY_VALUE, useCommonText } from '../text/common';
import { getCustomersExcelUrl, getCustomersExportUrl } from '../features/exports/api';
import { downloadFile } from '../lib/api';
import { useCustomersText } from '../text/customers';
import { getLocalDateStr } from '../lib/dates';

function emptyForm() {
  const today = getLocalDateStr();
  return { full_name: '', registration_date: today, groom_name: '', bride_name: '', phone: '', phone_2: '', email: '', address: '', notes: '', is_active: true } satisfies CustomerFormState;
}

export function CustomersPage() {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const customersText = useCustomersText();
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<CustomerRecord | null>(null);
  const [statementCustomerId, setStatementCustomerId] = useState<string | null>(null);
  const [form, setForm] = useState<CustomerFormState>(emptyForm());
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [lifecycleTarget, setLifecycleTarget] = useState<CustomerRecord | null>(null);
  const [lifecycleMode, setLifecycleMode] = useState<'archive' | 'restore'>('archive');
  const [lifecycleReason, setLifecycleReason] = useState('');
  const [deleteTarget, setDeleteTarget] = useState<CustomerRecord | null>(null);
  const customersQuery = useQuery({ queryKey: ['customers', statusFilter], queryFn: () => listCustomers(statusFilter) });

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
  const lifecycleMutation = useMutation({
    mutationFn: ({ customer, archive, reason }: { customer: CustomerRecord; archive: boolean; reason?: string }) =>
      archive ? archiveCustomer(customer.id, reason) : restoreCustomer(customer.id, reason),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['customers'] });
      closeLifecycleDialog();
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

  const openEditDialog = useCallback((customer: CustomerRecord) => {
    setError(null);
    setEditingCustomer(customer);
    setForm({
      full_name: customer.full_name,
      registration_date: customer.registration_date ?? '',
      groom_name: customer.groom_name ?? '',
      bride_name: customer.bride_name ?? '',
      phone: customer.phone,
      phone_2: customer.phone_2 ?? '',
      email: customer.email ?? '',
      address: customer.address ?? '',
      notes: customer.notes ?? '',
      is_active: customer.is_active,
    });
    setDialogOpen(true);
  }, [setEditingCustomer, setForm, setDialogOpen]);

  async function saveCustomer() {
    setError(null);
    
    // Validation
    if (!form.bride_name.trim() && !form.groom_name.trim()) {
      setError(language === 'ar' ? 'يجب إدخال اسم العروسة أو العريس على الأقل' : 'At least Bride or Groom name is required');
      return;
    }
    if (!form.address || form.address.trim().length < 2) {
      setError(language === 'ar' ? 'العنوان مطلوب (حرفين على الأقل)' : 'Address is required (at least 2 chars)');
      return;
    }
    if (!form.phone || form.phone.trim().length < 3) {
      setError(language === 'ar' ? 'رقم الهاتف مطلوب' : 'Phone number is required');
      return;
    }

    const calculatedFullName = form.full_name || (form.groom_name && form.bride_name ? `${form.groom_name} & ${form.bride_name}` : (form.groom_name || form.bride_name || 'Customer'));
    
    if (editingCustomer) {
      await updateMutation.mutateAsync({
        customerId: editingCustomer.id,
        payload: { 
          ...form, 
          full_name: calculatedFullName,
          email: form.email || null, 
          address: form.address, 
          notes: form.notes || null 
        },
      });
      return;
    }
    await createMutation.mutateAsync({
      full_name: calculatedFullName,
      registration_date: form.registration_date || null,
      groom_name: form.groom_name || null,
      bride_name: form.bride_name || null,
      phone: form.phone,
      phone_2: form.phone_2 || null,
      email: form.email || null,
      address: form.address,
      notes: form.notes || null,
    });
  }

  const openLifecycleDialog = useCallback((customer: CustomerRecord, archive: boolean) => {
    setError(null);
    setLifecycleTarget(customer);
    setLifecycleMode(archive ? 'archive' : 'restore');
    setLifecycleReason('');
  }, [setLifecycleTarget, setLifecycleMode, setLifecycleReason]);

  function closeLifecycleDialog() {
    setLifecycleTarget(null);
    setLifecycleReason('');
  }

  async function confirmLifecycle() {
    if (!lifecycleTarget) return;
    await lifecycleMutation.mutateAsync({
      customer: lifecycleTarget,
      archive: lifecycleMode === 'archive',
      reason: lifecycleReason || undefined,
    });
  }

  function closeDeleteDialog() {
    setDeleteTarget(null);
  }

  const rows = useMemo(() => customersQuery.data ?? [], [customersQuery.data]);

  const labels =
    language === 'ar'
      ? { search: 'بحث', searchPlaceholder: 'ابحث بالاسم أو العريس أو العروسة أو الهاتف', columns: 'الأعمدة', export: 'تصدير', reset: 'إعادة الضبط', noRows: 'لا توجد بيانات مطابقة' }
      : { search: 'Search', searchPlaceholder: 'Search by name, groom, bride, or phone', columns: 'Columns', export: 'Export', reset: 'Reset', noRows: 'No matching rows' };

  const columns = useMemo<ColDef<CustomerRecord>[]>(
    () => [
      { colId: 'groom_name', field: 'groom_name', headerName: customersText.table.groomName, pinned: language === 'ar' ? 'right' : 'left' },
      { colId: 'bride_name', field: 'bride_name', headerName: customersText.table.brideName },
      { colId: 'registration_date', field: 'registration_date', headerName: language === 'ar' ? 'تاريخ التسجيل' : 'Reg. Date' },
      { colId: 'phone', field: 'phone', headerName: customersText.table.phone },
      { colId: 'phone_2', field: 'phone_2', headerName: customersText.table.phone2, valueFormatter: ({ value }) => value ?? EMPTY_VALUE },
      { colId: 'address', field: 'address', headerName: customersText.dialog.address, valueFormatter: ({ value }) => value ?? EMPTY_VALUE },
      {
        colId: 'status',
        headerName: customersText.table.status,
        valueGetter: ({ data }) => (data?.is_active ? customersText.status.active : customersText.status.inactive),
        cellRenderer: ({ data }: { data: CustomerRecord | undefined }) =>
          data ? <Chip label={data.is_active ? customersText.status.active : customersText.status.inactive} size='small' color={data.is_active ? 'success' : 'default'} /> : null,
      },
      {
        colId: 'action',
        headerName: customersText.table.action,
        sortable: false,
        filter: false,
        width: 160,
        suppressSizeToFit: true,
        pinned: language === 'ar' ? 'left' : 'right',
        cellRenderer: ({ data }: { data: CustomerRecord | undefined }) =>
          data ? (
            <Stack direction='row' spacing={0.5} alignItems='center' justifyContent='center' sx={{ height: '100%' }}>
              <Tooltip title={customersText.statement.actionBtn} arrow enterTouchDelay={0}>
                <IconButton size='small' color='info' sx={{ p: 0.75 }} onClick={() => setStatementCustomerId(data.id)}>
                  <ReceiptLongOutlinedIcon fontSize='small' />
                </IconButton>
              </Tooltip>
              <Tooltip title={commonText.edit} arrow enterTouchDelay={0}>
                <IconButton size='small' color='primary' sx={{ p: 0.75 }} onClick={() => openEditDialog(data)}>
                  <EditOutlinedIcon fontSize='small' />
                </IconButton>
              </Tooltip>
              <Tooltip title={data.is_active ? (language === 'ar' ? 'أرشفة' : 'Archive') : language === 'ar' ? 'استعادة' : 'Restore'} arrow enterTouchDelay={0}>
                <IconButton size='small' color={data.is_active ? 'warning' : 'success'} sx={{ p: 0.75 }} onClick={() => openLifecycleDialog(data, data.is_active)}>
                  {data.is_active ? <ArchiveOutlinedIcon fontSize='small' /> : <UnarchiveOutlinedIcon fontSize='small' />}
                </IconButton>
              </Tooltip>
              <Tooltip title={language === 'ar' ? 'حذف تصحيحي' : 'Corrective delete'} arrow enterTouchDelay={0}>
                <IconButton size='small' color='error' sx={{ p: 0.75 }} onClick={() => setDeleteTarget(data)}>
                  <DeleteOutlineIcon fontSize='small' />
                </IconButton>
              </Tooltip>
            </Stack>
          ) : null,
      },
    ],
    [commonText.edit, customersText.statement.actionBtn, customersText.status.active, customersText.status.inactive, customersText.table.action, customersText.table.email, customersText.table.fullName, customersText.table.phone, customersText.table.status, language, openEditDialog, openLifecycleDialog, setDeleteTarget],
  );

  return (
    <Stack spacing={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent='space-between' alignItems={{ xs: 'stretch', sm: 'center' }}>
        <Box>
          <Typography variant='h4'>{customersText.page.title}</Typography>
          <Typography color='text.secondary'>{customersText.page.description}</Typography>
        </Box>
        <Button variant='contained' startIcon={<PersonAddOutlinedIcon />} onClick={openCreateDialog} sx={{ alignSelf: { xs: 'stretch', sm: 'auto' } }}>
          {customersText.page.create}
        </Button>
      </Stack>

      {error ? <Alert severity='error'>{error}</Alert> : null}

      <SectionCard title={customersText.page.listTitle} subtitle={customersText.page.listSubtitle}>
        <AppAgGrid
          tableKey='customers-list'
          rows={rows}
          columns={columns}
          language={language}
          searchLabel={labels.search}
          searchPlaceholder={labels.searchPlaceholder}
          columnsLabel={labels.columns}
          exportLabel={labels.export}
          resetLabel={labels.reset}
          closeLabel={language === 'ar' ? 'إغلاق' : 'Close'}
          noRowsLabel={labels.noRows}
          rowsPerPageLabel={language === 'ar' ? 'عدد الصفوف' : 'Rows per page'}
          toolbarFilters={
            <TextField
              select
              SelectProps={{ native: true }}
              size='small'
              label={customersText.table.status}
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value as 'all' | 'active' | 'inactive')}
              sx={{ minWidth: 180 }}
            >
              <option value='all'>{language === 'ar' ? 'الكل' : 'All'}</option>
              <option value='active'>{customersText.status.active}</option>
              <option value='inactive'>{customersText.status.inactive}</option>
            </TextField>
          }
          onExport={useCallback((format: 'csv' | 'xlsx') => {
            const isXlsx = format === 'xlsx';
            const url = isXlsx ? getCustomersExcelUrl() : getCustomersExportUrl();
            downloadFile(url);
          }, [])}
          getRowId={({ data }) => data.id}
        />
      </SectionCard>

      <CustomerFormDialog open={dialogOpen} editing={Boolean(editingCustomer)} form={form} onChange={setForm} onClose={closeDialog} onSave={() => void saveCustomer()} />

      <CustomerStatementDialog open={Boolean(statementCustomerId)} customerId={statementCustomerId} language={language} onClose={() => setStatementCustomerId(null)} />

      <LifecycleReasonDialog
        open={Boolean(lifecycleTarget)}
        mode={lifecycleMode}
        entityLabel={lifecycleTarget?.full_name ?? ''}
        reason={lifecycleReason}
        language={language}
        onReasonChange={setLifecycleReason}
        onCancel={closeLifecycleDialog}
        onConfirm={() => void confirmLifecycle()}
        loading={lifecycleMutation.isPending}
      />
      <DestructiveDeleteDialog
        open={Boolean(deleteTarget)}
        entityType='customer'
        entityId={deleteTarget?.id ?? null}
        entityLabel={deleteTarget?.full_name ?? ''}
        onClose={closeDeleteDialog}
        onDeleted={() => void queryClient.invalidateQueries({ queryKey: ['customers'] })}
        onError={(message) => setError(message)}
      />
    </Stack>
  );
}

