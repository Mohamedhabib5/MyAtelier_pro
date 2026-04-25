import { apiRequest } from '../../lib/api';

export type DepartmentRecord = {
  id: string;
  company_id: string;
  code: string;
  name: string;
  is_active: boolean;
};

export type ServiceRecord = {
  id: string;
  company_id: string;
  department_id: string;
  department_name: string;
  name: string;
  default_price: number;
  duration_minutes: number | null;
  notes: string | null;
  is_active: boolean;
};

export type DepartmentPayload = {
  code: string;
  name: string;
};

export type DepartmentUpdatePayload = DepartmentPayload & {
  is_active: boolean;
};

export type ServicePayload = {
  department_id: string;
  name: string;
  default_price: number;
  duration_minutes?: number | null;
  notes?: string | null;
};

export type ServiceUpdatePayload = ServicePayload & {
  is_active: boolean;
};

export type RecordStatusFilter = 'all' | 'active' | 'inactive';

function resolveStatus(status: unknown): RecordStatusFilter {
  return status === 'active' || status === 'inactive' || status === 'all' ? status : 'all';
}

export function listDepartments(status: RecordStatusFilter | unknown = 'all'): Promise<DepartmentRecord[]> {
  const resolved = resolveStatus(status);
  return apiRequest<DepartmentRecord[]>(`/api/catalog/departments?status=${resolved}`, { method: 'GET' });
}

export function createDepartment(payload: DepartmentPayload): Promise<DepartmentRecord> {
  return apiRequest<DepartmentRecord>('/api/catalog/departments', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateDepartment(departmentId: string, payload: DepartmentUpdatePayload): Promise<DepartmentRecord> {
  return apiRequest<DepartmentRecord>(`/api/catalog/departments/${departmentId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function archiveDepartment(departmentId: string, reason?: string): Promise<DepartmentRecord> {
  return apiRequest<DepartmentRecord>(`/api/catalog/departments/${departmentId}/archive`, {
    method: 'POST',
    body: JSON.stringify({ reason: reason ?? null }),
  });
}

export function restoreDepartment(departmentId: string, reason?: string): Promise<DepartmentRecord> {
  return apiRequest<DepartmentRecord>(`/api/catalog/departments/${departmentId}/restore`, {
    method: 'POST',
    body: JSON.stringify({ reason: reason ?? null }),
  });
}

export function listServices(status: RecordStatusFilter | unknown = 'all'): Promise<ServiceRecord[]> {
  const resolved = resolveStatus(status);
  return apiRequest<ServiceRecord[]>(`/api/catalog/services?status=${resolved}`, { method: 'GET' });
}

export function createService(payload: ServicePayload): Promise<ServiceRecord> {
  return apiRequest<ServiceRecord>('/api/catalog/services', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateService(serviceId: string, payload: ServiceUpdatePayload): Promise<ServiceRecord> {
  return apiRequest<ServiceRecord>(`/api/catalog/services/${serviceId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function archiveService(serviceId: string, reason?: string): Promise<ServiceRecord> {
  return apiRequest<ServiceRecord>(`/api/catalog/services/${serviceId}/archive`, {
    method: 'POST',
    body: JSON.stringify({ reason: reason ?? null }),
  });
}

export function restoreService(serviceId: string, reason?: string): Promise<ServiceRecord> {
  return apiRequest<ServiceRecord>(`/api/catalog/services/${serviceId}/restore`, {
    method: 'POST',
    body: JSON.stringify({ reason: reason ?? null }),
  });
}
