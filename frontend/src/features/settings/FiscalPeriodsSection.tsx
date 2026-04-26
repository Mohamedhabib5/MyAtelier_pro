import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import CalendarTodayOutlinedIcon from '@mui/icons-material/CalendarTodayOutlined';
import DeleteIcon from '@mui/icons-material/Delete';
import { 
  Alert, 
  Button, 
  Chip, 
  IconButton, 
  Stack, 
  Switch, 
  TextField, 
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions
} from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import { AppDataTable } from '../../components/data-table/AppDataTable';
import { SectionCard } from '../../components/SectionCard';
import { queryClient } from '../../lib/queryClient';
import { createFiscalPeriod, deleteFiscalPeriod, listFiscalPeriods, updateFiscalPeriod } from './api';

type FiscalPeriodsSectionProps = {
  language: 'ar' | 'en';
};

export function FiscalPeriodsSection({ language }: FiscalPeriodsSectionProps) {
  const [newName, setNewName] = useState('');
  const [newStartsOn, setNewStartsOn] = useState(new Date().getFullYear() + '-01-01');
  const [newEndsOn, setNewEndsOn] = useState(new Date().getFullYear() + '-12-31');
  const [deleteTarget, setDeleteTarget] = useState<{ id: string; name: string } | null>(null);
  
  const query = useQuery({ 
    queryKey: ['settings', 'fiscal-periods'], 
    queryFn: listFiscalPeriods 
  });

  const createMutation = useMutation({
    mutationFn: createFiscalPeriod,
    onSuccess: () => {
      setNewName('');
      queryClient.invalidateQueries({ queryKey: ['settings', 'fiscal-periods'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: any }) => updateFiscalPeriod(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'fiscal-periods'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteFiscalPeriod(id),
    onSuccess: () => {
      setDeleteTarget(null);
      queryClient.invalidateQueries({ queryKey: ['settings', 'fiscal-periods'] });
    },
  });

  const labels = useMemo(() => language === 'ar' ? {
    title: 'الفترات المالية',
    subtitle: 'إدارة السنوات المالية وتفعيلها أو قفلها. لا يمكن التسجيل المالي إلا في فترة نشطة وغير مقفلة.',
    add: 'إضافة فترة جديدة',
    name: 'اسم الفترة (مثلاً: عام 2026)',
    starts: 'تبدأ في',
    ends: 'تنتهي في',
    save: 'حفظ',
    status: 'الحالة',
    active: 'نشطة',
    locked: 'مقفولة',
    actions: 'الإجراءات',
    noRows: 'لا توجد فترات مالية مسجلة.',
    search: 'بحث',
    reset: 'إعادة ضبط',
    rows: 'صفوف',
    close: 'إغلاق',
    filters: 'الفلاتر',
    columns: 'الأعمدة',
    export: 'تصدير',
    deleteConfirmTitle: 'حذف الفترة المالية',
    deleteConfirmBody: 'هل أنت متأكد من حذف الفترة "{name}"؟ لا يمكن التراجع عن هذا الإجراء.',
    cancel: 'إلغاء',
    delete: 'حذف'
  } : {
    title: 'Fiscal Periods',
    subtitle: 'Manage fiscal years, activate, or lock them. Financial recording is only possible in an active, unlocked period.',
    add: 'Add New Period',
    name: 'Period Name (e.g. Year 2026)',
    starts: 'Starts On',
    ends: 'Ends On',
    save: 'Save',
    status: 'Status',
    active: 'Active',
    locked: 'Locked',
    actions: 'Actions',
    noRows: 'No fiscal periods found.',
    search: 'Search',
    reset: 'Reset',
    rows: 'Rows',
    close: 'Close',
    filters: 'Filters',
    columns: 'Columns',
    export: 'Export',
    deleteConfirmTitle: 'Delete Fiscal Period',
    deleteConfirmBody: 'Are you sure you want to delete period "{name}"? This action cannot be undone.',
    cancel: 'Cancel',
    delete: 'Delete'
  }, [language]);

  const handleDeleteClick = (row: any) => {
    setDeleteTarget({ id: row.id, name: row.name });
  };

  return (
    <Stack spacing={3}>
      <SectionCard title={labels.title} subtitle={labels.subtitle}>
        <Stack spacing={3}>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems='flex-end'>
            <TextField 
              fullWidth 
              label={labels.name} 
              value={newName} 
              onChange={(e) => setNewName(e.target.value)} 
            />
            <TextField 
              label={labels.starts} 
              type='date' 
              value={newStartsOn} 
              onChange={(e) => setNewStartsOn(e.target.value)} 
              InputLabelProps={{ shrink: true }} 
            />
            <TextField 
              label={labels.ends} 
              type='date' 
              value={newEndsOn} 
              onChange={(e) => setNewEndsOn(e.target.value)} 
              InputLabelProps={{ shrink: true }} 
            />
            <Button 
              variant='contained' 
              startIcon={<AddCircleOutlineIcon />}
              onClick={() => createMutation.mutate({ name: newName, starts_on: newStartsOn, ends_on: newEndsOn })}
              disabled={!newName || createMutation.isPending}
            >
              {labels.add}
            </Button>
          </Stack>

          {createMutation.isError ? (
            <Alert severity='error'>{(createMutation.error as Error).message}</Alert>
          ) : null}

          {deleteMutation.isError ? (
            <Alert severity='error'>{(deleteMutation.error as Error).message}</Alert>
          ) : null}

          <AppDataTable
            tableKey='settings-fiscal-periods'
            rows={query.data ?? []}
            columns={[
              { 
                key: 'name', 
                header: labels.name, 
                searchValue: (row) => row.name, 
                render: (row) => (
                  <Stack direction='row' spacing={1} alignItems='center'>
                    <CalendarTodayOutlinedIcon fontSize='small' color='action' />
                    <Typography variant='body2' fontWeight='medium'>{row.name}</Typography>
                  </Stack>
                )
              },
              { 
                key: 'dates', 
                header: `${labels.starts} - ${labels.ends}`, 
                render: (row) => (
                  <Typography variant='body2' color='text.secondary'>
                    {`${row.starts_on} / ${row.ends_on}`}
                  </Typography>
                )
              },
              { 
                key: 'is_active', 
                header: labels.active, 
                render: (row) => (
                  <Switch 
                    size='small' 
                    checked={row.is_active} 
                    onChange={(e) => updateMutation.mutate({ id: row.id, payload: { is_active: e.target.checked } })}
                    disabled={updateMutation.isPending}
                  />
                )
              },
              { 
                key: 'is_locked', 
                header: labels.locked, 
                render: (row) => (
                  <Chip 
                    label={row.is_locked ? labels.locked : (language === 'ar' ? 'مفتوحة' : 'Open')} 
                    color={row.is_locked ? 'warning' : 'success'} 
                    size='small'
                    onClick={() => updateMutation.mutate({ id: row.id, payload: { is_locked: !row.is_locked } })}
                  />
                )
              },
              {
                key: 'actions',
                header: labels.actions,
                render: (row) => (
                  <IconButton 
                    size='small' 
                    color='error' 
                    onClick={() => handleDeleteClick(row)}
                  >
                    <DeleteIcon fontSize='small' />
                  </IconButton>
                )
              }
            ]}
            searchLabel={labels.search}
            resetColumnsLabel={labels.reset}
            noRowsLabel={labels.noRows}
            rowsPerPageLabel={labels.rows}
            closeLabel={labels.close}
            filtersLabel={labels.filters}
            columnsLabel={labels.columns}
            exportLabel={labels.export}
          />
        </Stack>
      </SectionCard>

      <Dialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)}>
        <DialogTitle>{labels.deleteConfirmTitle}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {labels.deleteConfirmBody.replace('{name}', deleteTarget?.name ?? '')}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteTarget(null)}>{labels.cancel}</Button>
          <Button 
            color='error' 
            variant='contained' 
            onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
            disabled={deleteMutation.isPending}
          >
            {labels.delete}
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
