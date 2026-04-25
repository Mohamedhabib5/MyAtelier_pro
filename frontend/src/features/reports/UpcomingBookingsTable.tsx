import { Typography } from '@mui/material';

import { AppDataTable } from '../../components/data-table/AppDataTable';
import { useReportsText } from '../../text/reports';
import { useLanguage } from '../language/LanguageProvider';
import type { UpcomingBookingItem } from './api';

export function UpcomingBookingsTable({ items }: { items: UpcomingBookingItem[] }) {
  const { language } = useLanguage();
  const reportsText = useReportsText();

  if (!items.length) {
    return <Typography color='text.secondary'>{reportsText.print.noData}</Typography>;
  }

  return (
    <AppDataTable
      tableKey='reports-upcoming-bookings'
      rows={items}
      columns={[
        { key: 'booking_number', header: reportsText.table.bookingNumber, searchValue: (row) => row.booking_number, render: (row) => row.booking_number },
        { key: 'customer_name', header: reportsText.table.customer, searchValue: (row) => row.customer_name, render: (row) => row.customer_name },
        { key: 'service_name', header: reportsText.table.service, searchValue: (row) => row.service_name, render: (row) => row.service_name },
        { key: 'service_date', header: reportsText.table.serviceDate, searchValue: (row) => row.service_date, render: (row) => row.service_date },
        { key: 'status', header: reportsText.table.status, searchValue: (row) => row.status, render: (row) => row.status },
      ]}
      searchLabel={language === 'ar' ? 'بحث' : 'Search'}
      searchPlaceholder={language === 'ar' ? 'ابحث برقم الحجز أو العميل أو الخدمة' : 'Search by booking, customer, or service'}
      resetColumnsLabel={language === 'ar' ? 'إعادة الضبط' : 'Reset'}
      noRowsLabel={reportsText.print.noData}
      filtersLabel={language === 'ar' ? 'الفلاتر' : 'Filters'}
      columnsLabel={language === 'ar' ? 'الأعمدة' : 'Columns'}
      exportLabel={language === 'ar' ? 'تصدير' : 'Export'}
      rowsPerPageLabel={language === 'ar' ? 'عدد الصفوف' : 'Rows per page'}
      closeLabel={language === 'ar' ? 'إغلاق' : 'Close'}
      searchFields={[(row) => row.booking_number, (row) => row.customer_name, (row) => row.service_name, (row) => row.status]}
    />
  );
}
