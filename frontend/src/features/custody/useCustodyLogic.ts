import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { applyCustodyAction, createCustodyCase, listCustodyCases, type CustodyCaseCreatePayload, type CustodyCaseView } from './api';
import { listPaymentMethods } from '../paymentMethods/api';
import { queryClient } from '../../lib/queryClient';
import { useCustodyText } from '../../text/custody';

export function useCustodyLogic(isArabic: boolean) {
  const custodyText = useCustodyText();
  const [caseView, setCaseView] = useState<CustodyCaseView>('open');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(25);
  const [targetCaseId, setTargetCaseId] = useState('');
  const [action, setAction] = useState('handover');
  const [actionDate, setActionDate] = useState(new Date().toISOString().slice(0, 10));
  const [actionNote, setActionNote] = useState('');
  const [actionCondition, setActionCondition] = useState('');
  const [returnOutcome, setReturnOutcome] = useState('good');
  const [compensationAmount, setCompensationAmount] = useState('');
  const [actionPaymentMethodId, setActionPaymentMethodId] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [actionDialogOpen, setActionDialogOpen] = useState(false);
  const [compensationDialogOpen, setCompensationDialogOpen] = useState(false);

  const casesQuery = useQuery({ 
    queryKey: ['custody', 'cases', caseView, page, pageSize], 
    queryFn: () => listCustodyCases(caseView, page + 1, pageSize) 
  });
  
  const allCasesQuery = useQuery({ queryKey: ['custody', 'cases', 'all'], queryFn: () => listCustodyCases('all') });
  const paymentMethodsQuery = useQuery({ queryKey: ['payment-methods', 'active'], queryFn: () => listPaymentMethods('active') });

  const createMutation = useMutation({
    mutationFn: async (payloads: CustodyCaseCreatePayload[]) => {
      for (const payload of payloads) await createCustodyCase(payload);
    },
    onSuccess: async () => {
      setMessage(custodyText.page.created);
      setError(null);
      await queryClient.invalidateQueries({ queryKey: ['custody', 'cases'] });
      setCreateDialogOpen(false);
    },
    onError: (mutationError: Error) => {
      setError(mutationError.message);
      setMessage(null);
    },
  });

  const actionMutation = useMutation({
    mutationFn: ({ caseId, actionValue, actionDateValue, noteValue, conditionValue, returnOutcomeValue, compensationAmountValue }: {
      caseId: string; actionValue: string; actionDateValue: string; noteValue: string; conditionValue: string; returnOutcomeValue: string | null; compensationAmountValue: string;
    }) =>
      applyCustodyAction(caseId, {
        action: actionValue,
        action_date: actionDateValue,
        note: noteValue || null,
        product_condition: conditionValue || null,
        return_outcome: returnOutcomeValue,
        compensation_amount: compensationAmountValue.trim() ? Number(compensationAmountValue) : null,
        payment_method_id: actionValue === 'customer_return' ? actionPaymentMethodId || null : null,
      }),
    onSuccess: async () => {
      setMessage(isArabic ? 'تم تحديث حالة الحيازة بنجاح.' : 'Custody case updated successfully.');
      setError(null);
      setActionDate(new Date().toISOString().slice(0, 10));
      setActionNote('');
      setActionCondition('');
      setReturnOutcome('good');
      setCompensationAmount('');
      await queryClient.invalidateQueries({ queryKey: ['custody', 'cases'] });
      await queryClient.invalidateQueries({ queryKey: ['payments'] });
      setActionDialogOpen(false);
    },
    onError: (mutationError: Error) => {
      setError(mutationError.message);
      setMessage(null);
    },
  });

  return {
    state: {
      caseView, setCaseView, page, setPage, pageSize, setPageSize,
      targetCaseId, setTargetCaseId, action, setAction, actionDate, setActionDate,
      actionNote, setActionNote, actionCondition, setActionCondition,
      returnOutcome, setReturnOutcome, compensationAmount, setCompensationAmount,
      actionPaymentMethodId, setActionPaymentMethodId, message, setMessage, error, setError,
      createDialogOpen, setCreateDialogOpen, actionDialogOpen, setActionDialogOpen, compensationDialogOpen, setCompensationDialogOpen
    },
    queries: { casesQuery, allCasesQuery, paymentMethodsQuery },
    mutations: { createMutation, actionMutation }
  };
}
