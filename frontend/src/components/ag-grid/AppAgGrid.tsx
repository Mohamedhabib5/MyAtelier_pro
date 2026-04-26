import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined';
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
import ViewColumnOutlinedIcon from '@mui/icons-material/ViewColumnOutlined';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  InputAdornment,
  Menu,
  MenuItem,
  Paper,
  Stack,
  TablePagination,
  TextField,
  Typography,
} from '@mui/material';
import type { ColDef, Column, ColumnMovedEvent, ColumnPinnedEvent, ColumnResizedEvent, ColumnVisibleEvent, FilterChangedEvent, FirstDataRenderedEvent, GetRowIdParams, GridApi, GridReadyEvent, SortChangedEvent } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { useCallback, useMemo, useRef, useState } from 'react';

import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-quartz.css';
import '../../styles/ag-grid.css';
import { ensureAgGridModulesRegistered } from '../../lib/agGrid';
import { buildAgGridLocaleText } from './buildAgGridLocaleText';
import { GridColumnPanel } from './GridColumnPanel';
import type { AgGridPreferenceState, AppAgGridColumn } from './types';
import { useAgGridPreferences } from './useAgGridPreferences';

ensureAgGridModulesRegistered();

type ExternalPagination = {
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
};

type Props<Row> = {
  tableKey: string;
  rows: Row[];
  columns: AppAgGridColumn<Row>[];
  title?: string;
  subtitle?: string;
  language: 'ar' | 'en';
  searchLabel: string;
  searchPlaceholder: string;
  columnsLabel: string;
  exportLabel: string;
  resetLabel: string;
  closeLabel: string;
  noRowsLabel: string;
  rowsPerPageLabel: string;
  loading?: boolean;
  error?: string | null;
  toolbarFilters?: React.ReactNode;
  toolbarActions?: React.ReactNode;
  quickSearchValue?: string;
  onQuickSearchChange?: (value: string) => void;
  externalPagination?: ExternalPagination;
  csvFileName?: string;
  onExportXlsx?: () => void;
  getRowId?: (params: GetRowIdParams<Row>) => string;
  emptyState?: React.ReactNode;
  height?: number;
  onSortChange?: (sortBy: string | null, sortDir: 'asc' | 'desc' | null) => void;
  hideToolbar?: boolean;
  pagination?: boolean;
};

