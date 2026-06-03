import { Button, Stack, TextField, Box, IconButton, Typography, CircularProgress } from '@mui/material';
import { PhotoCamera, Delete, Add as AddIcon } from '@mui/icons-material';
import { useState, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';

import { AppDialogShell } from '../../components/AppDialogShell';
import { useLanguage } from '../language/LanguageProvider';
import { useCommonText } from '../../text/common';
import { dressStatusLabel, useDressesText } from '../../text/dresses';
import { AppDateField } from '../../components/inputs/AppDateField';
import { uploadDressImage } from './api';
import { listDepartments, listServices, type ServiceRecord } from '../catalog/api';
import { QuickAddServiceDialog } from './QuickAddServiceDialog';
import { queryClient } from '../../lib/queryClient';

export type DressFormState = {
  code: string;
  name: string;
  dress_type_id: string;
  purchase_date: string;
  status: string;
  description: string;
  image_path: string;
  is_active: boolean;
};

type DressFormDialogProps = {
  open: boolean;
  editing: boolean;
  form: DressFormState;
  onChange: (next: DressFormState) => void;
  onClose: () => void;
  onSave: () => void;
};

export function DressFormDialog({ open, editing, form, onChange, onClose, onSave }: DressFormDialogProps) {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const dressesText = useDressesText();
  const [uploading, setUploading] = useState(false);
  const [quickAddOpen, setQuickAddOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch departments to identify the dresses department
  const deptsQuery = useQuery({
    queryKey: ['catalog', 'departments', 'active'],
    queryFn: () => listDepartments('active'),
    enabled: open,
  });

  // Fetch services
  const servicesQuery = useQuery({
    queryKey: ['catalog', 'services', 'active'],
    queryFn: () => listServices('active'),
    enabled: open,
  });

  // Fetch company settings to know the dresses mode
  const companyQuery = useQuery({
    queryKey: ['settings', 'company'],
    queryFn: () => import('../settings/api').then(m => m.getCompany()),
    enabled: open,
  });

  const dressesMode = companyQuery.data?.dresses_mode ?? 'free';
  const dressDept = deptsQuery.data?.find(d => d.is_dress_department);
  const dressServices = (servicesQuery.data ?? []).filter(s => s.department_id === dressDept?.id);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.size > 307200) {
      alert(dressesText.dialog.invalidSize);
      return;
    }

    if (!file.type.startsWith('image/')) {
      alert(dressesText.dialog.invalidType);
      return;
    }

    try {
      setUploading(true);
      const { image_path } = await uploadDressImage(file);
      onChange({ ...form, image_path });
    } catch (error: any) {
      alert(error.message || 'Error uploading image');
    } finally {
      setUploading(false);
    }
  };

  const removeImage = () => {
    onChange({ ...form, image_path: '' });
  };

  const handleServiceAdded = (newService: ServiceRecord) => {
    void queryClient.invalidateQueries({ queryKey: ['catalog', 'services'] });
    onChange({ ...form, dress_type_id: newService.id });
  };

  const backendUrl = `${window.location.protocol}//${window.location.hostname}:8000`;
  const imageUrl = form.image_path ? (form.image_path.startsWith('http') ? form.image_path : `${backendUrl}/attachments/${form.image_path}`) : null;

  return (
    <>
      <AppDialogShell
        open={open}
        onClose={onClose}
        title={editing ? dressesText.dialog.edit : dressesText.dialog.create}
        actions={
          <>
            <Button onClick={onClose}>{commonText.cancel}</Button>
            <Button variant='contained' onClick={onSave}>
              {commonText.save}
            </Button>
          </>
        }
      >
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField label={dressesText.dialog.code} value={form.code} onChange={(event) => onChange({ ...form, code: event.target.value })} />
          <TextField label={dressesText.dialog.name} value={form.name} onChange={(event) => onChange({ ...form, name: event.target.value })} />
          
          {dressesMode === 'coupled' && (
            <Stack direction='row' spacing={1} alignItems='center'>
              <TextField
                select
                SelectProps={{ native: true }}
                InputLabelProps={{ shrink: true }}
                label={dressesText.dialog.type}
                value={form.dress_type_id}
                onChange={(event) => onChange({ ...form, dress_type_id: event.target.value })}
                fullWidth
                disabled={servicesQuery.isLoading || deptsQuery.isLoading}
              >
                <option value="">
                  {servicesQuery.isLoading || deptsQuery.isLoading
                    ? (language === 'ar' ? 'جاري التحميل...' : 'Loading...')
                    : (language === 'ar' ? '-- اختر نوع الفستان --' : '-- Select Dress Type --')}
                </option>
                {dressServices.map(s => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </TextField>
              <IconButton
                color="primary"
                onClick={() => setQuickAddOpen(true)}
                sx={{
                  bgcolor: 'action.hover',
                  border: '1px solid',
                  borderColor: 'divider',
                }}
              >
                <AddIcon />
              </IconButton>
            </Stack>
          )}

          <AppDateField label={dressesText.dialog.purchaseDate} value={form.purchase_date} onChange={(val) => onChange({ ...form, purchase_date: val })} />
          <TextField select SelectProps={{ native: true }} InputLabelProps={{ shrink: true }} label={dressesText.dialog.status} value={form.status} onChange={(event) => onChange({ ...form, status: event.target.value })}>
            <option value='available'>{dressStatusLabel(language, 'available')}</option>
            <option value='reserved'>{dressStatusLabel(language, 'reserved')}</option>
            <option value='with_customer'>{dressStatusLabel(language, 'with_customer')}</option>
            <option value='maintenance'>{dressStatusLabel(language, 'maintenance')}</option>
          </TextField>
          <TextField label={dressesText.dialog.description} value={form.description} multiline minRows={3} onChange={(event) => onChange({ ...form, description: event.target.value })} />
          
          <Box>
            <Typography variant='caption' color='textSecondary' display='block' sx={{ mb: 1 }}>
              {dressesText.dialog.imageRef}
            </Typography>
            <Stack direction='row' spacing={2} alignItems='center'>
              {imageUrl ? (
                <Box sx={{ position: 'relative', width: 100, height: 100 }}>
                  <Box
                    component='img'
                    src={imageUrl}
                    alt='Dress'
                    sx={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                      borderRadius: 1,
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  />
                  <IconButton
                    size='small'
                    color='error'
                    onClick={removeImage}
                    sx={{
                      position: 'absolute',
                      top: -8,
                      right: -8,
                      bgcolor: 'background.paper',
                      boxShadow: 1,
                      '&:hover': { bgcolor: 'background.paper' },
                    }}
                  >
                    <Delete fontSize='small' />
                  </IconButton>
                </Box>
              ) : (
                <Button
                  variant='outlined'
                  component='label'
                  startIcon={uploading ? <CircularProgress size={20} /> : <PhotoCamera />}
                  disabled={uploading}
                  sx={{ width: 100, height: 100, flexDirection: 'column', gap: 1 }}
                >
                  {dressesText.dialog.uploadButton}
                  <input type='file' hidden accept='image/*' ref={fileInputRef} onChange={handleFileChange} />
                </Button>
              )}
              <Typography variant='caption' color='textSecondary'>
                {dressesText.dialog.imageHint}
              </Typography>
            </Stack>
          </Box>

          {editing ? (
            <TextField select SelectProps={{ native: true }} label={dressesText.dialog.operationalStatus} value={form.is_active ? 'active' : 'inactive'} onChange={(event) => onChange({ ...form, is_active: event.target.value === 'active' })}>
              <option value='active'>{dressesText.status.active}</option>
              <option value='inactive'>{dressesText.status.inactive}</option>
            </TextField>
          ) : null}
        </Stack>
      </AppDialogShell>

      <QuickAddServiceDialog
        open={quickAddOpen}
        onClose={() => setQuickAddOpen(false)}
        onServiceAdded={handleServiceAdded}
      />
    </>
  );
}
