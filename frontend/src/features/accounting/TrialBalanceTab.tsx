import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Alert, Box, Button, Chip, CircularProgress, FormControl, FormControlLabel,
  Grid, InputLabel, MenuItem, Select, Stack, Switch,
  Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, TextField, Typography, Paper
} from '@mui/material';
import FileDownloadOutlinedIcon from '@mui/icons-material/FileDownloadOutlined';
import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined';

import { getTrialBalance, getTrialBalanceExcelUrl } from './api';
import { getCompany } from '../settings/api';
import { useAuth } from '../auth/AuthProvider';
import { useLanguage } from '../language/LanguageProvider';
import { useLanguageFormatters } from '../../text/common';
import { downloadFile } from '../../lib/api';
import { AppDateField } from '../../components/inputs/AppDateField';

export function TrialBalanceTab() {
  const { user } = useAuth();
  const { language } = useLanguage();
  const formatters = useLanguageFormatters();

  const [branchId, setBranchId] = useState<string>(user?.active_branch_id || '');
  const [asOfDate, setAsOfDate] = useState<string>('');
  const [includeZero, setIncludeZero] = useState<boolean>(false);

  const companyQuery = useQuery({ queryKey: ['settings', 'company'], queryFn: getCompany });
  const trialBalanceQuery = useQuery({
    queryKey: ['accounting', 'trial-balance', asOfDate, branchId, includeZero],
    queryFn: () => getTrialBalance({
      asOfDate: asOfDate || undefined,
      branchId: branchId || undefined,
      includeZeroAccounts: includeZero
    }),
  });

  const branches = (companyQuery.data?.branches ?? []).filter((b) => b.is_active);

  const handleExportExcel = () => {
    const url = getTrialBalanceExcelUrl({
      asOfDate: asOfDate || undefined,
      branchId: branchId || undefined,
      includeZeroAccounts: includeZero,
    });
    void downloadFile(url);
  };

  const handlePrint = () => {
    const searchParams = new URLSearchParams();
    searchParams.set('type', 'trial-balance');
    if (asOfDate) searchParams.set('asOfDate', asOfDate);
    if (branchId) searchParams.set('branchId', branchId);
    if (includeZero) searchParams.set('includeZero', 'true');
    
    const activeBranchName = branchId
      ? branches.find(b => b.id === branchId)?.name ?? ''
      : (language === 'ar' ? 'جميع الفروع (مجمع)' : 'All Branches (Consolidated)');
    searchParams.set('branchName', activeBranchName);

    window.open(`/print/accounting?${searchParams.toString()}`, '_blank');
  };

  const isAr = language === 'ar';
  const data = trialBalanceQuery.data;
  const summary = data?.summary;

  return (
    <Stack spacing={3}>
      <Paper sx={{ p: 2.5, borderRadius: 2, border: '1px solid', borderColor: 'divider', background: 'rgba(255,255,255,0.8)', backdropFilter: 'blur(8px)' }}>
        <Grid container spacing={2.5} alignItems="center">
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <FormControl fullWidth size="small">
              <InputLabel id="branch-select-label">{isAr ? 'الفرع' : 'Branch'}</InputLabel>
              <Select
                labelId="branch-select-label"
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
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <AppDateField
              size="small"
              label={isAr ? 'حتى تاريخ' : 'As of Date'}
              value={asOfDate}
              onChange={(val) => setAsOfDate(val)}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <FormControlLabel
              control={<Switch checked={includeZero} onChange={(e) => setIncludeZero(e.target.checked)} />}
              label={isAr ? 'إظهار الحسابات الصفرية' : 'Include zero accounts'}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Stack direction="row" spacing={1.5} justifyContent="flex-end">
              <Button
                variant="outlined"
                color="success"
                startIcon={<FileDownloadOutlinedIcon />}
                onClick={handleExportExcel}
                disabled={trialBalanceQuery.isPending}
              >
                {isAr ? 'تصدير إكسل' : 'Excel'}
              </Button>
              <Button
                variant="contained"
                color="primary"
                startIcon={<PrintOutlinedIcon />}
                onClick={handlePrint}
                disabled={trialBalanceQuery.isPending}
              >
                {isAr ? 'طباعة' : 'Print'}
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </Paper>

      {trialBalanceQuery.error && (
        <Alert severity="error">{(trialBalanceQuery.error as Error).message}</Alert>
      )}

      {summary && (
        <Grid container spacing={2}>
          {[
            { label: isAr ? 'حركات مدينة' : 'Debit Movements', val: summary.movement_debit_total },
            { label: isAr ? 'حركات دائنة' : 'Credit Movements', val: summary.movement_credit_total },
            { label: isAr ? 'إجمالي الأرصدة المدينة' : 'Total Debit Balances', val: summary.balance_debit_total },
            { label: isAr ? 'إجمالي الأرصدة الدائنة' : 'Total Credit Balances', val: summary.balance_credit_total },
          ].map((card, i) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={i}>
              <Paper sx={{ p: 2, borderRadius: 2, border: '1px solid', borderColor: 'divider', background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,244,248,0.9) 100%)' }}>
                <Typography variant="caption" color="text.secondary" fontWeight="500">{card.label}</Typography>
                <Typography variant="h6" fontWeight="bold" sx={{ mt: 0.5 }}>
                  {formatters.formatCurrency(Number(card.val))}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}

      <TableContainer component={Paper} sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow sx={{ '& th': { backgroundColor: '#f8fafc', fontWeight: 'bold' } }}>
              <TableCell>{isAr ? 'الكود' : 'Code'}</TableCell>
              <TableCell>{isAr ? 'اسم الحساب' : 'Account Name'}</TableCell>
              <TableCell>{isAr ? 'نوع الحساب' : 'Account Type'}</TableCell>
              <TableCell align="right">{isAr ? 'حركة مدين' : 'Movement Debit'}</TableCell>
              <TableCell align="right">{isAr ? 'حركة دائن' : 'Movement Credit'}</TableCell>
              <TableCell align="right">{isAr ? 'رصيد مدين' : 'Balance Debit'}</TableCell>
              <TableCell align="right">{isAr ? 'رصيد دائن' : 'Balance Credit'}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {trialBalanceQuery.isPending ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 8 }}>
                  <CircularProgress size={30} />
                </TableCell>
              </TableRow>
            ) : !data?.rows.length ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
                  {isAr ? 'لا توجد بيانات مطابقة للمحددات.' : 'No data matching selected filters.'}
                </TableCell>
              </TableRow>
            ) : (
              data.rows.map((row) => (
                <TableRow key={row.account_id} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                  <TableCell sx={{ fontFamily: 'monospace', fontWeight: 'bold' }}>{row.account_code}</TableCell>
                  <TableCell>{row.account_name}</TableCell>
                  <TableCell>
                    <Chip label={row.account_type} size="small" variant="outlined" sx={{ fontSize: '0.75rem', height: 20 }} />
                  </TableCell>
                  <TableCell align="right">{formatters.formatDecimal(Number(row.movement_debit))}</TableCell>
                  <TableCell align="right">{formatters.formatDecimal(Number(row.movement_credit))}</TableCell>
                  <TableCell align="right" sx={{ fontWeight: '500', color: Number(row.balance_debit) > 0 ? 'success.main' : 'inherit' }}>
                    {formatters.formatDecimal(Number(row.balance_debit))}
                  </TableCell>
                  <TableCell align="right" sx={{ fontWeight: '500', color: Number(row.balance_credit) > 0 ? 'error.main' : 'inherit' }}>
                    {formatters.formatDecimal(Number(row.balance_credit))}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Stack>
  );
}
