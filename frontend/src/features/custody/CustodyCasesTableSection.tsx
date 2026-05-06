import { Chip, MenuItem, TextField } from '@mui/material';
import type { ColDef } from 'ag-grid-community';
import { useMemo } from 'react';

import { AppAgGrid } from '../../components/ag-grid';
import { SectionCard } from '../../components/SectionCard';
import { getCustodyStatusLabel, type Language } from './presentation';
import type { CustodyCaseRecord, CustodyCaseView } from './api';

type Props = {
  rows: CustodyCaseRecord[];
  total: number;
  loading: boolean;
  page: number;
  pageSize: number;
  onPageChange: (value: number) => void;
  onPageSizeChange: (value: number) => void;
  view: CustodyCaseView;
  onViewChange: (value: CustodyCaseView) => void;
  language: Language;
  title: string;
  subtitle: string;
  viewOpenLabel: string;
  viewSettledLabel: string;
  viewAllLabel: string;
  labels: {
    caseNumber: string;
    custodyDate: string;
    customerName: string;
    bookingNumber: string;
    dressCode: string;
    statement: string;
    depositAmount: string;
    compensationAmount: string;
    status: string;
    search: string;
    searchPlaceholder: string;
    reset: string;
    noRows: string;
    filters: string;
    columns: string;
    export: string;
    rowsPerPage: string;
    close: string;
    emptyValue: string;
  };
  onExport: (format: 'csv' | 'xlsx', scope: 'all' | 'page') => void;
};

export function CustodyCasesTableSection({
  rows,
  total,
  loading,
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
  view,
  onViewChange,
  language,
  title,
  subtitle,
  labels,
  onExport,
}: Props) {
  const isAr = language === 'ar';
  
  const columns = useMemo<ColDef<CustodyCaseRecord>[]>(
    () => [
      { colId: 'case_number', field: 'case_number', headerName: labels.caseNumber, pinned: isAr ? 'right' : 'left' },
      { colId: 'custody_date', field: 'custody_date', headerName: labels.custodyDate },
      { colId: 'customer_name', field: 'customer_name', headerName: labels.customerName },
      { colId: 'booking_number', field: 'booking_number', headerName: labels.bookingNumber },
      { colId: 'dress_code', field: 'dress_code', headerName: labels.dressCode, valueFormatter: ({ value }) => value ?? labels.emptyValue },
      { colId: 'notes', field: 'notes', headerName: labels.statement, flex: 1.2 },
      { 
        colId: 'security_deposit_amount', 
        field: 'security_deposit_amount', 
        headerName: labels.depositAmount, 
        filter: 'agNumberColumnFilter',
        valueFormatter: (params) => params.value ? `${params.value.toLocaleString()} EGP` : labels.emptyValue
      },
      { 
        colId: 'compensation_amount', 
        field: 'compensation_amount', 
        headerName: labels.compensationAmount, 
        filter: 'agNumberColumnFilter',
        valueFormatter: (params) => params.value ? `${params.value.toLocaleString()} EGP` : labels.emptyValue
      },
      {
        colId: 'status',
        headerName: labels.status,
        cellRenderer: ({ data }: { data: CustodyCaseRecord | undefined }) =>
          data ? <Chip size='small' color={data.status === 'settled' ? 'success' : 'primary'} label={getCustodyStatusLabel(data.status, language)} /> : null,
      },
    ],
    [labels, language, isAr],
  );

  return (
    <SectionCard title={title} subtitle={subtitle}>
      <AppAgGrid
        tableKey='custody-cases-grid'
        rows={rows}
        columns={columns}
        language={language}
        searchLabel={labels.search}
        searchPlaceholder={labels.searchPlaceholder}
        columnsLabel={labels.columns}
        exportLabel={labels.export}
        resetLabel={labels.reset}
        closeLabel={labels.close}
        noRowsLabel={labels.noRows}
        rowsPerPageLabel={labels.rowsPerPage}
        toolbarFilters={
          <TextField select size='small' label={labels.filters} value={view} onChange={(e) => onViewChange(e.target.value as CustodyCaseView)} sx={{ minWidth: 160 }}>
            <MenuItem value='all'>{isAr ? 'الكل' : 'All'}</MenuItem>
            <MenuItem value='open'>{isAr ? 'المفتوحة' : 'Open'}</MenuItem>
            <MenuItem value='settled'>{isAr ? 'المسواة' : 'Settled'}</MenuItem>
          </TextField>
        }
        externalPagination={{ total, page, pageSize, onPageChange, onPageSizeChange }}
        loading={loading}
        onExport={onExport}
        getRowId={({ data }) => data.id}
      />
    </SectionCard>
  );
}
