import { useMutation } from '@tanstack/react-query';

import { queryClient } from '../../lib/queryClient';
import { createCustomer, type CustomerPayload, type CustomerRecord } from '../customers/api';
import { cancelBookingLine, completeBookingLine, createBooking, reverseBookingLineRevenue, updateBooking, type BookingDocumentPayload } from './api';

async function invalidateViews() {
  await Promise.all([
    queryClient.invalidateQueries({ queryKey: ['bookings'] }),
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
  closeEditor: () => void;
};

export function useBookingActions({
  creatingNew,
  editingBookingId,
  reverseOverrideLineId,
  setError,
  setReverseOverrideLineId,
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
  const cancelLineMutation = useMutation({
    mutationFn: ({ bookingId, lineId }: { bookingId: string; lineId: string }) => cancelBookingLine(bookingId, lineId),
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

  async function handleCancelLine(lineId: string) {
    if (!editingBookingId) return;
    await cancelLineMutation.mutateAsync({ bookingId: editingBookingId, lineId });
    await queryClient.invalidateQueries({ queryKey: ['bookings', editingBookingId] });
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

  return {
    handleSave,
    handleCreateCustomer,
    handleCompleteLine,
    handleCancelLine,
    handleReverseRevenueLine,
    handleConfirmRevenueOverride,
    saving: createMutation.isPending || updateMutation.isPending,
  };
}
