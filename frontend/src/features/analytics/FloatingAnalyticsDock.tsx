import { Paper, Stack, Box, Chip, IconButton, Typography, Divider, Tooltip, Portal } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import RefreshIcon from '@mui/icons-material/Refresh';
import HomeIcon from '@mui/icons-material/Home';
import LayersIcon from '@mui/icons-material/Layers';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';

interface FloatingAnalyticsDockProps {
  language: 'ar' | 'en';
  groupStack: any[];
  setGroupStack: (stack: any[]) => void;
  drillDownPath: any[];
  onBack: () => void;
  onReset: () => void;
  onRefresh: () => void;
  availableGroups: any[];
}

export function FloatingAnalyticsDock({
  language,
  groupStack,
  setGroupStack,
  drillDownPath,
  onBack,
  onReset,
  onRefresh,
  availableGroups
}: FloatingAnalyticsDockProps) {
  const isAr = language === 'ar';

  return (
    <Portal>
      <Box
        sx={{
          position: 'fixed',
          bottom: 40, // Slightly higher to avoid mobile browser bars
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 9999,
          width: 'auto',
          maxWidth: '95vw',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          pointerEvents: 'none' // Allow scrolling content behind the dock box
        }}
      >
        <Paper
          elevation={12}
          sx={{
            p: 0.8,
            borderRadius: 100,
            bgcolor: 'rgba(255, 255, 255, 0.98)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(233, 30, 99, 0.2)',
            display: 'flex',
            alignItems: 'center',
            gap: 1.2,
            px: 1.5,
            boxShadow: '0 15px 45px rgba(0,0,0,0.15)',
            pointerEvents: 'auto' // Re-enable clicks for the buttons
          }}
        >
          {/* Main Actions */}
          <Stack direction="row" spacing={1} alignItems="center">
            <Tooltip title={isAr ? "الرئيسية" : "Home"}>
              <IconButton 
                size="small" 
                onClick={onReset}
                sx={{ bgcolor: 'background.paper', border: '1px solid #eee' }}
              >
                <HomeIcon fontSize="small" color="primary" />
              </IconButton>
            </Tooltip>
            
            <Tooltip title={isAr ? "رجوع" : "Back"}>
              <IconButton 
                size="small" 
                onClick={onBack}
                disabled={drillDownPath.length === 0 && groupStack.length === 0}
                sx={{ bgcolor: 'background.paper', border: '1px solid #eee' }}
              >
                <ArrowBackIcon fontSize="small" sx={{ transform: isAr ? 'rotate(180deg)' : 'none' }} />
              </IconButton>
            </Tooltip>
          </Stack>

          <Divider orientation="vertical" flexItem sx={{ height: 24, alignSelf: 'center' }} />

          {/* Grouping Section */}
          <Stack direction="row" spacing={1} alignItems="center" sx={{ overflowX: 'auto', maxWidth: { xs: 200, sm: 400, md: 600 } }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mr: 1 }}>
              <LayersIcon sx={{ fontSize: '1rem', color: 'primary.main' }} />
              <Typography variant="caption" fontWeight={900} color="primary.main" sx={{ whiteSpace: 'nowrap' }}>
                {isAr ? "تجميع:" : "Group:"}
              </Typography>
            </Box>
            {availableGroups.map((group) => {
              const isSelected = groupStack.find((gs) => gs.id === group.id);
              return (
                <Chip
                  key={group.id}
                  label={group.label}
                  onClick={() =>
                    isSelected
                      ? setGroupStack(groupStack.filter((gs) => gs.id !== group.id))
                      : setGroupStack([...groupStack, group])
                  }
                  color={isSelected ? "primary" : "default"}
                  size="small"
                  variant={isSelected ? "filled" : "outlined"}
                  sx={{
                    fontWeight: 800,
                    height: 28,
                    fontSize: '0.75rem',
                    transition: 'all 0.2s',
                    '&:hover': { transform: 'translateY(-2px)' }
                  }}
                />
              );
            })}
          </Stack>

          <Divider orientation="vertical" flexItem sx={{ height: 24, alignSelf: 'center' }} />

          {/* Sync/Refresh Action */}
          <Tooltip title={isAr ? "تحديث البيانات" : "Refresh Data"}>
            <IconButton 
              size="medium" 
              onClick={onRefresh}
              sx={{ 
                bgcolor: '#FF3366', 
                color: 'white',
                boxShadow: '0 4px 15px rgba(255, 51, 102, 0.4)',
                width: 42,
                height: 42,
                '&:hover': { 
                  bgcolor: '#E62E5C',
                  transform: 'rotate(180deg)'
                },
                transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          {/* Breadcrumb Path (Minimalist) */}
          {drillDownPath.length > 0 && (
            <>
              <Divider orientation="vertical" flexItem sx={{ height: 24, alignSelf: 'center' }} />
              <Stack direction="row" spacing={0.5} alignItems="center">
                {drillDownPath.map((p, i) => (
                  <Box key={i} sx={{ display: 'flex', alignItems: 'center' }}>
                    {i > 0 && <NavigateNextIcon sx={{ fontSize: '0.8rem', opacity: 0.5, transform: isAr ? 'rotate(180deg)' : 'none' }} />}
                    <Typography variant="caption" fontWeight={800} color="text.secondary" sx={{ bgcolor: 'rgba(0,0,0,0.04)', px: 1, py: 0.2, borderRadius: 1 }}>
                      {p.value}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            </>
          )}
        </Paper>
      </Box>
    </Portal>
  );
}
