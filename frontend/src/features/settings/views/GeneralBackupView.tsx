import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined';
import { Alert, Button, Link, Stack } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { AppDataTable } from '../../../components/data-table/AppDataTable';
import { SectionCard } from '../../../components/SectionCard';
import { useLanguage } from '../../language/LanguageProvider';
import { createBackup, getBackupDownloadUrl, listBackups } from '../api';
import { queryClient } from '../../../lib/queryClient';
import { useSettingsText } from '../../../text/settings';

export function GeneralBackupView() {
  const { language } = useLanguage();
  const settingsText = useSettingsText();
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const backupsQuery = useQuery({ queryKey: ['settings', 'backups'], queryFn: listBackups });

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
      {message ? <Alert severity='success'>{message}</Alert> : null}
      {error ? <Alert severity='error'>{error}</Alert> : null}

      <SectionCard title={settingsText.backups.title} subtitle={settingsText.backups.subtitle}>
        <Stack spacing={2}>
          <Button 
            variant='contained' 
            startIcon={<DownloadOutlinedIcon />} 
            onClick={() => void backupMutation.mutateAsync()}
            disabled={backupMutation.isPending}
          >
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
    </Stack>
  );
}
