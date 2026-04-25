import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined';
import { Alert, Button, MenuItem, Stack, TextField, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useState } from 'react';

import { SectionCard } from '../../components/SectionCard';
import { listDepartments, setDressDepartment } from '../catalog/api';
import { queryClient } from '../../lib/queryClient';
import { useSettingsText } from '../../text/settings';

export function DressDepartmentSection() {
  const settingsText = useSettingsText();
  const [selectedId, setSelectedId] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const departmentsQuery = useQuery({ 
    queryKey: ['catalog', 'departments', 'active'], 
    queryFn: () => listDepartments('active') 
  });

  useEffect(() => {
    if (departmentsQuery.data) {
      const current = departmentsQuery.data.find(d => d.is_dress_department);
      if (current) {
        setSelectedId(current.id);
      }
    }
  }, [departmentsQuery.data]);

  const mutation = useMutation({
    mutationFn: setDressDepartment,
    onSuccess: async () => {
      setMessage(settingsText.operationalDepartments.success);
      setError(null);
      await queryClient.invalidateQueries({ queryKey: ['catalog', 'departments'] });
    },
    onError: (err: Error) => {
      setError(err.message);
      setMessage(null);
    }
  });

  return (
    <SectionCard 
      title={settingsText.operationalDepartments.title} 
      subtitle={settingsText.operationalDepartments.subtitle}
    >
      <Stack spacing={3}>
        {message ? <Alert severity='success'>{message}</Alert> : null}
        {error ? <Alert severity='error'>{error}</Alert> : null}

        <Stack spacing={1}>
          <Typography variant='subtitle2'>
            {settingsText.operationalDepartments.dressesDepartment}
          </Typography>
          <Typography variant='body2' color='text.secondary' sx={{ mb: 1 }}>
            {settingsText.operationalDepartments.dressesDepartmentSubtitle}
          </Typography>
          <TextField
            select
            fullWidth
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
            disabled={departmentsQuery.isLoading}
          >
            <MenuItem value=''>
              <em>{settingsText.operationalDepartments.selectDepartment}</em>
            </MenuItem>
            {(departmentsQuery.data ?? []).map((dept) => (
              <MenuItem key={dept.id} value={dept.id}>
                {dept.name} ({dept.code})
              </MenuItem>
            ))}
          </TextField>
        </Stack>

        <Button
          variant='contained'
          startIcon={<SaveOutlinedIcon />}
          onClick={() => selectedId && void mutation.mutateAsync(selectedId)}
          disabled={mutation.isPending || !selectedId}
          sx={{ alignSelf: 'flex-start' }}
        >
          {settingsText.operationalDepartments.save}
        </Button>
      </Stack>
    </SectionCard>
  );
}
