import { useState, useMemo } from 'react';
import { Box, Paper, Stack, Typography, alpha, useTheme, Button, IconButton, ButtonGroup, Select, MenuItem, FormControl } from '@mui/material';
import { ChevronRight, ChevronLeft, Calendar as CalendarIcon, Filter } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

import { listCalendarEvents, type CalendarEventRecord, type CalendarQuery } from '../features/bookings/api';
import { listDepartments, listServices } from '../features/catalog/api';
import { CalendarFilters } from './components/CalendarFilters';
import { CalendarGrid } from './components/CalendarGrid';
import { EventDetailsModal } from './components/EventDetailsModal';
import { useLanguage } from '../features/language/LanguageProvider';

export type CalendarViewMode = 'day' | 'week' | 'month' | 'year';

export function CalendarPage() {
  const theme = useTheme();
  const { language, direction } = useLanguage();
  const isRtl = direction === 'rtl';

  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<CalendarViewMode>('month');
  const [filters, setFilters] = useState<CalendarQuery>({
    dateMode: 'service',
  });
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(true);

  // Fetch Data
  const { data: events = [] } = useQuery({
    queryKey: ['calendar-events', filters, currentDate.getMonth(), currentDate.getFullYear(), viewMode],
    queryFn: () => {
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth();
      
      // Calculate a wide range to cover the current view plus some padding
      const dateFrom = new Date(year, month - 1, 1).toISOString().split('T')[0];
      const dateTo = new Date(year, month + 2, 0).toISOString().split('T')[0];

      return listCalendarEvents({ ...filters, dateFrom, dateTo });
    }
  });

  const { data: departments = [] } = useQuery({
    queryKey: ['departments', 'active'],
    queryFn: () => listDepartments('active')
  });

  const { data: services = [] } = useQuery({
    queryKey: ['services', 'active'],
    queryFn: () => listServices('active')
  });

  const handlePrev = () => {
    const newDate = new Date(currentDate);
    if (viewMode === 'month') newDate.setMonth(newDate.getMonth() - 1);
    else if (viewMode === 'week') newDate.setDate(newDate.getDate() - 7);
    else if (viewMode === 'day') newDate.setDate(newDate.getDate() - 1);
    else if (viewMode === 'year') newDate.setFullYear(newDate.getFullYear() - 1);
    setCurrentDate(newDate);
  };

  const handleNext = () => {
    const newDate = new Date(currentDate);
    if (viewMode === 'month') newDate.setMonth(newDate.getMonth() + 1);
    else if (viewMode === 'week') newDate.setDate(newDate.getDate() + 7);
    else if (viewMode === 'day') newDate.setDate(newDate.getDate() + 1);
    else if (viewMode === 'year') newDate.setFullYear(newDate.getFullYear() + 1);
    setCurrentDate(newDate);
  };

  const handleToday = () => setCurrentDate(new Date());

  const monthName = currentDate.toLocaleString(language === 'ar' ? 'ar-EG' : 'en-US', { month: 'long', year: 'numeric' });

  const selectedEvent = useMemo(() => events.find(e => e.id === selectedEventId), [events, selectedEventId]);

  return (
    <Stack spacing={3} sx={{ height: 'calc(100vh - 160px)' }}>
      {/* Header */}
      <Paper sx={{ p: 2, borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Stack direction="row" spacing={2} alignItems="center">
            <IconButton onClick={() => setShowFilters(!showFilters)} color={showFilters ? 'primary' : 'inherit'}>
              <Filter size={20} />
            </IconButton>
            
            <Stack direction="row" spacing={1} alignItems="center">
              <Select
                size="small"
                value={currentDate.getMonth()}
                onChange={(e) => {
                  const newDate = new Date(currentDate);
                  newDate.setMonth(e.target.value as number);
                  setCurrentDate(newDate);
                }}
                sx={{ fontWeight: 800, borderRadius: 2, minWidth: 120 }}
              >
                {Array.from({ length: 12 }, (_, i) => (
                  <MenuItem key={i} value={i}>
                    {new Date(2000, i, 1).toLocaleString(language === 'ar' ? 'ar-EG' : 'en-US', { month: 'long' })}
                  </MenuItem>
                ))}
              </Select>
              
              <Select
                size="small"
                value={currentDate.getFullYear()}
                onChange={(e) => {
                  const newDate = new Date(currentDate);
                  newDate.setFullYear(e.target.value as number);
                  setCurrentDate(newDate);
                }}
                sx={{ fontWeight: 800, borderRadius: 2 }}
              >
                {Array.from({ length: 10 }, (_, i) => {
                  const year = new Date().getFullYear() - 5 + i;
                  return <MenuItem key={year} value={year}>{year}</MenuItem>;
                })}
              </Select>
            </Stack>
            <ButtonGroup variant="outlined" size="small">
              <IconButton onClick={handlePrev}>
                {isRtl ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
              </IconButton>
              <Button onClick={handleToday} sx={{ fontWeight: 700 }}>
                {language === 'ar' ? 'اليوم' : 'Today'}
              </Button>
              <IconButton onClick={handleNext}>
                {isRtl ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
              </IconButton>
            </ButtonGroup>
          </Stack>

          <ButtonGroup variant="soft" color="primary">
            <Button 
              onClick={() => setViewMode('day')} 
              variant={viewMode === 'day' ? 'contained' : 'text'}
            >
              {language === 'ar' ? 'يوم' : 'Day'}
            </Button>
            <Button 
              onClick={() => setViewMode('week')} 
              variant={viewMode === 'week' ? 'contained' : 'text'}
            >
              {language === 'ar' ? 'أسبوع' : 'Week'}
            </Button>
            <Button 
              onClick={() => setViewMode('month')} 
              variant={viewMode === 'month' ? 'contained' : 'text'}
            >
              {language === 'ar' ? 'شهر' : 'Month'}
            </Button>
            <Button 
              onClick={() => setViewMode('year')} 
              variant={viewMode === 'year' ? 'contained' : 'text'}
            >
              {language === 'ar' ? 'سنة' : 'Year'}
            </Button>
          </ButtonGroup>
        </Stack>
      </Paper>

      <Stack direction="row" spacing={3} sx={{ flex: 1, overflow: 'hidden' }}>
        {/* Filters Sidebar */}
        {showFilters && (
          <Paper sx={{ width: 280, p: 3, borderRadius: 4, overflowY: 'auto' }}>
            <CalendarFilters 
              filters={filters} 
              setFilters={setFilters} 
              departments={departments}
              services={services}
            />
          </Paper>
        )}

        {/* Calendar Grid */}
        <Paper sx={{ flex: 1, borderRadius: 4, overflow: 'hidden', position: 'relative' }}>
          <CalendarGrid 
            viewMode={viewMode} 
            currentDate={currentDate} 
            events={events}
            onEventClick={setSelectedEventId}
            onDayClick={(date) => {
              setCurrentDate(date);
              setViewMode('day');
            }}
          />
        </Paper>
      </Stack>

      {/* Details Modal */}
      <EventDetailsModal 
        event={selectedEvent} 
        open={!!selectedEventId} 
        onClose={() => setSelectedEventId(null)} 
      />
    </Stack>
  );
}
