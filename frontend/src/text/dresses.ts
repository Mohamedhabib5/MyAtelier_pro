import type { LanguageCode } from '../lib/language';
import { useLocalizedText } from './useText';

const dressesText = {
  ar: {
    page: {
      create: 'إضافة فستان',
      description: 'إدارة موارد الفساتين الأساسية مع حالة التوفر ومرجع الصورة تمهيدًا لربطها بالحجوزات.',
      listSubtitle: 'هذه المرحلة تحفظ بيانات الفستان وحالة توفره ومرجع الصورة فقط، بدون رفع ملفات فعلي حتى الآن.',
      listTitle: 'قائمة الفساتين',
      title: 'الفساتين',
    },
    table: {
      action: 'إجراء',
      code: 'الكود',
      imageRef: 'مرجع الصورة',
      purchaseDate: 'تاريخ الشراء',
      status: 'الحالة',
      type: 'النوع',
    },
    dialog: {
      code: 'كود الفستان',
      create: 'إضافة فستان',
      description: 'وصف الفستان',
      edit: 'تعديل فستان',
      imageHint: 'اسم الملف أو المسار المرجعي فقط في هذه المرحلة.',
      imageRef: 'مرجع الصورة',
      operationalStatus: 'الحالة التشغيلية',
      purchaseDate: 'تاريخ الشراء',
      status: 'الحالة',
      type: 'نوع الفستان',
    },
    status: {
      active: 'نشط',
      available: 'متاح',
      inactive: 'موقوف',
      maintenance: 'صيانة',
      reserved: 'محجوز',
    },
  },
  en: {
    page: {
      create: 'Add dress',
      description: 'Manage core dress resources with availability and image reference before deeper booking linkage.',
      listSubtitle: 'This stage stores dress details, availability, and image reference only, without real uploads yet.',
      listTitle: 'Dress list',
      title: 'Dresses',
    },
    table: {
      action: 'Action',
      code: 'Code',
      imageRef: 'Image reference',
      purchaseDate: 'Purchase date',
      status: 'Status',
      type: 'Type',
    },
    dialog: {
      code: 'Dress code',
      create: 'Create dress',
      description: 'Dress description',
      edit: 'Edit dress',
      imageHint: 'File name or reference path only at this stage.',
      imageRef: 'Image reference',
      operationalStatus: 'Operational status',
      purchaseDate: 'Purchase date',
      status: 'Status',
      type: 'Dress type',
    },
    status: {
      active: 'Active',
      available: 'Available',
      inactive: 'Inactive',
      maintenance: 'Maintenance',
      reserved: 'Reserved',
    },
  },
} as const;

export function useDressesText() {
  return useLocalizedText(dressesText);
}

export function dressStatusLabel(language: LanguageCode, value: string) {
  return dressesText[language].status[value as keyof typeof dressesText.ar.status] ?? value;
}
