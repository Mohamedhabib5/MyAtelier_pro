import BlockOutlinedIcon from '@mui/icons-material/BlockOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import { Button, Chip, MenuItem, Stack, TextField, Typography } from '@mui/material';
import type { ColDef } from 'ag-grid-community';
import { useMemo } from 'react';

import { AppAgGrid } from '../../components/ag-grid';
import { SectionCard } from '../../components/SectionCard';
import { getPaymentsExcelUrl, type PaymentExportFilters } from '../exports/api';
import { downloadFile } from '../../lib/api';
import { useLanguage } from '../language/LanguageProvider';
import { joinLocalizedList, paymentDocumentStatusLabel, paymentKindLabel, useCommonText } from '../../text/common';
import { usePaymentsText } from '../../text/payments';
import type { PaymentDocumentSummaryRecord } from './api';

type PaymentSortField = 'payment_date' | 'payment_number' | 'customer_name' | 'status' | 'document_kind';

type PaymentsTableSectionProps = {
  rows: PaymentDocumentSummaryRecord[];
  total: number;
  loading: boolean;
  tableSearchInput: string;
  onTableSearchChange: (value: string) => void;
  statusFilter: string;
  onStatusFilterChange: (value: string) => void;
  documentKindFilter: string;
  onDocumentKindFilterChange: (value: string) => void;
  dateFrom: string;
  onDateFromChange: (value: string) => void;
  dateTo: string;
  onDateToChange: (value: string) => void;
  page: number;
  pageSize: number;
  onPageChange: (value: number) => void;
  onPageSizeChange: (value: number) => void;
  sortBy: PaymentSortField;
  sortDir: 'asc' | 'desc';
  onSortChange: (sortBy: PaymentSortField, sortDir: 'asc' | 'desc') => void;
  exportFilters: PaymentExportFilters;
  onOpenEdit: (row: PaymentDocumentSummaryRecord) => void;
  onOpenVoid: (row: PaymentDocumentSummaryRecord) => void;
};

