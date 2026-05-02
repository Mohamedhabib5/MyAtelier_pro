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
      type: 'اسم الفستان',
      description: 'وصف الفستان',
    },
    dialog: {
      code: 'كود الفستان',
      create: 'إضافة فستان',
      description: 'وصف الفستان',
      edit: 'تعديل فستان',
      imageHint: 'قم برفع صورة للفستان (الحد الأقصى 300 كيلوبايت).',
      imageRef: 'صورة الفستان',
      uploadButton: 'رفع صورة',
      removeButton: 'حذف الصورة',
      invalidSize: 'حجم الملف كبير جداً. الحد الأقصى هو 300 كيلوبايت.',
      invalidType: 'يجب أن يكون الملف صورة.',
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
      with_customer: 'مع العميل',
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
      type: 'Dress Name',
      description: 'Description',
    },
    dialog: {
      code: 'Dress code',
      create: 'Create dress',
      description: 'Dress description',
      edit: 'Edit dress',
      imageHint: 'Upload a dress image (max 300 KB).',
      imageRef: 'Dress Image',
      uploadButton: 'Upload Image',
      removeButton: 'Remove Image',
      invalidSize: 'File size too large. Max is 300 KB.',
      invalidType: 'File must be an image.',
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
      with_customer: 'With customer',
    },
  },
} as const;

export function useDressesText() {
  return useLocalizedText(dressesText);
}

export function dressStatusLabel(language: LanguageCode, value: string) {
  return dressesText[language].status[value as keyof typeof dressesText.ar.status] ?? value;
}
