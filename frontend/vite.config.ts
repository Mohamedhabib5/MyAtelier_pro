import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

const proxyTarget = process.env.VITE_API_PROXY_TARGET ?? 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: proxyTarget,
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router', 'react-router-dom', '@tanstack/react-query'],
          'mui-vendor': [
            '@emotion/cache',
            '@emotion/react',
            '@emotion/styled',
            '@mui/icons-material',
            '@mui/material',
            '@popperjs/core',
            'stylis',
            'stylis-plugin-rtl',
          ],
        },
      },
    },
  },
});
