import { createTheme } from '@mui/material/styles';

import type { Direction } from '../lib/language';

export function buildAppTheme(direction: Direction) {
  return createTheme({
    direction,
    palette: {
      mode: 'light',
      primary: {
        main: '#6b2fb3',
      },
      secondary: {
        main: '#d68c45',
      },
    },
    typography: {
      fontFamily: "'Segoe UI', Tahoma, sans-serif",
    },
    shape: {
      borderRadius: 12,
    },
  });
}