export function AppAgGrid<Row>({
  tableKey,
  rows,
  columns,
  title,
  subtitle,
  language,
  searchLabel,
  searchPlaceholder,
  columnsLabel,
  exportLabel,
  resetLabel,
  closeLabel,
  noRowsLabel,
  rowsPerPageLabel,
  loading = false,
  error = null,
  toolbarFilters,
  toolbarActions,
  quickSearchValue,
  onQuickSearchChange,
  externalPagination,
  csvFileName,
  onExportXlsx,
  getRowId,
  emptyState,
  height = 520,
  onSortChange,
  hideToolbar = false,
  pagination = true,
}: Props<Row>) {
  const [internalSearch, setInternalSearch] = useState('');
  const [columnsAnchor, setColumnsAnchor] = useState<HTMLElement | null>(null);
  const [exportAnchor, setExportAnchor] = useState<HTMLElement | null>(null);
  const gridApiRef = useRef<GridApi<Row> | null>(null);
  const { state, setState, defaults } = useAgGridPreferences(tableKey);
  const search = quickSearchValue ?? internalSearch;
  const localeText = useMemo(() => buildAgGridLocaleText(language), [language]);

  const columnDefs = useMemo<ColDef<Row>[]>(
    () =>
      columns.map((column) => ({
        sortable: true,
        filter: true,
        resizable: true,
        minWidth: 120,
        suppressHeaderMenuButton: false,
        ...column,
      })),
    [columns],
  );

  const saveGridState = useCallback(() => {
    const api = gridApiRef.current;
    if (!api) return;
    const nextState: AgGridPreferenceState = {
      columnState: api.getColumnState().map((item) => ({
        colId: item.colId,
        hide: item.hide ?? undefined,
        width: item.width ?? undefined,
        pinned: item.pinned === true ? 'left' : item.pinned === false ? undefined : (item.pinned ?? undefined),
        sort: item.sort ?? undefined,
        sortIndex: item.sortIndex ?? undefined,
      })),
      filterModel: api.getFilterModel(),
      pageSize: externalPagination?.pageSize ?? state.pageSize,
    };
    setState(nextState);
  }, [externalPagination?.pageSize, setState, state.pageSize]);

  const applySavedState = useCallback(
    (api: GridApi<Row>) => {
      if (state.columnState?.length) {
        api.applyColumnState({ state: state.columnState, applyOrder: true });
      }
      if (state.filterModel && !externalPagination) {
        api.setFilterModel(state.filterModel);
      }
    },
    [externalPagination, state.columnState, state.filterModel],
  );

  const handleGridReady = useCallback(
    (event: GridReadyEvent<Row>) => {
      gridApiRef.current = event.api;
      applySavedState(event.api);
    },
    [applySavedState],
  );

  const handleFirstDataRendered = useCallback(
    (event: FirstDataRenderedEvent<Row>) => {
      applySavedState(event.api);
    },
    [applySavedState],
  );

  const handleGridStateChanged = useCallback(
    (_event: ColumnMovedEvent<Row> | ColumnVisibleEvent<Row> | ColumnPinnedEvent<Row> | ColumnResizedEvent<Row> | SortChangedEvent<Row> | FilterChangedEvent<Row>) => {
      saveGridState();
    },
    [saveGridState],
  );

  const columnsList: Column[] = gridApiRef.current?.getColumns() ?? [];

  const visibleRowsCount = externalPagination ? externalPagination.total : rows.length;

  return (
    <Stack spacing={2}>
      {(title || subtitle) ? (
        <Box>
          {title ? <Typography variant='h6'>{title}</Typography> : null}
          {subtitle ? <Typography color='text.secondary'>{subtitle}</Typography> : null}
        </Box>
      ) : null}

      {error ? <Alert severity='error'>{error}</Alert> : null}

      <Paper variant='outlined' sx={{ overflow: 'hidden', borderRadius: 3 }}>
        {!hideToolbar ? (
        <Stack spacing={2} sx={{ p: { xs: 2, md: 2.5 }, background: 'linear-gradient(180deg, rgba(124,58,237,0.05) 0%, rgba(124,58,237,0) 100%)' }}>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} justifyContent='space-between' alignItems={{ md: 'center' }}>
            <Stack spacing={0.5}>
              <Typography variant='subtitle1' fontWeight={700}>
                {title ?? searchLabel}
              </Typography>
              <Typography variant='body2' color='text.secondary'>
                {visibleRowsCount}
              </Typography>
            </Stack>
            <TextField
              label={searchLabel}
              placeholder={searchPlaceholder}
              value={search}
              onChange={(event) => {
                if (onQuickSearchChange) {
                  onQuickSearchChange(event.target.value);
                } else {
                  setInternalSearch(event.target.value);
                }
              }}
              size='small'
              sx={{ minWidth: { xs: '100%', md: 320 } }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position='start'>
                    <SearchOutlinedIcon fontSize='small' color='action' />
                  </InputAdornment>
                ),
              }}
            />
          </Stack>

          <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.25} justifyContent='space-between' alignItems={{ md: 'center' }}>
            <Box>{toolbarFilters}</Box>
            <Stack direction='row' spacing={1} flexWrap='wrap' useFlexGap>
              {toolbarActions}
              <Button variant='outlined' startIcon={<ViewColumnOutlinedIcon />} onClick={(event) => setColumnsAnchor(event.currentTarget)}>
                {columnsLabel}
              </Button>
              <Button variant='contained' color='inherit' startIcon={<DownloadOutlinedIcon />} onClick={(event) => setExportAnchor(event.currentTarget)}>
                {exportLabel}
              </Button>
            </Stack>
          </Stack>
        </Stack>
        ) : null}

        <Box className='ag-theme-quartz app-ag-grid' sx={{ height, width: '100%' }}>
          {loading ? (
            <Stack alignItems='center' justifyContent='center' sx={{ height: '100%', gap: 1.5 }}>
              <CircularProgress size={24} />
              <Typography color='text.secondary'>{language === 'ar' ? 'جار التحميل...' : 'Loading...'}</Typography>
            </Stack>
          ) : (
            <AgGridReact<Row>
              theme='legacy'
              rowData={rows}
              columnDefs={columnDefs}
              localeText={localeText}
              quickFilterText={search}
              enableRtl={language === 'ar'}
              pagination={!externalPagination && pagination}
              paginationPageSize={externalPagination?.pageSize ?? state.pageSize}
              suppressPaginationPanel
              rowSelection={{ mode: 'multiRow', checkboxes: false, headerCheckbox: false }}
              animateRows
              suppressDragLeaveHidesColumns
              suppressCellFocus={false}
              getRowId={getRowId}
              overlayNoRowsTemplate={`<span>${noRowsLabel}</span>`}
              onGridReady={handleGridReady}
              onFirstDataRendered={handleFirstDataRendered}
              onColumnMoved={handleGridStateChanged}
              onColumnPinned={handleGridStateChanged}
              onColumnVisible={handleGridStateChanged}
              onColumnResized={(event) => {
                if (event.finished) {
                  handleGridStateChanged(event);
                }
              }}
              onSortChanged={(event) => {
                handleGridStateChanged(event);
                if (onSortChange) {
                  const sorted = event.api.getColumnState().find((column) => column.sort);
                  onSortChange(sorted?.colId ?? null, (sorted?.sort as 'asc' | 'desc' | null) ?? null);
                }
              }}
              onFilterChanged={(event) => {
                if (!externalPagination) {
                  handleGridStateChanged(event);
                }
              }}
            />
          )}
          {!loading && !rows.length && emptyState ? (
            <Stack alignItems='center' justifyContent='center' sx={{ height: '100%', px: 3 }}>
              {emptyState}
            </Stack>
          ) : null}
        </Box>

        {externalPagination ? (
          <TablePagination
            component='div'
            count={externalPagination.total}
            page={externalPagination.page}
            onPageChange={(_, nextPage) => externalPagination.onPageChange(nextPage)}
            rowsPerPage={externalPagination.pageSize}
            onRowsPerPageChange={(event) => externalPagination.onPageSizeChange(Number(event.target.value))}
            rowsPerPageOptions={[10, 25, 50, 100]}
            labelRowsPerPage={rowsPerPageLabel}
          />
        ) : !hideToolbar && pagination ? null : null}
      </Paper>

      <GridColumnPanel
        open={Boolean(columnsAnchor)}
        anchorEl={columnsAnchor}
        title={columnsLabel}
        resetLabel={resetLabel}
        closeLabel={closeLabel}
        columns={columnsList}
        language={language}
        onClose={() => setColumnsAnchor(null)}
        onToggleVisibility={(colId, visible) => {
          gridApiRef.current?.setColumnsVisible([colId], visible);
          saveGridState();
        }}
        onPinChange={(colId, pinned) => {
          gridApiRef.current?.applyColumnState({ state: [{ colId, pinned }] });
          saveGridState();
        }}
        onReset={() => {
      setState(defaults);
          if (gridApiRef.current) {
            gridApiRef.current.resetColumnState();
            gridApiRef.current.setFilterModel(null);
          }
        }}
      />

      <Menu anchorEl={exportAnchor} open={Boolean(exportAnchor)} onClose={() => setExportAnchor(null)}>
        <MenuItem
          onClick={() => {
            gridApiRef.current?.exportDataAsCsv({ fileName: csvFileName ?? `${tableKey}.csv` });
            setExportAnchor(null);
          }}
        >
          CSV
        </MenuItem>
        {onExportXlsx ? (
          <MenuItem
            onClick={() => {
              onExportXlsx();
              setExportAnchor(null);
            }}
          >
            XLSX
          </MenuItem>
        ) : null}
      </Menu>
    </Stack>
  );
}
