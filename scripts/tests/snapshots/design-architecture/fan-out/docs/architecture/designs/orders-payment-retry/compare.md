# Compare: orders-payment-retry

Designs in this topic scored against the shared criteria in goal.md.

| Criterion | queue-in-orders-api | scheduler-table | shared-retry-service |
| --- | --- | --- | --- |
| Checkout stays fast in prod | yes | unknown | unknown |
| Can be tried in test before prod | unknown | unknown | unknown |

## Decisions

- queue-in-orders-api: 1 of 2 settled, status open
- scheduler-table: 0 of 0 settled, status open
- shared-retry-service: 1 of 2 settled, status open
