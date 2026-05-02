import { Alert, Box, Chip, FormControl, IconButton, InputLabel, MenuItem, Select, Stack, Typography } from '@mui/material';
import type { ColDef } from 'ag-grid-community';
import { useMemo, useState } from 'react';
import { reportStatusLabel, useReportsText } from '../../text/reports';

import { AppAgGrid } from '../../components/ag-grid';
import { EMPTY_VALUE, bookingStatusLabel, useCommonText, useLanguageFormatters } from '../../text/common';
import type { DetailedReportRowResponse } from './api';

type Props = {
  language: 'ar' | 'en';
  rows: DetailedReportRowResponse[];
  loading: boolean;
};

type GroupByField = 
    | 'none' 
    | 'booking_number' 
    | 'customer_name' 
    | 'department_name' 
    | 'service_name' 
    | 'dress_name'
    | 'payment_method'
    | 'booking_date' 
    | 'booking_status' 
    | 'created_by';

export function DetailedReportGrid({ language, rows, loading }: Props) {
  const commonText = useCommonText();
  const formatters = useLanguageFormatters();
  const reportsText = useReportsText();
  const t = reportsText.comprehensive.detailedTable;
  
  const [groupBy, setGroupBy] = useState<GroupByField>('none');

  const groupableOptions: { value: GroupByField; label: string }[] = [
    { value: 'none', label: language === 'ar' ? 'بدون تجميع' : 'No Grouping' },
    { value: 'booking_number', label: t.bookingId },
    { value: 'customer_name', label: t.customerName },
    { value: 'department_name', label: t.department },
    { value: 'service_name', label: t.service },
    { value: 'dress_name', label: language === 'ar' ? 'اسم الفستان' : 'Dress Name' },
    { value: 'payment_method', label: language === 'ar' ? 'طريقة الدفع' : 'Payment Method' },
    { value: 'booking_date', label: t.bookingDate },
    { value: 'booking_status', label: t.bookingStatus },
    { value: 'created_by', label: language === 'ar' ? 'الموظف' : 'Created By' },
  ];

  const transformedRows = useMemo(() => {
    if (!groupBy || groupBy === 'none' || !rows.length) return rows;

    const groupedMap: Record<string, DetailedReportRowResponse[]> = {};
    rows.forEach(row => {
      let val = String(row[groupBy as keyof DetailedReportRowResponse] ?? EMPTY_VALUE);
      if (groupBy === 'booking_status') val = reportStatusLabel(language, val);
      
      if (!groupedMap[val]) groupedMap[val] = [];
      groupedMap[val].push(row);
    });

    const result: any[] = [];
    Object.entries(groupedMap).forEach(([key, items]) => {
      const totalLine = items.reduce((sum, i) => sum + i.line_price, 0);
      const totalPaid = items.reduce((sum, i) => sum + i.paid_amount, 0);
      const totalRem = items.reduce((sum, i) => sum + i.remaining_amount, 0);

      result.push({
        isGroupHeader: true,
        groupLabel: key,
        groupCount: items.length,
        line_price: totalLine,
        paid_amount: totalPaid,
        remaining_amount: totalRem,
        booking_line_id: `header-${key}-${groupBy}`,
        // Empty fields to avoid undefined
        booking_number: '',
        customer_name: '',
        service_name: '',
        booking_date: '',
        service_date: '',
      });
      result.push(...items);
    });

    return result;
  }, [rows, groupBy, language]);

  const grandTotalRow = useMemo(() => {
    if (!rows.length) return [];
    
    const totalLine = rows.reduce((sum, i) => sum + i.line_price, 0);
    const totalPaid = rows.reduce((sum, i) => sum + i.paid_amount, 0);
    const totalRem = rows.reduce((sum, i) => sum + i.remaining_amount, 0);

    return [{
        isGrandTotal: true,
        booking_number: language === 'ar' ? 'الإجمالي الكلي' : 'Grand Total',
        line_price: totalLine,
        paid_amount: totalPaid,
        remaining_amount: totalRem,
        booking_line_id: 'grand-total'
    }];
  }, [rows, language]);

  const columns = useMemo<ColDef<any>[]>(
    () => [
      { 
        colId: 'booking_number', 
        field: 'booking_number', 
        headerName: t.bookingId, 
        pinned: language === 'ar' ? 'right' : 'left',
        cellRenderer: (params: any) => {
            if (params.data?.isGroupHeader) {
                return (
                    <Typography variant="subtitle2" fontWeight={800} color="primary.main">
                        {params.data.groupLabel} ({params.data.groupCount})
                    </Typography>
                );
            }
            if (params.data?.isGrandTotal) {
                return (
                    <Typography variant="subtitle2" fontWeight={900} color="secondary.main">
                        {params.value}
                    </Typography>
                );
            }
            return params.value || EMPTY_VALUE;
        }
      },
      { colId: 'external_code', field: 'external_code', headerName: t.externalCode, valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      { colId: 'booking_date', field: 'booking_date', headerName: t.bookingDate, valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      { colId: 'customer_name', field: 'customer_name', headerName: t.customerName, valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      { colId: 'customer_phone', field: 'customer_phone', headerName: t.customerPhone, valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      { colId: 'customer_phone_2', field: 'customer_phone_2', headerName: language === 'ar' ? 'رقم الهاتف 2' : 'Phone 2', valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      { colId: 'department_name', field: 'department_name', headerName: t.department, valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      { colId: 'service_name', field: 'service_name', headerName: t.service, valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      { colId: 'dress_code', field: 'dress_code', headerName: t.dressCode, valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      { colId: 'dress_name', field: 'dress_name', headerName: language === 'ar' ? 'اسم الفستان' : 'Dress Name', valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      { colId: 'service_date', field: 'service_date', headerName: t.serviceDate, valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      { 
        colId: 'line_price', 
        field: 'line_price', 
        headerName: t.linePrice, 
        filter: 'agNumberColumnFilter',
        valueFormatter: ({ value }) => formatters.formatCurrency(value ?? 0),
        cellStyle: (params) => (params.data?.isGroupHeader || params.data?.isGrandTotal) ? { fontWeight: 'bold', color: '#1565c0' } : undefined
      },
      { 
        colId: 'paid_amount', 
        field: 'paid_amount', 
        headerName: t.paidAmount, 
        filter: 'agNumberColumnFilter',
        valueFormatter: ({ value }) => formatters.formatCurrency(value ?? 0),
        cellStyle: (params) => (params.data?.isGroupHeader || params.data?.isGrandTotal) ? { fontWeight: 'bold', color: '#2e7d32' } : undefined
      },
      { 
        colId: 'remaining_amount', 
        field: 'remaining_amount', 
        headerName: t.remainingAmount, 
        filter: 'agNumberColumnFilter',
        valueFormatter: ({ value }) => formatters.formatCurrency(value ?? 0),
        cellStyle: (params) => (params.data?.isGroupHeader || params.data?.isGrandTotal) ? { fontWeight: 'bold', color: '#d32f2f' } : undefined
      },
      { colId: 'payment_method', field: 'payment_method', headerName: language === 'ar' ? 'طريقة الدفع' : 'Payment Method', valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      { colId: 'payment_reference', field: 'payment_reference', headerName: language === 'ar' ? 'كود الدفعة / المرجع' : 'Payment Ref', valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      { colId: 'payment_type', field: 'payment_type', headerName: language === 'ar' ? 'نوع الحركة' : 'Payment Type', valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      {
        colId: 'booking_status',
        field: 'booking_status',
        headerName: t.bookingStatus,
        cellRenderer: ({ data }: { data: any | undefined }) => {
          if (!data || data.isGroupHeader || data.isGrandTotal) return null;
          return (
            <Chip
              size="small"
              label={bookingStatusLabel(language, data.booking_status)}
              color={data.booking_status === 'completed' ? 'success' : data.booking_status === 'cancelled' ? 'default' : 'warning'}
            />
          );
        }
      },
      {
        colId: 'line_status',
        field: 'line_status',
        headerName: t.lineStatus,
        cellRenderer: ({ data }: { data: any | undefined }) => {
          if (!data || data.isGroupHeader || data.isGrandTotal) return null;
          return (
            <Chip
              size="small"
              label={bookingStatusLabel(language, data.line_status)}
              color={data.line_status === 'completed' ? 'success' : data.line_status === 'cancelled' ? 'default' : 'primary'}
            />
          );
        }
      },
      { colId: 'created_by', field: 'created_by', headerName: language === 'ar' ? 'الموظف' : 'Employee', valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
      { colId: 'notes', field: 'notes', headerName: t.notes, valueFormatter: ({ value, data }) => (data?.isGroupHeader || data?.isGrandTotal) ? '' : (value ?? EMPTY_VALUE) },
    ],
    [language, t, formatters]
  );

  return (
    <Stack spacing={2}>
        <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 1 }}>
            <FormControl size="small" sx={{ minWidth: 200 }}>
                <InputLabel id="group-by-label">{language === 'ar' ? 'تجميع حسب' : 'Group By'}</InputLabel>
                <Select
                    labelId="group-by-label"
                    value={groupBy}
                    label={language === 'ar' ? 'تجميع حسب' : 'Group By'}
                    onChange={(e) => setGroupBy(e.target.value as GroupByField)}
                    sx={{ borderRadius: 3 }}
                >
                    {groupableOptions.map(opt => (
                        <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                    ))}
                </Select>
            </FormControl>
            <Typography variant="caption" color="text.secondary">
                {language === 'ar' 
                    ? 'اختر عموداً لتجميع البيانات وعرض الإجماليات الفرعية' 
                    : 'Select a column to group data and show sub-totals'}
            </Typography>
        </Stack>

        <AppAgGrid
            tableKey="detailed-reports-grid"
            rows={transformedRows}
            columns={columns}
            language={language}
            searchLabel={language === 'ar' ? 'بحث تفصيلي' : 'Search data'}
            searchPlaceholder={language === 'ar' ? 'رقم الحجز، العميل، الخدمة...' : 'Booking, customer, service...'}
            columnsLabel={language === 'ar' ? 'الأعمدة' : 'Columns'}
            exportLabel={language === 'ar' ? 'تصدير' : 'Export'}
            resetLabel={language === 'ar' ? 'إعادة الضبط' : 'Reset'}
            closeLabel={language === 'ar' ? 'إغلاق' : 'Close'}
            noRowsLabel={language === 'ar' ? 'لا توجد بيانات مطابقة.' : 'No matching data found.'}
            rowsPerPageLabel={language === 'ar' ? 'عدد الصفوف' : 'Rows per page'}
            loading={loading}
            csvFileName="detailed_report.csv"
            getRowId={({ data }) => data.booking_line_id}
            externalPagination={undefined}
            getRowStyle={(params) => {
                if (params.data?.isGroupHeader) {
                    return { 
                        backgroundColor: 'rgba(21, 101, 192, 0.08)', 
                        fontWeight: 'bold',
                        borderBottom: '2px solid rgba(21, 101, 192, 0.2)'
                    };
                }
                if (params.data?.isGrandTotal) {
                    return {
                        backgroundColor: 'rgba(0, 0, 0, 0.05)',
                        fontWeight: 900,
                        borderTop: '2px solid rgba(0, 0, 0, 0.2)'
                    };
                }
                return undefined;
            }}
            pinnedBottomRowData={grandTotalRow}
        />
    </Stack>
  );
}
