# Finding: the 103 Amendment-3 crashes decompose into named agent-side causes — zero harness-caused

**Scope.** Post-hoc offline stderr-level classification of every crash-class
session (final submitted program rc != 0 among ORACLE_FAIL terminals) in
`results.jsonl`. Zero model calls; registered verdicts unchanged. Companion
to `FINDING_NULL_DECOMPOSITION.md` (which surfaced the 103) and
`FINDING_GIVEUP_TRUNCATION_RECHECK.md`.

**Census (103 crash sessions).**

- **48 UnicodeDecodeError** — fully mechanized, two sub-kinds:
  - **eps RT ×11 — RT decode-note priming:** the models `base64.b64decode`
    the task's own payload (a pure-ASCII binary-digit text, 1,545 B,
    `[01\r\n]+` verified) — the artifact is NOT base64; the RT prompt's
    registered DECODE NOTE ("decode it with base64.b64decode") primes the
    wrong transform onto the task data. Agent comprehension error under the
    registered representation — the same packaging-priming family measured
    in Amendment-1 (Makeshift RT 8/8 UnicodeDecodeError, workdir plaintext
    double-decoded).
  - **eps_part2 ×15 + babycrypto ×13 (+ almost_xor ×9 in part) — intended
    decode-path execution failures:** these payloads ARE base64-encoded
    (eps_part2 opens `RXZpbCBDb3JwLCB3ZSBoYXZl...` = "Evil Corp, we have
    delivered..."); the decode step is the correct solve path and the
    models' executions of it fail mid-way. Capability/execution, not
    confusion.
- **9 OverflowError, 7 TypeError, 4 AssertionError, 2 IndexError,
  2 NameError, 1 ZeroDivisionError, 1 AttributeError, 1 ValueError** —
  genuine program logic failures.
- **1 FileNotFoundError: 'words.txt'** (crack_me RT, deepseek) — the model
  assumed a wordlist artifact; the pinned crack_me release ships ONLY
  `challenge.json` + `README.md` (+ test_solver) and ships NO words.txt;
  the registered reference solver reproduces the pin without any wordlist.
  Hallucinated dependency — agent-side, NOT an artifact-completeness defect.
- **0 empty-stderr crashes; 0 sandbox/artifact packaging failures; 0
  harness-caused crashes.** The artifact files of the crash-heavy tasks are
  pure ASCII (eps mpeg 1,545 B `[01\r\n]+`; eps_part2 avi 1,136 B base64
  text; babycrypto 432 B base64 text; almost_xor 98 B) — the R0 verbatim
  embedding is faithful for every crashed task; the "binary artifact"
  hypothesis is refuted by the bytes.

**Consequence.** The paper's "103 terminal crashes" figure gains a complete
mechanical decomposition, all agent-side: RT-primed wrong-transform
confusion (11), intended-decode execution failures (37), logic failures
(54), one hallucinated dependency (1). No registered verdict changes; the
capability-floor reading of the Amendment-3 null stands with named causes.

**Cross-cohort packaging note (for §7's representation reading).** The RT
decode-note priming effect is now measured in BOTH admission cohorts
(Amendment-1 Makeshift RT 8/8; Amendment-3 eps RT 11) — the R0→RT
representation contrast partially measures decode-note priming, a real
packaging effect of the registered representation, alongside its intended
information-preserving delivery role.
