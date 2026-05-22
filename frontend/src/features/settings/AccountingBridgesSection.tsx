import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import RotateLeftOutlinedIcon from '@mui/icons-material/RotateLeftOutlined';
import {
  Alert,
  Autocomplete,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import { SectionCard } from '../../components/SectionCard';
import { queryClient } from '../../lib/queryClient';
import { getChartOfAccounts } from '../accounting/api';
import {
  listAccountingBridges,
  resetAccountingBridge,
  updateAccountingBridge,
  type AccountingBridgeConfigRecord,
} from './api';

type Props = {
  language: 'ar' | 'en';
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
};

export function AccountingBridgesSection({ language, onSuccess, onError }: Props) {
  const isAr = language === 'ar';
  
  const [editingBridge, setEditingBridge] = useState<AccountingBridgeConfigRecord | null>(null);
  const [selectedAccountCode, setSelectedAccountCode] = useState<string>('');
  const [resetConfirmKey, setResetConfirmKey] = useState<string | null>(null);

  // Queries
  const bridgesQuery = useQuery({
    queryKey: ['accounting-bridges'],
    queryFn: listAccountingBridges,
  });

  const chartQuery = useQuery({
    queryKey: ['chart-of-accounts'],
    queryFn: getChartOfAccounts,
  });

  // Mutations
  const updateMutation = useMutation({
    mutationFn: ({ key, code }: { key: string; code: string }) =>
      updateAccountingBridge(key, { account_code: code }),
    onSuccess: async () => {
      setEditingBridge(null);
      await queryClient.invalidateQueries({ queryKey: ['accounting-bridges'] });
      onSuccess(isAr ? 'تم تحديث الجسر المحاسبي بنجاح.' : 'Accounting bridge updated successfully.');
    },
    onError: (err: Error) => {
      onError(err.message);
    },
  });

  const resetMutation = useMutation({
    mutationFn: (key: string) => resetAccountingBridge(key),
    onSuccess: async () => {
      setResetConfirmKey(null);
      await queryClient.invalidateQueries({ queryKey: ['accounting-bridges'] });
      onSuccess(isAr ? 'تم إعادة تعيين الجسر للافتراضي.' : 'Bridge reset to default successfully.');
    },
    onError: (err: Error) => {
      onError(err.message);
    },
  });

  // Filtering posting-eligible accounts
  const postingAccounts = useMemo(() => {
    return (chartQuery.data ?? []).filter((acc) => acc.is_active && acc.allows_posting);
  }, [chartQuery.data]);

  const activeAccount = useMemo(() => {
    return postingAccounts.find((acc) => acc.code === selectedAccountCode) || null;
  }, [postingAccounts, selectedAccountCode]);

  const rows = bridgesQuery.data ?? [];

  return (
    <SectionCard
      title={isAr ? 'الجسور المحاسبية التلقائية' : 'Automated Accounting Bridges'}
      subtitle={
        isAr
          ? 'تحديد الحسابات التي تسجل عليها مبالغ التحصيلات والمستحقات والضرائب والعهود تلقائياً عند إجراء المعاملات.'
          : 'Define accounts for automatic postings of cash, receivables, taxes, and custody upon document recording.'
      }
    >
      <Stack spacing={2}>
        {bridgesQuery.error instanceof Error ? (
          <Alert severity="error">{bridgesQuery.error.message}</Alert>
        ) : null}

        <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
          <Table size="small">
            <TableHead sx={{ bgcolor: 'action.hover' }}>
              <TableRow>
                <TableCell align={isAr ? 'right' : 'left'}>{isAr ? 'اسم الجسر' : 'Bridge Key'}</TableCell>
                <TableCell align="center">{isAr ? 'كود الحساب' : 'Account Code'}</TableCell>
                <TableCell align={isAr ? 'right' : 'left'}>{isAr ? 'اسم الحساب الحالي' : 'Current Account Name'}</TableCell>
                <TableCell align="center">{isAr ? 'إجراءات' : 'Actions'}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.bridge_key} hover>
                  <TableCell align={isAr ? 'right' : 'left'} sx={{ fontWeight: 'medium' }}>
                    {isAr ? row.label_ar : row.label_en}
                  </TableCell>
                  <TableCell align="center">
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 'bold' }}>
                      {row.account_code}
                    </Typography>
                  </TableCell>
                  <TableCell align={isAr ? 'right' : 'left'}>
                    {row.account_name ? (
                      row.account_name
                    ) : (
                      <Typography variant="caption" color="error">
                        {isAr ? '⚠️ الحساب غير موجود في شجرة الحسابات' : '⚠️ Account not found in COA'}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell align="center">
                    <Stack direction="row" spacing={1} justifyContent="center">
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => {
                          setEditingBridge(row);
                          setSelectedAccountCode(row.account_code);
                        }}
                      >
                        <EditOutlinedIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="warning"
                        onClick={() => setResetConfirmKey(row.bridge_key)}
                      >
                        <RotateLeftOutlinedIcon fontSize="small" />
                      </IconButton>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Edit Config Modal */}
        <Dialog
          open={!!editingBridge}
          onClose={() => setEditingBridge(null)}
          fullWidth
          maxWidth="sm"
        >
          <DialogTitle sx={{ textAlign: isAr ? 'right' : 'left' }}>
            {isAr ? 'تعديل ربط الجسر المحاسبي' : 'Modify Accounting Bridge Assignment'}
          </DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Alert severity="warning" sx={{ textAlign: isAr ? 'right' : 'left' }}>
                {isAr
                  ? 'تنبيه: تغيير الحسابات المحاسبية للجسور يؤثر بشكل مباشر على القيود التلقائية التي يتم توليدها عند ترحيل المستندات مثل التحصيل والصرف والإيرادات.'
                  : 'Warning: Changing bridge account assignments directly impacts automatic journal entries generated upon booking/payment postings.'}
              </Alert>

              <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                {isAr ? 'الجسر المحدد:' : 'Selected Bridge:'}{' '}
                {editingBridge && (isAr ? editingBridge.label_ar : editingBridge.label_en)}
              </Typography>

              <Autocomplete
                options={postingAccounts}
                getOptionLabel={(option) => `${option.code} - ${option.name}`}
                value={activeAccount}
                onChange={(_, newValue) => {
                  setSelectedAccountCode(newValue ? newValue.code : '');
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label={isAr ? 'اختر حساباً للترحيل' : 'Select posting account'}
                    required
                    fullWidth
                  />
                )}
                fullWidth
              />
            </Stack>
          </DialogContent>
          <DialogActions sx={{ justifyContent: isAr ? 'flex-start' : 'flex-end', px: 3, pb: 2 }}>
            <Button
              variant="contained"
              color="primary"
              disabled={!selectedAccountCode || updateMutation.isPending}
              onClick={() => {
                if (editingBridge) {
                  updateMutation.mutate({ key: editingBridge.bridge_key, code: selectedAccountCode });
                }
              }}
            >
              {isAr ? 'حفظ التعديل' : 'Save Changes'}
            </Button>
            <Button variant="outlined" onClick={() => setEditingBridge(null)}>
              {isAr ? 'إلغاء' : 'Cancel'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Reset Confirmation Dialog */}
        <Dialog open={!!resetConfirmKey} onClose={() => setResetConfirmKey(null)}>
          <DialogTitle sx={{ textAlign: isAr ? 'right' : 'left' }}>
            {isAr ? 'تأكيد إعادة التعيين للافتراضي' : 'Confirm Reset to Default'}
          </DialogTitle>
          <DialogContent>
            <DialogContentText sx={{ textAlign: isAr ? 'right' : 'left' }}>
              {isAr
                ? 'هل أنت متأكد من رغبتك في إعادة تعيين هذا الجسر المحاسبي إلى الحساب الافتراضي الموصى به من النظام؟'
                : 'Are you sure you want to reset this accounting bridge config back to the system default account?'}
            </DialogContentText>
          </DialogContent>
          <DialogActions sx={{ justifyContent: isAr ? 'flex-start' : 'flex-end', px: 3, pb: 2 }}>
            <Button
              variant="contained"
              color="warning"
              disabled={resetMutation.isPending}
              onClick={() => {
                if (resetConfirmKey) {
                  resetMutation.mutate(resetConfirmKey);
                }
              }}
            >
              {isAr ? 'إعادة تعيين' : 'Reset to Default'}
            </Button>
            <Button variant="outlined" onClick={() => setResetConfirmKey(null)}>
              {isAr ? 'إلغاء' : 'Cancel'}
            </Button>
          </DialogActions>
        </Dialog>
      </Stack>
    </SectionCard>
  );
}
