import CloseOutlinedIcon from '@mui/icons-material/CloseOutlined';
import { Dialog, DialogActions, DialogContent, DialogProps, DialogTitle, IconButton, Stack, Typography, useMediaQuery, useTheme } from '@mui/material';
import type { ReactNode } from 'react';

type AppDialogShellProps = {
  open: boolean;
  title: string;
  subtitle?: string;
  onClose: () => void;
  children: ReactNode;
  actions?: ReactNode;
  maxWidth?: DialogProps['maxWidth'];
  fullScreenOnMobile?: boolean;
  contentDividers?: boolean;
  disableCloseButton?: boolean;
};

export function AppDialogShell({
  open,
  title,
  subtitle,
  onClose,
  children,
  actions,
  maxWidth = 'sm',
  fullScreenOnMobile = false,
  contentDividers = true,
  disableCloseButton = false,
}: AppDialogShellProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const fullScreen = fullScreenOnMobile && isMobile;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth={maxWidth}
      fullScreen={fullScreen}
      PaperProps={{
        sx: {
          borderRadius: { xs: fullScreen ? 0 : 3, sm: 3 },
          overflow: 'hidden',
          m: { xs: 1, sm: 2, md: 4 },
          width: { xs: 'calc(100% - 16px)', sm: 'calc(100% - 32px)', md: 'auto' },
        },
      }}
    >
      <DialogTitle sx={{ 
        px: { xs: 2, sm: 3 }, 
        py: 2, 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'flex-start', 
        gap: 1.5,
        borderBottom: '1px solid rgba(0,0,0,0.05)'
      }}>
        <Stack spacing={0.5}>
          <Typography variant='h6' sx={{ fontWeight: 800 }}>{title}</Typography>
          {subtitle ? (
            <Typography variant='body2' color='text.secondary'>
              {subtitle}
            </Typography>
          ) : null}
        </Stack>
        {!disableCloseButton ? (
          <IconButton onClick={onClose} aria-label='close' size='small' sx={{ mt: -0.5, mr: -0.5 }}>
            <CloseOutlinedIcon fontSize='small' />
          </IconButton>
        ) : null}
      </DialogTitle>
      <DialogContent dividers={contentDividers} sx={{ 
        px: { xs: 2, sm: 3 }, 
        py: { xs: 2, sm: 2.5 },
        bgcolor: 'rgba(0,0,0,0.01)'
      }}>
        {children}
      </DialogContent>
      {actions ? (
        <DialogActions sx={{ 
          px: { xs: 2, sm: 3 }, 
          pb: { xs: 2, sm: 2.5 }, 
          pt: 2, 
          gap: 1, 
          flexDirection: { xs: 'column-reverse', sm: 'row' }, 
          alignItems: 'stretch',
          '& > button, & > div': {
            width: { xs: '100%', sm: 'auto' },
            m: '0 !important'
          }
        }}>
          {actions}
        </DialogActions>
      ) : null}
    </Dialog>
  );
}
