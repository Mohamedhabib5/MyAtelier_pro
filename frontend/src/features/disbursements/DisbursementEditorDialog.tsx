import { 
  Alert,
  Autocomplete, 
  Button, 
  Dialog, 
  DialogActions, 
  DialogContent, 
  DialogTitle, 
  MenuItem, 
  Stack, 
  TextField, 
  Typography 
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';

import { AppDateField } from '../../components/inputs/AppDateField';
import { StableNumericField } from '../../components/inputs/StableNumericField';
import { getChartOfAccounts } from '../accounting/api';
import { useLanguage } from '../language/LanguageProvider';
import { useDisbursementsText } from '../../text/disbursements';
import type { PaymentMethodRecord } from '../paymentMethods/api';
import type { DisbursementVoucherRecord, DisbursementCreatePayload, DisbursementUpdatePayload } from './api';

type Props = {
  open: boolean;
  onClose: () => void;
  voucher: DisbursementVoucherRecord | null;
  paymentMethods: PaymentMethodRecord[];
  saving: boolean;
  onSave: (payload: DisbursementCreatePayload | DisbursementUpdatePayload) => Promise<void>;
};

export function DisbursementEditorDialog({
  open,
  onClose,
  voucher,
  paymentMethods,
  saving,
  onSave,
}: Props) {
  const { language } = useLanguage();
  const text = useDisbursementsText();
  const isAr = language === 'ar';

  const [amount, setAmount] = useState('');
  const [payeeType, setPayeeType] = useState<'customer' | 'supplier' | 'employee' | 'expense'>('expense');
  const [payeeName, setPayeeName] = useState('');
  const [expenseAccountId, setExpenseAccountId] = useState('');
  const [paymentMethodId, setPaymentMethodId] = useState('');
  const [voucherDate, setVoucherDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [notes, setNotes] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  // Load CoA for Expense Accounts
  const chartQuery = useQuery({
    queryKey: ['chart-of-accounts'],
    queryFn: getChartOfAccounts,
    enabled: open,
  });

  const expenseAccounts = useMemo(() => {
    return (chartQuery.data ?? []).filter(
      (acc) => acc.is_active && acc.allows_posting && acc.account_type.toLowerCase() === 'expense'
    );
  }, [chartQuery.data]);

  // Load existing voucher details when editing
  useEffect(() => {
    if (open) {
      setLocalError(null);
      if (voucher) {
        setAmount(String(voucher.amount));
        setPayeeType(voucher.payee_type);
        setPayeeName(voucher.payee_name ?? '');
        setExpenseAccountId(voucher.expense_account_id ?? '');
        setPaymentMethodId(voucher.payment_method_id);
        setVoucherDate(voucher.voucher_date);
        setNotes(voucher.notes ?? '');
      } else {
        setAmount('');
        setPayeeType('expense');
        setPayeeName('');
        setExpenseAccountId('');
        setPaymentMethodId(paymentMethods[0]?.id ?? '');
        setVoucherDate(new Date().toISOString().slice(0, 10));
        setNotes('');
      }
    }
  }, [open, voucher, paymentMethods]);

  const selectedExpenseAccount = expenseAccounts.find((acc) => acc.id === expenseAccountId) || null;

  async function handleSubmit() {
    setLocalError(null);
    const numAmount = Number(amount);
    if (!amount || isNaN(numAmount) || numAmount <= 0) {
      setLocalError(text.editor.amountError);
      return;
    }
    if (!paymentMethodId) {
      setLocalError(isAr ? 'يجب اختيار طريقة الصرف / الخزنة' : 'Safe/Payment method is required');
      return;
    }
    if (payeeType === 'expense' && !expenseAccountId) {
      setLocalError(isAr ? 'يجب تحديد حساب مصروف من الشجرة' : 'Expense account is required');
      return;
    }
    if (payeeType !== 'expense' && !payeeName.trim()) {
      setLocalError(isAr ? 'يجب كتابة اسم المستلم' : 'Payee name is required');
      return;
    }

    const payload: DisbursementCreatePayload = {
      payment_method_id: paymentMethodId,
      voucher_date: voucherDate,
      amount: numAmount,
      payee_type: payeeType,
      payee_name: payeeType === 'expense' ? (selectedExpenseAccount?.name ?? '') : payeeName.trim(),
      payee_id: null,
      expense_account_id: payeeType === 'expense' ? expenseAccountId : null,
      notes: notes.trim() || null,
    };

    try {
      await onSave(payload);
    } catch (err: unknown) {
      setLocalError(err.message || (isAr ? 'حدث خطأ أثناء الحفظ' : 'An error occurred while saving'));
    }
  }

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle sx={{ textAlign: isAr ? 'right' : 'left' }}>
        {voucher 
          ? text.editor.editTitle.replace('{number}', voucher.voucher_number) 
          : text.editor.createTitle}
      </DialogTitle>
      
      <DialogContent>
        <Stack spacing={2.5} sx={{ mt: 1.5 }}>
          {voucher && (
            <Alert severity="warning" sx={{ textAlign: isAr ? 'right' : 'left' }}>
              {text.editor.editNotice}
            </Alert>
          )}

          {localError && <Alert severity="error">{localError}</Alert>}

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <TextField
              select
              label={text.editor.payeeType}
              value={payeeType}
              onChange={(e) => setPayeeType(e.target.value as any)}
              fullWidth
            >
              <MenuItem value="expense">{text.page.types.expense}</MenuItem>
              <MenuItem value="supplier">{text.page.types.supplier}</MenuItem>
              <MenuItem value="customer">{text.page.types.customer}</MenuItem>
              <MenuItem value="employee">{text.page.types.employee}</MenuItem>
            </TextField>

            <StableNumericField
              label={text.editor.amount}
              value={amount}
              onValueChange={setAmount}
              allowDecimal
              fullWidth
            />
          </Stack>

          {payeeType === 'expense' ? (
            <Autocomplete
              options={expenseAccounts}
              getOptionLabel={(option) => `${option.code} - ${option.name}`}
              value={selectedExpenseAccount}
              onChange={(_, newValue) => setExpenseAccountId(newValue ? newValue.id : '')}
              loading={chartQuery.isLoading}
              renderInput={(params) => (
                <TextField {...params} label={text.editor.expenseAccount} variant="outlined" required />
              )}
              fullWidth
            />
          ) : (
            <TextField
              label={text.editor.payeeName}
              value={payeeName}
              onChange={(e) => setPayeeName(e.target.value)}
              required
              fullWidth
            />
          )}

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <TextField
              select
              label={text.editor.paymentMethod}
              value={paymentMethodId}
              onChange={(e) => setPaymentMethodId(e.target.value)}
              fullWidth
            >
              {paymentMethods.map((pm) => (
                <MenuItem key={pm.id} value={pm.id}>
                  {pm.name} {pm.linked_account_code ? `(${pm.linked_account_code})` : ''}
                </MenuItem>
              ))}
            </TextField>

            <AppDateField
              label={text.editor.date}
              value={voucherDate}
              onChange={setVoucherDate}
              sx={{ width: '100%' }}
            />
          </Stack>

          <TextField
            label={text.editor.notes}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            multiline
            rows={3}
            fullWidth
          />
        </Stack>
      </DialogContent>

      <DialogActions sx={{ justifyContent: isAr ? 'flex-start' : 'flex-end', px: 3, pb: 2 }}>
        <Button 
          variant="contained" 
          onClick={handleSubmit} 
          disabled={saving}
          sx={{ px: 3 }}
        >
          {text.editor.save}
        </Button>
        <Button variant="outlined" onClick={onClose} disabled={saving}>
          {text.editor.cancel}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
