import { lazy } from 'react';

import { createBrowserRouter, Navigate } from 'react-router-dom';

import { ProtectedRoute } from '../components/ProtectedRoute';

const DashboardShell = lazy(() => import('../pages/DashboardShell').then((module) => ({ default: module.DashboardShell })));
const LoginPage = lazy(() => import('../pages/LoginPage').then((module) => ({ default: module.LoginPage })));
const FinanceDashboardPage = lazy(() => import('../pages/FinanceDashboardPage').then((module) => ({ default: module.FinanceDashboardPage })));
const FinancePrintPage = lazy(() => import('../pages/FinancePrintPage').then((module) => ({ default: module.FinancePrintPage })));
const BookingsPage = lazy(() => import('../pages/BookingsPage').then((module) => ({ default: module.BookingsPage })));
const CustomersPage = lazy(() => import('../pages/CustomersPage').then((module) => ({ default: module.CustomersPage })));
const ServicesPage = lazy(() => import('../pages/ServicesPage').then((module) => ({ default: module.ServicesPage })));
const DressesPage = lazy(() => import('../pages/DressesPage').then((module) => ({ default: module.DressesPage })));
const PaymentsPage = lazy(() => import('../pages/PaymentsPage').then((module) => ({ default: module.PaymentsPage })));
const CustodyPage = lazy(() => import('../pages/CustodyPage').then((module) => ({ default: module.CustodyPage })));
const AuditExplorerPage = lazy(() => import('../pages/AuditExplorerPage').then((module) => ({ default: module.AuditExplorerPage })));
const ReportsPage = lazy(() => import('../pages/ReportsPage').then((module) => ({ default: module.ReportsPage })));
const ReportsPrintPage = lazy(() => import('../pages/ReportsPrintPage').then((module) => ({ default: module.ReportsPrintPage })));
const ExportsPage = lazy(() => import('../pages/ExportsPage').then((module) => ({ default: module.ExportsPage })));
const AccountingPage = lazy(() => import('../pages/AccountingPage').then((module) => ({ default: module.AccountingPage })));
const UsersPage = lazy(() => import('../pages/UsersPage').then((module) => ({ default: module.UsersPage })));
const SettingsPage = lazy(() => import('../pages/SettingsPage').then((module) => ({ default: module.SettingsPage })));

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    element: <ProtectedRoute />,
    children: [
      { path: 'print/finance', element: <FinancePrintPage /> },
      { path: 'print/reports', element: <ReportsPrintPage /> },
      {
        path: '/',
        element: <DashboardShell />,
        children: [
          { index: true, element: <Navigate to='/dashboard' replace /> },
          { path: 'dashboard', element: <FinanceDashboardPage /> },
          { path: 'bookings', element: <BookingsPage /> },
          { path: 'customers', element: <CustomersPage /> },
          { path: 'services', element: <ServicesPage /> },
          { path: 'dresses', element: <DressesPage /> },
          { path: 'payments', element: <PaymentsPage /> },
          { path: 'custody', element: <CustodyPage /> },
          { path: 'custody-reports', element: <Navigate to='/custody' replace /> },
          { path: 'audit', element: <AuditExplorerPage /> },
          { path: 'reports', element: <ReportsPage /> },
          { path: 'exports', element: <ExportsPage /> },
          { path: 'accounting', element: <AccountingPage /> },
          { path: 'users', element: <UsersPage /> },
          { path: 'settings', element: <SettingsPage /> },
        ],
      },
    ],
  },
]);
