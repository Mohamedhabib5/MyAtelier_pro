import { useMutation } from '@tanstack/react-query';

import { queryClient } from '../../lib/queryClient';
import { createCustomer, type CustomerPayload, type CustomerRecord } from '../customers/api';
import { cancelBooking, cancelBookingLine, completeBookingLine, createBooking, reverseBookingLineRevenue, updateBooking, deleteBooking, deleteBookingLine, undoCancellation, type BookingDocumentPayload, type BookingCancellationPayload } from './api';

async function invalidateViews() {
  await Promise.all([
    queryClient.invalidateQueries({ queryKey: ['bookings'] }),
    queryClient.invalidateQueries({ queryKey: ['calendar-events'] }),
    queryClient.invalidateQueries({ queryKey: ['payments'] }),
    queryClient.invalidateQueries({ queryKey: ['dashboard', 'finance'] }),
    queryClient.invalidateQueries({ queryKey: ['reports', 'overview'] }),
    queryClient.invalidateQueries({ queryKey: ['accounting'] }),
    queryClient.invalidateQueries({ queryKey: ['exports'] }),
  ]);
}

type Params = {
  creatingNew: boolean;
  editingBookingId: string | null;
  reverseOverrideLineId: string | null;
  setError: (value: string | null) => void;
  setReverseOverrideLineId: (value: string | null) => void;
  setPendingCancelPayload: (value: { bookingId: string; lineId?: string; payload: BookingCancellationPayload } | null) => void;
  closeEditor: () => void;
};

