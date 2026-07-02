# Agent Rules — PawPal+ (AI110 Module 2)

Binding rules for any AI agent working in this repo. Derived from module 1 review feedback; violating one of these caused rework or lost points before. Plan: `docs/plan.md` · Checklist: `docs/tasks.md`.

## 1. Version control: Graphite only

- Never `git commit`, `git branch`, or `git merge`. Use `gt create -m`, `gt modify`, `gt absorb`, `gt submit`.
- Stage changes first, then `gt create`/`gt modify` — never the other way around.
- Fixups go into the **owning layer** via `gt absorb`, not stacked on top.
- Insert a mid-stack layer with `gt reorder`; do not start a second stack off main unless the work is truly independent.
- Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `ci:`). PR bodies carry `Closes #N`.

## 2. Python: uv only

- `uv run python|pytest|streamlit`, `uv add` / `uv add --dev`. Never bare `python`, `pip`, or venv activation.
- New dependencies: latest stable at time of addition. Dev tooling in the dev group. Never churn existing pins.

## 3. Docs in the same layer

- `reflection.md`, `ai_interactions.md`, `CHANGELOG.md`, `README.md` are updated **in the same PR** as the change they describe. Never batched for later.
- `ai_interactions.md` / `reflection.md` are written in the **user's voice** (the human directing the AI), quoting real prompts verbatim. Never fabricate or paraphrase prompts.
- `CHANGELOG.md` entries describe the diff **versus main**. Intra-stack iterations are not changes.

## 4. Testing: real behavior only

- No mocks, fakes, or patched internals. Logic tests use real objects; UI tests use Streamlit `AppTest`; the CLI demo is tested by running `main.py` via `subprocess`.
- One behavior per test. No loops or conditionals inside test bodies. Descriptive test names.
- Red → green inside a layer: write the failing test, then the code, in the same PR.
- `xfail` only as a **static** marker, and only when a later, already-planned layer removes it.

## 5. Evidence integrity

- Any output shown in README/docs is captured from a real run — never hand-written, never edited.
- Never claim tool behavior without a verifiable source.
- Never commit scratch/helper/temp files. Temp work lives outside the repo.

## 6. Releasable layers

- Every layer passes `uv run pytest` and `trunk check` before submission.
- No `NotImplementedError`/`...` stubs above the skeleton layer (PR 8). Nothing is "deferred" without closing its issue with a reason.

## 7. CI and reviews

- Workflows trigger on unfiltered `pull_request` (+ `push` to main) so **stacked** PRs get checks.
- When addressing PR reviews: handle inline/diff comments as well as conversation comments; reply to each; resolve threads; then `gt absorb` + `gt submit --stack`.
- UI-changing PRs include before/after recordings (agent-recorded, or ask the user to record).

## 8. Decisions

- Significant tool/design choices get an ADR in `docs/decisions/` (MADR template, sequential numbering), in the same PR as the decision, listed in the index.
