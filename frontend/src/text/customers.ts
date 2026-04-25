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
      groomName: 'اسم العريس',
      brideName: 'اسم العروسة',
      phone: 'الهاتف 1',
      phone2: 'الهاتف 2',
      status: 'الحالة',
    },
    dialog: {
      create: 'إضافة عميل',
      edit: 'تعديل عميل',
      address: 'العنوان',
      email: 'البريد الإلكتروني',
      fullName: 'الاسم الكامل',
      groomName: 'اسم العريس',
      brideName: 'اسم العروسة',
      notes: 'ملاحظات',
      phone: 'رقم تليفون 1',
      phone2: 'رقم تليفون 2',
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
      groomName: "Groom's Name",
      brideName: "Bride's Name",
      phone: 'Phone 1',
      phone2: 'Phone 2',
      status: 'Status',
    },
    dialog: {
      create: 'Create customer',
      edit: 'Edit customer',
      address: 'Address',
      email: 'Email',
      fullName: 'Full name',
      groomName: "Groom's Name",
      brideName: "Bride's Name",
      notes: 'Notes',
      phone: 'Phone 1',
      phone2: 'Phone 2',
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
