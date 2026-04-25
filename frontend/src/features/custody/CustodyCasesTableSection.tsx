import { ToggleButton, ToggleButtonGroup } from '@mui/material';
import { useMemo } from 'react';

import { AppDataTable } from '../../components/data-table/AppDataTable';
import { SectionCard } from '../../components/SectionCard';
import { getCustodyStatusLabel, type Language } from './presentation';
import type { CustodyCaseRecord, CustodyCaseView } from './api';

type Props = {
  rows: CustodyCaseRecord[];
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
};

function formatAmount(value: number | null, emptyValue: string): string {
  if (value === null || value === undefined) return emptyValue;
  return `${value.toLocaleString()} EGP`;
}

export function CustodyCasesTableSection({
  rows,
  view,
  onViewChange,
  language,
  title,
  subtitle,
  viewOpenLabel,
  viewSettledLabel,
  viewAllLabel,
  labels,
}: Props) {
  const searchFields = useMemo(
    () => [
      (row: CustodyCaseRecord) => row.case_number,
      (row: CustodyCaseRecord) => row.customer_name ?? '',
      (row: CustodyCaseRecord) => row.booking_number ?? '',
      (row: CustodyCaseRecord) => row.dress_code ?? '',
      (row: CustodyCaseRecord) => row.notes ?? '',
      (row: CustodyCaseRecord) => getCustodyStatusLabel(row.status, language),
    ],
    [language],
  );

  return (
    <SectionCard title={title} subtitle={subtitle}>
      <ToggleButtonGroup
        size='small'
        value={view}
        exclusive
        onChange={(_event, value: CustodyCaseView | null) => {
          if (!value) return;
          onViewChange(value);
        }}
        aria-label='custody-view-filter'
      >
        <ToggleButton value='open'>{viewOpenLabel}</ToggleButton>
        <ToggleButton value='settled'>{viewSettledLabel}</ToggleButton>
        <ToggleButton value='all'>{viewAllLabel}</ToggleButton>
      </ToggleButtonGroup>
      <AppDataTable
        tableKey='custody-cases'
        rows={rows}
        columns={[
          { key: 'case_number', header: labels.caseNumber, searchValue: (row) => row.case_number, render: (row) => row.case_number },
          { key: 'custody_date', header: labels.custodyDate, searchValue: (row) => row.custody_date, render: (row) => row.custody_date },
          {
            key: 'customer_name',
            header: labels.customerName,
            searchValue: (row) => row.customer_name ?? '',
            render: (row) => row.customer_name ?? labels.emptyValue,
          },
          {
            key: 'booking_number',
            header: labels.bookingNumber,
            searchValue: (row) => row.booking_number ?? '',
            render: (row) => row.booking_number ?? labels.emptyValue,
          },
          {
            key: 'dress_code',
            header: labels.dressCode,
            searchValue: (row) => row.dress_code ?? '',
            render: (row) => row.dress_code ?? labels.emptyValue,
          },
          {
            key: 'notes',
            header: labels.statement,
            searchValue: (row) => row.notes ?? '',
            render: (row) => row.notes ?? labels.emptyValue,
          },
          {
            key: 'security_deposit_amount',
            header: labels.depositAmount,
            searchValue: (row) => row.security_deposit_amount?.toString() ?? '',
            render: (row) => formatAmount(row.security_deposit_amount, labels.emptyValue),
          },
          {
            key: 'compensation_amount',
            header: labels.compensationAmount,
            searchValue: (row) => row.compensation_amount?.toString() ?? '',
            render: (row) => formatAmount(row.compensation_amount, labels.emptyValue),
          },
          {
            key: 'status',
            header: labels.status,
            searchValue: (row) => getCustodyStatusLabel(row.status, language),
            render: (row) => getCustodyStatusLabel(row.status, language),
          },
        ]}
        searchLabel={labels.search}
        searchPlaceholder={labels.searchPlaceholder}
        resetColumnsLabel={labels.reset}
        noRowsLabel={labels.noRows}
        filtersLabel={labels.filters}
        columnsLabel={labels.columns}
        exportLabel={labels.export}
        rowsPerPageLabel={labels.rowsPerPage}
        closeLabel={labels.close}
        searchFields={searchFields}
      />
    </SectionCard>
  );
}
