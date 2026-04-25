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
          borderRadius: { xs: fullScreen ? 0 : 2.5, sm: 2.5 },
          overflow: 'hidden',
        },
      }}
    >
      <DialogTitle sx={{ px: 3, py: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 1.5 }}>
        <Stack spacing={0.5}>
          <Typography variant='h6'>{title}</Typography>
          {subtitle ? (
            <Typography variant='body2' color='text.secondary'>
              {subtitle}
            </Typography>
          ) : null}
        </Stack>
        {!disableCloseButton ? (
          <IconButton onClick={onClose} aria-label='close' size='small'>
            <CloseOutlinedIcon fontSize='small' />
          </IconButton>
        ) : null}
      </DialogTitle>
      <DialogContent dividers={contentDividers} sx={{ px: 3, py: 2.5 }}>
        {children}
      </DialogContent>
      {actions ? (
        <DialogActions sx={{ px: 3, pb: 2.5, pt: 2, gap: 1, flexDirection: { xs: 'column', sm: 'row' }, alignItems: 'stretch' }}>
          {actions}
        </DialogActions>
      ) : null}
    </Dialog>
  );
}
