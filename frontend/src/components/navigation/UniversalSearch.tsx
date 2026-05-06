import { useState, useEffect, useCallback } from 'react';
import { 
  Dialog, 
  DialogContent, 
  Box, 
  InputBase, 
  List, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText, 
  Typography, 
  Stack, 
  Divider,
  CircularProgress,
  alpha,
  useTheme
} from '@mui/material';
import { 
  Search, 
  User, 
  Calendar, 
  Shirt, 
  X, 
  Command,
  ChevronRight
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useThemeSettings } from '../../features/theme/ThemeSettingsProvider';
import { apiRequest } from '../../lib/api';

interface SearchResult {
  id: string;
  title: string;
  subtitle: string;
  type: 'customer' | 'booking' | 'dress' | 'action';
  path: string;
}

export function UniversalSearch() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const { primaryColor, themeMode } = useThemeSettings();
  const theme = useTheme();
  const navigate = useNavigate();

  const isDark = themeMode === 'dark';

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSearch = useCallback(async (val: string) => {
    setQuery(val);
    if (val.length < 2) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      const data = await apiRequest<SearchResult[]>(`/api/search?q=${encodeURIComponent(val)}`);
      setResults(data);
    } catch (err) {
      console.error('Search failed:', err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSelect = (result: SearchResult) => {
    navigate(result.path);
    setOpen(false);
    setQuery('');
  };

  const getIcon = (type: SearchResult['type']) => {
    switch (type) {
      case 'customer': return <User size={18} />;
      case 'booking': return <Calendar size={18} />;
      case 'dress': return <Shirt size={18} />;
      case 'action': return <Command size={18} />;
      default: return <Search size={18} />;
    }
  };

  return (
    <>
      <Box 
        onClick={() => setOpen(true)}
        sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 1, 
          px: 2, 
          py: 0.8, 
          borderRadius: 50, 
          bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)',
          cursor: 'pointer',
          transition: 'all 0.2s',
          border: '1px solid transparent',
          '&:hover': {
            bgcolor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)',
            borderColor: alpha(primaryColor, 0.3)
          },
          minWidth: { xs: 40, md: 240 }
        }}
      >
        <Search size={18} style={{ opacity: 0.6 }} />
        <Typography sx={{ display: { xs: 'none', md: 'block' }, opacity: 0.5, fontSize: '0.85rem', flex: 1, fontWeight: 500 }}>
          بحث...
        </Typography>
        <Box sx={{ 
          display: { xs: 'none', md: 'flex' }, 
          alignItems: 'center', 
          gap: 0.5, 
          px: 0.6, 
          py: 0.1, 
          borderRadius: 1, 
          border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
          bgcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)',
          fontSize: '0.65rem',
          fontWeight: 800,
          opacity: 0.7,
          color: primaryColor
        }}>
          {navigator.platform.toUpperCase().indexOf('MAC') >= 0 ? '⌘ K' : 'CTRL K'}
        </Box>
      </Box>

      <Dialog 
        open={open} 
        onClose={() => setOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 4,
            mt: '10vh',
            backgroundImage: 'none',
            bgcolor: isDark ? 'rgba(30, 31, 46, 0.95)' : 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)'}`,
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
          }
        }}
        sx={{
          '& .MuiBackdrop-root': {
            backdropFilter: 'blur(4px)',
            bgcolor: 'rgba(0,0,0,0.4)'
          }
        }}
      >
        <DialogContent sx={{ p: 2 }}>
          <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 1 }}>
            <Search size={22} style={{ color: primaryColor }} />
            <InputBase 
              autoFocus
              placeholder="ابحث عن عميل، حجز، أو فستان..."
              fullWidth
              value={query}
              onChange={(e) => handleSearch(e.target.value)}
              sx={{ fontSize: '1.1rem', fontWeight: 500 }}
            />
            {loading ? <CircularProgress size={20} /> : query && <X size={20} style={{ cursor: 'pointer', opacity: 0.5 }} onClick={() => setQuery('')} />}
          </Stack>
          
          <Divider sx={{ mx: -2, my: 1 }} />

          <List sx={{ maxHeight: '60vh', overflow: 'auto', py: 0 }}>
            {results.length > 0 ? (
              results.map((result) => (
                <ListItemButton 
                  key={`${result.type}-${result.id}`}
                  onClick={() => handleSelect(result)}
                  sx={{ 
                    borderRadius: 2, 
                    mb: 0.5,
                    '&:hover': { bgcolor: alpha(primaryColor, 0.08) }
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 40, color: primaryColor }}>
                    {getIcon(result.type)}
                  </ListItemIcon>
                  <ListItemText 
                    primary={result.title} 
                    secondary={result.subtitle}
                    primaryTypographyProps={{ fontWeight: 700 }}
                  />
                  <ChevronRight size={16} style={{ opacity: 0.3 }} />
                </ListItemButton>
              ))
            ) : query.length >= 2 && !loading ? (
              <Box sx={{ p: 4, textAlign: 'center', opacity: 0.5 }}>
                <Typography>لا توجد نتائج مطابقة لبحثك.</Typography>
              </Box>
            ) : !query && (
              <Box sx={{ p: 2 }}>
                <Typography variant="caption" sx={{ fontWeight: 800, opacity: 0.5, letterSpacing: 1, textTransform: 'uppercase' }}>
                  عمليات سريعة مقترحة
                </Typography>
                <ListItemButton sx={{ borderRadius: 2, mt: 1 }} onClick={() => handleSelect({ id: 'new-booking', title: 'حجز جديد', subtitle: 'إضافة حجز فستان جديد', type: 'action', path: '/bookings?action=new' })}>
                  <ListItemIcon sx={{ minWidth: 40 }}><Command size={18} /></ListItemIcon>
                  <ListItemText primary="إنشاء حجز جديد" />
                </ListItemButton>
                <ListItemButton sx={{ borderRadius: 2 }} onClick={() => handleSelect({ id: 'reports', title: 'التقارير', subtitle: 'الذهاب للتقارير التحليلية', type: 'action', path: '/reports' })}>
                  <ListItemIcon sx={{ minWidth: 40 }}><Calendar size={18} /></ListItemIcon>
                  <ListItemText primary="عرض التقارير" />
                </ListItemButton>
              </Box>
            )}
          </List>
          
          <Divider sx={{ mx: -2, mt: 1, mb: 1 }} />
          
          <Stack direction="row" spacing={2} sx={{ px: 1, opacity: 0.5 }}>
            <Stack direction="row" alignItems="center" spacing={0.5}>
              <Box sx={{ px: 0.6, py: 0.2, bgcolor: 'rgba(0,0,0,0.1)', borderRadius: 0.5, fontSize: '0.7rem' }}>ENTER</Box>
              <Typography variant="caption">للإختيار</Typography>
            </Stack>
            <Stack direction="row" alignItems="center" spacing={0.5}>
              <Box sx={{ px: 0.6, py: 0.2, bgcolor: 'rgba(0,0,0,0.1)', borderRadius: 0.5, fontSize: '0.7rem' }}>ESC</Box>
              <Typography variant="caption">للإغلاق</Typography>
            </Stack>
          </Stack>
        </DialogContent>
      </Dialog>
    </>
  );
}
