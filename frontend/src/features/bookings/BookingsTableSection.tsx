import BlockOutlinedIcon from '@mui/icons-material/BlockOutlined';
import DeleteForeverOutlinedIcon from '@mui/icons-material/DeleteForeverOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import { Button, Chip, IconButton, Stack, Tooltip } from '@mui/material';
import type { ColDef } from 'ag-grid-community';
import { useMemo } from 'react';

import { AppAgGrid } from '../../components/ag-grid';
import { SectionCard } from '../../components/SectionCard';
import { getBookingsExcelUrl, type BookingExportFilters } from '../exports/api';
import { EMPTY_VALUE, bookingStatusLabel, useCommonText } from '../../text/common';
import { useBookingsText } from '../../text/bookings';
import { BookingsTableFilters } from './BookingsTableFilters';
import type { DatePreset } from '../../components/inputs/useDateRangeFilter';
import type { BookingSummaryRecord } from './api';

export type BookingSortField = 'booking_date' | 'booking_number' | 'customer_name' | 'status';

type Props = {
  language: 'ar' | 'en';
  rows: BookingSummaryRecord[];
  total: number;
  loading: boolean;
  searchInput: string;
  onSearchChange: (value: string) => void;
  statusFilter: string;
  onStatusFilterChange: (value: string) => void;
  activePreset: DatePreset;
  customFrom: string;
  customTo: string;
  onSelectPreset: (preset: DatePreset) => void;
  onCustomFromChange: (v: string) => void;
  onCustomToChange: (v: string) => void;
  page: number;
  pageSize: number;
  onPageChange: (value: number) => void;
  onPageSizeChange: (value: number) => void;
  sortBy: BookingSortField;
  sortDir: 'asc' | 'desc';
  onSortChange: (sortBy: BookingSortField, sortDir: 'asc' | 'desc') => void;
  exportFilters: BookingExportFilters;
  onOpenEdit: (record: BookingSummaryRecord) => void;
  onOpenCancel: (record: BookingSummaryRecord) => void;
  onDelete: (record: BookingSummaryRecord) => void;
  onExport: (format: 'csv' | 'xlsx', scope: 'all' | 'page') => void;
};

