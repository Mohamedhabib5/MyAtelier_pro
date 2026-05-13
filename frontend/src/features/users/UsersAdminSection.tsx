import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import { Button, Chip, Stack, Tooltip, IconButton } from '@mui/material';
import { Snowflake, Flame } from 'lucide-react';

import { AppDataTable } from '../../components/data-table/AppDataTable';
import { SectionCard } from '../../components/SectionCard';
import { type LanguageCode } from '../../lib/language';
import { useCommonText } from '../../text/common';
import { useUsersText, userRoleLabel } from '../../text/users';
import { type UserRecord } from './api';

type Props = {
  rows: UserRecord[];
  language: LanguageCode;
  currentLanguage: LanguageCode;
  usersText: ReturnType<typeof useUsersText>;
  commonText: ReturnType<typeof useCommonText>;
  onEditUser: (targetUser: UserRecord) => void;
  onFreezeUser: (userId: string, until?: string) => void;
  onUnfreezeUser: (userId: string) => void;
};

export function UsersAdminSection({ 
  rows, language, currentLanguage, usersText, commonText, 
  onEditUser, onFreezeUser, onUnfreezeUser 
}: Props) {
  const tableLabels =
    language === 'ar'
      ? {
          search: 'بحث',
          searchPlaceholder: 'ابحث باسم المستخدم أو الاسم الكامل أو الدور',
          filters: 'الفلاتر',
          columns: 'الأعمدة',
          export: 'تصدير',
          reset: 'إعادة الضبط',
          noRows: 'لا توجد بيانات مطابقة',
          rowsPerPage: 'عدد الصفوف',
          close: 'إغلاق',
        }
      : {
          search: 'Search',
          searchPlaceholder: 'Search by username, full name, or role',
          filters: 'Filters',
          columns: 'Columns',
          export: 'Export',
          reset: 'Reset',
          noRows: 'No matching rows',
          rowsPerPage: 'Rows per page',
          close: 'Close',
        };

  return (
    <SectionCard title={usersText.admin.listTitle} subtitle={usersText.admin.listSubtitle}>
      <AppDataTable
        tableKey='users-admin-list'
        rows={rows}
        columns={[
          { key: 'username', header: usersText.fields.username, searchValue: (row) => row.username, render: (row) => row.username },
          { key: 'full_name', header: usersText.fields.fullName, searchValue: (row) => row.full_name, render: (row) => row.full_name },
          {
            key: 'role_names',
            header: usersText.fields.role,
            searchValue: (row) => row.role_names.join(' '),
            render: (row) => (
              <Stack direction='row' spacing={1} flexWrap='wrap' useFlexGap>
                {row.role_names.map((roleName) => (
                  <Chip key={roleName} label={userRoleLabel(currentLanguage, roleName)} size='small' />
                ))}
              </Stack>
            ),
          },
          {
            key: 'status',
            header: commonText.status,
            searchValue: (row) => (row.is_frozen_until ? 'frozen' : (row.is_active ? usersText.status.active : usersText.status.inactive)),
            render: (row) => {
              const isFrozen = row.is_frozen_until && new Date(row.is_frozen_until) > new Date();
              if (isFrozen) {
                return <Chip label="مجمد" size="small" color="error" variant="filled" icon={<Snowflake size={14} />} />;
              }
              return <Chip label={row.is_active ? usersText.status.active : usersText.status.inactive} size="small" color={row.is_active ? 'success' : 'default'} />;
            }
          },
          {
            key: 'actions',
            header: commonText.actions,
            render: (row) => {
              const isFrozen = row.is_frozen_until && new Date(row.is_frozen_until) > new Date();
              return (
                <Stack direction="row" spacing={1}>
                  <Button startIcon={<EditOutlinedIcon />} onClick={() => onEditUser(row)} size="small">
                    {commonText.edit}
                  </Button>
                  {isFrozen ? (
                    <Tooltip title="فك التجميد">
                      <IconButton size="small" color="success" onClick={() => onUnfreezeUser(row.id)}>
                        <Flame size={18} />
                      </IconButton>
                    </Tooltip>
                  ) : (
                    <Tooltip title="تجميد الحساب">
                      <IconButton size="small" color="error" onClick={() => onFreezeUser(row.id)}>
                        <Snowflake size={18} />
                      </IconButton>
                    </Tooltip>
                  )}
                </Stack>
              );
            }
          },
        ]}
        searchLabel={tableLabels.search}
        searchPlaceholder={tableLabels.searchPlaceholder}
        resetColumnsLabel={tableLabels.reset}
        noRowsLabel={tableLabels.noRows}
        filtersLabel={tableLabels.filters}
        columnsLabel={tableLabels.columns}
        exportLabel={tableLabels.export}
        rowsPerPageLabel={tableLabels.rowsPerPage}
        closeLabel={tableLabels.close}
        searchFields={[(row) => row.username, (row) => row.full_name, (row) => row.role_names.join(' ')]}
      />
    </SectionCard>
  );
}
