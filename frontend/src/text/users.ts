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
