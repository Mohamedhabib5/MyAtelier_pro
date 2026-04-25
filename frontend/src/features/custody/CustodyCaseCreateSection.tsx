import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  CircularProgress,
  InputAdornment,
  List,
  ListItemButton,
  ListItemText,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useDeferredValue, useEffect, useMemo, useState } from 'react';

import { SectionCard } from '../../components/SectionCard';
import { StableNumericField } from '../../components/inputs/StableNumericField';
import { getBooking, listBookingsPage, type BookingSummaryRecord } from '../bookings/api';
import type { PaymentMethodRecord } from '../paymentMethods/api';
import type { CustodyCaseCreatePayload } from './api';

type Props = {
  language: 'ar' | 'en';
  title: string;
  subtitle: string;
  custodyDateLabel: string;
  createLabel: string;
  notesLabel: string;
  conditionLabel: string;
  depositAmountLabel: string;
  depositDocumentLabel: string;
  paymentMethodLabel: string;
  bookingSearchLabel: string;
  bookingSearchHint: string;
  bookingLineLabel: string;
  lineAlreadyUsedLabel: string;
  noLinesLabel: string;
  lineNoDressLabel: string;
  showCard?: boolean;
  existingCaseLineIds: string[];
  paymentMethods: PaymentMethodRecord[];
  isSubmitting: boolean;
  onCreateMany: (payloads: CustodyCaseCreatePayload[]) => Promise<void>;
};

