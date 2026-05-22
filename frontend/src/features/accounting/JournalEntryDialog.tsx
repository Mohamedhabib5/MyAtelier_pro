import { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton,
  Stack, Typography, Alert, CircularProgress, Autocomplete, Grid
} from '@mui/material';
import { Trash2, Plus } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import { createJournalEntry, postJournalEntry, updateJournalEntry, ChartAccountRecord, JournalEntryRecord } from './api';
import { queryClient } from '../../lib/queryClient';

type Props = {
  open: boolean;
  onClose: () => void;
  accounts: ChartAccountRecord[];
  isAr: boolean;
  entry?: JournalEntryRecord | null;
};

type EntryLine = {
  accountId: string;
  description: string;
  debit: string;
  credit: string;
};

export function JournalEntryDialog({ open, onClose, accounts, isAr, entry }: Props) {
  const postingAccounts = accounts.filter(a => a.allows_posting);
  const [lines, setLines] = useState<EntryLine[]>([
    { accountId: '', description: '', debit: '', credit: '' },
    { accountId: '', description: '', debit: '', credit: '' },
  ]);
  const [entryDate, setEntryDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [reference, setReference] = useState('');
  const [notes, setNotes] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const isViewOnly = entry ? entry.status !== 'draft' : false;

  useEffect(() => {
    if (open) {
      if (entry) {
        setEntryDate(entry.entry_date.split('T')[0]);
        setReference(entry.reference || '');
        setNotes(entry.notes || '');
        setLines(entry.lines.map(l => ({
          accountId: l.account_id,
          description: l.description || '',
          debit: parseFloat(l.debit_amount) > 0 ? l.debit_amount : '',
          credit: parseFloat(l.credit_amount) > 0 ? l.credit_amount : '',
        })));
      } else {
        setLines([
          { accountId: '', description: '', debit: '', credit: '' },
          { accountId: '', description: '', debit: '', credit: '' },
        ]);
        setEntryDate(new Date().toISOString().split('T')[0]);
        setReference('');
        setNotes('');
      }
      setErrorMsg(null);
    }
  }, [open, entry]);

  const totalDebit = lines.reduce((acc, l) => acc + (parseFloat(l.debit) || 0), 0);
  const totalCredit = lines.reduce((acc, l) => acc + (parseFloat(l.credit) || 0), 0);
  const difference = Math.abs(totalDebit - totalCredit);

  const mutation = useMutation({
    mutationFn: async (shouldPost: boolean) => {
      const payload = {
        entry_date: entryDate,
        reference: reference.trim() || null,
        notes: notes.trim() || null,
        lines: lines.map((l, index) => ({
          line_number: index + 1,
          account_id: l.accountId,
          description: l.description.trim() || null,
          debit_amount: parseFloat(l.debit || '0').toFixed(2),
          credit_amount: parseFloat(l.credit || '0').toFixed(2),
        })),
      };
      const res = entry ? await updateJournalEntry(entry.id, payload) : await createJournalEntry(payload);
      if (shouldPost) await postJournalEntry(res.id);
      return res;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['accounting', 'journals'] });
      handleClose();
    },
    onError: (err: any) => {
      setErrorMsg(err.message || (isAr ? 'حدث خطأ أثناء حفظ القيد.' : 'An error occurred.'));
    },
  });

  const handleClose = () => {
    setLines([
      { accountId: '', description: '', debit: '', credit: '' },
      { accountId: '', description: '', debit: '', credit: '' },
    ]);
    setEntryDate(new Date().toISOString().split('T')[0]);
    setReference('');
    setNotes('');
    setErrorMsg(null);
    onClose();
  };

  const updateLine = (index: number, field: keyof EntryLine, val: string) => {
    const updated = [...lines];
    updated[index] = { ...updated[index], [field]: val };
    if (field === 'debit' && val) updated[index].credit = '';
    if (field === 'credit' && val) updated[index].debit = '';
    setLines(updated);
  };

  const isFormValid = lines.length >= 2 && difference < 0.01 && totalDebit > 0 &&
    lines.every(l => l.accountId && (parseFloat(l.debit) > 0 || parseFloat(l.credit) > 0));

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>{isAr ? 'إنشاء قيد يومي يدوي جديد' : 'Create New Manual Journal Entry'}</DialogTitle>
      <DialogContent dividers sx={{ pb: 1 }}>
        <Stack spacing={2}>
          {errorMsg && <Alert severity="error">{errorMsg}</Alert>}
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField label={isAr ? 'التاريخ' : 'Date'} type="date" value={entryDate} onChange={e => setEntryDate(e.target.value)} fullWidth size="small" InputLabelProps={{ shrink: true }} disabled={isViewOnly} />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField label={isAr ? 'المرجع' : 'Reference'} value={reference} onChange={e => setReference(e.target.value)} fullWidth size="small" disabled={isViewOnly} />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField label={isAr ? 'الملاحظات' : 'Notes'} value={notes} onChange={e => setNotes(e.target.value)} fullWidth size="small" disabled={isViewOnly} />
            </Grid>
          </Grid>

          <TableContainer sx={{ border: '1px solid #e0e0e0', borderRadius: 1, maxHeight: 300 }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell width="35%">{isAr ? 'الحساب' : 'Account'}</TableCell>
                  <TableCell width="35%">{isAr ? 'البيان' : 'Description'}</TableCell>
                  <TableCell width="12%">{isAr ? 'مدين' : 'Debit'}</TableCell>
                  <TableCell width="12%">{isAr ? 'دائن' : 'Credit'}</TableCell>
                  <TableCell width="6%"></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {lines.map((line, idx) => (
                  <TableRow key={idx}>
                    <TableCell sx={{ py: 0.5 }}>
                      <Autocomplete
                        options={postingAccounts}
                        getOptionLabel={opt => `${opt.code} - ${opt.name}`}
                        value={postingAccounts.find(a => a.id === line.accountId) || undefined}
                        onChange={(_, val) => updateLine(idx, 'accountId', val?.id || '')}
                        renderInput={params => <TextField {...params} size="small" placeholder={isAr ? 'اختر حساباً' : 'Select account'} />}
                        fullWidth
                        disableClearable
                        disabled={isViewOnly}
                      />
                    </TableCell>
                    <TableCell sx={{ py: 0.5 }}>
                      <TextField size="small" value={line.description} onChange={e => updateLine(idx, 'description', e.target.value)} fullWidth disabled={isViewOnly} />
                    </TableCell>
                    <TableCell sx={{ py: 0.5 }}>
                      <TextField size="small" type="number" value={line.debit} onChange={e => updateLine(idx, 'debit', e.target.value)} inputProps={{ min: 0, step: "any" }} fullWidth disabled={isViewOnly} />
                    </TableCell>
                    <TableCell sx={{ py: 0.5 }}>
                      <TextField size="small" type="number" value={line.credit} onChange={e => updateLine(idx, 'credit', e.target.value)} inputProps={{ min: 0, step: "any" }} fullWidth disabled={isViewOnly} />
                    </TableCell>
                    <TableCell sx={{ py: 0.5 }} align="center">
                      <IconButton size="small" color="error" disabled={isViewOnly || lines.length <= 2} onClick={() => setLines(lines.filter((_, i) => i !== idx))}>
                        <Trash2 size={16} />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Button size="small" startIcon={<Plus size={16} />} onClick={() => setLines([...lines, { accountId: '', description: '', debit: '', credit: '' }])} disabled={isViewOnly}>
              {isAr ? 'إضافة سطر' : 'Add Line'}
            </Button>
            <Stack direction="row" spacing={3} sx={{ bgcolor: '#f8f9fa', p: 1.5, borderRadius: 1, border: '1px solid #e0e0e0' }}>
              <Typography variant="body2"><strong>{isAr ? 'إجمالي المدين:' : 'Total Debit:'}</strong> {totalDebit.toFixed(2)}</Typography>
              <Typography variant="body2"><strong>{isAr ? 'إجمالي الدائن:' : 'Total Credit:'}</strong> {totalCredit.toFixed(2)}</Typography>
              <Typography variant="body2" color={difference < 0.01 ? 'success.main' : 'error.main'}>
                <strong>{isAr ? 'الفرق:' : 'Diff:'}</strong> {difference.toFixed(2)}
              </Typography>
            </Stack>
          </Stack>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} color="inherit">
          {isViewOnly ? (isAr ? 'إغلاق' : 'Close') : (isAr ? 'إلغاء' : 'Cancel')}
        </Button>
        {!isViewOnly && (
          <>
            <Button variant="outlined" color="primary" disabled={!isFormValid || mutation.isPending} onClick={() => mutation.mutate(false)}>
              {mutation.isPending ? <CircularProgress size={20} /> : (isAr ? 'حفظ كمسودة' : 'Save as Draft')}
            </Button>
            <Button variant="contained" color="primary" disabled={!isFormValid || mutation.isPending} onClick={() => mutation.mutate(true)}>
              {mutation.isPending ? <CircularProgress size={20} /> : (isAr ? 'حفظ وترحيل' : 'Save & Post')}
            </Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
}
