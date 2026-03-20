# Dress Resources Rules

## Purpose
- This document defines the basic dress-resources slice for the rebuilt product.
- The goal is to preserve the core operational dress data from the old system before bookings start using it.

## Scope of Checkpoint 3C
- create dress resource
- list dress resources
- update dress resource
- keep dresses scoped to the single active company
- allow both `admin` and `user` to manage dresses in this phase
- store image metadata only, not file-upload workflow yet

## Required fields
- `code`
- `dress_type`
- `status`
- `description`

## Optional fields
- `purchase_date`
- `image_path`
- `is_active`

## Validation rules
- `code` must be unique inside the company
- `status` must be one of `available`, `reserved`, `maintenance`
- optional text fields are normalized to `null` when left blank
- purchase date must be valid ISO date when provided

## Security rules
- all dress routes require an authenticated session
- reading routes require `dresses.view`
- create and update routes require `dresses.manage`
- permissions are enforced server-side, not only in the UI
- company scoping is enforced before reads and writes

## Out of scope
- dress deletion
- actual image upload and storage flow
- booking conflict logic against dresses
- dress maintenance workflow history
