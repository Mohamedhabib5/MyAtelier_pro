import { ApiError, apiRequest } from '../../lib/api';
import type { LanguageCode } from '../../lib/language';

export type CurrentUser = {
  id: string;
  username: string;
  full_name: string;
  is_active: boolean;
  role_names: string[];
  active_branch_id: string;
  active_branch_name: string;
  preferred_language: LanguageCode;
  session_language: LanguageCode;
  effective_language: LanguageCode;
};

export type LoginPayload = {
  username: string;
  password: string;
  language?: LanguageCode;
};

export type SessionLanguagePayload = {
  language: LanguageCode;
};

export async function fetchCurrentUser(): Promise<CurrentUser | null> {
  try {
    return await apiRequest<CurrentUser>('/api/auth/me', { method: 'GET' });
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return null;
    }
    throw error;
  }
}

export function login(payload: LoginPayload): Promise<CurrentUser> {
  return apiRequest<CurrentUser>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function logout(): Promise<void> {
  return apiRequest<void>('/api/auth/logout', { method: 'POST' });
}

export function setSessionLanguage(payload: SessionLanguagePayload): Promise<CurrentUser> {
  return apiRequest<CurrentUser>('/api/auth/language', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
