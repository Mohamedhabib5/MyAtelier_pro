import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
import { Box, Chip, CircularProgress, InputAdornment, List, ListItemButton, ListItemText, Stack, TextField, Typography } from '@mui/material';

import { SectionCard } from '../../components/SectionCard';
import type { PaymentTargetSearchRecord } from './api';

type Props = {
  title: string;
  subtitle: string;
  label: string;
  hint: string;
  searchText: string;
  onSearchTextChange: (value: string) => void;
  results: PaymentTargetSearchRecord[];
  loading: boolean;
  hasSearched: boolean;
  loadingLabel: string;
  noResultsLabel: string;
  customerKindLabel: string;
  bookingKindLabel: string;
  onSelectTarget: (target: PaymentTargetSearchRecord) => void;
};

export function PaymentTargetSearchSection({
  title,
  subtitle,
  label,
  hint,
  searchText,
  onSearchTextChange,
  results,
  loading,
  hasSearched,
  loadingLabel,
  noResultsLabel,
  customerKindLabel,
  bookingKindLabel,
  onSelectTarget,
}: Props) {
  const isArabic = /[\u0600-\u06FF]/.test(title);
  const suggestedCountLabel = isArabic ? `عدد الحسابات المقترحة: ${results.length}` : `Suggested accounts: ${results.length}`;
  const scrollHintLabel = isArabic ? 'مرر للأسفل لعرض باقي النتائج.' : 'Scroll down for more results.';
  const emptyLabel = hasSearched ? noResultsLabel : hint;

  return (
    <SectionCard title={title} subtitle={subtitle}>
      <Stack spacing={1.5}>
        <TextField
          label={label}
          value={searchText}
          onChange={(event) => onSearchTextChange(event.target.value)}
          inputProps={{ 'data-payment-target-search-input': 'true' }}
          InputProps={{
            startAdornment: (
              <InputAdornment position='start'>
                <SearchOutlinedIcon sx={{ color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 1.25,
              backgroundColor: 'background.paper',
            },
          }}
        />

        <Stack direction='row' justifyContent='space-between' alignItems='center' sx={{ px: 0.25 }}>
          <Typography variant='caption' color='text.secondary'>
            {suggestedCountLabel}
          </Typography>
          {loading ? (
            <Stack direction='row' spacing={0.75} alignItems='center'>
              <CircularProgress size={14} />
              <Typography variant='caption' color='text.secondary'>
                {loadingLabel}
              </Typography>
            </Stack>
          ) : null}
        </Stack>

        <Box sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1.5, overflow: 'hidden', backgroundColor: 'background.paper' }}>
          {results.length ? (
            <List
              sx={{
                p: 0,
                maxHeight: 280,
                overflowY: 'auto',
                '&::-webkit-scrollbar': { width: 8 },
                '&::-webkit-scrollbar-thumb': { backgroundColor: 'rgba(107, 47, 179, 0.35)', borderRadius: 8 },
              }}
            >
              {results.map((result, index) => (
                <ListItemButton
                  key={`${result.kind}-${result.id}`}
                  onClick={() => onSelectTarget(result)}
                  divider={index < results.length - 1}
                  sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, py: 1.15, px: 1.5 }}
                >
                  <ListItemText
                    primary={result.label}
                    secondary={result.booking_number ? `${result.customer_name} - ${result.booking_number}` : result.customer_name}
                    primaryTypographyProps={{ sx: { fontSize: 15 } }}
                    secondaryTypographyProps={{ sx: { fontSize: 13 } }}
                  />
                  <Chip size='small' label={result.kind === 'booking' ? bookingKindLabel : customerKindLabel} />
                </ListItemButton>
              ))}
            </List>
          ) : (
            <Box sx={{ py: 2, px: 2 }}>
              <Typography variant='body2' color='text.secondary'>
                {loading ? loadingLabel : emptyLabel}
              </Typography>
            </Box>
          )}
        </Box>

        {results.length > 6 ? (
          <Typography variant='caption' color='text.secondary'>
            {scrollHintLabel}
          </Typography>
        ) : null}
      </Stack>
    </SectionCard>
  );
}
