import { Alert, Stack } from '@mui/material';
import { useState } from 'react';

import { useLanguage } from '../../language/LanguageProvider';
import { NightlyStatusSection } from '../NightlyStatusSection';
import { PaymentMethodsSection } from '../PaymentMethodsSection';
import { PeriodLockSection } from '../PeriodLockSection';
import { FiscalPeriodsSection } from '../FiscalPeriodsSection';
import { CompensationTypesSettingsSection } from '../CompensationTypesSettingsSection';

export function GeneralFinancialView() {
  const { language } = useLanguage();
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  return (
    <Stack spacing={3}>
      {message ? <Alert severity='success'>{message}</Alert> : null}
      {error ? <Alert severity='error'>{error}</Alert> : null}

      <PaymentMethodsSection
        language={language}
        onError={(nextError) => {
          setError(nextError);
          if (nextError) setMessage(null);
        }}
        onSuccess={(nextMessage) => {
          setMessage(nextMessage);
          setError(null);
        }}
      />

      <PeriodLockSection
        language={language}
        onError={(nextError) => {
          setError(nextError);
          if (nextError) setMessage(null);
        }}
        onSuccess={(nextMessage) => {
          setMessage(nextMessage);
          setError(null);
        }}
      />

      <FiscalPeriodsSection language={language} />
      
      <CompensationTypesSettingsSection 
        language={language}
        onError={(nextError) => {
          setError(nextError);
          if (nextError) setMessage(null);
        }}
        onSuccess={(nextMessage) => {
          setMessage(nextMessage);
          setError(null);
        }}
      />

      <NightlyStatusSection language={language} />
    </Stack>
  );
}
