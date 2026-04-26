import { createContext, useContext, useState, useEffect, PropsWithChildren } from 'react';
import { DEFAULT_PRIMARY, DEFAULT_SECONDARY } from '../../app/theme';

interface ThemeSettingsContextType {
  primaryColor: string;
  secondaryColor: string;
  sidebarColor: string;
  headerColor: string;
  sidebarTextColor: string;
  bgGradientStart: string;
  bgGradientEnd: string;
  accentColor: string;
  setPrimaryColor: (color: string) => void;
  setSecondaryColor: (color: string) => void;
  setSidebarColor: (color: string) => void;
  setHeaderColor: (color: string) => void;
  setSidebarTextColor: (color: string) => void;
  setBgGradientStart: (color: string) => void;
  setBgGradientEnd: (color: string) => void;
  setAccentColor: (color: string) => void;
  resetTheme: () => void;
}

const ThemeSettingsContext = createContext<ThemeSettingsContextType | undefined>(undefined);

const STORAGE_KEY_PRIMARY = 'myatelier_theme_primary';
const STORAGE_KEY_SECONDARY = 'myatelier_theme_secondary';
const STORAGE_KEY_SIDEBAR = 'myatelier_theme_sidebar';
const STORAGE_KEY_HEADER = 'myatelier_theme_header';
const STORAGE_KEY_SIDEBAR_TEXT = 'myatelier_theme_sidebar_text';
const STORAGE_KEY_BG_START = 'myatelier_theme_bg_start';
const STORAGE_KEY_BG_END = 'myatelier_theme_bg_end';
const STORAGE_KEY_ACCENT = 'myatelier_theme_accent';

const DEFAULT_BG_START = '#E2E8F0';
const DEFAULT_BG_END = '#CBD5E1';
const DEFAULT_ACCENT = '#DFFF00'; // Neon Lime

export function ThemeSettingsProvider({ children }: PropsWithChildren) {
  const [primaryColor, setPrimaryColor] = useState(() => 
    localStorage.getItem(STORAGE_KEY_PRIMARY) || DEFAULT_PRIMARY
  );
  const [secondaryColor, setSecondaryColor] = useState(() => 
    localStorage.getItem(STORAGE_KEY_SECONDARY) || DEFAULT_SECONDARY
  );
  const [sidebarColor, setSidebarColor] = useState(() => 
    localStorage.getItem(STORAGE_KEY_SIDEBAR) || '#FFFFFF'
  );
  const [headerColor, setHeaderColor] = useState(() => 
    localStorage.getItem(STORAGE_KEY_HEADER) || '#FFFFFF'
  );
  const [sidebarTextColor, setSidebarTextColor] = useState(() => 
    localStorage.getItem(STORAGE_KEY_SIDEBAR_TEXT) || '#2B2C3E'
  );
  const [bgGradientStart, setBgGradientStart] = useState(() => 
    localStorage.getItem(STORAGE_KEY_BG_START) || DEFAULT_BG_START
  );
  const [bgGradientEnd, setBgGradientEnd] = useState(() => 
    localStorage.getItem(STORAGE_KEY_BG_END) || DEFAULT_BG_END
  );
  const [accentColor, setAccentColor] = useState(() => 
    localStorage.getItem(STORAGE_KEY_ACCENT) || DEFAULT_ACCENT
  );

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_PRIMARY, primaryColor);
  }, [primaryColor]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_SECONDARY, secondaryColor);
  }, [secondaryColor]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_SIDEBAR, sidebarColor);
  }, [sidebarColor]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_HEADER, headerColor);
  }, [headerColor]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_SIDEBAR_TEXT, sidebarTextColor);
  }, [sidebarTextColor]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_BG_START, bgGradientStart);
  }, [bgGradientStart]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_BG_END, bgGradientEnd);
  }, [bgGradientEnd]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_ACCENT, accentColor);
  }, [accentColor]);

  const resetTheme = () => {
    setPrimaryColor(DEFAULT_PRIMARY);
    setSecondaryColor(DEFAULT_SECONDARY);
    setSidebarColor('#FFFFFF');
    setHeaderColor('#FFFFFF');
    setSidebarTextColor('#2B2C3E');
    setBgGradientStart(DEFAULT_BG_START);
    setBgGradientEnd(DEFAULT_BG_END);
    setAccentColor(DEFAULT_ACCENT);
  };

  return (
    <ThemeSettingsContext.Provider value={{ 
      primaryColor, 
      secondaryColor,
      sidebarColor,
      headerColor,
      sidebarTextColor,
      bgGradientStart,
      bgGradientEnd,
      accentColor,
      setPrimaryColor, 
      setSecondaryColor,
      setSidebarColor,
      setHeaderColor,
      setSidebarTextColor,
      setBgGradientStart,
      setBgGradientEnd,
      setAccentColor,
      resetTheme
    }}>
      {children}
    </ThemeSettingsContext.Provider>
  );
}

export function useThemeSettings() {
  const context = useContext(ThemeSettingsContext);
  if (!context) {
    throw new Error('useThemeSettings must be used within a ThemeSettingsProvider');
  }
  return context;
}
