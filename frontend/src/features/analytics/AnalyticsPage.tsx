import { useState, useMemo } from 'react';
import { Container, Stack, Typography, TextField, Button, Box, Paper, Divider, Breadcrumbs, Link, IconButton } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { getAdvancedBIReport, type AdvancedBIRecord } from './api';
import { AnalyticsDashboard } from './AnalyticsDashboard';
import { AdvancedReportGrid } from './AdvancedReportGrid';
import FilterAltIcon from '@mui/icons-material/FilterAlt';
import SearchIcon from '@mui/icons-material/Search';
import HomeIcon from '@mui/icons-material/Home';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import CloseIcon from '@mui/icons-material/Close';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

import { FloatingAnalyticsDock } from './FloatingAnalyticsDock';

export default function AnalyticsPage() {
  const language = 'ar';
  const isAr = language === 'ar';

  const availableGroups = useMemo(() => [
    { id: 'department_name', label: isAr ? 'القسم' : 'Department' },
    { id: 'booking_status', label: isAr ? 'الحالة' : 'Status' },
    { id: 'customer_name', label: isAr ? 'العميل' : 'Customer' },
    { id: 'service_name', label: isAr ? 'الخدمة' : 'Service' },
    { id: 'dress_name', label: isAr ? 'الفستان' : 'Dress' },
    { id: 'payment_method', label: isAr ? 'طريقة الدفع' : 'Payment Method' },
    { id: 'customer_address', label: isAr ? 'العنوان' : 'Address' },
  ], [isAr]);

  const [dateFrom, setDateFrom] = useState(() => {
    const d = new Date();
    d.setMonth(d.getMonth() - 1);
    return d.toISOString().split('T')[0];
  });
  const [dateTo, setDateTo] = useState(() => new Date().toISOString().split('T')[0]);
  
  // BI Context (Central Logic for Zoho/Power BI experience)
  const [groupStack, setGroupStack] = useState<any[]>([]);
  const [drillDownPath, setDrillDownPath] = useState<Array<{ label: string, value: string }>>([]);
  const [selectedBookingId, setSelectedBookingId] = useState<string | null>(null);

  // Robust Sync Logic: If group stack changes, reset or truncate path to prevent "messy" state
  const handleSetGroupStack = (newStack: any[]) => {
    setGroupStack(newStack);
    // If we remove a dimension or change order, it's safest to reset path to avoid logic mismatch
    setDrillDownPath([]); 
    setSelectedBookingId(null);
  };

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['advanced-bi', dateFrom, dateTo],
    queryFn: () => getAdvancedBIReport(dateFrom, dateTo),
  });

  // Dynamic Intelligence: Compute current context aggregates for both Charts and Grid
  const { filteredRecords, dynamicChartData, totals } = useMemo(() => {
    if (!data?.records) return { filteredRecords: [], dynamicChartData: [], totals: { sales: 0, paid: 0, rem: 0 } };

    let currentData = data.records;

    // 1. Apply active drill-down path filters
    drillDownPath.forEach((path, index) => {
      const fieldId = groupStack[index]?.id as keyof AdvancedBIRecord;
      if (fieldId) {
        currentData = currentData.filter(rec => String(rec[fieldId]) === path.value);
      }
    });

    // 2. Compute sums for the current focused view
    const currentTotals = currentData.reduce((acc, curr) => ({
      sales: acc.sales + (curr.line_price || 0),
      paid: acc.paid + (curr.paid_amount || 0),
      rem: acc.rem + (curr.remaining_amount || 0),
    }), { sales: 0, paid: 0, rem: 0 });

    // 3. Aggregate data for charts based on the NEXT dimension in the stack
    // FALLBACK: If no group stack, default to Department for charts
    const nextGroupField = groupStack[drillDownPath.length] || { id: 'department_name', label: isAr ? 'القسم' : 'Department' };
    const chartGroups: Record<string, any> = {};

    currentData.forEach(rec => {
      const fieldId = nextGroupField.id as keyof AdvancedBIRecord;
      const key = String(rec[fieldId]);
      if (!chartGroups[key]) {
        chartGroups[key] = { label: key, sales: 0, count: 0 };
      }
      chartGroups[key].sales += rec.line_price || 0;
      chartGroups[key].count += 1;
    });

    return { 
      filteredRecords: currentData, 
      dynamicChartData: Object.values(chartGroups),
      totals: currentTotals
    };
  }, [data?.records, drillDownPath, groupStack, isAr]);

  const dynamicSummary = useMemo(() => ({
    total_sales: totals.sales,
    total_paid: totals.paid,
    total_remaining: totals.rem,
    record_count: filteredRecords.length,
    department_breakdown: dynamicChartData
  }), [totals, filteredRecords.length, dynamicChartData]);

  const resetPath = () => {
    setDrillDownPath([]);
    setGroupStack([]);
    setSelectedBookingId(null);
  };

  const handleBack = () => {
    if (selectedBookingId) {
      setSelectedBookingId(null);
    } else if (drillDownPath.length > 0) {
      setDrillDownPath(drillDownPath.slice(0, -1));
    } else if (groupStack.length > 0) {
      // Universal Back: If at top level of drill-down, undo the last grouping selection
      setGroupStack(groupStack.slice(0, -1));
    }
  };

  return (
    <Container maxWidth='xl' sx={{ py: 2, pb: 12 }}>
      <Stack spacing={2}>
        {/* Compact Integrated Header & Filters */}
        <Paper 
          variant="outlined"
          sx={{ 
            p: 2, 
            borderRadius: 4, 
            bgcolor: 'background.paper',
            border: '1px solid rgba(0,0,0,0.05)',
            position: 'sticky',
            top: 0,
            zIndex: 1000,
            boxShadow: '0 4px 20px rgba(0,0,0,0.03)',
            backdropFilter: 'blur(8px)',
          }}
        >
          <Stack direction={{ xs: 'column', lg: 'row' }} spacing={2} justifyContent='space-between' alignItems={{ lg: 'center' }}>
            {/* Title Only - Isolated & Clean */}
            <Box>
              <Typography variant='h6' fontWeight={900} sx={{ lineHeight: 1.2, color: 'text.primary' }}>
                {isAr ? 'مركز التحليلات الذكية' : 'Smart Analytics Center'}
              </Typography>
            </Box>

            {/* Compact Filters & Actions */}
            <Stack direction='row' spacing={1.5} alignItems='center' sx={{ flexWrap: 'wrap', gap: 1 }}>
              <Stack direction='row' spacing={1} alignItems='center' sx={{ display: { xs: 'none', sm: 'flex' } }}>
                <FilterAltIcon fontSize="small" color='primary' />
                <Typography variant='caption' fontWeight={800}>
                  {isAr ? 'تصفية بالتاريخ:' : 'Date Filter:'}
                </Typography>
              </Stack>
              <TextField
                type='date'
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                size='small'
                sx={{ 
                  '& .MuiInputBase-root': { borderRadius: 3, height: 36, fontSize: '0.8rem' },
                  width: 140
                }}
              />
              <TextField
                type='date'
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                size='small'
                sx={{ 
                  '& .MuiInputBase-root': { borderRadius: 3, height: 36, fontSize: '0.8rem' },
                  width: 140
                }}
              />
              <Button 
                variant='contained' 
                onClick={() => refetch()}
                size="small"
                sx={{ 
                  borderRadius: 3, 
                  height: 36, 
                  px: 2, 
                  fontWeight: 800,
                  boxShadow: '0 4px 12px rgba(233, 30, 99, 0.2)' 
                }}
              >
                {isAr ? 'تحديث' : 'Update'}
              </Button>
            </Stack>
          </Stack>
        </Paper>

        {/* Dashboard Section (Dynamic Charts) */}
        {data && (
          <AnalyticsDashboard 
            summary={dynamicSummary} 
            language={language} 
            drillDownPath={drillDownPath}
            onBack={handleBack}
            onFilterChange={(value) => {
              const nextGroupField = groupStack[drillDownPath.length] || { id: 'booking_status', label: isAr ? 'الحالة' : 'Status' };
              setDrillDownPath([...drillDownPath, { label: nextGroupField.label, value }]);
            }}
            activeFilterValue={null}
          />
        )}

        <Divider />

        {/* Grid Section */}
        <AdvancedReportGrid 
          records={filteredRecords} 
          loading={isLoading} 
          language={language}
          dateFrom={dateFrom}
          dateTo={dateTo}
          drillDownPath={drillDownPath}
          setDrillDownPath={(path) => {
            setDrillDownPath(path);
            setSelectedBookingId(null); // Reset booking when path changes
          }}
          groupStack={groupStack}
          setGroupStack={handleSetGroupStack}
          selectedBookingId={selectedBookingId}
          setSelectedBookingId={setSelectedBookingId}
          availableGroups={availableGroups}
        />

        {/* The Floating Smart Dock */}
        <FloatingAnalyticsDock 
          language={language}
          groupStack={groupStack}
          setGroupStack={handleSetGroupStack}
          drillDownPath={drillDownPath}
          onBack={handleBack}
          onReset={resetPath}
          onRefresh={() => refetch()}
          availableGroups={availableGroups}
        />
      </Stack>
    </Container>
  );
}
