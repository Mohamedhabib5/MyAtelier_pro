import { Box, Grid2 as Grid, Typography, alpha, useTheme, Tooltip, Chip, Stack, Paper } from '@mui/material';
import { Calendar as CalendarIcon } from 'lucide-react';
import type { CalendarEventRecord } from '../../features/bookings/api';
import type { CalendarViewMode } from '../CalendarPage';
import { useLanguage } from '../../features/language/LanguageProvider';

interface Props {
  viewMode: CalendarViewMode;
  currentDate: Date;
  events: CalendarEventRecord[];
  onEventClick: (id: string) => void;
  onDayClick: (date: Date) => void;
}

export function CalendarGrid({ viewMode, currentDate, events, onEventClick, onDayClick }: Props) {
  const theme = useTheme();
  const { language, direction } = useLanguage();
  const isRtl = direction === 'rtl';

  if (viewMode === 'month') {
    return <MonthView currentDate={currentDate} events={events} onEventClick={onEventClick} onDayClick={onDayClick} language={language} isRtl={isRtl} />;
  }

  if (viewMode === 'week') {
    return <WeekView currentDate={currentDate} events={events} onEventClick={onEventClick} onDayClick={onDayClick} language={language} isRtl={isRtl} />;
  }

  if (viewMode === 'day') {
    return <DayView currentDate={currentDate} events={events} onEventClick={onEventClick} language={language} />;
  }

  if (viewMode === 'year') {
    return <YearView currentDate={currentDate} events={events} onMonthClick={(month: number) => { onDayClick(new Date(currentDate.getFullYear(), month, 1)); }} language={language} />;
  }

  return (
    <Box sx={{ p: 10, textAlign: 'center' }}>
      <Typography variant="h6" color="text.secondary">
        {language === 'ar' ? 'هذا العرض قيد التطوير' : 'This view is under development'}
      </Typography>
    </Box>
  );
}

function MonthView({ currentDate, events, onEventClick, onDayClick, language, isRtl }: any) {
  const theme = useTheme();
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  
  const firstDayOfMonth = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  
  const days = [];
  // Fill empty slots for previous month
  const prevMonthLastDay = new Date(year, month, 0).getDate();
  for (let i = firstDayOfMonth - 1; i >= 0; i--) {
    days.push({ day: prevMonthLastDay - i, currentMonth: false, date: new Date(year, month - 1, prevMonthLastDay - i) });
  }
  // Current month days
  for (let i = 1; i <= daysInMonth; i++) {
    days.push({ day: i, currentMonth: true, date: new Date(year, month, i) });
  }
  // Fill empty slots for next month
  const totalSlots = 42; // 6 rows * 7 days
  const remaining = totalSlots - days.length;
  for (let i = 1; i <= remaining; i++) {
    days.push({ day: i, currentMonth: false, date: new Date(year, month + 1, i) });
  }

  const dayNames = language === 'ar' 
    ? ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
    : ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', borderBottom: `1px solid ${theme.palette.divider}`, bgcolor: alpha(theme.palette.primary.main, 0.02) }}>
        {dayNames.map(name => (
          <Box key={name} sx={{ p: 1.5, textAlign: 'center' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 800, color: 'text.secondary' }}>{name}</Typography>
          </Box>
        ))}
      </Box>
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', flex: 1 }}>
        {days.map((dayObj, index) => {
          const dateStr = dayObj.date.toISOString().split('T')[0];
          const dayEvents = events.filter((e: any) => e.start === dateStr);
          const isToday = new Date().toDateString() === dayObj.date.toDateString();

          return (
            <Box 
              key={index} 
              onClick={() => onDayClick(dayObj.date)}
              sx={{ 
                borderRight: `1px solid ${theme.palette.divider}`, 
                borderBottom: `1px solid ${theme.palette.divider}`,
                p: 0.5,
                minHeight: 100,
                transition: 'background 0.2s',
                bgcolor: dayObj.currentMonth ? 'background.paper' : alpha(theme.palette.action.disabledBackground, 0.3),
                '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.05), cursor: 'pointer' }
              }}
            >
              <Stack direction="row" justifyContent="space-between" sx={{ mb: 1, px: 1 }}>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    fontWeight: isToday ? 900 : 600,
                    color: isToday ? 'primary.main' : dayObj.currentMonth ? 'text.primary' : 'text.disabled',
                    bgcolor: isToday ? alpha(theme.palette.primary.main, 0.1) : 'transparent',
                    px: 0.8, py: 0.2, borderRadius: 1
                  }}
                >
                  {dayObj.day}
                </Typography>
              </Stack>
              <Stack spacing={0.5}>
                {dayEvents.slice(0, 4).map((event: any) => (
                  <Chip
                    key={event.id}
                    label={event.title}
                    size="small"
                    onClick={(e) => { e.stopPropagation(); onEventClick(event.id); }}
                    sx={{ 
                      borderRadius: 1, 
                      fontSize: '0.65rem', 
                      height: 20,
                      bgcolor: alpha(theme.palette.primary.main, 0.1),
                      color: 'primary.dark',
                      fontWeight: 700,
                      justifyContent: 'flex-start',
                      '& .MuiChip-label': { px: 1 }
                    }}
                  />
                ))}
                {dayEvents.length > 4 && (
                  <Typography variant="caption" sx={{ px: 1, fontSize: '0.6rem', color: 'text.secondary', fontWeight: 700 }}>
                    + {dayEvents.length - 4} {language === 'ar' ? 'المزيد' : 'more'}
                  </Typography>
                )}
              </Stack>
            </Box>
          );
        })}
      </Box>
    </Box>
  );
}

