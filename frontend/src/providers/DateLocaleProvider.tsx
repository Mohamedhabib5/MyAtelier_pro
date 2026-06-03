import { PropsWithChildren } from 'react';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useLanguage } from '../features/language/LanguageProvider';
import { ar, enUS } from 'date-fns/locale';

export function DateLocaleProvider({ children }: PropsWithChildren) {
  const { language } = useLanguage();
  const locale = language === 'ar' ? ar : enUS;

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={locale}>
      {children}
    </LocalizationProvider>
  );
}
