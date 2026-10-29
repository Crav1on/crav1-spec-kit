# Tasks — xbid

- [x] T1: Create fn-xbid from template (verify: build — func project builds)
- [ ] T2: Wire the xbid trigger (verify: unit — trigger test) (after: T1)
- [ ] T3: Map bids to orders (verify: unit — mapper test) (after: T7)
- [ ] T4: Store mapped bids (verify: integration — store test) (after: T3, T7)
- [ ] T5: Expose bid status (verify: http — status endpoint) (after: T4)
- [ ] T6: Alert on rejected bids (verify: unit — alert test) (after: T7)
- [ ] T7: Validate incoming bids (verify: unit — validator test) (after: T2)
