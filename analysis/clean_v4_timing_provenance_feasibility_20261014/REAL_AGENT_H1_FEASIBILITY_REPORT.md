# Real-agent H1 feasibility report

## Verdict

**FEASIBLE WITH MATERIAL PROVIDER/IDENTITY LIMITATIONS — APPROVAL REQUIRED.** The unchanged H1 checker requires source, configuration, task instance, immutable local environment, execution identity and retained result linkage. It does not impose an immutable proprietary provider-weight requirement. The existing checker specifically excludes `immutable_backend_weights` from its H1 conjunction. Do not interpret a pass as hosted-model reproducibility.

A networked real-agent runner can satisfy H1 if a digest-pinned local OCI runtime executes the frozen harness, task, tool sandbox and verifier; run records bind the digest, config, task, identity and result. Provider egress must be explicit and bounded. A network-disabled EXP-035 image cannot itself call APMIX unchanged.

V4 currently fails H1 on immutable environment identity: it retains host/runtime fingerprints but no content-addressed runtime digest. EXP-035 demonstrates the unchanged criterion using three deterministic local executions. However, its v2 manifest still says `execution_status=FROZEN_NOT_LAUNCHED`, while the retained run records, H1 check, validation report and active successor lock show 3/3 completed. This is a provenance metadata contradiction in the control package; it does not change the H1 field checks, but should be disclosed and resolved by a versioned administrative record before reuse. No hypothetical real-agent H1 outcome is asserted.

The practical design is technically viable with narrow egress and full HTTP exchange capture, but provider response generation and model weights remain outside the locally content-addressed boundary. A successful H1 result would establish the retained local source/config/task/environment/execution/result link, not deterministic hosted inference, provider immutability, or replayability of the backend.

