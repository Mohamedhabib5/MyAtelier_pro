import ApartmentOutlinedIcon from '@mui/icons-material/ApartmentOutlined';
import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined';
import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined';
import StorefrontOutlinedIcon from '@mui/icons-material/StorefrontOutlined';
import { Alert, Box, Button, Chip, Grid, Link, Stack, TextField, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useState } from 'react';

import { AppDataTable } from '../components/data-table/AppDataTable';
import { SectionCard } from '../components/SectionCard';
import { useLanguage } from '../features/language/LanguageProvider';
import { NightlyStatusSection } from '../features/settings/NightlyStatusSection';
import { PaymentMethodsSection } from '../features/settings/PaymentMethodsSection';
import { PeriodLockSection } from '../features/settings/PeriodLockSection';
import { createBackup, createBranch, getActiveBranch, getBackupDownloadUrl, getCompany, listBackups, updateCompany } from '../features/settings/api';
import { queryClient } from '../lib/queryClient';
import { EMPTY_VALUE } from '../text/common';
import { useSettingsText } from '../text/settings';

export function SettingsPage() {
  const { language } = useLanguage();
  const settingsText = useSettingsText();
  const [name, setName] = useState('');
  const [legalName, setLegalName] = useState('');
  const [currency, setCurrency] = useState('EGP');
  const [branchCode, setBranchCode] = useState('');
  const [branchName, setBranchName] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const companyQuery = useQuery({ queryKey: ['settings', 'company'], queryFn: getCompany });
  const activeBranchQuery = useQuery({ queryKey: ['settings', 'active-branch'], queryFn: getActiveBranch });
  const backupsQuery = useQuery({ queryKey: ['settings', 'backups'], queryFn: listBackups });

  useEffect(() => {
    if (!companyQuery.data) return;
    setName(companyQuery.data.name);
    setLegalName(companyQuery.data.legal_name ?? '');
    setCurrency(companyQuery.data.default_currency);
  }, [companyQuery.data]);

  const saveCompanyMutation = useMutation({
    mutationFn: updateCompany,
    onSuccess: async () => {
      setMessage(settingsText.messages.companySaved);
      setError(null);
      await queryClient.invalidateQueries({ queryKey: ['settings', 'company'] });
    },
    onError: (mutationError: Error) => {
      setError(mutationError.message);
      setMessage(null);
    },
  });
  const createBranchMutation = useMutation({
    mutationFn: createBranch,
    onSuccess: async () => {
      setMessage(settingsText.messages.branchCreated);
      setError(null);
      setBranchCode('');
      setBranchName('');
      await queryClient.invalidateQueries({ queryKey: ['settings', 'company'] });
      await queryClient.invalidateQueries({ queryKey: ['settings', 'active-branch'] });
    },
    onError: (mutationError: Error) => {
      setError(mutationError.message);
      setMessage(null);
    },
  });
  const backupMutation = useMutation({
    mutationFn: createBackup,
    onSuccess: async (backup) => {
      setMessage(settingsText.messages.backupCreated);
      setError(null);
      await queryClient.invalidateQueries({ queryKey: ['settings', 'backups'] });
      window.location.assign(getBackupDownloadUrl(backup.id));
    },
    onError: (mutationError: Error) => {
      setError(mutationError.message);
      setMessage(null);
    },
  });
  const tableLabels =
    language === 'ar'
      ? {
          search: 'بحث',
          searchPlaceholder: 'ابحث باسم الملف أو الحالة',
          filters: 'الفلاتر',
          columns: 'الأعمدة',
          export: 'تصدير',
          reset: 'إعادة الضبط',
          noRows: 'لا توجد نسخ احتياطية مطابقة',
          rowsPerPage: 'عدد الصفوف',
          close: 'إغلاق',
        }
      : {
          search: 'Search',
          searchPlaceholder: 'Search by filename or status',
          filters: 'Filters',
          columns: 'Columns',
          export: 'Export',
          reset: 'Reset',
          noRows: 'No matching backups',
          rowsPerPage: 'Rows per page',
          close: 'Close',
        };

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant='h4'>{settingsText.page.title}</Typography>
        <Typography color='text.secondary'>{settingsText.page.description}</Typography>
      </Box>

      {message ? <Alert severity='success'>{message}</Alert> : null}
      {error ? <Alert severity='error'>{error}</Alert> : null}

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 7 }}>
          <SectionCard title={settingsText.company.title} subtitle={settingsText.company.subtitle}>
            <Stack spacing={2}>
              <TextField label={settingsText.company.name} value={name} onChange={(event) => setName(event.target.value)} />
              <TextField label={settingsText.company.legalName} value={legalName} onChange={(event) => setLegalName(event.target.value)} />
              <TextField label={settingsText.company.currency} value={currency} onChange={(event) => setCurrency(event.target.value.toUpperCase())} />
              <Button variant='contained' startIcon={<SaveOutlinedIcon />} onClick={() => void saveCompanyMutation.mutateAsync({ name, legal_name: legalName || null, default_currency: currency })}>
                {settingsText.company.save}
              </Button>
            </Stack>
          </SectionCard>
        </Grid>

        <Grid size={{ xs: 12, md: 5 }}>
          <SectionCard title={settingsText.activeBranch.title} subtitle={settingsText.activeBranch.subtitle}>
            <Stack spacing={1.5}>
              <Stack direction='row' spacing={1} alignItems='center'>
                <ApartmentOutlinedIcon fontSize='small' color='action' />
                <Typography variant='h6'>{activeBranchQuery.data?.name ?? EMPTY_VALUE}</Typography>
              </Stack>
              <Typography color='text.secondary'>{activeBranchQuery.data?.code ?? EMPTY_VALUE}</Typography>
              <Stack direction='row' spacing={1}>
                {activeBranchQuery.data?.is_default ? <Chip label={settingsText.activeBranch.default} size='small' /> : null}
                {activeBranchQuery.data ? <Chip label={activeBranchQuery.data.is_active ? settingsText.activeBranch.active : settingsText.activeBranch.inactive} size='small' color='success' /> : null}
              </Stack>
              <Typography variant='body2' color='text.secondary'>{settingsText.activeBranch.note}</Typography>
            </Stack>
          </SectionCard>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 5 }}>
          <SectionCard title={settingsText.createBranch.title} subtitle={settingsText.createBranch.subtitle}>
            <Stack spacing={2}>
              <TextField label={settingsText.createBranch.code} value={branchCode} onChange={(event) => setBranchCode(event.target.value.toUpperCase())} placeholder={settingsText.createBranch.codePlaceholder} />
              <TextField label={settingsText.createBranch.name} value={branchName} onChange={(event) => setBranchName(event.target.value)} placeholder={settingsText.createBranch.namePlaceholder} />
              <Button variant='contained' startIcon={<StorefrontOutlinedIcon />} onClick={() => void createBranchMutation.mutateAsync({ code: branchCode, name: branchName })}>
                {settingsText.createBranch.create}
              </Button>
            </Stack>
          </SectionCard>
        </Grid>

        <Grid size={{ xs: 12, md: 7 }}>
          <SectionCard title={settingsText.branchList.title} subtitle={settingsText.branchList.subtitle}>
            <Stack spacing={1.5}>
              {(companyQuery.data?.branches ?? []).map((branch) => (
                <Stack key={branch.id} direction='row' justifyContent='space-between' alignItems='center'>
                  <Box>
                    <Typography>{branch.name}</Typography>
                    <Typography variant='body2' color='text.secondary'>{branch.code}</Typography>
                  </Box>
                  <Stack direction='row' spacing={1}>
                    {branch.id === activeBranchQuery.data?.id ? <Chip label={settingsText.branchList.current} size='small' color='primary' /> : null}
                    {branch.is_default ? <Chip label={settingsText.branchList.default} size='small' /> : null}
                    <Chip label={branch.is_active ? settingsText.branchList.active : settingsText.branchList.inactive} size='small' color={branch.is_active ? 'success' : 'default'} />
                  </Stack>
                </Stack>
              ))}
            </Stack>
          </SectionCard>
        </Grid>
      </Grid>

      <SectionCard title={settingsText.backups.title} subtitle={settingsText.backups.subtitle}>
        <Stack spacing={2}>
          <Button variant='contained' startIcon={<DownloadOutlinedIcon />} onClick={() => void backupMutation.mutateAsync()}>
            {settingsText.backups.create}
          </Button>
          <AppDataTable
            tableKey='settings-backups'
            rows={backupsQuery.data ?? []}
            columns={[
              { key: 'filename', header: settingsText.backups.filename, searchValue: (row) => row.filename, render: (row) => row.filename },
              { key: 'status', header: settingsText.backups.status, searchValue: (row) => row.status, render: (row) => row.status },
              { key: 'size_bytes', header: settingsText.backups.size, sortValue: (row) => row.size_bytes, render: (row) => row.size_bytes },
              {
                key: 'download',
                header: settingsText.backups.download,
                render: (row) => (
                  <Link href={getBackupDownloadUrl(row.id)} underline='hover'>
                    {settingsText.backups.download}
                  </Link>
                ),
              },
            ]}
            searchLabel={tableLabels.search}
            searchPlaceholder={tableLabels.searchPlaceholder}
            resetColumnsLabel={tableLabels.reset}
            noRowsLabel={tableLabels.noRows}
            filtersLabel={tableLabels.filters}
            columnsLabel={tableLabels.columns}
            exportLabel={tableLabels.export}
            rowsPerPageLabel={tableLabels.rowsPerPage}
            closeLabel={tableLabels.close}
            searchFields={[(row) => row.filename, (row) => row.status]}
          />
        </Stack>
      </SectionCard>

      <PaymentMethodsSection
        language={language}
        onError={(nextError) => {
          setError(nextError);
          if (nextError) setMessage(null);
        }}
        onSuccess={(nextMessage) => {
          setMessage(nextMessage);
          setError(null);
        }}
      />

      <PeriodLockSection
        language={language}
        onError={(nextError) => {
          setError(nextError);
          if (nextError) setMessage(null);
        }}
        onSuccess={(nextMessage) => {
          setMessage(nextMessage);
          setError(null);
        }}
      />
      <NightlyStatusSection language={language} />
    </Stack>
  );
}
