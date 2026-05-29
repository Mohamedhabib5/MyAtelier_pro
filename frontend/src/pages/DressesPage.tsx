import CheckroomOutlinedIcon from '@mui/icons-material/CheckroomOutlined';
import { Alert, Box, Button, Stack, Typography, Dialog, DialogContent, IconButton, TextField } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useMemo } from 'react';
import { DestructiveDeleteDialog } from '../components/DestructiveDeleteDialog';
import { LifecycleReasonDialog } from '../components/LifecycleReasonDialog';
import { AppDataTable } from '../components/data-table/AppDataTable';
import { SectionCard } from '../components/SectionCard';
import { DressFormDialog } from '../features/dresses/DressFormDialog';
import { useLanguage } from '../features/language/LanguageProvider';
import { queryClient } from '../lib/queryClient';
import { useCommonText } from '../text/common';
import { dressStatusLabel, useDressesText } from '../text/dresses';
import { useDressesState } from '../features/dresses/hooks/useDressesState';
import { useDressColumns } from '../features/dresses/hooks/useDressColumns';

export function DressesPage() {
  const { language } = useLanguage();
  const commonText = useCommonText();
  const dressesText = useDressesText();

  const {
    error, setError,
    dialogOpen,
    editingDress,
    form, setForm,
    statusFilter, setStatusFilter,
    activeFilter, setActiveFilter,
    lifecycleTarget,
    lifecycleMode,
    lifecycleReason, setLifecycleReason,
    deleteTarget, setDeleteTarget,
    previewImage, setPreviewImage,
    dressesQuery,
    lifecycleMutation,
    closeDialog,
    openCreateDialog,
    openEditDialog,
    saveDress,
    openLifecycleDialog,
    closeLifecycleDialog,
    confirmLifecycle,
    closeDeleteDialog,
  } = useDressesState();

  const columns = useDressColumns({
    language,
    commonText,
    dressesText,
    openEditDialog,
    openLifecycleDialog,
    setDeleteTarget,
    setPreviewImage,
  });

  const rows = useMemo(
    () => (dressesQuery.data ?? []).filter((dress) => (statusFilter === 'all' ? true : dress.status === statusFilter)),
    [dressesQuery.data, statusFilter]
  );

  const labels = useMemo(() =>
    language === 'ar'
      ? { search: 'بحث', searchPlaceholder: 'ابحث بالكود أو النوع أو الوصف', filters: 'الفلاتر', columns: 'الأعمدة', export: 'تصدير', reset: 'إعادة الضبط', noRows: 'لا توجد بيانات مطابقة' }
      : { search: 'Search', searchPlaceholder: 'Search by code, type, or description', filters: 'Filters', columns: 'Columns', export: 'Export', reset: 'Reset', noRows: 'No matching rows' }
  , [language]);

  return (
    <Stack spacing={3}>
      <Stack direction='row' justifyContent='space-between' alignItems='center'>
        <Box>
          <Typography variant='h4'>{dressesText.page.title}</Typography>
          <Typography color='text.secondary'>{dressesText.page.description}</Typography>
        </Box>
        <Button variant='contained' startIcon={<CheckroomOutlinedIcon />} onClick={openCreateDialog}>
          {dressesText.page.create}
        </Button>
      </Stack>

      {error ? <Alert severity='error'>{error}</Alert> : null}

      <SectionCard title={dressesText.page.listTitle} subtitle={dressesText.page.listSubtitle}>
        <AppDataTable
          tableKey='dresses-list'
          rows={rows}
          columns={columns}
          searchLabel={labels.search}
          searchPlaceholder={labels.searchPlaceholder}
          resetColumnsLabel={labels.reset}
          noRowsLabel={labels.noRows}
          filtersLabel={labels.filters}
          columnsLabel={labels.columns}
          exportLabel={labels.export}
          rowsPerPageLabel={language === 'ar' ? 'عدد الصفوف' : 'Rows per page'}
          closeLabel={language === 'ar' ? 'إغلاق' : 'Close'}
          searchFields={[(row) => row.code, (row) => row.name, (row) => row.dress_type_name ?? '', (row) => row.description ?? '', (row) => row.image_path ?? '']}
          filterContent={
            <Stack spacing={2}>
              <TextField select SelectProps={{ native: true }} fullWidth label={language === 'ar' ? 'الحالة التشغيلية' : 'Operational status'} value={activeFilter} onChange={(event) => setActiveFilter(event.target.value as any)}>
                <option value='all'>{language === 'ar' ? 'الكل' : 'All'}</option>
                <option value='active'>{dressesText.status.active}</option>
                <option value='inactive'>{dressesText.status.inactive}</option>
              </TextField>
              <TextField select SelectProps={{ native: true }} fullWidth label={dressesText.table.status} value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as any)}>
                <option value='all'>{language === 'ar' ? 'الكل' : 'All'}</option>
                <option value='available'>{dressStatusLabel(language, 'available')}</option>
                <option value='reserved'>{dressStatusLabel(language, 'reserved')}</option>
                <option value='with_customer'>{dressStatusLabel(language, 'with_customer')}</option>
                <option value='maintenance'>{dressStatusLabel(language, 'maintenance')}</option>
              </TextField>
            </Stack>
          }
        />
      </SectionCard>

      <DressFormDialog open={dialogOpen} editing={Boolean(editingDress)} form={form} onChange={setForm} onClose={closeDialog} onSave={() => void saveDress()} />

      <LifecycleReasonDialog
        open={Boolean(lifecycleTarget)}
        mode={lifecycleMode}
        entityLabel={lifecycleTarget?.code ?? ''}
        reason={lifecycleReason}
        language={language}
        onReasonChange={setLifecycleReason}
        onCancel={closeLifecycleDialog}
        onConfirm={() => void confirmLifecycle()}
        loading={lifecycleMutation.isPending}
      />
      <DestructiveDeleteDialog
        open={Boolean(deleteTarget)}
        entityType='dress'
        entityId={deleteTarget?.id ?? null}
        entityLabel={deleteTarget?.code ?? ''}
        onClose={closeDeleteDialog}
        onDeleted={() => {
          void queryClient.invalidateQueries({ queryKey: ['dresses'] });
        }}
        onError={(message) => setError(message)}
      />

      <Dialog open={Boolean(previewImage)} onClose={() => setPreviewImage(null)} maxWidth='lg'>
        <DialogContent sx={{ p: 0, position: 'relative', bgcolor: 'black', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <IconButton aria-label={language === 'ar' ? 'إغلاق' : 'Close'} onClick={() => setPreviewImage(null)} sx={{ position: 'absolute', top: 8, right: 8, color: 'white', bgcolor: 'rgba(0,0,0,0.5)', '&:hover': { bgcolor: 'rgba(0,0,0,0.7)' } }}>
            <CloseIcon />
          </IconButton>
          {previewImage && (
            <Box
              component='img'
              src={previewImage}
              alt='Preview'
              sx={{
                maxWidth: '100%',
                maxHeight: '90vh',
                display: 'block',
                boxShadow: 24,
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Stack>
  );
}

