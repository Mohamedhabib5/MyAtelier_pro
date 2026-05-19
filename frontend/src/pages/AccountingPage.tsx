import { Box, Chip, Grid, Stack, Tab, Tabs, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { AppDataTable } from '../components/data-table/AppDataTable';
import { SectionCard } from '../components/SectionCard';
import { getChartOfAccounts, getJournalEntries } from '../features/accounting/api';
import { useLanguage } from '../features/language/LanguageProvider';
import { useAccountingText } from '../text/accounting';
import { useLanguageFormatters } from '../text/common';
import ReconciliationPage from '../features/finance/ReconciliationPage';
import { TrialBalanceTab } from '../features/accounting/TrialBalanceTab';
import { IncomeStatementTab } from '../features/accounting/IncomeStatementTab';
import { AgingReportTab } from '../features/accounting/AgingReportTab';

export function AccountingPage() {
  const { language } = useLanguage();
  const accountingText = useAccountingText();
  const formatters = useLanguageFormatters();
  const [activeTab, setActiveTab] = useState(0);

  const chartQuery = useQuery({ queryKey: ['accounting', 'chart'], queryFn: getChartOfAccounts });
  const journalsQuery = useQuery({ queryKey: ['accounting', 'journals'], queryFn: getJournalEntries });

  const isAr = language === 'ar';

  const tableLabels = isAr
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
      <Box sx={{ borderBottom: 1, borderColor: 'divider', pb: 1 }}>
        <Typography variant='h4'>{accountingText.page.title}</Typography>
        <Typography color='text.secondary'>{accountingText.page.description}</Typography>
        
        <Tabs value={activeTab} onChange={(_, val) => setActiveTab(val)} sx={{ mt: 2 }} variant="scrollable" scrollButtons="auto">
          <Tab label={isAr ? 'شجرة الحسابات والقيود' : 'Accounts & Journals'} id='accounting-subtab-main' />
          <Tab label={isAr ? 'ميزان المراجعة' : 'Trial Balance'} id='accounting-subtab-trial' />
          <Tab label={isAr ? 'قائمة الدخل' : 'Income Statement'} id='accounting-subtab-income' />
          <Tab label={isAr ? 'أعمار الذمم' : 'Aging Report'} id='accounting-subtab-aging' />
          <Tab label={isAr ? 'تسوية النقدية' : 'Cash Reconciliation'} id='accounting-subtab-reconciliation' />
        </Tabs>
      </Box>

      {activeTab === 0 && (
        <Stack spacing={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={5}>
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
                  searchPlaceholder={isAr ? 'ابحث بالكود أو اسم الحساب' : 'Search by code or account name'}
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

            <Grid item xs={12} md={7}>
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
                  searchPlaceholder={isAr ? 'ابحث برقم القيد أو المرجع' : 'Search by entry number or reference'}
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
        </Stack>
      )}

      {activeTab === 1 && <TrialBalanceTab />}
      {activeTab === 2 && <IncomeStatementTab />}
      {activeTab === 3 && <AgingReportTab />}
      {activeTab === 4 && <ReconciliationPage />}
    </Stack>
  );
}
