import type { LanguageCode } from '../lib/language';
import { useLocalizedText } from './useText';

const usersText = {
  ar: {
    admin: {
      description: 'إدارة جميع المستخدمين وصلاحياتهم الأساسية.',
      dialogCreateTitle: 'إضافة مستخدم',
      dialogEditTitle: 'تعديل مستخدم',
      listSubtitle: 'المدير يرى جميع المستخدمين ويمكنه تعديلهم.',
      listTitle: 'قائمة المستخدمين',
    },
    fields: {
      fullName: 'الاسم الكامل',
      newPassword: 'كلمة المرور الجديدة',
      password: 'كلمة المرور',
      passwordHint: 'اتركها فارغة إذا كنت لا تريد تغييرها',
      preferredLanguage: 'اللغة الافتراضية',
      role: 'الدور',
      username: 'اسم المستخدم',
    },
    profile: {
      description: 'يمكنك تعديل اسمك الكامل وكلمة المرور واللغة الافتراضية.',
      subtitle: 'المستخدم العادي لا يرى أي مستخدم آخر.',
      title: 'بيانات الحساب',
    },
    roles: {
      admin: 'مدير',
      user: 'مستخدم',
    },
    roleManagement: {
      title: 'إدارة الأدوار والصلاحيات',
      addRole: 'إضافة دور جديد',
      system: 'نظامي',
      noDescription: 'لا يوجد وصف',
      activePermissions: 'صلاحيات مفعلة',
      editTooltip: 'تعديل',
      cloneTooltip: 'نسخ',
      deleteTooltip: 'حذف',
      deleteConfirm: 'هل أنت متأكد من حذف هذا الدور؟',
      dialogEdit: 'تعديل الدور:',
      dialogCreate: 'إنشاء دور جديد',
      roleName: 'اسم الدور',
      description: 'الوصف',
      permissionsCount: 'الصلاحيات ({count})',
      cancel: 'إلغاء',
      save: 'حفظ التغييرات',
      clonePrompt: 'أدخل الاسم الجديد للدور:',
      errorLoad: 'فشل تحميل البيانات',
      errorSave: 'فشل حفظ الدور',
      categories: {
        system: 'النظام والأمان',
        finance: 'المالية والتقارير',
        data: 'البيانات الأساسية',
        atelier: 'الأتيليه',
        salon: 'الصالون',
        crm: 'CRM والتسويق',
        inventory: 'المخزون',
        operations: 'العمليات'
      }
    },
    status: {
      active: 'نشط',
      inactive: 'موقوف',
    },
  },
  en: {
    admin: {
      description: 'Manage all users and their base roles.',
      dialogCreateTitle: 'Create user',
      dialogEditTitle: 'Edit user',
      listSubtitle: 'Admins can view and update all users.',
      listTitle: 'Users list',
    },
    fields: {
      fullName: 'Full name',
      newPassword: 'New password',
      password: 'Password',
      passwordHint: 'Leave empty if you do not want to change it',
      preferredLanguage: 'Default language',
      role: 'Role',
      username: 'Username',
    },
    profile: {
      description: 'You can update your full name, password, and default language.',
      subtitle: 'A regular user cannot see any other user.',
      title: 'My account',
    },
    roles: {
      admin: 'Admin',
      user: 'User',
    },
    roleManagement: {
      title: 'Roles & Permissions Management',
      addRole: 'Add New Role',
      system: 'System',
      noDescription: 'No description available',
      activePermissions: 'active permissions',
      editTooltip: 'Edit',
      cloneTooltip: 'Clone',
      deleteTooltip: 'Delete',
      deleteConfirm: 'Are you sure you want to delete this role?',
      dialogEdit: 'Edit Role:',
      dialogCreate: 'Create New Role',
      roleName: 'Role Name',
      description: 'Description',
      permissionsCount: 'Permissions ({count})',
      cancel: 'Cancel',
      save: 'Save Changes',
      clonePrompt: 'Enter the new name for the role:',
      errorLoad: 'Failed to load data',
      errorSave: 'Failed to save role',
      categories: {
        system: 'System & Security',
        finance: 'Finance & Reports',
        data: 'Master Data',
        atelier: 'Atelier',
        salon: 'Salon',
        crm: 'CRM & Marketing',
        inventory: 'Inventory',
        operations: 'Operations'
      }
    },
    status: {
      active: 'Active',
      inactive: 'Inactive',
    },
  },
} as const;

export function useUsersText() {
  return useLocalizedText(usersText);
}

export function userRoleLabel(language: LanguageCode, value: string) {
  return usersText[language].roles[value as keyof typeof usersText.ar.roles] ?? value;
}
