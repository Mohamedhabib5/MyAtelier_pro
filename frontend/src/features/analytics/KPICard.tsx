import { Box, Card, CardContent, Stack, Typography } from '@mui/material';

interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  color?: string;
}

export function KPICard({ title, value, subtitle, icon, color = 'primary.main' }: Props) {
  return (
    <Card variant='outlined' sx={{ 
      borderRadius: 4, 
      height: '100%', 
      border: '1px solid rgba(0,0,0,0.05)',
      bgcolor: 'background.paper',
      transition: 'transform 0.2s, box-shadow 0.2s',
      '&:hover': { transform: 'translateY(-2px)', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }
    }}>
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        <Stack direction='row' justifyContent='space-between' alignItems='center'>
          <Stack spacing={0}>
            <Typography variant='caption' fontWeight={800} color='text.secondary' sx={{ textTransform: 'uppercase', letterSpacing: 0.5, fontSize: '0.65rem' }}>
              {title}
            </Typography>
            <Typography variant='h5' fontWeight={900} sx={{ color, mt: -0.5 }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant='caption' color='text.secondary' fontWeight={600} sx={{ fontSize: '0.65rem' }}>
                {subtitle}
              </Typography>
            )}
          </Stack>
          {icon && (
            <Box sx={{ p: 1, borderRadius: 2, bgcolor: `${color}15`, color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {icon}
            </Box>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
