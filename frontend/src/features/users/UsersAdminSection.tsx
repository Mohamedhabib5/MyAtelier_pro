import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import { Button, Chip, Stack } from '@mui/material';

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
};

export function UsersAdminSection({ rows, language, currentLanguage, usersText, commonText, onEditUser }: Props) {
  const tableLabels =
    language === 'ar'
      ? {
          search: 'ط¨ط­ط«',
          searchPlaceholder: 'ط§ط¨ط­ط« ط¨ط§ط³ظ… ط§ظ„ظ…ط³طھط®ط¯ظ… ط£ظˆ ط§ظ„ط§ط³ظ… ط§ظ„ظƒط§ظ…ظ„ ط£ظˆ ط§ظ„ط¯ظˆط±',
          filters: 'ط§ظ„ظپظ„ط§طھط±',
          columns: 'ط§ظ„ط£ط¹ظ…ط¯ط©',
          export: 'طھطµط¯ظٹط±',
          reset: 'ط¥ط¹ط§ط¯ط© ط§ظ„ط¶ط¨ط·',
          noRows: 'ظ„ط§ طھظˆط¬ط¯ ط¨ظٹط§ظ†ط§طھ ظ…ط·ط§ط¨ظ‚ط©',
          rowsPerPage: 'ط¹ط¯ط¯ ط§ظ„طµظپظˆظپ',
          close: 'ط¥ط؛ظ„ط§ظ‚',
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
            searchValue: (row) => (row.is_active ? usersText.status.active : usersText.status.inactive),
            render: (row) => <Chip label={row.is_active ? usersText.status.active : usersText.status.inactive} size='small' color={row.is_active ? 'success' : 'default'} />,
          },
          {
            key: 'actions',
            header: commonText.actions,
            render: (row) => (
              <Button startIcon={<EditOutlinedIcon />} onClick={() => onEditUser(row)}>
                {commonText.edit}
              </Button>
            ),
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
