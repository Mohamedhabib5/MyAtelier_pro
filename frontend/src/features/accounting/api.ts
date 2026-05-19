import { apiRequest } from "../../lib/api";

export type ChartAccountRecord = {
  id: string;
  company_id: string;
  code: string;
  name: string;
  account_type: string;
  parent_account_id: string | null;
  allows_posting: boolean;
  is_active: boolean;
};

export type JournalEntryLineRecord = {
  id: string;
  line_number: number;
  account_id: string;
  account_code: string;
  account_name: string;
  description: string | null;
  debit_amount: string;
  credit_amount: string;
};

export type JournalEntryRecord = {
  id: string;
  company_id: string;
  fiscal_period_id: string;
  entry_number: string;
  entry_date: string;
  status: string;
  reference: string | null;
  notes: string | null;
  posted_at: string | null;
  posted_by_user_id: string | null;
  reversed_at: string | null;
  reversed_by_user_id: string | null;
  total_debit: string;
  total_credit: string;
  lines: JournalEntryLineRecord[];
};

export type TrialBalanceRowRecord = {
  account_id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  movement_debit: string;
  movement_credit: string;
  balance_debit: string;
  balance_credit: string;
};

export type TrialBalanceRecord = {
  as_of_date: string | null;
  fiscal_period_id: string | null;
  included_statuses: string[];
  rows: TrialBalanceRowRecord[];
  summary: {
    movement_debit_total: string;
    movement_credit_total: string;
    balance_debit_total: string;
    balance_credit_total: string;
    entry_count: number;
  };
};

export type IncomeStatementItem = {
  account_id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  parent_account_id: string | null;
  level: number;
  debit: string;
  credit: string;
  balance: string;
};

export type IncomeStatementSection = {
  items: IncomeStatementItem[];
  total: string;
};

export type IncomeStatementRecord = {
  as_of_date: string | null;
  branch_id: string | null;
  revenues: IncomeStatementSection;
  expenses: IncomeStatementSection;
  net_income: string;
};

export type AgingReportRow = {
  party_id: string;
  party_name: string;
  party_type: string;
  total_outstanding: string;
  buckets: {
    "current": string;
    "31-60": string;
    "61-90": string;
    "91+": string;
  };
};

export type AgingReportRecord = {
  as_of_date: string;
  party_type: string;
  rows: AgingReportRow[];
  total_receivable_or_payable: string;
};

export function getChartOfAccounts(): Promise<ChartAccountRecord[]> {
  return apiRequest<ChartAccountRecord[]>("/api/accounting/chart-of-accounts", { method: "GET" });
}

export function getJournalEntries(): Promise<JournalEntryRecord[]> {
  return apiRequest<JournalEntryRecord[]>("/api/accounting/journal-entries", { method: "GET" });
}

export function getTrialBalance(params?: {
  asOfDate?: string;
  fiscalPeriodId?: string;
  branchId?: string;
  includeZeroAccounts?: boolean;
}): Promise<TrialBalanceRecord> {
  const search = new URLSearchParams();
  if (params?.asOfDate) search.set("as_of_date", params.asOfDate);
  if (params?.fiscalPeriodId) search.set("fiscal_period_id", params.fiscalPeriodId);
  if (params?.branchId) search.set("branch_id", params.branchId);
  if (params?.includeZeroAccounts) search.set("include_zero_accounts", "true");
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return apiRequest<TrialBalanceRecord>(`/api/accounting/trial-balance${suffix}`, { method: "GET" });
}

export function getIncomeStatement(params?: {
  asOfDate?: string;
  branchId?: string;
}): Promise<IncomeStatementRecord> {
  const search = new URLSearchParams();
  if (params?.asOfDate) search.set("as_of_date", params.asOfDate);
  if (params?.branchId) search.set("branch_id", params.branchId);
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return apiRequest<IncomeStatementRecord>(`/api/accounting/income-statement${suffix}`, { method: "GET" });
}

export function getAgingReport(params: {
  partyType: "customer" | "supplier";
  asOfDate?: string;
}): Promise<AgingReportRecord> {
  const search = new URLSearchParams();
  search.set("party_type", params.partyType);
  if (params.asOfDate) search.set("as_of_date", params.asOfDate);
  return apiRequest<AgingReportRecord>(`/api/accounting/aging?${search.toString()}`, { method: "GET" });
}

export function getTrialBalanceExcelUrl(params?: {
  asOfDate?: string;
  fiscalPeriodId?: string;
  branchId?: string;
  includeZeroAccounts?: boolean;
}): string {
  const search = new URLSearchParams();
  if (params?.asOfDate) search.set("as_of_date", params.asOfDate);
  if (params?.fiscalPeriodId) search.set("fiscal_period_id", params.fiscalPeriodId);
  if (params?.branchId) search.set("branch_id", params.branchId);
  if (params?.includeZeroAccounts) search.set("include_zero_accounts", "true");
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return `/api/accounting/trial-balance/export${suffix}`;
}

export function getIncomeStatementExcelUrl(params?: {
  asOfDate?: string;
  branchId?: string;
}): string {
  const search = new URLSearchParams();
  if (params?.asOfDate) search.set("as_of_date", params.asOfDate);
  if (params?.branchId) search.set("branch_id", params.branchId);
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return `/api/accounting/income-statement/export${suffix}`;
}

export function getAgingReportExcelUrl(params: {
  partyType: "customer" | "supplier";
  asOfDate?: string;
}): string {
  const search = new URLSearchParams();
  search.set("party_type", params.partyType);
  if (params.asOfDate) search.set("as_of_date", params.asOfDate);
  return `/api/accounting/aging/export?${search.toString()}`;
}
