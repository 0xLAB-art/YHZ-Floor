# Finding: the Amendment-4 null decomposes into two measured transport layers

**Scope.** Post-hoc offline audit of the registered Amendment-4 artifacts
(freeze commit per `FREEZE_COMMIT.txt`; results `results.jsonl` and
`results_recovery_8400.jsonl`; 279 raw provider response bodies in
`sessions/raw_provider_responses/`). Zero model calls, zero network, zero
changes to the registered verdicts. Audit script:
`audit_transport_decomposition.py` → `AUDIT_TRANSPORT_DECOMPOSITION.json`
(schema `amend4-transport-decomposition-audit/1`).

## 1. Layer 1 — the "give-up" floor is an empty-visible-content artifact

`SUMMARY_AMEND4.json` records 61 primary-4200 and 47 recovery-8400 sessions as
`AGENT_GIVEUP` ("floor-exhausted"). The audit re-parsed every raw provider
body and cross-tabulates:

- **All 108 AGENT_GIVEUP sessions' 216 raw calls ended `stop_reason:
  "length"` with a visible content of EMPTY STRING.** The registered
  finish-reason pair is `('length','length')` for all 61 primary and all 47
  recovery giveups — 108/108 sessions, no exceptions.
- The gateway re-serializes an OpenAI-chat-style backend into the
  Anthropic-messages facade (every response id begins `chatcmpl-`). Under
  that facade, **hidden reasoning consumed the entire `max_tokens` budget
  before any text block was emitted**; the facade then returned
  `content=[{"type":"text","text":""}]`.
- Charged output tokens on the 220 empty-visible-content calls:
  **1,323,000** (`4200` or `8400` per call) — paid for zero visible content.
- **220 of 279 raw calls (78.8%) are empty-visible-content `length` cuts.**
  The remaining 59 have `stop_reason: "end_turn"` and text (266–2,614
  chars); essentially every program the panel measured came from those 59
  calls: 46 of the 48 ORACLE_FAIL calls and 13 of the 14 SUCCESS calls
  (plus 2 length-cut turns inside ORACLE_FAIL and 1 inside SUCCESS
  sessions that still reached a visible answer).

**Taxonomy consequence.** Under the registered taxonomy,
`AGENT_GIVEUP`/floor-exhausted reads as the agent declining to submit. The
measured mechanism is different: the route's hidden-reasoning budget
consumed the completion floor before any visible token; no agent decision
is observable. For the paper's reading this layer should be described as an
**empty-visible-content completion artifact of the transport**, not agent
behavior. The registered verdicts stand unchanged; this audit only certifies
what the Give-Up class actually measured.

**The one strong mock-replication: doubling the floor did not move it.**
8,400 tokens still ends `length` empty on 47 of 48 recovery sessions — the
hidden-reasoning run is not near-missed at 2×; the route's budget
interaction, not the token amount alone, is the binding constraint.

## 2. Layer 2 — the gateway content filter deleted 43% of the grid

- The events log (`sessions/events/events_amend4.jsonl`) contains **216
  provider-failure events, all `HTTP 400 content-blocked`** surfaced at
  `agent_router_api_error` — label-independent, task- and
  representation-specific.
- `CONTENT_FILTER_MAP.json` (registered with the run) maps them to **72 of
  168 grid slots (42.9%) silently erased**: `babycrypto` R0+RT and
  `eps_part2` R0+RT entirely on all three labels, plus `almost_xor` RT and
  `lowe` RT on all three labels (the base64 RT wrapper trips the filter on
  two further tasks). Those five (task, representation) denominators never
  existed.

## 3. One unrecorded disclosure

Recovery inventory: 48 terminal rows but **one orphan raw call** —
`gpt-6.1-sol / another_xor / R0 / seed_424 / rec8400` has a `length`-cut
response and no terminal row (its wave's records end at seed_423). Counted
in the audit as `UNRECORDED_SESSION` (1 call, length-cut, empty content);
never pooled into any cell.

## 4. What this changes (and does not change)

**Unchanged.** The registered verdict product (F1 not evaluable at its
grid; F2/F3 as regraded; C1 11 vs C2 24 acceptances; 57 retained programs;
5/57 arm-admitted) stands exactly as registered. Amendment-3's record is
likewise untouched.

**Changed reading.** The external panel's null has now three named,
measured components, none of which is pure agent capability at the
registered tasks:

1. the Amendment-3 layers (whole-stdout pin rejects 11 statement-faithful
   outputs; 103 crashes hidden by the taxonomy; benchmark-native
   first-flag-token shown more faithful);
2. **transport layer 1 (this audit): empty-visible-content completions
   under an Anthropic facade over an OpenAI-chat backend — 78.8% of calls,
   1,323,000 charged tokens, no visible text; misfiled as AGENT_GIVEUP;**
3. **transport layer 2 (this audit): gateway-side content filter erases
   42.9% of the grid's denominators before any measurement.**

## 5. Registered follow-up required before any new wave

Per the Amendment-3 audit precedent, a transport-fix wave is a **new
registered amendment** (Amendment 5), not an edit of Amendment 4. Its
design must, before the first evidence call (all pre-outcome): pin a
transport whose completions are visible (chat-completions with
`reasoning_effort` control, or an equivalent route attested at call time);
run a compat pre-gate over all 14 frozen prompts × registered labels
(fail → route rejected at freeze, the Amend-3 gate discipline that would
have caught layers 1–2); carry the CRASH class forward; keep the dual
C1/C2 codings and the two-sided provider-failure rule unchanged.

## 6. Paper-relevant one-liners (for the authors' own use)

- *"78.8% of the frontier panel's provider calls returned an empty visible
  completion under its transport — hidden reasoning consumed the whole
  completion budget and the grep-visible answer never arrived; the panel's
  108 give-ups are 108 measured transport artifacts, each charged in full."*
- *"The gateway's content filter deleted 72 of 168 registered slots (all of
  two tasks plus the base64 representation of two more) — 43% of the port's
  denominators never existed."*
- *"Doubling the token floor replicated the same empty result 47 times out
  of 48: the give-up class measures the route, not the agent."*
