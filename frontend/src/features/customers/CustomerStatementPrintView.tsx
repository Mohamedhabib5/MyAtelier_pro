import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined';
import CloseOutlinedIcon from '@mui/icons-material/CloseOutlined';
import { Box, Button, Card, CardContent, Divider, Grid, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';
import type { CustomerStatementResponse } from './api';
import { formatCurrency } from './CustomerStatementDialog';

type Props = {
  data: CustomerStatementResponse;
  language: 'ar' | 'en';
  onClose: () => void;
};

export function CustomerStatementPrintView({ data, language, onClose }: Props) {
  const isAr = language === 'ar';
  const { customer, summary, bookings, payments, ledger_movements } = data;

  const title = isAr ? 'كشف حساب عميل' : 'Customer Account Statement';
  const customerNameLabel = isAr ? 'اسم العميل' : 'Customer Name';
  const groomBrideLabel = isAr ? 'العريس والعروسة' : 'Groom & Bride';
  const phoneLabel = isAr ? 'رقم الهاتف' : 'Phone Number';
  const addressLabel = isAr ? 'العنوان' : 'Address';
  const regDateLabel = isAr ? 'تاريخ التسجيل' : 'Reg. Date';

  return (
    <Box sx={{ p: 3, bgcolor: 'background.paper', minHeight: '100vh', '@media print': { p: 0 } }}>
      {/* Top Action Bar - Hidden during printing */}
      <Stack direction='row' spacing={2} justifyContent='space-between' alignItems='center' sx={{ mb: 3, '@media print': { display: 'none' } }}>
        <Typography variant='h6'>{title}</Typography>
        <Stack direction='row' spacing={1}>
          <Button variant='contained' startIcon={<PrintOutlinedIcon />} onClick={() => window.print()}>
            {isAr ? 'طباعة كشف الحساب' : 'Print Statement'}
          </Button>
          <Button variant='outlined' color='inherit' startIcon={<CloseOutlinedIcon />} onClick={onClose}>
            {isAr ? 'إغلاق المعاينة' : 'Close Preview'}
          </Button>
        </Stack>
      </Stack>

      <Paper variant='outlined' sx={{ p: 4, borderRadius: 2 }}>
        {/* Statement Header */}
        <Stack direction='row' justifyContent='space-between' alignItems='flex-start' sx={{ mb: 3 }}>
          <Box>
            <Typography variant='h5' fontWeight='bold' color='primary'>
              {title}
            </Typography>
            <Typography variant='subtitle1' color='text.secondary'>
              {customer.full_name}
            </Typography>
          </Box>
          <Box textAlign={isAr ? 'left' : 'right'}>
            <Typography variant='caption' color='text.secondary' display='block'>
              {isAr ? 'تاريخ التقرير' : 'Report Date'}: {new Date().toLocaleDateString(isAr ? 'ar-EG' : 'en-US')}
            </Typography>
          </Box>
        </Stack>

        <Divider sx={{ mb: 3 }} />

        {/* Customer Details Grid */}
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Typography variant='caption' color='text.secondary'>
              {customerNameLabel}
            </Typography>
            <Typography variant='body1' fontWeight='medium'>
              {customer.full_name}
            </Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Typography variant='caption' color='text.secondary'>
              {groomBrideLabel}
            </Typography>
            <Typography variant='body1'>
              {customer.groom_name || customer.bride_name ? `${customer.groom_name ?? ''} ${customer.bride_name ? `& ${customer.bride_name}` : ''}` : '-'}
            </Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Typography variant='caption' color='text.secondary'>
              {phoneLabel}
            </Typography>
            <Typography variant='body1'>{customer.phone}</Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Typography variant='caption' color='text.secondary'>
              {addressLabel}
            </Typography>
            <Typography variant='body1'>{customer.address ?? '-'}</Typography>
          </Grid>
        </Grid>

        {/* Financial KPI Summary Cards */}
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid size={{ xs: 6, sm: 3 }}>
            <Card variant='outlined' sx={{ bgcolor: 'action.hover' }}>
              <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Typography variant='caption' color='text.secondary'>
                  {isAr ? 'إجمالي الحجوزات' : 'Total Bookings'}
                </Typography>
                <Typography variant='h6' color='primary.main' fontWeight='bold'>
                  {formatCurrency(summary.total_bookings_amount, language)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 6, sm: 3 }}>
            <Card variant='outlined' sx={{ bgcolor: 'success.50' }}>
              <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Typography variant='caption' color='text.secondary'>
                  {isAr ? 'إجمالي المقبوضات' : 'Total Collections'}
                </Typography>
                <Typography variant='h6' color='success.main' fontWeight='bold'>
                  {formatCurrency(summary.total_collections_amount, language)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 6, sm: 3 }}>
            <Card variant='outlined' sx={{ bgcolor: summary.remaining_balance > 0 ? 'error.50' : 'background.paper' }}>
              <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Typography variant='caption' color='text.secondary'>
                  {isAr ? 'الرصيد المتبقي المستحق' : 'Remaining Balance'}
                </Typography>
                <Typography variant='h6' color={summary.remaining_balance > 0 ? 'error.main' : 'text.primary'} fontWeight='bold'>
                  {formatCurrency(summary.remaining_balance, language)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 6, sm: 3 }}>
            <Card variant='outlined' sx={{ bgcolor: 'info.50' }}>
              <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Typography variant='caption' color='text.secondary'>
                  {isAr ? 'الرصيد المحاسبي' : 'Ledger Balance'}
                </Typography>
                <Typography variant='h6' color='info.main' fontWeight='bold'>
                  {formatCurrency(summary.accounting_ledger_balance, language)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Section 1: Bookings & Services */}
        <Typography variant='h6' sx={{ mb: 1.5, fontWeight: 'bold' }}>
          {isAr ? '1. الحجوزات والخدمات وتواريخ التنفيذ' : '1. Bookings & Services Schedule'}
        </Typography>
        {bookings.length === 0 ? (
          <Typography variant='body2' color='text.secondary' sx={{ mb: 3 }}>
            {isAr ? 'لا توجد حجوزات مسجلة' : 'No bookings recorded.'}
          </Typography>
        ) : (
          <TableContainer component={Paper} variant='outlined' sx={{ mb: 4 }}>
            <Table size='small'>
              <TableHead>
                <TableRow sx={{ bgcolor: 'action.hover' }}>
                  <TableCell>{isAr ? 'رقم الحجز' : 'Booking #'}</TableCell>
                  <TableCell>{isAr ? 'تاريخ الحجز' : 'Booking Date'}</TableCell>
                  <TableCell>{isAr ? 'الخدمة / الفستان' : 'Service / Dress'}</TableCell>
                  <TableCell>{isAr ? 'تاريخ الخدمة' : 'Service Date'}</TableCell>
                  <TableCell>{isAr ? 'الحالة' : 'Status'}</TableCell>
                  <TableCell align='right'>{isAr ? 'المبلغ' : 'Amount'}</TableCell>
                  <TableCell align='right'>{isAr ? 'المدفوع' : 'Paid'}</TableCell>
                  <TableCell align='right'>{isAr ? 'المتبقي' : 'Remaining'}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {bookings.map((b) => (
                  <TableRow key={b.booking_id}>
                    <TableCell sx={{ fontWeight: 'medium' }}>{b.booking_number}</TableCell>
                    <TableCell>{b.booking_date}</TableCell>
                    <TableCell>
                      {b.lines.map((l) => (
                        <Box key={l.line_id} sx={{ mb: 0.5 }}>
                          <Typography variant='body2'>
                            {l.service_name} {l.dress_name ? `(${l.dress_name})` : ''}
                          </Typography>
                        </Box>
                      ))}
                    </TableCell>
                    <TableCell>
                      {b.lines.map((l) => (
                        <Typography key={l.line_id} variant='body2' display='block'>
                          {l.service_date}
                        </Typography>
                      ))}
                    </TableCell>
                    <TableCell>{b.status}</TableCell>
                    <TableCell align='right'>{formatCurrency(b.total_amount, language)}</TableCell>
                    <TableCell align='right'>{formatCurrency(b.paid_total, language)}</TableCell>
                    <TableCell align='right'>{formatCurrency(b.remaining_amount, language)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* Section 2: Payments & Collections */}
        <Typography variant='h6' sx={{ mb: 1.5, fontWeight: 'bold' }}>
          {isAr ? '2. المقبوضات وسندات التحصيل' : '2. Collections & Receipts'}
        </Typography>
        {payments.length === 0 ? (
          <Typography variant='body2' color='text.secondary' sx={{ mb: 3 }}>
            {isAr ? 'لا توجد مقبوضات مسجلة' : 'No payments recorded.'}
          </Typography>
        ) : (
          <TableContainer component={Paper} variant='outlined' sx={{ mb: 4 }}>
            <Table size='small'>
              <TableHead>
                <TableRow sx={{ bgcolor: 'action.hover' }}>
                  <TableCell>{isAr ? 'رقم السند' : 'Receipt #'}</TableCell>
                  <TableCell>{isAr ? 'التاريخ' : 'Date'}</TableCell>
                  <TableCell>{isAr ? 'طريقة الدفع' : 'Payment Method'}</TableCell>
                  <TableCell>{isAr ? 'نوع المستند' : 'Kind'}</TableCell>
                  <TableCell>{isAr ? 'الحالة' : 'Status'}</TableCell>
                  <TableCell align='right'>{isAr ? 'المبلغ' : 'Amount'}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {payments.map((p) => (
                  <TableRow key={p.payment_id}>
                    <TableCell sx={{ fontWeight: 'medium' }}>{p.payment_number}</TableCell>
                    <TableCell>{p.payment_date}</TableCell>
                    <TableCell>{p.payment_method_name}</TableCell>
                    <TableCell>{p.document_kind}</TableCell>
                    <TableCell>{p.status}</TableCell>
                    <TableCell align='right'>{formatCurrency(p.amount, language)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* Section 3: Ledger Movements */}
        <Typography variant='h6' sx={{ mb: 1.5, fontWeight: 'bold' }}>
          {isAr ? '3. كشف الحساب المحاسبي (دفتر الأستاذ)' : '3. General Ledger Movements'}
        </Typography>
        {ledger_movements.length === 0 ? (
          <Typography variant='body2' color='text.secondary'>
            {isAr ? 'لا توجد قيود محاسبية رحلت بعد' : 'No posted journal entries.'}
          </Typography>
        ) : (
          <TableContainer component={Paper} variant='outlined'>
            <Table size='small'>
              <TableHead>
                <TableRow sx={{ bgcolor: 'action.hover' }}>
                  <TableCell>{isAr ? 'التاريخ' : 'Date'}</TableCell>
                  <TableCell>{isAr ? 'رقم القيد' : 'Entry #'}</TableCell>
                  <TableCell>{isAr ? 'البيان' : 'Description'}</TableCell>
                  <TableCell align='right'>{isAr ? 'مدين' : 'Debit'}</TableCell>
                  <TableCell align='right'>{isAr ? 'دائن' : 'Credit'}</TableCell>
                  <TableCell align='right'>{isAr ? 'الرصيد المتراكم' : 'Balance'}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {ledger_movements.map((m, idx) => (
                  <TableRow key={idx}>
                    <TableCell>{m.entry_date}</TableCell>
                    <TableCell>{m.entry_number}</TableCell>
                    <TableCell>{m.description ?? m.reference ?? '-'}</TableCell>
                    <TableCell align='right'>{formatCurrency(m.debit_amount, language)}</TableCell>
                    <TableCell align='right'>{formatCurrency(m.credit_amount, language)}</TableCell>
                    <TableCell align='right' sx={{ fontWeight: 'bold' }}>
                      {formatCurrency(m.running_balance, language)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Box>
  );
}