function DayView({ currentDate, events, onEventClick, language }: any) {
  const theme = useTheme();
  const dateStr = currentDate.toISOString().split('T')[0];
  const dayEvents = events.filter((e: any) => e.start === dateStr);

  return (
    <Box sx={{ p: 4, height: '100%', overflowY: 'auto' }}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 800 }}>
        {language === 'ar' ? 'أحداث اليوم' : 'Today Events'}
      </Typography>
      {dayEvents.length === 0 ? (
        <Box sx={{ mt: 10, textAlign: 'center', opacity: 0.5 }}>
          <CalendarIcon size={48} />
          <Typography variant="body1" sx={{ mt: 2 }}>
            {language === 'ar' ? 'لا توجد أحداث مجدولة لهذا اليوم' : 'No events scheduled for this day'}
          </Typography>
        </Box>
      ) : (
        <Stack spacing={2} sx={{ mt: 3 }}>
          {dayEvents.map((event: any) => (
            <Paper 
              key={event.id} 
              onClick={() => onEventClick(event.id)}
              sx={{ 
                p: 3, 
                borderRadius: 4, 
                borderLeft: `6px solid ${theme.palette.primary.main}`,
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': { transform: 'translateY(-2px)', boxShadow: theme.shadows[4], cursor: 'pointer' }
              }}
            >
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 800 }}>{event.title}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {event.department_name} • {event.service_name}
                  </Typography>
                </Box>
                <Chip 
                  label={event.status} 
                  color={event.status === 'completed' ? 'success' : 'primary'} 
                  variant="soft" 
                  sx={{ fontWeight: 800, borderRadius: 2 }}
                />
              </Stack>
            </Paper>
          ))}
        </Stack>
      )}
    </Box>
  );
}

