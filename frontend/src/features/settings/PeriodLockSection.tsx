import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { Alert, Button, Chip, Stack, TextField, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';

import { AppDataTable } from '../../components/data-table/AppDataTable';
import { SectionCard } from '../../components/SectionCard';
import { queryClient } from '../../lib/queryClient';
import { getPeriodLock, listPeriodLockExceptions, updatePeriodLock } from './api';

type PeriodLockSectionProps = {
  language: 'ar' | 'en';
  onError: (message: string | null) => void;
  onSuccess: (message: string) => void;
};

export function PeriodLockSection({ language, onError, onSuccess }: PeriodLockSectionProps) {
  const [lockedThrough, setLockedThrough] = useState('');
  const [note, setNote] = useState('');
  const periodLockQuery = useQuery({ queryKey: ['settings', 'period-lock'], queryFn: getPeriodLock });
  const exceptionsQuery = useQuery({
    queryKey: ['settings', 'period-lock-exceptions'],
    queryFn: () => listPeriodLockExceptions(100),
  });

  useEffect(() => {
    setLockedThrough(periodLockQuery.data?.locked_through ?? '');
  }, [periodLockQuery.data?.locked_through]);

  const updateMutation = useMutation({
    mutationFn: updatePeriodLock,
    onSuccess: async () => {
      onError(null);
      onSuccess(language === 'ar' ? 'تم تحديث إعداد قفل الفترة بنجاح.' : 'Period lock settings updated.');
      setNote('');
      await queryClient.invalidateQueries({ queryKey: ['settings', 'period-lock'] });
      await queryClient.invalidateQueries({ queryKey: ['settings', 'period-lock-exceptions'] });
    },
    onError: (mutationError: Error) => {
      onError(mutationError.message);
    },
  });

  const labels = useMemo(
    () =>
      language === 'ar'
        ? {
            title: 'قفل الفترة',
            subtitle: 'حدد تاريخ الإغلاق الذي يمنع التعديلات التصحيحية بعده إلا عبر Override مع سبب.',
            date: 'مقفول حتى تاريخ',
            note: 'ملاحظة التغيير (اختيارية)',
            save: 'حفظ قفل الفترة',
            clear: 'إلغاء القفل',
            locked: 'الفترة مقفولة',
            unlocked: 'الفترة مفتوحة',
            exceptionsTitle: 'استثناءات قفل الفترة (Override)',
            exceptionSearch: 'بحث في الاستثناءات',
            exceptionSearchPlaceholder: 'بحث بالعملية أو المستخدم أو السبب',
            noRows: 'لا توجد استثناءات مسجلة.',
            when: 'التاريخ والوقت',
            actor: 'المستخدم',
            action: 'العملية',
            actionDate: 'تاريخ العملية',
            lockDate: 'تاريخ القفل',
            reason: 'سبب Override',
            filters: 'الفلاتر',
            columns: 'الأعمدة',
            export: 'تصدير',
            reset: 'إعادة الضبط',
            rowsPerPage: 'عدد الصفوف',
            close: 'إغلاق',
          }
        : {
            title: 'Period lock',
            subtitle: 'Set closing date to block corrective actions unless override is approved with a reason.',
            date: 'Locked through date',
            note: 'Change note (optional)',
            save: 'Save period lock',
            clear: 'Clear lock',
            locked: 'Period locked',
            unlocked: 'Period unlocked',
            exceptionsTitle: 'Period-lock override exceptions',
            exceptionSearch: 'Search exceptions',
            exceptionSearchPlaceholder: 'Search by action, actor, or reason',
            noRows: 'No override exceptions found.',
            when: 'Occurred at',
            actor: 'Actor',
            action: 'Action',
            actionDate: 'Action date',
            lockDate: 'Lock date',
            reason: 'Override reason',
            filters: 'Filters',
            columns: 'Columns',
            export: 'Export',
            reset: 'Reset',
            rowsPerPage: 'Rows per page',
            close: 'Close',
          },
    [language],
  );

  return (
    <Stack spacing={3}>
      <SectionCard title={labels.title} subtitle={labels.subtitle}>
        <Stack spacing={2}>
          <Stack direction='row' spacing={1} alignItems='center'>
            <LockOutlinedIcon fontSize='small' color='action' />
            <Chip color={periodLockQuery.data?.is_locked ? 'warning' : 'success'} size='small' label={periodLockQuery.data?.is_locked ? labels.locked : labels.unlocked} />
          </Stack>
          <TextField label={labels.date} type='date' InputLabelProps={{ shrink: true }} value={lockedThrough} onChange={(event) => setLockedThrough(event.target.value)} />
          <TextField label={labels.note} value={note} onChange={(event) => setNote(event.target.value)} multiline minRows={2} />
          <Stack direction='row' spacing={1}>
            <Button
              variant='contained'
              onClick={() =>
                void updateMutation.mutateAsync({
                  locked_through: lockedThrough || null,
                  note: note || null,
                })
              }
            >
              {labels.save}
            </Button>
            <Button
              variant='outlined'
              color='warning'
              onClick={() =>
                void updateMutation.mutateAsync({
                  locked_through: null,
                  note: note || null,
                })
              }
            >
              {labels.clear}
            </Button>
          </Stack>
          {periodLockQuery.data?.updated_at ? (
            <Typography variant='body2' color='text.secondary'>
              {`${labels.when}: ${periodLockQuery.data.updated_at}`}
            </Typography>
          ) : null}
          {exceptionsQuery.isError ? <Alert severity='error'>{(exceptionsQuery.error as Error).message}</Alert> : null}
        </Stack>
      </SectionCard>

      <SectionCard title={labels.exceptionsTitle}>
        <AppDataTable
          tableKey='settings-period-lock-exceptions'
          rows={exceptionsQuery.data ?? []}
          columns={[
            { key: 'occurred_at', header: labels.when, searchValue: (row) => row.occurred_at, render: (row) => row.occurred_at },
            { key: 'actor_name', header: labels.actor, searchValue: (row) => row.actor_name ?? row.actor_user_id ?? '', render: (row) => row.actor_name ?? row.actor_user_id ?? '-' },
            { key: 'action_key', header: labels.action, searchValue: (row) => row.action_key ?? '', render: (row) => row.action_key ?? '-' },
            { key: 'action_date', header: labels.actionDate, searchValue: (row) => row.action_date ?? '', render: (row) => row.action_date ?? '-' },
            { key: 'locked_through', header: labels.lockDate, searchValue: (row) => row.locked_through ?? '', render: (row) => row.locked_through ?? '-' },
            { key: 'override_reason', header: labels.reason, searchValue: (row) => row.override_reason ?? '', render: (row) => row.override_reason ?? '-' },
          ]}
          searchLabel={labels.exceptionSearch}
          searchPlaceholder={labels.exceptionSearchPlaceholder}
          resetColumnsLabel={labels.reset}
          noRowsLabel={labels.noRows}
          filtersLabel={labels.filters}
          columnsLabel={labels.columns}
          exportLabel={labels.export}
          rowsPerPageLabel={labels.rowsPerPage}
          closeLabel={labels.close}
          searchFields={[(row) => row.action_key ?? '', (row) => row.actor_name ?? '', (row) => row.override_reason ?? '']}
        />
      </SectionCard>
    </Stack>
  );
}
