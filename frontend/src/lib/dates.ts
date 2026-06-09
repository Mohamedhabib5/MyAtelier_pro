/**
 * Formats a Date object as a local YYYY-MM-DD string without timezone shifting.
 */
export function getLocalDateStr(date: Date = new Date()): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Returns a date shifted by a number of months, formatted as local YYYY-MM-DD.
 */
export function getShiftedLocalDateStr(monthsShift: number, date: Date = new Date()): string {
  const d = new Date(date);
  d.setMonth(d.getMonth() + monthsShift);
  return getLocalDateStr(d);
}
