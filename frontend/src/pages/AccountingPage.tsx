import { Alert, Box, Chip, FormControlLabel, Grid, Stack, Switch, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import { SectionCard } from '../components/SectionCard';
import { getChartOfAccounts, getJournalEntries, getTrialBalance } from '../features/accounting/api';
import { useAccountingText } from '../text/accounting';
import { useLanguageFormatters } from '../text/common';

export function AccountingPage() {
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
            <Table size='small'>
              <TableHead>
                <TableRow>
                  <TableCell>{accountingText.chart.code}</TableCell>
                  <TableCell>{accountingText.chart.account}</TableCell>
                  <TableCell>{accountingText.chart.type}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(chartQuery.data ?? []).map((account) => (
                  <TableRow key={account.id}>
                    <TableCell>{account.code}</TableCell>
                    <TableCell>{account.name}</TableCell>
                    <TableCell>{account.account_type}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </SectionCard>
        </Grid>

        <Grid size={{ xs: 12, md: 7 }}>
          <SectionCard title={accountingText.journals.title} subtitle={accountingText.journals.subtitle}>
            <Table size='small'>
              <TableHead>
                <TableRow>
                  <TableCell>{accountingText.journals.number}</TableCell>
                  <TableCell>{accountingText.journals.date}</TableCell>
                  <TableCell>{accountingText.journals.status}</TableCell>
                  <TableCell>{accountingText.journals.reference}</TableCell>
                  <TableCell>{accountingText.journals.debit}</TableCell>
                  <TableCell>{accountingText.journals.credit}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(journalsQuery.data ?? []).map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell>{entry.entry_number}</TableCell>
                    <TableCell>{entry.entry_date}</TableCell>
                    <TableCell><Chip label={entry.status} size='small' /></TableCell>
                    <TableCell>{entry.reference ?? '-'}</TableCell>
                    <TableCell>{formatters.formatDecimal(Number(entry.total_debit))}</TableCell>
                    <TableCell>{formatters.formatDecimal(Number(entry.total_credit))}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
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

          <Table size='small'>
            <TableHead>
              <TableRow>
                <TableCell>{accountingText.trialBalance.code}</TableCell>
                <TableCell>{accountingText.trialBalance.account}</TableCell>
                <TableCell>{accountingText.trialBalance.accountType}</TableCell>
                <TableCell>{accountingText.trialBalance.movementDebit}</TableCell>
                <TableCell>{accountingText.trialBalance.movementCredit}</TableCell>
                <TableCell>{accountingText.trialBalance.balanceDebit}</TableCell>
                <TableCell>{accountingText.trialBalance.balanceCredit}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(trialBalanceQuery.data?.rows ?? []).map((row) => (
                <TableRow key={row.account_id}>
                  <TableCell>{row.account_code}</TableCell>
                  <TableCell>{row.account_name}</TableCell>
                  <TableCell>{row.account_type}</TableCell>
                  <TableCell>{formatters.formatDecimal(Number(row.movement_debit))}</TableCell>
                  <TableCell>{formatters.formatDecimal(Number(row.movement_credit))}</TableCell>
                  <TableCell>{formatters.formatDecimal(Number(row.balance_debit))}</TableCell>
                  <TableCell>{formatters.formatDecimal(Number(row.balance_credit))}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Stack>
      </SectionCard>
    </Stack>
  );
}
