import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import { Chip, Stack, TextField, Typography, Button } from '@mui/material';
import type { ICellRendererParams, SuppressKeyboardEventParams } from 'ag-grid-community';
import { useMemo } from 'react';

import { type AppAgGridColumn } from '../../components/ag-grid';
import { EMPTY_VALUE, bookingStatusLabel } from '../../text/common';
import type { DepartmentRecord, ServiceRecord } from '../catalog/api';
import type { DressRecord } from '../dresses/api';
import { departmentUsesDressCode } from './departmentRules';
import type { EditableLine } from './editorLineModel';
import { NumericCell } from './NumericCell';

interface UseBookingEditorColumnsProps {
  language: string;
  bookingsText: any;
  commonText: any;
  departments: DepartmentRecord[];
  services: ServiceRecord[];
  dresses: DressRecord[];
  lineStatusOptions: { value: string; label: string }[];
  updateLine: (localId: string, patch: Partial<EditableLine>) => void;
  handleDepartmentChange: (localId: string, departmentId: string) => void;
  handleServiceChange: (localId: string, serviceId: string) => void;
  onCompleteLine: (lineId: string) => Promise<void>;
  onCancelLine: (lineId: string) => Promise<void>;
  onReverseRevenueLine: (lineId: string) => Promise<void>;
  setLines: React.Dispatch<React.SetStateAction<EditableLine[]>>;
}

