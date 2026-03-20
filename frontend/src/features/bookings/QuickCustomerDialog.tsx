import { useEffect, useState } from 'react';

import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Stack, TextField } from '@mui/material';

import { useBookingsText } from '../../text/bookings';
import { useCommonText } from '../../text/common';
import type { CustomerPayload } from '../customers/api';

const emptyForm = { full_name: '', phone: '', email: '', address: '', notes: '' };

export function QuickCustomerDialog({
  open,
  onClose,
  onSubmit,
}: {
  open: boolean;
  onClose: () => void;
  onSubmit: (payload: CustomerPayload) => Promise<void>;
}) {
  const bookingsText = useBookingsText();
  const commonText = useCommonText();
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    if (open) {
      setForm(emptyForm);
    }
  }, [open]);

  async function handleSubmit() {
    await onSubmit({
      full_name: form.full_name,
      phone: form.phone,
      email: form.email || null,
      address: form.address || null,
      notes: form.notes || null,
    });
  }

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth='sm'>
      <DialogTitle>{bookingsText.quickCustomer.title}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ pt: 1 }}>
          <TextField label={bookingsText.quickCustomer.fullName} value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} />
          <TextField label={bookingsText.quickCustomer.phone} value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} />
          <TextField label={bookingsText.quickCustomer.email} value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} />
          <TextField label={bookingsText.quickCustomer.address} value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} />
          <TextField label={bookingsText.quickCustomer.notes} value={form.notes} multiline minRows={3} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{commonText.cancel}</Button>
        <Button variant='contained' onClick={() => void handleSubmit()}>
          {bookingsText.quickCustomer.save}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