function WeekView({ currentDate, events, onEventClick, onDayClick, language, isRtl }: any) {
  const theme = useTheme();
  const startOfWeek = new Date(currentDate);
  startOfWeek.setDate(currentDate.getDate() - currentDate.getDay());
  
  const days = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date(startOfWeek);
    d.setDate(startOfWeek.getDate() + i);
    days.push(d);
  }

  const dayNames = language === 'ar' 
    ? ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
    : ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', borderBottom: `1px solid ${theme.palette.divider}`, bgcolor: alpha(theme.palette.primary.main, 0.02) }}>
        {dayNames.map((name, i) => (
          <Box key={name} sx={{ p: 1.5, textAlign: 'center' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 800, color: 'text.secondary' }}>{name}</Typography>
            <Typography variant="h6" sx={{ fontWeight: 900 }}>{days[i].getDate()}</Typography>
          </Box>
        ))}
      </Box>
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', flex: 1 }}>
        {days.map((date, index) => {
          const dateStr = date.toISOString().split('T')[0];
          const dayEvents = events.filter((e: any) => e.start === dateStr);
          const isToday = new Date().toDateString() === date.toDateString();

          return (
            <Box 
              key={index} 
              onClick={() => onDayClick(date)}
              sx={{ 
                borderRight: `1px solid ${theme.palette.divider}`, 
                p: 1,
                minHeight: 200,
                transition: 'background 0.2s',
                bgcolor: isToday ? alpha(theme.palette.primary.main, 0.02) : 'background.paper',
                '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.05), cursor: 'pointer' }
              }}
            >
              <Stack spacing={1}>
                {dayEvents.map((event: any) => (
                  <Paper
                    key={event.id}
                    elevation={0}
                    onClick={(e) => { e.stopPropagation(); onEventClick(event.id); }}
                    sx={{ 
                      p: 1, 
                      borderRadius: 2, 
                      bgcolor: alpha(theme.palette.primary.main, 0.1),
                      borderLeft: `4px solid ${theme.palette.primary.main}`,
                      '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.15) }
                    }}
                  >
                    <Typography variant="caption" sx={{ fontWeight: 800, display: 'block', lineHeight: 1.2 }}>
                      {event.title}
                    </Typography>
                    <Typography variant="caption" sx={{ fontSize: '0.6rem', opacity: 0.7 }}>
                      {event.service_name}
                    </Typography>
                  </Paper>
                ))}
              </Stack>
            </Box>
          );
        })}
      </Box>
    </Box>
  );
}

function YearView({ currentDate, events, onMonthClick, language }: any) {
  const theme = useTheme();
  const year = currentDate.getFullYear();
  const months = Array.from({ length: 12 }, (_, i) => i);
  
  const monthNames = language === 'ar'
    ? ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
    : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  return (
    <Box sx={{ p: 3, height: '100%', overflowY: 'auto' }}>
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 3 }}>
        {months.map(month => {
          const monthEvents = events.filter((e: any) => {
            const d = new Date(e.start);
            return d.getFullYear() === year && d.getMonth() === month;
          });

          return (
            <Paper 
              key={month} 
              onClick={() => onMonthClick(month)}
              sx={{ 
                p: 2, 
                borderRadius: 4, 
                height: 180,
                transition: 'all 0.2s',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                '&:hover': { transform: 'scale(1.02)', boxShadow: theme.shadows[4], cursor: 'pointer' }
              }}
            >
              <Typography variant="h6" sx={{ fontWeight: 900, color: 'primary.main' }}>
                {monthNames[month]}
              </Typography>
              <Box>
                <Typography variant="h3" sx={{ fontWeight: 900, textAlign: 'center' }}>
                  {monthEvents.length}
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', fontWeight: 700, opacity: 0.6 }}>
                  {language === 'ar' ? 'حدث' : 'Events'}
                </Typography>
              </Box>
              <Box sx={{ height: 4, bgcolor: alpha(theme.palette.primary.main, 0.1), borderRadius: 2, overflow: 'hidden' }}>
                <Box sx={{ width: `${Math.min(100, monthEvents.length * 5)}%`, height: '100%', bgcolor: 'primary.main' }} />
              </Box>
            </Paper>
          );
        })}
      </Box>
    </Box>
  );
}
