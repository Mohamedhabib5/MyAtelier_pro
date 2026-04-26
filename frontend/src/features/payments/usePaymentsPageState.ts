import { useDeferredValue, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { PaymentTargetSearchRecord, PaymentDocumentSummaryRecord, PaymentDocumentPayload } from './api';
import { listPaymentsPage, searchPaymentTargets, getPaymentDocument, getBookingPaymentTarget, getCustomerPaymentTarget } from './api';
import { listPaymentMethods } from '../paymentMethods/api';

export type PaymentSortField = 'payment_date' | 'payment_number' | 'customer_name' | 'status' | 'document_kind';

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export function usePaymentsPageState() {
  const [error, setError] = useState<string | null>(null);
  const [creatingNew, setCreatingNew] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [selectedTarget, setSelectedTarget] = useState<PaymentTargetSearchRecord | null>(null);
  const [editingPaymentId, setEditingPaymentId] = useState<string | null>(null);
  const [voidingPayment, setVoidingPayment] = useState<PaymentDocumentSummaryRecord | null>(null);
  const [voidDate, setVoidDate] = useState(todayIso());
  const [voidReason, setVoidReason] = useState('');
  const [voidOverrideLock, setVoidOverrideLock] = useState(false);
  const [voidOverrideReason, setVoidOverrideReason] = useState('');
  const [tableSearchInput, setTableSearchInput] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [documentKindFilter, setDocumentKindFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [sortBy, setSortBy] = useState<PaymentSortField>('payment_date');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [pendingUpdateOverridePayload, setPendingUpdateOverridePayload] = useState<PaymentDocumentPayload | null>(null);
  
  const deferredTargetSearch = useDeferredValue(searchText);
  const deferredTableSearch = useDeferredValue(tableSearchInput.trim());
  const editorOpen = creatingNew || Boolean(editingPaymentId);

  const paymentsQuery = useQuery({
    queryKey: ['payments', 'table', deferredTableSearch, statusFilter, documentKindFilter, dateFrom, dateTo, page, pageSize, sortBy, sortDir],
    queryFn: () =>
      listPaymentsPage({
        search: deferredTableSearch || undefined,
        status: statusFilter || undefined,
        documentKind: documentKindFilter || undefined,
        dateFrom: dateFrom || undefined,
        dateTo: dateTo || undefined,
        page: page + 1,
        pageSize,
        sortBy,
        sortDir,
      }),
  });

  const searchQuery = useQuery({
    queryKey: ['payment-targets', 'search', deferredTargetSearch],
    queryFn: () => searchPaymentTargets(deferredTargetSearch),
    enabled: editorOpen && !selectedTarget,
  });

  const paymentMethodsQuery = useQuery({
    queryKey: ['payment-methods', 'active'],
    queryFn: () => listPaymentMethods('active'),
  });

  const paymentDocumentQuery = useQuery({
    queryKey: ['payments', editingPaymentId],
    queryFn: () => getPaymentDocument(editingPaymentId!),
    enabled: Boolean(editingPaymentId),
  });

  const targetQuery = useQuery({
    queryKey: ['payment-target', selectedTarget?.kind, selectedTarget?.id, editingPaymentId],
    queryFn: () => (selectedTarget?.kind === 'booking' ? getBookingPaymentTarget(selectedTarget.id, editingPaymentId) : getCustomerPaymentTarget(selectedTarget!.id, editingPaymentId)),
    enabled: Boolean(selectedTarget),
  });

  return {
    error, setError,
    creatingNew, setCreatingNew,
    searchText, setSearchText,
    selectedTarget, setSelectedTarget,
    editingPaymentId, setEditingPaymentId,
    voidingPayment, setVoidingPayment,
    voidDate, setVoidDate,
    voidReason, setVoidReason,
    voidOverrideLock, setVoidOverrideLock,
    voidOverrideReason, setVoidOverrideReason,
    tableSearchInput, setTableSearchInput,
    statusFilter, setStatusFilter,
    documentKindFilter, setDocumentKindFilter,
    dateFrom, setDateFrom,
    dateTo, setDateTo,
    page, setPage,
    pageSize, setPageSize,
    sortBy, setSortBy,
    sortDir, setSortDir,
    pendingUpdateOverridePayload, setPendingUpdateOverridePayload,
    deferredTableSearch,
    editorOpen,
    paymentsQuery,
    searchQuery,
    paymentMethodsQuery,
    paymentDocumentQuery,
    targetQuery,
    todayIso,
  };
}
