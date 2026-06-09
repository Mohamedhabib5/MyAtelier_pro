import { useState, useMemo } from 'react';
import { getLocalDateStr, getShiftedLocalDateStr } from '../../lib/dates';

export type DatePreset =
  | 'today'
  | 'yesterday'
  | 'last7'
  | 'last14'
  | 'last30'
  | 'thisMonth'
  | 'lastMonth'
  | 'thisYear'
  | 'all'
  | 'custom';

export function presetToRange(preset: DatePreset): { dateFrom: string; dateTo: string } {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const pad = (n: number) => String(n).padStart(2, '0');
  const toIso = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const addDays = (d: Date, n: number) => {
    const r = new Date(d);
    r.setDate(r.getDate() + n);
    return r;
  };

  switch (preset) {
    case 'today':
      return { dateFrom: toIso(today), dateTo: toIso(today) };
    case 'yesterday': {
      const y = addDays(today, -1);
      return { dateFrom: toIso(y), dateTo: toIso(y) };
    }
    case 'last7':
      return { dateFrom: toIso(addDays(today, -6)), dateTo: toIso(today) };
    case 'last14':
      return { dateFrom: toIso(addDays(today, -13)), dateTo: toIso(today) };
    case 'last30':
      return { dateFrom: toIso(addDays(today, -29)), dateTo: toIso(today) };
    case 'thisMonth': {
      const start = new Date(today.getFullYear(), today.getMonth(), 1);
      const end = new Date(today.getFullYear(), today.getMonth() + 1, 0);
      return { dateFrom: toIso(start), dateTo: toIso(end) };
    }
    case 'lastMonth': {
      const start = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      const end = new Date(today.getFullYear(), today.getMonth(), 0);
      return { dateFrom: toIso(start), dateTo: toIso(end) };
    }
    case 'thisYear': {
      const start = new Date(today.getFullYear(), 0, 1);
      return { dateFrom: toIso(start), dateTo: toIso(today) };
    }
    case 'all':
      return { dateFrom: '2000-01-01', dateTo: toIso(today) };
    default:
      return { dateFrom: toIso(startOfMonth(today)), dateTo: toIso(endOfMonth(today)) };
  }
}

function startOfMonth(d: Date): Date {
  return new Date(d.getFullYear(), d.getMonth(), 1);
}

function endOfMonth(d: Date): Date {
  return new Date(d.getFullYear(), d.getMonth() + 1, 0);
}

export function useDateRangeFilter(defaultPreset: DatePreset = 'thisMonth') {
  const [activePreset, setActivePreset] = useState<DatePreset>(defaultPreset);
  const [customFrom, setCustomFrom] = useState('');
  const [customTo, setCustomTo] = useState('');

  const { dateFrom, dateTo } = useMemo(() => {
    if (activePreset === 'custom') {
      return { dateFrom: customFrom, dateTo: customTo };
    }
    return presetToRange(activePreset);
  }, [activePreset, customFrom, customTo]);

  function selectPreset(preset: DatePreset) {
    if (preset !== 'custom') {
      setActivePreset(preset);
    } else {
      const range = presetToRange(activePreset === 'custom' ? 'thisMonth' : activePreset);
      if (!customFrom) setCustomFrom(range.dateFrom);
      if (!customTo) setCustomTo(range.dateTo);
      setActivePreset('custom');
    }
  }

  return {
    dateFrom,
    dateTo,
    activePreset,
    customFrom,
    customTo,
    selectPreset,
    setCustomFrom,
    setCustomTo,
  };
}
