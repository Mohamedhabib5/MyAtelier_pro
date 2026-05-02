import { useMemo } from 'react';

import { AppAgGrid } from '../../components/ag-grid/AppAgGrid';
import type { AppAgGridColumn } from '../../components/ag-grid/types';
import type { SummaryMetric } from './api';

type StatusRow = {
  key: string;
  label: string;
  count: number;
};

type Props = {
  statuses: SummaryMetric[];
  language: 'ar' | 'en';
  text: {
    bookingStatuses: string;
    bookingStatusesSubtitle: string;
    noData: string;
  };
  statusLabel: (key: string) => string;
};

export function BookingStatusGrid({ statuses, language, text, statusLabel }: Props) {
  const rows: StatusRow[] = statuses.map((s) => ({
    key: s.key,
    label: statusLabel(s.key),
    count: s.count,
  }));

  const columns = useMemo<AppAgGridColumn<StatusRow>[]>(
    () => [
      {
        field: 'label',
        headerName: language === 'ar' ? 'الحالة' : 'Status',
        flex: 2,
      },
      {
        field: 'count',
        headerName: language === 'ar' ? 'العدد' : 'Count',
        flex: 1,
        type: 'numericColumn',
      },
    ],
    [language]
  );

  return (
    <AppAgGrid<StatusRow>
      tableKey="report-booking-statuses"
      rows={rows}
      columns={columns}
      language={language}
      title={text.bookingStatuses}
      subtitle={text.bookingStatusesSubtitle}
      searchLabel={language === 'ar' ? 'بحث' : 'Search'}
      searchPlaceholder={language === 'ar' ? 'ابحث عن حالة...' : 'Search status...'}
      columnsLabel={language === 'ar' ? 'الأعمدة' : 'Columns'}
      exportLabel={language === 'ar' ? 'تصدير' : 'Export'}
      resetLabel={language === 'ar' ? 'إعادة تعيين' : 'Reset'}
      closeLabel={language === 'ar' ? 'إغلاق' : 'Close'}
      noRowsLabel={text.noData}
      rowsPerPageLabel={language === 'ar' ? 'صفوف في الصفحة' : 'Rows per page'}
      getRowId={(p) => p.data.key}
      height={280}
      csvFileName="booking-statuses.csv"
      pagination={false}
    />
  );
}
