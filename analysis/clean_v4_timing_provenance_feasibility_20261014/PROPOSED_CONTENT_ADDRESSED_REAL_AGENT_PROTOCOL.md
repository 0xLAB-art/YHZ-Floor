# Proposed content-addressed real-agent protocol

**NOT APPROVED**  
**NOT EXECUTED**

## Objective and boundary

Test whether a real-agent session can satisfy the unchanged H1 link across frozen local source, configuration, task instance, digest-pinned OCI runtime, unique execution identity and retained result. A pass would not imply immutable hosted weights or reproducible provider responses. This protocol is a design only; it creates no experiment registration or result.

## Freeze before launch

Freeze one provider route and requested model label; task card, instance, prompt, sampling, token budget and tool schema; source tree and runner; local oracle; OCI base and final digest; read-only/write mounts; proxy/egress policy; retry and timeout semantics; run-ID schedule; and unchanged H1 checker hash. Publish manifest and sidecar before any model request. Use exactly one unique scheduled run per preregistered cell and preserve every terminal outcome.

## Event units

Count and retain separately: scheduled session; provider HTTP attempt; provider response; model turn; agent code submission/execution; oracle request/attempt; terminal session result. Assign stable IDs and parent links. Instrument a maximum transport retry count of zero or a preregistered fixed bound; record every failed and successful HTTP attempt, including status, time, request/response hash and retry reason. Do not treat the schedule's one-cell rule as a one-request guarantee.

## Runtime and network

Use a read-only digest-pinned agent OCI image with only explicit writable scratch/output mounts. Permit only the provider endpoint through an allowlisted proxy or constrained egress policy. Record the agent image digest, proxy image/config digest, DNS/TLS/route policy, provider endpoint, timestamps and all exchange envelopes. Explicitly describe the runtime as networked. Do not claim the provider backend or weights are content-addressed.

## Verification and clocks

Run the unchanged H1 checker over each run record. Retain raw monotonic start and terminal readings as well as their difference, both bound to run ID and terminal event. The interval starts at first retained agent execution after provisioning and ends at terminal/session close. Keep oracle operation spans and model-turn latency separate. Retain task-specific oracle request, submitted candidate digest, verdict and terminal classifier inputs.

## Stop and reporting

No replacement cells, adaptive prompts, fallbacks or post-observation fixes. Technical failures remain in the census. Do not estimate task capability from 1–2 qualification sessions. Any protocol modification after freeze requires a new versioned protocol and separate review. Do not execute without explicit approval and separate arm registration after design acceptance.

