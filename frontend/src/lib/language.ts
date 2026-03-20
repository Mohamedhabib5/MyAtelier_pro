export type LanguageCode = 'ar' | 'en';
export type Direction = 'rtl' | 'ltr';

export const DEFAULT_LANGUAGE: LanguageCode = 'ar';
export const GUEST_LANGUAGE_STORAGE_KEY = 'myatelier_pro_guest_language';

export function isLanguageCode(value: string | null | undefined): value is LanguageCode {
  return value === 'ar' || value === 'en';
}

export function normalizeLanguage(value: string | null | undefined): LanguageCode {
  return isLanguageCode(value) ? value : DEFAULT_LANGUAGE;
}

export function directionForLanguage(language: LanguageCode): Direction {
  return language === 'ar' ? 'rtl' : 'ltr';
}

export function localeForLanguage(language: LanguageCode): string {
  return language === 'ar' ? 'ar-EG' : 'en-US';
}

export function alignForLanguage(language: LanguageCode): 'right' | 'left' {
  return language === 'ar' ? 'right' : 'left';
}
