import { Box, Card, CardContent, CircularProgress, Grid, Stack, Typography } from '@mui/material';

type KpiDef = {
  label: string;
  value: string;
  helper: string;
  color: string;
};

type Props = {
  kpis: KpiDef[];
  loading: boolean;
};

export function ComprehensiveKpiRow({ kpis, loading }: Props) {
  return (
    <Grid container spacing={2}>
      {kpis.map((kpi) => (
        <Grid key={kpi.label} size={{ xs: 12, sm: 6, md: 'auto' }} sx={{ flex: { md: 1 } }}>
          <KpiCard {...kpi} loading={loading} />
        </Grid>
      ))}
    </Grid>
  );
}

function KpiCard({
  label,
  value,
  helper,
  color,
  loading,
}: KpiDef & { loading: boolean }) {
  return (
    <Card
      sx={{
        height: '100%',
        background: (theme) =>
          theme.palette.mode === 'dark'
            ? `linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)`
            : `linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%)`,
        backdropFilter: 'blur(12px)',
        border: (theme) =>
          theme.palette.mode === 'dark'
            ? '1px solid rgba(255,255,255,0.08)'
            : '1px solid rgba(0,0,0,0.06)',
        boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
        borderRadius: 3,
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          insetInlineStart: 0,
          width: 4,
          height: '100%',
          bgcolor: color,
          borderRadius: '4px 0 0 4px',
        },
      }}
    >
      <CardContent>
        <Stack spacing={1}>
          <Typography color="text.secondary" variant="body2" fontWeight={600}>
            {label}
          </Typography>
          <Box sx={{ minHeight: 44, display: 'flex', alignItems: 'center' }}>
            {loading ? (
              <CircularProgress size={20} />
            ) : (
              <Typography variant="h4" fontWeight={800} sx={{ color }}>
                {value}
              </Typography>
            )}
          </Box>
          <Typography color="text.disabled" variant="caption">
            {helper}
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}
