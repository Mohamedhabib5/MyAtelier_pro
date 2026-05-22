import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Alert, Box, Button, CircularProgress, FormControl,
  Grid, InputLabel, MenuItem, Select, Stack, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow,
  TextField, Typography, Paper
} from '@mui/material';
import FileDownloadOutlinedIcon from '@mui/icons-material/FileDownloadOutlined';
import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

import { getIncomeStatement, getIncomeStatementExcelUrl } from './api';
import { getCompany } from '../settings/api';
import { useAuth } from '../auth/AuthProvider';
import { useLanguage } from '../language/LanguageProvider';
import { useLanguageFormatters } from '../../text/common';
import { downloadFile } from '../../lib/api';

export function IncomeStatementTab() {
  const { user } = useAuth();
  const { language } = useLanguage();
  const formatters = useLanguageFormatters();

  const [branchId, setBranchId] = useState<string>(user?.active_branch_id || '');
  const [asOfDate, setAsOfDate] = useState<string>('');

  const companyQuery = useQuery({ queryKey: ['settings', 'company'], queryFn: getCompany });
  const incomeStatementQuery = useQuery({
    queryKey: ['accounting', 'income-statement', asOfDate, branchId],
    queryFn: () => getIncomeStatement({
      asOfDate: asOfDate || undefined,
      branchId: branchId || undefined,
    }),
  });

  const branches = (companyQuery.data?.branches ?? []).filter((b) => b.is_active);

  const handleExportExcel = () => {
    const url = getIncomeStatementExcelUrl({
      asOfDate: asOfDate || undefined,
      branchId: branchId || undefined,
    });
    void downloadFile(url);
  };

  const handlePrint = () => {
    const searchParams = new URLSearchParams();
    searchParams.set('type', 'income-statement');
    if (asOfDate) searchParams.set('asOfDate', asOfDate);
    if (branchId) searchParams.set('branchId', branchId);
    
    const activeBranchName = branchId
      ? branches.find(b => b.id === branchId)?.name ?? ''
      : (language === 'ar' ? 'جميع الفروع (مجمع)' : 'All Branches (Consolidated)');
    searchParams.set('branchName', activeBranchName);

    window.open(`/print/accounting?${searchParams.toString()}`, '_blank');
  };

  const isAr = language === 'ar';
  const data = incomeStatementQuery.data;
  const netIncome = Number(data?.net_income ?? 0);
  const isProfit = netIncome >= 0;

  return (
    <Stack spacing={3}>
      <Paper sx={{ p: 2.5, borderRadius: 2, border: '1px solid', borderColor: 'divider', background: 'rgba(255,255,255,0.8)', backdropFilter: 'blur(8px)' }}>
        <Grid container spacing={2.5} alignItems="center">
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <FormControl fullWidth size="small">
              <InputLabel id="is-branch-select-label">{isAr ? 'الفرع' : 'Branch'}</InputLabel>
              <Select
                labelId="is-branch-select-label"
                value={branchId}
                label={isAr ? 'الفرع' : 'Branch'}
                onChange={(e) => setBranchId(e.target.value)}
              >
                <MenuItem value="">
                  <em>{isAr ? 'جميع الفروع (مجمّع)' : 'All Branches (Consolidated)'}</em>
                </MenuItem>
                {branches.map((b) => (
                  <MenuItem key={b.id} value={b.id}>
                    {b.name} ({b.code})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <TextField
              fullWidth
              size="small"
              label={isAr ? 'حتى تاريخ' : 'As of Date'}
              type="date"
              value={asOfDate}
              onChange={(e) => setAsOfDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 12, md: 4 }}>
            <Stack direction="row" spacing={1.5} justifyContent="flex-end">
              <Button
                variant="outlined"
                color="success"
                startIcon={<FileDownloadOutlinedIcon />}
                onClick={handleExportExcel}
                disabled={incomeStatementQuery.isPending}
              >
                {isAr ? 'تصدير إكسل' : 'Excel'}
              </Button>
              <Button
                variant="contained"
                color="primary"
                startIcon={<PrintOutlinedIcon />}
                onClick={handlePrint}
                disabled={incomeStatementQuery.isPending}
              >
                {isAr ? 'طباعة' : 'Print'}
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </Paper>

      {incomeStatementQuery.error && (
        <Alert severity="error">{(incomeStatementQuery.error as Error).message}</Alert>
      )}

      {data && (
        <Paper
          sx={{
            p: 3,
            borderRadius: 3,
            border: '1px solid',
            borderColor: isProfit ? 'success.light' : 'error.light',
            background: isProfit
              ? 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)'
              : 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)',
            boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.05)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Box>
            <Typography variant="subtitle2" color={isProfit ? 'success.dark' : 'error.dark'} fontWeight="700" letterSpacing={0.5}>
              {isAr ? 'صافي الدخل (الربح / الخسارة)' : 'Net Income (Profit / Loss)'}
            </Typography>
            <Typography variant="h3" fontWeight="bold" color={isProfit ? 'success.main' : 'error.main'} sx={{ mt: 1 }}>
              {formatters.formatCurrency(netIncome)}
            </Typography>
          </Box>
          <Box
            sx={{
              p: 2,
              borderRadius: '50%',
              bgcolor: isProfit ? 'success.main' : 'error.main',
              color: 'common.white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0px 8px 16px rgba(0, 0, 0, 0.1)',
            }}
          >
            {isProfit ? <TrendingUpIcon fontSize="large" /> : <TrendingDownIcon fontSize="large" />}
          </Box>
        </Paper>
      )}

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 2.5, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="h6" fontWeight="bold" color="primary">
                {isAr ? 'الإيرادات' : 'Revenues'}
              </Typography>
              <Typography variant="subtitle1" fontWeight="bold" color="success.main">
                {isAr ? 'إجمالي الإيرادات: ' : 'Total: '}
                {data ? formatters.formatCurrency(Number(data.revenues.total)) : '—'}
              </Typography>
            </Stack>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ '& th': { fontWeight: 'bold', backgroundColor: '#f8fafc' } }}>
                    <TableCell>{isAr ? 'كود الحساب' : 'Code'}</TableCell>
                    <TableCell>{isAr ? 'الحساب' : 'Account'}</TableCell>
                    <TableCell align="right">{isAr ? 'الرصيد' : 'Balance'}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {incomeStatementQuery.isPending ? (
                    <TableRow><TableCell colSpan={3} align="center" sx={{ py: 4 }}><CircularProgress size={20} /></TableCell></TableRow>
                  ) : !data?.revenues.items.length ? (
                    <TableRow><TableCell colSpan={3} align="center" sx={{ py: 3 }}>{isAr ? 'لا توجد إيرادات مسجلة.' : 'No revenues recorded.'}</TableCell></TableRow>
                  ) : (
                    data.revenues.items.map((item) => (
                      <TableRow key={item.account_id} hover sx={{ pl: item.level * 2 }}>
                        <TableCell sx={{ fontFamily: 'monospace', pl: item.level * 1.5 }}>{item.account_code}</TableCell>
                        <TableCell sx={{ pl: item.level * 1.5 }}>{item.account_name}</TableCell>
                        <TableCell align="right" sx={{ fontWeight: '500' }}>{formatters.formatDecimal(Number(item.balance))}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 2.5, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="h6" fontWeight="bold" color="error">
                {isAr ? 'المصروفات' : 'Expenses'}
              </Typography>
              <Typography variant="subtitle1" fontWeight="bold" color="error.main">
                {isAr ? 'إجمالي المصروفات: ' : 'Total: '}
                {data ? formatters.formatCurrency(Number(data.expenses.total)) : '—'}
              </Typography>
            </Stack>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ '& th': { fontWeight: 'bold', backgroundColor: '#f8fafc' } }}>
                    <TableCell>{isAr ? 'كود الحساب' : 'Code'}</TableCell>
                    <TableCell>{isAr ? 'الحساب' : 'Account'}</TableCell>
                    <TableCell align="right">{isAr ? 'الرصيد' : 'Balance'}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {incomeStatementQuery.isPending ? (
                    <TableRow><TableCell colSpan={3} align="center" sx={{ py: 4 }}><CircularProgress size={20} /></TableCell></TableRow>
                  ) : !data?.expenses.items.length ? (
                    <TableRow><TableCell colSpan={3} align="center" sx={{ py: 3 }}>{isAr ? 'لا توجد مصروفات مسجلة.' : 'No expenses recorded.'}</TableCell></TableRow>
                  ) : (
                    data.expenses.items.map((item) => (
                      <TableRow key={item.account_id} hover sx={{ pl: item.level * 2 }}>
                        <TableCell sx={{ fontFamily: 'monospace', pl: item.level * 1.5 }}>{item.account_code}</TableCell>
                        <TableCell sx={{ pl: item.level * 1.5 }}>{item.account_name}</TableCell>
                        <TableCell align="right" sx={{ fontWeight: '500' }}>{formatters.formatDecimal(Number(item.balance))}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Stack>
  );
}
