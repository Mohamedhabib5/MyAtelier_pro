import { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Card, 
  CardContent, 
  Stack, 
  IconButton, 
  Chip, 
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  Alert,
  alpha,
  useTheme
} from '@mui/material';
import { 
  Database, 
  FileArchive, 
  Server, 
  Download, 
  Trash2, 
  RefreshCcw,
  Plus,
  HardDrive
} from 'lucide-react';
import { format } from 'date-fns';
import { ar, enUS } from 'date-fns/locale';

import { useLanguage } from '../../features/language/LanguageProvider';
import { apiRequest, downloadFile } from '../../lib/api';
import { useThemeSettings } from '../../features/theme/ThemeSettingsProvider';

interface BackupInfo {
  id: string;
  filename: string;
  size_bytes: number;
  created_at: string;
  kind: 'db' | 'media' | 'full';
}

export default function BackupPage() {
  const { language, direction } = useLanguage();
  const { primaryColor, accentColor, themeMode } = useThemeSettings();
  const theme = useTheme();
  const isRtl = direction === 'rtl';
  const isDark = themeMode === 'dark';

  const [backups, setBackups] = useState<BackupInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchBackups = async () => {
    try {
      setLoading(true);
      const data = await apiRequest<BackupInfo[]>('/api/ops/backups');
      setBackups(data);
      setError(null);
    } catch (err: unknown) {
      setError((err as any).message || 'Failed to fetch backups');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBackups();
  }, []);

  const handleCreateBackup = async (kind: 'db' | 'media' | 'full') => {
    try {
      setCreating(kind);
      await apiRequest<void>(`/api/ops/backups/${kind}`, { method: 'POST' });
      await fetchBackups();
    } catch (err: unknown) {
      setError((err as any).message || 'Failed to create backup');
    } finally {
      setCreating(null);
    }
  };

  const handleDeleteBackup = async (filename: string) => {
    if (!window.confirm(language === 'ar' ? 'هل أنت متأكد من حذف هذه النسخة؟' : 'Are you sure you want to delete this backup?')) return;
    try {
      await apiRequest<void>(`/api/ops/backups/${filename}`, { method: 'DELETE' });
      await fetchBackups();
    } catch (err: unknown) {
      setError((err as any).message || 'Failed to delete backup');
    }
  };

  const handleDownload = async (filename: string) => {
    await downloadFile(`/api/ops/backups/${filename}/download`);
  };

  const formatSize = (bytes: number) => {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    while (size > 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    return `${size.toFixed(2)} ${units[unitIndex]}`;
  };

  const getKindLabel = (kind: string) => {
    if (language === 'ar') {
      switch (kind) {
        case 'db': return 'قاعدة البيانات';
        case 'media': return 'الوسائط (الصور)';
        case 'full': return 'نسخة شاملة';
        default: return kind;
      }
    }
    return kind.toUpperCase();
  };

  const getKindIcon = (kind: string) => {
    switch (kind) {
      case 'db': return <Database size={18} />;
      case 'media': return <HardDrive size={18} />;
      case 'full': return <Server size={18} />;
      default: return <FileArchive size={18} />;
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: { xs: 1, md: 3 } }}>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="space-between" alignItems={{ xs: 'stretch', sm: 'center' }} sx={{ mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 900, letterSpacing: -1, color: primaryColor }}>
            {language === 'ar' ? 'إدارة النسخ الاحتياطي' : 'Backup Management'}
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.6 }}>
            {language === 'ar' ? 'تأمين بيانات النظام والملفات' : 'Secure your system data and files'}
          </Typography>
        </Box>
        <Button 
          variant="outlined" 
          onClick={fetchBackups} 
          disabled={loading}
          startIcon={<RefreshCcw size={18} />}
          sx={{ borderRadius: 4, alignSelf: { xs: 'stretch', sm: 'auto' } }}
        >
          {language === 'ar' ? 'تحديث' : 'Refresh'}
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: 4 }}>
          {error}
        </Alert>
      )}

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={3} sx={{ mb: 6 }}>
        <Card sx={{ 
          flex: 1, 
          borderRadius: 6, 
          background: `linear-gradient(135deg, ${alpha(primaryColor, 0.05)}, ${alpha(primaryColor, 0.1)})`,
          border: `1px solid ${alpha(primaryColor, 0.1)}`,
          position: 'relative',
          overflow: 'hidden'
        }}>
          <CardContent>
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
              <Box sx={{ p: 1.5, bgcolor: alpha(primaryColor, 0.1), borderRadius: 3, color: primaryColor }}>
                <Database />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 800 }}>
                {language === 'ar' ? 'قاعدة البيانات' : 'Database'}
              </Typography>
            </Stack>
            <Typography variant="body2" sx={{ mb: 3, opacity: 0.7 }}>
              {language === 'ar' ? 'نسخة سريعة من كل البيانات والمعاملات' : 'Quick dump of all data and transactions'}
            </Typography>
            <Button 
              fullWidth 
              variant="contained" 
              onClick={() => handleCreateBackup('db')}
              disabled={!!creating}
              startIcon={creating === 'db' ? <CircularProgress size={16} color="inherit" /> : <Plus size={18} />}
              sx={{ borderRadius: 3, py: 1.5, bgcolor: primaryColor }}
            >
              {language === 'ar' ? 'إنشاء نسخة الآن' : 'Create Now'}
            </Button>
          </CardContent>
        </Card>

        <Card sx={{ 
          flex: 1, 
          borderRadius: 6, 
          background: `linear-gradient(135deg, ${alpha(accentColor || '#DFFF00', 0.05)}, ${alpha(accentColor || '#DFFF00', 0.1)})`,
          border: `1px solid ${alpha(accentColor || '#DFFF00', 0.1)}`,
        }}>
          <CardContent>
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
              <Box sx={{ p: 1.5, bgcolor: alpha(accentColor || '#DFFF00', 0.1), borderRadius: 3, color: accentColor }}>
                <HardDrive />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 800 }}>
                {language === 'ar' ? 'ملفات الوسائط' : 'Media Files'}
              </Typography>
            </Stack>
            <Typography variant="body2" sx={{ mb: 3, opacity: 0.7 }}>
              {language === 'ar' ? 'أرشفة كافة صور الفساتين والملحقات' : 'Archive all dress photos and attachments'}
            </Typography>
            <Button 
              fullWidth 
              variant="contained" 
              onClick={() => handleCreateBackup('media')}
              disabled={!!creating}
              startIcon={creating === 'media' ? <CircularProgress size={16} color="inherit" /> : <Plus size={18} />}
              sx={{ borderRadius: 3, py: 1.5, bgcolor: accentColor, color: '#000', '&:hover': { bgcolor: alpha(accentColor || '#DFFF00', 0.8) } }}
            >
              {language === 'ar' ? 'أرشفة الصور' : 'Archive Media'}
            </Button>
          </CardContent>
        </Card>

        <Card sx={{ 
          flex: 1, 
          borderRadius: 6, 
          background: `linear-gradient(135deg, ${alpha('#6366f1', 0.05)}, ${alpha('#6366f1', 0.1)})`,
          border: `1px solid ${alpha('#6366f1', 0.1)}`,
        }}>
          <CardContent>
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
              <Box sx={{ p: 1.5, bgcolor: alpha('#6366f1', 0.1), borderRadius: 3, color: '#6366f1' }}>
                <Server />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 800 }}>
                {language === 'ar' ? 'نسخة شاملة' : 'Full Backup'}
              </Typography>
            </Stack>
            <Typography variant="body2" sx={{ mb: 3, opacity: 0.7 }}>
              {language === 'ar' ? 'تجميع البيانات والوسائط في ملف واحد' : 'Combine data and media in one file'}
            </Typography>
            <Button 
              fullWidth 
              variant="contained" 
              onClick={() => handleCreateBackup('full')}
              disabled={!!creating}
              startIcon={creating === 'full' ? <CircularProgress size={16} color="inherit" /> : <Plus size={18} />}
              sx={{ borderRadius: 3, py: 1.5, bgcolor: '#6366f1' }}
            >
              {language === 'ar' ? 'نسخ النظام بالكامل' : 'Full System Backup'}
            </Button>
          </CardContent>
        </Card>
      </Stack>

      <Typography variant="h5" sx={{ fontWeight: 800, mb: 3 }}>
        {language === 'ar' ? 'الأرشيف المتاح' : 'Available Archives'}
      </Typography>

      <TableContainer component={Paper} sx={{ 
        borderRadius: 5, 
        overflowX: 'auto',
        border: isDark ? '1px solid rgba(255,255,255,0.05)' : '1px solid rgba(0,0,0,0.05)',
        boxShadow: 'none',
        bgcolor: 'transparent'
      }}>
        <Table sx={{ minWidth: 650 }}>
          <TableHead sx={{ bgcolor: isDark ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)' }}>
            <TableRow>
              <TableCell align={isRtl ? 'right' : 'left'}>{language === 'ar' ? 'النوع' : 'Kind'}</TableCell>
              <TableCell align={isRtl ? 'right' : 'left'}>{language === 'ar' ? 'اسم الملف' : 'Filename'}</TableCell>
              <TableCell align={isRtl ? 'right' : 'left'}>{language === 'ar' ? 'التاريخ' : 'Date'}</TableCell>
              <TableCell align={isRtl ? 'right' : 'left'}>{language === 'ar' ? 'الحجم' : 'Size'}</TableCell>
              <TableCell align="center">{language === 'ar' ? 'الإجراءات' : 'Actions'}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ py: 8 }}>
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : backups.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ py: 8 }}>
                  <Typography sx={{ opacity: 0.5 }}>
                    {language === 'ar' ? 'لا يوجد نسخ احتياطية حتى الآن' : 'No backups created yet'}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              backups.map((backup) => (
                <TableRow key={backup.id} sx={{ '&:hover': { bgcolor: isDark ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.01)' } }}>
                  <TableCell align={isRtl ? 'right' : 'left'}>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Box sx={{ color: backup.kind === 'full' ? '#6366f1' : backup.kind === 'db' ? primaryColor : accentColor }}>
                        {getKindIcon(backup.kind)}
                      </Box>
                      <Chip 
                        label={getKindLabel(backup.kind)} 
                        size="small" 
                        sx={{ fontWeight: 700, borderRadius: 2 }} 
                      />
                    </Stack>
                  </TableCell>
                  <TableCell align={isRtl ? 'right' : 'left'} sx={{ fontWeight: 500, fontFamily: 'monospace' }}>
                    {backup.filename}
                  </TableCell>
                  <TableCell align={isRtl ? 'right' : 'left'}>
                    {format(new Date(backup.created_at), 'PPP pp', { locale: language === 'ar' ? ar : enUS })}
                  </TableCell>
                  <TableCell align={isRtl ? 'right' : 'left'}>
                    <Typography variant="caption" sx={{ fontWeight: 800 }}>
                      {formatSize(backup.size_bytes)}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Stack direction="row" spacing={1} justifyContent="center">
                      <Tooltip title={language === 'ar' ? 'تحميل' : 'Download'}>
                        <IconButton aria-label={language === 'ar' ? 'تنزيل' : 'Download'} size="small" onClick={() => handleDownload(backup.filename)} sx={{ color: primaryColor }}>
                          <Download size={18} />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title={language === 'ar' ? 'حذف' : 'Delete'}>
                        <IconButton aria-label={language === 'ar' ? 'حذف' : 'Delete'} size="small" onClick={() => handleDeleteBackup(backup.filename)} color="error">
                          <Trash2 size={18} />
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
    </Box>
  );
}
