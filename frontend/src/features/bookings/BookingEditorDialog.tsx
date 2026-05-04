import { CircularProgress, Stack } from '@mui/material';

import { AppDialogShell } from '../../components/AppDialogShell';
import { BookingDocumentEditor } from './BookingDocumentEditor';
import type { BookingDocumentPayload, BookingDocumentRecord } from './api';
import type { CustomerPayload, CustomerRecord } from '../customers/api';
import type { DepartmentRecord, ServiceRecord } from '../catalog/api';
import type { DressRecord } from '../dresses/api';
import type { PaymentMethodRecord } from '../paymentMethods/api';

type Props = {
  open: boolean;
  title: string;
  subtitle: string;
  loading: boolean;
  creatingNew: boolean;
  document: BookingDocumentRecord | null;
  customers: CustomerRecord[];
  departments: DepartmentRecord[];
  services: ServiceRecord[];
  dresses: DressRecord[];
  paymentMethods: PaymentMethodRecord[];
  error: string | null;
  saving: boolean;
  onClose: () => void;
  onSave: (payload: BookingDocumentPayload) => Promise<void>;
  onCreateCustomer: (payload: CustomerPayload) => Promise<CustomerRecord>;
  onCompleteLine: (lineId: string) => Promise<void>;
  onCancelLine: (lineId: string) => Promise<void>;
  onReverseRevenueLine: (lineId: string) => Promise<void>;
  onDeleteLine: (lineId: string) => Promise<void>;
  onUndoCancellation: (lineIds: string[]) => Promise<void>;
  onCancelFull?: () => void;
  mode?: 'edit' | 'cancel';
};

export function BookingEditorDialog({
  open,
  title,
  subtitle,
  loading,
  creatingNew,
  document,
  customers,
  departments,
  services,
  dresses,
  paymentMethods,
  error,
  saving,
  onClose,
  onSave,
  onCreateCustomer,
  onCompleteLine,
  onCancelLine,
  onReverseRevenueLine,
  onDeleteLine,
  onUndoCancellation,
  onCancelFull,
  mode,
}: Props) {
  return (
    <AppDialogShell open={open} onClose={onClose} title={title} subtitle={subtitle} maxWidth='xl'>
      {loading && !creatingNew ? (
        <Stack alignItems='center' justifyContent='center' sx={{ minHeight: 240 }}>
          <CircularProgress />
        </Stack>
      ) : (
        <BookingDocumentEditor
          customers={customers}
          departments={departments}
          services={services}
          dresses={dresses}
          paymentMethods={paymentMethods}
          document={document}
          error={error}
          saving={saving}
          onSave={onSave}
          onCancel={onClose}
          onCreateCustomer={onCreateCustomer}
          onCompleteLine={onCompleteLine}
          onCancelLine={onCancelLine}
          onReverseRevenueLine={onReverseRevenueLine}
          onDeleteLine={onDeleteLine}
          onUndoCancellation={onUndoCancellation}
          onCancelFull={onCancelFull}
          mode={mode}
        />
      )}
    </AppDialogShell>
  );
}
