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
    <Stack direction='row' justifyContent='space-between' alignItems='center'>
      <Box>
        <Typography variant='h4'>{title}</Typography>
        <Typography color='text.secondary'>{subtitle}</Typography>
      </Box>
      <Stack direction='row' spacing={1} alignItems='center'>
        <Button
          variant='contained'
          startIcon={<PostAddOutlinedIcon />}
          onClick={onCreate}
          data-payment-create-dialog-button='true'
        >
          {createLabel}
        </Button>
      </Stack>
    </Stack>
  );
}
