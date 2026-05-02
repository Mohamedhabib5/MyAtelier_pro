import { Box, Button, Dialog, DialogActions, DialogContent, DialogTitle, FormControl, InputLabel, MenuItem, Select, Stack, TextField, Typography, Alert } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState, useMemo } from 'react';
import { createCompensationBooking } from './api';
import { listDepartments, listServices } from '../catalog/api';
import { useCommonText } from '../../text/common';

type Props = {
  open: boolean;
  bookingId: string;
  bookingNumber: string;
  language: 'ar' | 'en';
  onClose: () => void;
  onSuccess: (newBookingNumber: string) => void;
};

export function CompensationDialog({ open, bookingId, bookingNumber, language, onClose, onSuccess }: Props) {
  const commonText = useCommonText();
  const [departmentId, setDepartmentId] = useState('');
  const [serviceId, setServiceId] = useState('');
  const [amount, setAmount] = useState<number>(0);
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);

  const departmentsQuery = useQuery({ queryKey: ['departments', 'active'], queryFn: listDepartments });
  const servicesQuery = useQuery({ queryKey: ['services', 'active'], queryFn: listServices });

  const filteredServices = useMemo(() => {
    if (!departmentId) return [];
    return (servicesQuery.data ?? []).filter(s => s.department_id === departmentId);
  }, [servicesQuery.data, departmentId]);

  const compensateMutation = useMutation({
    mutationFn: (payload: any) => createCompensationBooking(bookingId, payload),
    onSuccess: (data) => {
      onSuccess(data.booking_number);
      handleClose();
    },
    onError: (err: Error) => setError(err.message),
  });

  const handleClose = () => {
    setDepartmentId('');
    setServiceId('');
    setAmount(0);
    setNotes('');
    setError(null);
    onClose();
  };

  const handleConfirm = () => {
    if (!departmentId || !serviceId || amount <= 0) {
      setError(language === 'ar' ? 'يرجى إكمال البيانات' : 'Please complete all fields');
      return;
    }
    compensateMutation.mutate({
      department_id: departmentId,
      service_id: serviceId,
      amount,
      notes
    });
  };

  const t = {
    title: language === 'ar' ? `إضافة سند تعويض للحجز ${bookingNumber}` : `Add Compensation for ${bookingNumber}`,
    dept: language === 'ar' ? 'القسم' : 'Department',
    service: language === 'ar' ? 'نوع التعويض / الخدمة' : 'Compensation Type / Service',
    amount: language === 'ar' ? 'المبلغ' : 'Amount',
    notes: language === 'ar' ? 'ملاحظات' : 'Notes',
    confirm: language === 'ar' ? 'إصدار السند' : 'Issue Compensation',
    cancel: commonText.cancel,
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>{t.title}</DialogTitle>
      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          {error && <Alert severity="error">{error}</Alert>}
          
          <FormControl fullWidth>
            <InputLabel>{t.dept}</InputLabel>
            <Select
              value={departmentId}
              label={t.dept}
              onChange={(e) => {
                setDepartmentId(e.target.value);
                setServiceId('');
              }}
            >
              {(departmentsQuery.data ?? []).map(d => (
                <MenuItem key={d.id} value={d.id}>{d.name}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth disabled={!departmentId}>
            <InputLabel>{t.service}</InputLabel>
            <Select
              value={serviceId}
              label={t.service}
              onChange={(e) => {
                setServiceId(e.target.value);
                const s = filteredServices.find(x => x.id === e.target.value);
                if (s) setAmount(s.price);
              }}
            >
              {filteredServices.map(s => (
                <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label={t.amount}
            type="number"
            value={amount}
            onChange={(e) => setAmount(Number(e.target.value))}
            fullWidth
          />

          <TextField
            label={t.notes}
            multiline
            rows={3}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            fullWidth
            placeholder={language === 'ar' ? 'تلف فستان، ضياع قطعة، إلخ...' : 'Damage, loss, delay...'}
          />
        </Stack>
      </DialogContent>
      <DialogActions sx={{ p: 2, pt: 0 }}>
        <Button onClick={handleClose}>{t.cancel}</Button>
        <Button 
          variant="contained" 
          onClick={handleConfirm} 
          disabled={compensateMutation.isPending}
        >
          {compensateMutation.isPending ? '...' : t.confirm}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
