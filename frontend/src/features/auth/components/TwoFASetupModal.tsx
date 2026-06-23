import React, { useState } from 'react';
import { 
  Dialog, DialogTitle, DialogContent, DialogActions, 
  Button, Typography, Box, TextField, Alert,
  Stepper, Step, StepLabel, Divider, IconButton,
  Paper, useTheme, Fade, Grid, Stack
} from '@mui/material';
import { QRCodeSVG } from 'qrcode.react';
import { Copy, Check, Download, AlertTriangle, ShieldCheck, Key, Smartphone, Lock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { setup2FA, activate2FA, type TwoFASetupResponse } from '../api';
import { useLoginText } from '../../../text/auth';

type Props = {
  open: boolean;
  onClose: () => void;
  onComplete: () => void;
};

// steps handled in component

export const TwoFASetupModal: React.FC<Props> = ({ open, onClose, onComplete }) => {
  const theme = useTheme();
  const authText = useLoginText();
  const steps = [authText.stepSetup, authText.stepScan, authText.stepVerify, authText.stepSecurity];
  const [activeStep, setActiveStep] = useState(0);
  const [setupData, setSetupData] = useState<TwoFASetupResponse | null>(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleStartSetup = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await setup2FA();
      setSetupData(data);
      setActiveStep(1);
    } catch (err: unknown) {
      setError((err as any).message || authText.startSetupFailed);
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
    } catch (err: unknown) {
      setError((err as any).message || authText.invalidCode);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadBackupCodes = () => {
    const content = `MyAtelier Pro - Backup Codes\nGenerated at: ${new Date().toLocaleString()}\n\n${backupCodes.join('\n')}\n\nKeep these codes safe!`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'myatelier-backup-codes.txt';
    link.click();
  };

  return (
    <Dialog 
      open={open} 
      maxWidth="sm" 
      fullWidth 
      disableEscapeKeyDown
      PaperProps={{
        sx: {
          borderRadius: 4,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 20px 40px rgba(0,0,0,0.1)'
        }
      }}
    >
      <DialogTitle sx={{ 
        textAlign: 'center', 
        pt: 4, 
        fontWeight: 800, 
        fontSize: '1.5rem',
        color: theme.palette.primary.dark
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 1 }}>
          <ShieldCheck size={32} color={theme.palette.primary.main} />
          {authText.setupTitle}
        </Box>
      </DialogTitle>
      
      <DialogContent sx={{ overflow: 'hidden' }}>
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4, mt: 1 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <AnimatePresence mode="wait">
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
            >
              <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>{error}</Alert>
            </motion.div>
          )}
        </AnimatePresence>

        <Box sx={{ minHeight: 320, display: 'flex', flexDirection: 'column' }}>
          <AnimatePresence mode="wait">
            {activeStep === 0 && (
              <motion.div
                key="step0"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="h6" gutterBottom fontWeight="bold" color="text.primary">
                    {authText.enhanceSecurityTitle}
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ mb: 4, px: 4 }}>
                    {authText.enhanceSecurityDesc}
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4, mb: 4 }}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Smartphone size={40} color={theme.palette.text.disabled} />
                      <Typography variant="caption" display="block">{authText.phoneApp}</Typography>
                    </Box>
                    <Box sx={{ alignSelf: 'center' }}>
                      <Typography variant="h4" color="text.disabled">→</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'center' }}>
                      <Lock size={40} color={theme.palette.primary.main} />
                      <Typography variant="caption" display="block">{authText.protectedAccount}</Typography>
                    </Box>
                  </Box>
                  <Button 
                    variant="contained" 
                    size="large"
                    onClick={handleStartSetup} 
                    disabled={loading}
                    sx={{ 
                      borderRadius: 10, 
                      px: 6, 
                      py: 1.5,
                      boxShadow: theme.shadows[4]
                    }}
                  >
                    {authText.startSetupNow}
                  </Button>
                </Box>
              </motion.div>
            )}

            {activeStep === 1 && setupData && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                    {authText.scanQROrManual}
                  </Typography>
                  <Paper 
                    elevation={0}
                    sx={{ 
                      bgcolor: 'white', 
                      p: 3, 
                      display: 'inline-block', 
                      borderRadius: 4, 
                      mb: 2, 
                      border: `2px solid ${theme.palette.divider}` 
                    }}
                  >
                    <QRCodeSVG value={setupData.provisioning_uri} size={180} />
                  </Paper>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {authText.manualEntryDesc}
                  </Typography>
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    gap: 1, 
                    mb: 3,
                    bgcolor: 'rgba(0,0,0,0.04)',
                    p: 1.5,
                    borderRadius: 2
                  }}>
                    <Typography sx={{ letterSpacing: 2, fontFamily: 'monospace', fontWeight: 'bold' }}>
                      {setupData.secret_base32}
                    </Typography>
                    <IconButton size="small" onClick={() => copyToClipboard(setupData.secret_base32)}>
                      {copied ? <Check size={18} color={theme.palette.success.main} /> : <Copy size={18} />}
                    </IconButton>
                  </Box>
                  <Button variant="contained" onClick={() => setActiveStep(2)} sx={{ borderRadius: 10, px: 4 }}>
                    {authText.scannedNext}
                  </Button>
                </Box>
              </motion.div>
            )}

            {activeStep === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                    {authText.enterCodeTitle}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    {authText.enterCodeDesc}
                  </Typography>
                  <TextField
                    fullWidth
                    placeholder="000000"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
                    inputProps={{ 
                      maxLength: 6, 
                      style: { 
                        textAlign: 'center', 
                        fontSize: '2rem', 
                        letterSpacing: '0.8rem',
                        fontWeight: 'bold',
                        color: theme.palette.primary.main
                      } 
                    }}
                    sx={{ 
                      mb: 4, 
                      maxWidth: 300,
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 3,
                        bgcolor: 'rgba(0,0,0,0.02)'
                      }
                    }}
                    autoFocus
                  />
                  <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
                    <Button variant="text" onClick={() => setActiveStep(1)} sx={{ borderRadius: 10 }}>
                      {authText.back}
                    </Button>
                    <Button 
                      variant="contained" 
                      onClick={handleVerify} 
                      disabled={loading || verificationCode.length < 6}
                      sx={{ borderRadius: 10, px: 4 }}
                    >
                      {authText.confirmActivation}
                    </Button>
                  </Box>
                </Box>
              </motion.div>
            )}

            {activeStep === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4 }}
              >
                <Box>
                  <Alert 
                    severity="warning" 
                    icon={<AlertTriangle />} 
                    sx={{ 
                      mb: 3, 
                      borderRadius: 3,
                      '& .MuiAlert-message': { fontWeight: 'bold' }
                    }}
                  >
                    {authText.importantKeepCodes}
                  </Alert>
                  
                  <Paper 
                    variant="outlined" 
                    sx={{ 
                      p: 2.5, 
                      borderRadius: 3, 
                      bgcolor: 'rgba(0,0,0,0.02)',
                      borderStyle: 'dashed',
                      borderWidth: 2,
                      mb: 3
                    }}
                  >
                    <Grid container spacing={1}>
                      {backupCodes.map((code, idx) => (
                        <Grid size={{ xs: 6 }} key={idx}>
                          <Box sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            gap: 1,
                            p: 1,
                            bgcolor: 'white',
                            borderRadius: 1.5,
                            border: '1px solid rgba(0,0,0,0.05)'
                          }}>
                            <Key size={14} color={theme.palette.text.disabled} />
                            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 'bold' }}>{code}</Typography>
                          </Box>
                        </Grid>
                      ))}
                    </Grid>
                  </Paper>

                  <Stack direction="row" spacing={2} justifyContent="center">
                    <Button 
                      variant="outlined" 
                      startIcon={<Copy size={18} />} 
                      onClick={() => copyToClipboard(backupCodes.join('\n'))}
                      sx={{ borderRadius: 10 }}
                    >
                      {authText.copyAll}
                    </Button>
                    <Button 
                      variant="outlined" 
                      startIcon={<Download size={18} />} 
                      onClick={downloadBackupCodes}
                      sx={{ borderRadius: 10 }}
                    >
                      {authText.downloadAsFile}
                    </Button>
                  </Stack>
                </Box>
              </motion.div>
            )}
          </AnimatePresence>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 4, pt: 0 }}>
        {activeStep === 3 ? (
          <Button 
            variant="contained" 
            fullWidth 
            size="large" 
            onClick={onComplete} 
            color="success"
            sx={{ 
              borderRadius: 10, 
              py: 1.5, 
              fontWeight: 'bold',
              boxShadow: '0 8px 16px rgba(46, 125, 50, 0.2)'
            }}
          >
            {authText.completeAndFinish}
          </Button>
        ) : (
          <Button 
            onClick={onClose} 
            disabled={loading}
            color="inherit"
            sx={{ borderRadius: 10 }}
          >
            {authText.cancel}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};
