import BlockOutlinedIcon from '@mui/icons-material/BlockOutlined';
import DeleteForeverOutlinedIcon from '@mui/icons-material/DeleteForeverOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import { Button, Chip, MenuItem, Stack, TextField, Typography } from '@mui/material';
import type { ColDef } from 'ag-grid-community';
import { useMemo } from 'react';

import { AppAgGrid } from '../../components/ag-grid';
import { SectionCard } from '../../components/SectionCard';
import { useLanguage } from '../language/LanguageProvider';
import { useCommonText } from '../../text/common';
import { useDisbursementsText } from '../../text/disbursements';
import type { DisbursementVoucherRecord } from './api';
import { AppDateRangeFilter } from '../../components/inputs/AppDateRangeFilter';
import type { DatePreset } from '../../components/inputs/useDateRangeFilter';

type DisbursementSortField = 'voucher_date' | 'voucher_number' | 'amount' | 'status' | 'payee_type';

type DisbursementsTableSectionProps = {
  rows: DisbursementVoucherRecord[];
  total: number;
  loading: boolean;
  tableSearchInput: string;
  onTableSearchChange: (value: string) => void;
  statusFilter: string;
  onStatusFilterChange: (value: string) => void;
  payeeTypeFilter: string;
  onPayeeTypeFilterChange: (value: string) => void;
  activePreset: DatePreset;
  customFrom: string;
  customTo: string;
  onSelectPreset: (preset: DatePreset) => void;
  onCustomFromChange: (value: string) => void;
  onCustomToChange: (value: string) => void;
  page: number;
  pageSize: number;
  onPageChange: (value: number) => void;
  onPageSizeChange: (value: number) => void;
  sortBy: DisbursementSortField;
  sortDir: 'asc' | 'desc';
  onSortChange: (sortBy: DisbursementSortField, sortDir: 'asc' | 'desc') => void;
  onOpenEdit: (row: DisbursementVoucherRecord) => void;
  onOpenVoid: (row: DisbursementVoucherRecord) => void;
  onDelete: (row: DisbursementVoucherRecord) => void;
};

