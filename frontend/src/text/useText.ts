import { useLanguage } from '../features/language/LanguageProvider';
import type { LanguageCode } from '../lib/language';

export type LocalizedText<T extends Record<LanguageCode, unknown> = Record<LanguageCode, unknown>> = T;

export function getLocalizedText<T extends Record<LanguageCode, unknown>>(text: T, language: LanguageCode): T[LanguageCode] {
  return text[language];
}

export function useLocalizedText<T extends Record<LanguageCode, unknown>>(text: T): T[LanguageCode] {
  const { language } = useLanguage();
  return getLocalizedText(text, language);
}
