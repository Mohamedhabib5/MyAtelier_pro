import { FormEvent, useState } from 'react';

import { Alert, Box, Button, Card, CardContent, Stack, TextField, Typography } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';

import { useAuth } from '../features/auth/AuthProvider';
import { LanguageSwitcher } from '../features/language/LanguageSwitcher';
import { useLanguage } from '../features/language/LanguageProvider';
import { ApiError } from '../lib/api';
import { useLoginText } from '../text/auth';
import { verify2FA, verifyBackup2FA } from '../features/auth/api';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
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
        // Handle 2FA verification
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
    <Box sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center', bgcolor: 'grey.100', p: 2 }}>
      <Card sx={{ width: '100%', maxWidth: 460 }}>
        <CardContent>
          <Stack spacing={3} component='form' onSubmit={handleSubmit}>
            <Stack direction='row' justifyContent='space-between' alignItems='center'>
              <Box />
              <LanguageSwitcher />
            </Stack>
            <Stack spacing={1}>
              <Typography variant='h4'>{loginText.title}</Typography>
              <Typography color='text.secondary'>{loginText.subtitle}</Typography>
            </Stack>
            {error ? <Alert severity='error'>{error}</Alert> : null}
            {!is2FARequired ? (
              <>
                <TextField label={loginText.username} value={username} onChange={(event) => setUsername(event.target.value)} required />
                <TextField label={loginText.password} type='password' value={password} onChange={(event) => setPassword(event.target.value)} required />
              </>
            ) : (
              <>
                <Typography variant="body1" textAlign="center" fontWeight="bold">
                  {useBackupCode ? 'أدخل كود النسخ الاحتياطي' : 'التحقق الثنائي مطلوب'}
                </Typography>
                <TextField 
                  label={useBackupCode ? 'كود النسخ الاحتياطي' : 'رمز التحقق (6 أرقام)'} 
                  value={twoFACode} 
                  onChange={(event) => setTwoFACode(event.target.value)} 
                  autoFocus
                  required 
                />
                <Button variant="text" size="small" onClick={() => { setUseBackupCode(!useBackupCode); setTwoFACode(''); }}>
                  {useBackupCode ? 'استخدام رمز التطبيق' : 'فقدت هاتفي؟ استخدم كود النسخ الاحتياطي'}
                </Button>
              </>
            )}
            <Button type='submit' variant='contained' size='large' disabled={submitting}>
              {submitting ? loginText.submitting : (is2FARequired ? 'تأكيد الرمز' : loginText.submit)}
            </Button>
            {!is2FARequired && (
              <Typography variant='body2' color='text.secondary'>
                {loginText.helper} <strong>admin / admin123</strong>
              </Typography>
            )}
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
