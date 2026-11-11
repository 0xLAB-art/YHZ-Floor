# Recheck: the two AGENT_GIVEUP sessions of Amendment 3 are transport truncations

**Scope.** Post-hoc offline recheck (zero model calls, zero network, zero
changes to registered verdicts), following the Amendment-3
null-decomposition audit precedent and extending the Amendment-4 transport
decomposition
(`../external_admission_amend4_frontier_20261106/FINDING_TRANSPORT_DECOMPOSITION.md`)
backward to this namespace's raw provider bodies.

**Method.** Every raw body in `sessions/raw_provider_responses/` (310 files)
re-parsed under its actual schema — OpenAI chat.completion
(`choices[0].message.content`, `finish_reason`) — and cross-tabulated against
the terminal statuses in `results.jsonl`.

**Results.**

- 310 calls: 299 `finish_reason: stop` (complete), 11 `finish_reason:
  length` — **zero empty-content calls** (this route served visible text on
  every call; the free/ OpenAI-chat route did NOT have the Amendment-4
  empty-completion artifact).
- The 11 length cuts all carry PARTIAL text (7.8k–11.9k chars, all at
  exactly 4096 completion tokens — the route's cap) and all sit on
  `almost_xor` / `another_xor` R0 — the registered near-solve zone.
- **Both AGENT_GIVEUP sessions (2/168) are length-cut turns whose JSON was
  truncated mid-string: no parseable submission existed to give up.** Under
  the taxonomy Amendment 5 registers, these are COMPLETION_TRUNCATED
  (provider-side), not agent behavior. Same misclassification class as
  Amendment 4's 108 give-ups, 106 sessions smaller.
- ORACLE_FAIL (145) and TIMEOUT (9) sessions are text-bearing throughout;
  the 103 crashes the null-decomposition audit surfaced remain task-side
  program failures, unaffected by this recheck.

**Consequence.** Amendment 3's registered verdicts stand unchanged. The
status-taxonomy correction (AGENT_GIVEUP can be transport truncation)
applies to 2 of this panel's 168 sessions and to 108 of Amendment 4's 168;
the paper's decomposition story gains one sentence of generality: the
give-up class is route-contaminated in BOTH frontier waves, not only the
messages-facade one.

**Reproduction.**

```
python3 - <<'EOF'
import json, glob
from collections import Counter
cuts = []
for p in glob.glob('sessions/raw_provider_responses/*.json'):
    d = json.load(open(p)); ch = d['choices'][0]
    cuts.append((ch.get('finish_reason'), len(ch['message']['content'] or ''),
                 d['usage']['completion_tokens']))
print(Counter(f for f,_,_ in cuts), 'length-with-text:',
      sum(1 for f,c,_ in cuts if f=='length' and c>0))
EOF
```
