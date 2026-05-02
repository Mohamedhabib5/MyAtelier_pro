import { useState } from 'react';
import AssessmentOutlinedIcon from '@mui/icons-material/AssessmentOutlined';
import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined';
import PictureAsPdfOutlinedIcon from '@mui/icons-material/PictureAsPdfOutlined';
import { Alert, Box, Button, Divider, Stack, Tab, Tabs, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';

import {
  getBookingsExcelUrl,
  getBookingsExportUrl,
  getPaymentsExcelUrl,
  getPaymentsExportUrl,
  getReportsPrintUrl,
} from '../features/exports/api';
import { useLanguage } from '../features/language/LanguageProvider';
import { BookingStatusGrid } from '../features/reports/BookingStatusGrid';
import { ComprehensiveKpiRow } from '../features/reports/ComprehensiveKpiRow';
import { ReportChartsRow } from '../features/reports/ReportChartsRow';
import { ReportDateRangeFilter } from '../features/reports/ReportDateRangeFilter';
import { TopClientsTable } from '../features/reports/TopClientsTable';
import { DetailedReportGrid } from '../features/reports/DetailedReportGrid';
import { getComprehensiveReport, getDetailedLinesReport } from '../features/reports/api';
import { useReportFilters } from '../features/reports/useReportFilters';
import { useLanguageFormatters } from '../text/common';
import { reportStatusLabel, useReportsText } from '../text/reports';
import { downloadFile } from '../lib/api';

function openUrl(url: string) {
  window.open(url, '_blank', 'noopener,noreferrer');
}

export function ReportsPage() {
  const { language } = useLanguage();
  const formatters = useLanguageFormatters();
  const reportsText = useReportsText();
  const ct = reportsText.comprehensive;

  const {
    dateFrom,
    dateTo,
    activePreset,
    customFrom,
    customTo,
    selectPreset,
    setCustomFrom,
    setCustomTo,
  } = useReportFilters();

  const canFetch = Boolean(dateFrom && dateTo);

  const reportQuery = useQuery({
    queryKey: ['reports', 'comprehensive', dateFrom, dateTo],
    queryFn: () => getComprehensiveReport({ date_from: dateFrom, date_to: dateTo }),
    enabled: canFetch,
    staleTime: 60_000,
  });

  const [currentTab, setCurrentTab] = useState(0);

  const detailedQuery = useQuery({
    queryKey: ['reports', 'detailed', dateFrom, dateTo],
    queryFn: () => getDetailedLinesReport({ date_from: dateFrom, date_to: dateTo }),
    enabled: canFetch && currentTab === 1,
    staleTime: 60_000,
  });

  const report = reportQuery.data;

  const kpis = [
    {
      label: ct.totalCollected,
      value: formatters.formatCurrency(report?.total_collected ?? 0),
      helper: ct.totalCollectedHelper,
      color: '#2e7d32',
    },
    {
      label: ct.totalRecognized,
      value: formatters.formatCurrency(report?.total_recognized ?? 0),
      helper: ct.totalRecognizedHelper,
      color: '#1565c0',
    },
    {
      label: ct.totalRemaining,
      value: formatters.formatCurrency(report?.total_remaining ?? 0),
      helper: ct.totalRemainingHelper,
      color: '#ef6c00',
    },
    {
      label: ct.totalBookings,
      value: formatters.formatCount(report?.total_bookings ?? 0),
      helper: ct.totalBookingsHelper,
      color: '#6a1b9a',
    },
    {
      label: ct.cancellationRate,
      value: `${report?.cancellation_rate ?? 0}%`,
      helper: ct.cancellationRateHelper,
      color: '#c62828',
    },
  ];

  const bookingExportFilters = {
    dateFrom: dateFrom || undefined,
    dateTo: dateTo || undefined,
  };

  const paymentExportFilters = {
    dateFrom: dateFrom || undefined,
    dateTo: dateTo || undefined,
  };

  return (
    <Stack spacing={3}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
        <Box>
          <Typography variant="h4">{ct.pageTitle}</Typography>
          <Typography color="text.secondary">{ct.pageSubtitle}</Typography>
        </Box>
        <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<DownloadOutlinedIcon />}
            onClick={() => downloadFile(getBookingsExportUrl(undefined, bookingExportFilters))}
          >
            {ct.exportCSV}
          </Button>
          <Button
            variant="outlined"
            size="small"
            startIcon={<DownloadOutlinedIcon />}
            onClick={() => downloadFile(getBookingsExcelUrl(undefined, bookingExportFilters))}
          >
            {ct.exportExcel}
          </Button>
          <Button
            variant="outlined"
            size="small"
            startIcon={<PictureAsPdfOutlinedIcon />}
            onClick={() => openUrl(getReportsPrintUrl())}
          >
            {ct.exportPDF}
          </Button>
        </Stack>
      </Stack>

      {/* Date range filter */}
      <ReportDateRangeFilter
        text={ct}
        activePreset={activePreset}
        customFrom={customFrom}
        customTo={customTo}
        dateFrom={dateFrom}
        dateTo={dateTo}
        onSelectPreset={selectPreset}
        onCustomFromChange={setCustomFrom}
        onCustomToChange={setCustomTo}
      />

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={currentTab} onChange={(_, v) => setCurrentTab(v)} aria-label="report tabs">
          <Tab label={ct.tabs?.overview ?? 'Overview'} />
          <Tab label={ct.tabs?.detailed ?? 'Detailed Data'} />
        </Tabs>
      </Box>

      {currentTab === 0 && (
        <Stack spacing={3}>
          {reportQuery.error instanceof Error ? (
            <Alert severity="error">{reportQuery.error.message}</Alert>
          ) : null}

          {/* KPI row */}
          <ComprehensiveKpiRow kpis={kpis} loading={reportQuery.isLoading} />

          <Divider />

          {/* Charts */}
          <ReportChartsRow
            dailyIncome={report?.daily_income ?? []}
            departmentIncome={report?.department_income ?? []}
            topServices={report?.top_services ?? []}
            text={ct}
            formatCurrency={formatters.formatCurrency}
            formatCount={formatters.formatCount}
          />

          <Divider />

          {/* Top clients */}
          <TopClientsTable
            clients={report?.top_clients ?? []}
            text={ct}
            formatCurrency={formatters.formatCurrency}
            formatCount={formatters.formatCount}
          />

          <Divider />

          {/* Booking statuses AG Grid */}
          <BookingStatusGrid
            statuses={report?.booking_status_counts ?? []}
            language={language}
            text={ct}
            statusLabel={(key) => reportStatusLabel(language, key)}
          />
        </Stack>
      )}

      {currentTab === 1 && (
        <Stack spacing={3}>
          {detailedQuery.error instanceof Error ? (
            <Alert severity="error">{detailedQuery.error.message}</Alert>
          ) : null}
          <DetailedReportGrid 
            language={language} 
            rows={detailedQuery.data ?? []} 
            loading={detailedQuery.isLoading} 
          />
        </Stack>
      )}
    </Stack>
  );
}
