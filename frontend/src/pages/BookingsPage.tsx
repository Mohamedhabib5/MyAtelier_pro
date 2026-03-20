import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import EventAvailableOutlinedIcon from '@mui/icons-material/EventAvailableOutlined';
import { Alert, Box, Button, Chip, CircularProgress, Stack, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { SectionCard } from '../components/SectionCard';
import { BookingDocumentEditor } from '../features/bookings/BookingDocumentEditor';
import { cancelBookingLine, completeBookingLine, createBooking, getBooking, listBookings, updateBooking, type BookingDocumentPayload } from '../features/bookings/api';
import { listDepartments, listServices } from '../features/catalog/api';
import { createCustomer, listCustomers, type CustomerPayload } from '../features/customers/api';
import { listDresses } from '../features/dresses/api';
import { useLanguage } from '../features/language/LanguageProvider';
import { queryClient } from '../lib/queryClient';
import { useBookingsText } from '../text/bookings';
import { EMPTY_VALUE, bookingStatusLabel, useCommonText } from '../text/common';

async function invalidateViews() {
  await Promise.all([
    queryClient.invalidateQueries({ queryKey: ['bookings'] }),
    queryClient.invalidateQueries({ queryKey: ['payments'] }),
    queryClient.invalidateQueries({ queryKey: ['dashboard', 'finance'] }),
    queryClient.invalidateQueries({ queryKey: ['reports', 'overview'] }),
    queryClient.invalidateQueries({ queryKey: ['accounting'] }),
    queryClient.invalidateQueries({ queryKey: ['exports'] }),
  ]);
}

export function BookingsPage() {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const bookingsText = useBookingsText();
  const [error, setError] = useState<string | null>(null);
  const [editingBookingId, setEditingBookingId] = useState<string | null>(null);
  const [creatingNew, setCreatingNew] = useState(false);
  const customersQuery = useQuery({ queryKey: ['customers'], queryFn: listCustomers });
  const departmentsQuery = useQuery({ queryKey: ['catalog', 'departments'], queryFn: listDepartments });
  const servicesQuery = useQuery({ queryKey: ['catalog', 'services'], queryFn: listServices });
  const dressesQuery = useQuery({ queryKey: ['dresses'], queryFn: listDresses });
  const bookingsQuery = useQuery({ queryKey: ['bookings'], queryFn: listBookings });
  const bookingDocumentQuery = useQuery({
    queryKey: ['bookings', editingBookingId],
    queryFn: () => getBooking(editingBookingId!),
    enabled: Boolean(editingBookingId),
  });

  const createMutation = useMutation({
    mutationFn: createBooking,
    onSuccess: async () => {
      await invalidateViews();
      closeEditor();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const updateMutation = useMutation({
    mutationFn: ({ bookingId, payload }: { bookingId: string; payload: BookingDocumentPayload }) => updateBooking(bookingId, payload),
    onSuccess: async () => {
      await invalidateViews();
      closeEditor();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const completeMutation = useMutation({
    mutationFn: ({ bookingId, lineId }: { bookingId: string; lineId: string }) => completeBookingLine(bookingId, lineId),
    onSuccess: async (document) => {
      await invalidateViews();
      queryClient.setQueryData(['bookings', document.id], document);
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const cancelLineMutation = useMutation({
    mutationFn: ({ bookingId, lineId }: { bookingId: string; lineId: string }) => cancelBookingLine(bookingId, lineId),
    onSuccess: async (document) => {
      await invalidateViews();
      queryClient.setQueryData(['bookings', document.id], document);
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const createCustomerMutation = useMutation({
    mutationFn: createCustomer,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['customers'] });
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  function closeEditor() {
    setCreatingNew(false);
    setEditingBookingId(null);
  }

  async function handleSave(payload: BookingDocumentPayload) {
    setError(null);
    if (creatingNew) {
      await createMutation.mutateAsync(payload);
      return;
    }
    if (editingBookingId) {
      await updateMutation.mutateAsync({ bookingId: editingBookingId, payload });
    }
  }

  async function handleCreateCustomer(payload: CustomerPayload) {
    return await createCustomerMutation.mutateAsync(payload);
  }

  const document = creatingNew ? null : bookingDocumentQuery.data ?? null;

  return (
    <Stack spacing={3}>
      <Stack direction='row' justifyContent='space-between' alignItems='center'>
        <Box>
          <Typography variant='h4'>{bookingsText.page.title}</Typography>
          <Typography color='text.secondary'>{bookingsText.page.subtitle}</Typography>
        </Box>
        <Button variant='contained' startIcon={<EventAvailableOutlinedIcon />} onClick={() => { setCreatingNew(true); setEditingBookingId(null); }}>
          {bookingsText.page.createDocument}
        </Button>
      </Stack>

      {error ? <Alert severity='error'>{error}</Alert> : null}

      <SectionCard title={bookingsText.page.listTitle} subtitle={bookingsText.page.listSubtitle}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{bookingsText.table.bookingNumber}</TableCell>
              <TableCell>{bookingsText.table.customer}</TableCell>
              <TableCell>{bookingsText.table.lineCount}</TableCell>
              <TableCell>{bookingsText.table.serviceSummary}</TableCell>
              <TableCell>{bookingsText.table.nextServiceDate}</TableCell>
              <TableCell>{bookingsText.table.total}</TableCell>
              <TableCell>{bookingsText.table.paid}</TableCell>
              <TableCell>{bookingsText.table.remaining}</TableCell>
              <TableCell>{bookingsText.table.status}</TableCell>
              <TableCell>{commonText.actions}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(bookingsQuery.data ?? []).map((booking) => (
              <TableRow key={booking.id}>
                <TableCell>{booking.booking_number}</TableCell>
                <TableCell>{booking.customer_name}</TableCell>
                <TableCell>{booking.line_count}</TableCell>
                <TableCell>{booking.service_summary}</TableCell>
                <TableCell>{booking.next_service_date ?? EMPTY_VALUE}</TableCell>
                <TableCell>{booking.total_amount}</TableCell>
                <TableCell>{booking.paid_total}</TableCell>
                <TableCell>{booking.remaining_amount}</TableCell>
                <TableCell>
                  <Chip size='small' label={bookingStatusLabel(language, booking.status)} color={booking.status === 'completed' ? 'success' : booking.status === 'cancelled' ? 'default' : 'warning'} />
                </TableCell>
                <TableCell>
                  <Button startIcon={<EditOutlinedIcon />} onClick={() => { setCreatingNew(false); setEditingBookingId(booking.id); }}>
                    {bookingsText.page.openDocument}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </SectionCard>

      {creatingNew || editingBookingId ? (
        <SectionCard title={bookingsText.page.editorTitle} subtitle={bookingsText.page.editorSubtitle}>
          {bookingDocumentQuery.isLoading && !creatingNew ? <CircularProgress /> : null}
          <BookingDocumentEditor
            customers={customersQuery.data ?? []}
            departments={departmentsQuery.data ?? []}
            services={servicesQuery.data ?? []}
            dresses={dressesQuery.data ?? []}
            document={document}
            saving={createMutation.isPending || updateMutation.isPending}
            onSave={handleSave}
            onCancel={closeEditor}
            onCreateCustomer={handleCreateCustomer}
            onCompleteLine={async (lineId) => {
              if (!editingBookingId) return;
              await completeMutation.mutateAsync({ bookingId: editingBookingId, lineId });
              await queryClient.invalidateQueries({ queryKey: ['bookings', editingBookingId] });
            }}
            onCancelLine={async (lineId) => {
              if (!editingBookingId) return;
              await cancelLineMutation.mutateAsync({ bookingId: editingBookingId, lineId });
              await queryClient.invalidateQueries({ queryKey: ['bookings', editingBookingId] });
            }}
          />
        </SectionCard>
      ) : null}
    </Stack>
  );
}
