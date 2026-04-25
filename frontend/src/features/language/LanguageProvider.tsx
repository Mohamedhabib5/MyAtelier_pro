import { PropsWithChildren, createContext, useContext, useEffect, useMemo, useState } from 'react';

import { useAuth } from '../auth/AuthProvider';
import { DEFAULT_LANGUAGE, GUEST_LANGUAGE_STORAGE_KEY, alignForLanguage, directionForLanguage, localeForLanguage, normalizeLanguage, type Direction, type LanguageCode } from '../../lib/language';

type LanguageContextValue = {
  language: LanguageCode;
  direction: Direction;
  locale: string;
  textAlign: 'right' | 'left';
  preferredLanguage: LanguageCode;
  setGuestLanguage: (language: LanguageCode) => void;
  setSessionLanguage: (language: LanguageCode) => Promise<void>;
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

function readGuestLanguage(): LanguageCode {
  if (typeof window === 'undefined') {
    return DEFAULT_LANGUAGE;
  }
  return normalizeLanguage(window.localStorage.getItem(GUEST_LANGUAGE_STORAGE_KEY));
}

function persistGuestLanguage(language: LanguageCode) {
  if (typeof window === 'undefined') {
    return;
  }
  window.localStorage.setItem(GUEST_LANGUAGE_STORAGE_KEY, language);
}

export function LanguageProvider({ children }: PropsWithChildren) {
  const { user, setSessionLanguageAction } = useAuth();
  const [guestLanguage, setGuestLanguageState] = useState<LanguageCode>(readGuestLanguage);
  const preferredLanguage = normalizeLanguage(user?.preferred_language ?? guestLanguage);
  const language = normalizeLanguage(user?.effective_language ?? guestLanguage);
  const direction = directionForLanguage(language);
  const locale = localeForLanguage(language);
  const textAlign = alignForLanguage(language);

  useEffect(() => {
    persistGuestLanguage(language);
    document.documentElement.lang = language;
    document.documentElement.dir = direction;
    document.documentElement.setAttribute('translate', 'no');
    document.body.dir = direction;
    document.body.style.direction = direction;
    document.body.style.textAlign = textAlign;
    document.body.setAttribute('translate', 'no');
  }, [direction, language, textAlign]);

  const value = useMemo<LanguageContextValue>(
    () => ({
      language,
      direction,
      locale,
      textAlign,
      preferredLanguage,
      setGuestLanguage: (nextLanguage) => {
        persistGuestLanguage(nextLanguage);
        setGuestLanguageState(nextLanguage);
      },
      setSessionLanguage: async (nextLanguage) => {
        persistGuestLanguage(nextLanguage);
        setGuestLanguageState(nextLanguage);
        if (user) {
          await setSessionLanguageAction(nextLanguage);
        }
      },
    }),
    [direction, language, locale, preferredLanguage, setSessionLanguageAction, textAlign, user],
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage(): LanguageContextValue {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
}
