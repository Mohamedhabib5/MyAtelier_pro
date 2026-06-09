import { Alert, Button, Grid, Stack, TextField, Typography, CircularProgress } from '@mui/material';
import { ShieldCheck } from 'lucide-react';

import { AppDataTable } from '../components/data-table/AppDataTable';
import { SectionCard } from '../components/SectionCard';
import { NightlyExportSummary } from '../features/audit/NightlyExportSummary';
import { useAuditExplorer } from '../features/audit/hooks/useAuditExplorer';
import { AuditIntegrityDialog } from '../features/audit/components/AuditIntegrityDialog';
import { AppDateRangeFilter } from '../components/inputs/AppDateRangeFilter';

export function AuditExplorerPage() {
  const {
    search, setSearch,
    actorUserId, setActorUserId,
    action, setAction,
    targetType, setTargetType,
    targetId, setTargetId,
    branchId, setBranchId,
    dateFrom,
    dateTo,
    activePreset,
    customFrom,
    customTo,
    selectPreset,
    setCustomFrom,
    setCustomTo,
    mode, setMode,
    setFiltersVersion,
    verifying,
    integrityResult,
    showIntegrityDialog, setShowIntegrityDialog,
    auditQuery,
    labels,
    exportNightlyOpsCsv,
    handleVerifyIntegrity,
    activeFilterPairs,
    auditText,
    language,
  } = useAuditExplorer();

  return (
    <Stack spacing={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="space-between" alignItems={{ xs: 'stretch', sm: 'center' }}>
        <Stack spacing={0.5}>
          <Typography variant='h4'>{auditText.page.title}</Typography>
          <Typography color='text.secondary'>{auditText.page.subtitle}</Typography>
        </Stack>
        <Button 
          variant="contained" 
          color="secondary" 
          startIcon={verifying ? <CircularProgress size={20} color="inherit" /> : <ShieldCheck size={20} />}
          onClick={handleVerifyIntegrity}
          disabled={verifying}
          sx={{ borderRadius: 3, fontWeight: 'bold', alignSelf: { xs: 'stretch', sm: 'auto' } }}
        >
          {verifying ? 'جاري التحقق...' : 'التحقق من نزاهة السجل'}
        </Button>
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
            <Grid size={{ xs: 12, md: 8 }}>
              <AppDateRangeFilter
                language={language}
                activePreset={activePreset}
                customFrom={customFrom}
                customTo={customTo}
                onSelectPreset={selectPreset}
                onCustomFromChange={setCustomFrom}
                onCustomToChange={setCustomTo}
              />
            </Grid>
          </Grid>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
            <Button variant='contained' onClick={() => setFiltersVersion((value) => value + 1)} sx={{ width: { xs: '100%', sm: 'auto' } }}>
              {auditText.page.applyFilters}
            </Button>
            <Button
              variant={mode === 'destructive' ? 'contained' : 'outlined'}
              onClick={() => {
                setMode((value) => (value === 'destructive' ? 'all' : 'destructive'));
                setFiltersVersion((value) => value + 1);
              }}
              sx={{ width: { xs: '100%', sm: 'auto' } }}
            >
              {mode === 'destructive' ? auditText.page.allActions : auditText.page.destructiveOnly}
            </Button>
            <Button
              variant={mode === 'nightly_ops' ? 'contained' : 'outlined'}
              onClick={() => {
                setMode((value) => (value === 'nightly_ops' ? 'all' : 'nightly_ops'));
                setFiltersVersion((value) => value + 1);
              }}
              sx={{ width: { xs: '100%', sm: 'auto' } }}
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
                selectPreset('all');
                setMode('all');
                setFiltersVersion((value) => value + 1);
              }}
              sx={{ width: { xs: '100%', sm: 'auto' } }}
            >
              {auditText.page.resetFilters}
            </Button>
            {mode === 'nightly_ops' ? (
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ width: { xs: '100%', sm: 'auto' }, alignItems: 'center', gap: 1 }}>
                <Typography variant='body2' color='text.secondary' sx={{ alignSelf: 'center' }}>
                  {`${auditText.page.exportRows}: ${auditQuery.data?.total ?? 0}`}
                </Typography>
                <Typography variant='body2' color='text.secondary' sx={{ alignSelf: 'center' }}>
                  {`${auditText.page.exportFilters}: ${activeFilterPairs.length > 0 ? activeFilterPairs.join(' | ') : auditText.page.noActiveFilters}`}
                </Typography>
                <Button variant='outlined' color='success' onClick={exportNightlyOpsCsv} sx={{ width: { xs: '100%', sm: 'auto' } }}>
                  {auditText.page.exportNightlyCsv}
                </Button>
              </Stack>
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

      <AuditIntegrityDialog 
        open={showIntegrityDialog} 
        onClose={() => setShowIntegrityDialog(false)} 
        result={integrityResult} 
      />
    </Stack>
  );
}

