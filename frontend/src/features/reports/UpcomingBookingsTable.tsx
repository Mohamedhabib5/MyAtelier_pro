import { Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';

import { useReportsText } from '../../text/reports';
import type { UpcomingBookingItem } from './api';

export function UpcomingBookingsTable({ items }: { items: UpcomingBookingItem[] }) {
  const reportsText = useReportsText();

  if (!items.length) {
    return <Typography color='text.secondary'>{reportsText.print.noData}</Typography>;
  }

  return (
    <Table size='small'>
      <TableHead>
        <TableRow>
          <TableCell>{reportsText.table.bookingNumber}</TableCell>
          <TableCell>{reportsText.table.customer}</TableCell>
          <TableCell>{reportsText.table.service}</TableCell>
          <TableCell>{reportsText.table.serviceDate}</TableCell>
          <TableCell>{reportsText.table.status}</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {items.map((item) => (
          <TableRow key={`${item.booking_number}-${item.service_name}-${item.service_date}`}>
            <TableCell>{item.booking_number}</TableCell>
            <TableCell>{item.customer_name}</TableCell>
            <TableCell>{item.service_name}</TableCell>
            <TableCell>{item.service_date}</TableCell>
            <TableCell>{item.status}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
