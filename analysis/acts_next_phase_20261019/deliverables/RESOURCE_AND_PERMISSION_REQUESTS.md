# Resource and Permission Requests — ACTS-Attack

**Phase:** `acts_next_phase_20261019`
**Date:** 2026-10-20

Only *genuinely blocking* items are listed. Items that are **not** blocking, and
items that were deliberately **not** requested (with the reason), are recorded
in §4 so that the absence is itself documented rather than silent.

---

## 1. R-1 — Install `in-toto` 3.1.0 into an isolated virtual environment
**Blocks:** Objective 3 (the empirical part).
**Status:** ☐ NOT YET APPROVED — **request awaiting the user's decision.**

**What is requested (exactly, and nothing more):**

```
python3 -m venv sp2027/analysis/acts_next_phase_20261019/stage2_provenance/venv
sp2027/analysis/acts_next_phase_20261019/stage2_provenance/venv/bin/pip install \
    "in-toto==3.1.0"
```

* The venv is created **inside this phase's own directory**; the main
  project's dependencies are **not** modified.
* `in-toto` is the **only** real provenance implementation that is genuinely
  comparable as a *verdict* comparator (see
  `deliverables/REAL_PROVENANCE_BASELINE_COMPARISON.md` §1). slsa-verifier and
  cosign are `NOT_COMPARABLE` and are not requested.
* After installation, all `in-toto verify` runs are **offline** (in-toto's
  layout verification is offline by design; no transparency-log or TUF
  interaction is required for a locally generated key and a local layout).
* The installed distribution's version and the SHA-256 of the resolved
  `in_toto` package directory will be recorded in the results.
* **No credential, no account, no third-party service, and no write outside
  this phase's directory is required.**

**What it unblocks (precisely, four steps):**

1. Install the pinned version into the isolated venv and record its digest.
2. Translate the **frozen** 58-case IAR-B held-out corpus (already in the
   repository, unmodified) into in-toto links and layouts.
3. Run `in-toto verify` offline on the translated corpus, capturing raw
   verdicts.
4. Compare in-toto's verdict with (a) the **frozen** Stage01 production verdict
   and (b) the Stage 1 `full` verdict under **one declared common contract**,
   with every shared guarantee marked `N` and every custom construction marked
   `[CUSTOM-INSPECTION]`.

**If declined:** Objective 3 remains `BLOCKED_BY_RESOURCE_OR_AUTHORIZATION` for
its empirical part, with the design portion `PARTIALLY_ESTABLISHED`. No
consequence for Objectives 1, 2 or 4.

---

## 2. R-2 — Model-provider authorisation for the Stage 4 AI-vs-scripted arm
**Blocks:** Stage 4 (and any residual AI-specific claim).
**Status:** ☐ NOT YET APPROVED — **request awaiting the user's decision.**
**Note:** this is a *request for authorisation*, not a request to spend money.
The programme will make **zero** calls unless every one of the seven
confirmations below is answered affirmatively.

The seven confirmations that must all be given before **any** provider call:

1. **Provider authorisation** — is `https://api.apmix.ai` authorised for use
   from this environment for this experiment?
2. **Model identity** — the repository records the route as
   `claude-sonnet-4-6-free` at `provider_adapter.py:19`. The independent
   auditor could **not** re-derive the catalogue facts (the catalogue tool was
   unavailable and calls are forbidden). Confirm the exact model identifier
   that the route resolves to, and that it is the intended one.
3. **Spending limit** — a free tier only; a hard ceiling in calls and in
   tokens.
4. **Maximum call count** — the number of calls the Stage 4 design may make.
   The design's attempt budget is specified in
   `stage4_arms/STAGE4_ARM_STATUS.md`; note the sibling tree
   `acts_next_phase_20261019_v2/` has **already run a 14-call model arm** on
   this route, which is a budget fact, not an authorisation.
5. **No paid fallback** — confirm the client must fail closed rather than
   route to a paid model.
6. **Sampling controls** — confirm which of `temperature`, `seed`, `top_p` are
   honoured. If `seed` is unavailable, one submission is not a fixed function
   of the prompt, and the design must be reported accordingly.
