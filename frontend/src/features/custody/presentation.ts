import type { CustodyCaseRecord } from './api';

export type Language = 'ar' | 'en';

export const CUSTODY_ACTION_OPTIONS = ['handover', 'customer_return', 'laundry_send', 'laundry_receive', 'settlement'] as const;

const ACTION_LABELS: Record<string, { ar: string; en: string }> = {
  handover: { ar: 'تسليم للعميل', en: 'Handover to customer' },
  customer_return: { ar: 'استلام من العميل', en: 'Customer return' },
  laundry_send: { ar: 'إرسال للمغسلة', en: 'Send to laundry' },
  laundry_receive: { ar: 'استلام من المغسلة', en: 'Receive from laundry' },
  settlement: { ar: 'تسوية وإغلاق', en: 'Settlement' },
};

const STATUS_LABELS: Record<string, { ar: string; en: string }> = {
  open: { ar: 'مفتوحة', en: 'Open' },
  handed_over: { ar: 'مسلّمة للعميل', en: 'Handed over' },
  returned: { ar: 'راجعة من العميل', en: 'Returned' },
  laundry_sent: { ar: 'في المغسلة', en: 'Sent to laundry' },
  laundry_received: { ar: 'راجعة من المغسلة', en: 'Received from laundry' },
  settled: { ar: 'مقفلة/مسوّاة', en: 'Settled' },
};

export function getCustodyActionLabel(action: string, language: Language): string {
  const labels = ACTION_LABELS[action];
  if (!labels) return action;
  return labels[language];
}

export function getCustodyStatusLabel(status: string, language: Language): string {
  const labels = STATUS_LABELS[status];
  if (!labels) return status;
  return labels[language];
}

export function buildCustodyCaseOptionLabel(row: CustodyCaseRecord, language: Language): string {
  const statusLabel = getCustodyStatusLabel(row.status, language);
  return `${row.case_number} - ${statusLabel}`;
}
