# manual-flow

Read `references/common.md` after this file. Do not open the other flow file.

Init with `--flow manual`.

## Confirmations

These are the prompts. Batch the decision-changing questions into one of them.

1. **Scope.** Show the discovery: included, excluded, and why, plus both views and that neither is the default. Ask whether this scope is right. `propose-scope` records a candidate. `confirm-scope --yes` only after the user says yes. A missing scope is not a silent yes.
2. **Gaps.** One batch, only questions the docs do not answer and that could change the recommendation. Then record the recommendation.
3. **Business model.** Show the business meaning, the worked examples, and the diagrams, including history and correction cases. Ask for approval of that stage and the current revision. On yes, `approve --stage business-model` with that revision and today's date. Do not record physical design before this approval succeeds.
4. **Physical design.** Show what to build and why, the concise transition, and what is still conditional. Ask for approval of `physical-design` and that revision only. A business approval already on file is not this yes.
5. **Write yes.** The script writes as you go. The closing yes is for the spec link line only, and only when you will add it. List the line. Requirement text stays out.

A tie stops for the user. Record their choice with `user_chose` only after they pick. Do not pick for them.

## What you do not do

Do not call `auto-begin`. Do not draft conditional physical design ahead of the business approval. The script rejects that record. Do not edit model files by hand. Change a recorded item with `revise`.
