import ApartmentOutlinedIcon from '@mui/icons-material/ApartmentOutlined';
import { FormControl, InputAdornment, InputLabel, MenuItem, Select } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';

import { useAuth } from '../features/auth/AuthProvider';
import { useLanguage } from '../features/language/LanguageProvider';
import { getCompany, setActiveBranch } from '../features/settings/api';
import { queryClient } from '../lib/queryClient';
import { useCommonText } from '../text/common';

const keysToRefresh = [
  ['auth', 'me'],
  ['bookings'],
  ['payments'],
  ['dashboard', 'finance'],
  ['reports', 'overview'],
];

export function BranchSelector() {
  const { user, refreshMe } = useAuth();
  const { direction } = useLanguage();
  const commonText = useCommonText();
  const companyQuery = useQuery({ queryKey: ['settings', 'company'], queryFn: getCompany });

  const mutation = useMutation({
    mutationFn: setActiveBranch,
    onSuccess: async () => {
      for (const key of keysToRefresh) {
        await queryClient.invalidateQueries({ queryKey: key });
      }
      await refreshMe();
    },
  });

  const branches = (companyQuery.data?.branches ?? []).filter((branch) => branch.is_active);
  if (!branches.length) {
    return null;
  }

  return (
    <FormControl size='small' sx={{ minWidth: 220 }}>
      <InputLabel id='branch-selector-label'>{commonText.branch}</InputLabel>
      <Select
        labelId='branch-selector-label'
        value={user?.active_branch_id ?? ''}
        label={commonText.branch}
        onChange={(event) => void mutation.mutateAsync({ branch_id: event.target.value })}
        sx={{ direction }}
        startAdornment={
          <InputAdornment position='start'>
            <ApartmentOutlinedIcon fontSize='small' />
          </InputAdornment>
        }
      >
        {branches.map((branch) => (
          <MenuItem key={branch.id} value={branch.id}>
            {`${branch.name} (${branch.code})`}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
