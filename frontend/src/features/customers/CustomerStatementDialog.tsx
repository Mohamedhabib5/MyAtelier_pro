import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined';
import FileDownloadOutlinedIcon from '@mui/icons-material/FileDownloadOutlined';
import CloseOutlinedIcon from '@mui/icons-material/CloseOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import EventAvailableOutlinedIcon from '@mui/icons-material/EventAvailableOutlined';
import PaymentsOutlinedIcon from '@mui/icons-material/PaymentsOutlined';
import AccountBalanceOutlinedIcon from '@mui/icons-material/AccountBalanceOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Paper,
  Stack,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Typography,
} from '@mui/material';

import { getCustomerStatement, type CustomerStatementResponse } from './api';
import { CustomerStatementPrintView } from './CustomerStatementPrintView';
import { useCustomersText } from '../../text/customers';

export function formatCurrency(value: number, language: 'ar' | 'en') {
  return new Intl.NumberFormat(language === 'ar' ? 'ar-EG' : 'en-US', { style: 'currency', currency: 'EGP', maximumFractionDigits: 2 }).format(value);
}

type Props = {
  open: boolean;
  customerId: string | null;
  language: 'ar' | 'en';
  onClose: () => void;
};

export function CustomerStatementDialog({ open, customerId, language, onClose }: Props) {
  const customersText = useCustomersText();
  const stText = customersText.statement;
  const isAr = language === 'ar';

  const [activeTab, setActiveTab] = useState(0);
  const [printMode, setPrintMode] = useState(false);

  const statementQuery = useQuery<CustomerStatementResponse>({
    queryKey: ['customer-statement', customerId],
    queryFn: () => getCustomerStatement(customerId!),
    enabled: Boolean(open && customerId),
  });

  if (!open) return null;

  if (printMode && statementQuery.data) {
    return (
      <Dialog fullScreen open={open} onClose={() => setPrintMode(false)}>
        <CustomerStatementPrintView data={statementQuery.data} language={language} onClose={() => setPrintMode(false)} />
      </Dialog>
    );
  }

  const data = statementQuery.data;
  const loading = statementQuery.isLoading;
  const error = statementQuery.error ? (statementQuery.error as Error).message : null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth='lg' fullWidth PaperProps={{ sx: { borderRadius: 2, minHeight: '80vh' } }}>
      <DialogTitle sx={{ pb: 1 }}>
        <Stack direction='row' justifyContent='space-between' alignItems='center'>
          <Stack direction='row' spacing={1.5} alignItems='center'>
            <ReceiptLongOutlinedIcon color='primary' sx={{ fontSize: 32 }} />
            <Box>
              <Typography variant='h6' fontWeight='bold'>
                {stText.title}
              </Typography>
              {data ? (
                <Typography variant='subtitle2' color='text.secondary'>
                  {data.customer.full_name} {data.customer.phone ? `(${data.customer.phone})` : ''}
                </Typography>
              ) : null}
            </Box>
          </Stack>
          <Stack direction='row' spacing={1}>
            {data ? (
              <Button variant='contained' color='primary' size='small' startIcon={<PrintOutlinedIcon />} onClick={() => setPrintMode(true)}>
                {stText.printBtn}
              </Button>
            ) : null}
            <Button variant='outlined' color='inherit' size='small' onClick={onClose} startIcon={<CloseOutlinedIcon />}>
              {isAr ? 'إغلاق' : 'Close'}
            </Button>
          </Stack>
        </Stack>
      </DialogTitle>

      <DialogContent dividers>
        {loading ? (
          <Stack alignItems='center' justifyContent='center' sx={{ py: 10 }}>
            <CircularProgress size={48} />
            <Typography variant='body2' color='text.secondary' sx={{ mt: 2 }}>
              {isAr ? 'جاري تحميل كشف الحساب والحركات...' : 'Loading statement & movements...'}
            </Typography>
          </Stack>
        ) : error ? (
          <Alert severity='error' sx={{ my: 2 }}>
            {error}
          </Alert>
        ) : data ? (
          <Stack spacing={3}>
            {/* KPI Cards Row */}
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Card variant='outlined' sx={{ bgcolor: 'action.hover' }}>
                  <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                    <Typography variant='caption' color='text.secondary'>
                      {stText.totalBookings}
                    </Typography>
                    <Typography variant='h6' color='primary.main' fontWeight='bold'>
                      {formatCurrency(data.summary.total_bookings_amount, language)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Card variant='outlined' sx={{ bgcolor: 'success.50' }}>
                  <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                    <Typography variant='caption' color='text.secondary'>
                      {stText.totalCollections}
                    </Typography>
                    <Typography variant='h6' color='success.main' fontWeight='bold'>
                      {formatCurrency(data.summary.total_collections_amount, language)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Card variant='outlined' sx={{ bgcolor: data.summary.remaining_balance > 0 ? 'error.50' : 'background.paper' }}>
                  <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                    <Typography variant='caption' color='text.secondary'>
                      {stText.remainingBalance}
                    </Typography>
                    <Typography variant='h6' color={data.summary.remaining_balance > 0 ? 'error.main' : 'text.primary'} fontWeight='bold'>
                      {formatCurrency(data.summary.remaining_balance, language)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Card variant='outlined' sx={{ bgcolor: 'info.50' }}>
                  <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                    <Typography variant='caption' color='text.secondary'>
                      {stText.ledgerBalance}
                    </Typography>
                    <Typography variant='h6' color='info.main' fontWeight='bold'>
                      {formatCurrency(data.summary.accounting_ledger_balance, language)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Navigation Tabs */}
            <Paper variant='outlined'>
              <Tabs value={activeTab} onChange={(_, val) => setActiveTab(val)} indicatorColor='primary' textColor='primary' variant='fullWidth'>
                <Tab icon={<EventAvailableOutlinedIcon />} iconPosition='start' label={stText.tabs.services} />
                <Tab icon={<PaymentsOutlinedIcon />} iconPosition='start' label={stText.tabs.payments} />
                <Tab icon={<AccountBalanceOutlinedIcon />} iconPosition='start' label={stText.tabs.ledger} />
              </Tabs>
            </Paper>

            {/* Tab 0: Bookings & Services */}
            {activeTab === 0 ? (
              <Box>
                {data.bookings.length === 0 ? (
                  <Typography variant='body2' color='text.secondary' sx={{ py: 4, textAlign: 'center' }}>
                    {stText.noMovements}
                  </Typography>
                ) : (
                  <Stack spacing={2}>
                    {data.bookings.map((b) => (
                      <Card key={b.booking_id} variant='outlined'>
                        <CardContent>
                          <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent='space-between' alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={1} sx={{ mb: 1.5 }}>
                            <Box>
                              <Typography variant='subtitle1' fontWeight='bold' color='primary'>
                                {stText.bookingNo}: {b.booking_number}
                              </Typography>
                              <Typography variant='caption' color='text.secondary'>
                                {stText.bookingDate}: {b.booking_date} | {stText.branch}: {b.branch_name}
                              </Typography>
                            </Box>
                            <Stack direction='row' spacing={1} alignItems='center'>
                              <Chip label={b.status} size='small' color={b.status === 'cancelled' ? 'error' : b.status === 'executed' ? 'success' : 'default'} />
                              <Typography variant='subtitle2' fontWeight='bold'>
                                {stText.totalAmount}: {formatCurrency(b.total_amount, language)}
                              </Typography>
                            </Stack>
                          </Stack>

                          {b.cancelled_at ? (
                            <Alert severity='warning' sx={{ mb: 1.5 }}>
                              {isAr ? 'حجز ملغي بتاريخ' : 'Cancelled at'}: {b.cancelled_at} {b.cancellation_reason ? `(${b.cancellation_reason})` : ''}
                            </Alert>
                          ) : null}

                          <TableContainer component={Paper} variant='outlined'>
                            <Table size='small'>
                              <TableHead>
                                <TableRow sx={{ bgcolor: 'action.hover' }}>
                                  <TableCell>{stText.serviceName}</TableCell>
                                  <TableCell>{stText.serviceDate}</TableCell>
                                  <TableCell>{isAr ? 'حالة البند' : 'Line Status'}</TableCell>
                                  <TableCell align='right'>{stText.totalAmount}</TableCell>
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {b.lines.map((l) => (
                                  <TableRow key={l.line_id}>
                                    <TableCell>
                                      <Typography variant='body2' fontWeight='medium'>
                                        {l.service_name}
                                      </Typography>
                                      {l.dress_code || l.dress_name ? (
                                        <Typography variant='caption' color='text.secondary' display='block'>
                                          {l.dress_name} ({l.dress_code})
                                        </Typography>
                                      ) : null}
                                    </TableCell>
                                    <TableCell>{l.service_date}</TableCell>
                                    <TableCell>
                                      <Chip label={l.status} size='small' variant='outlined' color={l.status === 'executed' ? 'success' : l.status === 'cancelled' ? 'error' : 'default'} />
                                    </TableCell>
                                    <TableCell align='right'>{formatCurrency(l.line_price, language)}</TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </TableContainer>
                        </CardContent>
                      </Card>
                    ))}
                  </Stack>
                )}
              </Box>
            ) : null}

            {/* Tab 1: Collections & Payments */}
            {activeTab === 1 ? (
              <Box>
                {data.payments.length === 0 ? (
                  <Typography variant='body2' color='text.secondary' sx={{ py: 4, textAlign: 'center' }}>
                    {stText.noMovements}
                  </Typography>
                ) : (
                  <TableContainer component={Paper} variant='outlined'>
                    <Table size='small'>
                      <TableHead>
                        <TableRow sx={{ bgcolor: 'action.hover' }}>
                          <TableCell>{stText.paymentNo}</TableCell>
                          <TableCell>{stText.paymentDate}</TableCell>
                          <TableCell>{stText.paymentMethod}</TableCell>
                          <TableCell>{isAr ? 'نوع السند' : 'Kind'}</TableCell>
                          <TableCell>{isAr ? 'الحالة' : 'Status'}</TableCell>
                          <TableCell align='right'>{stText.totalAmount}</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {data.payments.map((p) => (
                          <TableRow key={p.payment_id}>
                            <TableCell sx={{ fontWeight: 'medium' }}>{p.payment_number}</TableCell>
                            <TableCell>{p.payment_date}</TableCell>
                            <TableCell>{p.payment_method_name}</TableCell>
                            <TableCell>{p.document_kind}</TableCell>
                            <TableCell>
                              <Chip label={p.status} size='small' color={p.status === 'active' ? 'success' : 'error'} />
                            </TableCell>
                            <TableCell align='right' sx={{ fontWeight: 'bold' }}>
                              {formatCurrency(p.amount, language)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </Box>
            ) : null}

            {/* Tab 2: General Ledger */}
            {activeTab === 2 ? (
              <Box>
                {data.ledger_movements.length === 0 ? (
                  <Typography variant='body2' color='text.secondary' sx={{ py: 4, textAlign: 'center' }}>
                    {stText.noMovements}
                  </Typography>
                ) : (
                  <TableContainer component={Paper} variant='outlined'>
                    <Table size='small'>
                      <TableHead>
                        <TableRow sx={{ bgcolor: 'action.hover' }}>
                          <TableCell>{stText.entryDate}</TableCell>
                          <TableCell>{stText.entryNo}</TableCell>
                          <TableCell>{stText.description}</TableCell>
                          <TableCell align='right'>{stText.debit}</TableCell>
                          <TableCell align='right'>{stText.credit}</TableCell>
                          <TableCell align='right'>{stText.runningBalance}</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {data.ledger_movements.map((m, idx) => (
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
              </Box>
            ) : null}
          </Stack>
        ) : null}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button variant='outlined' onClick={onClose}>
          {isAr ? 'إغلاق' : 'Close'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
