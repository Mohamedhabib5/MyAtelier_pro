import AutorenewOutlinedIcon from '@mui/icons-material/AutorenewOutlined';
import PauseCircleOutlineOutlinedIcon from '@mui/icons-material/PauseCircleOutlineOutlined';
import PlayCircleOutlineOutlinedIcon from '@mui/icons-material/PlayCircleOutlineOutlined';
import ScheduleOutlinedIcon from '@mui/icons-material/ScheduleOutlined';
import { Alert, Button, Chip, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import { SectionCard } from '../../components/SectionCard';
import { queryClient } from '../../lib/queryClient';
import { cadenceLabel, exportTypeLabel, useExportsText } from '../../text/exports';
import { useLanguage } from '../language/LanguageProvider';
import { createExportSchedule, listExportSchedules, runExportSchedule, toggleExportSchedule } from './api';

const branchScopedTypes = new Set(['bookings_csv', 'booking_lines_csv', 'payments_csv', 'payment_allocations_csv', 'finance_print', 'reports_print']);

function openUrl(url: string) {
  window.open(url, '_blank', 'noopener,noreferrer');
}

export function ExportSchedulesSection({ activeBranchName }: { activeBranchName?: string | null }) {
  const { language } = useLanguage();
  const exportsText = useExportsText();
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: '', export_type: 'bookings_csv', cadence: 'daily', start_on: '' });
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
      openUrl(result.run_url);
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
              <option key={value} value={value}>{exportTypeLabel(language, value)}</option>
            ))}
          </TextField>
          <TextField select SelectProps={{ native: true }} label={exportsText.schedules.cadence} value={form.cadence} onChange={(event) => setForm({ ...form, cadence: event.target.value })}>
            {['daily', 'weekly'].map((value) => (
              <option key={value} value={value}>{cadenceLabel(language, value)}</option>
            ))}
          </TextField>
          <TextField label={exportsText.schedules.startOn} type='date' InputLabelProps={{ shrink: true }} value={form.start_on} onChange={(event) => setForm({ ...form, start_on: event.target.value })} />
          <Button variant='contained' startIcon={<ScheduleOutlinedIcon />} onClick={() => void submitCreate()}>{exportsText.schedules.create}</Button>
        </Stack>

        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{exportsText.schedules.tableName}</TableCell>
              <TableCell>{exportsText.schedules.type}</TableCell>
              <TableCell>{exportsText.schedules.scope}</TableCell>
              <TableCell>{exportsText.schedules.cadence}</TableCell>
              <TableCell>{exportsText.schedules.nextRun}</TableCell>
              <TableCell>{exportsText.schedules.lastRun}</TableCell>
              <TableCell>{exportsText.schedules.status}</TableCell>
              <TableCell>{exportsText.schedules.tableAction}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(schedulesQuery.data ?? []).map((schedule) => (
              <TableRow key={schedule.id}>
                <TableCell>{schedule.name}</TableCell>
                <TableCell>{exportTypeLabel(language, schedule.export_type)}</TableCell>
                <TableCell>{schedule.branch_name ?? exportsText.schedules.scopeCompany}</TableCell>
                <TableCell>{cadenceLabel(language, schedule.cadence)}</TableCell>
                <TableCell>{schedule.next_run_on}</TableCell>
                <TableCell>{schedule.last_run_at ?? exportsText.schedules.lastRunEmpty}</TableCell>
                <TableCell><Chip label={schedule.is_active ? exportsText.schedules.active : exportsText.schedules.inactive} size='small' color={schedule.is_active ? 'success' : 'default'} /></TableCell>
                <TableCell>
                  <Stack direction='row' spacing={1}>
                    <Button size='small' startIcon={<AutorenewOutlinedIcon />} disabled={!schedule.is_active} onClick={() => void runMutation.mutateAsync(schedule.id)}>
                      {exportsText.schedules.now}
                    </Button>
                    <Button size='small' color={schedule.is_active ? 'warning' : 'success'} startIcon={schedule.is_active ? <PauseCircleOutlineOutlinedIcon /> : <PlayCircleOutlineOutlinedIcon />} onClick={() => void toggleMutation.mutateAsync(schedule.id)}>
                      {schedule.is_active ? exportsText.schedules.toggleOff : exportsText.schedules.toggleOn}
                    </Button>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        {!schedulesQuery.data?.length ? <Typography color='text.secondary'>{exportsText.schedules.listEmpty}</Typography> : null}
      </Stack>
    </SectionCard>
  );
}