export function PaymentsTableSection({
  rows,
  total,
  loading,
  tableSearchInput,
  onTableSearchChange,
  statusFilter,
  onStatusFilterChange,
  documentKindFilter,
  onDocumentKindFilterChange,
  dateFrom,
  onDateFromChange,
  dateTo,
  onDateToChange,
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
  sortBy,
  sortDir,
  onSortChange,
  exportFilters,
  onOpenEdit,
  onOpenVoid,
}: PaymentsTableSectionProps) {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const paymentsText = usePaymentsText();

  const columns = useMemo<ColDef<PaymentDocumentSummaryRecord>[]>(
    () => [
      { colId: 'payment_number', field: 'payment_number', headerName: paymentsText.table.number, pinned: language === 'ar' ? 'right' : 'left', sort: sortBy === 'payment_number' ? sortDir : null },
      { colId: 'customer_name', field: 'customer_name', headerName: paymentsText.table.customer, sort: sortBy === 'customer_name' ? sortDir : null },
      { colId: 'payment_method_name', field: 'payment_method_name', headerName: paymentsText.table.paymentMethod },
      {
        colId: 'booking_numbers',
        headerName: paymentsText.table.bookings,
        valueGetter: ({ data }) => joinLocalizedList(language, data?.booking_numbers ?? []),
      },
      { colId: 'payment_date', field: 'payment_date', headerName: paymentsText.table.date, sort: sortBy === 'payment_date' ? sortDir : null },
      {
        colId: 'document_kind',
        headerName: paymentsText.table.type,
        valueGetter: ({ data }) => (data ? paymentKindLabel(language, data.document_kind) : ''),
        cellRenderer: ({ data }: { data: PaymentDocumentSummaryRecord | undefined }) => (data ? <Chip size='small' label={paymentKindLabel(language, data.document_kind)} /> : null),
        sort: sortBy === 'document_kind' ? sortDir : null,
      },
      {
        colId: 'status',
        headerName: paymentsText.table.status,
        valueGetter: ({ data }) => (data ? paymentDocumentStatusLabel(language, data.status) : ''),
        cellRenderer: ({ data }: { data: PaymentDocumentSummaryRecord | undefined }) => (data ? <Chip size='small' color={data.status === 'voided' ? 'warning' : 'primary'} label={paymentDocumentStatusLabel(language, data.status)} /> : null),
        sort: sortBy === 'status' ? sortDir : null,
      },
      { colId: 'total_amount', field: 'total_amount', headerName: paymentsText.table.total, filter: 'agNumberColumnFilter' },
      {
        colId: 'journal',
        headerName: paymentsText.table.journal,
        valueGetter: ({ data }) => `${data?.journal_entry_number ?? ''} ${data?.journal_entry_status ?? ''}`,
        cellRenderer: ({ data }: { data: PaymentDocumentSummaryRecord | undefined }) =>
          data?.journal_entry_number ? (
            <Stack spacing={0.5}>
              <Stack direction='row' spacing={1} alignItems='center'>
                <ReceiptLongOutlinedIcon fontSize='small' color='action' />
                <Typography variant='body2'>{data.journal_entry_number}</Typography>
              </Stack>
              <Typography variant='caption'>{data.journal_entry_status ?? '-'}</Typography>
            </Stack>
          ) : (
            '-'
          ),
      },
      {
        colId: 'actions',
        headerName: commonText.actions,
        sortable: false,
        filter: false,
        pinned: language === 'ar' ? 'left' : 'right',
        cellRenderer: ({ data }: { data: PaymentDocumentSummaryRecord | undefined }) =>
          !data ? null : data.status === 'voided' ? (
            <Typography variant='body2' color='text.secondary'>
              {paymentsText.page.voidedState}
            </Typography>
          ) : (
            <Stack direction='row' spacing={1}>
              <Button startIcon={<EditOutlinedIcon />} disabled={data.document_kind !== 'collection'} onClick={() => onOpenEdit(data)}>
                {paymentsText.page.edit}
              </Button>
              <Button color='warning' startIcon={<BlockOutlinedIcon />} onClick={() => onOpenVoid(data)}>
                {paymentsText.page.void}
              </Button>
            </Stack>
          ),
      },
    ],
    [commonText.actions, language, onOpenEdit, onOpenVoid, paymentsText.page.edit, paymentsText.page.void, paymentsText.page.voidedState, paymentsText.table.bookings, paymentsText.table.customer, paymentsText.table.date, paymentsText.table.journal, paymentsText.table.number, paymentsText.table.paymentMethod, paymentsText.table.status, paymentsText.table.total, paymentsText.table.type, sortBy, sortDir],
  );

  return (
    <SectionCard title={paymentsText.page.listTitle} subtitle={paymentsText.page.listSubtitle}>
      <AppAgGrid
        tableKey='payments-grid'
        rows={rows}
        columns={columns}
        language={language}
        searchLabel={language === 'ar' ? 'بحث السندات' : 'Search documents'}
        searchPlaceholder={language === 'ar' ? 'رقم السند أو العميل أو الحجز' : 'Document, customer, or booking'}
        columnsLabel={language === 'ar' ? 'الأعمدة' : 'Columns'}
        exportLabel={language === 'ar' ? 'تصدير' : 'Export'}
        resetLabel={language === 'ar' ? 'إعادة الضبط' : 'Reset'}
        closeLabel={language === 'ar' ? 'إغلاق' : 'Close'}
        noRowsLabel={language === 'ar' ? 'لا توجد نتائج مطابقة.' : 'No matching payment documents found.'}
        rowsPerPageLabel={language === 'ar' ? 'عدد الصفوف' : 'Rows per page'}
        quickSearchValue={tableSearchInput}
        onQuickSearchChange={onTableSearchChange}
        toolbarFilters={
          <Stack direction={{ xs: 'column', lg: 'row' }} spacing={1.5}>
            <TextField select size='small' label={language === 'ar' ? 'الحالة' : 'Status'} value={statusFilter} onChange={(event) => onStatusFilterChange(event.target.value)} sx={{ minWidth: 180 }}>
              <MenuItem value=''>{language === 'ar' ? 'كل الحالات' : 'All statuses'}</MenuItem>
              <MenuItem value='active'>{paymentDocumentStatusLabel(language, 'active')}</MenuItem>
              <MenuItem value='voided'>{paymentDocumentStatusLabel(language, 'voided')}</MenuItem>
            </TextField>
            <TextField select size='small' label={language === 'ar' ? 'النوع' : 'Kind'} value={documentKindFilter} onChange={(event) => onDocumentKindFilterChange(event.target.value)} sx={{ minWidth: 180 }}>
              <MenuItem value=''>{language === 'ar' ? 'كل الأنواع' : 'All kinds'}</MenuItem>
              <MenuItem value='collection'>{paymentKindLabel(language, 'collection')}</MenuItem>
              <MenuItem value='refund'>{paymentKindLabel(language, 'refund')}</MenuItem>
              <MenuItem value='custody_deposit'>{paymentKindLabel(language, 'custody_deposit')}</MenuItem>
              <MenuItem value='custody_compensation'>{paymentKindLabel(language, 'custody_compensation')}</MenuItem>
            </TextField>
            <TextField type='date' size='small' label={language === 'ar' ? 'من تاريخ' : 'From date'} value={dateFrom} onChange={(event) => onDateFromChange(event.target.value)} InputLabelProps={{ shrink: true }} />
            <TextField type='date' size='small' label={language === 'ar' ? 'إلى تاريخ' : 'To date'} value={dateTo} onChange={(event) => onDateToChange(event.target.value)} InputLabelProps={{ shrink: true }} />
          </Stack>
        }
        onSortChange={(nextSortBy, nextSortDir) => {
          const normalized = (nextSortBy as PaymentSortField | null) ?? 'payment_date';
          onSortChange(normalized, nextSortDir ?? 'desc');
        }}
        externalPagination={{
          total,
          page,
          pageSize,
          onPageChange,
          onPageSizeChange,
        }}
        loading={loading}
        csvFileName='payments.csv'
        onExportXlsx={() => {
          downloadFile(getPaymentsExcelUrl(undefined, exportFilters));
        }}
        getRowId={({ data }) => data.id}
      />
    </SectionCard>
  );
}
