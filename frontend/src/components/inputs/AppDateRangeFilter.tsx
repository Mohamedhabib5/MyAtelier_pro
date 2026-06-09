import { Collapse, MenuItem, Stack, TextField } from '@mui/material';
import type { DatePreset } from './useDateRangeFilter';
import { AppDateField } from './AppDateField';

type Props = {
  language: 'ar' | 'en';
  activePreset: DatePreset;
  customFrom: string;
  customTo: string;
  onSelectPreset: (preset: DatePreset) => void;
  onCustomFromChange: (v: string) => void;
  onCustomToChange: (v: string) => void;
  size?: 'small' | 'medium';
};

const TEXTS = {
  ar: {
    filterTitle: 'الفترة الزمنية',
    today: 'اليوم',
    yesterday: 'أمس',
    last7: 'آخر 7 أيام',
    last14: 'آخر 14 يوماً',
    last30: 'آخر 30 يوماً',
    thisMonth: 'هذا الشهر',
    lastMonth: 'الشهر الماضي',
    thisYear: 'هذه السنة',
    all: 'الكل (من البداية)',
    custom: 'مخصص',
    from: 'من تاريخ',
    to: 'إلى تاريخ',
  },
  en: {
    filterTitle: 'Date Range',
    today: 'Today',
    yesterday: 'Yesterday',
    last7: 'Last 7 days',
    last14: 'Last 14 days',
    last30: 'Last 30 days',
    thisMonth: 'This month',
    lastMonth: 'Last month',
    thisYear: 'This year',
    all: 'All Time',
    custom: 'Custom',
    from: 'From date',
    to: 'To date',
  },
};

const PRESETS: { key: DatePreset; labelKey: keyof typeof TEXTS.ar }[] = [
  { key: 'today', labelKey: 'today' },
  { key: 'yesterday', labelKey: 'yesterday' },
  { key: 'last7', labelKey: 'last7' },
  { key: 'last14', labelKey: 'last14' },
  { key: 'last30', labelKey: 'last30' },
  { key: 'thisMonth', labelKey: 'thisMonth' },
  { key: 'lastMonth', labelKey: 'lastMonth' },
  { key: 'thisYear', labelKey: 'thisYear' },
  { key: 'all', labelKey: 'all' },
  { key: 'custom', labelKey: 'custom' },
];

export function AppDateRangeFilter({
  language,
  activePreset,
  customFrom,
  customTo,
  onSelectPreset,
  onCustomFromChange,
  onCustomToChange,
  size = 'small',
}: Props) {
  const text = TEXTS[language] || TEXTS.ar;

  return (
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} alignItems="stretch">
      <TextField
        select
        size={size}
        label={text.filterTitle}
        value={activePreset}
        onChange={(e) => onSelectPreset(e.target.value as DatePreset)}
        sx={{ minWidth: 160 }}
      >
        {PRESETS.map(({ key, labelKey }) => (
          <MenuItem
            key={key}
            value={key}
            sx={{ fontWeight: activePreset === key ? 700 : 400 }}
          >
            {text[labelKey]}
          </MenuItem>
        ))}
      </TextField>

      <Collapse in={activePreset === 'custom'} orientation="horizontal" unmountOnExit={false}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          <AppDateField
            size={size}
            label={text.from}
            value={customFrom}
            onChange={(val) => onCustomFromChange(val)}
            sx={{ width: 140 }}
          />
          <AppDateField
            size={size}
            label={text.to}
            value={customTo}
            onChange={(val) => onCustomToChange(val)}
            sx={{ width: 140 }}
          />
        </Stack>
      </Collapse>
    </Stack>
  );
}
