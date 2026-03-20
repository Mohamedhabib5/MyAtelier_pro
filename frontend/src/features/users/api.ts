import { apiRequest } from '../../lib/api';
import type { LanguageCode } from '../../lib/language';

export type UserRecord = {
  id: string;
  username: string;
  full_name: string;
  is_active: boolean;
  last_login_at: string | null;
  role_names: string[];
  preferred_language: LanguageCode;
};

export type CreateUserPayload = {
  username: string;
  full_name: string;
  password: string;
  role_names: string[];
};

export type AdminUpdateUserPayload = Partial<CreateUserPayload> & {
  is_active?: boolean;
};

export type SelfUpdateUserPayload = {
  full_name?: string;
  password?: string;
  preferred_language?: LanguageCode;
};

export function listUsers(): Promise<UserRecord[]> {
  return apiRequest<UserRecord[]>('/api/users', { method: 'GET' });
}

export function getMyUser(): Promise<UserRecord> {
  return apiRequest<UserRecord>('/api/users/me', { method: 'GET' });
}

export function createUser(payload: CreateUserPayload): Promise<UserRecord> {
  return apiRequest<UserRecord>('/api/users', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateUser(userId: string, payload: AdminUpdateUserPayload): Promise<UserRecord> {
  return apiRequest<UserRecord>(`/api/users/${userId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function updateMyUser(payload: SelfUpdateUserPayload): Promise<UserRecord> {
  return apiRequest<UserRecord>('/api/users/me', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}
