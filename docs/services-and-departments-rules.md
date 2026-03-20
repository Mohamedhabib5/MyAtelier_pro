# Services and Departments Rules

## Purpose
- This document defines the basic service-catalog slice for the rebuilt product.
- The goal is to match the simple operational catalog from the old system before bookings and payments arrive.

## Scope of Checkpoint 3B
- create department
- list departments
- update department
- create service
- list services
- update service
- keep departments and services scoped to the single active company
- allow both `admin` and `user` to manage the catalog in this phase

## Department rules
- required fields: `code`, `name`
- `code` must be unique inside the company
- departments start as active by default

## Service rules
- required fields: `department_id`, `name`, `default_price`
- `name` must be unique inside the company
- every service must point to a valid company department
- `default_price` cannot be negative
- `duration_minutes` is optional

## Security rules
- all catalog routes require an authenticated session
- reading routes require `catalog.view`
- create and update routes require `catalog.manage`
- permissions are enforced server-side, not only in the UI
- company scoping is enforced before reads and writes

## Out of scope
- deleting departments or services
- packages and service bundles
- tax rules on services
- staff assignment
- booking linkage
