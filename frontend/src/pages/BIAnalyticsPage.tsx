import { lazy } from 'react';

const AnalyticsPage = lazy(() => import('../features/analytics/AnalyticsPage'));

export function BIAnalyticsPage() {
  return <AnalyticsPage />;
}
