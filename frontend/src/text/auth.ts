import { useLocalizedText } from './useText';

const authText = {
  ar: {
    fallbackError: 'تعذر تسجيل الدخول',
    helper: 'عند تشغيل قاعدة بيانات جديدة لأول مرة يتم إنشاء المستخدم الافتراضي:',
    password: 'كلمة المرور',
    subtitle: 'سجّل الدخول لبدء استخدام MyAtelier Pro',
    submitting: 'جارٍ تسجيل الدخول...',
    submit: 'تسجيل الدخول',
    title: 'مرحبًا بك',
    username: 'اسم المستخدم',
  },
  en: {
    fallbackError: 'Unable to sign in',
    helper: 'On a fresh database, the default account is created as:',
    password: 'Password',
    subtitle: 'Sign in to start using MyAtelier Pro',
    submitting: 'Signing in...',
    submit: 'Sign in',
    title: 'Welcome back',
    username: 'Username',
  },
} as const;

export function useLoginText() {
  return useLocalizedText(authText);
}
