import { Stack } from '@mui/material';
import { useQuery } from '@tanstack/react-query';

import { listDepartments } from '../api';
import { DepartmentsSection } from '../DepartmentsSection';
import { DressDepartmentSection } from '../../settings/DressDepartmentSection';

export function CatalogDepartmentsView() {
  const departmentsQuery = useQuery({ queryKey: ['catalog', 'departments'], queryFn: listDepartments });
  const departments = departmentsQuery.data ?? [];

  return (
    <Stack spacing={3}>
      <DepartmentsSection departments={departments} />
      <DressDepartmentSection />
    </Stack>
  );
}
