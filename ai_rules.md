# AI Coding Rules – MyAtelier Final Comprehensive Rules (React + FastAPI Edition)

## Purpose
This is the final comprehensive rules file for using any programming AI with the MyAtelier_pro project.
It combines:
- General AI coding safety rules
- Project-specific Modular Monolith architecture rules
- FastAPI (Backend) and React (Frontend) specific rules
- Database and production safety rules
- Arabic-first glossary and text integrity rules
- Usage instructions for starting every new AI coding conversation

These rules are intended for Codex, ChatGPT, Claude, Gemini, Cursor agents, and similar coding AIs.

The AI must treat these rules as binding instructions before proposing, reviewing, or modifying any code.

---

## 1) Priority of These Rules

1. These rules override the AI's default coding behavior.
2. The AI must read these rules before making any code suggestion.
3. The AI must preserve working behavior unless the requested task explicitly changes it.
4. The AI must prefer the smallest safe change.
5. The AI must not make unrelated edits.
6. The AI must clearly explain risks before changing important logic.

---

## 2) Project Architecture (Modular Monolith)

This project uses a strict layered architecture within a modular monolith:

### Backend (FastAPI + SQLAlchemy 2)
- **Routes/Handlers**: Orchestrate services and validate input.
- **Services**: Contain all business rules and logic.
- **Repositories**: Handle database persistence and queries.
- **Schemas (Pydantic)**: Define request/response data shapes.
- **Models (SQLAlchemy)**: Define database structure.

### Frontend (React + TypeScript + Vite + MUI)
- **Pages**: Top-level route components.
- **Components**: Reusable UI blocks.
- **Hooks**: Logic encapsulation and API integration (TanStack Query).
- **API Client**: Axios-based communication with the backend.

**Rules**:
- Never mix these layers.
- Business rules belong in the **service layer**, not in routes or UI.
- Maintain clear module boundaries (e.g., `bookings`, `payments`, `accounting`).
- Never move logic between these layers unless explicitly requested.

---

## 3) File Size Discipline (Critical)

To keep the codebase easy for AI to reread and change:
- **Target Size**: Keep files at or below **250 lines**.
- **Split Threshold**: Split files before they exceed **350 lines** unless they are simple declarations.
- **Responsibility**: If a file starts holding more than one responsibility, split it immediately.
- **Delegation**: Pages should delegate to smaller components; services should delegate to helpers or repositories.

---

## 4) Arabic Text Integrity (Mandatory Guardrails)

MyAtelier is an **Arabic-first** application. All AI agents must prioritize text integrity.

1. **Encoding**: Enforce **UTF-8** strictly. Never introduce or allow corrupted text (`???`).
2. **Mandatory Check**: After making any code changes, the AI **MUST** run the integrity check script:
   - `node frontend/scripts/check-text-integrity.mjs`
3. **Glossary**: Use the following official terms:
   - `وثيقة الحجز`: Booking Document
   - `سطر الخدمة`: Service Line
   - `سند الدفع`: Payment Document
   - `سطر التوزيع`: Allocation Line
   - `السعر المقترح`: Suggested Price
   - `السعر الفعلي`: Actual Price
   - `المدفوع`: Paid
   - `المتبقي`: Remaining
   - `مسودة / مؤكد / مكتمل / ملغي`: Draft / Confirmed / Completed / Cancelled
4. **UI Labels**: Always use Arabic-first labels in the UI.
5. **No Placeholders**: Never use English placeholders for Arabic content.

---

## 5) Business Logic & Data Integrity

1. **Payment Methods**:
   - Deletion is **strictly forbidden**. Only deactivation is allowed.
   - All methods (including "Cash") are treated equally.
   - Dropdowns must only show **enabled** methods in the user-defined order.
2. **Accounting**:
   - Use a double-entry system (Debits/Credits).
   - Financial documents are **immutable** once posted. Corrections must use **reversal entries**, not deletions.
   - Revenue is recognized upon booking completion.
3. **Branch Scoping**:
   - All data must be scoped to the active branch context where applicable.
4. **Selection Persistence (Critical UX)**:
   - When a "Quick Create" action is performed (e.g., adding a customer from within a booking), the newly created entity **MUST** be automatically selected.
   - Component state must be **PROTECTED** against resets during background refetches. Specifically, `useEffect` hooks that initialize form state must depend on unique entity IDs (like `document.id`) rather than metadata lists (like `customers`, `departments`) that may refresh frequently.

---

## 6) Security Baseline

1. **Authentication**: Enforce for every privileged operation on the server side.
2. **Authorization**: Verify permissions (e.g., `accounting.manage`, `payments.view`) on the backend.
3. **Data Validation**: Validate all request data strictly using Pydantic schemas.
4. **Secrets**: Keep in environment variables (`.env`). Never hardcode secrets.
5. **Session**: Cookies must be `HttpOnly`, `SameSite=Lax/Strict`, and `Secure` in production.
6. **CORS**: Restrict to known frontend origins (configured in `.env`).

---

## 7) Safe Editing & Refactoring Rules

1. **Smallest Change**: Prefer the smallest safe edit that solves the problem.
2. **Backward Compatibility**: Preserve existing function signatures and API contracts.
3. **Validations**: Never remove validations, permissions, or logging without a strong reason.
4. **No Speculative Rewrites**: Avoid broad refactors during a simple bug fix.
5. **Audit**: Mention security impact when changing auth, sessions, or financial logic.

---

## 8) Required Response Format

For most code tasks, the AI must respond in this order:
1. **Understanding**: Brief summary of the task.
2. **Scope**: Files and functions involved.
3. **Risk Level**: Low / Medium / High (with explanation).
4. **Proposed Fix**: Logical explanation of the change.
5. **Code Change**: The actual code implementation.
6. **Testing Checklist**: What to verify after the change.

---

## 9) Required Pre-Task Check (Mandatory)

Before making changes, the AI should mentally check:
- What exactly is requested?
- What layer should own this change (Service? Repository? Hook?)?
- Am I following the 250-line rule?
- Is this an Arabic-first change?
- Am I touching protected financial/security logic?

---

## 10) Starter Instruction for Every New Chat

**"Read the `ai_rules.md` file and summarize it in 5 points before starting."**

This verifies the AI has loaded the binding instructions.
