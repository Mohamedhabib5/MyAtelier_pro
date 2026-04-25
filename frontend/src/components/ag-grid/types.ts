import type { ColDef } from 'ag-grid-community';

export type AgGridPreferenceState = {
  columnState?: Array<{
    colId: string;
    hide?: boolean | null;
    width?: number;
    pinned?: 'left' | 'right' | null;
    sort?: 'asc' | 'desc' | null;
    sortIndex?: number | null;
  }>;
  filterModel?: Record<string, unknown>;
  pageSize: number;
};

export type AppAgGridColumn<Row> = ColDef<Row>;
