import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { parseISO, format, isValid } from 'date-fns';
import { SxProps, Theme } from '@mui/material';

interface AppDateFieldProps {
  label?: string;
  value?: string | null; // YYYY-MM-DD
  onChange?: (value: string) => void;
  disabled?: boolean;
  size?: 'small' | 'medium';
  fullWidth?: boolean;
  required?: boolean;
  sx?: SxProps<Theme>;
}

export function AppDateField({
  label,
  value,
  onChange,
  disabled,
  size = 'small',
  fullWidth = true,
  required,
  sx,
}: AppDateFieldProps) {
  // Convert string (YYYY-MM-DD) to Date object
  const parsedValue = value ? parseISO(value) : null;
  const dateValue = parsedValue && isValid(parsedValue) ? parsedValue : null;

  const handleChange = (newValue: Date | null) => {
    if (!onChange) return;
    if (newValue && isValid(newValue)) {
      onChange(format(newValue, 'yyyy-MM-dd'));
    } else {
      onChange('');
    }
  };

  return (
    <DatePicker
      label={label}
      value={dateValue}
      onChange={handleChange}
      disabled={disabled}
      slotProps={{
        textField: {
          size,
          fullWidth,
          required,
          sx,
        },
      }}
    />
  );
}
