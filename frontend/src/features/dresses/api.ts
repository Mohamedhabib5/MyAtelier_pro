import { apiRequest } from '../../lib/api';

export type DressRecord = {
  id: string;
  company_id: string;
  code: string;
  dress_type: string;
  purchase_date: string | null;
  status: string;
  description: string;
  image_path: string | null;
  is_active: boolean;
};

export type DressPayload = {
  code: string;
  dress_type: string;
  purchase_date?: string | null;
  status: string;
  description: string;
  image_path?: string | null;
};

export type DressUpdatePayload = DressPayload & {
  is_active: boolean;
};

export function listDresses(): Promise<DressRecord[]> {
  return apiRequest<DressRecord[]>('/api/dresses', { method: 'GET' });
}

export function createDress(payload: DressPayload): Promise<DressRecord> {
  return apiRequest<DressRecord>('/api/dresses', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateDress(dressId: string, payload: DressUpdatePayload): Promise<DressRecord> {
  return apiRequest<DressRecord>(`/api/dresses/${dressId}`, { method: 'PATCH', body: JSON.stringify(payload) });
}
