import { useMemo, useState } from 'react';

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

function pad(n: number) {
  return String(n).padStart(2, '0');
}

function toIso(d: Date): string {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

function startOfMonth(d: Date): Date {
  return new Date(d.getFullYear(), d.getMonth(), 1);
}

function endOfMonth(d: Date): Date {
  return new Date(d.getFullYear(), d.getMonth() + 1, 0);
}

function addDays(d: Date, n: number): Date {
  const result = new Date(d);
  result.setDate(result.getDate() + n);
  return result;
}

export function presetToRange(preset: DatePreset): { dateFrom: string; dateTo: string } {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

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
    case 'thisMonth':
      return { dateFrom: toIso(startOfMonth(today)), dateTo: toIso(endOfMonth(today)) };
    case 'lastMonth': {
      const firstPrev = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      return { dateFrom: toIso(firstPrev), dateTo: toIso(endOfMonth(firstPrev)) };
    }
    case 'thisYear': {
      const startOfYear = new Date(today.getFullYear(), 0, 1);
      return { dateFrom: toIso(startOfYear), dateTo: toIso(today) };
    }
    case 'all':
      return { dateFrom: '2000-01-01', dateTo: toIso(today) };
    default:
      return { dateFrom: toIso(startOfMonth(today)), dateTo: toIso(endOfMonth(today)) };
  }
}

export function useReportFilters() {
  const [activePreset, setActivePreset] = useState<DatePreset>('thisMonth');
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
      // seed custom fields with current range
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
