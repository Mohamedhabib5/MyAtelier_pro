import {
  Alert,
  Box,
  Button,
  MenuItem,
  Stack,
  TextField,
  Typography,
  Paper,
  Grid,
  useTheme,
  alpha,
} from '@mui/material';
import CancelScheduleSendOutlinedIcon from '@mui/icons-material/CancelScheduleSendOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import { useState, useEffect } from 'react';

import { AppDialogShell } from '../../components/AppDialogShell';
import { useLanguageFormatters } from '../../text/common';
import { useBookingsText } from '../../text/bookings';
import type { BookingSummaryRecord, BookingCancellationPayload, BookingDocumentRecord } from './api';
import type { PaymentMethodRecord } from '../paymentMethods/api';
import { AppDateField } from '../../components/inputs/AppDateField';
import { getLocalDateStr } from '../../lib/dates';

type Props = {
  open: boolean;
  booking: BookingSummaryRecord | null;
  detailedDocument?: BookingDocumentRecord;
  paymentMethods: PaymentMethodRecord[];
  saving: boolean;
  onClose: () => void;
  onConfirm: (payload: BookingCancellationPayload) => Promise<void>;
  lineId?: string;
  isSaving?: boolean;
  initialDate?: string;
};

export function BookingCancellationDialog({ open, booking, detailedDocument, paymentMethods, saving, onClose, onConfirm, lineId, initialDate }: Props) {
  const bookingsText = useBookingsText();
  const { formatCurrency } = useLanguageFormatters();
  const theme = useTheme();
  
  const [reason, setReason] = useState('');
  const [refundAmount, setRefundAmount] = useState<string>('0');
  const [transferAmount, setTransferAmount] = useState<string>('0');
  const [paymentMethodId, setPaymentMethodId] = useState('');
  const [transferToLineId, setTransferToLineId] = useState('');
  const [cancelDate, setCancelDate] = useState(getLocalDateStr());
  const [localError, setLocalError] = useState<string | null>(null);

  const isLineCancellation = !!lineId;
  const lineContext = detailedDocument?.lines.find(l => l.id === lineId);
  const maxRefundable = lineContext?.paid_total ?? booking?.paid_total ?? 0;

  const otherActiveLines = (detailedDocument?.lines ?? []).filter(l => 
    l.id !== lineId && l.status !== 'cancelled'
  );

  useEffect(() => {
    if (open) {
      setReason('');
      setRefundAmount('0');
      setTransferAmount('0');
      setPaymentMethodId(paymentMethods.find(m => m.is_active)?.id || '');
      setTransferToLineId('');
      setCancelDate(initialDate || getLocalDateStr());
      setLocalError(null);
    }
  }, [open, paymentMethods, initialDate]);

  if (!booking) return null;
  
  async function handleConfirm() {
    if (!reason.trim()) {
      setLocalError('يرجى إدخال سبب الإلغاء');
      return;
    }
    const refundVal = Number(refundAmount) || 0;
    const transferVal = Number(transferAmount) || 0;
    
    if (refundVal + transferVal > maxRefundable) {
      setLocalError(`مجموع الرد والتحويل لا يمكن أن يتجاوز ${formatCurrency(maxRefundable)}`);
      return;
    }
    if (refundVal > 0 && !paymentMethodId) {
      setLocalError('يرجى اختيار طريقة الدفع للرد');
      return;
    }

    const payload: BookingCancellationPayload = {
      reason,
      cancellation_date: cancelDate,
      refund_amount: refundVal,
      transfer_amount: transferVal,
      payment_method_id: refundVal > 0 ? paymentMethodId : null,
      line_ids: lineId ? [lineId] : null,
      transfer_to_line_id: transferToLineId || null
    };

    try {
      await onConfirm(payload);
    } catch (err: unknown) {
      setLocalError((err as any).message || 'حدث خطأ أثناء الإلغاء');
    }
  }

  return (
    <AppDialogShell
      open={open}
      onClose={onClose}
      title={isLineCancellation ? 'إلغاء سطر خدمة' : 'إلغاء الحجز بالكامل'}
      subtitle={`${booking.booking_number} • ${booking.customer_name}`}
      maxWidth='sm'
    >
      <Stack spacing={3}>
        {localError && <Alert severity='error' variant="filled" sx={{ borderRadius: 2 }}>{localError}</Alert>}

        {/* Selection Summary */}
        <Paper variant="outlined" sx={{ 
          p: 2.5, 
          borderRadius: 3, 
          bgcolor: alpha(theme.palette.info.main, 0.04),
          borderColor: alpha(theme.palette.info.main, 0.2),
          borderStyle: 'dashed'
        }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <ReceiptLongOutlinedIcon color="info" />
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                {isLineCancellation ? 'نطاق الإلغاء: سطر محدد' : 'نطاق الإلغاء: الحجز بالكامل'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {isLineCancellation ? lineContext?.service_name : 'سيتم إلغاء كافة الخدمات المرتبطة بهذا الحجز'}
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="caption" color="text.secondary" display="block">الحد الأقصى للرد</Typography>
              <Typography variant="h6" color="primary.main" sx={{ fontWeight: 800 }}>{formatCurrency(maxRefundable)}</Typography>
            </Box>
          </Stack>
        </Paper>

        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 6 }}>
            <AppDateField label="تاريخ الإلغاء" value={cancelDate} onChange={(val) => setCancelDate(val)} />
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <TextField fullWidth label="مبلغ الرد النقدي" type='number' value={refundAmount} onChange={(e) => setRefundAmount(e.target.value)} />
          </Grid>
          <Grid size={{ xs: 12 }}>
            <TextField fullWidth select label="طريقة رد المبلغ" value={paymentMethodId} onChange={(e) => setPaymentMethodId(e.target.value)} disabled={Number(refundAmount) <= 0}>
              {paymentMethods.map((m) => <MenuItem key={m.id} value={m.id}>{m.name}</MenuItem>)}
            </TextField>
          </Grid>
          {isLineCancellation && otherActiveLines.length > 0 && (
            <>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField 
                  fullWidth 
                  select 
                  label="تحويل إلى خدمة أخرى" 
                  value={transferToLineId} 
                  onChange={(e) => {
                    setTransferToLineId(e.target.value);
                    if (!e.target.value) setTransferAmount('0');
                  }}
                  disabled={Number(refundAmount) >= maxRefundable}
                >
                  <MenuItem value="">-- لا يوجد تحويل --</MenuItem>
                  {otherActiveLines.map((l) => (
                    <MenuItem key={l.id} value={l.id}>{l.service_name} ({l.line_number})</MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField 
                  fullWidth 
                  label="مبلغ التحويل" 
                  type='number' 
                  value={transferAmount} 
                  onChange={(e) => setTransferAmount(e.target.value)}
                  disabled={!transferToLineId}
                />
              </Grid>
            </>
          )}
          <Grid size={{ xs: 12 }}>
            <TextField fullWidth label="سبب الإلغاء" multiline rows={3} value={reason} onChange={(e) => setReason(e.target.value)} />
          </Grid>
        </Grid>

        {/* Breakdown Summary */}
        <Box sx={{ p: 2, borderRadius: 3, bgcolor: alpha(theme.palette.divider, 0.03), border: '1px solid', borderColor: 'divider' }}>
          <Typography variant="overline" color="text.secondary" sx={{ fontWeight: 700, mb: 1, display: 'block' }}>خلاصة الحركة المالية</Typography>
          <Stack spacing={1}>
            <Stack direction="row" justifyContent="space-between">
              <Typography variant="body2">مبلغ الرد النقدي:</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>{formatCurrency(Number(refundAmount) || 0)}</Typography>
            </Stack>
            {transferToLineId && (
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">مبلغ التحويل للرصيد:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }} color="info.main">{formatCurrency(Number(transferAmount) || 0)}</Typography>
              </Stack>
            )}
            <Stack direction="row" justifyContent="space-between">
              <Typography variant="body2">مبلغ المصادرة (الغرامة):</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }} color="error.main">
                {formatCurrency(Math.max(0, maxRefundable - (Number(refundAmount) || 0) - (Number(transferAmount) || 0)))}
              </Typography>
            </Stack>
          </Stack>
        </Box>

        {/* Final Action */}
        <Box sx={{ mt: 1 }}>
          <Button
            fullWidth
            variant='contained'
            color="error"
            size="large"
            startIcon={<CancelScheduleSendOutlinedIcon />}
            disabled={saving || Number(refundAmount) > maxRefundable || (Number(refundAmount) > 0 && !paymentMethodId)}
            onClick={handleConfirm}
            sx={{
              py: 1.5,
              borderRadius: 3,
              fontWeight: 800,
              fontSize: '1rem',
              textTransform: 'none',
              boxShadow: `0 8px 16px ${alpha(theme.palette.error.main, 0.25)}`,
              '&:hover': {
                bgcolor: theme.palette.error.dark,
                boxShadow: `0 12px 20px ${alpha(theme.palette.error.main, 0.35)}`,
              }
            }}
          >
            {saving ? 'جاري تنفيذ الإلغاء...' : 'تأكيد الإلغاء والرد المالي'}
          </Button>
        </Box>
      </Stack>
    </AppDialogShell>
  );
}
