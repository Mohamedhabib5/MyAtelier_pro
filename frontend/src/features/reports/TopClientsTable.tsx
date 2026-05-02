import {
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';

import type { TopClientItem } from './api';

type Props = {
  clients: TopClientItem[];
  text: {
    topClients: string;
    topClientsSubtitle: string;
    clientName: string;
    amountPaid: string;
    bookingCount: string;
    noData: string;
  };
  formatCurrency: (v: number) => string;
  formatCount: (v: number) => string;
};

export function TopClientsTable({ clients, text, formatCurrency, formatCount }: Props) {
  return (
    <Stack spacing={1.5}>
      <Stack spacing={0.5}>
        <Typography variant="h6">{text.topClients}</Typography>
        <Typography color="text.secondary" variant="body2">
          {text.topClientsSubtitle}
        </Typography>
      </Stack>

      <Paper variant="outlined" sx={{ borderRadius: 3, overflow: 'hidden' }}>
        {clients.length === 0 ? (
          <Stack alignItems="center" justifyContent="center" sx={{ py: 5 }}>
            <Typography color="text.secondary">{text.noData}</Typography>
          </Stack>
        ) : (
          <Table size="small">
            <TableHead>
              <TableRow
                sx={{
                  bgcolor: (theme) =>
                    theme.palette.mode === 'dark'
                      ? 'rgba(255,255,255,0.05)'
                      : 'rgba(0,0,0,0.03)',
                }}
              >
                <TableCell sx={{ fontWeight: 700, py: 1.5 }}>#</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>{text.clientName}</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700 }}>
                  {text.amountPaid}
                </TableCell>
                <TableCell align="right" sx={{ fontWeight: 700 }}>
                  {text.bookingCount}
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {clients.map((client, index) => (
                <TableRow
                  key={`${client.customer_name}-${index}`}
                  sx={{
                    '&:last-child td': { border: 0 },
                    transition: 'background 150ms',
                    '&:hover': {
                      bgcolor: (theme) =>
                        theme.palette.mode === 'dark'
                          ? 'rgba(255,255,255,0.04)'
                          : 'rgba(0,0,0,0.02)',
                    },
                  }}
                >
                  <TableCell>
                    <Typography
                      variant="caption"
                      fontWeight={700}
                      color="text.disabled"
                    >
                      {index + 1}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600}>
                      {client.customer_name}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="success.main" fontWeight={700}>
                      {formatCurrency(client.total_paid)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      {formatCount(client.booking_count)}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Paper>
    </Stack>
  );
}
