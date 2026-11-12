# ACTS-Attack research execution home

This directory is an additive orchestration layer. Frozen, historic, and raw
experiment artifacts remain outside this directory and are never rewritten.

The programme is attack-centered: attacker-visible information -> exploit
opportunity -> model inference -> candidate construction -> execution and
feedback -> independent oracle verdict -> workload, cost, provider, and
provenance limits. Catalog counts are discovery units, not physical trials.

The current status is `PARTIAL_EXECUTION`. This home records source-linked
audits and bounded next actions; it does not turn administrative checkpoints
into scientific completion.

Hard boundaries:

- exclude the invalid first H1 report from confirmatory interpretation;
- keep corrected H1 V2, historical V4 agent rows, fixed executors, CBC
  controls, policy controls, side-channel studies, and external benchmarks as
  distinct populations;
- preserve raw observations and append new interpretations;
- use only authorized local/synthetic targets and the configured provider
  route within the existing spend guardrails;
- never infer model capability from a deterministic executor or a provider
  route name alone.
