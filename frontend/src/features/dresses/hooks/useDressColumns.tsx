import { useMemo } from 'react';
import { Box, Button, Chip, Stack } from '@mui/material';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import { type DressRecord } from '../api';
import { dressStatusLabel } from '../../../text/dresses';
import { EMPTY_VALUE } from '../../../text/common';
import { type LanguageCode } from '../../../lib/language';

interface UseDressColumnsProps {
  language: LanguageCode;
  commonText: { edit: string };
  dressesText: {
    table: {
      code: string;
      type: string;
      description: string;
      status: string;
      purchaseDate: string;
      imageRef: string;
      action: string;
    };
    status: {
      active: string;
      inactive: string;
    };
  };
  openEditDialog: (dress: DressRecord) => void;
  openLifecycleDialog: (dress: DressRecord, archive: boolean) => void;
  setDeleteTarget: (dress: DressRecord) => void;
  setPreviewImage: (url: string) => void;
}

export function useDressColumns({
  language,
  commonText,
  dressesText,
  openEditDialog,
  openLifecycleDialog,
  setDeleteTarget,
  setPreviewImage,
}: UseDressColumnsProps) {
  return useMemo(() => [
    { key: 'code', header: dressesText.table.code, searchValue: (row: DressRecord) => row.code, render: (row: DressRecord) => row.code },
    { key: 'type', header: dressesText.table.type, searchValue: (row: DressRecord) => row.dress_type, render: (row: DressRecord) => row.dress_type },
    { key: 'description', header: dressesText.table.description, searchValue: (row: DressRecord) => row.description ?? '', render: (row: DressRecord) => row.description ?? EMPTY_VALUE },
    {
      key: 'status',
      header: dressesText.table.status,
      searchValue: (row: DressRecord) => dressStatusLabel(language, row.status),
      render: (row: DressRecord) => (
        <Chip 
          label={dressStatusLabel(language, row.status)} 
          size='small' 
          color={row.status === 'available' ? 'success' : row.status === 'reserved' ? 'warning' : row.status === 'with_customer' ? 'info' : 'default'} 
        />
      ),
    },
    {
      key: 'operational_status',
      header: language === 'ar' ? 'الحالة التشغيلية' : 'Operational status',
      searchValue: (row: DressRecord) => (row.is_active ? dressesText.status.active : dressesText.status.inactive),
      render: (row: DressRecord) => (
        <Chip 
          label={row.is_active ? dressesText.status.active : dressesText.status.inactive} 
          size='small' 
          color={row.is_active ? 'success' : 'default'} 
        />
      ),
    },
    { key: 'purchase_date', header: dressesText.table.purchaseDate, searchValue: (row: DressRecord) => row.purchase_date ?? '', render: (row: DressRecord) => row.purchase_date ?? EMPTY_VALUE },
    {
      key: 'image_path',
      header: dressesText.table.imageRef,
      searchValue: (row: DressRecord) => row.image_path ?? '',
      render: (row: DressRecord) => {
        if (!row.image_path) return EMPTY_VALUE;
        const backendUrl = `${window.location.protocol}//${window.location.hostname}:8000`;
        const imageUrl = row.image_path.startsWith('http') ? row.image_path : `${backendUrl}/attachments/${row.image_path}`;
        return (
          <Box
            component='img'
            src={imageUrl}
            alt={row.code}
            onClick={() => setPreviewImage(imageUrl)}
            sx={{
              width: 48,
              height: 48,
              objectFit: 'cover',
              borderRadius: 1.5,
              border: '1px solid',
              borderColor: 'divider',
              transition: 'all 0.2s ease-in-out',
              cursor: 'zoom-in',
              '&:hover': {
                transform: 'scale(1.1)',
                zIndex: 10,
                boxShadow: 2,
              },
            }}
          />
        );
      },
    },
    {
      key: 'action',
      header: dressesText.table.action,
      render: (row: DressRecord) => (
        <Stack direction='row' spacing={1}>
          <Button size='small' startIcon={<EditOutlinedIcon />} onClick={() => openEditDialog(row)}>
            {commonText.edit}
          </Button>
          <Button size='small' color={row.is_active ? 'warning' : 'success'} onClick={() => openLifecycleDialog(row, row.is_active)}>
            {row.is_active ? (language === 'ar' ? 'أرشفة' : 'Archive') : language === 'ar' ? 'استعادة' : 'Restore'}
          </Button>
          <Button size='small' color='error' startIcon={<DeleteOutlineOutlinedIcon />} onClick={() => setDeleteTarget(row)}>
            {language === 'ar' ? 'حذف تصحيحي' : 'Corrective delete'}
          </Button>
        </Stack>
      ),
    },
  ], [
    commonText.edit,
    dressesText.status.active,
    dressesText.status.inactive,
    dressesText.table.action,
    dressesText.table.code,
    dressesText.table.description,
    dressesText.table.imageRef,
    dressesText.table.purchaseDate,
    dressesText.table.status,
    dressesText.table.type,
    language,
    openEditDialog,
    openLifecycleDialog,
    setDeleteTarget,
    setPreviewImage,
  ]);
}
