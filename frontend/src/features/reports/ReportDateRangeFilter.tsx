import { Box, Collapse, MenuItem, Paper, Stack, TextField, Typography } from '@mui/material';
import type { DatePreset } from './useReportFilters';

type ReportsTextComprehensive = {
  filterTitle: string;
  today: string;
  yesterday: string;
  last7: string;
  last14: string;
  last30: string;
  thisMonth: string;
  lastMonth: string;
  thisYear: string;
  all: string;
  custom: string;
  from: string;
  to: string;
};

type Props = {
  text: ReportsTextComprehensive;
  activePreset: DatePreset;
  customFrom: string;
  customTo: string;
  dateFrom: string;
  dateTo: string;
  onSelectPreset: (preset: DatePreset) => void;
  onCustomFromChange: (v: string) => void;
  onCustomToChange: (v: string) => void;
};

const PRESETS: { key: DatePreset; labelKey: keyof ReportsTextComprehensive }[] = [
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

export function ReportDateRangeFilter({
  text,
  activePreset,
  customFrom,
  customTo,
  dateFrom,
  dateTo,
  onSelectPreset,
  onCustomFromChange,
  onCustomToChange,
}: Props) {
  return (
    <Paper
      variant="outlined"
      sx={{
        p: { xs: 2, md: 2.5 },
        borderRadius: 3,
        background: (theme) =>
          theme.palette.mode === 'dark'
            ? 'rgba(255,255,255,0.03)'
            : 'rgba(0,0,0,0.02)',
      }}
    >
      <Stack spacing={2}>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={2}
          alignItems={{ sm: 'center' }}
          justifyContent="space-between"
        >
          <Typography variant="subtitle2" fontWeight={700} color="text.secondary">
            {text.filterTitle}
          </Typography>
          <Typography variant="caption" color="text.disabled">
            {dateFrom} — {dateTo}
          </Typography>
        </Stack>

        {/* Preset dropdown */}
        <TextField
          select
          size="small"
          value={activePreset}
          onChange={(e) => onSelectPreset(e.target.value as DatePreset)}
          sx={{ minWidth: 200 }}
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

        {/* Custom date fields */}
        <Collapse in={activePreset === 'custom'}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <TextField
              type="date"
              size="small"
              label={text.from}
              value={customFrom}
              onChange={(e) => onCustomFromChange(e.target.value)}
              InputLabelProps={{ shrink: true }}
              sx={{ minWidth: 180 }}
            />
            <TextField
              type="date"
              size="small"
              label={text.to}
              value={customTo}
              onChange={(e) => onCustomToChange(e.target.value)}
              InputLabelProps={{ shrink: true }}
              sx={{ minWidth: 180 }}
            />
          </Stack>
        </Collapse>
      </Stack>
    </Paper>
  );
}
