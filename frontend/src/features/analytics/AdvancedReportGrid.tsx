import { useMemo } from 'react';
import { AppAgGrid } from '../../components/ag-grid';
import type { AdvancedBIRecord } from './api';
import { Chip, Stack, Typography, Box, Paper, IconButton, Breadcrumbs, Link } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import HomeIcon from '@mui/icons-material/Home';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import ReceiptIcon from '@mui/icons-material/Receipt';
import ListAltIcon from '@mui/icons-material/ListAlt';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useNavigate } from 'react-router-dom';
import { Button } from '@mui/material';

interface Props {
  records: AdvancedBIRecord[];
  loading: boolean;
  language: 'ar' | 'en';
  // Lifted Props
  groupStack: any[];
  setGroupStack: (stack: any[]) => void;
  drillDownPath: any[];
  setDrillDownPath: (path: any[]) => void;
  selectedBookingId: string | null;
  setSelectedBookingId: (id: string | null) => void;
}

type GroupField = { id: keyof AdvancedBIRecord; label: string };

export function AdvancedReportGrid({ 
  records, loading, language,
  groupStack, setGroupStack,
  drillDownPath, setDrillDownPath,
  selectedBookingId, setSelectedBookingId
}: Props) {
  const isAr = language === 'ar';
  const navigate = useNavigate();

  const handleBack = () => {
    if (selectedBookingId) {
      setSelectedBookingId(null);
    } else if (drillDownPath.length > 0) {
      setDrillDownPath(drillDownPath.slice(0, -1));
    } else if (groupStack.length > 0) {
      setGroupStack(groupStack.slice(0, -1));
    }
  };

  const processedRows = useMemo(() => {
    // If a specific booking is selected, show its lines
    if (selectedBookingId) {
      return records.filter(rec => rec.booking_id === selectedBookingId).map(line => ({
        ...line,
        isBookingLine: true
      }));
    }

    // If we are at the end of the grouping, show Unique Bookings
    if (drillDownPath.length >= groupStack.length) {
      const bookings: Record<string, any> = {};
      records.forEach(rec => {
        if (!bookings[rec.booking_id]) {
          bookings[rec.booking_id] = {
            isBookingSummary: true,
            booking_id: rec.booking_id,
            booking_number: rec.booking_number,
            customer_name: rec.customer_name,
            customer_phone: rec.customer_phone,
            customer_address: rec.customer_address,
            booking_date: rec.booking_date,
            line_price: 0,
            paid_amount: 0,
            remaining_amount: 0,
            line_count: 0
          };
        }
        bookings[rec.booking_id].line_price += rec.line_price || 0;
        bookings[rec.booking_id].paid_amount += rec.paid_amount || 0;
        bookings[rec.booking_id].remaining_amount += rec.remaining_amount || 0;
        bookings[rec.booking_id].line_count += 1;
      });
      return Object.values(bookings);
    }

    // Otherwise, show aggregated groups
    const currentGroupField = groupStack[drillDownPath.length];
    const groups: Record<string, any> = {};

    records.forEach(rec => {
      const fieldId = currentGroupField.id as keyof AdvancedBIRecord;
      const key = String(rec[fieldId]);
      if (!groups[key]) {
        groups[key] = {
          isGroup: true,
          groupName: key,
          groupFieldLabel: currentGroupField.label,
          line_price: 0,
          paid_amount: 0,
          remaining_amount: 0,
          record_count: 0
        };
      }
      groups[key].line_price += rec.line_price || 0;
      groups[key].paid_amount += rec.paid_amount || 0;
      groups[key].remaining_amount += rec.remaining_amount || 0;
      groups[key].record_count += 1;
    });

    return Object.values(groups);
  }, [records, groupStack, drillDownPath, selectedBookingId]);

  const columns = useMemo(() => {
    const isShowingLines = Boolean(selectedBookingId);
    const isShowingBookings = !selectedBookingId && drillDownPath.length >= groupStack.length;

    return [
      { 
        field: isShowingLines ? 'service_name' : (isShowingBookings ? 'booking_number' : 'groupName'), 
        headerName: isShowingLines ? (isAr ? 'الخدمة / السطر' : 'Service / Line') : (isShowingBookings ? (isAr ? 'رقم الحجز' : 'Booking #') : (isAr ? 'المجموعة' : 'Group')),
        pinned: isAr ? 'right' : 'left',
        width: 300,
        cellStyle: (params: any) => ({
          fontWeight: 'bold', 
          cursor: 'pointer',
          bgcolor: params.node.isRowPinned() ? 'rgba(0,0,0,0.05)' : 'inherit'
        }),
        cellRenderer: (params: any) => {
          if (params.node.isRowPinned()) return <Typography variant="body2" fontWeight={900}>{params.value}</Typography>;
          
          let displayValue = params.value;
          if (displayValue === 'null' || displayValue === null || displayValue === 'undefined' || displayValue === '') {
            const isDressField = params.data?.groupFieldLabel?.includes('فستان') || params.data?.groupFieldLabel?.includes('الفستان') || params.data?.groupFieldLabel?.includes('Dress');
            const isPaymentField = params.data?.groupFieldLabel?.includes('دفع') || params.data?.groupFieldLabel?.includes('الدفع') || params.data?.groupFieldLabel?.includes('Payment');
            const isUnpaid = params.data?.paid_amount === 0;

            if (isAr) {
              if (isDressField) displayValue = 'بدون فستان';
              else if (isPaymentField && isUnpaid) displayValue = 'لم يتم السداد بعد';
              else displayValue = `(${params.data?.groupFieldLabel || 'قيمة'} غير محددة)`;
            } else {
              if (isDressField) displayValue = 'No Dress';
              else if (isPaymentField && isUnpaid) displayValue = 'Not Paid Yet';
              else displayValue = `(No ${params.data?.groupFieldLabel || 'Value'})`;
            }
          }

          if (params.data?.isGroup) {
            return (
              <Stack direction='row' spacing={1} alignItems='center'>
                <NavigateNextIcon fontSize="small" color="primary" sx={{ transform: isAr ? 'rotate(180deg)' : 'none' }} />
                <Typography variant="body2" fontWeight={800} color="primary.main">{displayValue}</Typography>
                <Chip label={params.data.record_count} size="small" variant="outlined" sx={{ height: 20, fontSize: '0.7rem' }} />
              </Stack>
            );
          }
          if (params.data?.isBookingSummary) {
            return (
              <Stack direction='row' spacing={1} alignItems='center'>
                <ReceiptIcon fontSize="small" sx={{ color: 'text.secondary', mr: 0.5 }} />
                <Typography variant="body2" fontWeight={800}>#{params.value}</Typography>
                <Chip label={params.data.line_count} size="small" variant="outlined" sx={{ height: 18, fontSize: '0.6rem' }} />
              </Stack>
            );
          }
          if (params.data?.isBookingLine) {
            return (
              <Stack direction='row' spacing={1} alignItems='center'>
                <ListAltIcon fontSize="small" sx={{ color: 'primary.main', opacity: 0.7 }} />
                <Typography variant="body2" fontWeight={700} color="primary.dark">{params.value}</Typography>
              </Stack>
            );
          }
          return params.value;
        }
      },
      { 
        field: 'customer_name', 
        headerName: isAr ? 'العميل' : 'Customer',
        width: 180,
        hide: isShowingLines
      },
      { 
        field: 'customer_phone', 
        headerName: isAr ? 'رقم الهاتف' : 'Phone',
        width: 140,
        hide: !isShowingLines && !isShowingBookings
      },
      { 
        field: 'customer_address', 
        headerName: isAr ? 'العنوان' : 'Address',
        width: 200,
        hide: !isShowingLines && !isShowingBookings
      },
      { 
        field: 'dress_name', 
        headerName: isAr ? 'الفستان' : 'Dress',
        width: 150,
        hide: !isShowingLines
      },
      { 
        field: 'payment_method', 
        headerName: isAr ? 'طريقة الدفع' : 'Payment Method',
        width: 150,
        hide: !isShowingLines && !isShowingBookings
      },
      { 
        field: 'line_price', 
        headerName: isAr ? 'السعر' : 'Price',
        width: 130,
        cellStyle: (params: any) => ({ 
          fontWeight: 900,
          bgcolor: params.node.isRowPinned() ? 'rgba(0,0,0,0.05)' : 'inherit'
        }),
        valueFormatter: (params: any) => params.value?.toLocaleString()
      },
      { 
        field: 'paid_amount', 
        headerName: isAr ? 'المحصل' : 'Paid',
        width: 130,
        cellStyle: (params: any) => ({ 
          color: '#2e7d32', 
          fontWeight: 900,
          bgcolor: params.node.isRowPinned() ? 'rgba(46, 125, 50, 0.05)' : 'inherit'
        }),
        valueFormatter: (params: any) => params.value?.toLocaleString()
      },
      { 
        field: 'remaining_amount', 
        headerName: isAr ? 'المتبقي' : 'Remaining',
        width: 150,
        cellStyle: (params: any) => {
          const val = params.value || 0;
          let style: any = { fontWeight: 900 };
          
          if (val > 0) {
            style.color = '#d32f2f'; // Red color as requested
          } else {
            style.color = '#2e7d32';
          }
          
          if (params.node.isRowPinned()) {
            style.bgcolor = 'rgba(0,0,0,0.05)';
          }
          
          return style;
        },
        valueFormatter: (params: any) => params.value?.toLocaleString()
      }
    ];
  }, [isAr, groupStack, drillDownPath, selectedBookingId]);

  const pinnedBottomRowData = useMemo(() => {
    const totals = processedRows.reduce((acc, curr) => ({
      line_price: acc.line_price + (curr.line_price || 0),
      paid_amount: acc.paid_amount + (curr.paid_amount || 0),
      remaining_amount: acc.remaining_amount + (curr.remaining_amount || 0),
    }), { line_price: 0, paid_amount: 0, remaining_amount: 0 });

    return [{
      booking_number: isAr ? 'الإجمالي العام' : 'GRAND TOTAL',
      groupName: isAr ? 'الإجمالي العام' : 'GRAND TOTAL',
      service_name: isAr ? 'الإجمالي العام' : 'GRAND TOTAL',
      ...totals
    }];
  }, [processedRows, isAr]);

  const handleRowClick = (params: any) => {
    if (params.node.isRowPinned()) return;
    if (params.data?.isGroup) {
      setDrillDownPath([...drillDownPath, { label: params.data.groupFieldLabel, value: params.data.groupName }]);
    } else if (params.data?.isBookingSummary) {
      setSelectedBookingId(params.data.booking_id);
    } else if (params.data?.isBookingLine) {
      navigate(`/bookings?edit=${params.data.booking_id}`);
    }
  };

  return (
    <Box sx={{ '& .ag-row': { cursor: 'pointer' } }}>
      <AppAgGrid
        tableKey='advanced-bi-grid'
        rows={processedRows}
        columns={columns as any}
        language={language}
        loading={loading}
        pinnedBottomRowData={pinnedBottomRowData}
        onRowClicked={handleRowClick}
        height={600}
        searchLabel={isAr ? 'بحث' : 'Search'}
        searchPlaceholder={isAr ? 'ابحث...' : 'Search...'}
        columnsLabel={isAr ? 'الأعمدة' : 'Columns'}
        exportLabel={isAr ? 'تصدير' : 'Export'}
        resetLabel={isAr ? 'إعادة ضبط' : 'Reset'}
        closeLabel={isAr ? 'إغلاق' : 'Close'}
        noRowsLabel={isAr ? 'لا توجد بيانات' : 'No data'}
        rowsPerPageLabel={isAr ? 'سجل' : 'rows'}
        toolbarLeftContent={
          <Stack direction="row" spacing={2} alignItems="center" sx={{ overflowX: 'auto', py: 0.5, px: 1 }}>
            <Button
              size="small"
              variant="outlined"
              onClick={handleBack}
              disabled={drillDownPath.length === 0 && !selectedBookingId && groupStack.length === 0}
              startIcon={<ArrowBackIcon sx={{ transform: isAr ? 'rotate(180deg)' : 'none', fontSize: '0.9rem' }} />}
              sx={{ borderRadius: 2, fontWeight: 800, whiteSpace: 'nowrap', height: 32 }}
            >
              {isAr ? 'رجوع' : 'Back'}
            </Button>
          </Stack>
        }
      />
    </Box>
  );
}
