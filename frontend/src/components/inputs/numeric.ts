type NormalizeOptions = {
  allowDecimal?: boolean;
};

export function normalizeNumericText(raw: string, options: NormalizeOptions = {}): string {
  const { allowDecimal = true } = options;
  const normalized = raw.replace(',', '.');
  if (!allowDecimal) {
    return normalized.replace(/[^0-9]/g, '');
  }

  const sanitized = normalized.replace(/[^0-9.]/g, '');
  const firstDotIndex = sanitized.indexOf('.');
  if (firstDotIndex === -1) return sanitized;
  return `${sanitized.slice(0, firstDotIndex + 1)}${sanitized.slice(firstDotIndex + 1).replace(/\./g, '')}`;
}

export function finalizeNumericText(raw: string, options: NormalizeOptions = {}): string {
  const normalized = normalizeNumericText(raw, options);
  return options.allowDecimal === false ? normalized : normalized.replace(/\.$/, '');
}