export function CustodyCaseCreateSection({
  language,
  title,
  subtitle,
  custodyDateLabel,
  createLabel,
  notesLabel,
  conditionLabel,
  depositAmountLabel,
  depositDocumentLabel,
  paymentMethodLabel,
  bookingSearchLabel,
  bookingSearchHint,
  bookingLineLabel,
  lineAlreadyUsedLabel,
  noLinesLabel,
  lineNoDressLabel,
  showCard = true,
  existingCaseLineIds,
  paymentMethods,
  isSubmitting,
  onCreateMany,
}: Props) {
  const [searchText, setSearchText] = useState('');
  const [selectedBookingId, setSelectedBookingId] = useState<string | null>(null);
  const [selectedLineIds, setSelectedLineIds] = useState<string[]>([]);
  const [custodyDate, setCustodyDate] = useState(new Date().toISOString().slice(0, 10));
  const [notes, setNotes] = useState('');
  const [productCondition, setProductCondition] = useState('');
  const [depositAmount, setDepositAmount] = useState('');
  const [depositDocumentText, setDepositDocumentText] = useState('');
  const [paymentMethodId, setPaymentMethodId] = useState('');

  useEffect(() => {
    if (!paymentMethods.length) return;
    if (paymentMethodId && paymentMethods.some((item) => item.id === paymentMethodId)) return;
    setPaymentMethodId(paymentMethods[0].id);
  }, [paymentMethodId, paymentMethods]);

  const deferredSearch = useDeferredValue(searchText.trim());
  const bookingsQuery = useQuery({
    queryKey: ['custody', 'booking-search', deferredSearch || '__default__'],
    queryFn: () =>
      listBookingsPage({
        search: deferredSearch || undefined,
        page: 1,
        pageSize: 50,
        sortBy: 'booking_date',
        sortDir: 'desc',
      }),
  });
  const bookingQuery = useQuery({
    queryKey: ['custody', 'booking-detail', selectedBookingId],
    queryFn: () => getBooking(selectedBookingId!),
    enabled: Boolean(selectedBookingId),
  });

  const bookingRows = bookingsQuery.data?.items ?? [];
  const selectedBooking = bookingQuery.data ?? null;
  const existingSet = useMemo(() => new Set(existingCaseLineIds), [existingCaseLineIds]);
  const selectableLines = useMemo(
    () => (selectedBooking?.lines ?? []).filter((line) => line.status !== 'cancelled'),
    [selectedBooking],
  );
  const hasNoDressLineSelected = useMemo(
    () => selectableLines.some((line) => selectedLineIds.includes(line.id) && !line.dress_id),
    [selectableLines, selectedLineIds],
  );
  const requiresDepositDocument = Number(depositAmount || 0) > 0;

  const suggestedCountLabel = language === 'ar' ? `عدد الحجوزات المقترحة: ${bookingRows.length}` : `Suggested bookings: ${bookingRows.length}`;
  const scrollHintLabel = language === 'ar' ? 'مرر للأسفل لعرض باقي النتائج.' : 'Scroll down for more results.';
  const loadingLabel = language === 'ar' ? 'جاري التحميل...' : 'Loading...';
  const noResultsLabel = language === 'ar' ? 'لا توجد نتائج.' : 'No results.';
  const bookingTypeLabel = language === 'ar' ? 'حجز' : 'Booking';
  const searchSectionTitle = language === 'ar' ? 'اختيار الحجز' : 'Select booking';
  const selectedLinesTitle = language === 'ar' ? 'سطور الحجز' : 'Booking lines';
  const detailsTitle = language === 'ar' ? 'بيانات سند الحيازة' : 'Custody voucher details';
  const emptyLabel = bookingsQuery.isFetching ? loadingLabel : deferredSearch ? noResultsLabel : bookingSearchHint;

  function toggleLine(lineId: string) {
    setSelectedLineIds((current) => (current.includes(lineId) ? current.filter((value) => value !== lineId) : [...current, lineId]));
  }

  function handleSelectBooking(booking: BookingSummaryRecord) {
    setSelectedBookingId(booking.id);
    setSelectedLineIds([]);
  }

  async function submitCreate() {
    const payloads = selectedLineIds.map((lineId) => ({
      booking_line_id: lineId,
      custody_date: custodyDate,
      case_type: 'handover',
      notes: notes.trim() || null,
      product_condition: productCondition.trim() || null,
      security_deposit_amount: Number(depositAmount || 0) > 0 ? Number(depositAmount) : null,
      security_deposit_document_text: depositDocumentText.trim() || null,
      payment_method_id: Number(depositAmount || 0) > 0 ? paymentMethodId || null : null,
    }));
    await onCreateMany(payloads);
    setSelectedLineIds([]);
    setCustodyDate(new Date().toISOString().slice(0, 10));
    setNotes('');
    setProductCondition('');
    setDepositAmount('');
    setDepositDocumentText('');
    setPaymentMethodId(paymentMethods[0]?.id ?? '');
  }

  const form = (
    <Stack spacing={2}>
      <TextField
        label={bookingSearchLabel}
        value={searchText}
        onChange={(event) => setSearchText(event.target.value)}
        inputProps={{ 'data-custody-booking-search-input': 'true' }}
        InputProps={{
          startAdornment: (
            <InputAdornment position='start'>
              <SearchOutlinedIcon sx={{ color: 'text.secondary' }} />
            </InputAdornment>
          ),
        }}
      />

      <Stack direction={{ xs: 'column', lg: 'row' }} spacing={2}>
        <Stack spacing={1.25} sx={{ flex: 1, minWidth: 0 }}>
          <Typography variant='subtitle2'>{searchSectionTitle}</Typography>
          <Stack direction='row' justifyContent='space-between' alignItems='center'>
            <Typography variant='caption' color='text.secondary'>
              {suggestedCountLabel}
            </Typography>
            {bookingsQuery.isFetching ? (
              <Stack direction='row' spacing={0.75} alignItems='center'>
                <CircularProgress size={14} />
                <Typography variant='caption' color='text.secondary'>
                  {loadingLabel}
                </Typography>
              </Stack>
            ) : null}
          </Stack>

          <Box sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1.5, overflow: 'hidden', backgroundColor: 'background.paper' }}>
            {bookingRows.length ? (
              <List sx={{ p: 0, maxHeight: 220, overflowY: 'auto' }}>
                {bookingRows.map((booking, index) => (
                  <ListItemButton
                    key={booking.id}
                    selected={selectedBookingId === booking.id}
                    divider={index < bookingRows.length - 1}
                    onClick={() => handleSelectBooking(booking)}
                    sx={{ alignItems: 'flex-start', gap: 1, py: 1.1, px: 1.4 }}
                  >
                    <ListItemText
                      primary={booking.booking_number}
                      secondary={`${booking.customer_name} - ${booking.booking_date} - ${booking.service_summary}`}
                      primaryTypographyProps={{ sx: { fontSize: 14 } }}
                      secondaryTypographyProps={{ sx: { fontSize: 12.5 } }}
                    />
                    <Chip size='small' label={bookingTypeLabel} />
                  </ListItemButton>
                ))}
              </List>
            ) : (
              <Box sx={{ py: 2, px: 2 }}>
                <Typography variant='body2' color='text.secondary'>
                  {emptyLabel}
                </Typography>
              </Box>
            )}
          </Box>
          {bookingRows.length > 6 ? (
            <Typography variant='caption' color='text.secondary'>
              {scrollHintLabel}
            </Typography>
          ) : null}

          <Typography variant='subtitle2' sx={{ mt: 0.5 }}>
            {selectedLinesTitle}
          </Typography>
          {selectedBooking ? (
            <Stack spacing={1}>
              <Typography variant='body2' color='text.secondary'>{`${selectedBooking.booking_number} - ${selectedBooking.customer_name}`}</Typography>
              {bookingQuery.isFetching ? (
                <Stack direction='row' spacing={1} alignItems='center'>
                  <CircularProgress size={16} />
                  <Typography variant='body2' color='text.secondary'>
                    {language === 'ar' ? 'جاري تحميل سطور الحجز...' : 'Loading booking lines...'}
                  </Typography>
                </Stack>
              ) : selectableLines.length ? (
                <Box sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1.5, overflow: 'hidden', backgroundColor: 'background.paper' }}>
                  <List sx={{ p: 0, maxHeight: 240, overflowY: 'auto' }}>
                    {selectableLines.map((line, index) => {
                      const disabled = existingSet.has(line.id);
                      const checked = selectedLineIds.includes(line.id);
                      return (
                        <ListItemButton
                          key={line.id}
                          divider={index < selectableLines.length - 1}
                          disabled={disabled}
                          onClick={() => {
                            if (disabled) return;
                            toggleLine(line.id);
                          }}
                        >
                          <Checkbox checked={checked} tabIndex={-1} disableRipple />
                          <ListItemText
                            primary={`${bookingLineLabel} ${line.line_number} - ${line.service_name}`}
                            secondary={
                              disabled
                                ? lineAlreadyUsedLabel
                                : line.dress_code
                                  ? `${line.service_date} | ${line.dress_code}`
                                  : `${line.service_date} | ${lineNoDressLabel}`
                            }
                          />
                        </ListItemButton>
                      );
                    })}
                  </List>
                </Box>
              ) : (
                <Alert severity='info'>{noLinesLabel}</Alert>
              )}
            </Stack>
          ) : (
            <Alert severity='info'>{language === 'ar' ? 'اختر حجزًا أولًا ثم حدّد السطور.' : 'Select a booking first, then choose lines.'}</Alert>
          )}
        </Stack>

        <Stack spacing={1.25} sx={{ width: { xs: '100%', lg: 360 }, flexShrink: 0 }}>
          <Typography variant='subtitle2'>{detailsTitle}</Typography>
          <TextField
            label={custodyDateLabel}
            value={custodyDate}
            type='date'
            onChange={(event) => setCustodyDate(event.target.value)}
            slotProps={{ inputLabel: { shrink: true } }}
            fullWidth
            required
          />
          <StableNumericField label={depositAmountLabel} value={depositAmount} onValueChange={setDepositAmount} fullWidth />
          <TextField
            select
            label={paymentMethodLabel}
            value={paymentMethodId}
            onChange={(event) => setPaymentMethodId(event.target.value)}
            fullWidth
            disabled={!requiresDepositDocument}
          >
            {paymentMethods.map((method) => (
              <MenuItem key={method.id} value={method.id}>
                {method.name}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label={depositDocumentLabel}
            value={depositDocumentText}
            onChange={(event) => setDepositDocumentText(event.target.value)}
            fullWidth
            required={requiresDepositDocument}
          />
          <TextField label={conditionLabel} value={productCondition} onChange={(event) => setProductCondition(event.target.value)} />
          <TextField label={notesLabel} value={notes} onChange={(event) => setNotes(event.target.value)} multiline minRows={3} />
        </Stack>
      </Stack>

      <Button
        variant='contained'
        fullWidth
        disabled={
          isSubmitting
          || !selectedLineIds.length
          || !custodyDate
          || (requiresDepositDocument && !depositDocumentText.trim())
          || (requiresDepositDocument && !paymentMethodId)
          || (hasNoDressLineSelected && !notes.trim())
        }
        onClick={() => void submitCreate()}
      >
        {createLabel}
      </Button>
    </Stack>
  );

  if (!showCard) {
    return form;
  }

  return (
    <SectionCard title={title} subtitle={subtitle}>
      {form}
    </SectionCard>
  );
}
