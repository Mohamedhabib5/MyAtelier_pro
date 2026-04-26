import PushPinOutlinedIcon from '@mui/icons-material/PushPinOutlined';
import RestartAltOutlinedIcon from '@mui/icons-material/RestartAltOutlined';
import ViewColumnOutlinedIcon from '@mui/icons-material/ViewColumnOutlined';
import { Button, Checkbox, FormControl, InputLabel, MenuItem, Select, Stack, Typography, Popover, Box, Divider } from '@mui/material';
import type { Column } from 'ag-grid-community';

type Props = {
  anchorEl: HTMLElement | null;
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

export function GridColumnPanel({ anchorEl, open, title, resetLabel, columns, onClose, onToggleVisibility, onPinChange, onReset, language }: Props) {
  return (
    <Popover
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: language === 'ar' ? 'left' : 'right',
      }}
      transformOrigin={{
        vertical: 'top',
        horizontal: language === 'ar' ? 'left' : 'right',
      }}
      PaperProps={{
        sx: {
          width: 320,
          maxHeight: 480,
          borderRadius: 3,
          mt: 1,
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
          overflow: 'hidden'
        }
      }}
    >
      <Box sx={{ p: 2, background: 'rgba(124,58,237,0.03)' }}>
        <Stack direction='row' justifyContent='space-between' alignItems='center'>
          <Typography variant='subtitle2' fontWeight={700}>{title}</Typography>
          <Button 
            size='small' 
            variant='text' 
            color='primary' 
            startIcon={<RestartAltOutlinedIcon sx={{ fontSize: '1rem !important' }} />} 
            onClick={onReset}
            sx={{ fontSize: '0.75rem', py: 0 }}
          >
            {resetLabel}
          </Button>
        </Stack>
      </Box>
      
      <Divider />

      <Box sx={{ p: 1.5, maxHeight: 380, overflowY: 'auto' }}>
        <Stack spacing={1}>
          {columns.map((column) => {
            const def = column.getColDef();
            const label = def.headerName ?? column.getColId();
            return (
              <Stack key={column.getColId()} direction='row' spacing={1} justifyContent='space-between' alignItems='center' sx={{ 
                px: 1, 
                py: 0.5, 
                borderRadius: 1.5,
                '&:hover': { background: 'rgba(0,0,0,0.02)' }
              }}>
                <Stack direction='row' spacing={0.5} alignItems='center' sx={{ flex: 1, minWidth: 0 }}>
                  <Checkbox 
                    size='small'
                    checked={column.isVisible()} 
                    onChange={(event) => onToggleVisibility(column.getColId(), event.target.checked)} 
                  />
                  <Typography variant='body2' noWrap sx={{ fontSize: '0.875rem' }}>{label}</Typography>
                </Stack>
                
                <FormControl size='small' sx={{ minWidth: 90 }}>
                  <Select
                    value={(column.getPinned() as 'left' | 'right' | null) ?? ''}
                    onChange={(event) => onPinChange(column.getColId(), (event.target.value || null) as 'left' | 'right' | null)}
                    sx={{ 
                      fontSize: '0.75rem',
                      '.MuiSelect-select': { py: 0.5, px: 1 }
                    }}
                  >
                    <MenuItem value='' sx={{ fontSize: '0.75rem' }}>{language === 'ar' ? 'بدون' : 'None'}</MenuItem>
                    <MenuItem value='left' sx={{ fontSize: '0.75rem' }}>{language === 'ar' ? 'يسار' : 'Left'}</MenuItem>
                    <MenuItem value='right' sx={{ fontSize: '0.75rem' }}>{language === 'ar' ? 'يمين' : 'Right'}</MenuItem>
                  </Select>
                </FormControl>
              </Stack>
            );
          })}
        </Stack>
      </Box>
    </Popover>
  );
}
