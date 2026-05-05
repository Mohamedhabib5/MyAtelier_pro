import { Grid, Paper, Stack, Typography, Box, Chip, IconButton, Breadcrumbs, Link } from "@mui/material";
import { KPICard } from "./KPICard";
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import PendingActionsIcon from '@mui/icons-material/PendingActions';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import HomeIcon from '@mui/icons-material/Home';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';

interface DashboardProps {
  summary: {
    total_sales: number;
    total_paid: number;
    total_remaining: number;
    record_count: number;
    department_breakdown: Array<{ label: string, sales: number, count: number }>;
  };
  language: 'ar' | 'en';
  onFilterChange?: (value: string) => void;
  activeFilterValue?: string | null;
  drillDownPath?: Array<{ label: string, value: string }>;
  onBack?: () => void;
}

export function AnalyticsDashboard({ 
  summary, 
  language, 
  onFilterChange, 
  activeFilterValue,
  drillDownPath = [],
  onBack
}: DashboardProps) {
  const isAr = language === 'ar';

  return (
    <Stack spacing={2}>
      {/* KPI Cards */}
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KPICard
            title={isAr ? "إجمالي المبيعات" : "Total Sales"}
            value={summary.total_sales.toLocaleString()}
            color="#1976d2"
            icon={<TrendingUpIcon fontSize="small" />}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KPICard
            title={isAr ? "المبالغ المحصلة" : "Total Paid"}
            value={summary.total_paid.toLocaleString()}
            color="#2e7d32"
            icon={<AccountBalanceWalletIcon fontSize="small" />}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KPICard
            title={isAr ? "المبالغ المتبقية" : "Total Remaining"}
            value={summary.total_remaining.toLocaleString()}
            color="#d32f2f"
            icon={<PendingActionsIcon fontSize="small" />}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KPICard
            title={isAr ? "عدد العمليات" : "Total Records"}
            value={summary.record_count.toLocaleString()}
            color="#673ab7"
            icon={<ReceiptLongIcon fontSize="small" />}
          />
        </Grid>
      </Grid>

      {/* Dynamic Charts Section */}
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Paper 
            variant="outlined" 
            sx={{ 
              p: 2.5, 
              borderRadius: 5, 
              height: 380, 
              bgcolor: 'background.paper', 
              border: '1px solid rgba(0,0,0,0.06)',
              boxShadow: '0 4px 20px rgba(0,0,0,0.02)',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            {/* Simplified Chart Header */}
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Box>
                <Typography variant="subtitle1" fontWeight={900} color="text.primary" sx={{ lineHeight: 1.2 }}>
                  {isAr ? "توزيع المبيعات" : "Sales Distribution"}
                </Typography>
                <Typography variant="caption" fontWeight={700} color="text.secondary">
                  {isAr ? "نظرة عامة ديناميكية" : "Dynamic Overview"}
                </Typography>
              </Box>
              
              <Chip 
                icon={<TrendingUpIcon sx={{ fontSize: '0.9rem !important' }} />}
                label={isAr ? "تفاعلي" : "Interactive"} 
                color="primary"
                size="small"
                variant="outlined"
                sx={{ borderRadius: 2, fontWeight: 800, px: 0.5 }}
              />
            </Stack>

            <Box sx={{ flexGrow: 1, mt: 1 }}>
              <CustomBarChart 
                data={summary.department_breakdown} 
                onBarClick={onFilterChange}
                activeKey={activeFilterValue}
              />
            </Box>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper 
            variant="outlined" 
            sx={{ 
              p: 2.5, 
              borderRadius: 5, 
              height: 380, 
              bgcolor: 'background.paper', 
              border: '1px solid rgba(0,0,0,0.06)',
              boxShadow: '0 4px 20px rgba(0,0,0,0.02)',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <Typography variant="subtitle1" fontWeight={900} sx={{ mb: 2 }}>
              {isAr ? "نسبة التحصيل" : "Payment Ratio"}
            </Typography>
            <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <CustomDonutChart 
                paid={summary.total_paid} 
                remaining={summary.total_remaining} 
                language={language}
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Stack>
  );
}

// Phase 2: Enhanced Custom Bar Chart with Click Interaction
function CustomBarChart({ data, onBarClick, activeKey }: { data: any[], onBarClick?: (val: string) => void, activeKey?: string | null }) {
  const maxVal = Math.max(...data.map(d => d.sales), 1);
  
  return (
    <Box sx={{ width: '100%', height: '100%', display: 'flex', alignItems: 'flex-end', gap: 2, px: 2, pb: 4 }}>
      {data.map((item, i) => {
        const height = (item.sales / maxVal) * 100;
        const isActive = activeKey === item.label;
        
        return (
          <Box 
            key={i} 
            onClick={(e) => {
              e.stopPropagation();
              onBarClick?.(item.label);
            }}
            sx={{ 
              flex: 1, 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              gap: 1,
              cursor: 'pointer',
              height: '100%',
              justifyContent: 'flex-end',
              '&:hover .bar': { bgcolor: 'primary.main', transform: 'scaleX(1.1)' },
              '&:hover .val-text': { color: 'primary.main', fontWeight: 900 }
            }}
          >
            <Typography variant="caption" className="val-text" fontWeight={900} sx={{ fontSize: '0.65rem', transition: 'all 0.2s' }}>
              {Math.round(item.sales).toLocaleString()}
            </Typography>
            <Box 
              className="bar"
              sx={{ 
                width: '80%', 
                height: `${height}%`, 
                bgcolor: isActive ? 'primary.main' : 'primary.light',
                borderRadius: '4px 4px 0 0',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                minHeight: 4,
                boxShadow: isActive ? '0 0 12px rgba(25, 118, 210, 0.4)' : 'none'
              }} 
            />
            <Typography 
              variant="caption" 
              noWrap 
              sx={{ 
                width: '100%', 
                textAlign: 'center', 
                fontWeight: 800,
                fontSize: '0.7rem',
                transform: 'rotate(-30deg)',
                mt: 1,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                color: 'text.secondary'
              }}
            >
              {item.label}
            </Typography>
          </Box>
        );
      })}
    </Box>
  );
}

function CustomDonutChart({ paid, remaining, language }: { paid: number, remaining: number, language: string }) {
  const total = paid + remaining || 1;
  const paidPercent = (paid / total) * 100;
  const isAr = language === 'ar';
  
  const size = 160;
  const strokeWidth = 20;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (paidPercent / 100) * circumference;

  return (
    <Stack alignItems="center" spacing={2}>
      <Box sx={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          {/* Background circle (Remaining) */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="#f5f5f5"
            strokeWidth={strokeWidth}
          />
          {/* Remaining Amount Part */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="#d32f2f"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={0}
            strokeLinecap="round"
          />
          {/* Paid Amount Part */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="#2e7d32"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.5s ease' }}
          />
        </svg>
        <Box sx={{ 
          position: 'absolute', 
          top: '50%', 
          left: '50%', 
          transform: 'translate(-50%, -50%)',
          textAlign: 'center'
        }}>
          <Typography variant="h6" fontWeight={900} color="primary.main">
            {Math.round(paidPercent)}%
          </Typography>
          <Typography variant="caption" fontWeight={700} color="text.secondary">
            {isAr ? "نسبة التحصيل" : "Paid %"}
          </Typography>
        </Box>
      </Box>
      <Stack direction="row" spacing={2}>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Box sx={{ width: 12, height: 12, bgcolor: '#2e7d32', borderRadius: '50%' }} />
          <Typography variant="caption" fontWeight={700}>{isAr ? "محصل" : "Paid"}</Typography>
        </Stack>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Box sx={{ width: 12, height: 12, bgcolor: '#d32f2f', borderRadius: '50%' }} />
          <Typography variant="caption" fontWeight={700}>{isAr ? "متبقي" : "Remaining"}</Typography>
        </Stack>
      </Stack>
    </Stack>
  );
}
