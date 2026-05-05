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
import { BookingCancellationDialog } from './BookingCancellationDialog';
import { bulkCancelBookings, type BookingCancellationPayload } from './api';

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
  onDeleteLine,
  onUndoCancellation,
  onCancelFull,
  mode = 'edit',
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
  onDeleteLine: (lineId: string) => Promise<void>;
  onUndoCancellation: (lineIds: string[]) => Promise<void>;
  onCancelFull?: () => void;
  mode?: 'edit' | 'cancel';
}) {
  const { language } = useLanguage();
  const bookingsText = useBookingsText();
  const commonText = useCommonText();
  const [customerDialogOpen, setCustomerDialogOpen] = useState(false);
  const [customerId, setCustomerId] = useState('');
  const [initialPaymentMethodId, setInitialPaymentMethodId] = useState('');
  const [bookingDate, setBookingDate] = useState('');
  const [notes, setNotes] = useState('');
  const [externalCode, setExternalCode] = useState('');
  const [cancellationDate, setCancellationDate] = useState(new Date().toISOString().slice(0, 10));
  const [lines, setLines] = useState<EditableLine[]>([]);
  const [pendingCancellations, setPendingCancellations] = useState<Record<string, BookingCancellationPayload>>({});
  const [showCancelDialogFor, setShowCancelDialogFor] = useState<{ id: string; isFull?: boolean } | null>(null);

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
      setExternalCode(document.external_code ?? '');
      setLines(document.lines.map(lineFromRecord));
      return;
    }

    setCustomerId('');
    setInitialPaymentMethodId(paymentMethods[0]?.id ?? '');
    setBookingDate(new Date().toISOString().slice(0, 10));
    setNotes('');
    setExternalCode('');
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
    if (mode === 'cancel' && document) {
      const requests = Object.values(pendingCancellations);
      if (requests.length === 0) return;
      await bulkCancelBookings(document.id, requests);
      onCancel(); // Close editor on success
      return;
    }

    const payload: BookingDocumentPayload = {
      customer_id: customerId,
      initial_payment_method_id: initialPaymentMethodId || null,
      booking_date: bookingDate,
      notes: notes || null,
      external_code: externalCode || null,
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

  function handleMarkLineForCancellation(lineId: string) {
    setShowCancelDialogFor({ id: lineId, isFull: false });
  }

  function handleUnmarkLineForCancellation(lineId: string) {
    setPendingCancellations(curr => {
      const copy = { ...curr };
      delete copy[lineId];
      delete copy['__full__']; 
      return copy;
    });
  }

  function handleMarkFullForCancellation() {
    setShowCancelDialogFor({ id: document?.id || '', isFull: true });
  }

  async function handleConfirmPendingCancellation(payload: BookingCancellationPayload) {
    if (!showCancelDialogFor) return;

    if (showCancelDialogFor.isFull) {
      // Clear existing individual ones and set one "Full" marker
      setPendingCancellations({
        '__full__': { ...payload, line_ids: null } 
      });
    } else {
      setPendingCancellations(curr => {
        const copy = { ...curr };
        delete copy['__full__']; // Remove full marker if individual line is being handled
        copy[showCancelDialogFor.id] = { ...payload, line_ids: [showCancelDialogFor.id] };
        return copy;
      });
    }
    setShowCancelDialogFor(null);
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
    onCancelLine: handleMarkLineForCancellation, // Intercept to mark as pending
    onReverseRevenueLine,
    onDeleteLine,
    onUndoCancellation,
    onUnmarkPendingCancellation: handleUnmarkLineForCancellation,
    setLines,
    mode,
    pendingCancellations,
  });

  const gridHeight = Math.min(720, Math.max(260, lines.length * 84 + 110));
  const hasInitialPayments = lines.some((line) => Number(line.initial_payment_amount || 0) > 0);

  return (
    <Stack spacing={2.5}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent='space-between' alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={2}>
        <Box>
          <Typography variant='h5' sx={{ fontWeight: 800, fontSize: { xs: '1.25rem', md: '1.5rem' } }}>
            {document 
              ? (mode === 'cancel' ? `${bookingsText.editor.cancelTitlePrefix} ${document.booking_number}` : `${bookingsText.editor.updateTitlePrefix} ${document.booking_number}`)
              : bookingsText.editor.createTitle}
          </Typography>
          <Typography color='text.secondary' variant='body2'>{bookingsText.editor.subtitle}</Typography>
        </Box>
        <Stack direction='row' spacing={1} sx={{ alignSelf: { xs: 'stretch', sm: 'auto' } }}>
          <Button fullWidth onClick={onCancel} variant="outlined" color="inherit">{commonText.cancel}</Button>
          <Button
            fullWidth
            variant='contained'
            color={mode === 'cancel' ? 'warning' : 'primary'}
            disabled={saving || (mode === 'edit' && (!customerId || !lines.length)) || (mode === 'cancel' && Object.keys(pendingCancellations).length === 0) || (hasInitialPayments && !initialPaymentMethodId)}
            onClick={() => void handleSave()}
            sx={{ px: { sm: 4 }, fontWeight: 800 }}
          >
            {mode === 'cancel' ? bookingsText.editor.confirmCancellation : bookingsText.editor.save}
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
        <Stack spacing={1}>
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
            disabled={mode === 'cancel'}
          />
          {customerId && customers.find(c => c.id === customerId) && (
            <Stack 
              direction="row" 
              spacing={2} 
              alignItems="center" 
              sx={{ 
                px: 2, 
                py: 0.75, 
                bgcolor: 'rgba(25, 118, 210, 0.05)', 
                borderRadius: 2,
                border: '1px dashed rgba(25, 118, 210, 0.2)'
              }}
            >
              <Stack direction="row" spacing={0.5} alignItems="center">
                <Typography variant="caption" color="primary.main" fontWeight="bold">
                  {language === 'ar' ? '📍 العنوان:' : '📍 Address:'}
                </Typography>
                <Typography variant="caption" color="text.primary" fontWeight={500}>
                  {customers.find(c => c.id === customerId)?.address || EMPTY_VALUE}
                </Typography>
              </Stack>
              <Box sx={{ height: 12, width: 1, bgcolor: 'divider' }} />
              <Stack direction="row" spacing={0.5} alignItems="center">
                <Typography variant="caption" color="primary.main" fontWeight="bold">
                  {language === 'ar' ? '📞 الهاتف:' : '📞 Phone:'}
                </Typography>
                <Typography variant="caption" color="text.primary" fontWeight={500}>
                  {customers.find(c => c.id === customerId)?.phone || EMPTY_VALUE}
                </Typography>
              </Stack>
            </Stack>
          )}
        </Stack>
        {mode === 'edit' && (
          <Button 
            variant='outlined' 
            startIcon={<PersonAddOutlinedIcon />} 
            onClick={() => setCustomerDialogOpen(true)}
            sx={{ height: 56, borderRadius: 3, minWidth: 140 }}
          >
            {bookingsText.editor.addCustomer}
          </Button>
        )}
        <TextField
          select
          fullWidth
          label={bookingsText.editor.initialPaymentMethod}
          value={initialPaymentMethodId}
          onChange={(event) => setInitialPaymentMethodId(event.target.value)}
          disabled={mode === 'cancel'}
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
          disabled={mode === 'cancel'}
        />
        <TextField 
          fullWidth 
          label={bookingsText.editor.externalCode} 
          value={externalCode} 
          onChange={(event) => setExternalCode(event.target.value)} 
          disabled={mode === 'cancel'}
        />
        {mode === 'cancel' && (
          <TextField 
            fullWidth 
            label={language === 'ar' ? 'تاريخ الإلغاء' : 'Cancellation Date'} 
            type='date' 
            InputLabelProps={{ shrink: true }} 
            value={cancellationDate} 
            onChange={(event) => setCancellationDate(event.target.value)} 
            sx={{ 
              '& .MuiInputBase-root': { bgcolor: 'rgba(211, 47, 47, 0.05)', fontWeight: 'bold' } 
            }}
          />
        )}
        {mode === 'cancel' && document && document.status !== 'cancelled' && (
          <Button
            variant="contained"
            color="error"
            onClick={handleMarkFullForCancellation}
            sx={{ height: 56, borderRadius: 3, fontWeight: 800 }}
          >
            {bookingsText.editor.cancelFullDocument}
          </Button>
        )}
      </Box>

      <TextField 
        label={bookingsText.editor.notes} 
        value={notes} 
        multiline 
        minRows={3} 
        onChange={(event) => setNotes(event.target.value)} 
        disabled={mode === 'cancel'}
      />

      <Stack direction='row' justifyContent='space-between' alignItems='center'>
        <Typography variant='h6'>{bookingsText.editor.linesTitle}</Typography>
        {mode === 'edit' && (
          <Button variant='outlined' startIcon={<AddCircleOutlineIcon />} onClick={() => setLines((current) => [...current, buildEmptyLine(departments, services, bookingDate)])}>
            {bookingsText.editor.addLine}
          </Button>
        )}
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
        getRowStyle={(params) => {
          const isFullPending = Boolean(pendingCancellations['__full__']);
          const isLinePending = params.data?.id && Boolean(pendingCancellations[params.data.id]);
          if (isFullPending || isLinePending) {
            return { backgroundColor: 'rgba(211, 47, 47, 0.08)' };
          }
          return undefined;
        }}
        hideToolbar
        pagination={false}
        height={gridHeight}
      />

      <QuickCustomerDialog open={customerDialogOpen} onClose={() => setCustomerDialogOpen(false)} onSubmit={handleQuickCustomerSubmit} />

      {showCancelDialogFor && document && (
        <BookingCancellationDialog
          open={true}
          onClose={() => setShowCancelDialogFor(null)}
          onConfirm={handleConfirmPendingCancellation}
          booking={document}
          paymentMethods={paymentMethods}
          lineId={showCancelDialogFor.isFull ? undefined : showCancelDialogFor.id}
          saving={false}
          initialDate={cancellationDate}
        />
      )}
    </Stack>
  );
}
