import { useMemo } from 'react';

import { useLanguage } from '../features/language/LanguageProvider';
import type { LanguageCode } from '../lib/language';
import { useLocalizedText } from './useText';

export const EMPTY_VALUE = '—';

const commonText = {
  ar: {
    actions: 'الإجراءات',
    add: 'إضافة',
    branch: 'الفرع',
    cancel: 'إلغاء',
    create: 'إنشاء',
    delete: 'حذف',
    edit: 'تعديل',
    language: 'اللغة',
    save: 'حفظ',
    saveChanges: 'حفظ التغييرات',
    status: 'الحالة',
    unexpectedError: 'حدث خطأ غير متوقع',
  },
  en: {
    actions: 'Actions',
    add: 'Add',
    branch: 'Branch',
    cancel: 'Cancel',
    create: 'Create',
    delete: 'Delete',
    edit: 'Edit',
    language: 'Language',
    save: 'Save',
    saveChanges: 'Save changes',
    status: 'Status',
    unexpectedError: 'An unexpected error occurred',
  },
} as const;

const bookingStatusLabels = {
  ar: {
    draft: 'مسودة',
    confirmed: 'مؤكد',
    completed: 'مكتمل',
    cancelled: 'ملغي',
    partially_completed: 'مكتمل جزئيًا',
  },
  en: {
    draft: 'Draft',
    confirmed: 'Confirmed',
    completed: 'Completed',
    cancelled: 'Cancelled',
    partially_completed: 'Partially completed',
  },
} as const;

const paymentDocumentStatusLabels = {
  ar: {
    active: 'نشط',
    voided: 'مبطل',
  },
  en: {
    active: 'Active',
    voided: 'Voided',
  },
} as const;

const paymentKindLabels = {
  ar: {
    collection: 'تحصيل',
    refund: 'استرداد',
  },
  en: {
    collection: 'Collection',
    refund: 'Refund',
  },
} as const;

const linePaymentStateLabels = {
  ar: {
    unpaid: 'غير مدفوع',
    partial: 'مدفوع جزئيًا',
    paid: 'مدفوع بالكامل',
  },
  en: {
    unpaid: 'Unpaid',
    partial: 'Partially paid',
    paid: 'Paid in full',
  },
} as const;

export function useCommonText() {
  return useLocalizedText(commonText);
}

export function bookingStatusLabel(language: LanguageCode, value: string) {
  return bookingStatusLabels[language][value as keyof typeof bookingStatusLabels.ar] ?? value;
}

export function paymentDocumentStatusLabel(language: LanguageCode, value: string) {
  return paymentDocumentStatusLabels[language][value as keyof typeof paymentDocumentStatusLabels.ar] ?? value;
}

export function paymentKindLabel(language: LanguageCode, value: string) {
  return paymentKindLabels[language][value as keyof typeof paymentKindLabels.ar] ?? value;
}

export function linePaymentStateLabel(language: LanguageCode, value: string) {
  return linePaymentStateLabels[language][value as keyof typeof linePaymentStateLabels.ar] ?? value;
}

export function joinLocalizedList(language: LanguageCode, items: string[]) {
  return items.filter(Boolean).join(language === 'ar' ? '، ' : ', ');
}

export function useLanguageFormatters() {
  const { locale } = useLanguage();

  return useMemo(
    () => ({
      formatCount: (value: number) => new Intl.NumberFormat(locale).format(value),
      formatCurrency: (value: number, currency = 'EGP') =>
        new Intl.NumberFormat(locale, { style: 'currency', currency, maximumFractionDigits: 2 }).format(value),
      formatDateTime: (value: Date) => new Intl.DateTimeFormat(locale, { dateStyle: 'medium', timeStyle: 'short' }).format(value),
      formatDecimal: (value: number, minimumFractionDigits = 2, maximumFractionDigits = 2) =>
        new Intl.NumberFormat(locale, { minimumFractionDigits, maximumFractionDigits }).format(value),
    }),
    [locale],
  );
}
