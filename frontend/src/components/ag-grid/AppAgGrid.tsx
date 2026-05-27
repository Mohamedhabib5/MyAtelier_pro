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
  useMediaQuery,
  useTheme
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
import { MobileCardView } from './MobileCardView';

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
  onExport?: (format: 'csv' | 'xlsx', scope: 'all' | 'page') => void;
  getRowId?: (params: GetRowIdParams<Row>) => string;
  emptyState?: React.ReactNode;
  height?: number;
  onSortChange?: (sortBy: string | null, sortDir: 'asc' | 'desc' | null) => void;
  hideToolbar?: boolean;
  pagination?: boolean;
  getRowStyle?: (params: any) => any;
  getRowClass?: (params: any) => string | string[] | undefined;
  pinnedBottomRowData?: Row[];
  onRowClicked?: (params: any) => void;
  toolbarLeftContent?: React.ReactNode;
  disableMobileView?: boolean;
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
  onExport,
  getRowId,
  emptyState,
  height = 520,
  onSortChange,
  hideToolbar = false,
  pagination = true,
  getRowStyle,
  getRowClass,
  pinnedBottomRowData,
  onRowClicked,
  toolbarLeftContent,
  disableMobileView = false,
}: Props<Row>) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md')) && !disableMobileView;
  const [internalSearch, setInternalSearch] = useState('');
  const [columnsAnchor, setColumnsAnchor] = useState<HTMLElement | null>(null);
  const [exportAnchor, setExportAnchor] = useState<HTMLElement | null>(null);
  const [exportSubAnchor, setExportSubAnchor] = useState<HTMLElement | null>(null);
  const [exportFormat, setExportFormat] = useState<'csv' | 'xlsx' | null>(null);

  const gridApiRef = useRef<GridApi<Row> | null>(null);
  const { state, setState, defaults } = useAgGridPreferences(tableKey);
  const [localPage, setLocalPage] = useState(0);
  const [localPageSize, setLocalPageSize] = useState(state.pageSize ?? 25);
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
      pageSize: externalPagination?.pageSize ?? localPageSize,
    };
    setState(nextState);
  }, [externalPagination?.pageSize, localPageSize, setState]);

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

  const columnsList: Column[] = (gridApiRef.current && !gridApiRef.current.isDestroyed())
    ? (gridApiRef.current.getColumns() ?? [])
    : [];

  const effectivePageSize = externalPagination?.pageSize ?? localPageSize;
  const effectivePage = externalPagination?.page ?? localPage;
  const totalCount = externalPagination ? externalPagination.total : rows.length;

  const onPageChangeInternal = useCallback((newPage: number) => {
    if (externalPagination) {
      externalPagination.onPageChange(newPage);
    } else {
      setLocalPage(newPage);
      gridApiRef.current?.paginationGoToPage(newPage);
    }
  }, [externalPagination]);

  const onPageSizeChangeInternal = useCallback((newPageSize: number) => {
    if (externalPagination) {
      externalPagination.onPageSizeChange(newPageSize);
    } else {
      setLocalPageSize(newPageSize);
      setLocalPage(0);
      gridApiRef.current?.paginationGoToPage(0);
    }
  }, [externalPagination]);

  const visibleRowsCount = totalCount;

  const triggerLocalCsvExport = useCallback(() => {
    const api = gridApiRef.current;
    if (api) {
      const content = api.getDataAsCsv() ?? '';
      const filename = `${tableKey}.csv`;
      const blob = new Blob(['\uFEFF', content], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => {
        URL.revokeObjectURL(url);
        if (a.parentNode) {
            document.body.removeChild(a);
        }
      }, 1000);
    }
  }, [tableKey]);

  const handleExportClick = (format: 'csv' | 'xlsx', scope: 'all' | 'page') => {
    if (onExport) {
      onExport(format, scope);
    } else if (format === 'csv') {
      // Fallback to local grid export if no handler provided
      triggerLocalCsvExport();
    }
    setExportAnchor(null);
    setExportSubAnchor(null);
  };

  return (
    <Stack spacing={2}>
      {(title || subtitle) ? (
        <Box>
          {title ? <Typography variant='h6'>{title}</Typography> : null}
          {subtitle ? <Typography color='text.secondary'>{subtitle}</Typography> : null}
        </Box>
      ) : null}

      {error ? <Alert severity='error'>{error}</Alert> : null}

      <Paper variant='outlined' sx={{ overflow: 'hidden', borderRadius: 4, border: '1px solid rgba(0,0,0,0.05)' }}>
        {!hideToolbar ? (
        <Stack spacing={2} sx={{ p: { xs: 2, md: 3 }, background: 'rgba(0,0,0,0.02)' }}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent='space-between' alignItems={{ sm: 'center' }}>
            <Stack direction='row' spacing={2} alignItems='center' sx={{ flex: 1, minWidth: 0 }}>
              <Stack spacing={0.5} sx={{ minWidth: 'fit-content' }}>
                <Typography variant='subtitle1' fontWeight={800} sx={{ fontSize: { xs: '1rem', md: '1.1rem' }, whiteSpace: 'nowrap' }}>
                  {title ?? searchLabel}
                </Typography>
                <Typography variant='caption' color='text.secondary' sx={{ fontWeight: 600, opacity: 0.8 }}>
                  {visibleRowsCount} {language === 'ar' ? 'سجل' : 'records'}
                </Typography>
              </Stack>
              {toolbarLeftContent && (
                <Box sx={{ flex: 1, minWidth: 0, overflow: 'hidden' }}>
                  {toolbarLeftContent}
                </Box>
              )}
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
              sx={{ minWidth: { xs: '100%', sm: 300, md: 360 } }}
              InputProps={{
                sx: { borderRadius: 3, bgcolor: 'background.paper' },
                startAdornment: (
                  <InputAdornment position='start'>
                    <SearchOutlinedIcon fontSize='small' color='action' />
                  </InputAdornment>
                ),
              }}
            />
          </Stack>

          <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5} justifyContent='space-between' alignItems={{ md: 'center' }}>
            <Box sx={{ width: { xs: '100%', md: 'auto' } }}>{toolbarFilters}</Box>
            <Stack direction='row' spacing={1} sx={{ width: { xs: '100%', md: 'auto' }, flexWrap: 'nowrap', overflowX: 'auto', pb: { xs: 1, md: 0 } }}>
              {toolbarActions}
              <Button 
                variant='outlined' 
                onClick={(event) => setColumnsAnchor(event.currentTarget)}
                sx={{ 
                  whiteSpace: 'nowrap', 
                  borderRadius: 3,
                }}
              >
                {columnsLabel}
              </Button>
              <Button 
                variant='contained' 
                color='inherit' 
                onClick={(event) => setExportAnchor(event.currentTarget)}
                sx={{ 
                  whiteSpace: 'nowrap', 
                  borderRadius: 3,
                }}
                endIcon={<DownloadOutlinedIcon />}
              >
                {exportLabel}
              </Button>
            </Stack>
          </Stack>
        </Stack>
        ) : null}

        <Box className='ag-theme-quartz app-ag-grid' sx={{ height: isMobile ? 'auto' : height, width: '100%' }}>
          {loading ? (
            <Stack alignItems='center' justifyContent='center' sx={{ height: '100%', gap: 1.5 }}>
              <CircularProgress size={24} />
              <Typography color='text.secondary'>{language === 'ar' ? 'جار التحميل...' : 'Loading...'}</Typography>
            </Stack>
          ) : isMobile ? (
            <MobileCardView 
              rows={rows} 
              columns={columns} 
              onRowClicked={onRowClicked}
              getRowId={getRowId}
            />
          ) : (
            <AgGridReact<Row>
              theme='legacy'
              rowData={rows}
              columnDefs={columnDefs}
              localeText={localeText}
              quickFilterText={search}
              enableRtl={language === 'ar'}
              pagination={pagination}
              paginationPageSize={effectivePageSize}
              suppressPaginationPanel
              rowSelection={{ mode: 'multiRow', checkboxes: false, headerCheckbox: false }}
              animateRows
              suppressDragLeaveHidesColumns
              suppressCellFocus={false}
              getRowId={getRowId}
              overlayNoRowsTemplate={`<span>${noRowsLabel}</span>`}
              onGridReady={handleGridReady}
              onFirstDataRendered={handleFirstDataRendered}
              onGridPreDestroyed={() => {
                gridApiRef.current = null;
              }}
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
              getRowStyle={getRowStyle}
              getRowClass={getRowClass}
              pinnedBottomRowData={pinnedBottomRowData}
              onRowClicked={onRowClicked}
            />
          )}
          {!loading && !rows.length && emptyState ? (
            <Stack alignItems='center' justifyContent='center' sx={{ height: '100%', px: 3 }}>
              {emptyState}
            </Stack>
          ) : null}
        </Box>

        {pagination ? (
          <TablePagination
            component='div'
            count={totalCount}
            page={effectivePage}
            onPageChange={(_, nextPage) => onPageChangeInternal(nextPage)}
            rowsPerPage={effectivePageSize}
            onRowsPerPageChange={(event) => onPageSizeChangeInternal(Number(event.target.value))}
            rowsPerPageOptions={[10, 25, 50, 100]}
            labelRowsPerPage={rowsPerPageLabel}
          />
        ) : null}
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

      {/* Primary Export Menu: Select Format */}
      <Menu anchorEl={exportAnchor} open={Boolean(exportAnchor)} onClose={() => setExportAnchor(null)}>
        <MenuItem
          onClick={(e) => {
            setExportFormat('csv');
            setExportSubAnchor(e.currentTarget);
          }}
        >
          CSV
        </MenuItem>
        {onExport && (
          <MenuItem
            onClick={(e) => {
              setExportFormat('xlsx');
              setExportSubAnchor(e.currentTarget);
            }}
          >
            Excel (XLSX)
          </MenuItem>
        )}
      </Menu>

      {/* Secondary Export Menu: Select Scope */}
      <Menu 
        anchorEl={exportSubAnchor} 
        open={Boolean(exportSubAnchor)} 
        onClose={() => setExportSubAnchor(null)}
        anchorOrigin={{ vertical: 'top', horizontal: language === 'ar' ? 'left' : 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: language === 'ar' ? 'right' : 'left' }}
      >
        <MenuItem onClick={() => handleExportClick(exportFormat!, 'all')}>
          {language === 'ar' ? 'كل السجلات (المفلترة)' : 'All Records (Filtered)'}
        </MenuItem>
        <MenuItem onClick={() => handleExportClick(exportFormat!, 'page')}>
          {language === 'ar' ? 'الصفحة الحالية فقط' : 'Current Page Only'}
        </MenuItem>
      </Menu>
    </Stack>
  );
}
