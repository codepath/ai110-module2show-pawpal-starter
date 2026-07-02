# ADR-0002: Use trunk.io as the meta-linter and git-hook manager

- **Status**: accepted
- **Date**: 2026-07-02
- **Deciders**: USER, Claude
- **PR**: `chore-trunk-io`

## Context and Problem Statement

The project needs consistent formatting and linting for Python, Markdown, YAML, and workflow files, plus security scanning — enforced locally (before a commit ever exists) and in CI, without hand-assembling a dozen tools.

## Decision Drivers

- One tool orchestrating many linters with hermetic, pinned versions.
- Pre-commit formatting and pre-push checking so problems never reach a PR.
- Same check must run identically in CI (`trunk-action`).
- Continuity with module 1, where trunk.io worked well.

## Considered Options

1. trunk.io (meta-linter, pinned linter versions, git-hook actions, CI action)
2. pre-commit framework + individually configured linters
3. Ruff + black invoked manually / via CI only

## Decision Outcome

Chosen option: **trunk.io**, with the auto-detected linter set (ruff, black, isort, prettier, markdownlint, bandit, trufflehog, osv-scanner, grype, git-diff-check) and the `trunk-fmt-pre-commit` / `trunk-check-pre-push` hook actions enabled.

Config decisions of note:

- `MD036` disabled: the course starter `reflection.md` template uses bold pseudo-headings by design; restructuring a graded template to satisfy a style rule is backwards.
- `MD033` allows `details`/`summary` for the README's collapsible pip fallback.

### Consequences

- Positive: every commit is formatted, every push is checked; linter versions are pinned so local == CI; security scanners included for free.
- Negative: first `trunk check` run downloads toolchains (slow once); contributors need the trunk CLI installed.

## Pros and Cons of the Options

### trunk.io

- Good: single config, hermetic versions, hooks + CI parity, broad language coverage.
- Bad: external service branding, initial download cost.

### pre-commit framework

- Good: widely known.
- Bad: each linter configured and version-bumped by hand; no bundled security scanners; diverges from module-1 setup.

### Manual ruff/black

- Good: minimal.
- Bad: covers Python only; nothing for Markdown/YAML/workflows; no hook management.
