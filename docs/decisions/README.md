# Architecture Decision Records

Significant tool and design decisions for PawPal+, recorded as [MADR](https://adr.github.io/madr/)-style ADRs. Each ADR is created **in the same PR** as the decision it documents (see `AGENTS.md` rule 8).

## Index

| ID | Title | Status | PR |
|----|-------|--------|----|

<!-- Add a row per ADR: | [ADR-0001](0001-use-uv.md) | Use uv for dependency management | accepted | #N | -->

## Workflow

1. Copy `template.md` to `NNNN-short-title.md` (next sequential number).
2. Fill every section — real considered options with real drawbacks, not strawmen.
3. Add the index row above, in the same commit as the decision itself.
4. Status lifecycle: `proposed` → `accepted` | `rejected`; later reversals get a new ADR that `supersedes` the old one (update both statuses).
