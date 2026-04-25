import { Stack, TextField } from '@mui/material';

import { useUsersText } from '../../text/users';

type Props = {
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
};

export function UserFormFields({
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
}: Props) {
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
