# H1-R3 retained-output oracle replay

This locally staged package contains the 852 confirmatory sessions: 768 representation trials, 64 noise controls and 20 abstention controls. The 821 accepted predicates comprise 801 exploit recoveries and 20 correct abstentions; the other 31 sessions were rejected. Abstention is a different task predicate.

Run with Python 3.10+ and its standard library, without API credentials:

```sh
python3 replay.py --report /tmp/h1r3-replay-report.json
```

The replay first checks the complete SHA-256 file manifest. It then runs the original independent reference adjudicator on each retained output, using the original public observations and private synthetic fixture state. It also rechecks certificate file bindings, current/legacy source qualification, prompt hashes and the presence of each retained program in its provider response. Missing outputs in rejected sessions stay missing. Programs, prompts, provider responses and evidence records are byte-preserving copies. The original reference and source-policy implementations are included unchanged.

Only paths in temporary copies of the reference bundle and certificate are relocated. Their recorded hashes and other fields remain unchanged. The oracle calculates predicates before comparing them with stored verdicts; stored verdicts do not supply its answer. Hash agreement checks retained integrity, not authenticated historical provenance or actual enforcement of an isolation assertion in a stored record.

This is retained-output re-adjudication. It does not execute the generated programs again, regenerate a hosted model's responses, prove exclusive acquisition, or establish immutable model identity. Generalization subdirectories are excluded because they are not additional members of the 852-session census.

This package includes synthetic fixture secrets intentionally so the independent oracle can check outcomes. It also preserves original local paths, execution identities and provider metadata. It is a LOCAL REVIEW CANDIDATE: it has not been published, anonymized, licensed for public redistribution or independently evaluated. Do not describe it as an anonymous public artifact. A public release needs a separate, traceable anonymization and distribution review; never silently alter the originals or retain stale file hashes after redaction.
