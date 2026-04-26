import { apiRequest } from '../../lib/api';

export type DressRecord = {
  id: string;
  company_id: string;
  code: string;
  dress_type: string;
  purchase_date: string | null;
  status: string;
  description: string | null;
  image_path: string | null;
  is_active: boolean;
};

export type DressPayload = {
  code: string;
  dress_type: string;
  purchase_date?: string | null;
  status: string;
  description?: string | null;
  image_path?: string | null;
};

export type DressUpdatePayload = DressPayload & {
  is_active: boolean;
};

export type RecordStatusFilter = 'all' | 'active' | 'inactive';

function resolveStatus(status: unknown): RecordStatusFilter {
  return status === 'active' || status === 'inactive' || status === 'all' ? status : 'all';
}

export function listDresses(status: RecordStatusFilter | unknown = 'all'): Promise<DressRecord[]> {
  const resolved = resolveStatus(status);
  return apiRequest<DressRecord[]>(`/api/dresses?status=${resolved}`, { method: 'GET' });
}

export function createDress(payload: DressPayload): Promise<DressRecord> {
  return apiRequest<DressRecord>('/api/dresses', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateDress(dressId: string, payload: DressUpdatePayload): Promise<DressRecord> {
  return apiRequest<DressRecord>(`/api/dresses/${dressId}`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function archiveDress(dressId: string, reason?: string): Promise<DressRecord> {
  return apiRequest<DressRecord>(`/api/dresses/${dressId}/archive`, {
    method: 'POST',
    body: JSON.stringify({ reason: reason ?? null }),
  });
}

export function restoreDress(dressId: string, reason?: string): Promise<DressRecord> {
  return apiRequest<DressRecord>(`/api/dresses/${dressId}/restore`, {
    method: 'POST',
    body: JSON.stringify({ reason: reason ?? null }),
  });
}

export function uploadDressImage(file: File): Promise<{ image_path: string }> {
  const formData = new FormData();
  formData.append('file', file);
  return apiRequest<{ image_path: string }>('/api/dresses/upload', {
    method: 'POST',
    body: formData,
  });
}
