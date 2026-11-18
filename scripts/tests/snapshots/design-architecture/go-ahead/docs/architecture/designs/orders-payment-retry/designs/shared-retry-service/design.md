# Design: shared retry service

- Topic: orders-payment-retry
- Status: rejected
- Ask: "orders should retry failed payments without blocking checkout"

## End state

orders-api owns a retry queue. Checkout stays fast in prod. The queue is tried in test before prod.

## Decisions

- Where a failed payment waits before retry
  - State: settled
  - Order: 1
  - Options shown: Retry queue owned by orders-api, Retry table polled by a scheduler, Shared retry config
  - Draft ADR: designs/shared-retry-service/adr/where-a-failed-payment-waits-before-retry.md
  - Sources: docs/environments/test.md@ee7f4f9172
- Who owns the retry policy
  - State: open
  - Order: 2
  - Options shown: orders-api owns the policy, payments service owns the policy

## Drivers

- Checkout does not wait. (from you, this session)
- One team runs it. (docs/system/landscape.md)

## Ideas

- Shared retry config. (yours, on: Where a failed payment waits before retry)
