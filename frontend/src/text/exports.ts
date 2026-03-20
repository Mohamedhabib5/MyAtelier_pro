import type { LanguageCode } from '../lib/language';
import { useLocalizedText } from './useText';

const exportsText = {
  ar: {
    page: {
      description: 'تنزيل ملفات CSV أو فتح نسخ قابلة للطباعة والحفظ PDF مباشرة من المتصفح.',
      infoBranchPrefix: 'تصدير الحجوزات والمدفوعات يعتمد على الفرع النشط الحالي:',
      infoPrint: 'النسخ القابلة للطباعة تُفتح في تبويب مستقل، ثم يمكنك اختيار "طباعة" أو "Save as PDF".',
      title: 'التصدير',
    },
    sections: {
      bookingLinesButton: 'تنزيل CSV سطور الحجوزات',
      bookingsButton: 'تنزيل CSV الحجوزات',
      bookingsSubtitle: 'ملفات CSV للحجوزات الخاصة بالفرع النشط الحالي: ملخص الوثائق + تفاصيل السطور.',
      bookingsTitle: 'تصدير الحجوزات',
      customersButton: 'تنزيل CSV العملاء',
      customersSubtitle: 'ملف CSV يشمل بيانات العملاء على مستوى الشركة.',
      customersTitle: 'تصدير العملاء',
      financeButton: 'فتح النسخة المالية للطباعة',
      financeSubtitle: 'ملخص مالي مناسب للطباعة أو الحفظ PDF.',
      financeTitle: 'نسخة مالية للطباعة',
      paymentAllocationsButton: 'تنزيل CSV توزيعات الدفع',
      paymentsButton: 'تنزيل CSV سندات الدفع',
      paymentsSubtitle: 'ملفات CSV لسندات الدفع وسطور التوزيع الخاصة بالفرع النشط مع رقم القيد المحاسبي المرتبط.',
      paymentsTitle: 'تصدير سندات الدفع',
      reportsButton: 'فتح نسخة التقارير للطباعة',
      reportsSubtitle: 'تقرير تشغيلي مناسب للطباعة أو الحفظ PDF.',
      reportsTitle: 'نسخة التقارير للطباعة',
    },
    schedules: {
      active: 'نشط',
      cadence: 'التكرار',
      create: 'حفظ الجدول',
      exportType: 'نوع التصدير',
      heading: 'الجداول المحفوظة',
      inactive: 'متوقف',
      infoCompany: 'هذا التصدير على مستوى الشركة.',
      lastRun: 'آخر تشغيل',
      lastRunEmpty: '—',
      listEmpty: 'لا توجد جداول محفوظة بعد.',
      name: 'اسم الجدول',
      nextRun: 'التشغيل القادم',
      now: 'تشغيل الآن',
      runScopePrefix: 'هذا الجدول سيستخدم الفرع النشط الحالي:',
      scope: 'النطاق',
      scopeCompany: 'مستوى الشركة',
      startOn: 'يبدأ من',
      status: 'الحالة',
      subtitle: 'احفظ نوع التصدير والفاصل الزمني ثم شغّله يدويًا عند الحاجة مع تتبع موعد التشغيل القادم.',
      tableAction: 'إجراء',
      tableName: 'الاسم',
      toggleOff: 'إيقاف',
      toggleOn: 'تفعيل',
      type: 'النوع',
    },
    print: {
      back: 'العودة إلى التصدير',
      branch: 'الفرع النشط',
      generatedAt: 'وقت الإنشاء',
      print: 'طباعة / حفظ PDF',
      user: 'المستخدم',
    },
  },
  en: {
    page: {
      description: 'Download CSV files or open printable / PDF-ready pages directly from the browser.',
      infoBranchPrefix: 'Booking and payment exports depend on the current active branch:',
      infoPrint: 'Printable versions open in a separate tab, then you can choose "Print" or "Save as PDF".',
      title: 'Exports',
    },
    sections: {
      bookingLinesButton: 'Download booking lines CSV',
      bookingsButton: 'Download bookings CSV',
      bookingsSubtitle: 'CSV files for the current active branch bookings: document summary plus line details.',
      bookingsTitle: 'Bookings export',
      customersButton: 'Download customers CSV',
      customersSubtitle: 'A company-level CSV file for customer data.',
      customersTitle: 'Customers export',
      financeButton: 'Open printable finance view',
      financeSubtitle: 'A finance summary suitable for printing or saving as PDF.',
      financeTitle: 'Printable finance view',
      paymentAllocationsButton: 'Download payment allocations CSV',
      paymentsButton: 'Download payment documents CSV',
      paymentsSubtitle: 'CSV files for payment documents and allocation lines in the active branch, including linked journal numbers.',
      paymentsTitle: 'Payment exports',
      reportsButton: 'Open printable reports view',
      reportsSubtitle: 'An operational report suitable for printing or saving as PDF.',
      reportsTitle: 'Printable reports view',
    },
    schedules: {
      active: 'Active',
      cadence: 'Cadence',
      create: 'Save schedule',
      exportType: 'Export type',
      heading: 'Saved schedules',
      inactive: 'Stopped',
      infoCompany: 'This export runs at company level.',
      lastRun: 'Last run',
      lastRunEmpty: '—',
      listEmpty: 'No saved schedules yet.',
      name: 'Schedule name',
      nextRun: 'Next run',
      now: 'Run now',
      runScopePrefix: 'This schedule will use the current active branch:',
      scope: 'Scope',
      scopeCompany: 'Company level',
      startOn: 'Starts on',
      status: 'Status',
      subtitle: 'Save the export type and cadence, then run it manually when needed while tracking the next run date.',
      tableAction: 'Action',
      tableName: 'Name',
      toggleOff: 'Disable',
      toggleOn: 'Enable',
      type: 'Type',
    },
    print: {
      back: 'Back to exports',
      branch: 'Active branch',
      generatedAt: 'Generated at',
      print: 'Print / Save PDF',
      user: 'User',
    },
  },
} as const;

const exportTypeLabels = {
  ar: {
    booking_lines_csv: 'CSV سطور الحجوزات',
    bookings_csv: 'CSV الحجوزات',
    customers_csv: 'CSV العملاء',
    finance_print: 'طباعة المالية',
    payment_allocations_csv: 'CSV توزيعات الدفع',
    payments_csv: 'CSV سندات الدفع',
    reports_print: 'طباعة التقارير',
  },
  en: {
    booking_lines_csv: 'Booking lines CSV',
    bookings_csv: 'Bookings CSV',
    customers_csv: 'Customers CSV',
    finance_print: 'Finance print',
    payment_allocations_csv: 'Payment allocations CSV',
    payments_csv: 'Payment documents CSV',
    reports_print: 'Reports print',
  },
} as const;

const cadenceLabels = {
  ar: {
    daily: 'يومي',
    weekly: 'أسبوعي',
  },
  en: {
    daily: 'Daily',
    weekly: 'Weekly',
  },
} as const;

export function useExportsText() {
  return useLocalizedText(exportsText);
}

export function exportTypeLabel(language: LanguageCode, value: string) {
  return exportTypeLabels[language][value as keyof typeof exportTypeLabels.ar] ?? value;
}

export function cadenceLabel(language: LanguageCode, value: string) {
  return cadenceLabels[language][value as keyof typeof cadenceLabels.ar] ?? value;
}
