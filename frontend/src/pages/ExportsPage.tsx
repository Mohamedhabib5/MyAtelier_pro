import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined';
import FileDownloadOutlinedIcon from '@mui/icons-material/FileDownloadOutlined';
import PictureAsPdfOutlinedIcon from '@mui/icons-material/PictureAsPdfOutlined';
import { Alert, Box, Button, Stack, Typography } from '@mui/material';

import { SectionCard } from '../components/SectionCard';
import { useAuth } from '../features/auth/AuthProvider';
import { ExportSchedulesSection } from '../features/exports/ExportSchedulesSection';
import { getBookingLinesExportUrl, getBookingsExportUrl, getCustomersExportUrl, getFinancePrintUrl, getPaymentAllocationsExportUrl, getPaymentsExportUrl, getReportsPrintUrl } from '../features/exports/api';
import { EMPTY_VALUE } from '../text/common';
import { useExportsText } from '../text/exports';

function openUrl(url: string) {
  window.open(url, '_blank', 'noopener,noreferrer');
}

function downloadFile(url: string) {
  window.location.assign(url);
}

export function ExportsPage() {
  const { user } = useAuth();
  const exportsText = useExportsText();

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant='h4'>{exportsText.page.title}</Typography>
        <Typography color='text.secondary'>{exportsText.page.description}</Typography>
      </Box>

      <Alert severity='info'>{`${exportsText.page.infoBranchPrefix} ${user?.active_branch_name ?? EMPTY_VALUE}.`}</Alert>
      <Alert severity='info'>{exportsText.page.infoPrint}</Alert>

      <SectionCard title={exportsText.sections.customersTitle} subtitle={exportsText.sections.customersSubtitle}>
        <Button variant='contained' startIcon={<DownloadOutlinedIcon />} onClick={() => downloadFile(getCustomersExportUrl())}>{exportsText.sections.customersButton}</Button>
      </SectionCard>

      <SectionCard title={exportsText.sections.bookingsTitle} subtitle={exportsText.sections.bookingsSubtitle}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          <Button variant='contained' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getBookingsExportUrl())}>{exportsText.sections.bookingsButton}</Button>
          <Button variant='outlined' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getBookingLinesExportUrl())}>{exportsText.sections.bookingLinesButton}</Button>
        </Stack>
      </SectionCard>

      <SectionCard title={exportsText.sections.paymentsTitle} subtitle={exportsText.sections.paymentsSubtitle}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          <Button variant='contained' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getPaymentsExportUrl())}>{exportsText.sections.paymentsButton}</Button>
          <Button variant='outlined' startIcon={<FileDownloadOutlinedIcon />} onClick={() => downloadFile(getPaymentAllocationsExportUrl())}>{exportsText.sections.paymentAllocationsButton}</Button>
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
