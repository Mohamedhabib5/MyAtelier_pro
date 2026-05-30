import { useState, useCallback } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { archiveDress, createDress, listDresses, restoreDress, updateDress, type DressRecord } from '../api';
import { queryClient } from '../../../lib/queryClient';
import { type DressFormState } from '../DressFormDialog';

export function emptyForm(): DressFormState {
  return { code: '', name: '', dress_type_id: '', purchase_date: '', status: 'available', description: '', image_path: '', is_active: true };
}

export function useDressesState() {
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingDress, setEditingDress] = useState<DressRecord | null>(null);
  const [form, setForm] = useState<DressFormState>(emptyForm());
  const [statusFilter, setStatusFilter] = useState<'all' | 'available' | 'reserved' | 'with_customer' | 'maintenance'>('all');
  const [activeFilter, setActiveFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [lifecycleTarget, setLifecycleTarget] = useState<DressRecord | null>(null);
  const [lifecycleMode, setLifecycleMode] = useState<'archive' | 'restore'>('archive');
  const [lifecycleReason, setLifecycleReason] = useState('');
  const [deleteTarget, setDeleteTarget] = useState<DressRecord | null>(null);
  const [previewImage, setPreviewImage] = useState<string | null>(null);

  const dressesQuery = useQuery({ 
    queryKey: ['dresses', activeFilter], 
    queryFn: () => listDresses(activeFilter) 
  });

  const createMutation = useMutation({
    mutationFn: createDress,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['dresses'] });
      closeDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  const updateMutation = useMutation({
    mutationFn: ({ dressId, payload }: { dressId: string; payload: Parameters<typeof updateDress>[1] }) => updateDress(dressId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['dresses'] });
      closeDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  const lifecycleMutation = useMutation({
    mutationFn: ({ dress, archive, reason }: { dress: DressRecord; archive: boolean; reason?: string }) =>
      archive ? archiveDress(dress.id, reason) : restoreDress(dress.id, reason),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['dresses'] });
      closeLifecycleDialog();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  const closeDialog = useCallback(() => {
    setDialogOpen(false);
    setEditingDress(null);
    setForm(emptyForm());
  }, []);

  const openCreateDialog = useCallback(() => {
    setError(null);
    setEditingDress(null);
    setForm(emptyForm());
    setDialogOpen(true);
  }, []);

  const openEditDialog = useCallback((dress: DressRecord) => {
    setError(null);
    setEditingDress(dress);
    setForm({
      code: dress.code,
      name: dress.name,
      dress_type_id: dress.dress_type_id ?? '',
      purchase_date: dress.purchase_date ?? '',
      status: dress.status,
      description: dress.description ?? '',
      image_path: dress.image_path ?? '',
      is_active: dress.is_active,
    });
    setDialogOpen(true);
  }, []);

  const saveDress = useCallback(async () => {
    setError(null);
    const payload = {
      code: form.code,
      name: form.name,
      dress_type_id: form.dress_type_id,
      purchase_date: form.purchase_date || null,
      status: form.status,
      description: form.description,
      image_path: form.image_path || null,
      is_active: form.is_active,
    };
    if (editingDress) {
      await updateMutation.mutateAsync({ dressId: editingDress.id, payload });
      return;
    }
    await createMutation.mutateAsync(payload);
  }, [form, editingDress, updateMutation, createMutation]);

  const openLifecycleDialog = useCallback((dress: DressRecord, archive: boolean) => {
    setError(null);
    setLifecycleTarget(dress);
    setLifecycleMode(archive ? 'archive' : 'restore');
    setLifecycleReason('');
  }, []);

  const closeLifecycleDialog = useCallback(() => {
    setLifecycleTarget(null);
    setLifecycleReason('');
  }, []);

  const confirmLifecycle = useCallback(async () => {
    if (!lifecycleTarget) return;
    await lifecycleMutation.mutateAsync({
      dress: lifecycleTarget,
      archive: lifecycleMode === 'archive',
      reason: lifecycleReason || undefined,
    });
  }, [lifecycleTarget, lifecycleMode, lifecycleReason, lifecycleMutation]);

  const closeDeleteDialog = useCallback(() => {
    setDeleteTarget(null);
  }, []);

  return {
    error, setError,
    dialogOpen, setDialogOpen,
    editingDress, setEditingDress,
    form, setForm,
    statusFilter, setStatusFilter,
    activeFilter, setActiveFilter,
    lifecycleTarget, setLifecycleTarget,
    lifecycleMode, setLifecycleMode,
    lifecycleReason, setLifecycleReason,
    deleteTarget, setDeleteTarget,
    previewImage, setPreviewImage,
    dressesQuery,
    createMutation,
    updateMutation,
    lifecycleMutation,
    closeDialog,
    openCreateDialog,
    openEditDialog,
    saveDress,
    openLifecycleDialog,
    closeLifecycleDialog,
    confirmLifecycle,
    closeDeleteDialog,
  };
}
