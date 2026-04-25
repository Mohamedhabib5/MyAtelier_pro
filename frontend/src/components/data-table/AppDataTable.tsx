import type { ColDef } from 'ag-grid-community';
import { useMemo } from 'react';

import { AppAgGrid } from '../ag-grid';
import type { DataTableColumn } from './types';

type AppDataTableProps<Row> = {
  tableKey: string;
  title?: string;
  subtitle?: string;
  rows: Row[];
  columns: DataTableColumn<Row>[];
  searchPlaceholder: string;
  searchLabel: string;
  resetColumnsLabel: string;
  noRowsLabel: string;
  filtersLabel: string;
  columnsLabel: string;
  exportLabel: string;
  searchFields?: Array<(row: Row) => string>;
  filterContent?: React.ReactNode;
  footerContent?: React.ReactNode;
  rowsPerPageLabel?: string;
  closeLabel?: string;
};

export function AppDataTable<Row>({
  tableKey,
  title,
  subtitle,
  rows,
  columns,
  searchPlaceholder,
  searchLabel,
  resetColumnsLabel,
  noRowsLabel,
  columnsLabel,
  exportLabel,
  filterContent,
  footerContent,
  rowsPerPageLabel = 'Rows per page',
  closeLabel = 'Close',
}: AppDataTableProps<Row>) {
  const localeLanguage = /[\u0600-\u06FF]/.test(`${searchLabel}${searchPlaceholder}${columnsLabel}${exportLabel}`) ? 'ar' : 'en';
  const agColumns = useMemo<ColDef<Row>[]>(
    () =>
      columns.map((column) => ({
        colId: column.key,
        headerName: column.header,
        hide: column.defaultVisible === false,
        sortable: true,
        filter: true,
        resizable: true,
        valueGetter: column.searchValue ? ({ data }: { data: Row | undefined }) => (data ? column.searchValue?.(data) : '') : undefined,
        getQuickFilterText: column.searchValue ? ({ data }: { data: Row | undefined }) => (data ? column.searchValue?.(data) ?? '' : '') : undefined,
        comparator: column.sortValue
          ? (_left, _right, nodeA, nodeB) => {
              const leftValue = nodeA?.data ? column.sortValue?.(nodeA.data) : '';
              const rightValue = nodeB?.data ? column.sortValue?.(nodeB.data) : '';
              return String(leftValue ?? '').localeCompare(String(rightValue ?? ''), undefined, { numeric: true, sensitivity: 'base' });
            }
          : undefined,
        cellRenderer: ({ data }: { data: Row | undefined }) => (data ? column.render(data) : null),
      })),
    [columns],
  );

  return (
    <>
      <AppAgGrid
        tableKey={tableKey}
        title={title}
        subtitle={subtitle}
        rows={rows}
        columns={agColumns}
        language={localeLanguage}
        searchLabel={searchLabel}
        searchPlaceholder={searchPlaceholder}
        columnsLabel={columnsLabel}
        exportLabel={exportLabel}
        resetLabel={resetColumnsLabel}
        closeLabel={closeLabel}
        noRowsLabel={noRowsLabel}
        rowsPerPageLabel={rowsPerPageLabel}
        toolbarFilters={filterContent}
        csvFileName={`${tableKey}.csv`}
      />
      {footerContent}
    </>
  );
}
