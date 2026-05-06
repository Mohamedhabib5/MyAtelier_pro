import { createTheme, responsiveFontSizes, ThemeOptions } from '@mui/material/styles';
import type { Direction } from '../lib/language';

export const DEFAULT_PRIMARY = '#FF2D78'; // Pink
export const DEFAULT_SECONDARY = '#00F5D4'; // Teal
export const NEUTRAL_NAVY = '#2B2C3E';

export function buildAppTheme(
  direction: Direction, 
  primaryColor = DEFAULT_PRIMARY, 
  secondaryColor = DEFAULT_SECONDARY,
  mode: 'light' | 'dark' = 'light'
) {
  const isDark = mode === 'dark';
  const themeOptions: ThemeOptions = {
    direction,
    transitions: {
      duration: {
        shortest: 100,
        shorter: 150,
        short: 200,
        standard: 250,
        complex: 300,
        enteringScreen: 225,
        leavingScreen: 195,
      },
      easing: {
        easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
        easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
        easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
        sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
      },
    },
    palette: {
      mode,
      primary: {
        main: primaryColor,
      },
      secondary: {
        main: secondaryColor,
      },
      background: {
        default: 'transparent', // Let index.css mesh gradient show through
        paper: isDark ? 'rgba(30, 31, 46, 0.8)' : 'rgba(255, 255, 255, 0.7)', 
      },
      text: {
        primary: isDark ? '#E2E8F0' : NEUTRAL_NAVY,
        secondary: isDark ? '#94A3B8' : 'rgba(43, 44, 62, 0.7)',
      },
    },
    typography: {
      fontFamily: "'Inter', 'Segoe UI', Tahoma, sans-serif",
      h1: { fontWeight: 700, lineHeight: 1.2 },
      h2: { fontWeight: 700, lineHeight: 1.2 },
      h3: { fontWeight: 600, lineHeight: 1.3 },
      h4: { fontWeight: 600, lineHeight: 1.3 },
      h5: { fontWeight: 600, lineHeight: 1.4 },
      h6: { fontWeight: 600, lineHeight: 1.4 },
      body1: { lineHeight: 1.6 },
      body2: { lineHeight: 1.6 },
    },
    shape: {
      borderRadius: 16, // Slightly more rounded for premium feel
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundColor: isDark ? '#0f0f15' : '#F8F9FA', // Fallback
            WebkitTapHighlightColor: 'transparent', // Better mobile touch feel
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backdropFilter: 'blur(20px) saturate(180%)',
            WebkitBackdropFilter: 'blur(20px) saturate(180%)',
            border: isDark ? '1px solid rgba(255, 255, 255, 0.08)' : '1px solid rgba(255, 255, 255, 0.3)',
            boxShadow: isDark 
              ? '0 4px 24px 0 rgba(0, 0, 0, 0.4)' 
              : '0 8px 32px 0 rgba(31, 38, 135, 0.07)',
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            borderRadius: 50, // Pill shaped
            fontWeight: 600,
            padding: '10px 24px', // Larger touch target
            boxShadow: 'none',
            '&:hover': {
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            },
            '@media (max-width: 600px)': {
              padding: '12px 20px', // Even larger on mobile
            },
          },
        },
      },
      MuiIconButton: {
        styleOverrides: {
          root: {
            padding: 12, // Ensure minimum touch target size
          },
        },
      },
      MuiInputBase: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            '@media (max-width: 600px)': {
              fontSize: '16px', // Prevent iOS zoom on focus
            },
          },
          input: {
            padding: '12px 14px',
          }
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 32, // Extra rounded cards
            padding: '16px',
            border: isDark ? '1px solid rgba(255, 255, 255, 0.05)' : 'none',
            boxShadow: isDark 
              ? '0 4px 20px 0 rgba(0, 0, 0, 0.3)' 
              : '0 4px 12px rgba(0,0,0,0.03)',
            '@media (max-width: 600px)': {
              borderRadius: 24,
              padding: '12px',
            },
          },
        },
      },
      MuiSvgIcon: {
        styleOverrides: {
          root: {
            fontSize: '1.25rem',
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: isDark ? 'rgba(30, 31, 46, 0.6)' : 'rgba(255, 255, 255, 0.6)',
            backdropFilter: 'blur(10px)',
            color: isDark ? '#E2E8F0' : NEUTRAL_NAVY,
            boxShadow: isDark ? '0 4px 20px 0 rgba(0,0,0,0.3)' : '0 4px 20px 0 rgba(0,0,0,0.03)',
            borderBottom: isDark ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(255, 255, 255, 0.3)',
          },
        },
      },
    },
  };

  return responsiveFontSizes(createTheme(themeOptions));
}