export function DisbursementsTableSection({
  rows,
  total,
  loading,
  tableSearchInput,
  onTableSearchChange,
  statusFilter,
  onStatusFilterChange,
  payeeTypeFilter,
  onPayeeTypeFilterChange,
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
  onOpenEdit,
  onOpenVoid,
  onDelete,
}: DisbursementsTableSectionProps) {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const text = useDisbursementsText();
  const isAr = language === 'ar';

  const columns = useMemo<ColDef<DisbursementVoucherRecord>[]>(
    () => [
      { 
        colId: 'voucher_number', 
        field: 'voucher_number', 
        headerName: isAr ? 'رقم السند' : 'Voucher No', 
        pinned: isAr ? 'right' : 'left', 
        sort: sortBy === 'voucher_number' ? sortDir : null 
      },
      { 
        colId: 'payee_type', 
        headerName: text.page.payeeType,
        valueGetter: ({ data }) => (data ? text.page.types[data.payee_type] : ''),
        cellRenderer: ({ data }: { data: DisbursementVoucherRecord | undefined }) => 
          data ? <Chip size='small' label={text.page.types[data.payee_type]} /> : null,
        sort: sortBy === 'payee_type' ? sortDir : null 
      },
      { colId: 'payee_name', field: 'payee_name', headerName: text.editor.payeeName },
      { colId: 'payment_method_name', field: 'payment_method_name', headerName: text.page.safe },
      { colId: 'voucher_date', field: 'voucher_date', headerName: text.page.date, sort: sortBy === 'voucher_date' ? sortDir : null },
      { colId: 'amount', field: 'amount', headerName: text.page.amount, filter: 'agNumberColumnFilter' },
      {
        colId: 'status',
        headerName: text.page.status,
        valueGetter: ({ data }) => (data ? (isAr ? (data.status === 'voided' ? 'ملغى' : 'نشط') : data.status) : ''),
        cellRenderer: ({ data }: { data: DisbursementVoucherRecord | undefined }) => 
          data ? (
            <Chip 
              size='small' 
              color={data.status === 'voided' ? 'warning' : 'primary'} 
              label={isAr ? (data.status === 'voided' ? 'ملغى' : 'نشط') : data.status} 
            />
          ) : null,
        sort: sortBy === 'status' ? sortDir : null,
      },
      {
        colId: 'journal',
        headerName: text.page.journal,
        cellRenderer: ({ data }: { data: DisbursementVoucherRecord | undefined }) =>
          data?.journal_entry_number ? (
            <Stack spacing={0.5}>
              <Stack direction='row' spacing={1} alignItems='center'>
                <ReceiptLongOutlinedIcon fontSize='small' color='action' />
                <Typography variant='body2'>{data.journal_entry_number}</Typography>
              </Stack>
              <Typography variant='caption'>{isAr ? (data.journal_entry_status === 'posted' ? 'مرحل' : 'مسودة') : data.journal_entry_status}</Typography>
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
        pinned: isAr ? 'left' : 'right',
        cellRenderer: ({ data }: { data: DisbursementVoucherRecord | undefined }) =>
          !data ? null : data.status === 'voided' ? (
            <Typography variant='body2' color='text.secondary'>
              {text.page.voidedState}
            </Typography>
          ) : (
            <Stack direction='row' spacing={1}>
              <Button startIcon={<EditOutlinedIcon />} onClick={() => onOpenEdit(data)}>
                {text.page.edit}
              </Button>
              <Button color='warning' startIcon={<BlockOutlinedIcon />} onClick={() => onOpenVoid(data)}>
                {text.page.void}
              </Button>
              <Button color='error' startIcon={<DeleteForeverOutlinedIcon />} onClick={() => onDelete(data)}>
                {text.page.delete}
              </Button>
            </Stack>
          ),
      },
    ],
    [language, sortBy, sortDir, text, commonText, isAr]
  );

  return (
    <SectionCard title={isAr ? 'قائمة سندات الصرف' : 'Disbursements list'} subtitle={isAr ? 'كل صف يمثل سندًا واحدًا مع المستلم والحالة والقيد المحاسبي المرتبط.' : 'Each row represents one voucher with payee, status, and linked journal entry.'}>
      <AppAgGrid
        tableKey='disbursements-grid'
        rows={rows}
        columns={columns}
        language={language}
        searchLabel={language === 'ar' ? 'بحث السندات' : 'Search documents'}
        searchPlaceholder={text.page.searchHint}
        columnsLabel={language === 'ar' ? 'الأعمدة' : 'Columns'}
        exportLabel={language === 'ar' ? 'تصدير' : 'Export'}
        resetLabel={language === 'ar' ? 'إعادة الضبط' : 'Reset'}
        closeLabel={language === 'ar' ? 'إغلاق' : 'Close'}
        noRowsLabel={text.page.noResults}
        rowsPerPageLabel={language === 'ar' ? 'عدد الصفوف' : 'Rows per page'}
        quickSearchValue={tableSearchInput}
        onQuickSearchChange={onTableSearchChange}
        toolbarFilters={
          <Stack direction={{ xs: 'column', lg: 'row' }} spacing={1.5}>
            <TextField
              select
              size='small'
              label={text.page.payeeType}
              value={payeeTypeFilter}
              onChange={(e) => onPayeeTypeFilterChange(e.target.value)}
              sx={{ minWidth: 160 }}
            >
              <MenuItem value="">{isAr ? 'كل الجهات' : 'All'}</MenuItem>
              <MenuItem value="customer">{text.page.types.customer}</MenuItem>
              <MenuItem value="supplier">{text.page.types.supplier}</MenuItem>
              <MenuItem value="employee">{text.page.types.employee}</MenuItem>
              <MenuItem value="expense">{text.page.types.expense}</MenuItem>
            </TextField>

            <TextField
              select
              size='small'
              label={text.page.status}
              value={statusFilter}
              onChange={(e) => onStatusFilterChange(e.target.value)}
              sx={{ minWidth: 140 }}
            >
              <MenuItem value="">{isAr ? 'كل الحالات' : 'All'}</MenuItem>
              <MenuItem value="active">{isAr ? 'نشط' : 'Active'}</MenuItem>
              <MenuItem value="voided">{isAr ? 'ملغى' : 'Voided'}</MenuItem>
            </TextField>

            <AppDateRangeFilter
              language={language}
              activePreset={activePreset}
              customFrom={customFrom}
              customTo={customTo}
              onSelectPreset={onSelectPreset}
              onCustomFromChange={onCustomFromChange}
              onCustomToChange={onCustomToChange}
            />
          </Stack>
        }
        onSortChange={(nextSortBy, nextSortDir) => {
          const normalized = (nextSortBy as DisbursementSortField | null) ?? 'voucher_date';
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
        getRowId={({ data }) => data.id}
      />
    </SectionCard>
  );
}
