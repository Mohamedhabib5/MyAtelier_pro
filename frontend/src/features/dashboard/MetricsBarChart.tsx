import { Box, Stack, Typography } from '@mui/material';

type BarItem = {
  label: string;
  value: number;
  valueLabel: string;
};

export function MetricsBarChart({
  items,
  emptyLabel,
  color,
}: {
  items: BarItem[];
  emptyLabel: string;
  color: string;
}) {
  if (items.length === 0) {
    return (
      <Typography variant='body2' color='text.secondary'>
        {emptyLabel}
      </Typography>
    );
  }

  const maxValue = Math.max(...items.map((item) => item.value), 0);
  return (
    <Stack spacing={1.25}>
      {items.map((item) => {
        const widthPercent = maxValue > 0 ? Math.max((item.value / maxValue) * 100, 3) : 0;
        return (
          <Box key={`${item.label}-${item.value}`}>
            <Stack direction='row' justifyContent='space-between' alignItems='center' sx={{ mb: 0.5 }}>
              <Typography variant='body2' sx={{ fontWeight: 600 }}>
                {item.label}
              </Typography>
              <Typography variant='caption' color='text.secondary'>
                {item.valueLabel}
              </Typography>
            </Stack>
            <Box
              sx={{
                width: '100%',
                height: 10,
                borderRadius: 1,
                bgcolor: 'action.hover',
                overflow: 'hidden',
              }}
            >
              <Box
                sx={{
                  height: '100%',
                  width: `${widthPercent}%`,
                  bgcolor: color,
                  transition: 'width 300ms ease',
                }}
              />
            </Box>
          </Box>
        );
      })}
    </Stack>
  );
}
