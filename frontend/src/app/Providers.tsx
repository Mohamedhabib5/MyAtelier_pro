import { PropsWithChildren, useMemo } from 'react';

import { CacheProvider } from '@emotion/react';
import { CssBaseline, GlobalStyles, ThemeProvider } from '@mui/material';
import { QueryClientProvider } from '@tanstack/react-query';

import { AuthProvider } from '../features/auth/AuthProvider';
import { LanguageProvider, useLanguage } from '../features/language/LanguageProvider';
import { queryClient } from '../lib/queryClient';
import { getEmotionCache } from '../lib/rtl';
import { buildAppTheme } from './theme';

function DirectionalTheme({ children }: PropsWithChildren) {
  const { direction, textAlign } = useLanguage();
  const cache = useMemo(() => getEmotionCache(direction), [direction]);
  const theme = useMemo(() => buildAppTheme(direction), [direction]);

  return (
    <CacheProvider value={cache}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <GlobalStyles
          styles={{
            html: { direction },
            body: { direction, textAlign },
            '#root': { direction },
          }}
        />
        {children}
      </ThemeProvider>
    </CacheProvider>
  );
}

export function Providers({ children }: PropsWithChildren) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <LanguageProvider>
          <DirectionalTheme>{children}</DirectionalTheme>
        </LanguageProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
