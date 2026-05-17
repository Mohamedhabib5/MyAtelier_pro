import { FormEvent, useState } from 'react';
import { 
  Alert, Box, Button, Card, CardContent, Stack, 
  TextField, Typography, useTheme, InputAdornment,
  IconButton, Fade, CircularProgress, Paper
} from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import { Lock, User as UserIcon, ShieldCheck, Key, ArrowRight, Languages } from 'lucide-react';
import { motion } from 'framer-motion';

import { useAuth } from '../features/auth/AuthProvider';
import { LanguageSwitcher } from '../features/language/LanguageSwitcher';
import { useLanguage } from '../features/language/LanguageProvider';
import { ApiError } from '../lib/api';
import { useLoginText } from '../text/auth';
import { verify2FA, verifyBackup2FA } from '../features/auth/api';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const { language } = useLanguage();
  const { loginAction } = useAuth();
  const loginText = useLoginText();
  
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [is2FARequired, setIs2FARequired] = useState(false);
  const [twoFACode, setTwoFACode] = useState('');
  const [useBackupCode, setUseBackupCode] = useState(false);
  
  const targetPath = (location.state as { from?: string } | undefined)?.from ?? '/dashboard';

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (!is2FARequired) {
        const user = await loginAction({ username, password, language });
        if (user.is_2fa_required) {
          setIs2FARequired(true);
        } else {
          navigate(targetPath, { replace: true });
        }
      } else {
        if (useBackupCode) {
          await verifyBackup2FA(twoFACode);
        } else {
          await verify2FA(twoFACode);
        }
        navigate(targetPath, { replace: true });
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : loginText.fallbackError);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Box 
      sx={{ 
        minHeight: '100vh', 
        display: 'flex', 
        flexDirection: 'column',
        bgcolor: '#f8fafc',
        backgroundImage: 'radial-gradient(at 0% 0%, rgba(37, 99, 235, 0.05) 0, transparent 50%), radial-gradient(at 50% 0%, rgba(37, 99, 235, 0.05) 0, transparent 50%)',
        p: 2 
      }}
    >
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <LanguageSwitcher />
      </Box>

      <Box sx={{ flex: 1, display: 'grid', placeItems: 'center' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card 
            sx={{ 
              width: '100%', 
              maxWidth: 420, 
              borderRadius: 6,
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
              overflow: 'visible'
            }}
          >
            <Box 
              sx={{ 
                height: 8, 
                bgcolor: 'primary.main', 
                borderTopLeftRadius: 24, 
                borderTopRightRadius: 24 
              }} 
            />
            
            <CardContent sx={{ p: 5 }}>
              <Stack spacing={4} component='form' onSubmit={handleSubmit}>
                <Box sx={{ textAlign: 'center' }}>
                  <Box 
                    sx={{ 
                      display: 'inline-flex', 
                      p: 2, 
                      borderRadius: 4, 
                      bgcolor: 'primary.main', 
                      color: 'white',
                      mb: 2,
                      boxShadow: '0 10px 15px -3px rgba(37, 99, 235, 0.4)'
                    }}
                  >
                    <ShieldCheck size={32} />
                  </Box>
                  <Typography variant='h4' fontWeight='800' gutterBottom>
                    {is2FARequired ? (useBackupCode ? 'كود الطوارئ' : 'التحقق الثنائي') : 'MyAtelier Pro'}
                  </Typography>
                  <Typography color='text.secondary' variant='body2'>
                    {is2FARequired 
                      ? 'يرجى إدخال رمز التحقق الإضافي للمتابعة' 
                      : 'سجل دخولك لإدارة ورشتك بكفاءة'}
                  </Typography>
                </Box>

                {error && (
                  <Fade in={!!error}>
                    <Alert 
                      severity='error' 
                      variant="outlined"
                      sx={{ borderRadius: 3, bgcolor: 'error.lighter' }}
                    >
                      {error}
                    </Alert>
                  </Fade>
                )}

                <Stack spacing={2.5}>
                  {!is2FARequired ? (
                    <>
                      <TextField 
                        label={loginText.username} 
                        value={username} 
                        onChange={(event) => setUsername(event.target.value)} 
                        required 
                        fullWidth
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <UserIcon size={20} color={theme.palette.text.disabled} />
                            </InputAdornment>
                          ),
                          sx: { borderRadius: 3 }
                        }}
                      />
                      <TextField 
                        label={loginText.password} 
                        type='password' 
                        value={password} 
                        onChange={(event) => setPassword(event.target.value)} 
                        required 
                        fullWidth
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Lock size={20} color={theme.palette.text.disabled} />
                            </InputAdornment>
                          ),
                          sx: { borderRadius: 3 }
                        }}
                      />
                    </>
                  ) : (
                    <>
                      <TextField 
                        label={useBackupCode ? 'كود النسخ الاحتياطي' : 'رمز التحقق (6 أرقام)'} 
                        value={twoFACode} 
                        onChange={(event) => setTwoFACode(event.target.value)} 
                        autoFocus
                        required 
                        fullWidth
                        inputProps={{ 
                          maxLength: useBackupCode ? 20 : 6,
                          style: { textAlign: 'center', letterSpacing: useBackupCode ? '0' : '0.5rem', fontWeight: 'bold' } 
                        }}
                        InputProps={{
                          sx: { borderRadius: 3, fontSize: '1.2rem' }
                        }}
                      />
                      <Button 
                        variant="text" 
                        size="small" 
                        onClick={() => { setUseBackupCode(!useBackupCode); setTwoFACode(''); }}
                        startIcon={<Key size={16} />}
                        sx={{ alignSelf: 'center', borderRadius: 10 }}
                      >
                        {useBackupCode ? 'استخدام رمز التطبيق' : 'استخدم كود النسخ الاحتياطي'}
                      </Button>
                    </>
                  )}
                </Stack>

                <Button 
                  type='submit' 
                  variant='contained' 
                  size='large' 
                  disabled={submitting}
                  endIcon={submitting ? <CircularProgress size={20} color="inherit" /> : <ArrowRight size={20} />}
                  sx={{ 
                    py: 1.8, 
                    borderRadius: 3, 
                    fontWeight: 'bold', 
                    fontSize: '1rem',
                    textTransform: 'none',
                    boxShadow: '0 10px 15px -3px rgba(37, 99, 235, 0.3)'
                  }}
                >
                  {is2FARequired ? 'تأكيد الرمز' : loginText.submit}
                </Button>

                {!is2FARequired && (
                  <Paper 
                    elevation={0} 
                    sx={{ 
                      p: 2, 
                      bgcolor: 'rgba(0,0,0,0.02)', 
                      borderRadius: 3,
                      border: '1px solid rgba(0,0,0,0.05)',
                      textAlign: 'center'
                    }}
                  >
                    <Typography variant='caption' color='text.secondary' display='block'>
                      بيانات الدخول الافتراضية للتجربة:
                    </Typography>
                    <Typography variant='caption' fontWeight='bold' color='primary'>
                      admin / admin123
                    </Typography>
                  </Paper>
                )}
              </Stack>
            </CardContent>
          </Card>
        </motion.div>
      </Box>

      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant='caption' color='text.disabled'>
          © {new Date().getFullYear()} MyAtelier Pro. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
}