7. **Prompt and output retention policy** — confirm what the provider logs or
   retains, and that raw credentials are never printed, transmitted to an
   unrelated system, or stored in a research artefact.

**Additional binding rule carried over from Stage 3:** both arms (scripted and
model) must use an **identical transport**. A design in which one arm goes
through a gateway and the other does not would confound transport with the AI
factor and would not be interpretable.

**If declined:** Stage 4 stays `BLOCKED_BY_RESOURCE_OR_AUTHORIZATION`; the
AI-specificity claim stays unsupported; the Stage 1 and historical H1-R3
evidence stands unchanged (the H1-R3 composer was **scripted** and the Stage 1
composer is **also** scripted, so neither supplies AI evidence).

---

## 3. Items deliberately NOT requested, and why

| Item | Why not requested |
|---|---|
| **`slsa-verifier` 2.7.1** (Go binary) | `NOT_COMPARABLE` as a verdict comparator (it verifies only SLSA-generator GHA/GCB provenance; `verify-artifact` needs `--source-uri`; trust material is a network TUF/Rekor dependency; the project is unmaintained; v2.7.1 parses only v0.2/v1.0 predicates). The narrow `verify-vsa` mechanism demo is optional and strictly lower value than R-1. |
| **`cosign` 3.1.3** | `NOT_COMPARABLE` — a transport-and-signature layer with no step, join, inspection, ladder, attempt, or target-state concept. A binary would only be needed for the publication direction, which is not a comparison. |
| **An authorised submission gateway** | Stage 3 applied a six-point qualifying test to 14 candidate ingresses; **0/14** pass "identifiable owner and authorisation". The finding is `NO_AUTHORIZED_REACHABLE_INGRESS_IDENTIFIED`. Requesting one would in effect mean asking to *create* a gateway, which the brief explicitly forbids ("a deliberately weakened replacement gateway is not sufficient", "a locally constructed certificate passed directly to a validator is not sufficient"). Asking would also be a category error: it would seek permission to manufacture the very artefact the study is looking for. **The gap is documented instead.** |
| **`secp256k1` / `ecdsa` Python packages** | Not needed — the Stage 1 reference verifier imports the **frozen** `contract_sound_stage01_reference_verifier_v2.py`, which implements secp256k1 arithmetic itself. Installing a library would risk divergence from the frozen predicate for no benefit. |
| **`latexmk`** | Not blocking. The manuscript is a **protected artefact** and is not being rebuilt in this phase. |
| **Access to `preprints.org` 202610.0322 ("Grounded but Wrong")** | The site returned HTTP 403 on five attempts; OpenAlex supplied metadata and the abstract. This is a public-preprint fetch, not a gated resource, and no authorisation would change the 403. The novelty comparison is therefore reported as **incomplete for that one work** (`deliverables/NOVELTY_PRIOR_ART_MATRIX.md` §6). |

## 4. Non-blocking environmental facts (resolved, not requested)

| Fact | Resolution |
|---|---|
| The working tree is on **fuseblk**, which reports every file as `0777` and silently ignores `chmod` | The vetted `protected_signing.load_private_key` **correctly refuses** such a key. Rather than weaken that check, the private keystore was placed **outside the repository** at `/tmp/acts_s1_keystore` (0700 directories, 0600 key files) and only the **public** bundle and the custody record live in-tree. Recorded as deviation **D-05**. |
| `latexmk`, `secp256k1`, `ecdsa`, `in-toto`, `slsa-verifier`, `cosign` are absent | Only `in-toto` is requested (R-1); the rest are either `NOT_COMPARABLE` or not needed. |
| No `gpt-5.6-luna` model exists in the available catalogue; the `openai/gpt-5.4-nano` and `openai/gpt-6-luna` routes fail on credits | All subagents in this phase were run on `openrouter/minimax/minimax-m3.1-flash:free` under an explicit user directive. The prior team used "GPT-5.6 Luna"; that is a historical fact, not a reproducibility claim for this phase. |
| `preprints.org` 403 | See §3. |
