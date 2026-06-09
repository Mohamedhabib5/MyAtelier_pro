import { useDeferredValue, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { DisbursementVoucherRecord, DisbursementUpdatePayload } from './api';
import { listDisbursementsPage, getDisbursementVoucher } from './api';
import { listPaymentMethods } from '../paymentMethods/api';

import { useDateRangeFilter } from '../../components/inputs/useDateRangeFilter';

export type DisbursementSortField = 'voucher_date' | 'voucher_number' | 'amount' | 'status' | 'payee_type';

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export function useDisbursementsPageState() {
  const [error, setError] = useState<string | null>(null);
  const [creatingNew, setCreatingNew] = useState(false);
  const [editingVoucherId, setEditingVoucherId] = useState<string | null>(null);
  const [voidingVoucher, setVoidingVoucher] = useState<DisbursementVoucherRecord | null>(null);
  
  const [voidDate, setVoidDate] = useState(todayIso());
  const [voidReason, setVoidReason] = useState('');
  const [voidOverrideLock, setVoidOverrideLock] = useState(false);
  const [voidOverrideReason, setVoidOverrideReason] = useState('');
  
  const [tableSearchInput, setTableSearchInput] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [payeeTypeFilter, setPayeeTypeFilter] = useState('');

  const {
    dateFrom,
    dateTo,
    activePreset,
    customFrom,
    customTo,
    selectPreset,
    setCustomFrom,
    setCustomTo,
  } = useDateRangeFilter('all');
  
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [sortBy, setSortBy] = useState<DisbursementSortField>('voucher_date');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [pendingUpdateOverridePayload, setPendingUpdateOverridePayload] = useState<DisbursementUpdatePayload | null>(null);

  const deferredTableSearch = useDeferredValue(tableSearchInput.trim());
  const editorOpen = creatingNew || Boolean(editingVoucherId);

  const disbursementsQuery = useQuery({
    queryKey: ['disbursements', 'table', deferredTableSearch, statusFilter, payeeTypeFilter, dateFrom, dateTo, page, pageSize, sortBy, sortDir],
    queryFn: () =>
      listDisbursementsPage({
        search: deferredTableSearch || undefined,
        status: statusFilter || undefined,
        payeeType: payeeTypeFilter || undefined,
        dateFrom: dateFrom || undefined,
        dateTo: dateTo || undefined,
        page: page + 1,
        pageSize,
        sortBy,
        sortDir,
      }),
  });

  const paymentMethodsQuery = useQuery({
    queryKey: ['payment-methods', 'active'],
    queryFn: () => listPaymentMethods('active'),
  });

  const disbursementVoucherQuery = useQuery({
    queryKey: ['disbursements', editingVoucherId],
    queryFn: () => getDisbursementVoucher(editingVoucherId!),
    enabled: Boolean(editingVoucherId),
  });

  return {
    error, setError,
    creatingNew, setCreatingNew,
    editingVoucherId, setEditingVoucherId,
    voidingVoucher, setVoidingVoucher,
    voidDate, setVoidDate,
    voidReason, setVoidReason,
    voidOverrideLock, setVoidOverrideLock,
    voidOverrideReason, setVoidOverrideReason,
    tableSearchInput, setTableSearchInput,
    statusFilter, setStatusFilter,
    payeeTypeFilter, setPayeeTypeFilter,
    dateFrom,
    dateTo,
    activePreset,
    customFrom,
    customTo,
    selectPreset,
    setCustomFrom,
    setCustomTo,
    page, setPage,
    pageSize, setPageSize,
    sortBy, setSortBy,
    sortDir, setSortDir,
    pendingUpdateOverridePayload, setPendingUpdateOverridePayload,
    deferredTableSearch,
    editorOpen,
    disbursementsQuery,
    paymentMethodsQuery,
    disbursementVoucherQuery,
    todayIso,
  };
}
