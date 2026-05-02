import { Grid } from '@mui/material';

import { SectionCard } from '../../components/SectionCard';
import { MetricsBarChart } from '../dashboard/MetricsBarChart';
import type { ChartItem, CountItem, DailyIncomeItem } from './api';

type Props = {
  dailyIncome: DailyIncomeItem[];
  departmentIncome: ChartItem[];
  topServices: CountItem[];
  text: {
    dailyIncome: string;
    dailyIncomeSubtitle: string;
    deptIncome: string;
    deptIncomeSubtitle: string;
    topServices: string;
    topServicesSubtitle: string;
    noData: string;
  };
  formatCurrency: (v: number) => string;
  formatCount: (v: number) => string;
};

export function ReportChartsRow({
  dailyIncome,
  departmentIncome,
  topServices,
  text,
  formatCurrency,
  formatCount,
}: Props) {
  const dailyItems = dailyIncome.map((item) => ({
    label: item.date,
    value: item.amount,
    valueLabel: formatCurrency(item.amount),
  }));

  const deptItems = departmentIncome.map((item) => ({
    label: item.label,
    value: item.value,
    valueLabel: formatCurrency(item.value),
  }));

  const serviceItems = topServices.map((item) => ({
    label: item.label,
    value: item.count,
    valueLabel: `${formatCount(item.count)}`,
  }));

  return (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, md: 4 }}>
        <SectionCard title={text.dailyIncome} subtitle={text.dailyIncomeSubtitle}>
          <MetricsBarChart items={dailyItems} emptyLabel={text.noData} color="#2e7d32" />
        </SectionCard>
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <SectionCard title={text.deptIncome} subtitle={text.deptIncomeSubtitle}>
          <MetricsBarChart items={deptItems} emptyLabel={text.noData} color="#1565c0" />
        </SectionCard>
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <SectionCard title={text.topServices} subtitle={text.topServicesSubtitle}>
          <MetricsBarChart items={serviceItems} emptyLabel={text.noData} color="#ef6c00" />
        </SectionCard>
      </Grid>
    </Grid>
  );
}
