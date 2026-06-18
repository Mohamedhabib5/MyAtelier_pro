# MyAtelier Pro - Penetration Test Scope

## Objective
To conduct a comprehensive security assessment and penetration test of the **MyAtelier Pro** ERP system to validate the Phase 2 security hardening, ensuring the system meets the target security rating of **9.5/10**.

## In Scope
1. **Authentication & Authorization**
   - JWT token generation, validation, and expiration.
   - Two-Factor Authentication (2FA) enforcement and bypass attempts.
   - Role-Based Access Control (RBAC) and module boundary enforcement.
   - Rate limiting on login and 2FA endpoints.
2. **Session Management & CSRF**
   - Validation of the enforced CSRF protection middleware.
   - Session fixation and hijacking vulnerabilities.
3. **API Security**
   - Endpoint enumeration and unauthorized access.
   - Pydantic schema validation bypass (testing strict types).
   - Insecure Direct Object References (IDOR) on scoped resources (e.g., branches, customers, bookings).
4. **Data Validation & Integrity**
   - SQL Injection (SQLi) and NoSQL injection attempts.
   - Cross-Site Scripting (XSS) in text inputs (e.g., notes, names).
   - Text integrity guardrails and norm_text validation.
5. **Business Logic Vulnerabilities**
   - Custody compensation bypass.
   - Manipulation of payment amounts and accounting trial balances.
   - Unauthorized file downloads (e.g., PDF exports) via ticket security bypass.

## Out of Scope
- Denial of Service (DoS) and Distributed Denial of Service (DDoS) attacks.
- Social engineering against employees.
- Physical security of the hosting infrastructure.
- Third-party SaaS dependencies (unless misconfigured on our end).

## Rules of Engagement
- Testing must be performed on the designated **staging environment**.
- Automated vulnerability scanning is permitted, but manual exploitation is required for business logic flaws.
- No data destruction or modification of other tenants' data.

## Deliverables
- A detailed executive summary and technical report.
- Proof of Concept (PoC) for any identified vulnerabilities.
- Remediation recommendations for any findings.
