import { Alert, Box, Chip, FormControlLabel, Grid, Stack, Switch, TextField, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import { AppDataTable } from '../components/data-table/AppDataTable';
import { SectionCard } from '../components/SectionCard';
import { getChartOfAccounts, getJournalEntries, getTrialBalance } from '../features/accounting/api';
import { useLanguage } from '../features/language/LanguageProvider';
import { useAccountingText } from '../text/accounting';
import { useLanguageFormatters } from '../text/common';

export function AccountingPage() {
  const { language } = useLanguage();
  const accountingText = useAccountingText();
  const formatters = useLanguageFormatters();
  const [asOfDate, setAsOfDate] = useState('');
  const [includeZeroAccounts, setIncludeZeroAccounts] = useState(false);
  const chartQuery = useQuery({ queryKey: ['accounting', 'chart'], queryFn: getChartOfAccounts });
  const journalsQuery = useQuery({ queryKey: ['accounting', 'journals'], queryFn: getJournalEntries });
  const trialBalanceQuery = useQuery({
    queryKey: ['accounting', 'trial-balance', asOfDate, includeZeroAccounts],
    queryFn: () => getTrialBalance({ asOfDate: asOfDate || undefined, includeZeroAccounts }),
  });

  const errorMessage = (chartQuery.error as Error | null)?.message || (journalsQuery.error as Error | null)?.message || (trialBalanceQuery.error as Error | null)?.message || null;
  const summaryChips = useMemo(() => {
    const summary = trialBalanceQuery.data?.summary;
    if (!summary) return [];
    return [
      `${accountingText.trialBalance.summary.entries}: ${summary.entry_count}`,
      `${accountingText.trialBalance.summary.movementDebit}: ${formatters.formatDecimal(Number(summary.movement_debit_total))}`,
      `${accountingText.trialBalance.summary.movementCredit}: ${formatters.formatDecimal(Number(summary.movement_credit_total))}`,
      `${accountingText.trialBalance.summary.balanceDebit}: ${formatters.formatDecimal(Number(summary.balance_debit_total))}`,
      `${accountingText.trialBalance.summary.balanceCredit}: ${formatters.formatDecimal(Number(summary.balance_credit_total))}`,
    ];
  }, [accountingText.trialBalance.summary, formatters, trialBalanceQuery.data]);
  const tableLabels =
    language === 'ar'
      ? {
          search: 'بحث',
          filters: 'الفلاتر',
          columns: 'الأعمدة',
          export: 'تصدير',
          reset: 'إعادة الضبط',
          noRows: 'لا توجد بيانات مطابقة',
          rowsPerPage: 'عدد الصفوف',
          close: 'إغلاق',
        }
      : {
          search: 'Search',
          filters: 'Filters',
          columns: 'Columns',
          export: 'Export',
          reset: 'Reset',
          noRows: 'No matching rows',
          rowsPerPage: 'Rows per page',
          close: 'Close',
        };

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant='h4'>{accountingText.page.title}</Typography>
        <Typography color='text.secondary'>{accountingText.page.description}</Typography>
      </Box>

      {errorMessage ? <Alert severity='error'>{errorMessage}</Alert> : null}

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 5 }}>
          <SectionCard title={accountingText.chart.title} subtitle={accountingText.chart.subtitle}>
            <AppDataTable
              tableKey='accounting-chart'
              rows={chartQuery.data ?? []}
              columns={[
                { key: 'code', header: accountingText.chart.code, searchValue: (row) => row.code, render: (row) => row.code },
                { key: 'name', header: accountingText.chart.account, searchValue: (row) => row.name, render: (row) => row.name },
                { key: 'account_type', header: accountingText.chart.type, searchValue: (row) => row.account_type, render: (row) => row.account_type },
              ]}
              searchLabel={tableLabels.search}
              searchPlaceholder={language === 'ar' ? 'ابحث بالكود أو اسم الحساب' : 'Search by code or account name'}
              resetColumnsLabel={tableLabels.reset}
              noRowsLabel={tableLabels.noRows}
              filtersLabel={tableLabels.filters}
              columnsLabel={tableLabels.columns}
              exportLabel={tableLabels.export}
              rowsPerPageLabel={tableLabels.rowsPerPage}
              closeLabel={tableLabels.close}
              searchFields={[(row) => row.code, (row) => row.name, (row) => row.account_type]}
            />
          </SectionCard>
        </Grid>

        <Grid size={{ xs: 12, md: 7 }}>
          <SectionCard title={accountingText.journals.title} subtitle={accountingText.journals.subtitle}>
            <AppDataTable
              tableKey='accounting-journals'
              rows={journalsQuery.data ?? []}
              columns={[
                { key: 'entry_number', header: accountingText.journals.number, searchValue: (row) => row.entry_number, render: (row) => row.entry_number },
                { key: 'entry_date', header: accountingText.journals.date, searchValue: (row) => row.entry_date, render: (row) => row.entry_date },
                { key: 'status', header: accountingText.journals.status, searchValue: (row) => row.status, render: (row) => <Chip label={row.status} size='small' /> },
                { key: 'reference', header: accountingText.journals.reference, searchValue: (row) => row.reference ?? '', render: (row) => row.reference ?? '-' },
                { key: 'total_debit', header: accountingText.journals.debit, sortValue: (row) => Number(row.total_debit), render: (row) => formatters.formatDecimal(Number(row.total_debit)) },
                { key: 'total_credit', header: accountingText.journals.credit, sortValue: (row) => Number(row.total_credit), render: (row) => formatters.formatDecimal(Number(row.total_credit)) },
              ]}
              searchLabel={tableLabels.search}
              searchPlaceholder={language === 'ar' ? 'ابحث برقم القيد أو المرجع' : 'Search by entry number or reference'}
              resetColumnsLabel={tableLabels.reset}
              noRowsLabel={tableLabels.noRows}
              filtersLabel={tableLabels.filters}
              columnsLabel={tableLabels.columns}
              exportLabel={tableLabels.export}
              rowsPerPageLabel={tableLabels.rowsPerPage}
              closeLabel={tableLabels.close}
              searchFields={[(row) => row.entry_number, (row) => row.reference ?? '', (row) => row.status]}
            />
          </SectionCard>
        </Grid>
      </Grid>

      <SectionCard title={accountingText.trialBalance.title} subtitle={accountingText.trialBalance.subtitle}>
        <Stack spacing={2}>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ md: 'center' }}>
            <TextField label={accountingText.trialBalance.asOfDate} type='date' value={asOfDate} onChange={(event) => setAsOfDate(event.target.value)} InputLabelProps={{ shrink: true }} />
            <FormControlLabel control={<Switch checked={includeZeroAccounts} onChange={(event) => setIncludeZeroAccounts(event.target.checked)} />} label={accountingText.trialBalance.includeZero} />
          </Stack>

          <Stack direction='row' spacing={1} flexWrap='wrap' useFlexGap>
            {summaryChips.map((chip) => (
              <Chip key={chip} label={chip} />
            ))}
          </Stack>

          <AppDataTable
            tableKey='accounting-trial-balance'
            rows={trialBalanceQuery.data?.rows ?? []}
            columns={[
              { key: 'account_code', header: accountingText.trialBalance.code, searchValue: (row) => row.account_code, render: (row) => row.account_code },
              { key: 'account_name', header: accountingText.trialBalance.account, searchValue: (row) => row.account_name, render: (row) => row.account_name },
              { key: 'account_type', header: accountingText.trialBalance.accountType, searchValue: (row) => row.account_type, render: (row) => row.account_type },
              { key: 'movement_debit', header: accountingText.trialBalance.movementDebit, sortValue: (row) => Number(row.movement_debit), render: (row) => formatters.formatDecimal(Number(row.movement_debit)) },
              { key: 'movement_credit', header: accountingText.trialBalance.movementCredit, sortValue: (row) => Number(row.movement_credit), render: (row) => formatters.formatDecimal(Number(row.movement_credit)) },
              { key: 'balance_debit', header: accountingText.trialBalance.balanceDebit, sortValue: (row) => Number(row.balance_debit), render: (row) => formatters.formatDecimal(Number(row.balance_debit)) },
              { key: 'balance_credit', header: accountingText.trialBalance.balanceCredit, sortValue: (row) => Number(row.balance_credit), render: (row) => formatters.formatDecimal(Number(row.balance_credit)) },
            ]}
            searchLabel={tableLabels.search}
            searchPlaceholder={language === 'ar' ? 'ابحث بالكود أو اسم الحساب أو النوع' : 'Search by code, account, or type'}
            resetColumnsLabel={tableLabels.reset}
            noRowsLabel={tableLabels.noRows}
            filtersLabel={tableLabels.filters}
            columnsLabel={tableLabels.columns}
            exportLabel={tableLabels.export}
            rowsPerPageLabel={tableLabels.rowsPerPage}
            closeLabel={tableLabels.close}
            searchFields={[(row) => row.account_code, (row) => row.account_name, (row) => row.account_type]}
            footerContent={
              <Stack direction='row' spacing={1} flexWrap='wrap' useFlexGap>
                {summaryChips.map((chip) => (
                  <Chip key={chip} label={chip} />
                ))}
              </Stack>
            }
          />
        </Stack>
      </SectionCard>
    </Stack>
  );
}
