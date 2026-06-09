import { useLocalizedText } from './useText';

const navigationText = {
  ar: {
    appTitle: 'MyAtelier Pro',
    dashboard: 'الرئيسية',
    usersAdmin: 'إدارة المستخدمين',
    usersSelf: 'حسابي',
    modeAdmin: 'وضع المدير',
    modeUser: 'وضع المستخدم',
    logout: 'تسجيل الخروج',
    navTitle: 'التنقل',
    pages: {
      accounting: 'المحاسبة',
      audit: 'سجل التدقيق',
      bookings: 'الحجوزات',
      customers: 'العملاء',
      custody: 'الحيازة',
      dresses: 'الفساتين',
      exports: 'التصدير',
      payments: 'سندات القبض',
      disbursements: 'سندات الصرف',
      reports: 'التقارير',
      analytics: 'مركز التحليلات الذكية',
      services: 'الخدمات',
      calendar: 'التقويم',
      settings: 'الإعدادات',
    },
  },
  en: {
    appTitle: 'MyAtelier Pro',
    dashboard: 'Dashboard',
    usersAdmin: 'Users',
    usersSelf: 'My account',
    modeAdmin: 'Admin mode',
    modeUser: 'User mode',
    logout: 'Sign out',
    navTitle: 'Navigation',
    pages: {
      accounting: 'Accounting',
      audit: 'Audit',
      bookings: 'Bookings',
      customers: 'Customers',
      custody: 'Custody',
      dresses: 'Dresses',
      exports: 'Exports',
      payments: 'Receipts',
      disbursements: 'Payments',
      reports: 'Reports',
      analytics: 'Smart Analytics',
      services: 'Services',
      calendar: 'Calendar',
      settings: 'Settings',
    },
  },
} as const;

export function useNavigationText() {
  return useLocalizedText(navigationText);
}
