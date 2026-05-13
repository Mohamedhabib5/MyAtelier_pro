import React, { useState } from 'react';
import { 
  Box, Card, CardContent, Typography, Switch, 
  FormControlLabel, Button, Divider, Stack, Alert
} from '@mui/material';
import { Shield, ShieldAlert, Key, Lock } from 'lucide-react';
import { useAuth } from '../../auth/AuthProvider';
import { TwoFASetupModal } from '../../auth/components/TwoFASetupModal';

export const SecurityConfig: React.FC = () => {
  const { user, refreshMe } = useAuth();
  const [setupModalOpen, setSetupModalOpen] = useState(false);

  const is2faEnabled = user?.is_2fa_enabled ?? false;

  return (
    <Box>
      <Typography variant="h6" fontWeight="bold" sx={{ mb: 3 }}>إعدادات الأمان المتقدمة</Typography>
      
      <Stack spacing={3}>
        <Card variant="outlined">
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Box>
                <Stack direction="row" alignItems="center" gap={1}>
                  <Key size={20} color={is2faEnabled ? "#2e7d32" : "#757575"} />
                  <Typography variant="subtitle1" fontWeight="bold">
                    التحقق الثنائي (Two-Factor Authentication)
                  </Typography>
                </Stack>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  إضافة طبقة حماية إضافية لحسابك عبر رمز يتم توليده على هاتفك.
                </Typography>
              </Box>
              <Box>
                {is2faEnabled ? (
                  <Chip label="مفعل" color="success" size="small" />
                ) : (
                  <Button variant="contained" size="small" onClick={() => setSetupModalOpen(true)}>
                    تفعيل الآن
                  </Button>
                )}
              </Box>
            </Stack>
          </CardContent>
        </Card>

        <Card variant="outlined">
          <CardContent>
            <Stack direction="row" alignItems="center" gap={1} sx={{ mb: 2 }}>
              <ShieldAlert size={20} color="#d32f2f" />
              <Typography variant="subtitle1" fontWeight="bold" color="error">
                منطقة الخطر
              </Typography>
            </Stack>
            <Divider sx={{ mb: 2 }} />
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="body2" fontWeight="bold">تغيير كلمة المرور</Typography>
                <Typography variant="caption" color="text.secondary">ينصح بتغييرها كل 3 أشهر</Typography>
              </Box>
              <Button variant="outlined" size="small" color="error">تغيير</Button>
            </Stack>
          </CardContent>
        </Card>

        {is2faEnabled && (
          <Alert severity="info" variant="outlined">
            إذا فقدت الوصول إلى تطبيق التحقق، يرجى استخدام أكواد النسخ الاحتياطي التي قمت بحفظها أثناء الإعداد.
          </Alert>
        )}
      </Stack>

      <TwoFASetupModal 
        open={setupModalOpen} 
        onClose={() => setSetupModalOpen(false)}
        onComplete={async () => {
          await refreshMe();
          setSetupModalOpen(false);
        }}
      />
    </Box>
  );
};

import { Chip } from '@mui/material';
