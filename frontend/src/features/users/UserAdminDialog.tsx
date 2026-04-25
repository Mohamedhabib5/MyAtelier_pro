import { Box, Button } from '@mui/material';

import { AppDialogShell } from '../../components/AppDialogShell';
import { useCommonText } from '../../text/common';
import { useUsersText } from '../../text/users';
import { UserFormFields } from './UserFormFields';

type Props = {
  open: boolean;
  title: string;
  username: string;
  setUsername: (value: string) => void;
  fullName: string;
  setFullName: (value: string) => void;
  password: string;
  setPassword: (value: string) => void;
  role: string;
  setRole: (value: string) => void;
  usersText: ReturnType<typeof useUsersText>;
  commonText: ReturnType<typeof useCommonText>;
  onClose: () => void;
  onSave: () => void;
};

export function UserAdminDialog({
  open,
  title,
  username,
  setUsername,
  fullName,
  setFullName,
  password,
  setPassword,
  role,
  setRole,
  usersText,
  commonText,
  onClose,
  onSave,
}: Props) {
  return (
    <AppDialogShell
      open={open}
      onClose={onClose}
      title={title}
      actions={
        <>
          <Button onClick={onClose}>{commonText.cancel}</Button>
          <Button variant='contained' onClick={onSave}>
            {commonText.save}
          </Button>
        </>
      }
    >
      <Box>
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
    </AppDialogShell>
  );
}
