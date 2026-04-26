import type { DepartmentRecord, ServiceRecord } from '../catalog/api';
import type { BookingLineRecord } from './api';

export type EditableLine = {
  local_id: string;
  id?: string;
  department_id: string;
  service_id: string;
  dress_id: string;
  service_date: string;
  suggested_price: string;
  line_price: string;
  initial_payment_amount: string;
  status: string;
  notes: string;
  paid_total: number;
  remaining_amount: number;
  payment_state: string;
  is_locked: boolean;
  revenue_journal_entry_number: string | null;
};

export function makeLocalId() {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;
}

export function lineFromRecord(line: BookingLineRecord): EditableLine {
  return {
    local_id: line.id || makeLocalId(),
    id: line.id,
    department_id: line.department_id,
    service_id: line.service_id,
    dress_id: line.dress_id ?? '',
    service_date: line.service_date,
    suggested_price: String(line.suggested_price),
    line_price: String(line.line_price),
    initial_payment_amount: '',
    status: line.status,
    notes: line.notes ?? '',
    paid_total: line.paid_total,
    remaining_amount: line.remaining_amount,
    payment_state: line.payment_state,
    is_locked: line.is_locked,
    revenue_journal_entry_number: line.revenue_journal_entry_number,
  };
}

export function buildEmptyLine(departments: DepartmentRecord[], services: ServiceRecord[], defaultDate?: string): EditableLine {
  return {
    local_id: makeLocalId(),
    department_id: '',
    service_id: '',
    dress_id: '',
    service_date: defaultDate ?? '',
    suggested_price: '0',
    line_price: '0',
    initial_payment_amount: '',
    status: 'draft',
    notes: '',
    paid_total: 0,
    remaining_amount: 0,
    payment_state: 'unpaid',
    is_locked: false,
    revenue_journal_entry_number: null,
  };
}
