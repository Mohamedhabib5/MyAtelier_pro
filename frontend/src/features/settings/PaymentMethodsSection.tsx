import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined';
import { Alert, Button, Chip, Stack, TextField, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';

import { SectionCard } from '../../components/SectionCard';
import { queryClient } from '../../lib/queryClient';
import { createPaymentMethod, listPaymentMethods, updatePaymentMethod, type PaymentMethodRecord } from '../paymentMethods/api';

type Props = {
  language: 'ar' | 'en';
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
};

function toText(language: 'ar' | 'en') {
  if (language === 'ar') {
    return {
      title: '\u0637\u0631\u0642 \u0627\u0644\u062f\u0641\u0639',
      subtitle: '\u0625\u062f\u0627\u0631\u0629 \u0637\u0631\u0642 \u0627\u0644\u062f\u0641\u0639 \u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645\u0629 \u0641\u064a \u0643\u0644 \u0639\u0645\u0644\u064a\u0627\u062a \u0627\u0644\u0642\u0628\u0636 \u0648\u0627\u0644\u0635\u0631\u0641.',
      createName: '\u0627\u0633\u0645 \u0637\u0631\u064a\u0642\u0629 \u0627\u0644\u062f\u0641\u0639',
      createButton: '\u0625\u0636\u0627\u0641\u0629 \u0637\u0631\u064a\u0642\u0629',
      name: '\u0627\u0644\u0627\u0633\u0645',
      code: '\u0627\u0644\u0643\u0648\u062f',
      order: '\u0627\u0644\u062a\u0631\u062a\u064a\u0628',
      status: '\u0627\u0644\u062d\u0627\u0644\u0629',
      active: '\u0641\u0639\u0651\u0627\u0644\u0629',
      inactive: '\u0645\u0639\u0637\u0651\u0644\u0629',
      save: '\u062d\u0641\u0638',
      activate: '\u062a\u0641\u0639\u064a\u0644',
      deactivate: '\u062a\u0639\u0637\u064a\u0644',
      created: '\u062a\u0645\u062a \u0625\u0636\u0627\u0641\u0629 \u0637\u0631\u064a\u0642\u0629 \u0627\u0644\u062f\u0641\u0639 \u0628\u0646\u062c\u0627\u062d.',
      updated: '\u062a\u0645 \u062a\u062d\u062f\u064a\u062b \u0637\u0631\u064a\u0642\u0629 \u0627\u0644\u062f\u0641\u0639 \u0628\u0646\u062c\u0627\u062d.',
      empty: '\u0644\u0627 \u062a\u0648\u062c\u062f \u0637\u0631\u0642 \u062f\u0641\u0639 \u0645\u062d\u0641\u0648\u0638\u0629 \u062d\u062a\u0649 \u0627\u0644\u0622\u0646.',
    };
  }
  return {
    title: 'Payment methods',
    subtitle: 'Manage methods used by all incoming and outgoing money operations.',
    createName: 'Method name',
    createButton: 'Add method',
    name: 'Name',
    code: 'Code',
    order: 'Order',
    status: 'Status',
    active: 'Active',
    inactive: 'Inactive',
    save: 'Save',
    activate: 'Activate',
    deactivate: 'Deactivate',
    created: 'Payment method created successfully.',
    updated: 'Payment method updated successfully.',
    empty: 'No payment methods have been saved yet.',
  };
}

type DraftState = {
  name: string;
  displayOrder: string;
};

export function PaymentMethodsSection({ language, onSuccess, onError }: Props) {
  const text = useMemo(() => toText(language), [language]);
  const [newName, setNewName] = useState('');
  const [drafts, setDrafts] = useState<Record<string, DraftState>>({});
  const methodsQuery = useQuery({
    queryKey: ['payment-methods', 'all'],
    queryFn: () => listPaymentMethods('all'),
  });

  useEffect(() => {
    const next: Record<string, DraftState> = {};
    for (const item of methodsQuery.data ?? []) {
      next[item.id] = { name: item.name, displayOrder: String(item.display_order) };
    }
    setDrafts(next);
  }, [methodsQuery.data]);

  const createMutation = useMutation({
    mutationFn: createPaymentMethod,
    onSuccess: async () => {
      setNewName('');
      await queryClient.invalidateQueries({ queryKey: ['payment-methods'] });
      onSuccess(text.created);
    },
    onError: (error: Error) => onError(error.message),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: { name?: string; display_order?: number; is_active?: boolean } }) =>
      updatePaymentMethod(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['payment-methods'] });
      onSuccess(text.updated);
    },
    onError: (error: Error) => onError(error.message),
  });

  const rows = methodsQuery.data ?? [];

  function rowDraft(item: PaymentMethodRecord): DraftState {
    return drafts[item.id] ?? { name: item.name, displayOrder: String(item.display_order) };
  }

  return (
    <SectionCard title={text.title} subtitle={text.subtitle}>
      <Stack spacing={2}>
        {methodsQuery.error instanceof Error ? <Alert severity='error'>{methodsQuery.error.message}</Alert> : null}

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
          <TextField label={text.createName} value={newName} onChange={(event) => setNewName(event.target.value)} fullWidth />
          <Button
            variant='contained'
            startIcon={<AddOutlinedIcon />}
            disabled={!newName.trim() || createMutation.isPending}
            onClick={() => void createMutation.mutateAsync({ name: newName.trim() })}
          >
            {text.createButton}
          </Button>
        </Stack>

        {!rows.length ? (
          <Typography variant='body2' color='text.secondary'>
            {text.empty}
          </Typography>
        ) : (
          <Stack spacing={1.5}>
            {rows.map((item) => {
              const draft = rowDraft(item);
              const nextOrder = Number(draft.displayOrder || item.display_order);
              const canSave = draft.name.trim() && Number.isFinite(nextOrder) && nextOrder > 0;
              return (
                <Stack key={item.id} spacing={1}>
                  <Stack direction={{ xs: 'column', lg: 'row' }} spacing={1.5} alignItems={{ lg: 'center' }}>
                    <TextField
                      label={text.name}
                      value={draft.name}
                      onChange={(event) =>
                        setDrafts((current) => ({
                          ...current,
                          [item.id]: { ...rowDraft(item), name: event.target.value },
                        }))
                      }
                      sx={{ minWidth: 260 }}
                    />
                    <TextField label={text.code} value={item.code} InputProps={{ readOnly: true }} sx={{ minWidth: 180 }} />
                    <TextField
                      label={text.order}
                      type='number'
                      value={draft.displayOrder}
                      onChange={(event) =>
                        setDrafts((current) => ({
                          ...current,
                          [item.id]: { ...rowDraft(item), displayOrder: event.target.value },
                        }))
                      }
                      sx={{ minWidth: 130 }}
                    />
                    <Stack direction='row' spacing={1} alignItems='center'>
                      <Typography variant='body2' color='text.secondary'>
                        {text.status}:
                      </Typography>
                      <Chip size='small' color={item.is_active ? 'success' : 'default'} label={item.is_active ? text.active : text.inactive} />
                    </Stack>
                    <Button
                      variant='outlined'
                      startIcon={<SaveOutlinedIcon />}
                      disabled={!canSave || updateMutation.isPending}
                      onClick={() =>
                        void updateMutation.mutateAsync({
                          id: item.id,
                          payload: {
                            name: draft.name.trim(),
                            display_order: Math.max(1, Math.floor(nextOrder)),
                          },
                        })
                      }
                    >
                      {text.save}
                    </Button>
                    <Button
                      variant='outlined'
                      disabled={updateMutation.isPending}
                      onClick={() =>
                        void updateMutation.mutateAsync({
                          id: item.id,
                          payload: { is_active: !item.is_active },
                        })
                      }
                    >
                      {item.is_active ? text.deactivate : text.activate}
                    </Button>
                  </Stack>
                </Stack>
              );
            })}
          </Stack>
        )}
      </Stack>
    </SectionCard>
  );
}
