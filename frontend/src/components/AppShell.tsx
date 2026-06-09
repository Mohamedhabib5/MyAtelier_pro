import { 
  LayoutDashboard, 
  CalendarRange, 
  CalendarDays,
  Users, 
  Shirt, 
  Banknote,
  Warehouse, 
  BarChart3, 
  LineChart,
  Calculator, 
  ShieldCheck, 
  Settings, 
  LogOut,
  Menu,
  Database
} from 'lucide-react';
import { AppBar, Box, Button, Drawer, IconButton, List, ListItemButton, ListItemIcon, ListItemText, Stack, Toolbar, Typography, useMediaQuery, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { useState } from 'react';

import { useAuth } from '../features/auth/AuthProvider';
import { useLanguage } from '../features/language/LanguageProvider';
import { LanguageSwitcher } from '../features/language/LanguageSwitcher';
import { userIsAdmin } from '../lib/auth';
import { useNavigationText } from '../text/navigation';
import { BranchSelector } from './BranchSelector';
import { useThemeSettings } from '../features/theme/ThemeSettingsProvider';
import { UniversalSearch } from './navigation/UniversalSearch';

const drawerWidth = 260;

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, logoutAction } = useAuth();
  const { direction, textAlign, language } = useLanguage();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  
  const { 
    sidebarColor, 
    sidebarColorEnd,
    headerColor, 
    headerColorEnd,
    sidebarTextColor, 
    primaryColor,
    accentColor,
    bgGradientStart,
    themeMode
  } = useThemeSettings();
  const navigationText = useNavigationText();
  const location = useLocation();
  const roleNames = user?.role_names ?? [];
  const isAdmin = userIsAdmin(roleNames);
  const isRtl = direction === 'rtl';

  const appBarOffset = isRtl 
    ? { right: { md: drawerWidth + 32 } } 
    : { left: { md: drawerWidth + 32 } };
  
  const drawerSide = isRtl ? { right: isMobile ? 0 : 16 } : { left: isMobile ? 0 : 16 };
  const isDark = themeMode === 'dark';
  const defaultBg = isDark ? '#1a1b26' : '#FFFFFF';
  const defaultText = isDark ? '#e0e0e0' : '#2B2C3E';

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const custodyNavLabel = language === 'ar' ? 'استلام وتسليم الفساتين' : 'Custody & Delivery';

  const navItems = [
    { to: '/dashboard', label: navigationText.dashboard, icon: <LayoutDashboard size={20} /> },
    { to: '/bookings', label: navigationText.pages.bookings, icon: <CalendarRange size={20} /> },
    { to: '/calendar', label: navigationText.pages.calendar, icon: <CalendarDays size={20} /> },
    { to: '/customers', label: navigationText.pages.customers, icon: <Users size={20} /> },
    { to: '/dresses', label: navigationText.pages.dresses, icon: <Shirt size={20} /> },
    { to: '/payments', label: navigationText.pages.payments, icon: <Banknote size={20} /> },
    { to: '/disbursements', label: navigationText.pages.disbursements, icon: <Banknote size={20} /> },
    { to: '/custody', label: custodyNavLabel, icon: <Warehouse size={20} /> },
    { to: '/reports', label: navigationText.pages.reports, icon: <BarChart3 size={20} /> },
    { to: '/analytics', label: navigationText.pages.analytics, icon: <LineChart size={20} /> },
    { to: '/accounting', label: navigationText.pages.accounting, icon: <Calculator size={20} /> },
    ...(isAdmin ? [
      { to: '/audit', label: navigationText.pages.audit, icon: <ShieldCheck size={20} /> },
      { to: '/ops/backups', label: language === 'ar' ? 'النسخ الاحتياطي' : 'Backups', icon: <Database size={20} /> }
    ] : []),
    { to: '/settings', label: navigationText.pages.settings, icon: <Settings size={20} /> },
  ];

  const drawerContent = (
    <>
      <Box sx={{ p: 3, textAlign: 'center', mb: 2 }}>
        <Typography 
          variant="h5" 
          sx={{ 
            fontWeight: 1000, 
            background: `linear-gradient(135deg, ${primaryColor}, ${alpha(primaryColor, 0.7)})`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: -1.8,
            textTransform: 'uppercase',
            filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))'
          }}
        >
          MyAtelier
        </Typography>
        <Typography variant="caption" sx={{ opacity: 0.4, fontWeight: 700, letterSpacing: 2, display: 'block', mt: -0.5 }}>
          PRO EDITION
        </Typography>
      </Box>
      
      {isMobile && (
        <Box sx={{ px: 2, pb: 2, textAlign }}>
          <Stack spacing={1.5} sx={{ p: 1.5, bgcolor: alpha(primaryColor, 0.05), borderRadius: 4 }}>
            <Box>
              <Typography variant='subtitle1' sx={{ fontWeight: 800 }}>{user?.full_name}</Typography>
              <Typography variant='caption' sx={{ opacity: 0.6 }}>{user?.username}</Typography>
            </Box>
            <BranchSelector />
          </Stack>
        </Box>
      )}

      <Box sx={{ overflow: 'auto', flex: 1, px: 2 }}>
        <List sx={{ pt: 0 }}>
          {navItems.map((item) => (
            <ListItemButton
              key={item.to}
              component={RouterLink}
              to={item.to}
              selected={location.pathname === item.to}
              onClick={() => isMobile && setMobileOpen(false)}
              sx={{ 
                borderRadius: 50, 
                mb: 0.5, 
                px: 2,
                py: 1,
                flexDirection: isRtl ? 'row-reverse' : 'row', 
                justifyContent: 'flex-start', 
                textAlign,
                transition: 'background-color 0.2s ease, color 0.2s ease, transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                '&.Mui-selected': {
                  bgcolor: isDark ? alpha(accentColor || '#DFFF00', 0.15) : alpha(accentColor || '#DFFF00', 0.1),
                  color: isDark ? (accentColor || '#DFFF00') : '#000',
                  boxShadow: `inset 0 0 0 1px ${alpha(accentColor || '#DFFF00', 0.3)}`,
                  '& .MuiListItemIcon-root': {
                    color: accentColor || '#DFFF00',
                    transform: 'scale(1.1)',
                  },
                  '& .MuiListItemText-root span': {
                    fontWeight: 900,
                  },
                  '&::after': {
                    content: '""',
                    position: 'absolute',
                    ...(isRtl ? { right: 0 } : { left: 0 }),
                    top: '20%',
                    bottom: '20%',
                    width: 4,
                    borderRadius: 4,
                    bgcolor: accentColor || '#DFFF00',
                    boxShadow: `0 0 12px ${accentColor || '#DFFF00'}`,
                  },
                  '&:hover': {
                    bgcolor: isDark ? alpha(accentColor || '#DFFF00', 0.2) : alpha(accentColor || '#DFFF00', 0.15),
                  },
                },
                '&:hover': {
                  bgcolor: alpha(sidebarTextColor || '#2B2C3E', 0.05),
                  transform: isRtl ? 'translateX(-4px)' : 'translateX(4px)',
                }
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  ...(isRtl ? { ml: 2, mr: 0 } : { mr: 2, ml: 0 }),
                  justifyContent: 'center',
                  color: 'inherit',
                  opacity: 0.8,
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.label} 
                slotProps={{ 
                  primary: { 
                    sx: { 
                      textAlign, 
                      fontWeight: location.pathname === item.to ? 800 : 500,
                      fontSize: '1rem',
                      letterSpacing: -0.2
                    } 
                  } 
                }} 
              />
            </ListItemButton>
          ))}
        </List>
      </Box>
      
      {isMobile && (
        <Box sx={{ p: 2 }}>
          <Button 
            fullWidth
            color='error' 
            variant="outlined"
            startIcon={<LogOut size={18} />} 
            onClick={() => void logoutAction()}
            sx={{ borderRadius: 3, py: 1.5, textTransform: 'none' }}
          >
            {navigationText.logout}
          </Button>
        </Box>
      )}
    </>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', direction }}>
      <AppBar 
        position='fixed' 
        sx={{ 
          width: { md: `calc(100% - ${drawerWidth}px - 64px)` }, 
          top: { xs: 0, md: 16 }, 
          ...appBarOffset,
          background: `linear-gradient(135deg, ${alpha(headerColor || defaultBg, 0.95)}, ${alpha(headerColorEnd || headerColor || defaultBg, 0.9)}) !important`,
          backdropFilter: 'blur(20px)',
          borderRadius: { xs: 0, md: '20px' },
          color: `${sidebarTextColor || defaultText} !important`,
          mx: { xs: 0, md: 2 },
          border: isDark ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(255,255,255,0.5)',
          boxShadow: isDark ? '0 12px 40px rgba(0, 0, 0, 0.4)' : '0 12px 40px rgba(0, 0, 0, 0.06)',
          zIndex: theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          direction, 
          gap: 1,
          px: { xs: 1.5, md: 2.5 },
          minHeight: { xs: 64, md: 72 } 
        }}>
          <Stack direction="row" alignItems="center" spacing={1}>
            {isMobile && (
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{ mr: 0.5 }}
              >
                <Menu size={22} />
              </IconButton>
            )}
            <Stack spacing={0} sx={{ textAlign }}>
              <Typography variant='h6' sx={{ 
                fontWeight: 900, 
                letterSpacing: -0.5, 
                fontSize: { xs: '1.1rem', md: '1.25rem' },
                color: primaryColor 
              }}>
                {navigationText.appTitle}
              </Typography>
            </Stack>
            {!isMobile && (
              <Box sx={{ ml: 4 }}>
                <UniversalSearch />
              </Box>
            )}
          </Stack>
          
          <Stack direction='row' spacing={{ xs: 0.5, md: 2 }} alignItems='center' sx={{ flexDirection: isRtl ? 'row-reverse' : 'row' }}>
            <LanguageSwitcher authenticated />
            {!isMobile && (
              <>
                <BranchSelector />
                <Stack spacing={0} sx={{ textAlign: isRtl ? 'left' : 'right', px: 1, display: { xs: 'none', lg: 'block' } }}>
                  <Typography variant='subtitle2' sx={{ fontWeight: 700 }}>{user?.full_name}</Typography>
                  <Typography variant='caption' sx={{ opacity: 0.6 }}>
                    {user?.active_branch_name}
                  </Typography>
                </Stack>
                <Button 
                  color='inherit' 
                  variant="outlined"
                  startIcon={<LogOut size={18} />} 
                  onClick={() => void logoutAction()}
                  sx={{ borderRadius: 50, borderColor: 'rgba(0,0,0,0.1)', textTransform: 'none', px: 2 }}
                >
                  {navigationText.logout}
                </Button>
              </>
            )}
          </Stack>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { md: drawerWidth + 32 }, flexShrink: { md: 0 } }}
      >
        {isMobile ? (
          <Drawer
            variant="temporary"
            anchor={isRtl ? 'right' : 'left'}
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{ keepMounted: true }}
            sx={{
              display: { xs: 'block', md: 'none' },
              '& .MuiDrawer-paper': { 
                width: drawerWidth, 
                background: `linear-gradient(180deg, ${alpha(sidebarColor || defaultBg, 0.95)}, ${alpha(sidebarColorEnd || sidebarColor || defaultBg, 0.95)})`,
                boxSizing: 'border-box',
                border: 'none',
                boxShadow: isDark ? 'none' : (isRtl ? '-10px 0 30px rgba(0,0,0,0.1)' : '10px 0 30px rgba(0,0,0,0.1)')
              },
            }}
          >
            {drawerContent}
          </Drawer>
        ) : (
          <Drawer
            variant='permanent'
            anchor={isRtl ? 'right' : 'left'}
            sx={{
              display: { xs: 'none', md: 'block' },
              width: drawerWidth + 32,
              flexShrink: 0,
              ['& .MuiDrawer-paper']: {
                width: drawerWidth,
                boxSizing: 'border-box',
                top: 16,
                bottom: 16,
                height: 'calc(100% - 32px)',
                ...drawerSide,
                textAlign,
                background: `linear-gradient(180deg, ${alpha(sidebarColor || defaultBg, 0.9)}, ${alpha(sidebarColorEnd || sidebarColor || defaultBg, 0.85)}) !important`,
                backdropFilter: 'blur(20px)',
                color: `${sidebarTextColor || defaultText} !important`,
                borderRadius: '20px',
                border: isDark ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(255,255,255,0.4)',
                boxShadow: isDark ? 'none' : '8px 0 40px 0 rgba(0,0,0,0.08)',
                overflowX: 'hidden',
              },
            }}
          >
            {drawerContent}
          </Drawer>
        )}
      </Box>

      <Box component='main' sx={{ 
        flexGrow: 1, 
        p: { xs: 2, sm: 3, md: 4 }, 
        pt: { xs: 11, md: 14 }, 
        direction, 
        width: '100%',
        maxWidth: '100vw',
        overflowX: 'hidden'
      }}>
        {children}
      </Box>
    </Box>
  );
}
