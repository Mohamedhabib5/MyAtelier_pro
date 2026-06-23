import { useState } from 'react';
import { Button, TextField, Stack, Alert, CircularProgress } from '@mui/material';
import { AppDialogShell } from '../../components/AppDialogShell';
import { listDepartments, createService, type ServiceRecord } from '../catalog/api';
import { useLanguage } from '../language/LanguageProvider';

type QuickAddServiceDialogProps = {
  open: boolean;
  onClose: () => void;
  onServiceAdded: (service: ServiceRecord) => void;
};

export function QuickAddServiceDialog({ open, onClose, onServiceAdded }: QuickAddServiceDialogProps) {
  const { language } = useLanguage();
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    if (!name.trim()) {
      setError(language === 'ar' ? 'اسم الخدمة مطلوب' : 'Service name is required');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      // 1. Fetch departments to find the dress department
      const depts = await listDepartments('active');
      const dressDept = depts.find(d => d.is_dress_department);
      
      if (!dressDept) {
        throw new Error(
          language === 'ar' 
            ? 'لم يتم العثور على قسم الفساتين في دليل الخدمات. يرجى تفعيل قسم الفساتين أولاً.' 
            : 'Dress department not found in the service catalog. Please configure it first.'
        );
      }

      // 2. Create the service
      const newService = await createService({
        department_id: dressDept.id,
        name: name.trim(),
        default_price: 0,
        display_order: 0
      });

      onServiceAdded(newService);
      setName('');
      onClose();
    } catch (err: unknown) {
      setError((err as any).message || 'Error creating service');
    } finally {
      setSaving(false);
    }
  };

  const labels = language === 'ar' ? {
    title: 'إضافة نوع فستان سريع',
    name: 'اسم النوع الجديد (مثال: حنة، خطوبة، سواريه)',
    cancel: 'إلغاء',
    save: 'حفظ',
  } : {
    title: 'Quick Add Dress Type',
    name: 'New Type Name (e.g. Henna, Soiree, Engagement)',
    cancel: 'Cancel',
    save: 'Save',
  };

  return (
    <AppDialogShell
      open={open}
      onClose={onClose}
      title={labels.title}
      actions={
        <>
          <Button onClick={onClose} disabled={saving}>{labels.cancel}</Button>
          <Button 
            variant="contained" 
            onClick={handleSave} 
            disabled={saving}
            startIcon={saving ? <CircularProgress size={20} color="inherit" /> : null}
          >
            {labels.save}
          </Button>
        </>
      }
    >
      <Stack spacing={2} sx={{ mt: 1, minWidth: { xs: 280, sm: 400 } }}>
        {error && <Alert severity="error">{error}</Alert>}
        <TextField
          autoFocus
          label={labels.name}
          value={name}
          onChange={(e) => setName(e.target.value)}
          disabled={saving}
          fullWidth
        />
      </Stack>
    </AppDialogShell>
  );
}
