import { Stack } from '@mui/material';
import { useQuery } from '@tanstack/react-query';

import { listDepartments } from '../api';
import { ServicesSection } from '../ServicesSection';

export function CatalogServicesView() {
  const departmentsQuery = useQuery({ queryKey: ['catalog', 'departments'], queryFn: listDepartments });
  const departments = departmentsQuery.data ?? [];

  return (
    <Stack spacing={3}>
      <ServicesSection departments={departments} />
    </Stack>
  );
}
