import TranslateOutlinedIcon from '@mui/icons-material/TranslateOutlined';
import { CircularProgress, FormControl, InputLabel, MenuItem, Select, Stack } from '@mui/material';
import type { SelectChangeEvent } from '@mui/material/Select';
import { useState } from 'react';

import { type LanguageCode } from '../../lib/language';
import { useLanguage } from './LanguageProvider';

export function LanguageSwitcher({ authenticated = false }: { authenticated?: boolean }) {
  const { language, setGuestLanguage, setSessionLanguage } = useLanguage();
  const [submitting, setSubmitting] = useState(false);
  const label = language === 'ar' ? 'اللغة' : 'Language';
  const testId = authenticated ? 'language-switcher-auth' : 'language-switcher-guest';

  async function selectLanguage(nextLanguage: LanguageCode) {
    if (nextLanguage === language || submitting) {
      return;
    }
    if (!authenticated) {
      setGuestLanguage(nextLanguage);
      return;
    }
    setSubmitting(true);
    try {
      await setSessionLanguage(nextLanguage);
    } finally {
      setSubmitting(false);
    }
  }

  function handleChange(event: SelectChangeEvent<LanguageCode>) {
    void selectLanguage(event.target.value as LanguageCode);
  }

  return (
    <Stack direction='row' spacing={1} alignItems='center' aria-label='language switcher' sx={{ flexShrink: 0, minWidth: 150 }}>
      {submitting ? <CircularProgress size={18} color='inherit' /> : <TranslateOutlinedIcon fontSize='small' />}
      <FormControl size='small' variant='outlined' sx={{ minWidth: 120 }}>
        <InputLabel id='language-switcher-label' sx={{ color: 'inherit' }}>
          {label}
        </InputLabel>
        <Select
          data-testid={testId}
          labelId='language-switcher-label'
          value={language}
          label={label}
          onChange={handleChange}
          disabled={submitting}
          sx={{
            color: 'inherit',
            '.MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.45)' },
            '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.7)' },
            '.MuiSvgIcon-root': { color: 'inherit' },
          }}
        >
          <MenuItem value='ar'>العربية</MenuItem>
          <MenuItem value='en'>English</MenuItem>
        </Select>
      </FormControl>
    </Stack>
  );
}
