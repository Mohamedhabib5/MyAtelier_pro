import { Box, Stack, Tab, Tabs, Typography } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';

export type PageTabItem = {
  label: string;
  path: string;
  subTabs?: { label: string; path: string }[];
};

type PageTabsProps = {
  title: string;
  description?: string;
  tabs: PageTabItem[];
};

export function PageTabs({ title, description, tabs }: PageTabsProps) {
  const location = useLocation();
  const pathParts = location.pathname.split('/').filter(Boolean);
  
  // Find active main tab
  const activeMainTab = tabs.find(tab => {
    const tabParts = tab.path.split('/').filter(Boolean);
    return tabParts.every((part, i) => pathParts[i] === part);
  }) || tabs[0];

  // Find active sub tab
  const activeSubTab = activeMainTab.subTabs?.find(sub => {
    const subParts = sub.path.split('/').filter(Boolean);
    return subParts.every((part, i) => pathParts[i] === part);
  });

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant='h4' sx={{ fontWeight: 700 }}>{title}</Typography>
        {description && <Typography color='text.secondary'>{description}</Typography>}
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={activeMainTab.path} 
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': {
              fontWeight: 600,
              fontSize: '1rem',
              minHeight: 56,
            }
          }}
        >
          {tabs.map((tab) => (
            <Tab 
              key={tab.path} 
              label={tab.label} 
              value={tab.path} 
              component={Link} 
              to={tab.path} 
            />
          ))}
        </Tabs>
      </Box>

      {activeMainTab.subTabs && (
        <Box sx={{ bgcolor: 'background.paper', borderRadius: 1, p: 0.5, display: 'inline-flex', alignSelf: 'flex-start' }}>
          <Tabs 
            value={activeSubTab?.path ?? activeMainTab.subTabs[0].path}
            sx={{
              minHeight: 40,
              '& .MuiTabs-indicator': { display: 'none' },
              '& .MuiTab-root': {
                minHeight: 32,
                borderRadius: 1,
                mx: 0.5,
                fontSize: '0.875rem',
                fontWeight: 500,
                color: 'text.secondary',
                '&.Mui-selected': {
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                },
              }
            }}
          >
            {activeMainTab.subTabs.map((sub) => (
              <Tab 
                key={sub.path} 
                label={sub.label} 
                value={sub.path} 
                component={Link} 
                to={sub.path} 
              />
            ))}
          </Tabs>
        </Box>
      )}
    </Stack>
  );
}
