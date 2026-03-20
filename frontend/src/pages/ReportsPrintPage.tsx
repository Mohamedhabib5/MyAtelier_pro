import { Alert, Grid, Stack } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';

import { SectionCard } from '../components/SectionCard';
import { useAuth } from '../features/auth/AuthProvider';
import { MetricCard } from '../features/dashboard/MetricCard';
import { MetricsList } from '../features/dashboard/MetricsList';
import { useLanguage } from '../features/language/LanguageProvider';
import { PrintPageFrame } from '../features/exports/PrintPageFrame';
import { UpcomingBookingsTable } from '../features/reports/UpcomingBookingsTable';
import { getReportsOverview } from '../features/reports/api';
import { reportStatusLabel, useReportsText } from '../text/reports';
import { useLanguageFormatters } from '../text/common';

export function ReportsPrintPage() {
  const { user } = useAuth();
  const { language } = useLanguage();
  const reportsText = useReportsText();
  const formatters = useLanguageFormatters();
  const [params] = useSearchParams();
  const branchId = params.get('branchId');
  const branchName = params.get('branchName') ?? user?.active_branch_name;
  const reportsQuery = useQuery({ queryKey: ['reports', 'overview', branchId], queryFn: () => getReportsOverview(branchId) });
  const report = reportsQuery.data;
  const bookingStatuses = (report?.booking_status_counts ?? []).map((item) => ({ label: reportStatusLabel(language, item.key), value: `${formatters.formatCount(item.count)} ${reportsText.subtitles.itemsSuffix}` }));
  const paymentMix = (report?.payment_type_totals ?? []).map((item) => ({ label: reportStatusLabel(language, item.key), value: formatters.formatCurrency(item.value) }));
  const dressStatuses = (report?.dress_status_counts ?? []).map((item) => ({ label: reportStatusLabel(language, item.key), value: `${formatters.formatCount(item.count)} ${reportsText.subtitles.itemsSuffix}` }));
  const departmentServices = (report?.department_service_counts ?? []).map((item) => ({ label: item.label, value: `${formatters.formatCount(item.count)} ${reportsText.subtitles.servicesCountSuffix}` }));

  return (
    <PrintPageFrame title={reportsText.print.title} subtitle={reportsText.print.subtitle} branchName={branchName} userName={user?.full_name}>
      <Stack spacing={3}>
        {reportsQuery.error instanceof Error ? <Alert severity='error'>{reportsQuery.error.message}</Alert> : null}
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 3 }}><MetricCard label={reportsText.metrics.activeCustomers} value={formatters.formatCount(report?.active_customers ?? 0)} helper={reportsText.helpers.activeCustomers} /></Grid>
          <Grid size={{ xs: 12, md: 3 }}><MetricCard label={reportsText.metrics.activeServices} value={formatters.formatCount(report?.active_services ?? 0)} helper={reportsText.helpers.activeServices} /></Grid>
          <Grid size={{ xs: 12, md: 3 }}><MetricCard label={reportsText.metrics.availableDresses} value={formatters.formatCount(report?.available_dresses ?? 0)} helper={reportsText.helpers.availableDresses} /></Grid>
          <Grid size={{ xs: 12, md: 3 }}><MetricCard label={reportsText.metrics.upcomingBookings} value={formatters.formatCount(report?.upcoming_bookings ?? 0)} helper={reportsText.helpers.upcomingBookings} /></Grid>
        </Grid>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 3 }}><SectionCard title={reportsText.sections.bookingStatuses}><MetricsList items={bookingStatuses} emptyLabel={reportsText.print.noData} /></SectionCard></Grid>
          <Grid size={{ xs: 12, md: 3 }}><SectionCard title={reportsText.sections.paymentMix}><MetricsList items={paymentMix} emptyLabel={reportsText.print.noData} /></SectionCard></Grid>
          <Grid size={{ xs: 12, md: 3 }}><SectionCard title={reportsText.sections.dressStatuses}><MetricsList items={dressStatuses} emptyLabel={reportsText.print.noData} /></SectionCard></Grid>
          <Grid size={{ xs: 12, md: 3 }}><SectionCard title={reportsText.sections.departmentServices}><MetricsList items={departmentServices} emptyLabel={reportsText.print.noData} /></SectionCard></Grid>
        </Grid>
        <SectionCard title={reportsText.sections.upcoming}><UpcomingBookingsTable items={report?.upcoming_booking_items ?? []} /></SectionCard>
      </Stack>
    </PrintPageFrame>
  );
}