export function BookingsTableSection({
  language,
  rows,
  total,
  loading,
  searchInput,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  activePreset,
  customFrom,
  customTo,
  onSelectPreset,
  onCustomFromChange,
  onCustomToChange,
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
  sortBy,
  sortDir,
  onSortChange,
  exportFilters,
  onOpenEdit,
  onOpenCancel,
  onDelete,
  onExport,
}: Props) {
  const commonText = useCommonText();
  const bookingsText = useBookingsText();
  const columns = useMemo<ColDef<BookingSummaryRecord>[]>(
    () => [
      { colId: 'booking_number', field: 'booking_number', headerName: bookingsText.table.bookingNumber, pinned: language === 'ar' ? 'right' : 'left', sort: sortBy === 'booking_number' ? sortDir : null },
      { colId: 'external_code', field: 'external_code', headerName: bookingsText.table.externalCode, valueFormatter: ({ value }) => value ?? EMPTY_VALUE },
      { colId: 'customer_name', field: 'customer_name', headerName: bookingsText.table.customer, sort: sortBy === 'customer_name' ? sortDir : null },
      { colId: 'booking_date', field: 'booking_date', headerName: bookingsText.table.bookingDate, sort: sortBy === 'booking_date' ? sortDir : null },
      { colId: 'line_count', field: 'line_count', headerName: bookingsText.table.lineCount, filter: 'agNumberColumnFilter' },
      { colId: 'service_summary', field: 'service_summary', headerName: bookingsText.table.serviceSummary, flex: 1.3 },
      { colId: 'next_service_date', field: 'next_service_date', headerName: bookingsText.table.nextServiceDate, valueFormatter: ({ value }) => value ?? EMPTY_VALUE, sort: sortBy === 'booking_date' ? sortDir : null },
      { colId: 'total_amount', field: 'total_amount', headerName: bookingsText.table.total, filter: 'agNumberColumnFilter' },
      { colId: 'paid_total', field: 'paid_total', headerName: bookingsText.table.paid, filter: 'agNumberColumnFilter' },
      { colId: 'remaining_amount', field: 'remaining_amount', headerName: bookingsText.table.remaining, filter: 'agNumberColumnFilter' },
      { colId: 'notes', field: 'notes', headerName: bookingsText.table.notes, valueFormatter: ({ value }) => value ?? EMPTY_VALUE, flex: 1.2 },
      { colId: 'created_by_name', field: 'created_by_name', headerName: bookingsText.table.createdBy, valueFormatter: ({ value }) => value ?? EMPTY_VALUE, flex: 1.0 },
      {
        colId: 'status',
        headerName: bookingsText.table.status,
        valueGetter: ({ data }) => data?.status ?? '',
        cellRenderer: ({ data }: { data: BookingSummaryRecord | undefined }) =>
          data ? <Chip size='small' label={bookingStatusLabel(language, data.status)} color={data.status === 'completed' ? 'success' : data.status === 'cancelled' ? 'default' : 'warning'} /> : null,
        sort: sortBy === 'status' ? sortDir : null,
      },
      {
        colId: 'actions',
        headerName: commonText.actions,
        sortable: false,
        filter: false,
        width: 130,
        suppressSizeToFit: true,
        pinned: language === 'ar' ? 'left' : 'right',
        cellRenderer: ({ data }: { data: BookingSummaryRecord | undefined }) =>
          data ? (
            <Stack direction='row' spacing={0.5} alignItems='center' justifyContent='center' sx={{ height: '100%' }}>
              <Tooltip title={bookingsText.page.openDocument} arrow enterTouchDelay={0}>
                <IconButton size='small' color='primary' sx={{ p: 0.75 }} onClick={() => onOpenEdit(data)}>
                  <EditOutlinedIcon fontSize='small' />
                </IconButton>
              </Tooltip>
              {data.status !== 'cancelled' && (
                <Tooltip title={commonText.cancel} arrow enterTouchDelay={0}>
                  <IconButton size='small' color='warning' sx={{ p: 0.75 }} onClick={() => onOpenCancel(data)}>
                    <BlockOutlinedIcon fontSize='small' />
                  </IconButton>
                </Tooltip>
              )}
              <Tooltip title={commonText.delete} arrow enterTouchDelay={0}>
                <IconButton size='small' color='error' sx={{ p: 0.75 }} onClick={() => onDelete(data)}>
                  <DeleteForeverOutlinedIcon fontSize='small' />
                </IconButton>
              </Tooltip>
            </Stack>
          ) : null,
      },
    ],
    [bookingsText.page.openDocument, bookingsText.table.bookingNumber, bookingsText.table.bookingDate, bookingsText.table.customer, bookingsText.table.lineCount, bookingsText.table.nextServiceDate, bookingsText.table.paid, bookingsText.table.remaining, bookingsText.table.serviceSummary, bookingsText.table.status, bookingsText.table.total, bookingsText.table.notes, bookingsText.table.createdBy, commonText.actions, commonText.cancel, commonText.delete, language, onDelete, onOpenCancel, onOpenEdit, sortBy, sortDir],
  );

  return (
    <SectionCard title={bookingsText.page.listTitle} subtitle={bookingsText.page.listSubtitle}>
      <AppAgGrid
        tableKey='bookings-grid'
        rows={rows}
        columns={columns}
        language={language}
        searchLabel={language === 'ar' ? 'بحث الحجوزات' : 'Search bookings'}
        searchPlaceholder={language === 'ar' ? 'رقم الحجز أو اسم العميل أو الخدمة' : 'Booking, customer, or service'}
        columnsLabel={language === 'ar' ? 'الأعمدة' : 'Columns'}
        exportLabel={language === 'ar' ? 'تصدير' : 'Export'}
        resetLabel={language === 'ar' ? 'إعادة الضبط' : 'Reset'}
        closeLabel={language === 'ar' ? 'إغلاق' : 'Close'}
        noRowsLabel={language === 'ar' ? 'لا توجد حجوزات مطابقة.' : 'No matching bookings found.'}
        rowsPerPageLabel={language === 'ar' ? 'عدد الصفوف' : 'Rows per page'}
        quickSearchValue={searchInput}
        onQuickSearchChange={onSearchChange}
        toolbarFilters={
          <BookingsTableFilters
            language={language}
            statusFilter={statusFilter}
            onStatusChange={onStatusFilterChange}
            activePreset={activePreset}
            customFrom={customFrom}
            customTo={customTo}
            onSelectPreset={onSelectPreset}
            onCustomFromChange={onCustomFromChange}
            onCustomToChange={onCustomToChange}
          />
        }
        onSortChange={(nextSortBy, nextSortDir) => {
          const normalized = (nextSortBy as BookingSortField | null) ?? 'booking_date';
          onSortChange(normalized, nextSortDir ?? 'desc');
        }}
        externalPagination={{ total, page, pageSize, onPageChange, onPageSizeChange }}
        loading={loading}
        onExport={onExport}
        getRowId={({ data }) => data.id}
      />
    </SectionCard>
  );
}
