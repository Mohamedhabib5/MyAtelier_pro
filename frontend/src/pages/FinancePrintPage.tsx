import { Alert, Grid, Stack } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';

import { SectionCard } from '../components/SectionCard';
import { useAuth } from '../features/auth/AuthProvider';
import { MetricCard } from '../features/dashboard/MetricCard';
import { MetricsList } from '../features/dashboard/MetricsList';
import { PrintPageFrame } from '../features/exports/PrintPageFrame';
import { getFinanceDashboard } from '../features/dashboard/api';
import { useDashboardText } from '../text/dashboard';
import { useLanguageFormatters } from '../text/common';

export function FinancePrintPage() {
  const { user } = useAuth();
  const dashboardText = useDashboardText();
  const formatters = useLanguageFormatters();
  const [params] = useSearchParams();
  const branchId = params.get('branchId');
  const branchName = params.get('branchName') ?? user?.active_branch_name;
  const dashboardQuery = useQuery({ queryKey: ['dashboard', 'finance', branchId], queryFn: () => getFinanceDashboard(branchId) });
  const dashboard = dashboardQuery.data;
  const dailyIncome = (dashboard?.daily_income ?? []).map((item) => ({ label: item.label, value: formatters.formatCurrency(item.value) }));
  const departmentIncome = (dashboard?.department_income ?? []).map((item) => ({ label: item.label, value: formatters.formatCurrency(item.value) }));
  const topServices = (dashboard?.top_services ?? []).map((item) => ({ label: item.label, value: `${formatters.formatCount(item.count)} ${dashboardText.subtitles.bookingsSuffix}` }));

  return (
    <PrintPageFrame title={dashboardText.print.title} subtitle={dashboardText.print.subtitle} branchName={branchName} userName={user?.full_name}>
      <Stack spacing={3}>
        {dashboardQuery.error instanceof Error ? <Alert severity='error'>{dashboardQuery.error.message}</Alert> : null}
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 4 }}><MetricCard label={dashboardText.metrics.totalIncome} value={formatters.formatCurrency(dashboard?.total_income ?? 0)} helper={dashboardText.helpers.totalIncome} /></Grid>
          <Grid size={{ xs: 12, md: 4 }}><MetricCard label={dashboardText.metrics.totalRemaining} value={formatters.formatCurrency(dashboard?.total_remaining ?? 0)} helper={dashboardText.helpers.totalRemaining} /></Grid>
          <Grid size={{ xs: 12, md: 4 }}><MetricCard label={dashboardText.metrics.totalBookings} value={formatters.formatCount(dashboard?.total_bookings ?? 0)} helper={dashboardText.helpers.totalBookings} /></Grid>
        </Grid>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 4 }}><SectionCard title={dashboardText.sections.dailyIncome}><MetricsList items={dailyIncome} emptyLabel={dashboardText.subtitles.empty} /></SectionCard></Grid>
          <Grid size={{ xs: 12, md: 4 }}><SectionCard title={dashboardText.sections.departmentIncome}><MetricsList items={departmentIncome} emptyLabel={dashboardText.subtitles.empty} /></SectionCard></Grid>
          <Grid size={{ xs: 12, md: 4 }}><SectionCard title={dashboardText.sections.topServices}><MetricsList items={topServices} emptyLabel={dashboardText.subtitles.empty} /></SectionCard></Grid>
        </Grid>
      </Stack>
    </PrintPageFrame>
  );
}
