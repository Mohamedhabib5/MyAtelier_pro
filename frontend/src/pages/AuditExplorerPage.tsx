import { Alert, Button, Grid, Stack, TextField, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { AppDataTable } from '../components/data-table/AppDataTable';
import { SectionCard } from '../components/SectionCard';
import { buildNightlyOpsCsvUrl, listAuditEvents, listDestructiveActions, listNightlyOpsEvents } from '../features/audit/api';
import { NightlyExportSummary } from '../features/audit/NightlyExportSummary';
import { useLanguage } from '../features/language/LanguageProvider';
import { useAuditText } from '../text/audit';

type AuditFilterMode = 'all' | 'destructive' | 'nightly_ops';
type QuickRange = 'today' | 'last24h' | 'last7d';

export function AuditExplorerPage() {
  const auditText = useAuditText();
  const { language } = useLanguage();
  const [search, setSearch] = useState('');
  const [actorUserId, setActorUserId] = useState('');
  const [action, setAction] = useState('');
  const [targetType, setTargetType] = useState('');
  const [targetId, setTargetId] = useState('');
  const [branchId, setBranchId] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [mode, setMode] = useState<AuditFilterMode>('all');
  const [filtersVersion, setFiltersVersion] = useState(0);

  const auditQuery = useQuery({
    queryKey: ['audit', 'events', filtersVersion, search, actorUserId, action, targetType, targetId, branchId, dateFrom, dateTo],
    queryFn: () => {
      const query = {
        search: search || undefined,
        actorUserId: actorUserId || undefined,
        action: action || undefined,
        targetType: targetType || undefined,
        targetId: targetId || undefined,
        branchId: branchId || undefined,
        dateFrom: dateFrom || undefined,
        dateTo: dateTo || undefined,
      };
      if (mode === 'destructive') {
        return listDestructiveActions(query);
      }
      if (mode === 'nightly_ops') {
        return listNightlyOpsEvents(query);
      }
      return listAuditEvents(query);
    },
  });

  const labels =
    language === 'ar'
      ? {
          search: 'بحث',
          searchPlaceholder: 'بحث داخل نتائج السجل',
          filters: 'الفلاتر',
          columns: 'الأعمدة',
          export: 'تصدير',
          reset: 'إعادة الضبط',
          noRows: auditText.page.noRows,
          rowsPerPage: 'عدد الصفوف',
          close: 'إغلاق',
        }
      : {
          search: 'Search',
          searchPlaceholder: 'Search in audit rows',
          filters: 'Filters',
          columns: 'Columns',
          export: 'Export',
          reset: 'Reset',
          noRows: auditText.page.noRows,
          rowsPerPage: 'Rows per page',
          close: 'Close',
        };

  function applyQuickRange(range: QuickRange) {
    const today = new Date();
    const end = formatDate(today);
    if (range === 'today') {
      setDateFrom(end);
      setDateTo(end);
      setFiltersVersion((value) => value + 1);
      return;
    }
    const startDate = new Date(today);
    if (range === 'last24h') {
      startDate.setDate(startDate.getDate() - 1);
    } else {
      startDate.setDate(startDate.getDate() - 6);
    }
    setDateFrom(formatDate(startDate));
    setDateTo(end);
    setFiltersVersion((value) => value + 1);
  }

  function exportNightlyOpsCsv() {
    const exportReason = window.prompt(auditText.page.exportReasonPrompt, '')?.trim() ?? '';
    const url = buildNightlyOpsCsvUrl({
      search: search || undefined,
      actorUserId: actorUserId || undefined,
      targetType: targetType || undefined,
      targetId: targetId || undefined,
      branchId: branchId || undefined,
      dateFrom: dateFrom || undefined,
      dateTo: dateTo || undefined,
    }, 1000, exportReason || undefined);
    window.location.assign(url);
  }

  const activeFilterPairs: string[] = [
    search ? `search=${search}` : '',
    actorUserId ? `actor_user_id=${actorUserId}` : '',
    targetType ? `target_type=${targetType}` : '',
    targetId ? `target_id=${targetId}` : '',
    branchId ? `branch_id=${branchId}` : '',
    dateFrom ? `date_from=${dateFrom}` : '',
    dateTo ? `date_to=${dateTo}` : '',
  ].filter(Boolean);

  return (
    <Stack spacing={3}>
      <Stack spacing={0.5}>
        <Typography variant='h4'>{auditText.page.title}</Typography>
        <Typography color='text.secondary'>{auditText.page.subtitle}</Typography>
      </Stack>

      {auditQuery.error instanceof Error ? <Alert severity='error'>{auditQuery.error.message}</Alert> : null}

      <SectionCard title={auditText.page.applyFilters} subtitle={auditText.page.subtitle}>
        <Stack spacing={2}>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField fullWidth label={auditText.page.search} value={search} onChange={(event) => setSearch(event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField fullWidth label={auditText.page.actorUserId} value={actorUserId} onChange={(event) => setActorUserId(event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField fullWidth label={auditText.page.action} value={action} onChange={(event) => setAction(event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField fullWidth label={auditText.page.targetType} value={targetType} onChange={(event) => setTargetType(event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField fullWidth label={auditText.page.targetId} value={targetId} onChange={(event) => setTargetId(event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField fullWidth label={auditText.page.branchId} value={branchId} onChange={(event) => setBranchId(event.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField fullWidth label={auditText.page.dateFrom} type='date' value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} InputLabelProps={{ shrink: true }} />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField fullWidth label={auditText.page.dateTo} type='date' value={dateTo} onChange={(event) => setDateTo(event.target.value)} InputLabelProps={{ shrink: true }} />
            </Grid>
          </Grid>
          <Stack direction='row' spacing={1}>
            <Typography variant='body2' color='text.secondary' sx={{ alignSelf: 'center' }}>
              {auditText.page.quickRanges}
            </Typography>
            <Button variant='outlined' size='small' onClick={() => applyQuickRange('today')}>
              {auditText.page.today}
            </Button>
            <Button variant='outlined' size='small' onClick={() => applyQuickRange('last24h')}>
              {auditText.page.last24h}
            </Button>
            <Button variant='outlined' size='small' onClick={() => applyQuickRange('last7d')}>
              {auditText.page.last7d}
            </Button>
          </Stack>
          <Stack direction='row' spacing={1}>
            <Button variant='contained' onClick={() => setFiltersVersion((value) => value + 1)}>
              {auditText.page.applyFilters}
            </Button>
            <Button
              variant={mode === 'destructive' ? 'contained' : 'outlined'}
              onClick={() => {
                setMode((value) => (value === 'destructive' ? 'all' : 'destructive'));
                setFiltersVersion((value) => value + 1);
              }}
            >
              {mode === 'destructive' ? auditText.page.allActions : auditText.page.destructiveOnly}
            </Button>
            <Button
              variant={mode === 'nightly_ops' ? 'contained' : 'outlined'}
              onClick={() => {
                setMode((value) => (value === 'nightly_ops' ? 'all' : 'nightly_ops'));
                setFiltersVersion((value) => value + 1);
              }}
            >
              {mode === 'nightly_ops' ? auditText.page.allActions : auditText.page.nightlyOps}
            </Button>
            <Button
              variant='outlined'
              onClick={() => {
                setSearch('');
                setActorUserId('');
                setAction('');
                setTargetType('');
                setTargetId('');
                setBranchId('');
                setDateFrom('');
                setDateTo('');
                setMode('all');
                setFiltersVersion((value) => value + 1);
              }}
            >
              {auditText.page.resetFilters}
            </Button>
            {mode === 'nightly_ops' ? (
              <>
                <Typography variant='body2' color='text.secondary' sx={{ alignSelf: 'center' }}>
                  {`${auditText.page.exportRows}: ${auditQuery.data?.total ?? 0}`}
                </Typography>
                <Typography variant='body2' color='text.secondary' sx={{ alignSelf: 'center' }}>
                  {`${auditText.page.exportFilters}: ${activeFilterPairs.length > 0 ? activeFilterPairs.join(' | ') : auditText.page.noActiveFilters}`}
                </Typography>
                <Button variant='outlined' color='success' onClick={exportNightlyOpsCsv}>
                  {auditText.page.exportNightlyCsv}
                </Button>
              </>
            ) : null}
          </Stack>
          {mode === 'nightly_ops' ? <NightlyExportSummary language={language} items={auditQuery.data?.items ?? []} /> : null}
        </Stack>
      </SectionCard>

      <SectionCard title={auditText.page.title} subtitle={auditText.page.subtitle}>
        <AppDataTable
          tableKey='audit-events'
          rows={auditQuery.data?.items ?? []}
          columns={[
            { key: 'occurred_at', header: auditText.page.occurredAt, searchValue: (row) => row.occurred_at, render: (row) => row.occurred_at },
            { key: 'action', header: auditText.page.action, searchValue: (row) => row.action, render: (row) => row.action },
            { key: 'actor', header: auditText.page.actor, searchValue: (row) => row.actor_name ?? row.actor_user_id ?? '', render: (row) => row.actor_name ?? row.actor_user_id ?? '-' },
            { key: 'entity', header: auditText.page.entity, searchValue: (row) => `${row.target_type} ${row.target_id ?? ''}`, render: (row) => `${row.target_type}${row.target_id ? `/${row.target_id}` : ''}` },
            { key: 'summary', header: auditText.page.summary, searchValue: (row) => row.summary, render: (row) => row.summary },
            { key: 'status', header: auditText.page.status, searchValue: (row) => `${row.success ?? ''} ${row.error_code ?? ''}`, render: (row) => (row.success === false ? row.error_code ?? 'failed' : 'ok') },
          ]}
          searchLabel={labels.search}
          searchPlaceholder={labels.searchPlaceholder}
          resetColumnsLabel={labels.reset}
          noRowsLabel={labels.noRows}
          filtersLabel={labels.filters}
          columnsLabel={labels.columns}
          exportLabel={labels.export}
          rowsPerPageLabel={labels.rowsPerPage}
          closeLabel={labels.close}
          searchFields={[(row) => row.action, (row) => row.summary, (row) => row.target_type, (row) => row.target_id ?? '']}
        />
      </SectionCard>
    </Stack>
  );
}

function formatDate(value: Date): string {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, '0');
  const day = String(value.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}