export function useBookingEditorColumns({
  language,
  bookingsText,
  commonText,
  departments,
  services,
  dresses,
  lineStatusOptions,
  updateLine,
  handleDepartmentChange,
  handleServiceChange,
  onCompleteLine,
  onCancelLine,
  onReverseRevenueLine,
  setLines,
}: UseBookingEditorColumnsProps) {
  function suppressGridKeyboardEvent(params: SuppressKeyboardEventParams<EditableLine>) {
    const target = params.event?.target;
    return target instanceof HTMLElement && Boolean(target.closest('input, textarea, select'));
  }

  return useMemo<AppAgGridColumn<EditableLine>[]>(
    () => [
      {
        colId: 'line_number',
        headerName: '#',
        width: 72,
        maxWidth: 84,
        sortable: false,
        filter: false,
        pinned: language === 'ar' ? 'right' : 'left',
        valueGetter: (params) => params.node?.rowIndex !== null ? params.node!.rowIndex! + 1 : '',
      },
      {
        colId: 'department_id',
        headerName: bookingsText.lineTable.department,
        minWidth: 170,
        cellRenderer: ({ data }: ICellRendererParams<EditableLine>) =>
          data ? (
            <TextField
              select
              SelectProps={{ native: true }}
              size='small'
              fullWidth
              value={data.department_id}
              onChange={(event) => handleDepartmentChange(data.local_id, event.target.value)}
              disabled={data.is_locked}
            >
              <option value=''>{bookingsText.editor.selectDepartment}</option>
              {departments.map((department) => (
                <option key={department.id} value={department.id}>
                  {department.name}
                </option>
              ))}
            </TextField>
          ) : null,
      },
      {
        colId: 'service_id',
        headerName: bookingsText.lineTable.service,
        minWidth: 180,
        cellRenderer: ({ data }: ICellRendererParams<EditableLine>) => {
          if (!data) return null;
          const departmentServices = services.filter((item) => item.department_id === data.department_id);
          return (
            <TextField
              select
              SelectProps={{ native: true }}
              size='small'
              fullWidth
              value={data.service_id}
              onChange={(event) => handleServiceChange(data.local_id, event.target.value)}
              disabled={data.is_locked}
            >
              <option value=''>{bookingsText.editor.selectService}</option>
              {departmentServices.map((service) => (
                <option key={service.id} value={service.id}>
                  {service.name}
                </option>
              ))}
            </TextField>
          );
        },
      },
      {
        colId: 'service_date',
        headerName: bookingsText.lineTable.serviceDate,
        minWidth: 155,
        cellRenderer: ({ data }: ICellRendererParams<EditableLine>) =>
          data ? (
            <TextField
              type='date'
              size='small'
              fullWidth
              value={data.service_date}
              onChange={(event) => updateLine(data.local_id, { service_date: event.target.value })}
              InputLabelProps={{ shrink: true }}
              disabled={data.is_locked}
            />
          ) : null,
      },
      {
        colId: 'dress_id',
        headerName: bookingsText.lineTable.dress,
        minWidth: 150,
        cellRenderer: ({ data }: ICellRendererParams<EditableLine>) => {
          if (!data) return null;
          const selectedDepartment = departments.find((item) => item.id === data.department_id);
          const dressVisible = departmentUsesDressCode(selectedDepartment);

          if (!dressVisible) {
            return <Typography color='text.secondary'>{EMPTY_VALUE}</Typography>;
          }

          return (
            <TextField
              select
              SelectProps={{ native: true }}
              size='small'
              fullWidth
              value={data.dress_id}
              onChange={(event) => updateLine(data.local_id, { dress_id: event.target.value })}
              disabled={data.is_locked}
            >
              <option value=''>{bookingsText.editor.noDress}</option>
              {dresses.map((dress) => (
                <option key={dress.id} value={dress.id}>
                  {dress.code}
                </option>
              ))}
            </TextField>
          );
        },
      },
      {
        colId: 'suggested_price',
        headerName: bookingsText.lineTable.suggestedPrice,
        minWidth: 135,
        cellRenderer: ({ data }: ICellRendererParams<EditableLine>) =>
          data ? (
            <TextField
              type='text'
              size='small'
              fullWidth
              value={data.suggested_price === '0' ? '' : data.suggested_price}
              placeholder='0'
              disabled={true}
              InputProps={{ readOnly: true }}
              sx={{ 
                bgcolor: '#f5f5f5',
                '& .MuiInputBase-input': {
                  textAlign: 'center',
                  fontWeight: 'bold',
                },
              }}
            />
          ) : null,
      },
      {
        colId: 'line_price',
        headerName: bookingsText.lineTable.linePrice,
        minWidth: 135,
        suppressKeyboardEvent: suppressGridKeyboardEvent,
        cellRenderer: ({ data }: ICellRendererParams<EditableLine>) =>
          data ? (
            <NumericCell 
              value={data.line_price} 
              onFlush={(val) => updateLine(data.local_id, { line_price: val })} 
              disabled={data.is_locked}
            />
          ) : null,
      },
      {
        colId: 'initial_payment_amount',
        headerName: bookingsText.lineTable.initialPayment,
        minWidth: 145,
        suppressKeyboardEvent: suppressGridKeyboardEvent,
        cellRenderer: ({ data }: ICellRendererParams<EditableLine>) =>
          data ? (
            <NumericCell 
              value={data.initial_payment_amount} 
              onFlush={(val) => updateLine(data.local_id, { initial_payment_amount: val })} 
              disabled={data.is_locked}
            />
          ) : null,
      },
      {
        colId: 'paid_total',
        headerName: bookingsText.lineTable.paid,
        minWidth: 110,
        valueGetter: (params) => params.data?.paid_total ?? 0,
      },
      {
        colId: 'remaining_preview',
        headerName: bookingsText.lineTable.remaining,
        minWidth: 120,
        valueGetter: (params) => {
          const line = params.data;
          if (!line) return 0;
          return Number(line.line_price || 0) - line.paid_total - Number(line.initial_payment_amount || 0);
        },
      },
      {
        colId: 'status',
        headerName: bookingsText.lineTable.status,
        minWidth: 180,
        autoHeight: true,
        cellRenderer: ({ data }: ICellRendererParams<EditableLine>) =>
          data ? (
            <Stack spacing={1} sx={{ py: 1 }}>
              <TextField
                select
                SelectProps={{ native: true }}
                size='small'
                fullWidth
                value={data.status}
                onChange={(event) => updateLine(data.local_id, { status: event.target.value })}
                disabled={data.is_locked}
              >
                {lineStatusOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </TextField>
              {data.revenue_journal_entry_number ? (
                <Chip size='small' color='success' label={`${bookingsText.editor.revenueEntryPrefix} ${data.revenue_journal_entry_number}`} />
              ) : null}
            </Stack>
          ) : null,
      },
      {
        colId: 'actions',
        headerName: commonText.actions,
        minWidth: 190,
        autoHeight: true,
        sortable: false,
        filter: false,
        pinned: language === 'ar' ? 'left' : 'right',
        cellRenderer: ({ data }: ICellRendererParams<EditableLine>) => {
          if (!data) return null;

          return (
            <Stack spacing={1} sx={{ py: 1 }}>
              {data.id && data.status !== 'completed' && data.status !== 'cancelled' ? (
                <Button size='small' color='success' startIcon={<CheckCircleOutlineIcon />} onClick={() => void onCompleteLine(data.id!)}>
                  {bookingsText.editor.completeLine}
                </Button>
              ) : null}
              {data.id && data.status !== 'cancelled' && !data.is_locked ? (
                <Button size='small' onClick={() => void onCancelLine(data.id!)}>
                  {bookingsText.editor.cancelLine}
                </Button>
              ) : null}
              {data.id && data.status === 'completed' && data.is_locked ? (
                <Button size='small' color='warning' onClick={() => void onReverseRevenueLine(data.id!)}>
                  {language === 'ar' ? 'عكس الإيراد' : 'Reverse revenue'}
                </Button>
              ) : null}
              {!data.id && !data.is_locked ? (
                <Button
                  size='small'
                  color='error'
                  startIcon={<DeleteOutlineIcon />}
                  onClick={() => setLines((current) => current.filter((item) => item.local_id !== data.local_id))}
                >
                  {bookingsText.editor.deleteLine}
                </Button>
              ) : null}
            </Stack>
          );
        },
      },
    ],
    [bookingsText, commonText.actions, departments, dresses, language, lineStatusOptions, onCancelLine, onCompleteLine, onReverseRevenueLine, services, updateLine, handleDepartmentChange, handleServiceChange, setLines],
  );
}
