import { 
  LayoutDashboard, 
  CalendarRange, 
  Users, 
  Shirt, 
  Banknote,
  Warehouse, 
  BarChart3, 
  Calculator, 
  ShieldCheck, 
  Settings, 
  LogOut
} from 'lucide-react';
import { AppBar, Box, Button, Drawer, List, ListItemButton, ListItemIcon, ListItemText, Stack, Toolbar, Typography } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { Link as RouterLink, useLocation } from 'react-router-dom';

import { useAuth } from '../features/auth/AuthProvider';
import { useLanguage } from '../features/language/LanguageProvider';
import { LanguageSwitcher } from '../features/language/LanguageSwitcher';
import { userIsAdmin } from '../lib/auth';
import { useNavigationText } from '../text/navigation';
import { BranchSelector } from './BranchSelector';
import { useThemeSettings } from '../features/theme/ThemeSettingsProvider';

const drawerWidth = 260;

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, logoutAction } = useAuth();
  const { direction, textAlign, language } = useLanguage();
  const { 
    sidebarColor, 
    headerColor, 
    sidebarTextColor, 
    primaryColor,
    accentColor,
    bgGradientStart
  } = useThemeSettings();
  const navigationText = useNavigationText();
  const location = useLocation();
  const roleNames = user?.role_names ?? [];
  const isAdmin = userIsAdmin(roleNames);
  const isRtl = direction === 'rtl';

  const appBarOffset = isRtl ? { right: { md: drawerWidth + 32 } } : { left: { md: drawerWidth + 32 } };
  const drawerSide = isRtl ? { right: 16 } : { left: 16 };

  const custodyNavLabel = language === 'ar' ? 'استلام وتسليم الفساتين' : 'Custody & Delivery';

  const navItems = [
    { to: '/dashboard', label: navigationText.dashboard, icon: <LayoutDashboard size={20} /> },
    { to: '/bookings', label: navigationText.pages.bookings, icon: <CalendarRange size={20} /> },
    { to: '/customers', label: navigationText.pages.customers, icon: <Users size={20} /> },
    { to: '/dresses', label: navigationText.pages.dresses, icon: <Shirt size={20} /> },
    { to: '/payments', label: navigationText.pages.payments, icon: <Banknote size={20} /> },
    { to: '/custody', label: custodyNavLabel, icon: <Warehouse size={20} /> },
    { to: '/reports', label: navigationText.pages.reports, icon: <BarChart3 size={20} /> },
    { to: '/accounting', label: navigationText.pages.accounting, icon: <Calculator size={20} /> },
    ...(isAdmin ? [{ to: '/audit', label: navigationText.pages.audit, icon: <ShieldCheck size={20} /> }] : []),
    { to: '/settings', label: navigationText.pages.settings, icon: <Settings size={20} /> },
  ];

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', direction }}>
      <AppBar 
        position='fixed' 
        sx={{ 
          width: { md: `calc(100% - ${drawerWidth}px - 48px)` }, 
          top: 16,
          ...appBarOffset,
          bgcolor: alpha(headerColor || '#FFFFFF', 0.7),
          backdropFilter: 'blur(10px)',
          borderRadius: '16px', // Explicit pixel value for precision
          color: sidebarTextColor || '#2B2C3E',
          mx: 2,
          border: '1px solid rgba(255,255,255,0.3)',
          boxShadow: '0 4px 30px rgba(0, 0, 0, 0.05)',
        }}
      >
        <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', direction, gap: 2 }}>
          <Stack spacing={0.5} sx={{ textAlign }}>
            <Typography variant='h6' sx={{ fontWeight: 800, letterSpacing: -0.5 }}>{navigationText.appTitle}</Typography>
            <Typography variant='caption' sx={{ opacity: 0.6 }}>
              {isAdmin ? navigationText.modeAdmin : navigationText.modeUser}
            </Typography>
          </Stack>
          <Stack direction='row' spacing={2} alignItems='center' sx={{ flexDirection: isRtl ? 'row-reverse' : 'row' }}>
            <LanguageSwitcher authenticated />
            <BranchSelector />
            <Stack spacing={0} sx={{ textAlign: isRtl ? 'left' : 'right', px: 1 }}>
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
              sx={{ borderRadius: 50, borderColor: 'rgba(0,0,0,0.1)', textTransform: 'none' }}
            >
              {navigationText.logout}
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>

      <Drawer
        variant='permanent'
        anchor={isRtl ? 'right' : 'left'}
        sx={{
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
            bgcolor: alpha(sidebarColor || '#FFFFFF', 0.7),
            backdropFilter: 'blur(20px)',
            color: sidebarTextColor,
            borderRadius: '20px', // Explicit pixel value for precision
            border: '1px solid rgba(255,255,255,0.3)',
            boxShadow: '4px 0 32px 0 rgba(0,0,0,0.05)',
            overflowX: 'hidden',
          },
        }}
      >
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h5" sx={{ fontWeight: 900, color: primaryColor, letterSpacing: -1.5 }}>
            MYATELIER
          </Typography>
        </Box>
        <Box sx={{ overflow: 'auto', flex: 1, px: 2 }}>
          <List sx={{ pt: 0 }}>
            {navItems.map((item) => (
              <ListItemButton
                key={item.to}
                component={RouterLink}
                to={item.to}
                selected={location.pathname === item.to}
                sx={{ 
                  borderRadius: 50, // Pill shaped
                  mb: 1, 
                  px: 2.5,
                  py: 1.5,
                  flexDirection: isRtl ? 'row-reverse' : 'row', 
                  justifyContent: 'flex-start', 
                  textAlign,
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&.Mui-selected': {
                    bgcolor: accentColor || '#DFFF00',
                    color: '#000',
                    boxShadow: `0 4px 20px ${alpha(accentColor || '#DFFF00', 0.5)}`,
                    '& .MuiListItemIcon-root': {
                      color: '#000',
                    },
                    '&:hover': {
                      bgcolor: accentColor || '#DFFF00',
                      opacity: 0.9,
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
      </Drawer>

      <Box component='main' sx={{ flexGrow: 1, p: 4, pt: 14, direction }}>
        {children}
      </Box>
    </Box>
  );
}
