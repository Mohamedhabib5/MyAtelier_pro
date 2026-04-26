import PostAddOutlinedIcon from '@mui/icons-material/PostAddOutlined';
import { Box, Button, Stack, Typography } from '@mui/material';

type Props = {
  title: string;
  subtitle: string;
  createLabel: string;
  onCreate: () => void;
};

export function PaymentsPageHeader({ title, subtitle, createLabel, onCreate }: Props) {
  return (
    <Stack 
      direction={{ xs: 'column', sm: 'row' }} 
      justifyContent='space-between' 
      alignItems={{ xs: 'flex-start', sm: 'center' }}
      spacing={2}
    >
      <Box>
        <Typography variant='h4' sx={{ fontSize: { xs: '1.75rem', md: '2.125rem' } }}>{title}</Typography>
        <Typography color='text.secondary' sx={{ fontSize: { xs: '0.875rem', md: '1rem' } }}>{subtitle}</Typography>
      </Box>
      <Stack direction='row' spacing={1} alignItems='center' sx={{ width: { xs: '100%', sm: 'auto' } }}>
        <Button
          variant='contained'
          fullWidth={{ xs: true, sm: false } as any}
          startIcon={<PostAddOutlinedIcon />}
          onClick={onCreate}
          data-payment-create-dialog-button='true'
          sx={{ py: 1.25, px: 3, borderRadius: 3 }}
        >
          {createLabel}
        </Button>
      </Stack>
    </Stack>
  );
}
