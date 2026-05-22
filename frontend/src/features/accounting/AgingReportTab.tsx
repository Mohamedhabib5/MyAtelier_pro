import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Alert, Box, Button, CircularProgress, FormControlLabel,
  Grid, Stack, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, TextField, Typography, Paper,
  ToggleButton, ToggleButtonGroup
} from '@mui/material';
import FileDownloadOutlinedIcon from '@mui/icons-material/FileDownloadOutlined';
import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined';
import AccountCircleOutlinedIcon from '@mui/icons-material/AccountCircleOutlined';

import { getAgingReport, getAgingReportExcelUrl } from './api';
import { useLanguage } from '../language/LanguageProvider';
import { useLanguageFormatters } from '../../text/common';
import { downloadFile } from '../../lib/api';

export function AgingReportTab() {
  const { language } = useLanguage();
  const formatters = useLanguageFormatters();

  const [partyType, setPartyType] = useState<'customer' | 'supplier'>('customer');
  const [asOfDate, setAsOfDate] = useState<string>('');

  const agingQuery = useQuery({
    queryKey: ['accounting', 'aging-report', partyType, asOfDate],
    queryFn: () => getAgingReport({
      partyType,
      asOfDate: asOfDate || undefined,
    }),
  });

  const handleExportExcel = () => {
    const url = getAgingReportExcelUrl({
      partyType,
      asOfDate: asOfDate || undefined,
    });
    void downloadFile(url);
  };

  const handlePrint = () => {
    const searchParams = new URLSearchParams();
    searchParams.set('type', 'aging');
    searchParams.set('partyType', partyType);
    if (asOfDate) searchParams.set('asOfDate', asOfDate);
    window.open(`/print/accounting?${searchParams.toString()}`, '_blank');
  };

  const isAr = language === 'ar';
  const data = agingQuery.data;
  const totalOutstanding = Number(data?.total_receivable_or_payable ?? 0);

  return (
    <Stack spacing={3}>
      <Paper sx={{ p: 2.5, borderRadius: 2, border: '1px solid', borderColor: 'divider', background: 'rgba(255,255,255,0.8)', backdropFilter: 'blur(8px)' }}>
        <Grid container spacing={2.5} alignItems="center">
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography variant="body2" fontWeight="bold" sx={{ mr: 1 }}>
                {isAr ? 'نوع الحساب:' : 'Party Type:'}
              </Typography>
              <ToggleButtonGroup
                value={partyType}
                exclusive
                size="small"
                onChange={(_, val) => val && setPartyType(val)}
                color="primary"
              >
                <ToggleButton value="customer" sx={{ px: 3 }}>
                  {isAr ? 'العملاء (ذمم مدينة)' : 'Customers (AR)'}
                </ToggleButton>
                <ToggleButton value="supplier" sx={{ px: 3 }}>
                  {isAr ? 'الموردين (ذمم دائنة)' : 'Suppliers (AP)'}
                </ToggleButton>
              </ToggleButtonGroup>
            </Stack>
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
                disabled={agingQuery.isPending}
              >
                {isAr ? 'تصدير إكسل' : 'Excel'}
              </Button>
              <Button
                variant="contained"
                color="primary"
                startIcon={<PrintOutlinedIcon />}
                onClick={handlePrint}
                disabled={agingQuery.isPending}
              >
                {isAr ? 'طباعة' : 'Print'}
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </Paper>

      {agingQuery.error && (
        <Alert severity="error">{(agingQuery.error as Error).message}</Alert>
      )}

      {data && (
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 4 }}>
            <Paper
              sx={{
                p: 2.5,
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
                background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.05) 0%, rgba(25, 118, 210, 0.1) 100%)',
                display: 'flex',
                alignItems: 'center',
                gap: 2,
              }}
            >
              <Box sx={{ p: 1.5, borderRadius: '50%', bgcolor: 'primary.main', color: 'common.white', display: 'flex' }}>
                <AccountCircleOutlinedIcon fontSize="medium" />
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary" fontWeight="500">
                  {isAr ? 'إجمالي المبالغ المستحقة القائمة' : 'Total Outstanding Balance'}
                </Typography>
                <Typography variant="h5" fontWeight="bold" color="primary.main" sx={{ mt: 0.5 }}>
                  {formatters.formatCurrency(totalOutstanding)}
                </Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      )}

      <TableContainer component={Paper} sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow sx={{ '& th': { backgroundColor: '#f8fafc', fontWeight: 'bold' } }}>
              <TableCell>{isAr ? 'الطرف / الاسم' : 'Party / Name'}</TableCell>
              <TableCell align="right">{isAr ? 'إجمالي الرصيد المستحق' : 'Total Balance'}</TableCell>
              <TableCell align="right">{isAr ? 'حالي (0-30 يوم)' : 'Current (0-30)'}</TableCell>
              <TableCell align="right">{isAr ? '31 - 60 يوم' : '31 - 60 Days'}</TableCell>
              <TableCell align="right">{isAr ? '61 - 90 يوم' : '61 - 90 Days'}</TableCell>
              <TableCell align="right">{isAr ? 'أكثر من 90 يوم' : 'Over 90 Days'}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {agingQuery.isPending ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 8 }}>
                  <CircularProgress size={30} />
                </TableCell>
              </TableRow>
            ) : !data?.rows.length ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 6 }}>
                  {isAr ? 'لا توجد بيانات مطابقة للمحددات.' : 'No data matching selected filters.'}
                </TableCell>
              </TableRow>
            ) : (
              data.rows.map((row) => (
                <TableRow key={row.party_id} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                  <TableCell sx={{ fontWeight: '500' }}>{row.party_name}</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    {formatters.formatDecimal(Number(row.total_outstanding))}
                  </TableCell>
                  <TableCell align="right">{formatters.formatDecimal(Number(row.buckets['current']))}</TableCell>
                  <TableCell align="right">{formatters.formatDecimal(Number(row.buckets['31-60']))}</TableCell>
                  <TableCell align="right">{formatters.formatDecimal(Number(row.buckets['61-90']))}</TableCell>
                  <TableCell align="right" sx={{ fontWeight: '500', color: Number(row.buckets['91+']) > 0 ? 'error.main' : 'inherit' }}>
                    {formatters.formatDecimal(Number(row.buckets['91+']))}
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
