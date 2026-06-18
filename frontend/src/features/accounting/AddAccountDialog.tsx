import { useEffect, useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Autocomplete,
  FormControlLabel,
  Switch,
  Stack,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { createChartAccount, updateChartAccount, ChartAccountRecord } from './api';
import { queryClient } from '../../lib/queryClient';

type Props = {
  open: boolean;
  onClose: () => void;
  accounts: ChartAccountRecord[];
  isAr: boolean;
  account?: ChartAccountRecord | null;
};

export function AddAccountDialog({ open, onClose, accounts, isAr, account }: Props) {
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [accountType, setAccountType] = useState('asset');
  const [parentAccount, setParentAccount] = useState<ChartAccountRecord | null>(null);
  const [allowsPosting, setAllowsPosting] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      if (account) {
        setCode(account.code);
        setName(account.name);
        setAccountType(account.account_type);
        const parent = accounts.find((a) => a.id === account.parent_account_id) || null;
        setParentAccount(parent);
        setAllowsPosting(account.allows_posting);
      } else {
        setCode('');
        setName('');
        setAccountType('asset');
        setParentAccount(null);
        setAllowsPosting(true);
      }
      setErrorMsg(null);
    }
  }, [open, account, accounts]);

  const mutation = useMutation({
    mutationFn: (payload: Record<string, any>) => {
      if (account) {
        return updateChartAccount(account.id, payload);
      } else {
        return createChartAccount(payload);
      }
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['accounting', 'chart'] });
      handleClose();
    },
    onError: (err: Error | any) => {
      setErrorMsg(err.message || (isAr ? 'حدث خطأ أثناء حفظ الحساب.' : 'An error occurred.'));
    },
  });

  const handleClose = () => {
    setCode('');
    setName('');
    setAccountType('asset');
    setParentAccount(null);
    setAllowsPosting(true);
    setErrorMsg(null);
    onClose();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    if ((!account && !code.trim()) || !name.trim()) {
      setErrorMsg(isAr ? '⚠️ الكود والاسم حقول مطلوبة.' : '⚠️ Code and Name are required.');
      return;
    }
    const payload: Record<string, any> = {
      name: name.trim(),
      account_type: accountType,
      parent_account_id: parentAccount ? parentAccount.id : null,
      allows_posting: allowsPosting,
    };
    if (!account) {
      payload.code = code.trim();
    }
    mutation.mutate(payload);
  };

  const accountTypes = [
    { value: 'asset', label: isAr ? 'أصول' : 'Asset' },
    { value: 'liability', label: isAr ? 'التزامات (خصوم)' : 'Liability' },
    { value: 'equity', label: isAr ? 'حقوق ملكية' : 'Equity' },
    { value: 'revenue', label: isAr ? 'إيرادات' : 'Revenue' },
    { value: 'expense', label: isAr ? 'مصروفات' : 'Expense' },
    { value: 'cash', label: isAr ? 'نقدية' : 'Cash' },
    { value: 'bank', label: isAr ? 'بنك' : 'Bank' },
    { value: 'receivable', label: isAr ? 'ذمم مدينة (عملاء)' : 'Receivable' },
    { value: 'payable', label: isAr ? 'ذمم دائنة (موردين)' : 'Payable' },
  ];

  // Filter accounts list to prevent choosing itself as its own parent when editing
  const filteredAccounts = account
    ? accounts.filter((a) => a.id !== account.id)
    : accounts;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {account
          ? isAr ? 'تعديل الحساب المالي' : 'Edit Chart Account'
          : isAr ? 'إضافة حساب جديد لشجرة الحسابات' : 'Add New Account to Chart'}
      </DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent dividers>
          <Stack spacing={2.5}>
            {errorMsg && <Alert severity="error">{errorMsg}</Alert>}

            <TextField
              label={isAr ? 'كود الحساب' : 'Account Code'}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
              fullWidth
              size="small"
              disabled={Boolean(account)}
            />

            <TextField
              label={isAr ? 'اسم الحساب' : 'Account Name'}
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              fullWidth
              size="small"
            />

            <FormControl fullWidth size="small">
              <InputLabel>{isAr ? 'نوع الحساب' : 'Account Type'}</InputLabel>
              <Select
                value={accountType}
                onChange={(e) => setAccountType(e.target.value)}
                label={isAr ? 'نوع الحساب' : 'Account Type'}
              >
                {accountTypes.map((t) => (
                  <MenuItem key={t.value} value={t.value}>
                    {t.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Autocomplete
              options={filteredAccounts}
              getOptionLabel={(option) => `${option.code} - ${option.name}`}
              value={parentAccount}
              onChange={(_, newVal) => setParentAccount(newVal)}
              renderInput={(params) => (
                <TextField {...params} label={isAr ? 'الحساب الأب' : 'Parent Account'} size="small" />
              )}
              fullWidth
            />

            <FormControlLabel
              control={
                <Switch
                  checked={allowsPosting}
                  onChange={(e) => setAllowsPosting(e.target.checked)}
                  color="primary"
                />
              }
              label={isAr ? 'يقبل الترحيل المباشر (حساب ترصيد)' : 'Allows Direct Posting (Posting Account)'}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="inherit">
            {isAr ? 'إلغاء' : 'Cancel'}
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={mutation.isPending}
            startIcon={mutation.isPending ? <CircularProgress size={20} color="inherit" /> : null}
          >
            {account
              ? isAr ? 'حفظ التعديلات' : 'Save Changes'
              : isAr ? 'إضافة الحساب' : 'Add Account'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
