import EventAvailableOutlinedIcon from '@mui/icons-material/EventAvailableOutlined';
import { Box, Button, Stack, Typography } from '@mui/material';

type Props = {
  title: string;
  subtitle: string;
  createLabel: string;
  onCreate: () => void;
};

export function BookingsPageHeader({ title, subtitle, createLabel, onCreate }: Props) {
  return (
    <Stack direction='row' justifyContent='space-between' alignItems='center'>
      <Box>
        <Typography variant='h4'>{title}</Typography>
        <Typography color='text.secondary'>{subtitle}</Typography>
      </Box>
      <Button variant='contained' startIcon={<EventAvailableOutlinedIcon />} onClick={onCreate} sx={{ gap: 1 }}>
        {createLabel}
      </Button>
    </Stack>
  );
}
