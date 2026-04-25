import { Button, MenuItem, Stack, TextField } from '@mui/material';

import { StableNumericField } from '../../components/inputs/StableNumericField';
import type { PaymentMethodRecord } from '../paymentMethods/api';
import type { CustodyCaseRecord } from './api';
import { CUSTODY_ACTION_OPTIONS, buildCustodyCaseOptionLabel, getCustodyActionLabel } from './presentation';

type Props = {
  caseOptions: CustodyCaseRecord[];
  selectedLanguage: 'ar' | 'en';
  targetCaseId: string;
  action: string;
  actionDate: string;
  actionCondition: string;
  actionNote: string;
  returnOutcome: string;
  compensationAmount: string;
  paymentMethodId: string;
  paymentMethods: PaymentMethodRecord[];
  actionLabel: string;
  actionDateLabel: string;
  targetCaseLabel: string;
  conditionLabel: string;
  noteLabel: string;
  returnOutcomeLabel: string;
  returnGoodLabel: string;
  returnDamagedLabel: string;
  compensationAmountLabel: string;
  paymentMethodLabel: string;
  applyLabel: string;
  isSubmitting: boolean;
  onTargetCaseChange: (value: string) => void;
  onActionChange: (value: string) => void;
  onActionDateChange: (value: string) => void;
  onConditionChange: (value: string) => void;
  onNoteChange: (value: string) => void;
  onReturnOutcomeChange: (value: string) => void;
  onCompensationAmountChange: (value: string) => void;
  onPaymentMethodChange: (value: string) => void;
  onApply: () => void;
};

export function CustodyActionForm({
  caseOptions,
  selectedLanguage,
  targetCaseId,
  action,
  actionDate,
  actionCondition,
  actionNote,
  returnOutcome,
  compensationAmount,
  paymentMethodId,
  paymentMethods,
  actionLabel,
  actionDateLabel,
  targetCaseLabel,
  conditionLabel,
  noteLabel,
  returnOutcomeLabel,
  returnGoodLabel,
  returnDamagedLabel,
  compensationAmountLabel,
  paymentMethodLabel,
  applyLabel,
  isSubmitting,
  onTargetCaseChange,
  onActionChange,
  onActionDateChange,
  onConditionChange,
  onNoteChange,
  onReturnOutcomeChange,
  onCompensationAmountChange,
  onPaymentMethodChange,
  onApply,
}: Props) {
  const isCustomerReturn = action === 'customer_return';

  return (
    <Stack spacing={2}>
      <TextField select label={targetCaseLabel} value={targetCaseId} onChange={(event) => onTargetCaseChange(event.target.value)}>
        {caseOptions.map((item) => (
          <MenuItem key={item.id} value={item.id}>
            {buildCustodyCaseOptionLabel(item, selectedLanguage)}
          </MenuItem>
        ))}
      </TextField>
      <TextField select label={actionLabel} value={action} onChange={(event) => onActionChange(event.target.value)}>
        {CUSTODY_ACTION_OPTIONS.map((option) => (
          <MenuItem key={option} value={option}>
            {getCustodyActionLabel(option, selectedLanguage)}
          </MenuItem>
        ))}
      </TextField>
      <TextField
        label={actionDateLabel}
        value={actionDate}
        type='date'
        onChange={(event) => onActionDateChange(event.target.value)}
        slotProps={{ inputLabel: { shrink: true } }}
        required
      />
      {isCustomerReturn ? (
        <TextField select label={returnOutcomeLabel} value={returnOutcome} onChange={(event) => onReturnOutcomeChange(event.target.value)}>
          <MenuItem value='good'>{returnGoodLabel}</MenuItem>
          <MenuItem value='damaged'>{returnDamagedLabel}</MenuItem>
        </TextField>
      ) : null}
      {isCustomerReturn ? (
        <TextField select label={paymentMethodLabel} value={paymentMethodId} onChange={(event) => onPaymentMethodChange(event.target.value)}>
          {paymentMethods.map((item) => (
            <MenuItem key={item.id} value={item.id}>
              {item.name}
            </MenuItem>
          ))}
        </TextField>
      ) : null}
      {isCustomerReturn && returnOutcome === 'damaged' ? (
        <StableNumericField label={compensationAmountLabel} value={compensationAmount} onValueChange={onCompensationAmountChange} fullWidth />
      ) : null}
      <TextField label={conditionLabel} value={actionCondition} onChange={(event) => onConditionChange(event.target.value)} />
      <TextField label={noteLabel} value={actionNote} onChange={(event) => onNoteChange(event.target.value)} multiline minRows={2} />
      <Button
        variant='outlined'
        fullWidth
        disabled={!targetCaseId || !actionDate || isSubmitting || (isCustomerReturn && (!returnOutcome || !paymentMethodId))}
        onClick={onApply}
      >
        {applyLabel}
      </Button>
    </Stack>
  );
}
