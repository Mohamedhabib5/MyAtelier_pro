import AssessmentOutlinedIcon from '@mui/icons-material/AssessmentOutlined';
import { Alert, Box, Button, Grid, Stack, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';

import { SectionCard } from '../components/SectionCard';
import { MetricCard } from '../features/dashboard/MetricCard';
import { MetricsList } from '../features/dashboard/MetricsList';
import { useLanguage } from '../features/language/LanguageProvider';
import { UpcomingBookingsTable } from '../features/reports/UpcomingBookingsTable';
import { getReportsOverview } from '../features/reports/api';
import { reportStatusLabel, useReportsText } from '../text/reports';
import { useLanguageFormatters } from '../text/common';

export function ReportsPage() {
  const { language } = useLanguage();
  const formatters = useLanguageFormatters();
  const reportsText = useReportsText();
  const reportsQuery = useQuery({ queryKey: ['reports', 'overview'], queryFn: () => getReportsOverview() });
  const report = reportsQuery.data;
  const bookingStatuses = (report?.booking_status_counts ?? []).map((item) => ({ label: reportStatusLabel(language, item.key), value: `${formatters.formatCount(item.count)} ${reportsText.subtitles.itemsSuffix}` }));
  const paymentMix = (report?.payment_type_totals ?? []).map((item) => ({ label: reportStatusLabel(language, item.key), value: formatters.formatCurrency(item.value) }));
  const dressStatuses = (report?.dress_status_counts ?? []).map((item) => ({ label: reportStatusLabel(language, item.key), value: `${formatters.formatCount(item.count)} ${reportsText.subtitles.itemsSuffix}` }));
  const departmentServices = (report?.department_service_counts ?? []).map((item) => ({ label: item.label, value: `${formatters.formatCount(item.count)} ${reportsText.subtitles.servicesCountSuffix}` }));

  return (
    <Stack spacing={3}>
      <Stack direction='row' justifyContent='space-between' alignItems='center'>
        <Box>
          <Typography variant='h4'>{reportsText.page.title}</Typography>
          <Typography color='text.secondary'>{reportsText.page.description}</Typography>
        </Box>
        <Button variant='outlined' startIcon={<AssessmentOutlinedIcon />} disabled>{reportsText.page.button}</Button>
      </Stack>

      {reportsQuery.error instanceof Error ? <Alert severity='error'>{reportsQuery.error.message}</Alert> : null}

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 3 }}><MetricCard label={reportsText.metrics.activeCustomers} value={formatters.formatCount(report?.active_customers ?? 0)} helper={reportsText.helpers.activeCustomers} /></Grid>
        <Grid size={{ xs: 12, md: 3 }}><MetricCard label={reportsText.metrics.activeServices} value={formatters.formatCount(report?.active_services ?? 0)} helper={reportsText.helpers.activeServices} /></Grid>
        <Grid size={{ xs: 12, md: 3 }}><MetricCard label={reportsText.metrics.availableDresses} value={formatters.formatCount(report?.available_dresses ?? 0)} helper={reportsText.helpers.availableDresses} /></Grid>
        <Grid size={{ xs: 12, md: 3 }}><MetricCard label={reportsText.metrics.upcomingBookings} value={formatters.formatCount(report?.upcoming_bookings ?? 0)} helper={reportsText.helpers.upcomingBookings} /></Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 3 }}><SectionCard title={reportsText.sections.bookingStatuses} subtitle={reportsText.subtitles.bookingStatuses}><MetricsList items={bookingStatuses} emptyLabel={reportsText.subtitles.empty} /></SectionCard></Grid>
        <Grid size={{ xs: 12, md: 3 }}><SectionCard title={reportsText.sections.paymentMix} subtitle={reportsText.subtitles.paymentMix}><MetricsList items={paymentMix} emptyLabel={reportsText.subtitles.empty} /></SectionCard></Grid>
        <Grid size={{ xs: 12, md: 3 }}><SectionCard title={reportsText.sections.dressStatuses} subtitle={reportsText.subtitles.dressStatuses}><MetricsList items={dressStatuses} emptyLabel={reportsText.subtitles.empty} /></SectionCard></Grid>
        <Grid size={{ xs: 12, md: 3 }}><SectionCard title={reportsText.sections.departmentServices} subtitle={reportsText.subtitles.departmentServices}><MetricsList items={departmentServices} emptyLabel={reportsText.subtitles.empty} /></SectionCard></Grid>
      </Grid>

      <SectionCard title={reportsText.sections.upcoming} subtitle={reportsText.subtitles.upcoming}>
        <UpcomingBookingsTable items={report?.upcoming_booking_items ?? []} />
      </SectionCard>
    </Stack>
  );
}
