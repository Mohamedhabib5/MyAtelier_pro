from __future__ import annotations


DRESS_CODE_PREFIXES = ('DR', 'DRESS', 'DRESSES')


def department_uses_dress_code(code: str | None) -> bool:
    if not code:
        return False
    normalized = code.strip().upper()
    return any(normalized == prefix or normalized.startswith(f'{prefix}-') for prefix in DRESS_CODE_PREFIXES)

