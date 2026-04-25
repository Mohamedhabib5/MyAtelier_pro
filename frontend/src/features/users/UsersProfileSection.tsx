import { Button, Grid, Stack, TextField } from '@mui/material';

import { SectionCard } from '../../components/SectionCard';
import { type LanguageCode } from '../../lib/language';
import { useCommonText } from '../../text/common';
import { useUsersText } from '../../text/users';

type SelfInitialState = {
  username: string;
  fullName: string;
  preferredLanguage: LanguageCode;
};

type Props = {
  selfInitial: SelfInitialState;
  currentLanguage: LanguageCode;
  fullName: string;
  password: string;
  preferredLanguage: LanguageCode;
  setFullName: (value: string) => void;
  setPassword: (value: string) => void;
  setPreferredLanguage: (value: LanguageCode) => void;
  usersText: ReturnType<typeof useUsersText>;
  commonText: ReturnType<typeof useCommonText>;
  onSave: () => void;
};

function languageLabel(currentLanguage: LanguageCode, value: LanguageCode) {
  if (currentLanguage === 'ar') {
    return value === 'ar' ? 'ط§ظ„ط¹ط±ط¨ظٹط©' : 'ط§ظ„ط¥ظ†ط¬ظ„ظٹط²ظٹط©';
  }
  return value === 'ar' ? 'Arabic' : 'English';
}

export function UsersProfileSection({
  selfInitial,
  currentLanguage,
  fullName,
  password,
  preferredLanguage,
  setFullName,
  setPassword,
  setPreferredLanguage,
  usersText,
  commonText,
  onSave,
}: Props) {
  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 7 }}>
        <SectionCard title={usersText.profile.title} subtitle={usersText.profile.subtitle}>
          <Stack spacing={2}>
            <TextField label={usersText.fields.username} value={selfInitial.username} disabled />
            <TextField label={usersText.fields.fullName} value={fullName || selfInitial.fullName} onChange={(event) => setFullName(event.target.value)} />
            <TextField
              select
              SelectProps={{ native: true }}
              label={usersText.fields.preferredLanguage}
              value={preferredLanguage}
              onChange={(event) => setPreferredLanguage(event.target.value as LanguageCode)}
            >
              <option value='ar'>{languageLabel(currentLanguage, 'ar')}</option>
              <option value='en'>{languageLabel(currentLanguage, 'en')}</option>
            </TextField>
            <TextField
              label={usersText.fields.newPassword}
              type='password'
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              helperText={usersText.fields.passwordHint}
            />
            <Button variant='contained' onClick={onSave}>
              {commonText.saveChanges}
            </Button>
          </Stack>
        </SectionCard>
      </Grid>
    </Grid>
  );
}
