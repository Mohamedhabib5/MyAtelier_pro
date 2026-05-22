import { Alert, Box, Button, Dialog, DialogActions, DialogContent, DialogTitle, Stack, Typography } from '@mui/material';
import { CheckCircle2, AlertTriangle } from 'lucide-react';
import { type IntegrityVerifyResponse } from '../api';

interface AuditIntegrityDialogProps {
  open: boolean;
  onClose: () => void;
  result: IntegrityVerifyResponse | null;
}

export function AuditIntegrityDialog({ open, onClose, result }: AuditIntegrityDialogProps) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {result?.success ? <CheckCircle2 color="green" /> : <AlertTriangle color="red" />}
        نتيجة التحقق من النزاهة
      </DialogTitle>
      <DialogContent dividers>
        {result?.success ? (
          <Stack spacing={2} alignItems="center" sx={{ py: 2 }}>
            <Typography variant="h6" color="success.main" fontWeight="bold">
              سلسلة السجلات سليمة تماماً
            </Typography>
            <Typography variant="body2" textAlign="center">
              تم التحقق من <strong>{result.total_verified}</strong> سجل تدقيق. 
              لم يتم العثور على أي تلاعب أو فجوات في سلسلة التشفير (Hash Chain).
            </Typography>
          </Stack>
        ) : (
          <Stack spacing={2}>
            <Typography variant="h6" color="error.main" fontWeight="bold">
              تم اكتشاف مشكلات في نزاهة السجل!
            </Typography>
            <Alert severity="error">
              تم العثور على {result?.issues.length} مشكلة. قد يشير هذا إلى تلاعب في قاعدة البيانات أو خطأ في النظام.
            </Alert>
            <Box sx={{ maxHeight: 200, overflowY: 'auto', bgcolor: '#fff5f5', p: 1, borderRadius: 1 }}>
              {result?.issues.map((issue, idx) => (
                <Typography key={idx} variant="caption" display="block" sx={{ mb: 1, borderBottom: '1px solid #fed7d7' }}>
                  <strong>سجل {issue.log_id}:</strong> {issue.error}
                </Typography>
              ))}
            </Box>
          </Stack>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>إغلاق</Button>
      </DialogActions>
    </Dialog>
  );
}
