import { PropsWithChildren, useMemo } from 'react';

import { CacheProvider } from '@emotion/react';
import { CssBaseline, GlobalStyles, ThemeProvider } from '@mui/material';
import { QueryClientProvider } from '@tanstack/react-query';

import { AuthProvider } from '../features/auth/AuthProvider';
import { LanguageProvider, useLanguage } from '../features/language/LanguageProvider';
import { queryClient } from '../lib/queryClient';
import { getEmotionCache } from '../lib/rtl';
import { buildAppTheme } from './theme';
import { ThemeSettingsProvider, useThemeSettings } from '../features/theme/ThemeSettingsProvider';

function DirectionalTheme({ children }: PropsWithChildren) {
  const { direction, textAlign } = useLanguage();
  const { 
    primaryColor, 
    secondaryColor, 
    bgGradientStart, 
    bgGradientEnd, 
    accentColor 
  } = useThemeSettings();
  
  const safePrimary = primaryColor || '#FF2D78';
  const safeSecondary = secondaryColor || '#00F5D4';
  const safeBgStart = bgGradientStart || '#E2E8F0';
  const safeBgEnd = bgGradientEnd || '#CBD5E1';

  const cache = useMemo(() => getEmotionCache(direction), [direction]);
  const theme = useMemo(() => 
    buildAppTheme(direction, safePrimary, safeSecondary), 
    [direction, safePrimary, safeSecondary]
  );

  return (
    <CacheProvider value={cache}>
      <ThemeProvider theme={theme} key={`${safePrimary}-${safeSecondary}`}>
        <CssBaseline />
        <GlobalStyles
          styles={{
            html: { 
              direction,
              backgroundColor: safeBgEnd, // Base fallback
            },
            body: { 
              direction, 
              textAlign,
              margin: 0,
              minHeight: '100vh',
              backgroundColor: `${safeBgEnd} !important`,
              backgroundImage: `
                radial-gradient(circle at 0% 0%, ${safeBgStart} 0%, ${safeBgStart}00 75%), 
                radial-gradient(circle at 100% 0%, ${safeBgEnd} 0%, ${safeBgEnd}00 75%),
                radial-gradient(circle at 50% 100%, ${safeBgStart} 0%, ${safeBgStart}00 75%)
              !important`,
              backgroundAttachment: 'fixed !important',
              backgroundSize: 'cover !important',
              backgroundRepeat: 'no-repeat !important',
            },
            '#root': { direction },
            // Global Table Customization
            '.ag-theme-material': {
              '--ag-border-radius': '24px',
              '--ag-header-background-color': 'rgba(0,0,0,0.03)',
              '--ag-odd-row-background-color': 'transparent',
              '--ag-header-height': '60px',
              '--ag-row-height': '64px',
              '--ag-font-size': '15px',
              '& .ag-header': {
                borderBottom: '1px solid rgba(0,0,0,0.05)',
                fontWeight: 700,
              },
              '& .ag-row': {
                borderBottom: '1px solid rgba(0,0,0,0.02)',
              },
              '& .ag-root-wrapper': {
                border: 'none !important',
                background: 'transparent !important',
              },
              '@media (max-width: 768px)': {
                '--ag-font-size': '13px',
                '--ag-header-height': '48px',
                '--ag-row-height': '54px',
              }
            },
            // Custom Table Styles
            '.modern-table-container': {
              width: '100%',
              overflowX: 'auto',
              WebkitOverflowScrolling: 'touch',
              borderRadius: '24px',
              '&::-webkit-scrollbar': { height: '4px' },
              '&::-webkit-scrollbar-thumb': { backgroundColor: 'rgba(0,0,0,0.05)', borderRadius: '4px' }
            },
            '.modern-table': {
              width: '100%',
              borderCollapse: 'separate',
              borderSpacing: '0 8px',
              minWidth: { xs: '600px', md: '100%' }, // Ensure content doesn't squash too much
              '& thead th': {
                backgroundColor: 'rgba(0,0,0,0.03)',
                padding: '16px',
                whiteSpace: 'nowrap',
                textAlign: direction === 'rtl' ? 'right' : 'left',
                '&:first-of-type': { borderTopLeftRadius: '24px', borderBottomLeftRadius: '24px' },
                '&:last-of-type': { borderTopRightRadius: '24px', borderBottomRightRadius: '24px' },
              },
              '& tbody tr': {
                transition: 'transform 0.2s',
                '&:hover': { transform: 'scale(1.005)' }
              },
              '& td': {
                padding: '16px',
                borderBottom: '1px solid rgba(0,0,0,0.02)',
                whiteSpace: 'nowrap',
                '@media (max-width: 600px)': {
                  padding: '12px',
                }
              }
            }
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
          <ThemeSettingsProvider>
            <DirectionalTheme>{children}</DirectionalTheme>
          </ThemeSettingsProvider>
        </LanguageProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
