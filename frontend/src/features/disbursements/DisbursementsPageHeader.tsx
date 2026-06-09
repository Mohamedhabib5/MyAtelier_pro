import PostAddOutlinedIcon from '@mui/icons-material/PostAddOutlined';
import { Box, Button, Stack, Typography } from '@mui/material';

type Props = {
  title: string;
  subtitle: string;
  createLabel: string;
  onCreate: () => void;
  secondCreateLabel?: string;
  onSecondCreate?: () => void;
};

export function DisbursementsPageHeader({ title, subtitle, createLabel, onCreate, secondCreateLabel, onSecondCreate }: Props) {
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
        {secondCreateLabel && onSecondCreate && (
          <Button
            variant='outlined'
            fullWidth={{ xs: true, sm: false } as any}
            startIcon={<PostAddOutlinedIcon />}
            onClick={onSecondCreate}
            sx={{ py: 1.25, px: 3, borderRadius: 3 }}
          >
            {secondCreateLabel}
          </Button>
        )}
        <Button
          variant='contained'
          fullWidth={{ xs: true, sm: false } as any}
          startIcon={<PostAddOutlinedIcon />}
          onClick={onCreate}
          data-disbursement-create-button='true'
          sx={{ py: 1.25, px: 3, borderRadius: 3 }}
        >
          {createLabel}
        </Button>
      </Stack>
    </Stack>
  );
}
