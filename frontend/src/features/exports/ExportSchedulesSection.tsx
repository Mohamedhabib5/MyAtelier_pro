import AutorenewOutlinedIcon from '@mui/icons-material/AutorenewOutlined';
import PauseCircleOutlineOutlinedIcon from '@mui/icons-material/PauseCircleOutlineOutlined';
import PlayCircleOutlineOutlinedIcon from '@mui/icons-material/PlayCircleOutlineOutlined';
import ScheduleOutlinedIcon from '@mui/icons-material/ScheduleOutlined';
import { Alert, Button, Chip, Stack, TextField, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import { AppDataTable } from '../../components/data-table/AppDataTable';
import { SectionCard } from '../../components/SectionCard';
import { downloadFile } from '../../lib/api';
import { queryClient } from '../../lib/queryClient';
import { cadenceLabel, exportTypeLabel, useExportsText } from '../../text/exports';
import { useLanguage } from '../language/LanguageProvider';
import { createExportSchedule, listExportSchedules, runExportSchedule, toggleExportSchedule } from './api';

const branchScopedTypes = new Set(['bookings_csv', 'booking_lines_csv', 'payments_csv', 'payment_allocations_csv', 'finance_print', 'reports_print']);

export function ExportSchedulesSection({ activeBranchName }: { activeBranchName?: string | null }) {
  const { language } = useLanguage();
  const exportsText = useExportsText();
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: '', export_type: 'bookings_csv', cadence: 'daily', start_on: '' });
  const [activeFilter, setActiveFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const schedulesQuery = useQuery({ queryKey: ['exports', 'schedules'], queryFn: listExportSchedules });

  const createMutation = useMutation({
    mutationFn: createExportSchedule,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['exports', 'schedules'] });
      setForm({ name: '', export_type: 'bookings_csv', cadence: 'daily', start_on: '' });
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const runMutation = useMutation({
    mutationFn: runExportSchedule,
    onSuccess: async (result) => {
      await queryClient.invalidateQueries({ queryKey: ['exports', 'schedules'] });
      if (result.run_url.startsWith('/api/')) {
        downloadFile(result.run_url);
      } else {
        window.open(result.run_url, '_blank', 'noopener,noreferrer');
      }
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const toggleMutation = useMutation({
    mutationFn: toggleExportSchedule,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['exports', 'schedules'] });
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  const scopeLabel = useMemo(() => {
    if (!branchScopedTypes.has(form.export_type)) return exportsText.schedules.infoCompany;
    return `${exportsText.schedules.runScopePrefix} ${activeBranchName ?? '—'}.`;
  }, [activeBranchName, exportsText.schedules.infoCompany, exportsText.schedules.runScopePrefix, form.export_type]);

  const rows = useMemo(
    () => (schedulesQuery.data ?? []).filter((schedule) => (activeFilter === 'all' ? true : activeFilter === 'active' ? schedule.is_active : !schedule.is_active)),
    [activeFilter, schedulesQuery.data],
  );

  async function submitCreate() {
    setError(null);
    await createMutation.mutateAsync({
      name: form.name,
      export_type: form.export_type,
      cadence: form.cadence,
      start_on: form.start_on || null,
    });
  }

  return (
    <SectionCard title={exportsText.schedules.heading} subtitle={exportsText.schedules.subtitle}>
      <Stack spacing={2}>
        {error ? <Alert severity='error'>{error}</Alert> : null}
        <Alert severity='info'>{scopeLabel}</Alert>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          <TextField label={exportsText.schedules.name} value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} fullWidth />
          <TextField select SelectProps={{ native: true }} label={exportsText.schedules.exportType} value={form.export_type} onChange={(event) => setForm({ ...form, export_type: event.target.value })}>
            {['customers_csv', 'bookings_csv', 'booking_lines_csv', 'payments_csv', 'payment_allocations_csv', 'finance_print', 'reports_print'].map((value) => (
              <option key={value} value={value}>
                {exportTypeLabel(language, value)}
              </option>
            ))}
          </TextField>
          <TextField select SelectProps={{ native: true }} label={exportsText.schedules.cadence} value={form.cadence} onChange={(event) => setForm({ ...form, cadence: event.target.value })}>
            {['daily', 'weekly'].map((value) => (
              <option key={value} value={value}>
                {cadenceLabel(language, value)}
              </option>
            ))}
          </TextField>
          <TextField label={exportsText.schedules.startOn} type='date' InputLabelProps={{ shrink: true }} value={form.start_on} onChange={(event) => setForm({ ...form, start_on: event.target.value })} />
          <Button variant='contained' startIcon={<ScheduleOutlinedIcon />} onClick={() => void submitCreate()}>
            {exportsText.schedules.create}
          </Button>
        </Stack>

        <AppDataTable
          tableKey='export-schedules-list'
          rows={rows}
          columns={[
            { key: 'name', header: exportsText.schedules.tableName, searchValue: (row) => row.name, render: (row) => row.name },
            { key: 'type', header: exportsText.schedules.type, searchValue: (row) => exportTypeLabel(language, row.export_type), render: (row) => exportTypeLabel(language, row.export_type) },
            { key: 'scope', header: exportsText.schedules.scope, searchValue: (row) => row.branch_name ?? exportsText.schedules.scopeCompany, render: (row) => row.branch_name ?? exportsText.schedules.scopeCompany },
            { key: 'cadence', header: exportsText.schedules.cadence, searchValue: (row) => cadenceLabel(language, row.cadence), render: (row) => cadenceLabel(language, row.cadence) },
            { key: 'next_run_on', header: exportsText.schedules.nextRun, searchValue: (row) => row.next_run_on, render: (row) => row.next_run_on },
            { key: 'last_run_at', header: exportsText.schedules.lastRun, searchValue: (row) => row.last_run_at ?? '', render: (row) => row.last_run_at ?? exportsText.schedules.lastRunEmpty },
            {
              key: 'status',
              header: exportsText.schedules.status,
              searchValue: (row) => (row.is_active ? exportsText.schedules.active : exportsText.schedules.inactive),
              render: (row) => <Chip label={row.is_active ? exportsText.schedules.active : exportsText.schedules.inactive} size='small' color={row.is_active ? 'success' : 'default'} />,
            },
            {
              key: 'action',
              header: exportsText.schedules.tableAction,
              render: (row) => (
                <Stack direction='row' spacing={1}>
                  <Button size='small' startIcon={<AutorenewOutlinedIcon />} disabled={!row.is_active} onClick={() => void runMutation.mutateAsync(row.id)}>
                    {exportsText.schedules.now}
                  </Button>
                  <Button
                    size='small'
                    color={row.is_active ? 'warning' : 'success'}
                    startIcon={row.is_active ? <PauseCircleOutlineOutlinedIcon /> : <PlayCircleOutlineOutlinedIcon />}
                    onClick={() => void toggleMutation.mutateAsync(row.id)}
                  >
                    {row.is_active ? exportsText.schedules.toggleOff : exportsText.schedules.toggleOn}
                  </Button>
                </Stack>
              ),
            },
          ]}
          searchLabel={language === 'ar' ? 'بحث' : 'Search'}
          searchPlaceholder={language === 'ar' ? 'ابحث باسم الجدولة أو النوع أو الفرع' : 'Search by schedule, type, or branch'}
          resetColumnsLabel={language === 'ar' ? 'إعادة الضبط' : 'Reset'}
          noRowsLabel={exportsText.schedules.listEmpty}
          filtersLabel={language === 'ar' ? 'الفلاتر' : 'Filters'}
          columnsLabel={language === 'ar' ? 'الأعمدة' : 'Columns'}
          exportLabel={language === 'ar' ? 'تصدير' : 'Export'}
          rowsPerPageLabel={language === 'ar' ? 'عدد الصفوف' : 'Rows per page'}
          closeLabel={language === 'ar' ? 'إغلاق' : 'Close'}
          searchFields={[(row) => row.name, (row) => row.branch_name ?? '', (row) => exportTypeLabel(language, row.export_type)]}
          filterContent={
            <TextField select SelectProps={{ native: true }} fullWidth label={exportsText.schedules.status} value={activeFilter} onChange={(event) => setActiveFilter(event.target.value as typeof activeFilter)}>
              <option value='all'>{language === 'ar' ? 'الكل' : 'All'}</option>
              <option value='active'>{exportsText.schedules.active}</option>
              <option value='inactive'>{exportsText.schedules.inactive}</option>
            </TextField>
          }
        />

        {!schedulesQuery.data?.length ? <Typography color='text.secondary'>{exportsText.schedules.listEmpty}</Typography> : null}
      </Stack>
    </SectionCard>
  );
}
