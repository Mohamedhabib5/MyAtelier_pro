import { useQuery } from '@tanstack/react-query';
import { listDepartments, listServices } from '../catalog/api';
import { listCustomers } from '../customers/api';
import { listDresses } from '../dresses/api';
import { listPaymentMethods } from '../paymentMethods/api';
import { getBooking, listBookingsPage, type BookingSortField } from './api';

interface UseBookingsQueriesProps {
  deferredSearch: string;
  statusFilter: string;
  dateFrom: string;
  dateTo: string;
  page: number;
  pageSize: number;
  sortBy: BookingSortField;
  sortDir: 'asc' | 'desc';
  editingBookingId: string | null;
}

export function useBookingsQueries({
  deferredSearch,
  statusFilter,
  dateFrom,
  dateTo,
  page,
  pageSize,
  sortBy,
  sortDir,
  editingBookingId,
}: UseBookingsQueriesProps) {
  const customersQuery = useQuery({ queryKey: ['customers'], queryFn: listCustomers });
  const departmentsQuery = useQuery({ queryKey: ['catalog', 'departments'], queryFn: listDepartments });
  const servicesQuery = useQuery({ queryKey: ['catalog', 'services'], queryFn: listServices });
  const dressesQuery = useQuery({ queryKey: ['dresses'], queryFn: listDresses });
  const paymentMethodsQuery = useQuery({ queryKey: ['payment-methods', 'active'], queryFn: () => listPaymentMethods('active') });
  
  const bookingsQuery = useQuery({
    queryKey: ['bookings', 'table', deferredSearch, statusFilter, dateFrom, dateTo, page, pageSize, sortBy, sortDir],
    queryFn: () =>
      listBookingsPage({
        search: deferredSearch || undefined,
        status: statusFilter || undefined,
        dateFrom: dateFrom || undefined,
        dateTo: dateTo || undefined,
        page: page + 1,
        pageSize,
        sortBy,
        sortDir,
      }),
  });

  const bookingDocumentQuery = useQuery({
    queryKey: ['bookings', editingBookingId],
    queryFn: () => getBooking(editingBookingId!),
    enabled: Boolean(editingBookingId),
  });

  return {
    customersQuery,
    departmentsQuery,
    servicesQuery,
    dressesQuery,
    paymentMethodsQuery,
    bookingsQuery,
    bookingDocumentQuery,
  };
}
