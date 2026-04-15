# PawPal+ Model Card

## 1. System overview

PawPal+ is a pet-care planning assistant. It combines:

- a deterministic scheduler (`Owner → Pet → Task → Scheduler`),
- a retrieval-augmented Q&A feature grounded in 15 curated pet-care snippets,
- a "plan → act → check" review agent that audits a day's schedule and flags
  issues that survive deterministic validation,
- guardrails + logging + an 8-check offline reliability evaluator.

**Model used:** `claude-haiku-4-5-20251001` via the Anthropic API.
**Tasks performed by the model:** (a) grounded Q&A from retrieved snippets,
(b) structured JSON enumeration of schedule issues.

The model does **not** mutate user state. It produces text that the UI
displays; the human pet owner remains the sole actor on the schedule.

## 2. Intended use

- **In scope.** Household-level pet-care planning: remembering tasks, spotting
  same-time conflicts, suggesting rearrangements grounded in general best
  practices (exercise duration, feeding cadence, grooming, enrichment, etc.).
- **Out of scope.** Veterinary diagnosis, dosing decisions, emergency care,
  nutrition plans for pets with medical conditions, training disputes. The
  system prompt explicitly refuses medical advice and redirects to a vet.

## 3. Limitations and biases

- **Corpus bias.** The 15 snippets reflect mainstream US/European pet-care
  guidance (ASPCA / AVMA / AAHA style). Species coverage skews dog-heavy,
  followed by cat, with only one bird-focused snippet and nothing for
  reptiles, rabbits, rodents, or fish. Answers about underrepresented
  species will trigger the "no relevant guidance" path rather than a
  hallucinated one.
- **Units and locale.** Snippets use metric (°C, kg) with some imperial
  parentheticals. A user phrasing in Fahrenheit-only may or may not trigger
  the right retrieval; the `walk-weather` snippet contains both.
- **No individual-pet context.** The model has no memory of a specific pet's
  history, breed, age, medication list, or medical conditions. Advice is
  generic and may be inappropriate for an individual animal.
- **Retriever is keyword-based.** Paraphrased or highly idiomatic queries
  (e.g. "my pup is driving me bananas at night") may miss obvious topics.
  Tests catch the canonical cases; long-tail queries may fail silently.
- **Confidence scores are heuristics, not calibrated probabilities.** The
  0.0–1.0 number is a product-level signal (did retrieval find anything?
  did the answer cite its sources? did the validator accept the claims?),
  not a statistical confidence.

## 4. Misuse and mitigations

| Risk | Mitigation |
|---|---|
| User treats answers as veterinary advice | System prompt forbids medical advice; README + UI state "not a vet"; missing-context path says so explicitly rather than guessing. |
| Prompt-injection ("ignore all previous instructions…") | `sanitize_user_text()` blocks a small set of high-signal patterns before any LLM call. Input also capped at 2,000 chars. |
| Secret leakage via pasted text | Same guardrail blocks `api_key:`, `secret:`, `token:` patterns. |
| Hallucinated schedule conflicts | The agent's ACT step emits JSON; the CHECK step rejects any `conflict` claim whose `target_time` doesn't match a real `HH:MM` collision in `Scheduler.detect_conflicts()`. Rejected claims never render. |
| Over-trust in agent output | Every AI response carries a confidence score and source list in the UI; the review agent never mutates state — the human confirms. |
| Resource abuse / bill shock | Guardrail length cap + `max_tokens` cap on every call (400 for Q&A, 500 for agent); Haiku tier keeps per-call cost low. |

What I consciously *didn't* build: a full content-moderation pipeline. This
is a personal scheduling assistant, not a public-facing chatbot, so layered
moderation tooling would be over-engineering.

## 5. Testing + what surprised me

- **51 tests pass** across the scheduler, retriever, guardrails, agent
  validators, and evaluator. Run in ~0.2 s, no network required.
- **Evaluator score: 8/8 canonical checks pass.**
- **Surprise #1.** When the retriever returned *no* snippets, Claude still
  sometimes tried to answer from its own priors. Adding one sentence to the
  system prompt ("If the context does not contain the answer, say so plainly
  and recommend asking a veterinarian") was the single highest-impact fix I
  made during testing.
- **Surprise #2.** The agent's JSON output was wrapped in prose about 20% of
  the time ("Sure! Here's the JSON you asked for:\n\n{...}"). The tolerant
  `_extract_json` regex is *not* a nice-to-have — it's what keeps the agent
  from throwing on every fifth response.
- **Surprise #3.** The deterministic CHECK step quietly rejected a
  hallucinated "conflict at 13:00" on my very first test run, even though
  the real conflict was at 08:00. The model had absorbed the idea of
  "conflicts exist" and generalized it to a random time. This is exactly
  the failure mode the agent is designed for — and the validator caught it
  without me writing a single extra line.

## 6. AI collaboration during this project

I used Claude (the same model family this app calls) throughout the build.

**Helpful suggestion.** When I was designing the agent's CHECK stage I asked
Claude "should I validate the agent's claims or trust them?" It argued
strongly for validation and proposed the `kind → validator` dispatch pattern
that the code ended up using. That one suggestion drove the whole
"plan → act → check" structure; without it the agent would have been a
glorified prompt wrapper.

**Flawed suggestion.** When I asked Claude to draft the retriever, it
proposed using `sentence-transformers` for cosine similarity over the 15
snippets. For a corpus that small, that would have added ~400 MB of torch
dependencies for zero quality win over a tag + keyword scorer. I rejected
it and wrote the deterministic retriever instead. The tradeoff Claude
missed: deployment / test / CI simplicity beats model sophistication when
the corpus is this small. (I also appreciated that when I pushed back,
Claude immediately agreed and suggested the TF-style approach — this is
the pattern I see repeatedly: the model proposes the fancier option first,
and the human has to weigh simplicity.)

## 7. What I'd change with more time

- Persist the `Owner` graph to SQLite so sessions survive restarts.
- Widen the corpus to 40–60 snippets with better species coverage (rabbits,
  reptiles, seniors-by-breed). Add source citations on each snippet.
- Swap the keyword retriever for a hybrid lexical + embedding retriever
  once the corpus is large enough to benefit.
- Add duration-aware conflict detection (08:00 + 30min overlaps 08:15) to
  the Scheduler and expose it to the agent's validators.
- Capture a small golden set of "good schedule / bad schedule" pairs and
  track agent precision/recall across model versions as a real eval.
