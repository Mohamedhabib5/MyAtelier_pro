import { useLocalizedText } from './useText';

const customersText = {
  ar: {
    page: {
      create: 'إضافة عميل',
      description: 'إدارة قائمة العملاء الأساسية بنفس أسلوب النظام السابق ولكن على البنية الجديدة.',
      listSubtitle: 'يمكن للمدير والمستخدم العادي عرض العملاء وإضافتهم وتعديلهم في هذه المرحلة.',
      listTitle: 'قائمة العملاء',
      title: 'العملاء',
    },
    table: {
      action: 'إجراء',
      email: 'البريد',
      fullName: 'الاسم الكامل',
      phone: 'الهاتف',
      status: 'الحالة',
    },
    dialog: {
      create: 'إضافة عميل',
      edit: 'تعديل عميل',
      address: 'العنوان',
      email: 'البريد الإلكتروني',
      fullName: 'الاسم الكامل',
      notes: 'ملاحظات',
      phone: 'الهاتف',
      status: 'الحالة',
    },
    status: {
      active: 'نشط',
      inactive: 'موقوف',
    },
  },
  en: {
    page: {
      create: 'Add customer',
      description: 'Manage the core customer list in the same spirit as the previous system on the new architecture.',
      listSubtitle: 'Both admin and regular users can view, create, and update customers at this stage.',
      listTitle: 'Customers list',
      title: 'Customers',
    },
    table: {
      action: 'Action',
      email: 'Email',
      fullName: 'Full name',
      phone: 'Phone',
      status: 'Status',
    },
    dialog: {
      create: 'Create customer',
      edit: 'Edit customer',
      address: 'Address',
      email: 'Email',
      fullName: 'Full name',
      notes: 'Notes',
      phone: 'Phone',
      status: 'Status',
    },
    status: {
      active: 'Active',
      inactive: 'Inactive',
    },
  },
} as const;

export function useCustomersText() {
  return useLocalizedText(customersText);
}
