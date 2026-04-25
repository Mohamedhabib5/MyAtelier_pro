import PushPinOutlinedIcon from '@mui/icons-material/PushPinOutlined';
import RestartAltOutlinedIcon from '@mui/icons-material/RestartAltOutlined';
import ViewColumnOutlinedIcon from '@mui/icons-material/ViewColumnOutlined';
import { Button, Checkbox, FormControl, InputLabel, MenuItem, Select, Stack, Typography } from '@mui/material';
import type { Column } from 'ag-grid-community';

import { AppDialogShell } from '../AppDialogShell';

type Props = {
  open: boolean;
  title: string;
  resetLabel: string;
  closeLabel: string;
  columns: Column[];
  onClose: () => void;
  onToggleVisibility: (colId: string, visible: boolean) => void;
  onPinChange: (colId: string, pinned: 'left' | 'right' | null) => void;
  onReset: () => void;
  language: 'ar' | 'en';
};

export function GridColumnPanel({ open, title, resetLabel, closeLabel, columns, onClose, onToggleVisibility, onPinChange, onReset, language }: Props) {
  return (
    <AppDialogShell
      open={open}
      onClose={onClose}
      title={title}
      maxWidth='sm'
      actions={
        <>
          <Button startIcon={<RestartAltOutlinedIcon />} onClick={onReset}>
            {resetLabel}
          </Button>
          <Button onClick={onClose}>{closeLabel}</Button>
        </>
      }
    >
      <Stack spacing={1.5}>
        <Stack direction='row' spacing={1} alignItems='center'>
          <ViewColumnOutlinedIcon fontSize='small' color='action' />
          <Typography variant='body2' color='text.secondary'>
            {language === 'ar' ? 'تحديد الأعمدة المعروضة وتثبيتها.' : 'Choose visible columns and pin positions.'}
          </Typography>
        </Stack>
        {columns.map((column) => {
          const def = column.getColDef();
          const label = def.headerName ?? column.getColId();
          return (
            <Stack key={column.getColId()} direction='row' spacing={2} justifyContent='space-between' alignItems='center'>
              <Stack direction='row' spacing={1} alignItems='center'>
                <Checkbox checked={column.isVisible()} onChange={(event) => onToggleVisibility(column.getColId(), event.target.checked)} />
                <Typography>{label}</Typography>
              </Stack>
              <FormControl size='small' sx={{ minWidth: 140 }}>
                <InputLabel>{language === 'ar' ? 'ط§ظ„طھط«ط¨ظٹطھ' : 'Pin'}</InputLabel>
                <Select
                  label={language === 'ar' ? 'ط§ظ„طھط«ط¨ظٹطھ' : 'Pin'}
                  value={(column.getPinned() as 'left' | 'right' | null) ?? ''}
                  startAdornment={<PushPinOutlinedIcon fontSize='small' sx={{ ml: 1 }} />}
                  onChange={(event) => onPinChange(column.getColId(), (event.target.value || null) as 'left' | 'right' | null)}
                >
                  <MenuItem value=''>{language === 'ar' ? 'ط¨ط¯ظˆظ†' : 'None'}</MenuItem>
                  <MenuItem value='left'>{language === 'ar' ? 'ظٹط³ط§ط±' : 'Left'}</MenuItem>
                  <MenuItem value='right'>{language === 'ar' ? 'ظٹظ…ظٹظ†' : 'Right'}</MenuItem>
                </Select>
              </FormControl>
            </Stack>
          );
        })}
      </Stack>
    </AppDialogShell>
  );
}
