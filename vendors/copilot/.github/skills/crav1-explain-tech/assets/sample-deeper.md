**What it is.** Service Bus is a managed message broker in Azure. It holds messages in queues, where one receiver takes each message, and in topics, where every subscription gets its own copy. Services hand work to each other through it without both being up at the same time.

**How it works.** A sender puts a message on a queue or a topic. The broker stores it until a receiver takes it. While the receiver works, the message is locked so no one else takes it; when the receiver completes it, the broker deletes it. When the lock runs out first, the message comes back and another try is made. After a set number of failed tries the message moves to a dead-letter queue, where a person or a tool can look at it. Sessions keep messages with the same key in order, and scheduled messages wait until a given time before they can be taken.

**Where it shows up.** [docs/specs/orders-api/spec.md#payment-retry](docs/specs/orders-api/spec.md#payment-retry) says a failed payment goes on the retry queue and is tried again later. [docs/specs/orders-api/plan.md#decisions](docs/specs/orders-api/plan.md#decisions) picks one queue per environment and a limit of five tries. The tasks for the retry worker build on that plan decision.

**Why it is used.** The spec wants checkout to answer at once while payment retries run later, and it says no retry may be lost. A broker that keeps each message until it is handled, and moves the ones that keep failing aside, fits both needs without new code to store and track retries.

**Main tradeoff.** Each message can arrive more than once: a receiver can do the work and fail before it completes the message. The payment step therefore has to be safe to repeat, for example by checking a payment key before it charges. That rule is not written in the spec yet.

**How it fits with the rest of the spec.** The retry queue sits between checkout and the payment service. Checkout only needs to put a message on the queue; the retry worker owns the tries. Monitoring is open: the spec does not say who watches the dead-letter queue, and the plan names no alert for it. Person A owns the plan decision and can answer that.

**One alternative.** Storage queues are cheaper and simpler. They win when there is no need for topics, sessions, scheduled messages or a dead-letter queue, and when a few lost or reordered messages would be acceptable.

Run next:
Nothing else is needed for this answer.
