import { Box, Checkbox, FormControlLabel, FormGroup, Radio, RadioGroup, Typography, Divider, Stack } from '@mui/material';
import type { CalendarQuery } from '../../features/bookings/api';
import type { DepartmentRecord, ServiceRecord } from '../../features/catalog/api';
import { useLanguage } from '../../features/language/LanguageProvider';

interface Props {
  filters: CalendarQuery;
  setFilters: (filters: CalendarQuery) => void;
  departments: DepartmentRecord[];
  services: ServiceRecord[];
}

export function CalendarFilters({ filters, setFilters, departments, services }: Props) {
  const { language } = useLanguage();

  const handleDateModeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFilters({ ...filters, dateMode: event.target.value as 'service' | 'reservation' });
  };

  const handleDepartmentChange = (id: string) => {
    const current = filters.departmentIds || [];
    const next = current.includes(id) ? current.filter(x => x !== id) : [...current, id];
    setFilters({ ...filters, departmentIds: next });
  };

  const handleServiceChange = (id: string) => {
    const current = filters.serviceIds || [];
    const next = current.includes(id) ? current.filter(x => x !== id) : [...current, id];
    setFilters({ ...filters, serviceIds: next });
  };

  const filteredServices = filters.departmentIds?.length 
    ? services.filter(s => filters.departmentIds?.includes(s.department_id))
    : services;

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="overline" sx={{ fontWeight: 800, color: 'text.secondary' }}>
          {language === 'ar' ? 'عرض الأحداث حسب' : 'View events by'}
        </Typography>
        <RadioGroup value={filters.dateMode} onChange={handleDateModeChange}>
          <FormControlLabel 
            value="service" 
            control={<Radio size="small" />} 
            label={language === 'ar' ? 'تاريخ الخدمة' : 'Service Date'} 
          />
          <FormControlLabel 
            value="reservation" 
            control={<Radio size="small" />} 
            label={language === 'ar' ? 'تاريخ الحجز' : 'Reservation Date'} 
          />
        </RadioGroup>
      </Box>

      <Divider />

      <Box>
        <Typography variant="overline" sx={{ fontWeight: 800, color: 'text.secondary' }}>
          {language === 'ar' ? 'الأقسام' : 'Departments'}
        </Typography>
        <FormGroup sx={{ mt: 1 }}>
          {departments.map(dept => (
            <FormControlLabel
              key={dept.id}
              control={
                <Checkbox 
                  size="small" 
                  checked={filters.departmentIds?.includes(dept.id)} 
                  onChange={() => handleDepartmentChange(dept.id)}
                />
              }
              label={dept.name}
            />
          ))}
        </FormGroup>
      </Box>

      <Divider />

      <Box>
        <Typography variant="overline" sx={{ fontWeight: 800, color: 'text.secondary' }}>
          {language === 'ar' ? 'الخدمات' : 'Services'}
        </Typography>
        <FormGroup sx={{ mt: 1, maxHeight: 300, overflowY: 'auto' }}>
          {filteredServices.map(service => (
            <FormControlLabel
              key={service.id}
              control={
                <Checkbox 
                  size="small" 
                  checked={filters.serviceIds?.includes(service.id)} 
                  onChange={() => handleServiceChange(service.id)}
                />
              }
              label={service.name}
            />
          ))}
        </FormGroup>
      </Box>
    </Stack>
  );
}
