import React, { useState } from 'react';
import { 
  Dialog, DialogTitle, DialogContent, DialogActions, 
  Button, Typography, Box, TextField, Alert,
  Stepper, Step, StepLabel, Divider, IconButton
} from '@mui/material';
import { QRCodeSVG } from 'qrcode.react';
import { Copy, Check, Download, AlertTriangle } from 'lucide-react';
import { setup2FA, activate2FA, type TwoFASetupResponse } from '../api';

type Props = {
  open: boolean;
  onClose: () => void;
  onComplete: () => void;
};

const steps = ['الإعداد', 'المسح الضوئي', 'التحقق', 'أكواد النسخ الاحتياطي'];

export const TwoFASetupModal: React.FC<Props> = ({ open, onClose, onComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [setupData, setSetupData] = useState<TwoFASetupResponse | null>(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleStartSetup = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await setup2FA();
      setSetupData(data);
      setActiveStep(1);
    } catch (err: any) {
      setError(err.message || 'فشل بدء إعداد التحقق الثنائي');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    if (verificationCode.length < 6) return;
    setLoading(true);
    setError(null);
    try {
      const data = await activate2FA(verificationCode);
      setBackupCodes(data.backup_codes);
      setActiveStep(3);
    } catch (err: any) {
      setError(err.message || 'رمز التحقق غير صحيح');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const downloadBackupCodes = () => {
    const blob = new Blob([backupCodes.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'myatelier-backup-codes.txt';
    link.click();
  };

  return (
    <Dialog open={open} maxWidth="sm" fullWidth disableEscapeKeyDown>
      <DialogTitle sx={{ textAlign: 'center', fontWeight: 'bold' }}>
        تفعيل التحقق الثنائي (2FA)
      </DialogTitle>
      
      <DialogContent>
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4, mt: 2 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {activeStep === 0 && (
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <Typography variant="body1" gutterBottom>
              يحمي التحقق الثنائي حسابك عبر طلب رمز إضافي عند تسجيل الدخول.
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              سنستخدم تطبيق Google Authenticator أو أي تطبيق TOTP آخر.
            </Typography>
            <Button variant="contained" onClick={handleStartSetup} disabled={loading}>
              ابدأ الإعداد الآن
            </Button>
          </Box>
        )}

        {activeStep === 1 && setupData && (
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              1. امسح رمز QR التالي
            </Typography>
            <Box sx={{ bgcolor: 'white', p: 2, display: 'inline-block', borderRadius: 2, mb: 2, border: '1px solid #eee' }}>
              <QRCodeSVG value={setupData.provisioning_uri} size={200} />
            </Box>
            <Typography variant="body2" gutterBottom>
              أو أدخل الرمز يدوياً في التطبيق:
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 3 }}>
              <Typography sx={{ bgcolor: '#f5f5f5', p: 1, borderRadius: 1, letterSpacing: 2, fontFamily: 'monospace' }}>
                {setupData.secret_plain}
              </Typography>
              <IconButton size="small" onClick={() => copyToClipboard(setupData.secret_plain)}>
                <Copy size={16} />
              </IconButton>
            </Box>
            <Button variant="contained" onClick={() => setActiveStep(2)}>
              تم المسح، التالي
            </Button>
          </Box>
        )}

        {activeStep === 2 && (
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              2. أدخل رمز التحقق من التطبيق
            </Typography>
            <TextField
              fullWidth
              label="رمز التحقق (6 أرقام)"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
              inputProps={{ maxLength: 6, style: { textAlign: 'center', fontSize: '1.5rem', letterSpacing: '0.5rem' } }}
              sx={{ mb: 3, maxWidth: 300 }}
              autoFocus
            />
            <Box>
              <Button variant="outlined" onClick={() => setActiveStep(1)} sx={{ mr: 1 }}>
                رجوع
              </Button>
              <Button variant="contained" onClick={handleVerify} disabled={loading || verificationCode.length < 6}>
                تأكيد التفعيل
              </Button>
            </Box>
          </Box>
        )}

        {activeStep === 3 && (
          <Box>
            <Alert severity="warning" icon={<AlertTriangle />} sx={{ mb: 2 }}>
              احتفظ بهذه الأكواد في مكان آمن. ستحتاجها إذا فقدت الوصول إلى هاتفك.
            </Alert>
            <Typography variant="subtitle2" gutterBottom fontWeight="bold">
              أكواد النسخ الاحتياطي:
            </Typography>
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: '1fr 1fr', 
              gap: 1, 
              bgcolor: '#f9f9f9', 
              p: 2, 
              borderRadius: 1,
              fontFamily: 'monospace',
              mb: 3
            }}>
              {backupCodes.map((code, idx) => (
                <Typography key={idx} variant="body2">{code}</Typography>
              ))}
            </Box>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button startIcon={<Copy />} onClick={() => copyToClipboard(backupCodes.join('\n'))}>
                نسخ الكل
              </Button>
              <Button startIcon={<Download />} onClick={downloadBackupCodes}>
                تحميل كملف نصي
              </Button>
            </Box>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        {activeStep === 3 ? (
          <Button variant="contained" fullWidth size="large" onClick={onComplete} color="success">
            إكمال وإنهاء
          </Button>
        ) : (
          <Button onClick={onClose} disabled={loading}>
            إلغاء
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};
