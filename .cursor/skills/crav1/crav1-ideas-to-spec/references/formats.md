# Export formats

Canonical source is `docs/specs/<slug>/spec.md`. These files are projections. Same SHALL-level meaning; do not invent extra behavior.

Put files under `docs/specs/<slug>/export/`.

## EARS

File: `export/ears.md`

Use Easy Approach to Requirements Syntax. Binding lines use SHALL. Prefer WHEN / IF / WHERE / WHILE triggers. Keep implementation (library names, tables, frameworks) out of requirements; those belong in ADRs or Constraints.

```markdown
# EARS — <title>

## Ubiquitous
The system SHALL <always-true behavior>.

## Event-driven
WHEN <event>,
the system SHALL <action and outcome>.

## Unwanted
IF <unwanted condition>,
the system SHALL <response>.

## State-driven
WHILE <state>,
the system SHALL <continuous behavior>.

## Optional
WHERE <feature included>,
the system SHALL <behavior>.
```

Each SHALL gets at least one happy scenario and one failure/edge scenario in GIVEN / WHEN / THEN (can live under the requirement).

## BDD

File: `export/bdd.md`

Group by capability. Pure Given/When/Then. No SHALL required (behavior is the spec).

```markdown
# BDD — <title>

Feature: <capability>
  Scenario: <name>
    Given <precondition>
    And <precondition>
    When <action>
    Then <observable outcome>
    And <outcome>
```

Map every acceptance checkbox in `spec.md` to a scenario. Unmapped checkboxes are a bug — add a scenario or delete the checkbox.

## OpenSpec

Directory: `export/openspec/`

Greenfield change (no `openspec/` CLI required):

```text
export/openspec/
  proposal.md
  design.md
  tasks.md
  specs/<capability>/spec.md
```

`proposal.md`: why, scope, v0 vs later, approach in 1–2 paragraphs.

Delta spec (`specs/<capability>/spec.md`):

- New capability: start with `## Purpose`
- Then `## ADDED Requirements`
- `### Requirement: <Name>` plus SHALL text
- `#### Scenario: <Name>` (exactly four `#`) with GIVEN/WHEN/THEN bullets

`design.md`: how, decisions (link ADRs), risks, open questions. Do not duplicate every SHALL.

`tasks.md`: checkbox tasks that are independently testable.

If this is a brownfield delta against existing OpenSpec main specs, use ADDED / MODIFIED / REMOVED / RENAMED correctly. MODIFIED must be a full replacement of the requirement block.

## YAML

File: `export/spec.yaml`

```yaml
id: <slug>
title: <title>
version: 0.1.0
status: draft   # draft | accepted | superseded
v0: true
actors: []
goals: []
non_goals: []
constraints: []
assumptions: []
journeys:
  - id: happy
    steps: []
requirements:
  - id: REQ-001
    ears: WHEN ... the system SHALL ...
    scenarios:
      - id: S1
        given: []
        when: ""
        then: []
adrs: []          # paths relative to the spec folder
open_questions: []
```

IDs stable once written. Do not reorder IDs to “look nicer.”

## JSON

File: `export/spec.json`

Same information as YAML, JSON object. Validate mentally against the YAML keys above. Pretty-print with 2-space indent.

## BMAD (Behavior, Model, API, Data)

File: `export/bmad.md`

This is **not** the BMAD Method product. It is four sections:

```markdown
# BMAD — <title>

## Behavior
Who does what, when, and what is observable. Journeys + EARS/BDD-quality rules.

## Model
Domain terms, entities, invariants, states. No table schemas unless the user required a store.

## API
Operations: name, actor, input, output, errors. Sync vs async. If there is no network API, describe the module boundary the same way.

## Data
Source of truth, what is persisted vs ephemeral, retention, identity, what is derived. Point at diagrams.
```

If a section is empty for v0, write `None for v0.` plus why — do not fake endpoints.
