import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import PersonAddOutlinedIcon from '@mui/icons-material/PersonAddOutlined';
import { Alert, Autocomplete, Box, Button, Chip, MenuItem, Stack, TextField, Typography } from '@mui/material';
import type { ICellRendererParams, SuppressKeyboardEventParams } from 'ag-grid-community';
import { useEffect, useMemo, useState } from 'react';

import { AppAgGrid, type AppAgGridColumn } from '../../components/ag-grid';
import { useLanguage } from '../../features/language/LanguageProvider';
import { useBookingsText } from '../../text/bookings';
import { EMPTY_VALUE, bookingStatusLabel, useCommonText } from '../../text/common';
import type { DepartmentRecord, ServiceRecord } from '../catalog/api';
import type { CustomerPayload, CustomerRecord } from '../customers/api';
import type { DressRecord } from '../dresses/api';
import type { PaymentMethodRecord } from '../paymentMethods/api';
import type { BookingDocumentPayload, BookingDocumentRecord, BookingLinePayload } from './api';
import { departmentUsesDressCode } from './departmentRules';
import { buildEmptyLine, lineFromRecord, type EditableLine } from './editorLineModel';
import { NumericCell } from './NumericCell';
import { QuickCustomerDialog } from './QuickCustomerDialog';

export function BookingDocumentEditor({
  customers,
  departments,
  services,
  dresses,
  paymentMethods,
  document,
  error,
  saving,
  onSave,
  onCancel,
  onCreateCustomer,
  onCompleteLine,
  onCancelLine,
  onReverseRevenueLine,
}: {
  customers: CustomerRecord[];
  departments: DepartmentRecord[];
  services: ServiceRecord[];
  dresses: DressRecord[];
  paymentMethods: PaymentMethodRecord[];
  document: BookingDocumentRecord | null;
  error: string | null;
  saving: boolean;
  onSave: (payload: BookingDocumentPayload) => Promise<void>;
  onCancel: () => void;
  onCreateCustomer: (payload: CustomerPayload) => Promise<CustomerRecord>;
  onCompleteLine: (lineId: string) => Promise<void>;
  onCancelLine: (lineId: string) => Promise<void>;
  onReverseRevenueLine: (lineId: string) => Promise<void>;
}) {
  const { language } = useLanguage();
  const bookingsText = useBookingsText();
  const commonText = useCommonText();
  const [customerDialogOpen, setCustomerDialogOpen] = useState(false);
  const [customerId, setCustomerId] = useState('');
  const [initialPaymentMethodId, setInitialPaymentMethodId] = useState('');
  const [bookingDate, setBookingDate] = useState('');
  const [notes, setNotes] = useState('');
  const [lines, setLines] = useState<EditableLine[]>([]);

  const documentId = document?.id;

  useEffect(() => {
    // PROTECTED: This effect must only run when the document ID changes.
    // Do NOT add 'customers', 'departments', 'services', or 'paymentMethods' to dependencies.
    // Adding them will cause state resets during background refetches, breaking the "auto-select new customer" feature.
    if (document) {
      setCustomerId(document.customer_id);
      setInitialPaymentMethodId(paymentMethods[0]?.id ?? '');
      setBookingDate(document.booking_date);
      setNotes(document.notes ?? '');
      setLines(document.lines.map(lineFromRecord));
      return;
    }

    setCustomerId('');
    setInitialPaymentMethodId(paymentMethods[0]?.id ?? '');
    setBookingDate(new Date().toISOString().slice(0, 10));
    setNotes('');
    setLines([buildEmptyLine(departments, services, new Date().toISOString().slice(0, 10))]);
  }, [documentId]); // Only depend on documentId to trigger a full reset

  const lineStatusOptions = useMemo(
    () => [
      { value: 'draft', label: bookingStatusLabel(language, 'draft') },
      { value: 'confirmed', label: bookingStatusLabel(language, 'confirmed') },
      { value: 'cancelled', label: bookingStatusLabel(language, 'cancelled') },
    ],
    [language],
  );

  function updateLine(localId: string, patch: Partial<EditableLine>) {
    setLines((current) => current.map((line) => (line.local_id === localId ? { ...line, ...patch } : line)));
  }

  function suppressGridKeyboardEvent(params: SuppressKeyboardEventParams<EditableLine>) {
    const target = params.event?.target;
    return target instanceof HTMLElement && Boolean(target.closest('input, textarea, select'));
  }

  function handleDepartmentChange(localId: string, departmentId: string) {
    if (!departmentId) {
      updateLine(localId, {
        department_id: '',
        service_id: '',
        dress_id: '',
        suggested_price: '0',
        line_price: '0',
      });
      return;
    }
    const departmentServices = services.filter((item) => item.department_id === departmentId);
    const service = departmentServices[0];
    updateLine(localId, {
      department_id: departmentId,
      service_id: service?.id ?? '',
      dress_id: '',
      suggested_price: String(service?.default_price ?? 0),
      line_price: String(service?.default_price ?? 0),
    });
  }

  function handleServiceChange(localId: string, serviceId: string) {
    const service = services.find((item) => item.id === serviceId);
    if (!service) return;

    updateLine(localId, {
      department_id: service.department_id,
      service_id: service.id,
      suggested_price: String(service.default_price),
      line_price: String(service.default_price),
      dress_id: '',
    });
  }

  async function handleQuickCustomerSubmit(payload: CustomerPayload) {
    const created = await onCreateCustomer(payload);
    // PROTECTED: Auto-select newly created customer
    setCustomerId(created.id);
    setCustomerDialogOpen(false);
  }

  async function handleSave() {
    const payload: BookingDocumentPayload = {
      customer_id: customerId,
      initial_payment_method_id: initialPaymentMethodId || null,
      booking_date: bookingDate,
      notes: notes || null,
      lines: lines.map(
        (line): BookingLinePayload => ({
          id: line.id,
          department_id: line.department_id,
          service_id: line.service_id,
          service_date: line.service_date,
          dress_id: line.dress_id || null,
          suggested_price: Number(line.suggested_price || 0),
          line_price: Number(line.line_price || 0),
          initial_payment_amount: line.initial_payment_amount ? Number(line.initial_payment_amount) : null,
          status: line.status,
          notes: line.notes || null,
        }),
      ),
    };

    await onSave(payload);
  }

  const lineColumns = useMemo<AppAgGridColumn<EditableLine>[]>(
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
    [bookingsText, commonText.actions, departments, dresses, language, lineStatusOptions, onCancelLine, onCompleteLine, onReverseRevenueLine, services],
  );

  const gridHeight = Math.min(720, Math.max(260, lines.length * 84 + 110));
  const hasInitialPayments = lines.some((line) => Number(line.initial_payment_amount || 0) > 0);

  return (
    <Stack spacing={2}>
      <Stack direction='row' justifyContent='space-between' alignItems='center'>
        <Box>
          <Typography variant='h5'>
            {document ? `${bookingsText.editor.updateTitlePrefix} ${document.booking_number}` : bookingsText.editor.createTitle}
          </Typography>
          <Typography color='text.secondary'>{bookingsText.editor.subtitle}</Typography>
        </Box>
        <Stack direction='row' spacing={1}>
          <Button onClick={onCancel}>{commonText.cancel}</Button>
          <Button
            variant='contained'
            disabled={saving || !customerId || !lines.length || (hasInitialPayments && !initialPaymentMethodId)}
            onClick={() => void handleSave()}
          >
            {bookingsText.editor.save}
          </Button>
        </Stack>
      </Stack>

      {document ? (
        <Alert severity='info'>
          {`${bookingsText.editor.summaryPrefix}: ${bookingsText.editor.summaryLabels.status} ${bookingStatusLabel(language, document.status)} | ${bookingsText.editor.summaryLabels.total} ${document.total_amount} | ${bookingsText.editor.summaryLabels.paid} ${document.paid_total} | ${bookingsText.editor.summaryLabels.remaining} ${document.remaining_amount}`}
        </Alert>
      ) : null}

      {error ? <Alert severity='error'>{error}</Alert> : null}

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
        <Autocomplete
          fullWidth
          options={customers}
          getOptionLabel={(option) => option.full_name}
          value={customers.find((c) => c.id === customerId) || null}
          onChange={(_, newValue) => setCustomerId(newValue?.id ?? '')}
          renderInput={(params) => (
            <TextField {...params} label={bookingsText.editor.customer} placeholder={bookingsText.editor.selectCustomer} />
          )}
          noOptionsText={language === 'ar' ? 'لا توجد نتائج' : 'No results'}
        />
        <Button variant='outlined' startIcon={<PersonAddOutlinedIcon />} onClick={() => setCustomerDialogOpen(true)}>
          {bookingsText.editor.addCustomer}
        </Button>
        <TextField
          select
          label={bookingsText.editor.initialPaymentMethod}
          value={initialPaymentMethodId}
          onChange={(event) => setInitialPaymentMethodId(event.target.value)}
          sx={{ minWidth: 220 }}
        >
          {paymentMethods.map((method) => (
            <MenuItem key={method.id} value={method.id}>
              {method.name}
            </MenuItem>
          ))}
        </TextField>
        <TextField label={bookingsText.editor.bookingDate} type='date' InputLabelProps={{ shrink: true }} value={bookingDate} onChange={(event) => setBookingDate(event.target.value)} />
      </Stack>

      <TextField label={bookingsText.editor.notes} value={notes} multiline minRows={3} onChange={(event) => setNotes(event.target.value)} />

      <Stack direction='row' justifyContent='space-between' alignItems='center'>
        <Typography variant='h6'>{bookingsText.editor.linesTitle}</Typography>
        <Button variant='outlined' startIcon={<AddCircleOutlineIcon />} onClick={() => setLines((current) => [...current, buildEmptyLine(departments, services, bookingDate)])}>
          {bookingsText.editor.addLine}
        </Button>
      </Stack>

      <AppAgGrid
        tableKey='booking-document-editor-lines'
        rows={lines}
        columns={lineColumns}
        language={language}
        searchLabel={bookingsText.editor.linesTitle}
        searchPlaceholder={bookingsText.editor.linesTitle}
        columnsLabel={commonText.actions}
        exportLabel='Export'
        resetLabel='Reset'
        closeLabel='Close'
        noRowsLabel={language === 'ar' ? 'لا توجد سطور بعد' : 'No lines yet'}
        rowsPerPageLabel={language === 'ar' ? 'عدد الصفوف' : 'Rows per page'}
        getRowId={(params) => params.data.local_id}
        hideToolbar
        pagination={false}
        height={gridHeight}
      />

      <QuickCustomerDialog open={customerDialogOpen} onClose={() => setCustomerDialogOpen(false)} onSubmit={handleQuickCustomerSubmit} />
    </Stack>
  );
}
