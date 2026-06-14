import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import PlayArrowOutlinedIcon from '@mui/icons-material/PlayArrowOutlined';
import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined';
import {
  Alert,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
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
  Tooltip,
  Typography,
} from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useState } from 'react';

import { SectionCard } from '../../../components/SectionCard';
import { useLanguage } from '../../language/LanguageProvider';
import {
  createDailyReportConfig,
  deleteDailyReportConfig,
  listDailyReportConfigs,
  testDailyReportConfig,
  updateDailyReportConfig,
  type DailyReportConfigRecord,
} from '../api';
import { queryClient } from '../../../lib/queryClient';

export function DailyReportsView() {
  const { language } = useLanguage();
  const isAr = language === 'ar';

  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState<DailyReportConfigRecord | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [testingId, setTestingId] = useState<string | null>(null);

  const configsQuery = useQuery({
    queryKey: ['settings', 'daily-reports'],
    queryFn: listDailyReportConfigs,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteDailyReportConfig,
    onSuccess: async () => {
      setMessage(isAr ? 'تم حذف إعدادات التقرير البريدي بنجاح.' : 'Email report configuration deleted successfully.');
      setError(null);
      await queryClient.invalidateQueries({ queryKey: ['settings', 'daily-reports'] });
    },
    onError: (err: Error) => {
      setError(err.message);
      setMessage(null);
    },
  });

  const handleOpenAdd = () => {
    setSelectedConfig(null);
    setDialogOpen(true);
  };

  const handleOpenEdit = (config: DailyReportConfigRecord) => {
    setSelectedConfig(config);
    setDialogOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm(isAr ? 'هل أنت متأكد من رغبتك في حذف هذا التكوين البريدي؟' : 'Are you sure you want to delete this email configuration?')) {
      await deleteMutation.mutateAsync(id);
    }
  };

  const handleTestDispatch = async (id: string) => {
    setTestingId(id);
    setMessage(null);
    setError(null);
    try {
      const res = await testDailyReportConfig(id);
      if (res.success) {
        setMessage(isAr ? 'تم إرسال بريد تجريبي بنجاح! تفقد صندوق الوارد.' : 'Test email dispatched successfully! Check inbox.');
      } else {
        setError(res.error || (isAr ? 'فشل إرسال البريد التجريبي.' : 'Failed to send test email.'));
      }
    } catch (err: any) {
      setError(err.message || 'Error occurred during test dispatch.');
    } finally {
      setTestingId(null);
    }
  };

  return (
    <Stack spacing={3}>
      {message ? <Alert severity='success'>{message}</Alert> : null}
      {error ? <Alert severity='error'>{error}</Alert> : null}

      <SectionCard
        title={isAr ? 'التقارير البريدية اليومية (Gmail)' : 'Daily Email Reports (Gmail)'}
        subtitle={isAr ? 'إدارة تقارير الحجوزات والتحصيلات اليومية وتشفيرها بشكل آمن ومحمي' : 'Manage and securely encrypt daily booking and payments report channels'}
      >
        <Stack spacing={3}>
          <Box display='flex' justifyContent='flex-end'>
            <Button
              variant='contained'
              startIcon={<AddOutlinedIcon />}
              onClick={handleOpenAdd}
            >
              {isAr ? 'إضافة إعدادات بريد جديدة' : 'Add New Email Config'}
            </Button>
          </Box>

          <TableContainer component={Paper} variant='outlined'>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><b>{isAr ? 'الاسم التعريفي' : 'Name'}</b></TableCell>
                  <TableCell><b>{isAr ? 'بريد المرسل (جيميل)' : 'Sender Email (Gmail)'}</b></TableCell>
                  <TableCell><b>{isAr ? 'بريد الاستلام' : 'Recipient Email(s)'}</b></TableCell>
                  <TableCell><b>{isAr ? 'ساعة الإرسال' : 'Send Hour'}</b></TableCell>
                  <TableCell><b>{isAr ? 'الحالة' : 'Status'}</b></TableCell>
                  <TableCell align='center'><b>{isAr ? 'العمليات' : 'Actions'}</b></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {configsQuery.isLoading ? (
                  <TableRow>
                    <TableCell colSpan={6} align='center'>
                      {isAr ? 'جاري تحميل البيانات...' : 'Loading configurations...'}
                    </TableCell>
                  </TableRow>
                ) : (configsQuery.data ?? []).length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align='center'>
                      {isAr ? 'لم يتم إضافة أي تكوينات تقارير بريدية بعد.' : 'No email report configurations added yet.'}
                    </TableCell>
                  </TableRow>
                ) : (
                  (configsQuery.data ?? []).map((config) => (
                    <TableRow key={config.id}>
                      <TableCell><b>{config.name}</b></TableCell>
                      <TableCell>{config.sender_email}</TableCell>
                      <TableCell>
                        <Tooltip title={config.recipient_email}>
                          <span>
                            {config.recipient_email.length > 35
                              ? `${config.recipient_email.substring(0, 35)}...`
                              : config.recipient_email}
                          </span>
                        </Tooltip>
                      </TableCell>
                      <TableCell>
                        {config.send_hour === 0 ? (isAr ? '12:00 صباحاً (منتصف الليل)' : '12:00 AM') :
                         config.send_hour === 12 ? (isAr ? '12:00 مساءً (الظهر)' : '12:00 PM') :
                         config.send_hour < 12 ? (isAr ? `${config.send_hour}:00 صباحاً` : `${config.send_hour}:00 AM`) :
                         (isAr ? `${config.send_hour - 12}:00 مساءً` : `${config.send_hour - 12}:00 PM`)}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={config.is_active ? (isAr ? 'نشط' : 'Active') : (isAr ? 'موقف' : 'Inactive')}
                          color={config.is_active ? 'success' : 'default'}
                          size='small'
                        />
                      </TableCell>
                      <TableCell align='center'>
                        <Stack direction='row' spacing={1} justifyContent='center'>
                          <Tooltip title={isAr ? 'تجربة إرسال الآن' : 'Test Dispatch Now'}>
                            <IconButton
                              size='small'
                              color='secondary'
                              onClick={() => void handleTestDispatch(config.id)}
                              disabled={testingId !== null}
                            >
                              <PlayArrowOutlinedIcon fontSize='small' />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title={isAr ? 'تعديل التكوين' : 'Edit'}>
                            <IconButton
                              size='small'
                              color='primary'
                              onClick={() => handleOpenEdit(config)}
                            >
                              <EditOutlinedIcon fontSize='small' />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title={isAr ? 'حذف' : 'Delete'}>
                            <IconButton
                              size='small'
                              color='error'
                              onClick={() => void handleDelete(config.id)}
                            >
                              <DeleteOutlinedIcon fontSize='small' />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Stack>
      </SectionCard>

      {dialogOpen ? (
        <DailyReportConfigDialog
          open={dialogOpen}
          config={selectedConfig}
          onClose={() => setDialogOpen(false)}
          isAr={isAr}
        />
      ) : null}
    </Stack>
  );
}

interface DialogProps {
  open: boolean;
  config: DailyReportConfigRecord | null;
  onClose: () => void;
  isAr: boolean;
}

function DailyReportConfigDialog({ open, config, onClose, isAr }: DialogProps) {
  const [name, setName] = useState('');
  const [senderEmail, setSenderEmail] = useState('');
  const [senderPassword, setSenderPassword] = useState('');
  const [recipientEmail, setRecipientEmail] = useState('');
  const [sendHour, setSendHour] = useState(21);
  const [isActive, setIsActive] = useState(true);
  
  const [sendDailySummary, setSendDailySummary] = useState(true);
  const [notifyBookingCreated, setNotifyBookingCreated] = useState(false);
  const [notifyBookingModified, setNotifyBookingModified] = useState(false);
  const [notifyPaymentCaptured, setNotifyPaymentCaptured] = useState(false);
  const [notifyPaymentRefunded, setNotifyPaymentRefunded] = useState(false);
  const [notifyEntityDeleted, setNotifyEntityDeleted] = useState(true);
  const [notifyOperationsDaily, setNotifyOperationsDaily] = useState(true);
  const [notifyFinancialCritical, setNotifyFinancialCritical] = useState(true);
  const [notifyBackupWarnings, setNotifyBackupWarnings] = useState(true);
  const [bookingEmailTemplate, setBookingEmailTemplate] = useState('detailed');
  const [paymentEmailTemplate, setPaymentEmailTemplate] = useState('detailed');

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (config) {
      setName(config.name);
      setSenderEmail(config.sender_email);
      setSenderPassword(config.sender_password);
      setRecipientEmail(config.recipient_email);
      setSendHour(config.send_hour);
      setIsActive(config.is_active);
      setSendDailySummary(config.send_daily_summary ?? true);
      setNotifyBookingCreated(config.notify_booking_created ?? false);
      setNotifyBookingModified(config.notify_booking_modified ?? false);
      setNotifyPaymentCaptured(config.notify_payment_captured ?? false);
      setNotifyPaymentRefunded(config.notify_payment_refunded ?? false);
      setNotifyEntityDeleted(config.notify_entity_deleted ?? true);
      setNotifyOperationsDaily(config.notify_operations_daily ?? true);
      setNotifyFinancialCritical(config.notify_financial_critical ?? true);
      setNotifyBackupWarnings(config.notify_backup_warnings ?? true);
      setBookingEmailTemplate(config.booking_email_template ?? 'detailed');
      setPaymentEmailTemplate(config.payment_email_template ?? 'detailed');
    } else {
      setName('');
      setSenderEmail('');
      setSenderPassword('');
      setRecipientEmail('');
      setSendHour(21);
      setIsActive(true);
      setSendDailySummary(true);
      setNotifyBookingCreated(false);
      setNotifyBookingModified(false);
      setNotifyPaymentCaptured(false);
      setNotifyPaymentRefunded(false);
      setNotifyEntityDeleted(true);
      setNotifyOperationsDaily(true);
      setNotifyFinancialCritical(true);
      setNotifyBackupWarnings(true);
      setBookingEmailTemplate('detailed');
      setPaymentEmailTemplate('detailed');
    }
  }, [config]);

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        name,
        sender_email: senderEmail,
        sender_password: senderPassword,
        recipient_email: recipientEmail,
        send_hour: sendHour,
        is_active: isActive,
        smtp_server: 'smtp.gmail.com',
        smtp_port: 587,
        send_daily_summary: sendDailySummary,
        notify_booking_created: notifyBookingCreated,
        notify_booking_modified: notifyBookingModified,
        notify_payment_captured: notifyPaymentCaptured,
        notify_payment_refunded: notifyPaymentRefunded,
        notify_entity_deleted: notifyEntityDeleted,
        notify_operations_daily: notifyOperationsDaily,
        notify_financial_critical: notifyFinancialCritical,
        notify_backup_warnings: notifyBackupWarnings,
        booking_email_template: bookingEmailTemplate,
        payment_email_template: paymentEmailTemplate,
      };
      if (config) {
        await updateDailyReportConfig(config.id, payload);
      } else {
        await createDailyReportConfig(payload);
      }
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['settings', 'daily-reports'] });
      onClose();
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const handleSave = () => {
    if (!name.trim()) {
      setError(isAr ? 'الرجاء إدخال الاسم التعريفي.' : 'Please enter configuration name.');
      return;
    }
    if (!senderEmail.trim()) {
      setError(isAr ? 'الرجاء إدخال بريد المرسل.' : 'Please enter sender email.');
      return;
    }
    if (!senderPassword.trim()) {
      setError(isAr ? 'الرجاء إدخال كلمة مرور التطبيق.' : 'Please enter App Password.');
      return;
    }
    if (!recipientEmail.trim()) {
      setError(isAr ? 'الرجاء إدخال بريد الاستلام.' : 'Please enter recipient email.');
      return;
    }
    setError(null);
    void saveMutation.mutateAsync();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth='md' fullWidth>
      <DialogTitle>
        {config
          ? (isAr ? 'تعديل إعدادات التقرير البريدي وتفضيلات التنبيهات' : 'Edit Email Report & Notification Config')
          : (isAr ? 'إضافة إعدادات وتفضيلات تنبيهات بريدية جديدة' : 'Add New Email Report & Notification Config')}
      </DialogTitle>
      <DialogContent dividers>
        <Stack spacing={3}>
          {error ? <Alert severity='error'>{error}</Alert> : null}

          <Alert severity='info' sx={{ whiteSpace: 'pre-line' }}>
            {isAr ? (
              <>
                <strong>طريقة توليد كلمة مرور التطبيق (App Password) لحساب Gmail:</strong>
                {"\n"}1. تأكد من تفعيل ميزة <strong>التحقق بخطوتين (2-Step Verification)</strong> في إعدادات أمان حساب Google للمرسل.
                {"\n"}2. انتقل إلى <strong>أمان حساب جوجل (Google Account Security)</strong> ثم ابحث عن قسم <strong>كلمات مرور التطبيقات (App Passwords)</strong>.
                {"\n"}3. قم بإنشاء تطبيق جديد بالاسم الذي تفضله (مثل <i>MyAtelier Pro</i>).
                {"\n"}4. سيظهر لك كود مكون من 16 حرفاً، قم بنسخه ولصقه في حقل <strong>"كلمة مرور التطبيق"</strong> أدناه.
              </>
            ) : (
              <>
                <strong>How to generate a Google App Password for Gmail:</strong>
                {"\n"}1. Make sure <strong>2-Step Verification</strong> is enabled in your Google Account Security settings.
                {"\n"}2. Go to your Google account page, search for <strong>App Passwords</strong>.
                {"\n"}3. Create a new App Password, selecting a custom name (e.g. <i>MyAtelier Pro</i>).
                {"\n"}4. Copy the generated 16-character code and paste it in the <strong>"App Password"</strong> field below.
              </>
            )}
          </Alert>

          <Typography variant='subtitle1' color='primary' sx={{ fontWeight: 'bold' }}>
            {isAr ? '1. إعدادات الخادم والاتصال الأساسية' : '1. Connection & Server Settings'}
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                label={isAr ? 'الاسم التعريفي (تقرير الإدارة المالي)' : 'Configuration Name'}
                value={name}
                onChange={(e) => setName(e.target.value)}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label={isAr ? 'الحالة' : 'Status'}
                select
                SelectProps={{ native: true }}
                value={isActive ? 'true' : 'false'}
                onChange={(e) => setIsActive(e.target.value === 'true')}
                fullWidth
              >
                <option value='true'>{isAr ? 'نشط' : 'Active'}</option>
                <option value='false'>{isAr ? 'موقف' : 'Inactive'}</option>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label={isAr ? 'بريد المرسل (جيميل)' : 'Sender Email (Gmail)'}
                type='email'
                placeholder='example@gmail.com'
                value={senderEmail}
                onChange={(e) => setSenderEmail(e.target.value)}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label={isAr ? 'كلمة مرور التطبيق (App Password)' : 'App Password (16 characters)'}
                type='password'
                value={senderPassword}
                placeholder='xxxx xxxx xxxx xxxx'
                onChange={(e) => setSenderPassword(e.target.value)}
                helperText={config ? (isAr ? 'اتركها دون تغيير (نجوم) إذا كنت لا ترغب في تعديلها.' : 'Leave as is (stars) if you do not want to modify it.') : undefined}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} sm={8}>
              <TextField
                label={isAr ? 'بريد الاستلام (إيميلات متعددة مفصولة بفاصلة)' : 'Recipient Email(s) (comma-separated)'}
                placeholder='admin@example.com, owner@example.com'
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                select
                SelectProps={{ native: true }}
                label={isAr ? 'ساعة الإرسال اليومي (توقيت محلي)' : 'Daily Send Hour (Local Time)'}
                value={sendHour}
                onChange={(e) => setSendHour(parseInt(e.target.value, 10))}
                fullWidth
              >
                {Array.from({ length: 24 }).map((_, h) => (
                  <option key={h} value={h}>
                    {h === 0 ? (isAr ? '12:00 صباحاً (منتصف الليل)' : '12:00 AM') :
                     h === 12 ? (isAr ? '12:00 مساءً (الظهر)' : '12:00 PM') :
                     h < 12 ? (isAr ? `${h}:00 صباحاً` : `${h}:00 AM`) :
                     (isAr ? `${h - 12}:00 مساءً` : `${h - 12}:00 PM`)}
                  </option>
                ))}
              </TextField>
            </Grid>
          </Grid>

          <Typography variant='subtitle1' color='primary' sx={{ fontWeight: 'bold', mt: 2 }}>
            {isAr ? '2. إعدادات الملخصات والتقارير الدورية' : '2. Periodic Digests & Summaries'}
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                SelectProps={{ native: true }}
                label={isAr ? 'إرسال التقرير المالي اليومي العام' : 'Send Daily Financial Summary'}
                value={sendDailySummary ? 'true' : 'false'}
                onChange={(e) => setSendDailySummary(e.target.value === 'true')}
                fullWidth
              >
                <option value='true'>{isAr ? 'نعم (موصى به)' : 'Yes (Recommended)'}</option>
                <option value='false'>{isAr ? 'لا' : 'No'}</option>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                SelectProps={{ native: true }}
                label={isAr ? 'إرسال الملخص التشغيلي اليومي (الصباحي)' : 'Send Morning Operations Digest'}
                value={notifyOperationsDaily ? 'true' : 'false'}
                onChange={(e) => setNotifyOperationsDaily(e.target.value === 'true')}
                fullWidth
              >
                <option value='true'>{isAr ? 'نعم (موصى به)' : 'Yes (Recommended)'}</option>
                <option value='false'>{isAr ? 'لا' : 'No'}</option>
              </TextField>
            </Grid>
          </Grid>

          <Typography variant='subtitle1' color='primary' sx={{ fontWeight: 'bold', mt: 2 }}>
            {isAr ? '3. التنبيهات اللحظية للأحداث (الحجوزات والمالية)' : '3. Instant Alerts (Bookings & Cash Flow)'}
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                SelectProps={{ native: true }}
                label={isAr ? 'تنبيه عند إضافة حجز جديد' : 'Alert on New Booking'}
                value={notifyBookingCreated ? 'true' : 'false'}
                onChange={(e) => setNotifyBookingCreated(e.target.value === 'true')}
                fullWidth
              >
                <option value='false'>{isAr ? 'إيقاف التنبيه' : 'Disabled'}</option>
                <option value='true'>{isAr ? 'تفعيل التنبيه الفوري' : 'Enabled'}</option>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                SelectProps={{ native: true }}
                label={isAr ? 'تنبيه عند تعديل / إلغاء حجز قائم' : 'Alert on Booking Modification'}
                value={notifyBookingModified ? 'true' : 'false'}
                onChange={(e) => setNotifyBookingModified(e.target.value === 'true')}
                fullWidth
              >
                <option value='false'>{isAr ? 'إيقاف التنبيه' : 'Disabled'}</option>
                <option value='true'>{isAr ? 'تفعيل التنبيه الفوري' : 'Enabled'}</option>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                SelectProps={{ native: true }}
                label={isAr ? 'تنبيه عند استلام دفعة مالية (سند قبض)' : 'Alert on Payment Capture (Receipt)'}
                value={notifyPaymentCaptured ? 'true' : 'false'}
                onChange={(e) => setNotifyPaymentCaptured(e.target.value === 'true')}
                fullWidth
              >
                <option value='false'>{isAr ? 'إيقاف التنبيه' : 'Disabled'}</option>
                <option value='true'>{isAr ? 'تفعيل التنبيه الفوري' : 'Enabled'}</option>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                SelectProps={{ native: true }}
                label={isAr ? 'تنبيه عند صرف أو إرجاع مبالغ (سند صرف)' : 'Alert on Refund / Void (Disbursement)'}
                value={notifyPaymentRefunded ? 'true' : 'false'}
                onChange={(e) => setNotifyPaymentRefunded(e.target.value === 'true')}
                fullWidth
              >
                <option value='false'>{isAr ? 'إيقاف التنبيه' : 'Disabled'}</option>
                <option value='true'>{isAr ? 'تفعيل التنبيه الفوري' : 'Enabled'}</option>
              </TextField>
            </Grid>
          </Grid>

          <Typography variant='subtitle1' color='primary' sx={{ fontWeight: 'bold', mt: 2 }}>
            {isAr ? '4. تنبيهات الأمن والسلامة وإدارة النظام' : '4. Security, Backups & Fiscal Auditing'}
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <TextField
                select
                SelectProps={{ native: true }}
                label={isAr ? 'تنبيه أمني عند حذف أي عنصر' : 'Alert on Data Deletion'}
                value={notifyEntityDeleted ? 'true' : 'false'}
                onChange={(e) => setNotifyEntityDeleted(e.target.value === 'true')}
                fullWidth
              >
                <option value='true'>{isAr ? 'تفعيل (موصى به)' : 'Enabled (Recommended)'}</option>
                <option value='false'>{isAr ? 'تعطيل' : 'Disabled'}</option>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                select
                SelectProps={{ native: true }}
                label={isAr ? 'تنبيه أمني عند إغلاق الفترات / القيود اليدوية' : 'Alert on Fiscal Lock & JV'}
                value={notifyFinancialCritical ? 'true' : 'false'}
                onChange={(e) => setNotifyFinancialCritical(e.target.value === 'true')}
                fullWidth
              >
                <option value='true'>{isAr ? 'تفعيل (موصى به)' : 'Enabled (Recommended)'}</option>
                <option value='false'>{isAr ? 'تعطيل' : 'Disabled'}</option>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                select
                SelectProps={{ native: true }}
                label={isAr ? 'تنبيه عند فشل أو تأخر النسخ الاحتياطي' : 'Alert on Backup Failure/Stale'}
                value={notifyBackupWarnings ? 'true' : 'false'}
                onChange={(e) => setNotifyBackupWarnings(e.target.value === 'true')}
                fullWidth
              >
                <option value='true'>{isAr ? 'تفعيل (موصى به)' : 'Enabled (Recommended)'}</option>
                <option value='false'>{isAr ? 'تعطيل' : 'Disabled'}</option>
              </TextField>
            </Grid>
          </Grid>

          <Typography variant='subtitle1' color='primary' sx={{ fontWeight: 'bold', mt: 2 }}>
            {isAr ? '5. تخصيص قوالب الإيميلات المرسلة' : '5. Email Notification Templates'}
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                SelectProps={{ native: true }}
                label={isAr ? 'شكل قالب إيميل الحجوزات' : 'Booking Notification Template'}
                value={bookingEmailTemplate}
                onChange={(e) => setBookingEmailTemplate(e.target.value)}
                fullWidth
              >
                <option value='detailed'>{isAr ? 'تفصيلي (يحتوي على تفاصيل الخدمات والفساتين)' : 'Detailed (Services & Dresses)'}</option>
                <option value='basic'>{isAr ? 'مختصر (معلومات الحجز الأساسية والإجمالي)' : 'Basic (Totals Only)'}</option>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                SelectProps={{ native: true }}
                label={isAr ? 'شكل قالب إيميل السندات المالية' : 'Payment Notification Template'}
                value={paymentEmailTemplate}
                onChange={(e) => setPaymentEmailTemplate(e.target.value)}
                fullWidth
              >
                <option value='detailed'>{isAr ? 'تفصيلي (يحتوي على توزيع المبالغ على المواعيد)' : 'Detailed (Allocation breakdown)'}</option>
                <option value='basic'>{isAr ? 'مختصر (المبلغ الكلي وطريقة الدفع)' : 'Basic (Total & Method)'}</option>
              </TextField>
            </Grid>
          </Grid>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color='inherit'>
          {isAr ? 'إلغاء' : 'Cancel'}
        </Button>
        <Button
          variant='contained'
          onClick={handleSave}
          disabled={saveMutation.isPending}
          startIcon={<SaveOutlinedIcon />}
        >
          {isAr ? 'حفظ' : 'Save'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
