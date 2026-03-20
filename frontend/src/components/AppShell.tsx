import AccountBalanceOutlinedIcon from '@mui/icons-material/AccountBalanceOutlined';
import AccountCircleOutlinedIcon from '@mui/icons-material/AccountCircleOutlined';
import AssessmentOutlinedIcon from '@mui/icons-material/AssessmentOutlined';
import CheckroomOutlinedIcon from '@mui/icons-material/CheckroomOutlined';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import EventAvailableOutlinedIcon from '@mui/icons-material/EventAvailableOutlined';
import FileDownloadOutlinedIcon from '@mui/icons-material/FileDownloadOutlined';
import GroupsOutlinedIcon from '@mui/icons-material/GroupsOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import PaymentsOutlinedIcon from '@mui/icons-material/PaymentsOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import SpaOutlinedIcon from '@mui/icons-material/SpaOutlined';
import { AppBar, Box, Button, Drawer, List, ListItemButton, ListItemIcon, ListItemText, Stack, Toolbar, Typography } from '@mui/material';
import { Link as RouterLink, useLocation } from 'react-router-dom';

import { useAuth } from '../features/auth/AuthProvider';
import { useLanguage } from '../features/language/LanguageProvider';
import { LanguageSwitcher } from '../features/language/LanguageSwitcher';
import { userIsAdmin } from '../lib/auth';
import { useNavigationText } from '../text/navigation';
import { BranchSelector } from './BranchSelector';

const drawerWidth = 260;

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, logoutAction } = useAuth();
  const { direction, textAlign } = useLanguage();
  const navigationText = useNavigationText();
  const location = useLocation();
  const roleNames = user?.role_names ?? [];
  const isAdmin = userIsAdmin(roleNames);
  const isRtl = direction === 'rtl';
  const appBarOffset = { [isRtl ? 'mr' : 'ml']: { md: `${drawerWidth}px` } };
  const mainOffset = { [isRtl ? 'mr' : 'ml']: { md: `${drawerWidth}px` } };
  const drawerPaperSide = isRtl ? { right: 0, left: 'auto' } : { left: 0, right: 'auto' };
  const usersLabel = isAdmin ? navigationText.usersAdmin : navigationText.usersSelf;

  const navItems = [
    { to: '/dashboard', label: navigationText.dashboard, icon: <DashboardOutlinedIcon /> },
    { to: '/bookings', label: navigationText.pages.bookings, icon: <EventAvailableOutlinedIcon /> },
    { to: '/customers', label: navigationText.pages.customers, icon: <GroupsOutlinedIcon /> },
    { to: '/services', label: navigationText.pages.services, icon: <SpaOutlinedIcon /> },
    { to: '/dresses', label: navigationText.pages.dresses, icon: <CheckroomOutlinedIcon /> },
    { to: '/payments', label: navigationText.pages.payments, icon: <PaymentsOutlinedIcon /> },
    { to: '/reports', label: navigationText.pages.reports, icon: <AssessmentOutlinedIcon /> },
    { to: '/exports', label: navigationText.pages.exports, icon: <FileDownloadOutlinedIcon /> },
    { to: '/accounting', label: navigationText.pages.accounting, icon: <AccountBalanceOutlinedIcon /> },
    { to: '/users', label: usersLabel, icon: <AccountCircleOutlinedIcon /> },
    { to: '/settings', label: navigationText.pages.settings, icon: <SettingsOutlinedIcon /> },
  ];

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'grey.100', direction }}>
      <AppBar position='fixed' sx={{ width: { md: `calc(100% - ${drawerWidth}px)` }, ...appBarOffset }}>
        <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', direction, gap: 2 }}>
          <Stack spacing={0.5} sx={{ textAlign }}>
            <Typography variant='h6'>{navigationText.appTitle}</Typography>
            <Typography variant='body2'>{isAdmin ? navigationText.modeAdmin : navigationText.modeUser}</Typography>
          </Stack>
          <Stack direction='row' spacing={2} alignItems='center'>
            <LanguageSwitcher authenticated />
            <BranchSelector />
            <Stack spacing={0} sx={{ textAlign }}>
              <Typography variant='body2'>{user?.full_name}</Typography>
              <Typography variant='caption' color='inherit'>
                {user?.active_branch_name}
              </Typography>
            </Stack>
            <Button color='inherit' startIcon={<LogoutOutlinedIcon />} onClick={() => void logoutAction()}>
              {navigationText.logout}
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>

      <Drawer
        anchor={isRtl ? 'right' : 'left'}
        variant='permanent'
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          ['& .MuiDrawer-paper']: {
            width: drawerWidth,
            boxSizing: 'border-box',
            ...drawerPaperSide,
            textAlign,
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto', p: 2, direction, textAlign }}>
          <Typography variant='subtitle2' color='text.secondary' sx={{ mb: 2, textAlign }}>
            {navigationText.navTitle}
          </Typography>
          <List>
            {navItems.map((item) => (
              <ListItemButton
                key={item.to}
                component={RouterLink}
                to={item.to}
                selected={location.pathname === item.to}
                sx={{ borderRadius: 2, mb: 1, flexDirection: isRtl ? 'row-reverse' : 'row', justifyContent: 'flex-start', textAlign }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    ...(isRtl ? { ml: 1.5, mr: 0 } : { mr: 1.5, ml: 0 }),
                    justifyContent: 'center',
                    color: 'inherit',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.label} slotProps={{ primary: { sx: { textAlign, fontWeight: 500 } } }} />
              </ListItemButton>
            ))}
          </List>
        </Box>
      </Drawer>

      <Box component='main' sx={{ flexGrow: 1, p: 3, ...mainOffset, textAlign }}>
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
}
