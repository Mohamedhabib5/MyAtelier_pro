import { apiRequest } from '../../lib/api';

export type BranchRecord = {
  id: string;
  code: string;
  name: string;
  is_default: boolean;
  is_active: boolean;
};

export type CompanyRecord = {
  id: string;
  name: string;
  legal_name: string | null;
  default_currency: string;
  is_active: boolean;
  branches: BranchRecord[];
};

export type BackupRecord = {
  id: string;
  filename: string;
  status: string;
  size_bytes: number;
  notes: string | null;
  created_at: string;
};

export type ActiveBranchRecord = {
  id: string;
  code: string;
  name: string;
  is_default: boolean;
  is_active: boolean;
};

export type UpdateCompanyPayload = {
  name: string;
  legal_name?: string | null;
  default_currency: string;
};

export type CreateBranchPayload = {
  code: string;
  name: string;
};

export type SetActiveBranchPayload = {
  branch_id: string;
};

export function getCompany(): Promise<CompanyRecord> {
  return apiRequest<CompanyRecord>('/api/settings/company', { method: 'GET' });
}

export function updateCompany(payload: UpdateCompanyPayload): Promise<CompanyRecord> {
  return apiRequest<CompanyRecord>('/api/settings/company', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function createBranch(payload: CreateBranchPayload): Promise<BranchRecord> {
  return apiRequest<BranchRecord>('/api/settings/branches', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getActiveBranch(): Promise<ActiveBranchRecord> {
  return apiRequest<ActiveBranchRecord>('/api/settings/branches/active', { method: 'GET' });
}

export function setActiveBranch(payload: SetActiveBranchPayload): Promise<ActiveBranchRecord> {
  return apiRequest<ActiveBranchRecord>('/api/settings/branches/active', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listBackups(): Promise<BackupRecord[]> {
  return apiRequest<BackupRecord[]>('/api/settings/backups', { method: 'GET' });
}

export function createBackup(): Promise<BackupRecord> {
  return apiRequest<BackupRecord>('/api/settings/backups', { method: 'POST' });
}

export function getBackupDownloadUrl(backupId: string): string {
  return `/api/settings/backups/${backupId}/download`;
}
