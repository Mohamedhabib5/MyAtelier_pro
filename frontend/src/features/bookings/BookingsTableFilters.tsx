import { MenuItem, Stack, TextField } from '@mui/material';

import { bookingStatusLabel } from '../../text/common';
import { AppDateRangeFilter } from '../../components/inputs/AppDateRangeFilter';
import type { DatePreset } from '../../components/inputs/useDateRangeFilter';

type Props = {
  language: 'ar' | 'en';
  statusFilter: string;
  onStatusChange: (value: string) => void;
  activePreset: DatePreset;
  customFrom: string;
  customTo: string;
  onSelectPreset: (preset: DatePreset) => void;
  onCustomFromChange: (v: string) => void;
  onCustomToChange: (v: string) => void;
};

export function BookingsTableFilters({
  language,
  statusFilter,
  onStatusChange,
  activePreset,
  customFrom,
  customTo,
  onSelectPreset,
  onCustomFromChange,
  onCustomToChange,
}: Props) {
  return (
    <Stack direction={{ xs: 'column', lg: 'row' }} spacing={1.5}>
      <TextField select size='small' label={language === 'ar' ? 'الحالة' : 'Status'} value={statusFilter} onChange={(event) => onStatusChange(event.target.value)} sx={{ minWidth: 180 }}>
        <MenuItem value=''>{language === 'ar' ? 'كل الحالات' : 'All statuses'}</MenuItem>
        <MenuItem value='draft'>{bookingStatusLabel(language, 'draft')}</MenuItem>
        <MenuItem value='confirmed'>{bookingStatusLabel(language, 'confirmed')}</MenuItem>
        <MenuItem value='completed'>{bookingStatusLabel(language, 'completed')}</MenuItem>
        <MenuItem value='cancelled'>{bookingStatusLabel(language, 'cancelled')}</MenuItem>
      </TextField>
      
      <AppDateRangeFilter
        language={language}
        activePreset={activePreset}
        customFrom={customFrom}
        customTo={customTo}
        onSelectPreset={onSelectPreset}
        onCustomFromChange={onCustomFromChange}
        onCustomToChange={onCustomToChange}
      />
    </Stack>
  );
}
