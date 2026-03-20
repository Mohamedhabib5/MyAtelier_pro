import ArrowBackOutlinedIcon from '@mui/icons-material/ArrowBackOutlined';
import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined';
import { Box, Button, Divider, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

import { useLanguage } from '../language/LanguageProvider';
import { useExportsText } from '../../text/exports';
import { useLanguageFormatters } from '../../text/common';

type PrintPageFrameProps = {
  title: string;
  subtitle: string;
  branchName?: string | null;
  userName?: string | null;
  children: React.ReactNode;
};

export function PrintPageFrame({ title, subtitle, branchName, userName, children }: PrintPageFrameProps) {
  const { direction } = useLanguage();
  const formatters = useLanguageFormatters();
  const exportsText = useExportsText();

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f5', p: { xs: 2, md: 4 }, direction }}>
      <Stack spacing={3} sx={{ maxWidth: '210mm', mx: 'auto' }}>
        <Stack direction='row' justifyContent='space-between' sx={{ '@media print': { display: 'none' } }}>
          <Button component={RouterLink} to='/exports' startIcon={<ArrowBackOutlinedIcon />}>
            {exportsText.print.back}
          </Button>
          <Button variant='contained' startIcon={<PrintOutlinedIcon />} onClick={() => window.print()}>
            {exportsText.print.print}
          </Button>
        </Stack>

        <Box sx={{ bgcolor: 'common.white', p: { xs: 2, md: 4 }, boxShadow: 1, '@media print': { boxShadow: 'none', p: 0 } }}>
          <Stack spacing={2}>
            <Stack spacing={1}>
              <Typography variant='h4'>{title}</Typography>
              <Typography color='text.secondary'>{subtitle}</Typography>
            </Stack>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} justifyContent='space-between'>
              <Typography variant='body2'>{`${exportsText.print.branch}: ${branchName ?? '—'}`}</Typography>
              <Typography variant='body2'>{`${exportsText.print.user}: ${userName ?? '—'}`}</Typography>
              <Typography variant='body2'>{`${exportsText.print.generatedAt}: ${formatters.formatDateTime(new Date())}`}</Typography>
            </Stack>
            <Divider />
            {children}
          </Stack>
        </Box>
      </Stack>
    </Box>
  );
}
