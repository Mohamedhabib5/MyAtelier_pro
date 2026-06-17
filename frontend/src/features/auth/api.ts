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
  is_2fa_enabled: boolean;
  is_2fa_required?: boolean;
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

// 2FA APIs

export type TwoFASetupResponse = {
  provisioning_uri: string;
};

export type TwoFAActivationResponse = {
  backup_codes: string[];
};

export function setup2FA(): Promise<TwoFASetupResponse> {
  return apiRequest<TwoFASetupResponse>('/api/auth/2fa/setup', { method: 'POST' });
}

export function activate2FA(code: string): Promise<TwoFAActivationResponse> {
  return apiRequest<TwoFAActivationResponse>('/api/auth/2fa/activate', {
    method: 'POST',
    body: JSON.stringify({ code }),
  });
}

export function verify2FA(code: string): Promise<CurrentUser> {
  return apiRequest<CurrentUser>('/api/auth/2fa/verify', {
    method: 'POST',
    body: JSON.stringify({ code }),
  });
}

export function verifyBackup2FA(code: string): Promise<CurrentUser> {
  return apiRequest<CurrentUser>('/api/auth/2fa/verify-backup', {
    method: 'POST',
    body: JSON.stringify({ code }),
  });
}
