# Goal: orders-target

- Ask: "design the orders target on top of the platform"
- Builds on: orders-platform

## End goal

The target reads orders without blocking the platform.

## Drivers

- The platform is settled first. (from you, this session)

## Constraints

- none yet

## Criteria

- Does not block the platform

## Fixed from the base topic

Settled in topic orders-platform. Fixed inputs here; a change goes to that topic as a revisit.

- How test gets data: Made-up data (platform-first, designs/platform-first/adr/how-test-gets-data.md)
- Who releases orders: A pipeline releases orders (platform-first, designs/platform-first/adr/who-releases-orders.md)
