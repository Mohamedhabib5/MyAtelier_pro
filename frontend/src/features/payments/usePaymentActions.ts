import { useMutation } from '@tanstack/react-query';

import { queryClient } from '../../lib/queryClient';
import { createPayment, updatePayment, voidPayment, type PaymentDocumentPayload, type PaymentDocumentSummaryRecord, type PaymentTargetSearchRecord } from './api';

async function invalidatePaymentViews() {
  await Promise.all([
    queryClient.invalidateQueries({ queryKey: ['payments'] }),
    queryClient.invalidateQueries({ queryKey: ['bookings'] }),
    queryClient.invalidateQueries({ queryKey: ['dashboard'] }),
    queryClient.invalidateQueries({ queryKey: ['reports'] }),
    queryClient.invalidateQueries({ queryKey: ['accounting'] }),
    queryClient.invalidateQueries({ queryKey: ['exports'] }),
  ]);
}

type Params = {
  editingPaymentId: string | null;
  voidingPayment: PaymentDocumentSummaryRecord | null;
  voidDate: string;
  voidReason: string;
  voidOverrideLock: boolean;
  voidOverrideReason: string;
  setError: (value: string | null) => void;
  closeBuilder: () => void;
  closeVoidDialog: () => void;
  setPendingUpdateOverridePayload: (value: PaymentDocumentPayload | null) => void;
  setSelectedTarget: (value: PaymentTargetSearchRecord | null) => void;
  setEditingPaymentId: (value: string | null) => void;
};

export function usePaymentActions({
  editingPaymentId,
  voidingPayment,
  voidDate,
  voidReason,
  voidOverrideLock,
  voidOverrideReason,
  setError,
  closeBuilder,
  closeVoidDialog,
  setPendingUpdateOverridePayload,
  setSelectedTarget,
  setEditingPaymentId,
}: Params) {
  const createMutation = useMutation({
    mutationFn: createPayment,
    onSuccess: async () => {
      await invalidatePaymentViews();
      closeBuilder();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const updateMutation = useMutation({
    mutationFn: ({ paymentDocumentId, payload }: { paymentDocumentId: string; payload: PaymentDocumentPayload }) => updatePayment(paymentDocumentId, payload),
    onSuccess: async () => {
      await invalidatePaymentViews();
      closeBuilder();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const voidMutation = useMutation({
    mutationFn: ({ paymentDocumentId, payload }: { paymentDocumentId: string; payload: { void_date: string; reason: string; override_lock?: boolean; override_reason?: string | null } }) =>
      voidPayment(paymentDocumentId, payload),
    onSuccess: async () => {
      await invalidatePaymentViews();
      closeVoidDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  function startNewFromTarget(target: PaymentTargetSearchRecord) {
    setError(null);
    setEditingPaymentId(null);
    setSelectedTarget(target);
  }

  function openEditDocument(payment: PaymentDocumentSummaryRecord) {
    setError(null);
    setEditingPaymentId(payment.id);
    setSelectedTarget({
      kind: 'customer',
      id: payment.customer_id,
      label: payment.customer_name,
      customer_id: payment.customer_id,
      customer_name: payment.customer_name,
    });
  }

  async function handleSave(payload: PaymentDocumentPayload) {
    setError(null);
    if (editingPaymentId) {
      try {
        await updateMutation.mutateAsync({ paymentDocumentId: editingPaymentId, payload });
      } catch (mutationError) {
        const message = mutationError instanceof Error ? mutationError.message : '';
        if (!message.includes('period is locked')) throw mutationError;
        setPendingUpdateOverridePayload(payload);
      }
      return;
    }
    await createMutation.mutateAsync(payload);
  }

  async function submitVoid() {
    if (!voidingPayment) return;
    await voidMutation.mutateAsync({
      paymentDocumentId: voidingPayment.id,
      payload: {
        void_date: voidDate,
        reason: voidReason,
        override_lock: voidOverrideLock || undefined,
        override_reason: voidOverrideLock ? voidOverrideReason || null : undefined,
      },
    });
  }

  async function confirmUpdateOverride(reason: string, payload: PaymentDocumentPayload | null) {
    if (!editingPaymentId || !payload) return;
    await updateMutation.mutateAsync({
      paymentDocumentId: editingPaymentId,
      payload: {
        ...payload,
        override_lock: true,
        override_reason: reason,
      },
    });
    setPendingUpdateOverridePayload(null);
  }

  return {
    startNewFromTarget,
    openEditDocument,
    handleSave,
    submitVoid,
    confirmUpdateOverride,
    saving: createMutation.isPending || updateMutation.isPending,
  };
}
