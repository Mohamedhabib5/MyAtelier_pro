import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined';
import FileDownloadOutlinedIcon from '@mui/icons-material/FileDownloadOutlined';
import PictureAsPdfOutlinedIcon from '@mui/icons-material/PictureAsPdfOutlined';
import { Alert, Box, Button, MenuItem, Stack, TextField, Typography } from '@mui/material';
import { useState } from 'react';

import { SectionCard } from '../components/SectionCard';
import { useAuth } from '../features/auth/AuthProvider';
import {
  getBookingLinesExcelUrl,
  getBookingLinesExportUrl,
  getBookingsExcelUrl,
  getBookingsExportUrl,
  getCustomersExcelUrl,
  getCustomersExportUrl,
  getCustodyExcelUrl,
  getCustodyExportUrl,
  getFinancePrintUrl,
  getPaymentAllocationsExcelUrl,
  getPaymentAllocationsExportUrl,
  getPaymentsExcelUrl,
  getPaymentsExportUrl,
  getReportsPrintUrl,
  type BookingExportFilters,
  type PaymentExportFilters,
} from '../features/exports/api';
import { downloadFile } from '../lib/api';
import { useLanguage } from '../features/language/LanguageProvider';
import { ExportSchedulesSection } from '../features/exports/ExportSchedulesSection';
import { EMPTY_VALUE } from '../text/common';
import { useExportsText } from '../text/exports';

function openUrl(url: string) {
  window.open(url, '_blank', 'noopener,noreferrer');
}

