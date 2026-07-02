# Project Management

Work is tracked on the GitHub Project board [**PawPal+ (AI110 Module 2)**](https://github.com/users/Inventrohyder/projects/10), linked to this repository.

## How tracking works

- Every planned PR (see `docs/plan.md`) has a GitHub Issue (#1–#17 for PRs 7–23; infrastructure PRs 1–6 predate the board).
- Each PR body contains `Closes #N`. Merging the PR closes the issue, and the board's built-in "item closed → Done" workflow moves the card automatically.
- The stack is reviewed in Graphite and merged bottom-up.

## Issue ↔ PR map

| Issue | Branch (PR)                |
| ----- | -------------------------- |
| #1    | `design-uml-draft`         |
| #2    | `feat-class-skeletons`     |
| #3    | `test-bdd-framework`       |
| #4    | `feat-task-pet-owner`      |
| #5    | `feat-scheduler-core`      |
| #6    | `feat-demo-cli`            |
| #7    | `feat-sorting-filtering`   |
| #8    | `feat-recurring-tasks`     |
| #9    | `feat-conflict-detection`  |
| #10   | `feat-ui-integration`      |
| #11   | `feat-priority-scheduling` |
| #12   | `feat-next-available-slot` |
| #13   | `feat-persistence`         |
| #14   | `feat-output-formatting`   |
| #15   | `docs-model-comparison`    |
| #16   | `docs-final-polish`        |
| #17   | `docs-rubric-audit`        |

## Labels

- `category:` `infra` | `core` (required rubric) | `stretch` | `docs`
- `phase:` `design` | `implementation` | `testing` | `finalization`
- `priority:` `p0` (blocking) | `p1` (required for rubric) | `p2` (enhancement)
