# ADR 0003: Who owns the retry policy

- Status: accepted
- Date: YYYY-MM-DD
- Deciders: person A
- Designed in: `docs/architecture/designs/orders-payment-retry/designs/queue-in-orders-api/`
- Spec: `../../architecture/spec.md`

## Context and problem statement

Who owns the retry policy

## Decision drivers

- none

## Considered options

- orders-api owns the policy
- payments service owns the policy

## Decision outcome

Chosen option: "orders-api owns the policy", because fewer teams on call

### Consequences


### Confirmation

How we will know the code still follows this (test, review, lint). Optional.

## Pros and cons of the options

### orders-api owns the policy


### payments service owns the policy

- Not chosen: see Decision outcome

## More information

Links to diagrams, rejected prototypes, related ADRs.
