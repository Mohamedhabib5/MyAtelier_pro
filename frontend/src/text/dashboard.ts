import { useLocalizedText } from './useText';

const dashboardText = {
  ar: {
    page: {
      description: 'عرض سريع لأهم المؤشرات المالية الحالية على الفرع النشط داخل النظام.',
      title: 'الرئيسية المالية',
    },
    metrics: {
      totalBookings: 'عدد الحجوزات',
      totalIncome: 'إجمالي المحصل',
      totalRemaining: 'إجمالي المتبقي',
    },
    helpers: {
      totalBookings: 'إجمالي الحجوزات الحالية في النطاق النشط.',
      totalIncome: 'صافي الدفعات بعد خصم الاستردادات.',
      totalRemaining: 'المبالغ المتبقية على الحجوزات غير الملغاة.',
    },
    sections: {
      dailyIncome: 'الدخل اليومي',
      departmentIncome: 'الدخل حسب القسم',
      topServices: 'أكثر الخدمات طلبًا',
    },
    subtitles: {
      dailyIncome: 'آخر القيم اليومية المحسوبة من الحركات المالية.',
      departmentIncome: 'صافي الدخل موزعًا حسب أقسام الخدمات.',
      empty: 'لا توجد بيانات بعد.',
      topServices: 'الخدمات الأعلى من حيث عدد الحجوزات.',
      bookingsSuffix: 'حجوزات',
    },
    print: {
      subtitle: 'نسخة مناسبة للطباعة أو الحفظ بصيغة PDF من المتصفح.',
      title: 'ملخص مالي قابل للطباعة',
    },
  },
  en: {
    page: {
      description: 'A quick view of the most important current financial indicators for the active branch.',
      title: 'Finance dashboard',
    },
    metrics: {
      totalBookings: 'Total bookings',
      totalIncome: 'Total collected',
      totalRemaining: 'Total remaining',
    },
    helpers: {
      totalBookings: 'Current total bookings in the active scope.',
      totalIncome: 'Net payments after refunds.',
      totalRemaining: 'Remaining balances on non-cancelled bookings.',
    },
    sections: {
      dailyIncome: 'Daily income',
      departmentIncome: 'Income by department',
      topServices: 'Top services',
    },
    subtitles: {
      dailyIncome: 'Recent daily values calculated from financial movements.',
      departmentIncome: 'Net income distributed by service departments.',
      empty: 'No data yet.',
      topServices: 'Most requested services by booking count.',
      bookingsSuffix: 'bookings',
    },
    print: {
      subtitle: 'A printable or PDF-friendly version from the browser.',
      title: 'Printable finance summary',
    },
  },
} as const;

export function useDashboardText() {
  return useLocalizedText(dashboardText);
}
