import AccessTimeOutlinedIcon from '@mui/icons-material/AccessTimeOutlined';
import OpenInNewOutlinedIcon from '@mui/icons-material/OpenInNewOutlined';
import { Alert, Box, Chip, Link, Stack, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';

import { SectionCard } from '../../components/SectionCard';
import { getLatestNightlySnapshot } from './api';

type NightlyStatusSectionProps = {
  language: 'ar' | 'en';
};

function toText(language: 'ar' | 'en') {
  if (language === 'ar') {
    return {
      title: 'حالة التشغيل الليلي',
      subtitle: 'عرض آخر تقرير فشل تم استقباله من Nightly Full Regression.',
      status: 'الحالة',
      noData: 'لا يوجد تقرير فشل ليلي محفوظ بعد.',
      available: 'متاح',
      unavailable: 'غير متاح',
      repository: 'المستودع',
      ref: 'الفرع/المرجع',
      runId: 'Run ID',
      runAttempt: 'Run Attempt',
      failedAt: 'وقت الفشل',
      reportedAt: 'وقت الاستقبال',
      runUrl: 'رابط التشغيل',
      open: 'فتح',
      resultsTitle: 'نتائج المراحل',
      noResults: 'لا توجد نتائج مراحل مسجلة.',
      loadError: 'تعذر تحميل حالة التشغيل الليلي.',
    };
  }
  return {
    title: 'Nightly status',
    subtitle: 'Shows the latest failure report received from Nightly Full Regression.',
    status: 'Status',
    noData: 'No nightly failure report has been stored yet.',
    available: 'Available',
    unavailable: 'Unavailable',
    repository: 'Repository',
    ref: 'Ref',
    runId: 'Run ID',
    runAttempt: 'Run Attempt',
    failedAt: 'Failed at',
    reportedAt: 'Reported at',
    runUrl: 'Run URL',
    open: 'Open',
    resultsTitle: 'Stage results',
    noResults: 'No stage results were reported.',
    loadError: 'Failed to load nightly status.',
  };
}

export function NightlyStatusSection({ language }: NightlyStatusSectionProps) {
  const text = toText(language);
  const query = useQuery({
    queryKey: ['settings', 'ops-nightly-latest'],
    queryFn: getLatestNightlySnapshot,
    staleTime: 30000,
  });

  return (
    <SectionCard title={text.title} subtitle={text.subtitle}>
      <Stack spacing={2}>
        {query.isError ? <Alert severity='error'>{text.loadError}</Alert> : null}
        <Stack direction='row' spacing={1} alignItems='center'>
          <AccessTimeOutlinedIcon fontSize='small' color='action' />
          <Typography variant='body2' color='text.secondary'>
            {text.status}
          </Typography>
          <Chip size='small' color={query.data?.available ? 'warning' : 'default'} label={query.data?.available ? text.available : text.unavailable} />
        </Stack>
        {!query.data?.available ? (
          <Typography variant='body2' color='text.secondary'>
            {text.noData}
          </Typography>
        ) : (
          <Stack spacing={1.5}>
            <InfoRow label={text.repository} value={query.data.repository} />
            <InfoRow label={text.ref} value={query.data.ref} />
            <InfoRow label={text.runId} value={query.data.run_id} />
            <InfoRow label={text.runAttempt} value={query.data.run_attempt} />
            <InfoRow label={text.failedAt} value={query.data.failed_at_utc} />
            <InfoRow label={text.reportedAt} value={query.data.reported_at} />
            <Stack direction='row' spacing={1} alignItems='center'>
              <Typography variant='body2' color='text.secondary'>
                {text.runUrl}:
              </Typography>
              {query.data.run_url ? (
                <Link href={query.data.run_url} target='_blank' rel='noreferrer' underline='hover' sx={{ display: 'inline-flex', alignItems: 'center', gap: 0.5 }}>
                  {text.open}
                  <OpenInNewOutlinedIcon fontSize='inherit' />
                </Link>
              ) : (
                <Typography variant='body2'>-</Typography>
              )}
            </Stack>
            <Box>
              <Typography variant='subtitle2'>{text.resultsTitle}</Typography>
              {Object.keys(query.data.results ?? {}).length === 0 ? (
                <Typography variant='body2' color='text.secondary'>
                  {text.noResults}
                </Typography>
              ) : (
                <Stack direction='row' spacing={1} flexWrap='wrap' useFlexGap sx={{ mt: 1 }}>
                  {Object.entries(query.data.results).map(([key, value]) => (
                    <Chip key={key} size='small' label={`${key}: ${value}`} />
                  ))}
                </Stack>
              )}
            </Box>
          </Stack>
        )}
      </Stack>
    </SectionCard>
  );
}

type InfoRowProps = {
  label: string;
  value: string | null;
};

function InfoRow({ label, value }: InfoRowProps) {
  return (
    <Stack direction='row' spacing={1} alignItems='center'>
      <Typography variant='body2' color='text.secondary'>
        {label}:
      </Typography>
      <Typography variant='body2'>{value || '-'}</Typography>
    </Stack>
  );
}
