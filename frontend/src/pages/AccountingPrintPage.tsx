import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import {
  Alert, Box, CircularProgress, Stack, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow, Typography
} from '@mui/material';

import { useAuth } from '../features/auth/AuthProvider';
import { useLanguage } from '../features/language/LanguageProvider';
import { PrintPageFrame } from '../features/exports/PrintPageFrame';
import { getTrialBalance, getIncomeStatement, getAgingReport } from '../features/accounting/api';
import { useLanguageFormatters } from '../text/common';

export function AccountingPrintPage() {
  const { user } = useAuth();
  const { language } = useLanguage();
  const formatters = useLanguageFormatters();
  const [params] = useSearchParams();

  const type = params.get('type') ?? 'trial-balance';
  const asOfDate = params.get('asOfDate') ?? undefined;
  const branchId = params.get('branchId') ?? undefined;
  const branchName = params.get('branchName') ?? user?.active_branch_name;
  const includeZero = params.get('includeZero') === 'true';
  const partyType = params.get('partyType') as 'customer' | 'supplier' | null;

  const isAr = language === 'ar';

  // 1. Trial Balance Query
  const tbQuery = useQuery({
    queryKey: ['accounting', 'print-tb', asOfDate, branchId, includeZero],
    queryFn: () => getTrialBalance({ asOfDate, branchId, includeZeroAccounts: includeZero }),
    enabled: type === 'trial-balance'
  });

  // 2. Income Statement Query
  const isQuery = useQuery({
    queryKey: ['accounting', 'print-is', asOfDate, branchId],
    queryFn: () => getIncomeStatement({ asOfDate, branchId }),
    enabled: type === 'income-statement'
  });

  // 3. Aging Report Query
  const agingQuery = useQuery({
    queryKey: ['accounting', 'print-aging', partyType, asOfDate],
    queryFn: () => getAgingReport({ partyType: partyType || 'customer', asOfDate }),
    enabled: type === 'aging' && !!partyType
  });

  let title = isAr ? 'تقرير مالي' : 'Financial Report';
  let subtitle = '';

  if (type === 'trial-balance') {
    title = isAr ? 'ميزان المراجعة' : 'Trial Balance';
    subtitle = isAr 
      ? `تقرير ميزان المراجعة ${asOfDate ? `حتى تاريخ ${asOfDate}` : ''}`
      : `Trial Balance Report ${asOfDate ? `as of ${asOfDate}` : ''}`;
  } else if (type === 'income-statement') {
    title = isAr ? 'قائمة الدخل' : 'Income Statement';
    subtitle = isAr
      ? `تقرير قائمة الدخل ${asOfDate ? `حتى تاريخ ${asOfDate}` : ''}`
      : `Income Statement Report ${asOfDate ? `as of ${asOfDate}` : ''}`;
  } else if (type === 'aging') {
    title = partyType === 'customer' 
      ? (isAr ? 'تقرير أعمار ذمم العملاء' : 'Customer Aging Report')
      : (isAr ? 'تقرير أعمار ذمم الموردين' : 'Supplier Aging Report');
    subtitle = isAr
      ? `تحليل أعمار الذمم المجدولة ${asOfDate ? `حتى تاريخ ${asOfDate}` : ''}`
      : `Aging Report Buckets ${asOfDate ? `as of ${asOfDate}` : ''}`;
  }

  const isLoading = tbQuery.isPending || isQuery.isPending || agingQuery.isPending;
  const error = tbQuery.error || isQuery.error || agingQuery.error;

  return (
    <PrintPageFrame title={title} subtitle={subtitle} branchName={branchName} userName={user?.full_name}>
      <Stack spacing={3} sx={{ mt: 2 }}>
        {isLoading && (
          <Box display="flex" justifyContent="center" py={8}><CircularProgress /></Box>
        )}

        {error && (
          <Alert severity="error">{(error as Error).message}</Alert>
        )}

        {!isLoading && !error && type === 'trial-balance' && tbQuery.data && (
          <TableContainer>
            <Table size="small" sx={{ '& td, & th': { borderBottom: '1px solid #e2e8f0', py: 1 } }}>
              <TableHead>
                <TableRow sx={{ '& th': { fontWeight: 'bold', color: '#1e293b' } }}>
                  <TableCell>{isAr ? 'الكود' : 'Code'}</TableCell>
                  <TableCell>{isAr ? 'الحساب' : 'Account'}</TableCell>
                  <TableCell align="right">{isAr ? 'حركة مدين' : 'Mov Debit'}</TableCell>
                  <TableCell align="right">{isAr ? 'حركة دائن' : 'Mov Credit'}</TableCell>
                  <TableCell align="right">{isAr ? 'رصيد مدين' : 'Bal Debit'}</TableCell>
                  <TableCell align="right">{isAr ? 'رصيد دائن' : 'Bal Credit'}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tbQuery.data.rows.map((row) => (
                  <TableRow key={row.account_id}>
                    <TableCell sx={{ fontFamily: 'monospace' }}>{row.account_code}</TableCell>
                    <TableCell>{row.account_name}</TableCell>
                    <TableCell align="right">{formatters.formatDecimal(Number(row.movement_debit))}</TableCell>
                    <TableCell align="right">{formatters.formatDecimal(Number(row.movement_credit))}</TableCell>
                    <TableCell align="right">{formatters.formatDecimal(Number(row.balance_debit))}</TableCell>
                    <TableCell align="right">{formatters.formatDecimal(Number(row.balance_credit))}</TableCell>
                  </TableRow>
                ))}
                <TableRow sx={{ '& td': { fontWeight: 'bold', bgcolor: '#f8fafc' } }}>
                  <TableCell colSpan={2}>{isAr ? 'الإجمالي' : 'Total'}</TableCell>
                  <TableCell align="right">{formatters.formatDecimal(Number(tbQuery.data.summary.movement_debit_total))}</TableCell>
                  <TableCell align="right">{formatters.formatDecimal(Number(tbQuery.data.summary.movement_credit_total))}</TableCell>
                  <TableCell align="right">{formatters.formatDecimal(Number(tbQuery.data.summary.balance_debit_total))}</TableCell>
                  <TableCell align="right">{formatters.formatDecimal(Number(tbQuery.data.summary.balance_credit_total))}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {!isLoading && !error && type === 'income-statement' && isQuery.data && (
          <Stack spacing={4}>
            <Box sx={{ p: 2, bgcolor: '#f8fafc', borderRadius: 2, display: 'flex', justifyContent: 'space-between', border: '1px solid #e2e8f0' }}>
              <Typography variant="subtitle1" fontWeight="bold">{isAr ? 'صافي الدخل (الربح / الخسارة)' : 'Net Income'}</Typography>
              <Typography variant="h5" fontWeight="bold" color={Number(isQuery.data.net_income) >= 0 ? 'success.main' : 'error.main'}>
                {formatters.formatCurrency(Number(isQuery.data.net_income))}
              </Typography>
            </Box>

            <Box>
              <Typography variant="subtitle2" fontWeight="bold" color="primary" gutterBottom>{isAr ? 'الإيرادات' : 'Revenues'}</Typography>
              <Table size="small" sx={{ '& td': { py: 0.75 } }}>
                <TableBody>
                  {isQuery.data.revenues.items.map(row => (
                    <TableRow key={row.account_id}>
                      <TableCell sx={{ pl: row.level * 2, fontFamily: 'monospace' }}>{row.account_code}</TableCell>
                      <TableCell sx={{ pl: row.level * 2 }}>{row.account_name}</TableCell>
                      <TableCell align="right">{formatters.formatDecimal(Number(row.balance))}</TableCell>
                    </TableRow>
                  ))}
                  <TableRow sx={{ '& td': { fontWeight: 'bold', bgcolor: '#f8fafc' } }}>
                    <TableCell colSpan={2}>{isAr ? 'إجمالي الإيرادات' : 'Total Revenues'}</TableCell>
                    <TableCell align="right">{formatters.formatDecimal(Number(isQuery.data.revenues.total))}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </Box>

            <Box>
              <Typography variant="subtitle2" fontWeight="bold" color="error" gutterBottom>{isAr ? 'المصروفات' : 'Expenses'}</Typography>
              <Table size="small" sx={{ '& td': { py: 0.75 } }}>
                <TableBody>
                  {isQuery.data.expenses.items.map(row => (
                    <TableRow key={row.account_id}>
                      <TableCell sx={{ pl: row.level * 2, fontFamily: 'monospace' }}>{row.account_code}</TableCell>
                      <TableCell sx={{ pl: row.level * 2 }}>{row.account_name}</TableCell>
                      <TableCell align="right">{formatters.formatDecimal(Number(row.balance))}</TableCell>
                    </TableRow>
                  ))}
                  <TableRow sx={{ '& td': { fontWeight: 'bold', bgcolor: '#f8fafc' } }}>
                    <TableCell colSpan={2}>{isAr ? 'إجمالي المصروفات' : 'Total Expenses'}</TableCell>
                    <TableCell align="right">{formatters.formatDecimal(Number(isQuery.data.expenses.total))}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </Box>
          </Stack>
        )}

        {!isLoading && !error && type === 'aging' && agingQuery.data && (
          <TableContainer>
            <Table size="small" sx={{ '& td, & th': { borderBottom: '1px solid #e2e8f0', py: 1 } }}>
              <TableHead>
                <TableRow sx={{ '& th': { fontWeight: 'bold', color: '#1e293b' } }}>
                  <TableCell>{isAr ? 'الاسم' : 'Name'}</TableCell>
                  <TableCell align="right">{isAr ? 'إجمالي المستحق' : 'Total Balance'}</TableCell>
                  <TableCell align="right">{isAr ? 'حالي (0-30)' : 'Current'}</TableCell>
                  <TableCell align="right">31-60</TableCell>
                  <TableCell align="right">61-90</TableCell>
                  <TableCell align="right">91+</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {agingQuery.data.rows.map((row) => (
                  <TableRow key={row.party_id}>
                    <TableCell>{row.party_name}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>{formatters.formatDecimal(Number(row.total_outstanding))}</TableCell>
                    <TableCell align="right">{formatters.formatDecimal(Number(row.buckets['current']))}</TableCell>
                    <TableCell align="right">{formatters.formatDecimal(Number(row.buckets['31-60']))}</TableCell>
                    <TableCell align="right">{formatters.formatDecimal(Number(row.buckets['61-90']))}</TableCell>
                    <TableCell align="right">{formatters.formatDecimal(Number(row.buckets['91+']))}</TableCell>
                  </TableRow>
                ))}
                <TableRow sx={{ '& td': { fontWeight: 'bold', bgcolor: '#f8fafc' } }}>
                  <TableCell>{isAr ? 'الإجمالي' : 'Total'}</TableCell>
                  <TableCell align="right">{formatters.formatDecimal(Number(agingQuery.data.total_receivable_or_payable))}</TableCell>
                  <TableCell colSpan={4} />
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Stack>
    </PrintPageFrame>
  );
}
