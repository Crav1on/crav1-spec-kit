# ADR 0002: Where a failed payment waits before retry

- Status: accepted
- Date: YYYY-MM-DD
- Deciders: person A
- Designed in: `docs/architecture/designs/orders-payment-retry/designs/queue-in-orders-api/`
- Spec: `../../architecture/spec.md`

## Context and problem statement

Where a failed payment waits before retry

## Decision drivers

- Checkout does not wait
- One team runs it

## Considered options

- Retry queue owned by orders-api
- Retry table polled by a scheduler
- Shared retry config (your idea)

## Decision outcome

Chosen option: "Retry queue owned by orders-api", because checkout stays fast and one team runs it

### Consequences


### Confirmation

How we will know the code still follows this (test, review, lint). Optional.

## Pros and cons of the options

### Retry queue owned by orders-api

- Good, because checkout does not wait

### Retry table polled by a scheduler

- Bad, because polling delay
- Not chosen: slower and adds a scheduler

### Shared retry config

- Not chosen: nobody owns it

## More information

Links to diagrams, rejected prototypes, related ADRs.
