# PREREGISTRATION — P015: cross-family transfer of the information contract on the AES-GCM fixture

**Namespace:** `sp2027/research_execution/info_contract_aesgcm_apinex_20261102/`
**Date:** 2026-11-02 · Written before any experiment call under this protocol.
**Status:** registered; runner SHA-256 in `_REGISTRATION.json`, asserted by the
launch wrapper. Label reachability is established by a metadata inventory probe
plus an off-fixture smoke call, both recorded and both counted as **no** session.

## 1. Question this cohort answers

Every cohort so far — ChaCha20 (P010), ECDSA (P012), AES-CTR (P013), RC4 — ran
on one route, and P014 (AES-GCM) runs on the same route as P010/P011. The paper
therefore states transfer as an open hypothesis, not a result. This cohort asks
the smallest honest version of the transfer question:

> On an authenticated-encryption fixture whose reuse is public and whose
> load-bearing premise is secret content, does withholding the premise strand
> the agent on models from a **different provider family**, or is the effect a
> property of one route/label?

It is a **replication test of the mechanism at new labels**, not a capability
rate estimate, and it is not pooled with any prior cohort.

## 2. Labels, chosen from a measured inventory

`research_execution/labels_probe_20261102.json` (metadata-only `GET /v1/models`,
no experiment call, no key material recorded) was run before this document.
It returned 3 ids on AgentRouter, 44 on APINEX, and 0 on APMix. The registered
labels are the two APINEX families furthest from the AgentRouter reasoning route
that also returned text in the off-fixture smoke probe
(`smoke/labels_smoke_20261102.json`):

| label | family | registered |
|---|---|---|
| `claude-opus-5.5` | Anthropic-format chat | yes |
| `gemini-3.1-pro` | Gemini | yes |

If a label fails the smoke probe it is **dropped before launch and disclosed as
dropped**, never silently replaced; a replacement label would require an
amendment written before its first call. `APINEX_LABEL_MODEL` must name one
registered label; the wrapper refuses any other string.

## 3. Design (frozen, copied from P014)

- **Runner:** `run_info_contract_2x2_aesgcm.py`, byte-identical to the P014
  runner (SHA asserted against `_REGISTRATION.json`). Fixture, cells, slots,
  oracle, policy, sandbox, event log and summary schema are unchanged.
- **Cells:** C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−). B− withholds only
  the *content* of the reference record.
- **Seeds:** 501–516 per label — fresh, no overlap with 41–44, 81–84, 101–118,
  121–136, 141–156, 161–176, 181–196, 201–208, 211–218, 221–228, 301–332,
  401–416. Four balanced Latin squares, rotation = seed index mod 4.
- **Sessions:** 4 cells × 16 seeds = 64 per label, 128 registered total; ≤2
  turns, one provider call per turn, max_tokens=1400 requested.
- **Isolation:** one process and one namespace directory per label
  (`<slug>/results.jsonl`); no label shares a results file or an analysis.
- **Provider failures are terminal per session** — never retried, never
  imputed; consecutive provider failures halt that label's launch.

## 4. Disclosed transport deviations (APINEX route)

1. **Shape.** APINEX serves OpenAI `/v1/chat/completions`, not Anthropic
   `/v1/messages`; the runner's prompt is sent as a single user message and the
   raw OpenAI body is stored verbatim for audit.
2. **Temperature omitted** (provider default), matching the frozen rule. The
   older P010L5 adapter pinned 0.2; this one deliberately does not.
3. **Token floor 2800** uniform across cells and sessions, recorded per call as
   `max_tokens_sent` alongside the runner's `max_tokens_requested_by_runner`.
4. **Browser User-Agent** required by the route's edge filter.
5. **Timeout default 600 s** (the runner passes none).

Everything else — prompt bytes, slot sentences, fixture bytes, oracle, feedback
strings — comes from the frozen runner untouched.

## 5. Analysis plan (frozen before any call)

Per label, reported separately, never pooled:

- **Primary:** paired C1-vs-C4 discordance on shared seeds, exact binomial
  two-sided, with the full discordance count and the **evaluable-pair**
  denominator rather than the registered one.
- **Secondary (descriptive, prespecified):** per-cell acceptance with
  submissions/turns; premise marginal (C1+C3 vs C2+C3) and naming marginal
  (C1+C4 vs C2+C3), Fisher exact one- and two-sided; provider-dropout counts by
  cell, disclosed as a denominator effect.
- **Transfer statement:** the two labels are compared to each other and to the
  P014 label as a **descriptive table of direction and magnitude**, with no
  pooled estimate and no new significance claim across cohorts. A label whose
  C1 is at ceiling and whose C2 is at floor is reported as "direction
  replicated"; anything else is reported as "direction not replicated on this
  label", with the cell table shown either way.

**Falsifiers (prespecified):**
- **F1 stated-arm ceiling:** C1 below 12/16 on a label ⇒ instrument-difficulty
  result for that label, not a premise result.
- **F2 naming gates:** C3 materially below C1 ⇒ naming still does work.
- **F3 derive frame:** C2 near C1 ⇒ success without the premise; on a
  hidden-premise fixture that is a real negative and is reported as one.
- **F4 cross-family divergence:** if the two labels disagree in direction, the
  transfer claim is withdrawn and the divergence itself is the finding.

## 6. Discipline

Cost expectation ≤ $10 for 128 sessions (prior 64-session cohorts were
$0.39–$0.43 on AgentRouter; APINEX pricing differs and is recorded per call).
Every call's tokens/cost is appended to `sp2027/research_execution/
BUDGET_LEDGER.jsonl`. Leak scan over every prompt file before analysis: the
per-seed secret and the record content may appear in zero prompts other than
the premise sentence of the stated arms. No cross-cohort pooling; no
mid-cohort peeking that would change the design.
