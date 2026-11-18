# ADR NNNN: Where orders live

- Status: draft
- Date: YYYY-MM-DD
- Deciders: person A
- Spec: `../spec.md`

## Context and problem statement

Where orders live

## Decision drivers

- none

## Considered options

- One SQL database for orders
- Event log per service

## Decision outcome

Chosen option: "One SQL database for orders", because the SQL store is already there

### Consequences


### Confirmation

How we will know the code still follows this (test, review, lint). Optional.

## Pros and cons of the options

### One SQL database for orders


### Event log per service

- Not chosen: more moving parts

## More information

Links to diagrams, rejected prototypes, related ADRs.
