import { apiRequest } from '../../lib/api';

export type Permission = {
  key: string;
  description: string;
};

export type Role = {
  id: string;
  name: string;
  description: string | null;
  is_preset: boolean;
  permissions: Permission[];
};

export type CreateRolePayload = {
  name: string;
  description?: string;
  permission_keys: string[];
};

export type UpdateRolePayload = Partial<CreateRolePayload>;

export function fetchRoles(): Promise<Role[]> {
  return apiRequest<Role[]>('/api/roles', { method: 'GET' });
}

export function fetchPermissions(): Promise<Permission[]> {
  return apiRequest<Permission[]>('/api/roles/permissions', { method: 'GET' });
}

export function createRole(payload: CreateRolePayload): Promise<Role> {
  return apiRequest<Role>('/api/roles', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateRole(roleId: string, payload: UpdateRolePayload): Promise<Role> {
  return apiRequest<Role>(`/api/roles/${roleId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function deleteRole(roleId: string): Promise<void> {
  return apiRequest<void>(`/api/roles/${roleId}`, { method: 'DELETE' });
}

export function cloneRole(roleId: string, newName: string): Promise<Role> {
  const params = new URLSearchParams({ new_name: newName });
  return apiRequest<Role>(`/api/roles/${roleId}/clone?${params.toString()}`, { method: 'POST' });
}
