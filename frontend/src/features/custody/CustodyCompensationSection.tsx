import { Button, MenuItem, Stack, TextField } from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';

import { StableNumericField } from '../../components/inputs/StableNumericField';
import { SectionCard } from '../../components/SectionCard';
import { queryClient } from '../../lib/queryClient';
import type { PaymentMethodRecord } from '../paymentMethods/api';
import { collectCustodyCompensation, type CustodyCaseRecord } from './api';
import { buildCustodyCaseOptionLabel } from './presentation';

type CustodyCompensationSectionProps = {
  caseOptions: CustodyCaseRecord[];
  language: string;
  selectedLanguage: 'ar' | 'en';
  setMessage: (value: string | null) => void;
  setError: (value: string | null) => void;
  paymentMethods: PaymentMethodRecord[];
  showCard?: boolean;
  onCollected?: () => void;
  text: {
    title: string;
    subtitle: string;
    targetCase: string;
    amount: string;
    paymentMethod: string;
    date: string;
    note: string;
    apply: string;
  };
};

export function CustodyCompensationSection({
  caseOptions,
  language,
  selectedLanguage,
  setMessage,
  setError,
  paymentMethods,
  showCard = true,
  onCollected,
  text,
}: CustodyCompensationSectionProps) {
  const [compCaseId, setCompCaseId] = useState('');
  const [compAmount, setCompAmount] = useState('');
  const [compPaymentMethodId, setCompPaymentMethodId] = useState('');
  const [compDate, setCompDate] = useState(new Date().toISOString().slice(0, 10));
  const [compNote, setCompNote] = useState('');
  useEffect(() => {
    if (!paymentMethods.length) return;
    if (compPaymentMethodId && paymentMethods.some((item) => item.id === compPaymentMethodId)) return;
    setCompPaymentMethodId(paymentMethods[0].id);
  }, [compPaymentMethodId, paymentMethods]);
  const compensationMutation = useMutation({
    mutationFn: ({
      caseId,
      amountValue,
      dateValue,
      noteValue,
      paymentMethodId,
    }: {
      caseId: string;
      amountValue: number;
      dateValue: string;
      noteValue: string;
      paymentMethodId: string;
    }) =>
      collectCustodyCompensation(caseId, {
        amount: amountValue,
        payment_date: dateValue,
        note: noteValue || null,
        payment_method_id: paymentMethodId,
      }),
    onSuccess: async () => {
      setMessage(language === 'ar' ? 'تم تحصيل تعويض العهدة وربطه ماليًا بنجاح.' : 'Custody compensation collected successfully.');
      setError(null);
      setCompAmount('');
      setCompNote('');
      await queryClient.invalidateQueries({ queryKey: ['custody', 'cases'] });
      onCollected?.();
    },
    onError: (mutationError: Error) => {
      setError(mutationError.message);
      setMessage(null);
    },
  });

  const form = (
    <Stack spacing={2}>
      <TextField select label={text.targetCase} value={compCaseId} onChange={(event) => setCompCaseId(event.target.value)}>
        {caseOptions.map((item) => (
          <MenuItem key={item.id} value={item.id}>
            {buildCustodyCaseOptionLabel(item, selectedLanguage)}
          </MenuItem>
        ))}
      </TextField>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
        <StableNumericField label={text.amount} value={compAmount} onValueChange={setCompAmount} fullWidth />
        <TextField select label={text.paymentMethod} value={compPaymentMethodId} onChange={(event) => setCompPaymentMethodId(event.target.value)} fullWidth>
          {paymentMethods.map((method) => (
            <MenuItem key={method.id} value={method.id}>
              {method.name}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          label={text.date}
          value={compDate}
          type='date'
          onChange={(event) => setCompDate(event.target.value)}
          InputLabelProps={{ shrink: true }}
          fullWidth
        />
      </Stack>
      <TextField label={text.note} value={compNote} onChange={(event) => setCompNote(event.target.value)} multiline minRows={2} />
      <Button
        variant='outlined'
        fullWidth
        disabled={!compCaseId || !compAmount || Number(compAmount) <= 0 || !compPaymentMethodId || compensationMutation.isPending}
        onClick={() => {
          if (!compCaseId || !compAmount || Number(compAmount) <= 0) return;
          void compensationMutation.mutateAsync({
            caseId: compCaseId,
            amountValue: Number(compAmount),
            dateValue: compDate,
            noteValue: compNote,
            paymentMethodId: compPaymentMethodId,
          });
        }}
      >
        {text.apply}
      </Button>
    </Stack>
  );

  if (!showCard) {
    return form;
  }

  return (
    <SectionCard title={text.title} subtitle={text.subtitle}>
      {form}
    </SectionCard>
  );
}
