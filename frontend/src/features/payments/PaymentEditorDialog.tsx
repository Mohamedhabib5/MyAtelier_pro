import { CircularProgress, Stack } from '@mui/material';

import { AppDialogShell } from '../../components/AppDialogShell';
import type { PaymentMethodRecord } from '../paymentMethods/api';
import type { PaymentDocumentPayload, PaymentDocumentRecord, PaymentTargetDetailRecord, PaymentTargetSearchRecord } from './api';
import { PaymentDocumentBuilder } from './PaymentDocumentBuilder';
import { PaymentTargetSearchSection } from './PaymentTargetSearchSection';

type Props = {
  open: boolean;
  title: string;
  subtitle: string;
  loading: boolean;
  target: PaymentTargetDetailRecord | null;
  document: PaymentDocumentRecord | null;
  paymentMethods: PaymentMethodRecord[];
  saving: boolean;
  searchTitle: string;
  searchSubtitle: string;
  searchLabel: string;
  searchHint: string;
  searchText: string;
  searchResults: PaymentTargetSearchRecord[];
  searchLoading: boolean;
  hasTargetSearch: boolean;
  searchLoadingLabel: string;
  searchNoResultsLabel: string;
  customerKindLabel: string;
  bookingKindLabel: string;
  onSearchTextChange: (value: string) => void;
  onSelectTarget: (target: PaymentTargetSearchRecord) => void;
  onClose: () => void;
  onSave: (payload: PaymentDocumentPayload) => Promise<void>;
};

export function PaymentEditorDialog({
  open,
  title,
  subtitle,
  loading,
  target,
  document,
  paymentMethods,
  saving,
  searchTitle,
  searchSubtitle,
  searchLabel,
  searchHint,
  searchText,
  searchResults,
  searchLoading,
  hasTargetSearch,
  searchLoadingLabel,
  searchNoResultsLabel,
  customerKindLabel,
  bookingKindLabel,
  onSearchTextChange,
  onSelectTarget,
  onClose,
  onSave,
}: Props) {
  return (
    <AppDialogShell open={open} onClose={onClose} title={title} subtitle={subtitle} maxWidth='xl'>
      {loading ? (
        <Stack alignItems='center' justifyContent='center' sx={{ minHeight: 240 }}>
          <CircularProgress />
        </Stack>
      ) : target ? (
        <PaymentDocumentBuilder target={target} document={document} paymentMethods={paymentMethods} saving={saving} onSave={onSave} onCancel={onClose} />
      ) : (
        <PaymentTargetSearchSection
          title={searchTitle}
          subtitle={searchSubtitle}
          label={searchLabel}
          hint={searchHint}
          searchText={searchText}
          onSearchTextChange={onSearchTextChange}
          results={searchResults}
          loading={searchLoading}
          hasSearched={hasTargetSearch}
          loadingLabel={searchLoadingLabel}
          noResultsLabel={searchNoResultsLabel}
          customerKindLabel={customerKindLabel}
          bookingKindLabel={bookingKindLabel}
          onSelectTarget={onSelectTarget}
        />
      )}
    </AppDialogShell>
  );
}
