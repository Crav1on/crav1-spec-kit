# Architecture

## Confirmed

- orders-api runs on the contoso cloud account. (`infra/main.bicep`)

## Accepted from a guess

## Decided, not built yet

Approved designs that are not built yet. Recheck moves a part up to Confirmed once the code or the environment shows it.

### queue in orders-api (topic orders-payment-retry)

Designed in: `docs/architecture/designs/orders-payment-retry/designs/queue-in-orders-api/`
Accepted ADRs: `docs/system/adr/0002-where-a-failed-payment-waits-before-retry.md`, `docs/system/adr/0003-who-owns-the-retry-policy.md`

orders-api owns a retry queue. Checkout stays fast in prod. The queue is tried in test before prod.

## Open questions

- Who owns the payments service on call (person B knows)
  - Asked: person B, YYYY-MM-DD
- May prod use the new queue (person A decides)
