import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined';
import { Alert, Button, Chip, Stack, TextField, Typography, Autocomplete } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';

import { StableNumericField } from '../../components/inputs/StableNumericField';
import { SectionCard } from '../../components/SectionCard';
import { queryClient } from '../../lib/queryClient';
import { createPaymentMethod, listPaymentMethods, updatePaymentMethod, type PaymentMethodRecord } from '../paymentMethods/api';
import { getChartOfAccounts } from '../accounting/api';

type Props = {
  language: 'ar' | 'en';
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
};

function toText(language: 'ar' | 'en') {
  if (language === 'ar') {
    return {
      title: 'طرق الدفع والتحصيل (الخزن)',
      subtitle: 'إدارة طرق الدفع وربط كل طريقة بالحساب المحاسبي المقابل لها في شجرة الحسابات (مثل الصندوق الرئيسي، البنك، إلخ).',
      createName: 'اسم طريقة الدفع',
      createButton: 'إضافة طريقة',
      name: 'الاسم',
      code: 'الكود',
      order: 'الترتيب',
      status: 'الحالة',
      active: 'فعّالة',
      inactive: 'معطّلة',
      save: 'حفظ',
      activate: 'تفعيل',
      deactivate: 'تعطيل',
      created: 'تمت إضافة طريقة الدفع بنجاح.',
      updated: 'تم تحديث طريقة الدفع بنجاح.',
      empty: 'لا توجد طرق دفع محفوظة حتى الآن.',
      linkedAccount: 'الحساب المحاسبي المرتبط',
      selectAccount: 'اختر حساباً للترحيل',
    };
  }
  return {
    title: 'Payment Methods (Safes)',
    subtitle: 'Manage payment methods and link each to its corresponding account in the Chart of Accounts (e.g. Main Safe, Bank, etc).',
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
    linkedAccount: 'Linked Account',
    selectAccount: 'Select posting account',
  };
}

type DraftState = {
  name: string;
  displayOrder: string;
  linkedAccountId: string;
};

export function PaymentMethodsSection({ language, onSuccess, onError }: Props) {
  const text = useMemo(() => toText(language), [language]);
  const isAr = language === 'ar';
  const [newName, setNewName] = useState('');
  const [newLinkedAccountId, setNewLinkedAccountId] = useState<string>('');
  const [drafts, setDrafts] = useState<Record<string, DraftState>>({});

  const methodsQuery = useQuery({
    queryKey: ['payment-methods', 'all'],
    queryFn: () => listPaymentMethods('all'),
  });

  const chartQuery = useQuery({
    queryKey: ['chart-of-accounts'],
    queryFn: getChartOfAccounts,
  });

  // Filter posting-eligible accounts
  const postingAccounts = useMemo(() => {
    return (chartQuery.data ?? []).filter((acc) => acc.is_active && acc.allows_posting);
  }, [chartQuery.data]);

  useEffect(() => {
    const next: Record<string, DraftState> = {};
    for (const item of methodsQuery.data ?? []) {
      next[item.id] = {
        name: item.name,
        displayOrder: String(item.display_order),
        linkedAccountId: item.linked_account_id ?? '',
      };
    }
    setDrafts(next);
  }, [methodsQuery.data]);

  const createMutation = useMutation({
    mutationFn: createPaymentMethod,
    onSuccess: async () => {
      setNewName('');
      setNewLinkedAccountId('');
      await queryClient.invalidateQueries({ queryKey: ['payment-methods'] });
      onSuccess(text.created);
    },
    onError: (error: Error) => onError(error.message),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: { name?: string; display_order?: number; is_active?: boolean; linked_account_id?: string | null } }) =>
      updatePaymentMethod(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['payment-methods'] });
      onSuccess(text.updated);
    },
    onError: (error: Error) => onError(error.message),
  });

  const rows = methodsQuery.data ?? [];

  function rowDraft(item: PaymentMethodRecord): DraftState {
    return drafts[item.id] ?? { name: item.name, displayOrder: String(item.display_order), linkedAccountId: item.linked_account_id ?? '' };
  }

  const selectedNewAccount = postingAccounts.find((acc) => acc.id === newLinkedAccountId) || null;

  return (
    <SectionCard title={text.title} subtitle={text.subtitle}>
      <Stack spacing={2}>
        {methodsQuery.error instanceof Error ? <Alert severity='error'>{methodsQuery.error.message}</Alert> : null}

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5} alignItems="center">
          <TextField label={text.createName} value={newName} onChange={(event) => setNewName(event.target.value)} fullWidth />
          <Autocomplete
            options={postingAccounts}
            getOptionLabel={(option) => `${option.code} - ${option.name}`}
            value={selectedNewAccount}
            onChange={(_, newValue) => setNewLinkedAccountId(newValue ? newValue.id : '')}
            renderInput={(params) => (
              <TextField {...params} label={text.linkedAccount} variant="outlined" />
            )}
            sx={{ minWidth: 280, width: { xs: '100%', md: 'auto' } }}
          />
          <Button
            variant='contained'
            startIcon={<AddOutlinedIcon />}
            disabled={!newName.trim() || createMutation.isPending}
            onClick={() => void createMutation.mutateAsync({ name: newName.trim(), linked_account_id: newLinkedAccountId || null })}
            sx={{ height: 56, px: 3, flexShrink: 0 }}
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
              const selectedRowAccount = postingAccounts.find((acc) => acc.id === draft.linkedAccountId) || null;
              
              return (
                <Stack key={item.id} spacing={1} sx={{ p: 1.5, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
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
                      sx={{ flexGrow: 1, minWidth: 200 }}
                    />
                    <TextField label={text.code} value={item.code} InputProps={{ readOnly: true }} sx={{ minWidth: 120 }} />
                    
                    <Autocomplete
                      options={postingAccounts}
                      getOptionLabel={(option) => `${option.code} - ${option.name}`}
                      value={selectedRowAccount}
                      onChange={(_, newValue) => {
                        setDrafts((current) => ({
                          ...current,
                          [item.id]: { ...rowDraft(item), linkedAccountId: newValue ? newValue.id : '' },
                        }));
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label={text.linkedAccount} variant="outlined" />
                      )}
                      sx={{ minWidth: 260 }}
                    />

                    <StableNumericField
                      label={text.order}
                      value={draft.displayOrder}
                      onValueChange={(value) =>
                        setDrafts((current) => ({
                          ...current,
                          [item.id]: { ...rowDraft(item), displayOrder: value },
                        }))
                      }
                      sx={{ minWidth: 80 }}
                      allowDecimal={false}
                    />
                    
                    <Stack direction='row' spacing={1} alignItems='center' sx={{ minWidth: 100 }}>
                      <Typography variant='body2' color='text.secondary'>
                        {text.status}:
                      </Typography>
                      <Chip size='small' color={item.is_active ? 'success' : 'default'} label={item.is_active ? text.active : text.inactive} />
                    </Stack>
                    
                    <Stack direction="row" spacing={1}>
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
                              linked_account_id: draft.linkedAccountId || null,
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
                </Stack>
              );
            })}
          </Stack>
        )}
      </Stack>
    </SectionCard>
  );
}
