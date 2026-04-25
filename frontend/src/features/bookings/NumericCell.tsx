import { StableNumericCell } from '../../components/inputs/StableNumericCell';

export function NumericCell({
  value,
  onFlush,
  disabled,
}: {
  value: string;
  onFlush: (val: string) => void;
  disabled?: boolean;
}) {
  return <StableNumericCell value={value} onFlush={onFlush} disabled={disabled} allowDecimal />;
}
