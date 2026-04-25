import type { ReactNode } from 'react';

export type DataTableColumn<Row> = {
  key: string;
  header: string;
  searchValue?: (row: Row) => string;
  sortValue?: (row: Row) => string | number | boolean | null | undefined;
  exportValue?: (row: Row) => string | number | boolean | null | undefined;
  render: (row: Row) => ReactNode;
  defaultVisible?: boolean;
};

export type DataTablePreferenceState = {
  visibleColumnKeys: string[];
  orderedColumnKeys: string[];
  pageSize: number;
};
