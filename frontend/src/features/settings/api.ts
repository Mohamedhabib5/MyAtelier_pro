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

export type DestructiveReasonRecord = {
  code: string;
  category: string;
  label_ar: string;
  label_en: string;
  actions: string[];
};

export type DestructivePreviewPayload = {
  entity_type: string;
  entity_id: string;
  reason_code?: string | null;
  reason_text?: string | null;
};

export type PeriodLockOverridePayload = {
  override_lock?: boolean;
  override_reason?: string | null;
};

export type DestructivePreviewRecord = {
  entity_type: string;
  entity_id: string;
  entity_label: string;
  recommended_action: string;
  eligible_for_hard_delete: boolean;
  blockers: string[];
  impact: Record<string, number>;
  reason_code: string;
  reason_text: string | null;
};

export type DestructiveDeletePayload = DestructivePreviewPayload & PeriodLockOverridePayload;

export type DestructiveDeleteRecord = {
  entity_type: string;
  entity_id: string;
  entity_label: string;
  deleted: boolean;
  reason_code: string;
  reason_text: string | null;
  impact: Record<string, number>;
};

export type PeriodLockRecord = {
  locked_through: string | null;
  updated_by_user_id: string | null;
  updated_at: string | null;
  is_locked: boolean;
};

export type PeriodLockUpdatePayload = {
  locked_through: string | null;
  note?: string | null;
};

export type PeriodLockExceptionRecord = {
  audit_id: string;
  occurred_at: string;
  actor_user_id: string | null;
  actor_name: string | null;
  target_type: string;
  target_id: string | null;
  action_key: string | null;
  action_date: string | null;
  locked_through: string | null;
  override_reason: string | null;
};

export type CompensationTypeRecord = {
  id: string;
  name: string;
  default_price: number;
  duration_minutes: number | null;
  notes: string | null;
  display_order: number;
  is_active: boolean;
};

export type CompensationTypePayload = {
  name: string;
  default_price: number;
  duration_minutes?: number | null;
  notes?: string | null;
  display_order: number;
};

export type NightlyRunSnapshotRecord = {
  available: boolean;
  event: string | null;
  repository: string | null;
  ref: string | null;
  run_id: string | null;
  run_attempt: string | null;
  run_url: string | null;
  failed_at_utc: string | null;
  results: Record<string, string>;
  reported_at: string | null;
};

export type FiscalPeriodRecord = {
  id: string;
  name: string;
  starts_on: string;
  ends_on: string;
  is_active: boolean;
  is_locked: boolean;
};

export type FiscalPeriodCreatePayload = {
  name: string;
  starts_on: string;
  ends_on: string;
};

export type FiscalPeriodUpdatePayload = {
  name?: string;
  is_active?: boolean;
  is_locked?: boolean;
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

export function listDestructiveReasons(action = 'hard_delete'): Promise<DestructiveReasonRecord[]> {
  return apiRequest<DestructiveReasonRecord[]>(`/api/settings/destructive-reasons?action=${action}`, { method: 'GET' });
}

export function previewDestructiveDelete(payload: DestructivePreviewPayload): Promise<DestructivePreviewRecord> {
  return apiRequest<DestructivePreviewRecord>('/api/settings/destructive-preview', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function executeDestructiveDelete(payload: DestructiveDeletePayload): Promise<DestructiveDeleteRecord> {
  return apiRequest<DestructiveDeleteRecord>('/api/settings/destructive-delete', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getPeriodLock(): Promise<PeriodLockRecord> {
  return apiRequest<PeriodLockRecord>('/api/settings/period-lock', { method: 'GET' });
}

export function updatePeriodLock(payload: PeriodLockUpdatePayload): Promise<PeriodLockRecord> {
  return apiRequest<PeriodLockRecord>('/api/settings/period-lock', {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export function listPeriodLockExceptions(limit = 100): Promise<PeriodLockExceptionRecord[]> {
  return apiRequest<PeriodLockExceptionRecord[]>(`/api/settings/period-lock/exceptions?limit=${limit}`, { method: 'GET' });
}

export function listCompensationTypes(): Promise<CompensationTypeRecord[]> {
  return apiRequest<CompensationTypeRecord[]>('/api/settings/compensation-types', { method: 'GET' });
}

export function createCompensationType(payload: CompensationTypePayload): Promise<CompensationTypeRecord> {
  return apiRequest<CompensationTypeRecord>('/api/settings/compensation-types', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateCompensationType(id: string, payload: CompensationTypePayload): Promise<CompensationTypeRecord> {
  return apiRequest<CompensationTypeRecord>(`/api/settings/compensation-types/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function getLatestNightlySnapshot(): Promise<NightlyRunSnapshotRecord> {
  return apiRequest<NightlyRunSnapshotRecord>('/api/settings/ops/nightly/latest', { method: 'GET' });
}

export function listFiscalPeriods(): Promise<FiscalPeriodRecord[]> {
  return apiRequest<FiscalPeriodRecord[]>('/api/settings/fiscal-periods', { method: 'GET' });
}

export function createFiscalPeriod(payload: FiscalPeriodCreatePayload): Promise<FiscalPeriodRecord> {
  return apiRequest<FiscalPeriodRecord>('/api/settings/fiscal-periods', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateFiscalPeriod(periodId: string, payload: FiscalPeriodUpdatePayload): Promise<FiscalPeriodRecord> {
  return apiRequest<FiscalPeriodRecord>(`/api/settings/fiscal-periods/${periodId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function deleteFiscalPeriod(periodId: string): Promise<void> {
  return apiRequest<void>(`/api/settings/fiscal-periods/${periodId}`, { method: 'DELETE' });
}
