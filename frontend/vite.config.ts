import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

const proxyTarget = process.env.VITE_API_PROXY_TARGET ?? 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
    },
    proxy: {
      '/attachments': {
        target: proxyTarget,
        changeOrigin: true,
        secure: false,
        ws: true,
      },
      '/api': {
        target: proxyTarget,
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes) => {
            // Ensure Content-Disposition is exposed so the browser can read it
            const existing = proxyRes.headers['access-control-expose-headers'] ?? '';
            if (!String(existing).toLowerCase().includes('content-disposition')) {
              proxyRes.headers['access-control-expose-headers'] = existing
                ? `${existing}, Content-Disposition`
                : 'Content-Disposition';
            }
          });
        },
      },
    },
  },
  build: {
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) {
            return undefined;
          }

          if (id.includes('ag-grid-community') || id.includes('ag-grid-react')) {
            return 'ag-grid-vendor';
          }

          if (
            id.includes('@emotion/cache') ||
            id.includes('@emotion/react') ||
            id.includes('@emotion/styled') ||
            id.includes('@mui/icons-material') ||
            id.includes('@mui/material') ||
            id.includes('@popperjs/core') ||
            id.includes('stylis') ||
            id.includes('stylis-plugin-rtl')
          ) {
            return 'mui-vendor';
          }

          if (
            id.includes('react-dom') ||
            id.includes('react-router') ||
            id.includes('react-router-dom') ||
            id.includes('@tanstack/react-query') ||
            /[\\/]node_modules[\\/]react[\\/]/.test(id)
          ) {
            return 'react-vendor';
          }

          return undefined;
        },
      },
    },
  },
});
