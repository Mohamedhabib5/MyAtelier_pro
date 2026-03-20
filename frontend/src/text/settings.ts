import { useLocalizedText } from './useText';

const settingsText = {
  ar: {
    page: {
      description: 'إدارة بيانات الشركة والفروع والنسخ الاحتياطية.',
      title: 'الإعدادات',
    },
    messages: {
      backupCreated: 'تم إنشاء النسخة الاحتياطية وسيبدأ التنزيل الآن.',
      branchCreated: 'تم إنشاء الفرع الجديد بنجاح.',
      companySaved: 'تم تحديث بيانات الشركة بنجاح.',
    },
    company: {
      currency: 'العملة الافتراضية',
      legalName: 'الاسم القانوني',
      name: 'اسم الشركة',
      save: 'حفظ بيانات الشركة',
      subtitle: 'حدّث اسم الشركة والاسم القانوني والعملة الافتراضية.',
      title: 'بيانات الشركة',
    },
    activeBranch: {
      current: 'الفرع الحالي',
      default: 'افتراضي',
      inactive: 'موقوف',
      note: 'يمكنك تغيير الفرع من محدد الفروع الموجود في الشريط العلوي.',
      subtitle: 'هذا الفرع هو النطاق الحالي للحجوزات والمدفوعات واللوحات.',
      title: 'الفرع النشط',
      active: 'نشط',
    },
    createBranch: {
      code: 'كود الفرع',
      codePlaceholder: 'CAIRO-2',
      create: 'إنشاء فرع',
      name: 'اسم الفرع',
      namePlaceholder: 'فرع القاهرة الثاني',
      subtitle: 'أنشئ فرعًا جديدًا ليظهر مباشرة في محدد الفروع.',
      title: 'إضافة فرع',
    },
    branchList: {
      current: 'الفرع الحالي',
      default: 'افتراضي',
      inactive: 'موقوف',
      subtitle: 'عرض سريع للفروع المتاحة داخل الشركة الحالية.',
      title: 'قائمة الفروع',
      active: 'نشط',
    },
    backups: {
      create: 'إنشاء وتنزيل نسخة احتياطية',
      download: 'تنزيل',
      filename: 'الملف',
      size: 'الحجم',
      status: 'الحالة',
      subtitle: 'ينشئ النظام ملف ZIP جديدًا ويبدأ تنزيله مباشرة.',
      title: 'النسخ الاحتياطية',
    },
  },
  en: {
    page: {
      description: 'Manage company information, branches, and backups.',
      title: 'Settings',
    },
    messages: {
      backupCreated: 'The backup was created and the download will start now.',
      branchCreated: 'The new branch was created successfully.',
      companySaved: 'Company information was updated successfully.',
    },
    company: {
      currency: 'Default currency',
      legalName: 'Legal name',
      name: 'Company name',
      save: 'Save company details',
      subtitle: 'Update the company name, legal name, and default currency.',
      title: 'Company details',
    },
    activeBranch: {
      current: 'Current branch',
      default: 'Default',
      inactive: 'Inactive',
      note: 'You can change the branch from the selector in the top bar.',
      subtitle: 'This branch is the current scope for bookings, payments, and dashboards.',
      title: 'Active branch',
      active: 'Active',
    },
    createBranch: {
      code: 'Branch code',
      codePlaceholder: 'CAIRO-2',
      create: 'Create branch',
      name: 'Branch name',
      namePlaceholder: 'Cairo branch 2',
      subtitle: 'Create a new branch so it appears immediately in the branch selector.',
      title: 'Add branch',
    },
    branchList: {
      current: 'Current branch',
      default: 'Default',
      inactive: 'Inactive',
      subtitle: 'Quick overview of branches available in the current company.',
      title: 'Branch list',
      active: 'Active',
    },
    backups: {
      create: 'Create and download backup',
      download: 'Download',
      filename: 'File',
      size: 'Size',
      status: 'Status',
      subtitle: 'The system creates a new ZIP file and starts downloading it immediately.',
      title: 'Backups',
    },
  },
} as const;

export function useSettingsText() {
  return useLocalizedText(settingsText);
}
