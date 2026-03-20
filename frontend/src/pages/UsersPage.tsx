import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import PersonAddOutlinedIcon from '@mui/icons-material/PersonAddOutlined';
import { Alert, Box, Button, Chip, Dialog, DialogActions, DialogContent, DialogTitle, Grid, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';

import { SectionCard } from '../components/SectionCard';
import { useAuth } from '../features/auth/AuthProvider';
import { createUser, getMyUser, listUsers, updateMyUser, updateUser, type UserRecord } from '../features/users/api';
import { userIsAdmin } from '../lib/auth';
import { type LanguageCode } from '../lib/language';
import { queryClient } from '../lib/queryClient';
import { useCommonText } from '../text/common';
import { useNavigationText } from '../text/navigation';
import { useUsersText, userRoleLabel } from '../text/users';

function languageLabel(currentLanguage: LanguageCode, value: LanguageCode) {
  if (currentLanguage === 'ar') {
    return value === 'ar' ? 'العربية' : 'الإنجليزية';
  }
  return value === 'ar' ? 'Arabic' : 'English';
}

function UserFormFields({
  username,
  setUsername,
  fullName,
  setFullName,
  password,
  setPassword,
  role,
  setRole,
  disableUsername,
  hideRole,
  usersText,
}: {
  username: string;
  setUsername: (value: string) => void;
  fullName: string;
  setFullName: (value: string) => void;
  password: string;
  setPassword: (value: string) => void;
  role: string;
  setRole: (value: string) => void;
  disableUsername?: boolean;
  hideRole?: boolean;
  usersText: ReturnType<typeof useUsersText>;
}) {
  return (
    <Stack spacing={2}>
      {!hideRole ? (
        <TextField select SelectProps={{ native: true }} label={usersText.fields.role} value={role} onChange={(event) => setRole(event.target.value)}>
          <option value='user'>{usersText.roles.user}</option>
          <option value='admin'>{usersText.roles.admin}</option>
        </TextField>
      ) : null}
      <TextField label={usersText.fields.username} value={username} onChange={(event) => setUsername(event.target.value)} disabled={disableUsername} />
      <TextField label={usersText.fields.fullName} value={fullName} onChange={(event) => setFullName(event.target.value)} />
      <TextField
        label={hideRole ? usersText.fields.newPassword : usersText.fields.password}
        type='password'
        helperText={hideRole || disableUsername ? usersText.fields.passwordHint : undefined}
        value={password}
        onChange={(event) => setPassword(event.target.value)}
      />
    </Stack>
  );
}

export function UsersPage() {
  const { user } = useAuth();
  const commonText = useCommonText();
  const usersText = useUsersText();
  const navigationText = useNavigationText();
  const roleNames = user?.role_names ?? [];
  const isAdmin = userIsAdmin(roleNames);
  const title = isAdmin ? navigationText.usersAdmin : navigationText.usersSelf;
  const currentLanguage = user?.effective_language ?? 'ar';
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<UserRecord | null>(null);
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('user');
  const [preferredLanguage, setPreferredLanguage] = useState<LanguageCode>('ar');

  const usersQuery = useQuery({ queryKey: ['users', 'list'], queryFn: listUsers, enabled: isAdmin });
  const meQuery = useQuery({ queryKey: ['users', 'me'], queryFn: getMyUser, enabled: !isAdmin });

  const createMutation = useMutation({
    mutationFn: createUser,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['users'] });
      setDialogOpen(false);
      resetForm();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  const adminUpdateMutation = useMutation({
    mutationFn: ({ userId, payload }: { userId: string; payload: Parameters<typeof updateUser>[1] }) => updateUser(userId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['users'] });
      setDialogOpen(false);
      resetForm();
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  const selfUpdateMutation = useMutation({
    mutationFn: updateMyUser,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['users'] });
      await queryClient.invalidateQueries({ queryKey: ['auth', 'me'] });
      setPassword('');
    },
    onError: (mutationError: Error) => setError(mutationError.message),
  });

  const rows = usersQuery.data ?? [];
  const profile = meQuery.data ?? null;
  const dialogTitle = editingUser ? usersText.admin.dialogEditTitle : usersText.admin.dialogCreateTitle;

  function resetForm() {
    setEditingUser(null);
    setUsername('');
    setFullName('');
    setPassword('');
    setRole('user');
  }

  function openCreateDialog() {
    resetForm();
    setDialogOpen(true);
  }

  function openEditDialog(targetUser: UserRecord) {
    setEditingUser(targetUser);
    setUsername(targetUser.username);
    setFullName(targetUser.full_name);
    setPassword('');
    setRole(targetUser.role_names[0] ?? 'user');
    setDialogOpen(true);
  }

  async function saveAdminDialog() {
    setError(null);
    if (editingUser) {
      await adminUpdateMutation.mutateAsync({
        userId: editingUser.id,
        payload: {
          username,
          full_name: fullName,
          password: password || undefined,
          role_names: [role],
        },
      });
      return;
    }
    await createMutation.mutateAsync({ username, full_name: fullName, password, role_names: [role] });
  }

  const selfInitial = useMemo(
    () => ({
      username: profile?.username ?? user?.username ?? '',
      fullName: profile?.full_name ?? user?.full_name ?? '',
      preferredLanguage: profile?.preferred_language ?? user?.preferred_language ?? 'ar',
    }),
    [profile, user],
  );

  useEffect(() => {
    setPreferredLanguage(selfInitial.preferredLanguage);
  }, [selfInitial.preferredLanguage]);

  return (
    <Stack spacing={3}>
      <Stack direction='row' justifyContent='space-between' alignItems='center'>
        <Box>
          <Typography variant='h4'>{title}</Typography>
          <Typography color='text.secondary'>{isAdmin ? usersText.admin.description : usersText.profile.description}</Typography>
        </Box>
        {isAdmin ? (
          <Button variant='contained' startIcon={<PersonAddOutlinedIcon />} onClick={openCreateDialog}>
            {usersText.admin.dialogCreateTitle}
          </Button>
        ) : null}
      </Stack>

      {error ? <Alert severity='error'>{error}</Alert> : null}

      {isAdmin ? (
        <SectionCard title={usersText.admin.listTitle} subtitle={usersText.admin.listSubtitle}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{usersText.fields.username}</TableCell>
                <TableCell>{usersText.fields.fullName}</TableCell>
                <TableCell>{usersText.fields.role}</TableCell>
                <TableCell>{commonText.status}</TableCell>
                <TableCell>{commonText.actions}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.username}</TableCell>
                  <TableCell>{row.full_name}</TableCell>
                  <TableCell>
                    {row.role_names.map((roleName) => (
                      <Chip key={roleName} label={userRoleLabel(currentLanguage, roleName)} size='small' sx={{ ml: 1 }} />
                    ))}
                  </TableCell>
                  <TableCell>{row.is_active ? usersText.status.active : usersText.status.inactive}</TableCell>
                  <TableCell>
                    <Button startIcon={<EditOutlinedIcon />} onClick={() => openEditDialog(row)}>
                      {commonText.edit}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </SectionCard>
      ) : (
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
                <Button
                  variant='contained'
                  onClick={() =>
                    void selfUpdateMutation.mutateAsync({
                      full_name: fullName || selfInitial.fullName,
                      password: password || undefined,
                      preferred_language: preferredLanguage,
                    })
                  }
                >
                  {commonText.saveChanges}
                </Button>
              </Stack>
            </SectionCard>
          </Grid>
        </Grid>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} fullWidth maxWidth='sm'>
        <DialogTitle>{dialogTitle}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <UserFormFields
              username={username}
              setUsername={setUsername}
              fullName={fullName}
              setFullName={setFullName}
              password={password}
              setPassword={setPassword}
              role={role}
              setRole={setRole}
              usersText={usersText}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>{commonText.cancel}</Button>
          <Button variant='contained' onClick={() => void saveAdminDialog()}>
            {commonText.save}
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
