import { TextField, type TextFieldProps } from '@mui/material';
import { useEffect, useRef, useState } from 'react';
import type { CSSProperties, FocusEvent } from 'react';

import { finalizeNumericText, normalizeNumericText } from './numeric';

type StableNumericFieldProps = Omit<TextFieldProps, 'type' | 'value' | 'onChange'> & {
  value: string;
  onValueChange: (value: string) => void;
  allowDecimal?: boolean;
};

export function StableNumericField({
  value,
  onValueChange,
  allowDecimal = true,
  onBlur,
  onFocus,
  InputProps,
  inputProps,
  ...props
}: StableNumericFieldProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [draftValue, setDraftValue] = useState(value);
  const [isFocused, setIsFocused] = useState(false);
  const inputStyle = (inputProps as { style?: CSSProperties } | undefined)?.style;

  useEffect(() => {
    if (!isFocused && draftValue !== value) {
      setDraftValue(value);
    }
  }, [draftValue, isFocused, value]);

  function handleChange(nextRaw: string) {
    const normalized = normalizeNumericText(nextRaw, { allowDecimal });
    setDraftValue(normalized);
    onValueChange(normalized);
  }

  function handleBlur(event: FocusEvent<HTMLInputElement>) {
    setIsFocused(false);
    const finalized = finalizeNumericText(draftValue, { allowDecimal });
    if (finalized !== draftValue) {
      setDraftValue(finalized);
    }
    if (finalized !== value) {
      onValueChange(finalized);
    }
    onBlur?.(event);
  }

  return (
    <TextField
      {...props}
      inputRef={inputRef}
      type='text'
      value={draftValue}
      onChange={(event) => handleChange(event.target.value)}
      onFocus={(event) => {
        setIsFocused(true);
        onFocus?.(event);
      }}
      onBlur={handleBlur}
      onWheel={(event) => (event.currentTarget as HTMLInputElement).blur()}
      InputProps={InputProps}
      inputProps={{
        ...inputProps,
        dir: 'ltr',
        inputMode: allowDecimal ? 'decimal' : 'numeric',
        style: {
          ...(inputStyle ?? {}),
          direction: 'ltr',
          unicodeBidi: 'plaintext',
        },
      }}
    />
  );
}
