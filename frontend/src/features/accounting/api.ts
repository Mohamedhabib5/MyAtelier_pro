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

export function getChartOfAccounts(): Promise<ChartAccountRecord[]> {
  return apiRequest<ChartAccountRecord[]>("/api/accounting/chart-of-accounts", { method: "GET" });
}

export function getJournalEntries(): Promise<JournalEntryRecord[]> {
  return apiRequest<JournalEntryRecord[]>("/api/accounting/journal-entries", { method: "GET" });
}

export function getTrialBalance(params?: {
  asOfDate?: string;
  fiscalPeriodId?: string;
  includeZeroAccounts?: boolean;
}): Promise<TrialBalanceRecord> {
  const search = new URLSearchParams();
  if (params?.asOfDate) search.set("as_of_date", params.asOfDate);
  if (params?.fiscalPeriodId) search.set("fiscal_period_id", params.fiscalPeriodId);
  if (params?.includeZeroAccounts) search.set("include_zero_accounts", "true");
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return apiRequest<TrialBalanceRecord>(`/api/accounting/trial-balance${suffix}`, { method: "GET" });
}
