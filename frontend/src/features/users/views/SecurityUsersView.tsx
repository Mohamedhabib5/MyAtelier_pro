import PersonAddOutlinedIcon from '@mui/icons-material/PersonAddOutlined';
import { Alert, Box, Button, Stack, Typography } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';

import { useAuth } from '../../auth/AuthProvider';
import { useLanguage } from '../../language/LanguageProvider';
import { UserAdminDialog } from '../UserAdminDialog';
import { UsersAdminSection } from '../UsersAdminSection';
import { UsersProfileSection } from '../UsersProfileSection';
import { createUser, getMyUser, listUsers, updateMyUser, updateUser, type UserRecord } from '../api';
import { userIsAdmin } from '../../../lib/auth';
import { type LanguageCode } from '../../../lib/language';
import { queryClient } from '../../../lib/queryClient';
import { useCommonText } from '../../../text/common';
import { useNavigationText } from '../../../text/navigation';
import { useUsersText } from '../../../text/users';

export function SecurityUsersView() {
  const { user } = useAuth();
  const { language } = useLanguage();
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
        <UsersAdminSection rows={rows} language={language} currentLanguage={currentLanguage} usersText={usersText} commonText={commonText} onEditUser={openEditDialog} />
      ) : (
        <UsersProfileSection
          selfInitial={selfInitial}
          currentLanguage={currentLanguage}
          fullName={fullName}
          password={password}
          preferredLanguage={preferredLanguage}
          setFullName={setFullName}
          setPassword={setPassword}
          setPreferredLanguage={setPreferredLanguage}
          usersText={usersText}
          commonText={commonText}
          onSave={() =>
            void selfUpdateMutation.mutateAsync({
              full_name: fullName || selfInitial.fullName,
              password: password || undefined,
              preferred_language: preferredLanguage,
            })
          }
        />
      )}

      <UserAdminDialog
        open={dialogOpen}
        title={dialogTitle}
        username={username}
        setUsername={setUsername}
        fullName={fullName}
        setFullName={setFullName}
        password={password}
        setPassword={setPassword}
        role={role}
        setRole={setRole}
        usersText={usersText}
        commonText={commonText}
        onClose={() => setDialogOpen(false)}
        onSave={() => void saveAdminDialog()}
      />
    </Stack>
  );
}
