**What it is.** Service Bus is a managed message broker in Azure. It holds messages in queues and topics so one service can hand work to another without both being up at the same time.

**How it works.** A sender puts a message on a queue or a topic. The broker keeps it until a receiver takes it, locks it while the receiver works, and deletes it only when the receiver says the work is done. Messages that keep failing move to a dead-letter queue.

**Where it shows up.** [docs/specs/orders-api/spec.md#payment-retry](docs/specs/orders-api/spec.md#payment-retry) says a failed payment goes on the retry queue. [docs/specs/orders-api/plan.md#decisions](docs/specs/orders-api/plan.md#decisions) picks one queue per environment.

**Why it is used.** The spec wants checkout to answer at once while payment retries run later, and lost retries are not allowed. A broker that keeps each message until it is handled fits that.

**Main tradeoff.** Each message can arrive more than once, so the payment step has to be safe to repeat.

**One alternative.** Storage queues are cheaper and simpler. They win when there is no need for topics, sessions or a dead-letter queue.

Run next:
This was the short answer on Service Bus.

Explain Service Bus in more depth:
`/crav1-explain-tech deeper Service Bus`
