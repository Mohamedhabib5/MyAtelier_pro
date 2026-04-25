import { Box, CircularProgress, Typography } from '@mui/material';
import { useMemo } from 'react';

import { SectionCard } from '../../components/SectionCard';
import { useLanguage } from '../language/LanguageProvider';
import { usePaymentsText } from '../../text/payments';
import type { PaymentDocumentSummaryRecord } from './api';

function buildNumberFormatter(locale: string) {
  return new Intl.NumberFormat(locale);
}

function buildMoneyFormatter(locale: string) {
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export function PaymentsOverviewSection({ rows, total, loading }: { rows: PaymentDocumentSummaryRecord[]; total: number; loading: boolean }) {
  const { locale } = useLanguage();
  const paymentsText = usePaymentsText();
  const numberFormatter = useMemo(() => buildNumberFormatter(locale), [locale]);
  const moneyFormatter = useMemo(() => buildMoneyFormatter(locale), [locale]);

  const metrics = useMemo(() => {
    const activeRows = rows.filter((row) => row.status === 'active');
    const voidedRows = rows.filter((row) => row.status === 'voided');
    const activeTotal = activeRows.reduce((sum, row) => sum + row.total_amount, 0);
    const voidedTotal = voidedRows.reduce((sum, row) => sum + row.total_amount, 0);

    return [
      {
        id: 'documents-total',
        label: paymentsText.overview.totalDocuments,
        value: numberFormatter.format(total),
        helper: paymentsText.overview.totalDocumentsHelper,
      },
      {
        id: 'documents-active',
        label: paymentsText.overview.activeDocuments,
        value: numberFormatter.format(activeRows.length),
        helper: paymentsText.overview.currentPageHelper,
      },
      {
        id: 'amount-active',
        label: paymentsText.overview.activeAmount,
        value: moneyFormatter.format(activeTotal),
        helper: paymentsText.overview.currentPageHelper,
      },
      {
        id: 'amount-voided',
        label: paymentsText.overview.voidedAmount,
        value: moneyFormatter.format(voidedTotal),
        helper: paymentsText.overview.currentPageHelper,
      },
    ];
  }, [moneyFormatter, numberFormatter, paymentsText.overview, rows, total]);

  return (
    <SectionCard title={paymentsText.overview.title} subtitle={paymentsText.overview.subtitle}>
      {loading ? (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
          <CircularProgress size={18} />
          <Typography color='text.secondary'>{paymentsText.overview.loading}</Typography>
        </Box>
      ) : (
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, minmax(0, 1fr))', xl: 'repeat(4, minmax(0, 1fr))' },
            gap: 1.5,
          }}
        >
          {metrics.map((metric) => (
            <Box key={metric.id} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2, p: 1.75, bgcolor: 'background.paper' }}>
              <Typography variant='body2' color='text.secondary'>
                {metric.label}
              </Typography>
              <Typography variant='h5' sx={{ mt: 0.5 }}>
                {metric.value}
              </Typography>
              <Typography variant='caption' color='text.secondary'>
                {metric.helper}
              </Typography>
            </Box>
          ))}
        </Box>
      )}
    </SectionCard>
  );
}
