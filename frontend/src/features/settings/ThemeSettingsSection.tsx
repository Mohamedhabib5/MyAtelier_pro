import { Button, Stack, TextField, Typography, Box, Divider } from '@mui/material';
import { SectionCard } from '../../components/SectionCard';
import { useSettingsText } from '../../text/settings';
import { useThemeSettings } from '../theme/ThemeSettingsProvider';

export function ThemeSettingsSection() {
  const settingsText = useSettingsText();
  const { 
    primaryColor, secondaryColor, sidebarColor, sidebarColorEnd, headerColor, headerColorEnd, sidebarTextColor,
    bgGradientStart, bgGradientEnd, accentColor,
    setPrimaryColor, setSecondaryColor, setSidebarColor, setSidebarColorEnd, setHeaderColor, setHeaderColorEnd, setSidebarTextColor, 
    setBgGradientStart, setBgGradientEnd, setAccentColor,
    resetTheme 
  } = useThemeSettings();

  const ColorInput = ({ label, value, onChange }: { label: string, value: string, onChange: (v: string) => void }) => (
    <Box flex={1}>
      <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
        {label}
      </Typography>
      <Stack direction="row" spacing={2} alignItems="center">
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          style={{ 
            width: 54, 
            height: 40, 
            border: 'none', 
            borderRadius: 12, 
            cursor: 'pointer',
            padding: 0,
            boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
          }}
        />
        <TextField 
          size="small" 
          value={value} 
          onChange={(e) => onChange(e.target.value)}
          sx={{ 
            width: 120, 
            '& .MuiInputBase-root': { borderRadius: 3, bgcolor: 'rgba(0,0,0,0.02)' },
            '& .MuiInputBase-input': { fontSize: '0.85rem', py: 1 } 
          }}
        />
      </Stack>
    </Box>
  );

  return (
    <SectionCard 
      title={settingsText.appearance.title} 
      subtitle={settingsText.appearance.subtitle}
    >
      <Stack spacing={5}>
        <Stack spacing={3}>
          <Typography variant="overline" color="primary" sx={{ fontWeight: 800, letterSpacing: 1.5 }}>
            Background Gradient
          </Typography>
          <Stack direction="row" spacing={4}>
            <ColorInput label="Gradient Start" value={bgGradientStart} onChange={setBgGradientStart} />
            <ColorInput label="Gradient End" value={bgGradientEnd} onChange={setBgGradientEnd} />
          </Stack>
        </Stack>

        <Divider />

        <Stack spacing={3}>
          <Typography variant="overline" color="primary" sx={{ fontWeight: 800, letterSpacing: 1.5 }}>
            Theme Accents
          </Typography>
          <Stack direction="row" spacing={4}>
            <ColorInput label="Neon Accent (Highlights)" value={accentColor} onChange={setAccentColor} />
            <ColorInput label="Primary Action Color" value={primaryColor} onChange={setPrimaryColor} />
          </Stack>
        </Stack>

        <Divider />

        <Stack spacing={3}>
          <Typography variant="overline" color="primary" sx={{ fontWeight: 800, letterSpacing: 1.5 }}>
            Layout Elements
          </Typography>
          <Stack spacing={4}>
            <Stack direction="row" spacing={4}>
              <ColorInput label={settingsText.appearance.sidebarColor} value={sidebarColor} onChange={setSidebarColor} />
              <ColorInput label={settingsText.appearance.sidebarColorEnd} value={sidebarColorEnd} onChange={setSidebarColorEnd} />
            </Stack>
            <Stack direction="row" spacing={4}>
              <ColorInput label={settingsText.appearance.headerColor} value={headerColor} onChange={setHeaderColor} />
              <ColorInput label={settingsText.appearance.headerColorEnd} value={headerColorEnd} onChange={setHeaderColorEnd} />
            </Stack>
            <Stack direction="row" spacing={4}>
              <ColorInput label={settingsText.appearance.textColor} value={sidebarTextColor} onChange={setSidebarTextColor} />
              <Box flex={1} />
            </Stack>
          </Stack>
        </Stack>

        <Box sx={{ pt: 2 }}>
          <Button 
            variant="contained" 
            disableElevation
            onClick={resetTheme} 
            sx={{ 
              borderRadius: 50, 
              px: 4, 
              py: 1.5,
              bgcolor: 'rgba(0,0,0,0.05)',
              color: 'text.primary',
              '&:hover': { bgcolor: 'rgba(0,0,0,0.1)' }
            }}
          >
            {settingsText.appearance.reset}
          </Button>
        </Box>
      </Stack>
    </SectionCard>
  );
}
