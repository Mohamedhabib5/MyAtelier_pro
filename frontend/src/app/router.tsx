import { lazy } from 'react';

import { createBrowserRouter, Navigate } from 'react-router-dom';

import { ProtectedRoute } from '../components/ProtectedRoute';

const DashboardShell = lazy(() => import('../pages/DashboardShell').then((module) => ({ default: module.DashboardShell })));
const LoginPage = lazy(() => import('../pages/LoginPage').then((module) => ({ default: module.LoginPage })));
const FinanceDashboardPage = lazy(() => import('../pages/FinanceDashboardPage').then((module) => ({ default: module.FinanceDashboardPage })));
const FinancePrintPage = lazy(() => import('../pages/FinancePrintPage').then((module) => ({ default: module.FinancePrintPage })));
const BookingsPage = lazy(() => import('../pages/BookingsPage').then((module) => ({ default: module.BookingsPage })));
const CustomersPage = lazy(() => import('../pages/CustomersPage').then((module) => ({ default: module.CustomersPage })));
const DressesPage = lazy(() => import('../pages/DressesPage').then((module) => ({ default: module.DressesPage })));
const PaymentsPage = lazy(() => import('../pages/PaymentsPage').then((module) => ({ default: module.PaymentsPage })));
const CustodyPage = lazy(() => import('../pages/CustodyPage').then((module) => ({ default: module.CustodyPage })));
const AuditExplorerPage = lazy(() => import('../pages/AuditExplorerPage').then((module) => ({ default: module.AuditExplorerPage })));
const ReportsPage = lazy(() => import('../pages/ReportsPage').then((module) => ({ default: module.ReportsPage })));
const ReportsPrintPage = lazy(() => import('../pages/ReportsPrintPage').then((module) => ({ default: module.ReportsPrintPage })));
const AccountingPage = lazy(() => import('../pages/AccountingPage').then((module) => ({ default: module.AccountingPage })));
const SettingsPage = lazy(() => import('../pages/SettingsPage').then((module) => ({ default: module.SettingsPage })));

// Settings Views
const GeneralCompanyView = lazy(() => import('../features/settings/views/GeneralCompanyView').then((module) => ({ default: module.GeneralCompanyView })));
const GeneralBackupView = lazy(() => import('../features/settings/views/GeneralBackupView').then((module) => ({ default: module.GeneralBackupView })));
const GeneralFinancialView = lazy(() => import('../features/settings/views/GeneralFinancialView').then((module) => ({ default: module.GeneralFinancialView })));
const CatalogDepartmentsView = lazy(() => import('../features/catalog/views/CatalogDepartmentsView').then((module) => ({ default: module.CatalogDepartmentsView })));
const CatalogServicesView = lazy(() => import('../features/catalog/views/CatalogServicesView').then((module) => ({ default: module.CatalogServicesView })));
const SecurityUsersView = lazy(() => import('../features/users/views/SecurityUsersView').then((module) => ({ default: module.SecurityUsersView })));
const DataExportsView = lazy(() => import('../features/exports/views/DataExportsView').then((module) => ({ default: module.DataExportsView })));

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
          { path: 'dresses', element: <DressesPage /> },
          { path: 'payments', element: <PaymentsPage /> },
          { path: 'custody', element: <CustodyPage /> },
          { path: 'custody-reports', element: <Navigate to='/custody' replace /> },
          { path: 'audit', element: <AuditExplorerPage /> },
          { path: 'reports', element: <ReportsPage /> },
          { path: 'accounting', element: <AccountingPage /> },
          { path: 'services', element: <Navigate to='/settings/catalog/services' replace /> },
          { path: 'users', element: <Navigate to='/settings/security/users' replace /> },
          { path: 'exports', element: <Navigate to='/settings/data/exports' replace /> },
          { 
            path: 'settings', 
            element: <SettingsPage />,
            children: [
              { index: true, element: <Navigate to='/settings/general/company' replace /> },
              { path: 'general', element: <Navigate to='/settings/general/company' replace /> },
              { path: 'general/company', element: <GeneralCompanyView /> },
              { path: 'general/backups', element: <GeneralBackupView /> },
              { path: 'general/financial', element: <GeneralFinancialView /> },
              { path: 'catalog', element: <Navigate to='/settings/catalog/departments' replace /> },
              { path: 'catalog/departments', element: <CatalogDepartmentsView /> },
              { path: 'catalog/services', element: <CatalogServicesView /> },
              { path: 'security', element: <Navigate to='/settings/security/users' replace /> },
              { path: 'security/users', element: <SecurityUsersView /> },
              { path: 'data', element: <Navigate to='/settings/data/exports' replace /> },
              { path: 'data/exports', element: <DataExportsView /> },
            ]
          },
        ],
      },
    ],
  },
]);
