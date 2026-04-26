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
  LogOut,
  Menu
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
    bgGradientStart
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

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

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

  const drawerContent = (
    <>
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h5" sx={{ fontWeight: 900, color: primaryColor, letterSpacing: -1.5 }}>
          MYATELIER
        </Typography>
      </Box>
      
      {isMobile && (
        <Box sx={{ px: 2, pb: 3, textAlign }}>
          <Stack spacing={2} sx={{ p: 2, bgcolor: alpha(primaryColor, 0.05), borderRadius: 4 }}>
            <Box>
              <Typography variant='subtitle1' sx={{ fontWeight: 800 }}>{user?.full_name}</Typography>
              <Typography variant='caption' sx={{ opacity: 0.6 }}>{user?.username}</Typography>
            </Box>
            <BranchSelector fullWidth />
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
      
      {isMobile && (
        <Box sx={{ p: 2 }}>
          <Button 
            fullWidth
            color='error' 
            variant="soft"
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
          width: { md: `calc(100% - ${drawerWidth}px - 48px)` }, 
          top: { xs: 0, md: 16 }, // Stick to top on mobile for more space
          ...appBarOffset,
          background: `linear-gradient(135deg, ${alpha(headerColor || '#FFFFFF', 0.9)}, ${alpha(headerColorEnd || headerColor || '#FFFFFF', 0.85)}) !important`,
          backdropFilter: 'blur(12px)',
          borderRadius: { xs: 0, md: '16px' }, // No radius on mobile to save space
          color: `${sidebarTextColor || '#2B2C3E'} !important`,
          mx: { xs: 0, md: 2 },
          left: { xs: 0, md: 'auto' },
          right: { xs: 0, md: 'auto' },
          border: { xs: 'none', md: '1px solid rgba(255,255,255,0.4)' },
          borderBottom: { xs: '1px solid rgba(0,0,0,0.05)', md: '1px solid rgba(255,255,255,0.4)' },
          boxShadow: { xs: '0 2px 10px rgba(0,0,0,0.03)', md: '0 8px 32px rgba(0, 0, 0, 0.08)' },
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
                background: `linear-gradient(180deg, ${alpha(sidebarColor || '#FFFFFF', 0.95)}, ${alpha(sidebarColorEnd || sidebarColor || '#FFFFFF', 0.95)})`,
                boxSizing: 'border-box',
                border: 'none',
                boxShadow: isRtl ? '-10px 0 30px rgba(0,0,0,0.1)' : '10px 0 30px rgba(0,0,0,0.1)'
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
                background: `linear-gradient(180deg, ${alpha(sidebarColor || '#FFFFFF', 0.9)}, ${alpha(sidebarColorEnd || sidebarColor || '#FFFFFF', 0.85)}) !important`,
                backdropFilter: 'blur(20px)',
                color: `${sidebarTextColor || '#2B2C3E'} !important`,
                borderRadius: '20px',
                border: '1px solid rgba(255,255,255,0.4)',
                boxShadow: '8px 0 40px 0 rgba(0,0,0,0.08)',
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
