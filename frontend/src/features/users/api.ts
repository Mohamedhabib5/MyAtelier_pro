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

export type GridPreferenceState = {
  columnState?: Array<{
    colId: string;
    hide?: boolean | null;
    width?: number;
    pinned?: 'left' | 'right' | null;
    sort?: 'asc' | 'desc' | null;
    sortIndex?: number | null;
  }>;
  filterModel?: Record<string, unknown>;
  pageSize: number;
};

type GridPreferenceResponse = {
  table_key: string;
  state: GridPreferenceState;
  updated_at: string | null;
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

export type GridPreferenceEnvelope = {
  state: GridPreferenceState;
  updatedAt: string | null;
};

export async function getMyGridPreference(tableKey: string): Promise<GridPreferenceEnvelope> {
  const response = await apiRequest<GridPreferenceResponse>(`/api/users/me/grid-preferences/${encodeURIComponent(tableKey)}`, { method: 'GET' });
  return { state: response.state, updatedAt: response.updated_at };
}

export async function setMyGridPreference(tableKey: string, state: GridPreferenceState): Promise<GridPreferenceEnvelope> {
  const response = await apiRequest<GridPreferenceResponse>(`/api/users/me/grid-preferences/${encodeURIComponent(tableKey)}`, {
    method: 'PUT',
    body: JSON.stringify({ state }),
  });
  return { state: response.state, updatedAt: response.updated_at };
}
