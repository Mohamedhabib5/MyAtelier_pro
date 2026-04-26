import { MenuItem, Stack, TextField } from '@mui/material';

import { bookingStatusLabel } from '../../text/common';

type Props = {
  language: 'ar' | 'en';
  statusFilter: string;
  dateFrom: string;
  dateTo: string;
  onStatusChange: (value: string) => void;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
};

export function BookingsTableFilters({
  language,
  statusFilter,
  dateFrom,
  dateTo,
  onStatusChange,
  onDateFromChange,
  onDateToChange,
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
      <TextField type='date' size='small' label={language === 'ar' ? 'من تاريخ' : 'From date'} value={dateFrom} onChange={(event) => onDateFromChange(event.target.value)} InputLabelProps={{ shrink: true }} />
      <TextField type='date' size='small' label={language === 'ar' ? 'إلى تاريخ' : 'To date'} value={dateTo} onChange={(event) => onDateToChange(event.target.value)} InputLabelProps={{ shrink: true }} />
    </Stack>
  );
}
