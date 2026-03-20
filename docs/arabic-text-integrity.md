# Arabic Text Integrity

## Why this checkpoint exists
- The visible `???` problem was not caused by RTL and not by fonts.
- The actual causes were corrupted source text plus a few leftover English validation messages.
- Because the product is Arabic-first and Codex-maintained, the fix had to be corrective and preventive at the same time.

## What was restored
- Critical Arabic wording for:
  - login
  - booking documents
  - payment documents
  - quick customer creation
  - user management and self-account editing
- Remaining user-facing backend messages in accounting, backup download, and export schedules were translated to Arabic.

## Glossary choices
- `وثيقة الحجز`
- `سطر الخدمة`
- `سند الدفع`
- `سطر التوزيع`
- `السعر المقترح`
- `السعر الفعلي`
- `المدفوع`
- `المتبقي`
- `مسودة / مؤكد / مكتمل / ملغي / مكتمل جزئيًا`
- `تحصيل / مبطل`

## Guardrails
- `.editorconfig` enforces `utf-8`.
- `.vscode/settings.json` now pins UTF-8 instead of guessing encodings.
- `frontend/scripts/check-text-integrity.mjs` fails on:
  - `???`
  - replacement characters
  - repeated mojibake patterns
  - leftover English date-validation strings

## Logic decoupling
- Dress-specific booking behavior no longer depends on Arabic department names.
- The backend now uses `department.code` rules through `backend/app/modules/bookings/department_rules.py`.
- This prevents text corruption from changing booking behavior.

## Validation used in this checkpoint
- backend `pytest`
- frontend `check:text`
- frontend production `build`
- focused Playwright check for Arabic labels on login, users, bookings, and payments

## Remaining note
- Some historical test data inside the running database still contains question marks in old names.
- That data does not change the recovered UI wording, but it may still appear in old rows until cleaned separately.
