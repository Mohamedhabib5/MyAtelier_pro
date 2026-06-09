import { useMutation } from '@tanstack/react-query';
import { queryClient } from '../../lib/queryClient';
import { 
  createDisbursement, 
  updateDisbursement, 
  voidDisbursement, 
  deleteDisbursement, 
  type DisbursementCreatePayload,
  type DisbursementUpdatePayload, 
  type DisbursementVoucherRecord 
} from './api';

async function invalidateDisbursementViews() {
  await Promise.all([
    queryClient.invalidateQueries({ queryKey: ['disbursements'] }),
    queryClient.invalidateQueries({ queryKey: ['payments'] }),
    queryClient.invalidateQueries({ queryKey: ['dashboard'] }),
    queryClient.invalidateQueries({ queryKey: ['reports'] }),
    queryClient.invalidateQueries({ queryKey: ['accounting'] }),
    queryClient.invalidateQueries({ queryKey: ['exports'] }),
  ]);
}

type Params = {
  editingVoucherId: string | null;
  voidingVoucher: DisbursementVoucherRecord | null;
  voidDate: string;
  voidReason: string;
  voidOverrideLock: boolean;
  voidOverrideReason: string;
  setError: (value: string | null) => void;
  closeEditor: () => void;
  closeVoidDialog: () => void;
  setPendingUpdateOverridePayload: (value: DisbursementUpdatePayload | null) => void;
};

export function useDisbursementActions({
  editingVoucherId,
  voidingVoucher,
  voidDate,
  voidReason,
  voidOverrideLock,
  voidOverrideReason,
  setError,
  closeEditor,
  closeVoidDialog,
  setPendingUpdateOverridePayload,
}: Params) {
  const createMutation = useMutation({
    mutationFn: createDisbursement,
    onSuccess: async () => {
      await invalidateDisbursementViews();
      closeEditor();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: DisbursementUpdatePayload }) => updateDisbursement(id, payload),
    onSuccess: async () => {
      await invalidateDisbursementViews();
      closeEditor();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  const voidMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: { void_date: string; reason: string; override_lock?: boolean; override_reason?: string | null } }) =>
      voidDisbursement(id, payload),
    onSuccess: async () => {
      await invalidateDisbursementViews();
      closeVoidDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteDisbursement,
    onSuccess: async () => {
      await invalidateDisbursementViews();
      closeEditor();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  async function handleSave(payload: DisbursementCreatePayload | DisbursementUpdatePayload) {
    setError(null);
    if (editingVoucherId) {
      try {
        await updateMutation.mutateAsync({ id: editingVoucherId, payload: payload as DisbursementUpdatePayload });
      } catch (mutationError) {
        const message = mutationError instanceof Error ? mutationError.message : '';
        if (!message.includes('period is locked')) throw mutationError;
        setPendingUpdateOverridePayload(payload as DisbursementUpdatePayload);
      }
      return;
    }
    await createMutation.mutateAsync(payload as DisbursementCreatePayload);
  }

  async function submitVoid() {
    if (!voidingVoucher) return;
    await voidMutation.mutateAsync({
      id: voidingVoucher.id,
      payload: {
        void_date: voidDate,
        reason: voidReason,
        override_lock: voidOverrideLock || undefined,
        override_reason: voidOverrideLock ? voidOverrideReason || null : undefined,
      },
    });
  }

  async function confirmUpdateOverride(reason: string, payload: DisbursementUpdatePayload | null) {
    if (!editingVoucherId || !payload) return;
    await updateMutation.mutateAsync({
      id: editingVoucherId,
      payload: {
        ...payload,
        override_lock: true,
        override_reason: reason,
      },
    });
    setPendingUpdateOverridePayload(null);
  }

  async function handleDeleteDisbursement(voucherId: string) {
    setError(null);
    await deleteMutation.mutateAsync(voucherId);
  }

  return {
    handleSave,
    submitVoid,
    confirmUpdateOverride,
    handleDeleteDisbursement,
    saving: createMutation.isPending || updateMutation.isPending || deleteMutation.isPending,
  };
}