export function useBookingActions({
  creatingNew,
  editingBookingId,
  reverseOverrideLineId,
  setError,
  setReverseOverrideLineId,
  setPendingCancelPayload,
  closeEditor,
}: Params) {
  const createMutation = useMutation({
    mutationFn: createBooking,
    onSuccess: async () => {
      await invalidateViews();
      closeEditor();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const updateMutation = useMutation({
    mutationFn: ({ bookingId, payload }: { bookingId: string; payload: BookingDocumentPayload }) => updateBooking(bookingId, payload),
    onSuccess: async () => {
      await invalidateViews();
      closeEditor();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const completeMutation = useMutation({
    mutationFn: ({ bookingId, lineId }: { bookingId: string; lineId: string }) => completeBookingLine(bookingId, lineId),
    onSuccess: async (document) => {
      await invalidateViews();
      queryClient.setQueryData(['bookings', document.id], document);
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const cancelWorkflowMutation = useMutation({
    mutationFn: ({ bookingId, payload }: { bookingId: string; payload: BookingCancellationPayload }) => cancelBooking(bookingId, payload),
    onSuccess: async (document) => {
      await invalidateViews();
      queryClient.setQueryData(['bookings', document.id], document);
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const cancelLineMutation = useMutation({
    mutationFn: ({ bookingId, lineId, payload }: { bookingId: string; lineId: string; payload: BookingCancellationPayload }) => cancelBookingLine(bookingId, lineId, payload),
    onSuccess: async (document) => {
      await invalidateViews();
      queryClient.setQueryData(['bookings', document.id], document);
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const reverseRevenueMutation = useMutation({
    mutationFn: ({ bookingId, lineId }: { bookingId: string; lineId: string }) => reverseBookingLineRevenue(bookingId, lineId),
    onSuccess: async (document) => {
      await invalidateViews();
      queryClient.setQueryData(['bookings', document.id], document);
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const deleteMutation = useMutation({
    mutationFn: deleteBooking,
    onSuccess: async () => {
      await invalidateViews();
      closeEditor();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const deleteLineMutation = useMutation({
    mutationFn: ({ bookingId, lineId }: { bookingId: string; lineId: string }) => deleteBookingLine(bookingId, lineId),
    onSuccess: async (document) => {
      await invalidateViews();
      queryClient.setQueryData(['bookings', document.id], document);
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const undoCancelMutation = useMutation({
    mutationFn: ({ bookingId, lineIds }: { bookingId: string; lineIds?: string[] }) => undoCancellation(bookingId, lineIds),
    onSuccess: async (document) => {
      await invalidateViews();
      queryClient.setQueryData(['bookings', document.id], document);
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });
  const createCustomerMutation = useMutation({
    mutationFn: createCustomer,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['customers'] });
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  async function handleSave(payload: BookingDocumentPayload) {
    setError(null);
    if (creatingNew) {
      await createMutation.mutateAsync(payload);
      return;
    }
    if (editingBookingId) {
      await updateMutation.mutateAsync({ bookingId: editingBookingId, payload });
    }
  }

  async function handleCreateCustomer(payload: CustomerPayload): Promise<CustomerRecord> {
    return await createCustomerMutation.mutateAsync(payload);
  }

  async function handleCompleteLine(lineId: string) {
    if (!editingBookingId) return;
    await completeMutation.mutateAsync({ bookingId: editingBookingId, lineId });
    await queryClient.invalidateQueries({ queryKey: ['bookings', editingBookingId] });
  }

  async function handleCancelLine(lineId: string, payload?: BookingCancellationPayload) {
    if (!editingBookingId) return;
    const finalPayload = payload ?? { reason: 'Corrective Delete', refund_amount: 0, transfer_amount: 0 };
    try {
      await cancelLineMutation.mutateAsync({ bookingId: editingBookingId, lineId, payload: finalPayload });
      await queryClient.invalidateQueries({ queryKey: ['bookings', editingBookingId] });
    } catch (mutationError) {
      const message = mutationError instanceof Error ? mutationError.message : '';
      if (!message.includes('period is locked')) throw mutationError;
      setPendingCancelPayload({ bookingId: editingBookingId, lineId, payload: finalPayload });
    }
  }

  async function handleCancelWorkflow(bookingId: string, payload: BookingCancellationPayload): Promise<boolean> {
    setError(null);
    try {
      await cancelWorkflowMutation.mutateAsync({ bookingId, payload });
      return true;
    } catch (mutationError) {
      const message = mutationError instanceof Error ? mutationError.message : '';
      if (!message.includes('period is locked')) throw mutationError;
      setPendingCancelPayload({ bookingId, payload });
      return false;
    }
  }

  async function handleConfirmCancelOverride(reason: string, pending: { bookingId: string; lineId?: string; payload: BookingCancellationPayload } | null) {
    if (!pending) return;
    const payloadWithOverride = { ...pending.payload, override_lock: true, override_reason: reason };
    if (pending.lineId) {
      await cancelLineMutation.mutateAsync({ bookingId: pending.bookingId, lineId: pending.lineId, payload: payloadWithOverride });
    } else {
      await cancelWorkflowMutation.mutateAsync({ bookingId: pending.bookingId, payload: payloadWithOverride });
    }
    await invalidateViews();
    if (editingBookingId) {
      await queryClient.invalidateQueries({ queryKey: ['bookings', editingBookingId] });
    }
    setPendingCancelPayload(null);
  }

  async function handleReverseRevenueLine(lineId: string) {
    if (!editingBookingId) return;
    try {
      await reverseRevenueMutation.mutateAsync({ bookingId: editingBookingId, lineId });
      await queryClient.invalidateQueries({ queryKey: ['bookings', editingBookingId] });
    } catch (mutationError) {
      const message = mutationError instanceof Error ? mutationError.message : '';
      if (!message.includes('period is locked')) throw mutationError;
      setReverseOverrideLineId(lineId);
    }
  }

  async function handleConfirmRevenueOverride(reason: string) {
    if (!editingBookingId || !reverseOverrideLineId) return;
    await reverseBookingLineRevenue(editingBookingId, reverseOverrideLineId, { overrideLock: true, overrideReason: reason });
    await invalidateViews();
    await queryClient.invalidateQueries({ queryKey: ['bookings', editingBookingId] });
    setReverseOverrideLineId(null);
  }

  async function handleDeleteBooking(bookingId: string) {
    setError(null);
    await deleteMutation.mutateAsync(bookingId);
  }

  async function handleDeleteLine(lineId: string) {
    if (!editingBookingId) return;
    setError(null);
    await deleteLineMutation.mutateAsync({ bookingId: editingBookingId, lineId });
  }

  async function handleUndoCancellation(lineIds?: string[]) {
    if (!editingBookingId) return;
    setError(null);
    await undoCancelMutation.mutateAsync({ bookingId: editingBookingId, lineIds });
  }

  return {
    handleSave,
    handleCreateCustomer,
    handleCompleteLine,
    handleCancelLine,
    handleReverseRevenueLine,
    handleConfirmRevenueOverride,
    handleCancelWorkflow,
    handleConfirmCancelOverride,
    handleDeleteBooking,
    handleDeleteLine,
    handleUndoCancellation,
    saving: createMutation.isPending || updateMutation.isPending || cancelWorkflowMutation.isPending || cancelLineMutation.isPending || deleteMutation.isPending || deleteLineMutation.isPending || undoCancelMutation.isPending,
  };
}
