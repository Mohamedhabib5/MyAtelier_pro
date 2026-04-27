import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, Stack, Divider, Box, alpha, useTheme, IconButton } from '@mui/material';
import { ExternalLink, X, User, Tag, Calendar as CalendarIcon, Hash } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { CalendarEventRecord } from '../../features/bookings/api';
import { useLanguage } from '../../features/language/LanguageProvider';

interface Props {
  event?: CalendarEventRecord;
  open: boolean;
  onClose: () => void;
}

export function EventDetailsModal({ event, open, onClose }: Props) {
  const theme = useTheme();
  const navigate = useNavigate();
  const { language } = useLanguage();

  if (!event) return null;

  const handleGoToBooking = () => {
    navigate(`/bookings?id=${event.booking_id}`);
    onClose();
  };

  const DetailRow = ({ icon: Icon, label, value }: any) => (
    <Stack direction="row" spacing={2} alignItems="center">
      <Box sx={{ p: 1, borderRadius: 2, bgcolor: alpha(theme.palette.primary.main, 0.1), color: 'primary.main' }}>
        <Icon size={18} />
      </Box>
      <Box>
        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 700, display: 'block' }}>{label}</Typography>
        <Typography variant="body1" sx={{ fontWeight: 800 }}>{value}</Typography>
      </Box>
    </Stack>
  );

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="xs" 
      fullWidth
      PaperProps={{ sx: { borderRadius: 6, p: 1 } }}
    >
      <DialogTitle sx={{ m: 0, p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 900 }}>
          {language === 'ar' ? 'تفاصيل الحجز' : 'Booking Details'}
        </Typography>
        <IconButton onClick={onClose} size="small">
          <X size={20} />
        </IconButton>
      </DialogTitle>
      
      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          <DetailRow 
            icon={User} 
            label={language === 'ar' ? 'اسم العميلة' : 'Customer Name'} 
            value={event.customer_name} 
          />
          <DetailRow 
            icon={Hash} 
            label={language === 'ar' ? 'رقم الحجز' : 'Booking Number'} 
            value={event.booking_number} 
          />
          <DetailRow 
            icon={Tag} 
            label={language === 'ar' ? 'الخدمة / القسم' : 'Service / Department'} 
            value={`${event.service_name} (${event.department_name})`} 
          />
          <DetailRow 
            icon={CalendarIcon} 
            label={language === 'ar' ? 'التاريخ' : 'Date'} 
            value={event.start} 
          />
          
          <Box sx={{ p: 2, borderRadius: 4, bgcolor: alpha(theme.palette.primary.main, 0.05), textAlign: 'center' }}>
            <Typography variant="caption" sx={{ fontWeight: 800, color: 'primary.main', mb: 0.5, display: 'block' }}>
              {language === 'ar' ? 'الحالة' : 'Status'}
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 900, color: 'primary.dark' }}>
              {event.status}
            </Typography>
          </Box>
        </Stack>
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button 
          fullWidth 
          variant="contained" 
          startIcon={<ExternalLink size={18} />} 
          onClick={handleGoToBooking}
          sx={{ borderRadius: 3, py: 1.5, fontWeight: 800 }}
        >
          {language === 'ar' ? 'فتح وثيقة الحجز' : 'Open Booking Document'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
