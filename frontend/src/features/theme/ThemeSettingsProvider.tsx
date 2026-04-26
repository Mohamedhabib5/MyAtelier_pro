import { createContext, useContext, useState, useEffect, PropsWithChildren, useCallback, useRef } from 'react';
import { DEFAULT_PRIMARY, DEFAULT_SECONDARY } from '../../app/theme';
import { useAuth } from '../auth/AuthProvider';
import { apiRequest } from '../../lib/api';

interface ThemeSettingsContextType {
  primaryColor: string;
  secondaryColor: string;
  sidebarColor: string;
  sidebarColorEnd: string;
  headerColor: string;
  headerColorEnd: string;
  sidebarTextColor: string;
  bgGradientStart: string;
  bgGradientEnd: string;
  accentColor: string;
  setPrimaryColor: (color: string) => void;
  setSecondaryColor: (color: string) => void;
  setSidebarColor: (color: string) => void;
  setSidebarColorEnd: (color: string) => void;
  setHeaderColor: (color: string) => void;
  setHeaderColorEnd: (color: string) => void;
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
const STORAGE_KEY_SIDEBAR_END = 'myatelier_theme_sidebar_end';
const STORAGE_KEY_HEADER = 'myatelier_theme_header';
const STORAGE_KEY_HEADER_END = 'myatelier_theme_header_end';
const STORAGE_KEY_SIDEBAR_TEXT = 'myatelier_theme_sidebar_text';
const STORAGE_KEY_BG_START = 'myatelier_theme_bg_start';
const STORAGE_KEY_BG_END = 'myatelier_theme_bg_end';
const STORAGE_KEY_ACCENT = 'myatelier_theme_accent';

const DEFAULT_BG_START = '#E2E8F0';
const DEFAULT_BG_END = '#CBD5E1';
const DEFAULT_ACCENT = '#DFFF00'; // Neon Lime

export function ThemeSettingsProvider({ children }: PropsWithChildren) {
  const { user } = useAuth();
  
  const [primaryColor, setPrimaryColor] = useState(() => localStorage.getItem(STORAGE_KEY_PRIMARY) || DEFAULT_PRIMARY);
  const [secondaryColor, setSecondaryColor] = useState(() => localStorage.getItem(STORAGE_KEY_SECONDARY) || DEFAULT_SECONDARY);
  const [sidebarColor, setSidebarColor] = useState(() => localStorage.getItem(STORAGE_KEY_SIDEBAR) || '#FFFFFF');
  const [sidebarColorEnd, setSidebarColorEnd] = useState(() => localStorage.getItem(STORAGE_KEY_SIDEBAR_END) || '#FFFFFF');
  const [headerColor, setHeaderColor] = useState(() => localStorage.getItem(STORAGE_KEY_HEADER) || '#FFFFFF');
  const [headerColorEnd, setHeaderColorEnd] = useState(() => localStorage.getItem(STORAGE_KEY_HEADER_END) || '#FFFFFF');
  const [sidebarTextColor, setSidebarTextColor] = useState(() => localStorage.getItem(STORAGE_KEY_SIDEBAR_TEXT) || '#2B2C3E');
  const [bgGradientStart, setBgGradientStart] = useState(() => localStorage.getItem(STORAGE_KEY_BG_START) || DEFAULT_BG_START);
  const [bgGradientEnd, setBgGradientEnd] = useState(() => localStorage.getItem(STORAGE_KEY_BG_END) || DEFAULT_BG_END);
  const [accentColor, setAccentColor] = useState(() => localStorage.getItem(STORAGE_KEY_ACCENT) || DEFAULT_ACCENT);

  const isFirstRender = useRef(true);
  const isUpdatingFromBackend = useRef(false);

  // Persistence to localStorage
  useEffect(() => { localStorage.setItem(STORAGE_KEY_PRIMARY, primaryColor); }, [primaryColor]);
  useEffect(() => { localStorage.setItem(STORAGE_KEY_SECONDARY, secondaryColor); }, [secondaryColor]);
  useEffect(() => { localStorage.setItem(STORAGE_KEY_SIDEBAR, sidebarColor); }, [sidebarColor]);
  useEffect(() => { localStorage.setItem(STORAGE_KEY_SIDEBAR_END, sidebarColorEnd); }, [sidebarColorEnd]);
  useEffect(() => { localStorage.setItem(STORAGE_KEY_HEADER, headerColor); }, [headerColor]);
  useEffect(() => { localStorage.setItem(STORAGE_KEY_HEADER_END, headerColorEnd); }, [headerColorEnd]);
  useEffect(() => { localStorage.setItem(STORAGE_KEY_SIDEBAR_TEXT, sidebarTextColor); }, [sidebarTextColor]);
  useEffect(() => { localStorage.setItem(STORAGE_KEY_BG_START, bgGradientStart); }, [bgGradientStart]);
  useEffect(() => { localStorage.setItem(STORAGE_KEY_BG_END, bgGradientEnd); }, [bgGradientEnd]);
  useEffect(() => { localStorage.setItem(STORAGE_KEY_ACCENT, accentColor); }, [accentColor]);

  // Sync with Backend
  const saveToBackend = useCallback(async () => {
    if (!user || isUpdatingFromBackend.current) return;
    try {
      const themeData = {
        primaryColor, secondaryColor, sidebarColor, sidebarColorEnd, 
        headerColor, headerColorEnd,
        sidebarTextColor, bgGradientStart, bgGradientEnd, accentColor
      };
      await apiRequest('/api/users/me/theme-preferences', {
        method: 'PUT',
        body: JSON.stringify({ theme_json: JSON.stringify(themeData) })
      });
    } catch (err) {
      console.error('Failed to save theme preferences to backend:', err);
    }
  }, [user, primaryColor, secondaryColor, sidebarColor, sidebarColorEnd, headerColor, headerColorEnd, sidebarTextColor, bgGradientStart, bgGradientEnd, accentColor]);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    const timer = setTimeout(() => {
      saveToBackend();
    }, 1000); // Debounce saves
    return () => clearTimeout(timer);
  }, [saveToBackend]);

  useEffect(() => {
    const fetchFromBackend = async () => {
      if (!user) return;
      try {
        const response = await apiRequest<{ theme_json: string }>('/api/users/me/theme-preferences');
        if (response.theme_json && response.theme_json !== '{}') {
          const data = JSON.parse(response.theme_json);
          isUpdatingFromBackend.current = true;
          if (data.primaryColor) setPrimaryColor(data.primaryColor);
          if (data.secondaryColor) setSecondaryColor(data.secondaryColor);
          if (data.sidebarColor) setSidebarColor(data.sidebarColor);
          if (data.sidebarColorEnd) setSidebarColorEnd(data.sidebarColorEnd);
          if (data.headerColor) setHeaderColor(data.headerColor);
          if (data.headerColorEnd) setHeaderColorEnd(data.headerColorEnd);
          if (data.sidebarTextColor) setSidebarTextColor(data.sidebarTextColor);
          if (data.bgGradientStart) setBgGradientStart(data.bgGradientStart);
          if (data.bgGradientEnd) setBgGradientEnd(data.bgGradientEnd);
          if (data.accentColor) setAccentColor(data.accentColor);
          setTimeout(() => { isUpdatingFromBackend.current = false; }, 100);
        }
      } catch (err) {
        console.error('Failed to fetch theme preferences from backend:', err);
      }
    };
    fetchFromBackend();
  }, [user]);

  const resetTheme = () => {
    setPrimaryColor(DEFAULT_PRIMARY);
    setSecondaryColor(DEFAULT_SECONDARY);
    setSidebarColor('#FFFFFF');
    setSidebarColorEnd('#FFFFFF');
    setHeaderColor('#FFFFFF');
    setHeaderColorEnd('#FFFFFF');
    setSidebarTextColor('#2B2C3E');
    setBgGradientStart(DEFAULT_BG_START);
    setBgGradientEnd(DEFAULT_BG_END);
    setAccentColor(DEFAULT_ACCENT);
  };

  return (
    <ThemeSettingsContext.Provider value={{ 
      primaryColor, secondaryColor, sidebarColor, sidebarColorEnd, headerColor, headerColorEnd, sidebarTextColor,
      bgGradientStart, bgGradientEnd, accentColor,
      setPrimaryColor, setSecondaryColor, setSidebarColor, setSidebarColorEnd, setHeaderColor, setHeaderColorEnd, setSidebarTextColor, 
      setBgGradientStart, setBgGradientEnd, setAccentColor,
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
