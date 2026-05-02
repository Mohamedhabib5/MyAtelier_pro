import { Button, Dialog, DialogActions, DialogContent, DialogTitle, IconButton, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { SectionCard } from '../../components/SectionCard';
import { StableNumericField } from '../../components/inputs/StableNumericField';
import { queryClient } from '../../lib/queryClient';
import { type CompensationTypeRecord, createCompensationType, listCompensationTypes, updateCompensationType } from './api';
import { useCommonText } from '../../text/common';

type Props = {
  language: 'ar' | 'en';
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
};

export function CompensationTypesSettingsSection({ language, onSuccess, onError }: Props) {
  const commonText = useCommonText();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<CompensationTypeRecord | null>(null);
  
  const [name, setName] = useState('');
  const [defaultPrice, setDefaultPrice] = useState('0');
  const [displayOrder, setDisplayOrder] = useState('0');

  const typesQuery = useQuery({ queryKey: ['settings', 'compensation-types'], queryFn: listCompensationTypes });

  const saveMutation = useMutation({
    mutationFn: (payload: any) => {
      if (editingItem) {
        return updateCompensationType(editingItem.id, payload);
      }
      return createCompensationType(payload);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['settings', 'compensation-types'] });
      onSuccess(language === 'ar' ? 'تم الحفظ بنجاح' : 'Saved successfully');
      handleClose();
    },
    onError: (err: any) => {
      onError(err.message || 'Error saving compensation type');
    }
  });

  const handleOpen = (item?: CompensationTypeRecord) => {
    if (item) {
      setEditingItem(item);
      setName(item.name);
      setDefaultPrice(item.default_price.toString());
      setDisplayOrder(item.display_order.toString());
    } else {
      setEditingItem(null);
      setName('');
      setDefaultPrice('0');
      setDisplayOrder((typesQuery.data?.length ?? 0).toString());
    }
    setIsDialogOpen(true);
  };

  const handleClose = () => {
    setIsDialogOpen(false);
    setEditingItem(null);
  };

  const handleSave = () => {
    if (!name.trim()) return;
    saveMutation.mutate({
      name,
      default_price: Number(defaultPrice),
      display_order: Number(displayOrder),
    });
  };

  const t = {
    title: language === 'ar' ? 'أنواع التعويضات' : 'Compensation Types',
    subtitle: language === 'ar' ? 'إدارة أنواع التعويضات والغرامات التي يمكن تطبيقها في شاشة العهدة' : 'Manage compensation and penalty types available in custody screen',
    add: language === 'ar' ? 'إضافة نوع جديد' : 'Add New Type',
    name: language === 'ar' ? 'اسم التعويض (مثال: تلف، ضياع)' : 'Compensation Name',
    price: language === 'ar' ? 'المبلغ الافتراضي' : 'Default Amount',
    order: language === 'ar' ? 'الترتيب' : 'Order',
    edit: language === 'ar' ? 'تعديل' : 'Edit',
    save: commonText.save,
    cancel: commonText.cancel,
  };

  return (
    <SectionCard
      title={t.title}
      subtitle={t.subtitle}
    >
      <Stack direction="row" justifyContent="flex-end" sx={{ mb: 2 }}>
        <Button variant="contained" size="small" onClick={() => handleOpen()}>{t.add}</Button>
      </Stack>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t.name}</TableCell>
            <TableCell>{t.price}</TableCell>
            <TableCell align="center">{t.order}</TableCell>
            <TableCell align="right"></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(typesQuery.data ?? []).map((item) => (
            <TableRow key={item.id}>
              <TableCell>{item.name}</TableCell>
              <TableCell>{item.default_price}</TableCell>
              <TableCell align="center">{item.display_order}</TableCell>
              <TableCell align="right">
                <IconButton size="small" onClick={() => handleOpen(item)}>
                  <EditIcon fontSize="small" />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
          {typesQuery.data?.length === 0 && (
            <TableRow>
              <TableCell colSpan={4} align="center" sx={{ py: 3, color: 'text.secondary' }}>
                {language === 'ar' ? 'لا يوجد أنواع تعويضات مسجلة' : 'No compensation types found'}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      <Dialog open={isDialogOpen} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editingItem ? t.edit : t.add}</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label={t.name}
              value={name}
              onChange={(e) => setName(e.target.value)}
              fullWidth
              autoFocus
            />
            <StableNumericField
              label={t.price}
              value={defaultPrice}
              onValueChange={setDefaultPrice}
              fullWidth
            />
            <StableNumericField
              label={t.order}
              value={displayOrder}
              onValueChange={setDisplayOrder}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 2, pt: 0 }}>
          <Button onClick={handleClose}>{t.cancel}</Button>
          <Button 
            variant="contained" 
            onClick={handleSave} 
            disabled={!name.trim() || saveMutation.isPending}
          >
            {saveMutation.isPending ? '...' : t.save}
          </Button>
        </DialogActions>
      </Dialog>
    </SectionCard>
  );
}
