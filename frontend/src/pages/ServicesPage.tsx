import { Stack, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';

import { listDepartments } from '../features/catalog/api';
import { DepartmentsSection } from '../features/catalog/DepartmentsSection';
import { ServicesSection } from '../features/catalog/ServicesSection';
import { useCatalogText } from '../text/catalog';

export function ServicesPage() {
  const catalogText = useCatalogText();
  const departmentsQuery = useQuery({ queryKey: ['catalog', 'departments'], queryFn: listDepartments });
  const departments = departmentsQuery.data ?? [];

  return (
    <Stack spacing={3}>
      <Stack spacing={0.5}>
        <Typography variant='h4'>{catalogText.page.title}</Typography>
        <Typography color='text.secondary'>{catalogText.page.description}</Typography>
      </Stack>
      <DepartmentsSection departments={departments} />
      <ServicesSection departments={departments} />
    </Stack>
  );
}
