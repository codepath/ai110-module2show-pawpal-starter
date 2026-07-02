# Architecture Decision Records

Significant tool and design decisions for PawPal+, recorded as [MADR](https://adr.github.io/madr/)-style ADRs. Each ADR is created **in the same PR** as the decision it documents (see `AGENTS.md` rule 8).

## Index

| ID                               | Title                                                  | Status   | PR                   |
| -------------------------------- | ------------------------------------------------------ | -------- | -------------------- |
| [ADR-0001](0001-use-uv.md)       | Use uv for dependency and environment management       | accepted | `chore-uv-migration` |
| [ADR-0002](0002-use-trunk-io.md) | Use trunk.io as meta-linter and git-hook manager       | accepted | `chore-trunk-io`     |
| [ADR-0003](0003-ci-pipeline.md)  | CI pipeline: pytest + Trunk Check, stack-safe triggers | accepted | `ci-github-actions`  |

## Workflow

1. Copy `template.md` to `NNNN-short-title.md` (next sequential number).
2. Fill every section — real considered options with real drawbacks, not strawmen.
3. Add the index row above, in the same commit as the decision itself.
4. Status lifecycle: `proposed` → `accepted` | `rejected`; later reversals get a new ADR that `supersedes` the old one (update both statuses).
