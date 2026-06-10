import { lazy } from 'react';

import { createBrowserRouter, Navigate } from 'react-router-dom';

import { ProtectedRoute } from '../components/ProtectedRoute';

const DashboardShell = lazy(() => import('../pages/DashboardShell').then((module) => ({ default: module.DashboardShell })));
const LoginPage = lazy(() => import('../pages/LoginPage').then((module) => ({ default: module.LoginPage })));
const FinanceDashboardPage = lazy(() => import('../pages/FinanceDashboardPage').then((module) => ({ default: module.FinanceDashboardPage })));
const FinancePrintPage = lazy(() => import('../pages/FinancePrintPage').then((module) => ({ default: module.FinancePrintPage })));
const BookingsPage = lazy(() => import('../pages/BookingsPage').then((module) => ({ default: module.BookingsPage })));
const CalendarPage = lazy(() => import('../pages/CalendarPage').then((module) => ({ default: module.CalendarPage })));
const CustomersPage = lazy(() => import('../pages/CustomersPage').then((module) => ({ default: module.CustomersPage })));
const DressesPage = lazy(() => import('../pages/DressesPage').then((module) => ({ default: module.DressesPage })));
const PaymentsPage = lazy(() => import('../pages/PaymentsPage').then((module) => ({ default: module.PaymentsPage })));
const DisbursementsPage = lazy(() => import('../pages/DisbursementsPage').then((module) => ({ default: module.DisbursementsPage })));
const CustodyPage = lazy(() => import('../pages/CustodyPage').then((module) => ({ default: module.CustodyPage })));
const AuditExplorerPage = lazy(() => import('../pages/AuditExplorerPage').then((module) => ({ default: module.AuditExplorerPage })));
const ReportsPage = lazy(() => import('../pages/ReportsPage').then((module) => ({ default: module.ReportsPage })));
const ReportsPrintPage = lazy(() => import('../pages/ReportsPrintPage').then((module) => ({ default: module.ReportsPrintPage })));
const AccountingPrintPage = lazy(() => import('../pages/AccountingPrintPage').then((module) => ({ default: module.AccountingPrintPage })));
const AccountingPage = lazy(() => import('../pages/AccountingPage').then((module) => ({ default: module.AccountingPage })));
const SettingsPage = lazy(() => import('../pages/SettingsPage').then((module) => ({ default: module.SettingsPage })));
const BIAnalyticsPage = lazy(() => import('../pages/BIAnalyticsPage').then((module) => ({ default: module.BIAnalyticsPage })));
const BackupPage = lazy(() => import('../pages/ops/BackupPage'));

// Settings Views
const GeneralCompanyView = lazy(() => import('../features/settings/views/GeneralCompanyView').then((module) => ({ default: module.GeneralCompanyView })));
const DailyReportsView = lazy(() => import('../features/settings/views/DailyReportsView').then((module) => ({ default: module.DailyReportsView })));
const GeneralBackupView = lazy(() => import('../features/settings/views/GeneralBackupView').then((module) => ({ default: module.GeneralBackupView })));
const GeneralFinancialView = lazy(() => import('../features/settings/views/GeneralFinancialView').then((module) => ({ default: module.GeneralFinancialView })));
const ThemeSettingsView = lazy(() => import('../features/settings/views/ThemeSettingsView').then((module) => ({ default: module.ThemeSettingsView })));
const CatalogDepartmentsView = lazy(() => import('../features/catalog/views/CatalogDepartmentsView').then((module) => ({ default: module.CatalogDepartmentsView })));
const CatalogServicesView = lazy(() => import('../features/catalog/views/CatalogServicesView').then((module) => ({ default: module.CatalogServicesView })));
const SecurityUsersView = lazy(() => import('../features/users/views/SecurityUsersView').then((module) => ({ default: module.SecurityUsersView })));
const SecurityRolesView = lazy(() => import('../features/users/views/SecurityRolesView').then((module) => ({ default: module.SecurityRolesView })));
const SecurityConfigView = lazy(() => import('../features/settings/views/SecurityConfigView').then((module) => ({ default: module.SecurityConfigView })));
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
      { path: 'print/accounting', element: <AccountingPrintPage /> },
      {
        path: '/',
        element: <DashboardShell />,
        children: [
          { index: true, element: <Navigate to='/dashboard' replace /> },
          { path: 'dashboard', element: <FinanceDashboardPage /> },
          { path: 'bookings', element: <BookingsPage /> },
          { path: 'calendar', element: <CalendarPage /> },
          { path: 'customers', element: <CustomersPage /> },
          { path: 'dresses', element: <DressesPage /> },
          { path: 'payments', element: <PaymentsPage /> },
          { path: 'disbursements', element: <DisbursementsPage /> },
          { path: 'custody', element: <CustodyPage /> },
          { path: 'custody-reports', element: <Navigate to='/custody' replace /> },
          { path: 'audit', element: <AuditExplorerPage /> },
          { path: 'reports', element: <ReportsPage /> },
          { path: 'analytics', element: <BIAnalyticsPage /> },
          { path: 'accounting', element: <AccountingPage /> },
          { path: 'ops/backups', element: <BackupPage /> },
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
              { path: 'general/daily-reports', element: <DailyReportsView /> },
              { path: 'general/backups', element: <GeneralBackupView /> },
              { path: 'general/financial', element: <GeneralFinancialView /> },
              { path: 'general/appearance', element: <ThemeSettingsView /> },
              { path: 'catalog', element: <Navigate to='/settings/catalog/departments' replace /> },
              { path: 'catalog/departments', element: <CatalogDepartmentsView /> },
              { path: 'catalog/services', element: <CatalogServicesView /> },
              { path: 'security', element: <Navigate to='/settings/security/users' replace /> },
              { path: 'security/users', element: <SecurityUsersView /> },
              { path: 'security/roles', element: <SecurityRolesView /> },
              { path: 'security/config', element: <SecurityConfigView /> },
              { path: 'data', element: <Navigate to='/settings/data/exports' replace /> },
              { path: 'data/exports', element: <DataExportsView /> },
            ]
          },
        ],
      },
    ],
  },
]);
