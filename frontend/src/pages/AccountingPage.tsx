import { Box, Button, Chip, Grid, Stack, Tab, Tabs, Typography, Menu, MenuItem, IconButton } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { MoreVertical, Edit, Trash2 } from 'lucide-react';
import { AppDataTable } from '../components/data-table/AppDataTable';
import { SectionCard } from '../components/SectionCard';
import { getChartOfAccounts, getJournalEntries, postJournalEntry, reverseJournalEntry, deleteJournalEntry, deleteChartAccount, JournalEntryRecord, ChartAccountRecord } from '../features/accounting/api';
import { useLanguage } from '../features/language/LanguageProvider';
import { useAccountingText } from '../text/accounting';
import { useLanguageFormatters } from '../text/common';
import ReconciliationPage from '../features/finance/ReconciliationPage';
import { TrialBalanceTab } from '../features/accounting/TrialBalanceTab';
import { IncomeStatementTab } from '../features/accounting/IncomeStatementTab';
import { AgingReportTab } from '../features/accounting/AgingReportTab';
import { AddAccountDialog } from '../features/accounting/AddAccountDialog';
import { JournalEntryDialog } from '../features/accounting/JournalEntryDialog';
import { queryClient } from '../lib/queryClient';

export function AccountingPage() {
  const { language } = useLanguage();
  const accountingText = useAccountingText();
  const formatters = useLanguageFormatters();
  const [activeTab, setActiveTab] = useState(0);
  const [isAddAccountOpen, setIsAddAccountOpen] = useState(false);
  const [isJournalOpen, setIsJournalOpen] = useState(false);
  const [selectedJournal, setSelectedJournal] = useState<JournalEntryRecord | null>(null);
  const [selectedAccount, setSelectedAccount] = useState<ChartAccountRecord | null>(null);
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [activeJournalRow, setActiveJournalRow] = useState<JournalEntryRecord | null>(null);

  const chartQuery = useQuery({ queryKey: ['accounting', 'chart'], queryFn: getChartOfAccounts });
  const journalsQuery = useQuery({ queryKey: ['accounting', 'journals'], queryFn: getJournalEntries });
  const isAr = language === 'ar';

  const postMutation = useMutation({ mutationFn: postJournalEntry, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['accounting', 'journals'] }) });
  const reverseMutation = useMutation({ mutationFn: ({ id, reason }: { id: string; reason: string }) => reverseJournalEntry(id, { reversal_reason: reason }), onSuccess: () => queryClient.invalidateQueries({ queryKey: ['accounting', 'journals'] }) });
  const deleteJournalMutation = useMutation({ mutationFn: deleteJournalEntry, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['accounting', 'journals'] }) });
  const deleteAccountMutation = useMutation({ mutationFn: deleteChartAccount, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['accounting', 'chart'] }) });

  const handleReverse = (id: string) => {
    const reason = window.prompt(isAr ? 'أدخل سبب العكس:' : 'Enter reversal reason:');
    if (reason?.trim()) reverseMutation.mutate({ id, reason: reason.trim() });
  };

  const handleDeleteAccount = (row: ChartAccountRecord) => {
    if ((chartQuery.data ?? []).some(acc => acc.parent_account_id === row.id)) return window.alert(isAr ? '⚠️ لا يمكن حذف هذا الحساب لوجود حسابات فرعية تابعة له. يرجى حذف أو نقل الحسابات الفرعية أولاً.' : 'Cannot delete account with sub-accounts.');
    if ((journalsQuery.data ?? []).some(j => (j.lines ?? []).some(l => l.account_id === row.id))) return window.alert(isAr ? '⚠️ لا يمكن حذف هذا الحساب لوجود قيود يومية أو حركات مالية مسجلة عليه.' : 'Cannot delete account with registered movements.');
    if (window.confirm(isAr ? `هل أنت متأكد من حذف الحساب "${row.name}"؟` : `Are you sure you want to delete "${row.name}"?`)) deleteAccountMutation.mutate(row.id);
  };

  const tableLabels = {
    search: isAr ? 'بحث' : 'Search',
    filters: isAr ? 'الفلاتر' : 'Filters',
    columns: isAr ? 'الأعمدة' : 'Columns',
    export: isAr ? 'تصدير' : 'Export',
    reset: isAr ? 'إعادة الضبط' : 'Reset',
    noRows: isAr ? 'لا توجد بيانات مطابقة' : 'No matching rows',
    rowsPerPage: isAr ? 'عدد الصفوف' : 'Rows per page',
    close: isAr ? 'إغلاق' : 'Close',
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
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 5 }}>
            <SectionCard title={accountingText.chart.title} subtitle={accountingText.chart.subtitle}>
              <Stack direction="row" justifyContent="flex-end" sx={{ mb: 1 }}>
                <Button variant="contained" size="small" onClick={() => { setSelectedAccount(null); setIsAddAccountOpen(true); }}>
                  {isAr ? 'إضافة حساب جديد' : 'Add New Account'}
                </Button>
              </Stack>
              <AppDataTable
                tableKey='accounting-chart'
                rows={chartQuery.data ?? []}
                columns={[
                  { key: 'code', header: accountingText.chart.code, searchValue: (row) => row.code, render: (row) => row.code },
                  { key: 'name', header: accountingText.chart.account, searchValue: (row) => row.name, render: (row) => row.name },
                  { key: 'account_type', header: accountingText.chart.type, searchValue: (row) => row.account_type, render: (row) => row.account_type },
                  {
                    key: 'actions',
                    header: isAr ? 'إجراءات' : 'Actions',
                    render: (row) => (
                      <Stack direction="row" spacing={0.5}>
                        <IconButton size="small" onClick={() => { setSelectedAccount(row); setIsAddAccountOpen(true); }}>
                          <Edit size={16} />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleDeleteAccount(row)}>
                          <Trash2 size={16} />
                        </IconButton>
                      </Stack>
                    )
                  }
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

          <Grid size={{ xs: 12, md: 7 }}>
            <SectionCard title={accountingText.journals.title} subtitle={accountingText.journals.subtitle}>
              <Stack direction="row" justifyContent="flex-end" sx={{ mb: 1 }}>
                <Button variant="contained" size="small" onClick={() => { setSelectedJournal(null); setIsJournalOpen(true); }}>
                  {isAr ? 'إنشاء قيد يدوي' : 'Create Manual Entry'}
                </Button>
              </Stack>
              <AppDataTable
                tableKey='accounting-journals'
                rows={journalsQuery.data ?? []}
                columns={[
                  { key: 'entry_number', header: accountingText.journals.number, searchValue: (row) => row.entry_number, render: (row) => row.entry_number },
                  { key: 'entry_date', header: accountingText.journals.date, searchValue: (row) => row.entry_date, render: (row) => row.entry_date },
                  { key: 'status', header: accountingText.journals.status, searchValue: (row) => row.status, render: (row) => <Chip label={isAr && row.status === 'draft' ? 'مسودة' : isAr && row.status === 'posted' ? 'مرحل' : isAr && row.status === 'reversed' ? 'معكوس' : row.status} color={row.status === 'posted' ? 'success' : row.status === 'reversed' ? 'error' : 'default'} size='small' /> },
                  { key: 'reference', header: accountingText.journals.reference, searchValue: (row) => row.reference ?? '', render: (row) => row.reference ?? '-' },
                  { key: 'total_debit', header: accountingText.journals.debit, sortValue: (row) => Number(row.total_debit), render: (row) => formatters.formatDecimal(Number(row.total_debit)) },
                  { key: 'total_credit', header: accountingText.journals.credit, sortValue: (row) => Number(row.total_credit), render: (row) => formatters.formatDecimal(Number(row.total_credit)) },
                  {
                    key: 'actions',
                    header: isAr ? 'إجراءات' : 'Actions',
                    render: (row) => (
                      <IconButton size="small" onClick={(e) => { setActiveJournalRow(row); setMenuAnchor(e.currentTarget); }}>
                        <MoreVertical size={16} />
                      </IconButton>
                    ),
                  },
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
      )}

      {activeTab === 1 && <TrialBalanceTab />}
      {activeTab === 2 && <IncomeStatementTab />}
      {activeTab === 3 && <AgingReportTab />}
      {activeTab === 4 && <ReconciliationPage />}

      <AddAccountDialog
        open={isAddAccountOpen}
        onClose={() => { setIsAddAccountOpen(false); setSelectedAccount(null); }}
        accounts={chartQuery.data ?? []}
        isAr={isAr}
        account={selectedAccount}
      />

      <JournalEntryDialog
        open={isJournalOpen}
        onClose={() => { setIsJournalOpen(false); setSelectedJournal(null); }}
        accounts={chartQuery.data ?? []}
        isAr={isAr}
        entry={selectedJournal}
      />

      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={() => { setMenuAnchor(null); setActiveJournalRow(null); }}
      >
        <MenuItem onClick={() => { setSelectedJournal(activeJournalRow); setIsJournalOpen(true); setMenuAnchor(null); }}>
          {isAr ? 'عرض التفاصيل' : 'View Details'}
        </MenuItem>
        
        {activeJournalRow?.status === 'draft' && (
          <MenuItem onClick={() => { setSelectedJournal(activeJournalRow); setIsJournalOpen(true); setMenuAnchor(null); }}>
            {isAr ? 'تعديل القيد' : 'Edit Entry'}
          </MenuItem>
        )}

        {activeJournalRow?.status === 'draft' && (
          <MenuItem
            onClick={() => {
              if (activeJournalRow) postMutation.mutate(activeJournalRow.id);
              setMenuAnchor(null);
            }}
            disabled={postMutation.isPending}
          >
            {isAr ? 'ترحيل القيد' : 'Post Entry'}
          </MenuItem>
        )}

        {activeJournalRow?.status === 'draft' && (
          <MenuItem
            onClick={() => {
              if (activeJournalRow && window.confirm(isAr ? 'هل أنت متأكد من حذف هذا القيد المسودة؟' : 'Are you sure you want to delete this draft entry?')) {
                deleteJournalMutation.mutate(activeJournalRow.id);
              }
              setMenuAnchor(null);
            }}
            disabled={deleteJournalMutation.isPending}
            sx={{ color: 'error.main' }}
          >
            {isAr ? 'حذف القيد' : 'Delete Entry'}
          </MenuItem>
        )}

        {activeJournalRow?.status === 'posted' && (
          <MenuItem
            onClick={() => {
              if (activeJournalRow) handleReverse(activeJournalRow.id);
              setMenuAnchor(null);
            }}
            disabled={reverseMutation.isPending}
          >
            {isAr ? 'عكس القيد' : 'Reverse Entry'}
          </MenuItem>
        )}
      </Menu>
    </Stack>
  );
}

