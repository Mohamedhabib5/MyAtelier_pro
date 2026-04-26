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
import { useBookingEditorColumns } from './useBookingEditorColumns';

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

  const lineColumns = useBookingEditorColumns({
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
  });

  const gridHeight = Math.min(720, Math.max(260, lines.length * 84 + 110));
  const hasInitialPayments = lines.some((line) => Number(line.initial_payment_amount || 0) > 0);

  return (
    <Stack spacing={2.5}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent='space-between' alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={2}>
        <Box>
          <Typography variant='h5' sx={{ fontWeight: 800, fontSize: { xs: '1.25rem', md: '1.5rem' } }}>
            {document ? `${bookingsText.editor.updateTitlePrefix} ${document.booking_number}` : bookingsText.editor.createTitle}
          </Typography>
          <Typography color='text.secondary' variant='body2'>{bookingsText.editor.subtitle}</Typography>
        </Box>
        <Stack direction='row' spacing={1} sx={{ alignSelf: { xs: 'stretch', sm: 'auto' } }}>
          <Button fullWidth onClick={onCancel} variant="soft" color="inherit">{commonText.cancel}</Button>
          <Button
            fullWidth
            variant='contained'
            disabled={saving || !customerId || !lines.length || (hasInitialPayments && !initialPaymentMethodId)}
            onClick={() => void handleSave()}
            sx={{ px: { sm: 4 } }}
          >
            {bookingsText.editor.save}
          </Button>
        </Stack>
      </Stack>

      {document ? (
        <Alert severity='info' sx={{ borderRadius: 4 }}>
          {`${bookingsText.editor.summaryPrefix}: ${bookingsText.editor.summaryLabels.status} ${bookingStatusLabel(language, document.status)} | ${bookingsText.editor.summaryLabels.total} ${document.total_amount} | ${bookingsText.editor.summaryLabels.paid} ${document.paid_total} | ${bookingsText.editor.summaryLabels.remaining} ${document.remaining_amount}`}
        </Alert>
      ) : null}

      {error ? <Alert severity='error' sx={{ borderRadius: 4 }}>{error}</Alert> : null}

      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', md: '1fr auto 1fr 1fr' }, 
        gap: 2, 
        alignItems: 'flex-start' 
      }}>
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
        <Button 
          variant='outlined' 
          startIcon={<PersonAddOutlinedIcon />} 
          onClick={() => setCustomerDialogOpen(true)}
          sx={{ height: 56, borderRadius: 3 }}
        >
          {bookingsText.editor.addCustomer}
        </Button>
        <TextField
          select
          fullWidth
          label={bookingsText.editor.initialPaymentMethod}
          value={initialPaymentMethodId}
          onChange={(event) => setInitialPaymentMethodId(event.target.value)}
        >
          {paymentMethods.map((method) => (
            <MenuItem key={method.id} value={method.id}>
              {method.name}
            </MenuItem>
          ))}
        </TextField>
        <TextField 
          fullWidth 
          label={bookingsText.editor.bookingDate} 
          type='date' 
          InputLabelProps={{ shrink: true }} 
          value={bookingDate} 
          onChange={(event) => setBookingDate(event.target.value)} 
        />
      </Box>

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
