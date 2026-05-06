import { 
  Box, 
  Card, 
  Stack, 
  Typography, 
  IconButton, 
  Chip,
  alpha,
  Divider
} from '@mui/material';
import { MoreVertical, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { useThemeSettings } from '../../features/theme/ThemeSettingsProvider';

interface Props<Row> {
  rows: Row[];
  columns: any[];
  onRowClicked?: (params: any) => void;
  getRowId?: (params: any) => string;
}

export function MobileCardView<Row>({ rows, columns, onRowClicked, getRowId }: Props<Row>) {
  const { primaryColor, themeMode } = useThemeSettings();
  const isDark = themeMode === 'dark';

  // Filter out hidden columns and selection columns
  const visibleColumns = columns.filter(col => !col.hide && col.headerName && col.field);

  return (
    <Stack spacing={2} sx={{ p: 2 }}>
      {rows.map((row, index) => {
        const id = getRowId ? getRowId({ data: row } as any) : (row as any).id || index;
        
        return (
          <motion.div
            key={id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <Card 
              onClick={() => onRowClicked && onRowClicked({ data: row })}
              sx={{ 
                p: 2, 
                borderRadius: 4,
                cursor: 'pointer',
                transition: 'transform 0.2s',
                '&:active': { transform: 'scale(0.98)' },
                bgcolor: isDark ? 'rgba(255,255,255,0.03)' : '#fff',
                border: `1px solid ${isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'}`,
                boxShadow: isDark ? 'none' : '0 4px 12px rgba(0,0,0,0.03)'
              }}
            >
              <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 1.5 }}>
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 800, color: primaryColor }}>
                    {String((row as any)[visibleColumns[0]?.field] || '')}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.7 }}>
                    {String((row as any)[visibleColumns[1]?.field] || '')}
                  </Typography>
                </Box>
                <IconButton size="small">
                  <MoreVertical size={18} />
                </IconButton>
              </Stack>

              <Divider sx={{ my: 1.5, opacity: 0.1 }} />

              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1.5 }}>
                {visibleColumns.slice(2, 6).map((col) => (
                  <Box key={col.field}>
                    <Typography variant="caption" sx={{ opacity: 0.5, fontWeight: 700, display: 'block', mb: 0.2 }}>
                      {col.headerName}
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {String((row as any)[col.field] || '-')}
                    </Typography>
                  </Box>
                ))}
              </Box>

              <Stack direction="row" justifyContent="flex-end" sx={{ mt: 1 }}>
                <ChevronRight size={16} style={{ opacity: 0.3 }} />
              </Stack>
            </Card>
          </motion.div>
        );
      })}
    </Stack>
  );
}
