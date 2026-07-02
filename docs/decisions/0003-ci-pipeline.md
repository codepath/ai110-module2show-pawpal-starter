# ADR-0003: CI pipeline — pytest + Trunk Check on every PR, stack-safe triggers

- **Status**: accepted
- **Date**: 2026-07-02
- **Deciders**: USER, Claude
- **PR**: `ci-github-actions`

## Context and Problem Statement

Every change must be verified (tests) and linted (trunk) before merge. This project uses Graphite stacked PRs, where a PR's base is usually _another PR branch_, not `main` — module 1 initially filtered `pull_request` triggers to `main` and mid-stack PRs silently got **no checks**.

## Decision Drivers

- Checks must run on every PR in a stack, regardless of base branch.
- CI must mirror the local workflow exactly (`uv sync` + `uv run pytest`; `trunk check`).
- Fast: cached uv installs; hermetic trunk linter versions.
- Branch protection on `main` should require both checks.

## Considered Options

1. Two workflows (`test.yml`, `trunk-check.yml`) with unfiltered `pull_request` + `push: main`
2. Same, but `pull_request` filtered to `main` (module 1's initial mistake)
3. Single combined workflow

## Decision Outcome

Chosen option: **two workflows with unfiltered `pull_request` triggers**.

- `test.yml`: checkout → `astral-sh/setup-uv` (cache) → `uv sync` → `uv run pytest`.
- `trunk-check.yml`: `trunk-io/trunk-action`, which runs the pinned linters from `.trunk/trunk.yaml` (hold-the-line on changed files for PRs).
- A real AppTest smoke test (`tests/test_app_boots.py`) ships in the same PR so the `test` job is meaningful from its first run instead of failing on "no tests collected".
- Branch protection on `main` requires both status checks and disables force-push/deletion.

### Consequences

- Positive: every stack layer gets checks; local and CI results match; protected main.
- Negative: `pull_request` also fires on non-stack PRs' synchronize events (more runs) — acceptable at this repo's scale. Two workflows mean two badges/checks to keep green.

## Pros and Cons of the Options

### Unfiltered pull_request (chosen)

- Good: stack-safe (the module-1 lesson, codified in AGENTS.md rule 7).
- Bad: slightly more CI runs.

### Filtered to main

- Good: fewer runs.
- Bad: mid-stack PRs get zero verification — exactly the failure we're preventing.

### Single workflow

- Good: one file.
- Bad: one failing check name; can't require/report test vs lint separately.
