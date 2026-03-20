import { Suspense } from 'react';

import { CircularProgress, Stack } from '@mui/material';
import { RouterProvider } from 'react-router-dom';

import { router } from './app/router';

const loadingFallback = (
  <Stack alignItems='center' justifyContent='center' minHeight='100vh'>
    <CircularProgress />
  </Stack>
);

export default function App() {
  return (
    <Suspense fallback={loadingFallback}>
      <RouterProvider router={router} />
    </Suspense>
  );
}
