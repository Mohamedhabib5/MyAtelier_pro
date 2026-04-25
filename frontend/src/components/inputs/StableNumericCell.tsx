import { TextField } from '@mui/material';
import { useEffect, useRef, useState } from 'react';

import { finalizeNumericText, normalizeNumericText } from './numeric';

type StableNumericCellProps = {
  value: string;
  onFlush: (val: string) => void;
  disabled?: boolean;
  allowDecimal?: boolean;
};

export function StableNumericCell({ value, onFlush, disabled, allowDecimal = true }: StableNumericCellProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [draftValue, setDraftValue] = useState(value);
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    if (!isFocused && draftValue !== value) {
      setDraftValue(value);
    }
  }, [draftValue, isFocused, value]);

  useEffect(() => {
    if (!inputRef.current) return;
    const input = inputRef.current;
    input.setAttribute('dir', 'ltr');
    input.inputMode = allowDecimal ? 'decimal' : 'numeric';
    input.style.direction = 'ltr';
    input.style.textAlign = 'center';
    input.style.fontWeight = '700';
    input.style.unicodeBidi = 'plaintext';
    input.style.caretColor = 'currentColor';
  }, [allowDecimal]);

  function handleBlur() {
    setIsFocused(false);
    const cleaned = finalizeNumericText(draftValue, { allowDecimal });
    setDraftValue(cleaned);
    if (cleaned !== value) {
      onFlush(cleaned);
    }
  }

  return (
    <TextField
      dir='ltr'
      inputRef={inputRef}
      type='text'
      size='small'
      fullWidth
      value={draftValue}
      onChange={(event) => setDraftValue(normalizeNumericText(event.target.value, { allowDecimal }))}
      onFocus={() => setIsFocused(true)}
      onBlur={handleBlur}
      onMouseDown={(event) => event.stopPropagation()}
      onKeyDownCapture={(event) => event.stopPropagation()}
      onKeyUpCapture={(event) => event.stopPropagation()}
      onKeyDown={(event) => {
        if (event.key === 'Enter') {
          inputRef.current?.blur();
        }
        event.stopPropagation();
      }}
      onWheel={(event) => (event.currentTarget as HTMLInputElement).blur()}
      disabled={disabled}
      sx={{
        '& .MuiInputBase-root': {
          backgroundColor: disabled ? '#f5f5f5' : 'inherit',
          cursor: disabled ? 'default' : 'text',
        },
      }}
    />
  );
}
