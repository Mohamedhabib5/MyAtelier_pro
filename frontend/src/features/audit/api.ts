import { apiRequest } from '../../lib/api';

export type AuditEventRecord = {
  id: string;
  occurred_at: string;
  actor_user_id: string | null;
  actor_name: string | null;
  action: string;
  target_type: string;
  target_id: string | null;
  branch_id: string | null;
  summary: string;
  reason_code: string | null;
  reason_text: string | null;
  success: boolean | null;
  error_code: string | null;
  diff: Record<string, unknown>;
};

export type AuditEventPageResponse = {
  items: AuditEventRecord[];
  total: number;
  page: number;
  page_size: number;
};

export type AuditEventQuery = {
  actorUserId?: string;
  action?: string;
  targetType?: string;
  targetId?: string;
  branchId?: string;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
  page?: number;
  pageSize?: number;
};

export function listAuditEvents(query: AuditEventQuery): Promise<AuditEventPageResponse> {
  const params = new URLSearchParams();
  if (query.actorUserId) params.set('actor_user_id', query.actorUserId);
  if (query.action) params.set('action', query.action);
  if (query.targetType) params.set('target_type', query.targetType);
  if (query.targetId) params.set('target_id', query.targetId);
  if (query.branchId) params.set('branch_id', query.branchId);
  if (query.dateFrom) params.set('date_from', query.dateFrom);
  if (query.dateTo) params.set('date_to', query.dateTo);
  if (query.search) params.set('search', query.search);
  params.set('page', String(query.page ?? 1));
  params.set('page_size', String(query.pageSize ?? 25));
  return apiRequest<AuditEventPageResponse>(`/api/audit/events?${params.toString()}`, { method: 'GET' });
}

export function listDestructiveActions(query: AuditEventQuery): Promise<AuditEventPageResponse> {
  const params = new URLSearchParams();
  if (query.actorUserId) params.set('actor_user_id', query.actorUserId);
  if (query.targetType) params.set('target_type', query.targetType);
  if (query.targetId) params.set('target_id', query.targetId);
  if (query.branchId) params.set('branch_id', query.branchId);
  if (query.dateFrom) params.set('date_from', query.dateFrom);
  if (query.dateTo) params.set('date_to', query.dateTo);
  if (query.search) params.set('search', query.search);
  params.set('page', String(query.page ?? 1));
  params.set('page_size', String(query.pageSize ?? 25));
  return apiRequest<AuditEventPageResponse>(`/api/audit/destructive-actions?${params.toString()}`, { method: 'GET' });
}

export function listNightlyOpsEvents(query: AuditEventQuery): Promise<AuditEventPageResponse> {
  const params = new URLSearchParams();
  if (query.actorUserId) params.set('actor_user_id', query.actorUserId);
  if (query.targetType) params.set('target_type', query.targetType);
  if (query.targetId) params.set('target_id', query.targetId);
  if (query.branchId) params.set('branch_id', query.branchId);
  if (query.dateFrom) params.set('date_from', query.dateFrom);
  if (query.dateTo) params.set('date_to', query.dateTo);
  if (query.search) params.set('search', query.search);
  params.set('page', String(query.page ?? 1));
  params.set('page_size', String(query.pageSize ?? 25));
  return apiRequest<AuditEventPageResponse>(`/api/audit/nightly-ops?${params.toString()}`, { method: 'GET' });
}

export function buildNightlyOpsCsvUrl(query: AuditEventQuery, limit = 1000, exportReason?: string): string {
  const params = new URLSearchParams();
  if (query.actorUserId) params.set('actor_user_id', query.actorUserId);
  if (query.targetType) params.set('target_type', query.targetType);
  if (query.targetId) params.set('target_id', query.targetId);
  if (query.branchId) params.set('branch_id', query.branchId);
  if (query.dateFrom) params.set('date_from', query.dateFrom);
  if (query.dateTo) params.set('date_to', query.dateTo);
  if (query.search) params.set('search', query.search);
  if (exportReason) params.set('export_reason', exportReason);
  params.set('limit', String(limit));
  return `/api/audit/nightly-ops.csv?${params.toString()}`;
}
