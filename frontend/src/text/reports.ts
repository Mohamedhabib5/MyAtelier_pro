import type { LanguageCode } from '../lib/language';
import { useLocalizedText } from './useText';

const reportsText = {
  ar: {
    page: {
      button: 'عرض ملخص تشغيلي',
      description: 'ملخص تشغيلي أوسع يغطي العملاء والخدمات والفساتين والحجوزات والمدفوعات.',
      title: 'التقارير',
    },
    metrics: {
      activeCustomers: 'العملاء النشطون',
      activeServices: 'الخدمات النشطة',
      availableDresses: 'الفساتين المتاحة',
      upcomingBookings: 'الحجوزات القادمة',
    },
    helpers: {
      activeCustomers: 'عدد العملاء النشطين داخل النظام.',
      activeServices: 'عدد الخدمات المتاحة حاليًا.',
      availableDresses: 'الفساتين الجاهزة للحجز الآن.',
      upcomingBookings: 'الحجوزات غير الملغاة القادمة.',
    },
    sections: {
      bookingStatuses: 'حالات الحجوزات',
      departmentServices: 'الخدمات حسب القسم',
      dressStatuses: 'حالات الفساتين',
      paymentMix: 'خلطة المدفوعات',
      upcoming: 'أقرب الحجوزات القادمة',
    },
    table: {
      bookingNumber: 'رقم الحجز',
      customer: 'العميل',
      service: 'الخدمة',
      serviceDate: 'تاريخ الخدمة',
      status: 'الحالة',
    },
    subtitles: {
      bookingStatuses: 'تجميع الحجوزات حسب الحالة.',
      departmentServices: 'عدد الخدمات داخل كل قسم.',
      dressStatuses: 'توزيع الفساتين حسب حالتها الحالية.',
      empty: 'لا توجد بيانات بعد.',
      paymentMix: 'صافي المدفوعات بحسب نوع الحركة.',
      servicesCountSuffix: 'خدمات',
      upcoming: 'أول الحجوزات القادمة بحسب التاريخ.',
      itemsSuffix: 'عناصر',
    },
    print: {
      noData: 'لا توجد بيانات.',
      subtitle: 'نسخة مناسبة للطباعة أو الحفظ PDF من صفحة التقارير.',
      title: 'تقرير تشغيلي قابل للطباعة',
    },
  },
  en: {
    page: {
      button: 'Show operational summary',
      description: 'A broader operational summary across customers, services, dresses, bookings, and payments.',
      title: 'Reports',
    },
    metrics: {
      activeCustomers: 'Active customers',
      activeServices: 'Active services',
      availableDresses: 'Available dresses',
      upcomingBookings: 'Upcoming bookings',
    },
    helpers: {
      activeCustomers: 'Number of active customers in the system.',
      activeServices: 'Number of currently available services.',
      availableDresses: 'Dresses ready to be booked now.',
      upcomingBookings: 'Upcoming non-cancelled bookings.',
    },
    sections: {
      bookingStatuses: 'Booking statuses',
      departmentServices: 'Services by department',
      dressStatuses: 'Dress statuses',
      paymentMix: 'Payment mix',
      upcoming: 'Upcoming bookings',
    },
    table: {
      bookingNumber: 'Booking #',
      customer: 'Customer',
      service: 'Service',
      serviceDate: 'Service date',
      status: 'Status',
    },
    subtitles: {
      bookingStatuses: 'Bookings grouped by status.',
      departmentServices: 'Number of services in each department.',
      dressStatuses: 'Distribution of dresses by current status.',
      empty: 'No data yet.',
      paymentMix: 'Net payment mix by movement type.',
      servicesCountSuffix: 'services',
      upcoming: 'The nearest upcoming bookings by date.',
      itemsSuffix: 'items',
    },
    print: {
      noData: 'No data available.',
      subtitle: 'A printable or PDF-friendly version of the reports page.',
      title: 'Printable operational report',
    },
  },
} as const;

const reportStatusLabels = {
  ar: {
    available: 'متاح',
    cancelled: 'ملغي',
    completed: 'مكتمل',
    confirmed: 'مؤكد',
    deposit: 'عربون',
    draft: 'مسودة',
    maintenance: 'صيانة',
    payment: 'دفعة',
    refund: 'استرداد',
    reserved: 'محجوز',
    sold: 'مباع',
  },
  en: {
    available: 'Available',
    cancelled: 'Cancelled',
    completed: 'Completed',
    confirmed: 'Confirmed',
    deposit: 'Deposit',
    draft: 'Draft',
    maintenance: 'Maintenance',
    payment: 'Payment',
    refund: 'Refund',
    reserved: 'Reserved',
    sold: 'Sold',
  },
} as const;

export function useReportsText() {
  return useLocalizedText(reportsText);
}

export function reportStatusLabel(language: LanguageCode, value: string) {
  return reportStatusLabels[language][value as keyof typeof reportStatusLabels.ar] ?? value;
}
