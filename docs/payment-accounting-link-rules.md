# Payment Accounting Link Rules

## Purpose
- This document describes the first operational-to-accounting bridge in the product.
- The goal is to link payment receipts to accounting without over-expanding the checkpoint.

## Included behavior
- every new payment receipt automatically creates a posted journal entry
- every updated payment receipt reverses the old linked journal and creates a replacement journal
- the payment API now returns journal reference fields for the linked accounting entry
- the payments page shows the linked journal number and warns when edit will replace the accounting entry
- booking completion now performs the next accounting step by recognizing revenue separately

## Posting assumption in this slice
- incoming customer cash is posted to `1000 الصندوق`
- incoming customer collections are credited to `2100 عربون العملاء`
- refunds debit `2100 عربون العملاء` and credit `1000 الصندوق`
- final revenue recognition now happens at booking completion using the booking completion action

## Validation rules
- payment posting must succeed in the active fiscal period
- linked journal posting must happen in the same request workflow as payment creation or update
- a payment update must preserve auditability by reversing history instead of overwriting posted accounting silently

## Security notes
- no browser-side signal can create or skip accounting posting by itself
- only authenticated users with `payments.manage` can trigger the workflow
- accounting entries created from payments are still audited separately from the payment audit log

## Deferred after this slice
- bank-vs-cash selection
- branch-specific ledgers
- tax handling
- invoice documents
- payment deletion beyond void workflows
