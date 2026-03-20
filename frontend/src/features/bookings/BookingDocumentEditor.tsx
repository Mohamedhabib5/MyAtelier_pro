import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import PersonAddOutlinedIcon from '@mui/icons-material/PersonAddOutlined';
import { Alert, Box, Button, Chip, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material';
import { useEffect, useMemo, useState } from 'react';

import { useLanguage } from '../../features/language/LanguageProvider';
import { useBookingsText } from '../../text/bookings';
import { EMPTY_VALUE, bookingStatusLabel, useCommonText } from '../../text/common';
import type { DepartmentRecord, ServiceRecord } from '../catalog/api';
import type { CustomerPayload, CustomerRecord } from '../customers/api';
import type { DressRecord } from '../dresses/api';
import type { BookingDocumentPayload, BookingDocumentRecord, BookingLinePayload, BookingLineRecord } from './api';
import { departmentUsesDressCode } from './departmentRules';
import { QuickCustomerDialog } from './QuickCustomerDialog';

type EditableLine = {
  local_id: string;
  id?: string;
  department_id: string;
  service_id: string;
  dress_id: string;
  service_date: string;
  suggested_price: string;
  line_price: string;
  initial_payment_amount: string;
  status: string;
  notes: string;
  paid_total: number;
  remaining_amount: number;
  payment_state: string;
  is_locked: boolean;
  revenue_journal_entry_number: string | null;
};

function makeLocalId() {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;
}

function lineFromRecord(line: BookingLineRecord): EditableLine {
  return {
    local_id: makeLocalId(),
    id: line.id,
    department_id: line.department_id,
    service_id: line.service_id,
    dress_id: line.dress_id ?? '',
    service_date: line.service_date,
    suggested_price: String(line.suggested_price),
    line_price: String(line.line_price),
    initial_payment_amount: '',
    status: line.status,
    notes: line.notes ?? '',
    paid_total: line.paid_total,
    remaining_amount: line.remaining_amount,
    payment_state: line.payment_state,
    is_locked: line.is_locked,
    revenue_journal_entry_number: line.revenue_journal_entry_number,
  };
}

function buildEmptyLine(departments: DepartmentRecord[], services: ServiceRecord[]): EditableLine {
  const department = departments[0];
  const service = services.find((item) => item.department_id === department?.id) ?? services[0];
  const defaultPrice = Number(service?.default_price ?? 0);
  return {
    local_id: makeLocalId(),
    department_id: department?.id ?? '',
    service_id: service?.id ?? '',
    dress_id: '',
    service_date: '',
    suggested_price: String(defaultPrice),
    line_price: String(defaultPrice),
    initial_payment_amount: '',
    status: 'confirmed',
    notes: '',
    paid_total: 0,
    remaining_amount: defaultPrice,
    payment_state: 'unpaid',
    is_locked: false,
    revenue_journal_entry_number: null,
  };
}

export function BookingDocumentEditor({
  customers,
  departments,
  services,
  dresses,
  document,
  saving,
  onSave,
  onCancel,
  onCreateCustomer,
  onCompleteLine,
  onCancelLine,
}: {
  customers: CustomerRecord[];
  departments: DepartmentRecord[];
  services: ServiceRecord[];
  dresses: DressRecord[];
  document: BookingDocumentRecord | null;
  saving: boolean;
  onSave: (payload: BookingDocumentPayload) => Promise<void>;
  onCancel: () => void;
  onCreateCustomer: (payload: CustomerPayload) => Promise<CustomerRecord>;
  onCompleteLine: (lineId: string) => Promise<void>;
  onCancelLine: (lineId: string) => Promise<void>;
}) {
  const { language } = useLanguage();
  const bookingsText = useBookingsText();
  const commonText = useCommonText();
  const [customerDialogOpen, setCustomerDialogOpen] = useState(false);
  const [customerId, setCustomerId] = useState('');
  const [bookingDate, setBookingDate] = useState('');
  const [notes, setNotes] = useState('');
  const [lines, setLines] = useState<EditableLine[]>([]);

  useEffect(() => {
    if (document) {
      setCustomerId(document.customer_id);
      setBookingDate(document.booking_date);
      setNotes(document.notes ?? '');
      setLines(document.lines.map(lineFromRecord));
      return;
    }
    setCustomerId(customers[0]?.id ?? '');
    setBookingDate(new Date().toISOString().slice(0, 10));
    setNotes('');
    setLines([buildEmptyLine(departments, services)]);
  }, [customers, departments, document, services]);

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

  function handleDepartmentChange(localId: string, departmentId: string) {
    const service = services.find((item) => item.department_id === departmentId) ?? services[0];
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
    setCustomerId(created.id);
    setCustomerDialogOpen(false);
  }

  async function handleSave() {
    const payload: BookingDocumentPayload = {
      customer_id: customerId,
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
          <Button variant='contained' disabled={saving || !customerId || !lines.length} onClick={() => void handleSave()}>
            {bookingsText.editor.save}
          </Button>
        </Stack>
      </Stack>

      {document ? (
        <Alert severity='info'>
          {`${bookingsText.editor.summaryPrefix}: ${bookingsText.editor.summaryLabels.status} ${bookingStatusLabel(language, document.status)} | ${bookingsText.editor.summaryLabels.total} ${document.total_amount} | ${bookingsText.editor.summaryLabels.paid} ${document.paid_total} | ${bookingsText.editor.summaryLabels.remaining} ${document.remaining_amount}`}
        </Alert>
      ) : null}

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
        <TextField select SelectProps={{ native: true }} label={bookingsText.editor.customer} value={customerId} onChange={(event) => setCustomerId(event.target.value)} fullWidth>
          {customers.map((customer) => (
            <option key={customer.id} value={customer.id}>
              {customer.full_name}
            </option>
          ))}
        </TextField>
        <Button variant='outlined' startIcon={<PersonAddOutlinedIcon />} onClick={() => setCustomerDialogOpen(true)}>
          {bookingsText.editor.addCustomer}
        </Button>
        <TextField label={bookingsText.editor.bookingDate} type='date' InputLabelProps={{ shrink: true }} value={bookingDate} onChange={(event) => setBookingDate(event.target.value)} />
      </Stack>

      <TextField label={bookingsText.editor.notes} value={notes} multiline minRows={3} onChange={(event) => setNotes(event.target.value)} />

      <Stack direction='row' justifyContent='space-between' alignItems='center'>
        <Typography variant='h6'>{bookingsText.editor.linesTitle}</Typography>
        <Button variant='outlined' startIcon={<AddCircleOutlineIcon />} onClick={() => setLines((current) => [...current, buildEmptyLine(departments, services)])}>
          {bookingsText.editor.addLine}
        </Button>
      </Stack>

      <Table size='small'>
        <TableHead>
          <TableRow>
            <TableCell>#</TableCell>
            <TableCell>{bookingsText.lineTable.department}</TableCell>
            <TableCell>{bookingsText.lineTable.service}</TableCell>
            <TableCell>{bookingsText.lineTable.serviceDate}</TableCell>
            <TableCell>{bookingsText.lineTable.dress}</TableCell>
            <TableCell>{bookingsText.lineTable.suggestedPrice}</TableCell>
            <TableCell>{bookingsText.lineTable.linePrice}</TableCell>
            <TableCell>{bookingsText.lineTable.initialPayment}</TableCell>
            <TableCell>{bookingsText.lineTable.paid}</TableCell>
            <TableCell>{bookingsText.lineTable.remaining}</TableCell>
            <TableCell>{bookingsText.lineTable.status}</TableCell>
            <TableCell>{commonText.actions}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {lines.map((line, index) => {
            const lineId = line.id;
            const selectedDepartment = departments.find((item) => item.id === line.department_id);
            const departmentServices = services.filter((item) => item.department_id === line.department_id);
            const dressVisible = departmentUsesDressCode(selectedDepartment);
            const pendingRemaining = Number(line.line_price || 0) - line.paid_total - Number(line.initial_payment_amount || 0);

            return (
              <TableRow key={line.local_id}>
                <TableCell>{index + 1}</TableCell>
                <TableCell>
                  <TextField select SelectProps={{ native: true }} value={line.department_id} onChange={(event) => handleDepartmentChange(line.local_id, event.target.value)} disabled={line.is_locked}>
                    {departments.map((department) => (
                      <option key={department.id} value={department.id}>
                        {department.name}
                      </option>
                    ))}
                  </TextField>
                </TableCell>
                <TableCell>
                  <TextField select SelectProps={{ native: true }} value={line.service_id} onChange={(event) => handleServiceChange(line.local_id, event.target.value)} disabled={line.is_locked}>
                    {departmentServices.map((service) => (
                      <option key={service.id} value={service.id}>
                        {service.name}
                      </option>
                    ))}
                  </TextField>
                </TableCell>
                <TableCell>
                  <TextField type='date' value={line.service_date} onChange={(event) => updateLine(line.local_id, { service_date: event.target.value })} InputLabelProps={{ shrink: true }} disabled={line.is_locked} />
                </TableCell>
                <TableCell>
                  {dressVisible ? (
                    <TextField select SelectProps={{ native: true }} value={line.dress_id} onChange={(event) => updateLine(line.local_id, { dress_id: event.target.value })} disabled={line.is_locked}>
                      <option value=''>{bookingsText.editor.noDress}</option>
                      {dresses.map((dress) => (
                        <option key={dress.id} value={dress.id}>
                          {dress.code}
                        </option>
                      ))}
                    </TextField>
                  ) : (
                    EMPTY_VALUE
                  )}
                </TableCell>
                <TableCell>
                  <TextField type='number' value={line.suggested_price} onChange={(event) => updateLine(line.local_id, { suggested_price: event.target.value })} disabled={line.is_locked} />
                </TableCell>
                <TableCell>
                  <TextField type='number' value={line.line_price} onChange={(event) => updateLine(line.local_id, { line_price: event.target.value })} disabled={line.is_locked} />
                </TableCell>
                <TableCell>
                  <TextField type='number' value={line.initial_payment_amount} onChange={(event) => updateLine(line.local_id, { initial_payment_amount: event.target.value })} disabled={line.is_locked} />
                </TableCell>
                <TableCell>{line.paid_total}</TableCell>
                <TableCell>{pendingRemaining}</TableCell>
                <TableCell>
                  <Stack spacing={1}>
                    <TextField select SelectProps={{ native: true }} value={line.status} onChange={(event) => updateLine(line.local_id, { status: event.target.value })} disabled={line.is_locked}>
                      {lineStatusOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </TextField>
                    {line.revenue_journal_entry_number ? (
                      <Chip size='small' color='success' label={`${bookingsText.editor.revenueEntryPrefix} ${line.revenue_journal_entry_number}`} />
                    ) : null}
                  </Stack>
                </TableCell>
                <TableCell>
                  <Stack spacing={1}>
                    {lineId && line.status !== 'completed' && line.status !== 'cancelled' ? (
                      <Button size='small' color='success' startIcon={<CheckCircleOutlineIcon />} onClick={() => void onCompleteLine(lineId)}>
                        {bookingsText.editor.completeLine}
                      </Button>
                    ) : null}
                    {lineId && line.status !== 'cancelled' && !line.is_locked ? (
                      <Button size='small' onClick={() => void onCancelLine(lineId)}>
                        {bookingsText.editor.cancelLine}
                      </Button>
                    ) : null}
                    {!line.id && !line.is_locked ? (
                      <Button size='small' color='error' startIcon={<DeleteOutlineIcon />} onClick={() => setLines((current) => current.filter((item) => item.local_id !== line.local_id))}>
                        {bookingsText.editor.deleteLine}
                      </Button>
                    ) : null}
                  </Stack>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      <QuickCustomerDialog open={customerDialogOpen} onClose={() => setCustomerDialogOpen(false)} onSubmit={handleQuickCustomerSubmit} />
    </Stack>
  );
}
