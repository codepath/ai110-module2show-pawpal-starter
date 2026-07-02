# ADR-0004: pytest-bdd for behavior specs; real objects and AppTest only (no mocks)

- **Status**: accepted
- **Date**: 2026-07-02
- **Deciders**: USER, Claude
- **PR**: `test-bdd-framework`

## Context and Problem Statement

The rubric requires a pytest suite verifying system behavior. We also want tests that describe behavior the way a user experiences it, and a hard rule from module 1: tests must exercise **real** behavior — mocked internals repeatedly produced tests that passed while the app was broken.

## Decision Drivers

- Tests should read as user-level behavior (BDD) where that adds clarity.
- No mocks/fakes: logic tests drive real `pawpal_system` objects; UI tests drive the real app via Streamlit `AppTest`; the CLI demo is run as a real subprocess.
- The rubric's named artifact `tests/test_pawpal.py` must stay a plain pytest file graders recognize.
- Module-1 continuity (pytest-bdd + AppTest worked well there).

## Considered Options

1. pytest + pytest-bdd (Gherkin features for user-visible behaviors) + AppTest, no mocks
2. Plain pytest only
3. behave (separate BDD runner)

## Decision Outcome

Chosen option: **pytest + pytest-bdd + AppTest, no mocks**.

Layout:

- `tests/test_pawpal.py` — plain pytest, the rubric-named suite (core behaviors).
- `tests/features/*.feature` + `tests/step_defs/` — Gherkin scenarios for user-visible flows.
- `tests/test_app_ui.py` — Streamlit `AppTest` end-to-end UI tests.
- `tests/test_demo_cli.py` — runs `main.py` via `subprocess` and asserts on real output.
- `tests/conftest.py` — fixtures building **real** objects only.

Test rules (AGENTS.md rule 4): one behavior per test; no loops/conditionals in test bodies; static `xfail` only, removed by the layer that fixes it.

### Consequences

- Positive: green tests imply the real system works; Gherkin documents behavior; graders find the expected artifact.
- Negative: e2e tests are slower than mocked unit tests — acceptable at this scale (< a few seconds).

## Pros and Cons of the Options

### pytest + pytest-bdd + AppTest (chosen)

- Good: real-behavior guarantee, readable specs, single runner (`uv run pytest`).
- Bad: two styles of test to maintain.

### Plain pytest only

- Good: simplest.
- Bad: loses the executable, user-readable behavior specs that BDD gives.

### behave

- Good: pure Gherkin.
- Bad: second test runner and report stream; pytest-bdd gives Gherkin inside pytest.
