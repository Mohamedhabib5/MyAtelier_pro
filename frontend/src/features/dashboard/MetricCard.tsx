import { Card, CardContent, Stack, Typography } from '@mui/material';

export function MetricCard({ label, value, helper }: { label: string; value: string; helper: string }) {
  return (
    <Card>
      <CardContent>
        <Stack spacing={1}>
          <Typography color='text.secondary' variant='body2'>
            {label}
          </Typography>
          <Typography variant='h4'>{value}</Typography>
          <Typography color='text.secondary' variant='body2'>
            {helper}
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}
