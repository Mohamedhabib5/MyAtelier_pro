import { Stack } from '@mui/material';
import { Outlet } from 'react-router-dom';

import { PageTabs, type PageTabItem } from '../components/navigation/PageTabs';
import { useSettingsText } from '../text/settings';

export function SettingsPage() {
  const settingsText = useSettingsText();

  const tabs: PageTabItem[] = [
    {
      label: settingsText.tabs.general,
      path: '/settings/general',
      subTabs: [
        { label: settingsText.tabs.company, path: '/settings/general/company' },
        { label: settingsText.tabs.backups, path: '/settings/general/backups' },
        { label: settingsText.tabs.financial, path: '/settings/general/financial' },
      ]
    },
    {
      label: settingsText.tabs.catalog,
      path: '/settings/catalog',
      subTabs: [
        { label: settingsText.tabs.departments, path: '/settings/catalog/departments' },
        { label: settingsText.tabs.services, path: '/settings/catalog/services' },
      ]
    },
    {
      label: settingsText.tabs.security,
      path: '/settings/security',
      subTabs: [
        { label: settingsText.tabs.users, path: '/settings/security/users' },
      ]
    },
    {
      label: settingsText.tabs.data,
      path: '/settings/data',
      subTabs: [
        { label: settingsText.tabs.exports, path: '/settings/data/exports' },
      ]
    }
  ];

  return (
    <Stack spacing={4}>
      <PageTabs 
        title={settingsText.page.title} 
        description={settingsText.page.description} 
        tabs={tabs} 
      />
      <Outlet />
    </Stack>
  );
}
