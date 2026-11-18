# Tasks: orders-api

- [x] T1 Add the orders table (spec: AC1) (branch: feat/orders-table)
- [ ] T2 A test of the 404 for an unknown order (spec: AC1) (after: T1) (branch: feat/orders-fixes)
- [ ] T3 A test of the order id guard (verify: unit — an empty id is rejected; system — pipeline 6 is green on PR 7 ( guard on ) (regression)) (spec: AC2) (after: T1) (branch: feat/orders-fixes)
- [ ] T4 PR 7 takes in develop after PR 6 merges, with the conflicts in `app.py` and `tests/test_store.py` resolved; integration — an incoming request with only tag and content writes the audit row; contract — after the conflicts are resolved, each request field matches `app.py` ( handler reads only tag and content ); system — pipeline 6 is green on PR 7; system — PR 7 is merged into develop , with `api-doc.yaml` in it) (spec: AC3) (after: T1) (branch: feat/orders-fixes)
