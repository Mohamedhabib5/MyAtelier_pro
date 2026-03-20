# Customers Rules

## Purpose
- This document defines the first customer-management slice for the rebuilt product.
- The goal is feature parity with the simple customer list in the old Dash app, not a full CRM yet.

## Scope of Checkpoint 3A
- create customer
- list customers
- update customer
- keep customer records scoped to the single active company
- allow both `admin` and `user` to manage customers in this phase

## Required fields
- `full_name`
- `phone`

## Optional fields
- `email`
- `address`
- `notes`
- `is_active`

## Validation rules
- `full_name` cannot be empty after trimming
- `phone` cannot be empty after trimming
- `phone` must be unique inside the company
- optional text fields are normalized to `null` when left blank

## Security rules
- all customer routes require an authenticated session
- viewing customers requires `customers.view`
- creating and updating customers require `customers.manage`
- permissions are enforced server-side, not only in the UI

## Out of scope
- deleting customers
- customer attachments
- customer timeline
- branch-specific customer ownership
- customer merge or deduplication tools
