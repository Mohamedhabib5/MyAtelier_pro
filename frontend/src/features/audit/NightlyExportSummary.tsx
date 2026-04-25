import { Alert, Stack, Typography } from '@mui/material';

import type { AuditEventRecord } from './api';

type NightlyExportSummaryProps = {
  language: 'ar' | 'en';
  items: AuditEventRecord[];
};

function text(language: 'ar' | 'en') {
  if (language === 'ar') {
    return {
      title: 'آخر عمليات تصدير التشغيل الليلي',
      empty: 'لا توجد عمليات تصدير مسجلة ضمن النتائج الحالية.',
      by: 'بواسطة',
    };
  }
  return {
    title: 'Latest nightly exports',
    empty: 'No export actions were found in the current results.',
    by: 'by',
  };
}

export function NightlyExportSummary({ language, items }: NightlyExportSummaryProps) {
  const labels = text(language);
  const exportsOnly = items.filter((item) => item.action === 'audit.nightly_ops_exported').slice(0, 3);
  return (
    <Stack spacing={1}>
      <Typography variant='subtitle2'>{labels.title}</Typography>
      {exportsOnly.length === 0 ? (
        <Alert severity='info'>{labels.empty}</Alert>
      ) : (
        exportsOnly.map((item) => (
          <Typography key={item.id} variant='body2' color='text.secondary'>
            {`${item.occurred_at} - ${labels.by} ${item.actor_name ?? item.actor_user_id ?? '-'} - ${item.summary}`}
          </Typography>
        ))
      )}
    </Stack>
  );
}
