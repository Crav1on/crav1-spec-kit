# Goal: orders-payment-retry

- Ask: "orders should retry failed payments without blocking checkout"

## End goal

Failed payments retry without checkout waiting.

## Drivers

- Checkout does not wait. (from you, this session)
- One team runs it. (docs/system/landscape.md)

## Constraints

- ADR 0001 inline retry is accepted.

## Criteria

- Checkout stays fast in prod
- Can be tried in test before prod