export function ExportsPage() {
  const { user } = useAuth();
  const { language } = useLanguage();
  const exportsText = useExportsText();
  const [bookingFilters, setBookingFilters] = useState<BookingExportFilters>({ sortBy: 'booking_date', sortDir: 'desc' });
  const [paymentFilters, setPaymentFilters] = useState<PaymentExportFilters>({ sortBy: 'payment_date', sortDir: 'desc' });
  const custodyTitle = language === 'ar' ? 'تصدير الحيازة' : 'Custody export';
  const custodySubtitle = language === 'ar' ? 'تصدير حالات الحيازة الحالية في الفرع النشط.' : 'Export custody cases for the active branch.';
  const custodyButton = language === 'ar' ? 'تنزيل الحيازة' : 'Download custody';
  const filterHint =
    language === 'ar'
      ? 'يمكنك تحديد نفس فلاتر الجداول هنا لتصدير العرض الحالي بدقة.'
      : 'Set table-like filters here to export the exact current view.';

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant='h4'>{exportsText.page.title}</Typography>
        <Typography color='text.secondary'>{exportsText.page.description}</Typography>
      </Box>

      <Alert severity='info'>{`${exportsText.page.infoBranchPrefix} ${user?.active_branch_name ?? EMPTY_VALUE}.`}</Alert>
      <Alert severity='info'>{exportsText.page.infoPrint}</Alert>
      <Alert severity='success'>{filterHint}</Alert>

      <SectionCard title={exportsText.sections.customersTitle} subtitle={exportsText.sections.customersSubtitle}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          <Button variant='contained' startIcon={<DownloadOutlinedIcon />} onClick={() => downloadFile(getCustomersExportUrl())}>{`${exportsText.sections.customersButton} CSV`}</Button>
          <Button variant='outlined' startIcon={<DownloadOutlinedIcon />} onClick={() => downloadFile(getCustomersExcelUrl())}>{`${exportsText.sections.customersButton} Excel`}</Button>
        </Stack>
      </SectionCard>

      <SectionCard title={exportsText.sections.bookingsTitle} subtitle={exportsText.sections.bookingsSubtitle}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5} sx={{ mb: 2 }}>
          <TextField
            size='small'
            label={language === 'ar' ? 'بحث' : 'Search'}
            value={bookingFilters.search ?? ''}
            onChange={(event) => setBookingFilters((prev) => ({ ...prev, search: event.target.value || undefined }))}
          />
          <TextField
            select
            size='small'
            label={language === 'ar' ? 'الحالة' : 'Status'}
            value={bookingFilters.status ?? ''}
            onChange={(event) => setBookingFilters((prev) => ({ ...prev, status: event.target.value || undefined }))}
            sx={{ minWidth: 180 }}
          >
            <MenuItem value=''>{language === 'ar' ? 'كل الحالات' : 'All statuses'}</MenuItem>
            <MenuItem value='draft'>{language === 'ar' ? 'مسودة' : 'Draft'}</MenuItem>
            <MenuItem value='confirmed'>{language === 'ar' ? 'مؤكد' : 'Confirmed'}</MenuItem>
            <MenuItem value='completed'>{language === 'ar' ? 'مكتمل' : 'Completed'}</MenuItem>
            <MenuItem value='cancelled'>{language === 'ar' ? 'ملغي' : 'Cancelled'}</MenuItem>
          </TextField>
          <TextField
            type='date'
            size='small'
            label={language === 'ar' ? 'من تاريخ' : 'From'}
            value={bookingFilters.dateFrom ?? ''}
            onChange={(event) => setBookingFilters((prev) => ({ ...prev, dateFrom: event.target.value || undefined }))}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            type='date'
            size='small'
            label={language === 'ar' ? 'إلى تاريخ' : 'To'}
            value={bookingFilters.dateTo ?? ''}
            onChange={(event) => setBookingFilters((prev) => ({ ...prev, dateTo: event.target.value || undefined }))}
            InputLabelProps={{ shrink: true }}
          />
        </Stack>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          <Button variant='contained' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getBookingsExportUrl(undefined, bookingFilters))}>{`${exportsText.sections.bookingsButton} CSV`}</Button>
          <Button variant='outlined' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getBookingsExcelUrl(undefined, bookingFilters))}>{`${exportsText.sections.bookingsButton} Excel`}</Button>
          <Button variant='outlined' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getBookingLinesExportUrl(undefined, bookingFilters))}>{`${exportsText.sections.bookingLinesButton} CSV`}</Button>
          <Button variant='outlined' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getBookingLinesExcelUrl(undefined, bookingFilters))}>{`${exportsText.sections.bookingLinesButton} Excel`}</Button>
        </Stack>
      </SectionCard>

      <SectionCard title={exportsText.sections.paymentsTitle} subtitle={exportsText.sections.paymentsSubtitle}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5} sx={{ mb: 2 }}>
          <TextField
            size='small'
            label={language === 'ar' ? 'بحث' : 'Search'}
            value={paymentFilters.search ?? ''}
            onChange={(event) => setPaymentFilters((prev) => ({ ...prev, search: event.target.value || undefined }))}
          />
          <TextField
            select
            size='small'
            label={language === 'ar' ? 'الحالة' : 'Status'}
            value={paymentFilters.status ?? ''}
            onChange={(event) => setPaymentFilters((prev) => ({ ...prev, status: event.target.value || undefined }))}
            sx={{ minWidth: 160 }}
          >
            <MenuItem value=''>{language === 'ar' ? 'كل الحالات' : 'All statuses'}</MenuItem>
            <MenuItem value='active'>{language === 'ar' ? 'نشط' : 'Active'}</MenuItem>
            <MenuItem value='voided'>{language === 'ar' ? 'ملغي' : 'Voided'}</MenuItem>
          </TextField>
          <TextField
            select
            size='small'
            label={language === 'ar' ? 'النوع' : 'Kind'}
            value={paymentFilters.documentKind ?? ''}
            onChange={(event) => setPaymentFilters((prev) => ({ ...prev, documentKind: event.target.value || undefined }))}
            sx={{ minWidth: 160 }}
          >
            <MenuItem value=''>{language === 'ar' ? 'كل الأنواع' : 'All kinds'}</MenuItem>
            <MenuItem value='collection'>{language === 'ar' ? 'تحصيل' : 'Collection'}</MenuItem>
            <MenuItem value='refund'>{language === 'ar' ? 'استرداد' : 'Refund'}</MenuItem>
          </TextField>
          <TextField
            type='date'
            size='small'
            label={language === 'ar' ? 'من تاريخ' : 'From'}
            value={paymentFilters.dateFrom ?? ''}
            onChange={(event) => setPaymentFilters((prev) => ({ ...prev, dateFrom: event.target.value || undefined }))}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            type='date'
            size='small'
            label={language === 'ar' ? 'إلى تاريخ' : 'To'}
            value={paymentFilters.dateTo ?? ''}
            onChange={(event) => setPaymentFilters((prev) => ({ ...prev, dateTo: event.target.value || undefined }))}
            InputLabelProps={{ shrink: true }}
          />
        </Stack>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          <Button variant='contained' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getPaymentsExportUrl(undefined, paymentFilters))}>{`${exportsText.sections.paymentsButton} CSV`}</Button>
          <Button variant='outlined' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getPaymentsExcelUrl(undefined, paymentFilters))}>{`${exportsText.sections.paymentsButton} Excel`}</Button>
          <Button variant='outlined' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getPaymentAllocationsExportUrl(undefined, paymentFilters))}>{`${exportsText.sections.paymentAllocationsButton} CSV`}</Button>
          <Button variant='outlined' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getPaymentAllocationsExcelUrl(undefined, paymentFilters))}>{`${exportsText.sections.paymentAllocationsButton} Excel`}</Button>
        </Stack>
      </SectionCard>

      <SectionCard title={custodyTitle} subtitle={custodySubtitle}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          <Button variant='contained' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getCustodyExportUrl())}>{`${custodyButton} CSV`}</Button>
          <Button variant='outlined' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getCustodyExcelUrl())}>{`${custodyButton} Excel`}</Button>
        </Stack>
      </SectionCard>

      <SectionCard title={exportsText.sections.financeTitle} subtitle={exportsText.sections.financeSubtitle}>
        <Button variant='outlined' startIcon={<PictureAsPdfOutlinedIcon />} onClick={() => openUrl(getFinancePrintUrl())}>{exportsText.sections.financeButton}</Button>
      </SectionCard>

      <SectionCard title={exportsText.sections.reportsTitle} subtitle={exportsText.sections.reportsSubtitle}>
        <Button variant='outlined' startIcon={<PictureAsPdfOutlinedIcon />} onClick={() => openUrl(getReportsPrintUrl())}>{exportsText.sections.reportsButton}</Button>
      </SectionCard>

      <ExportSchedulesSection activeBranchName={user?.active_branch_name} />
    </Stack>
  );
}
