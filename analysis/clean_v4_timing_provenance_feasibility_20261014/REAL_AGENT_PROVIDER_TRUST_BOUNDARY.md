# Real-agent provider trust boundary

## Option A: digest-pinned agent container with narrow provider egress

The runner, task, oracle and local tool execution can be digest-pinned and identified. Permit egress only to the required provider endpoint through an allowlisted route, with DNS/TLS policy and request logging. Retain provider/model label, request body hash, response bytes/hash, timestamps and transport attempt IDs. This exposes the execution container to network access; it is not network-isolated. The hosted service and weights remain mutable and are not content-addressed locally. H1 can still pass because provider immutability is not a frozen H1 gate.

## Option B: pinned agent container plus separate pinned proxy

The agent container can address only a controlled proxy; proxy image, policy, configuration and logs are separately pinned and retained. The proxy becomes part of the execution trust boundary and adds network hop/queue/retry behavior. Record both proxy and agent digests and define whether proxy time is included in T_M (it ordinarily is if the agent waits for responses). The provider backend remains external and mutable. The H1 checker accepts additional environment evidence but must bind the agent environment and all relevant source/config/result identities; it does not certify proxy correctness automatically.

## Option C: provider relay with captured request/response spool

A local or separately deployed relay can capture exchanges while preserving the existing API protocol. The relay may be pinned; transport errors and retries must be logged as provider request attempts rather than collapsed into model turns. If the relay replays stored outputs, it is a mock/replay contract test, not a real-agent inference observation. A live relay still cannot pin hosted backend weights.

## Required clocks and identities

Define a session as schedule identity through terminal closure; a provider request attempt as each HTTP attempt; a model response as the response associated with a particular attempt; agent code attempts as submitted-code execution; oracle attempts as each grading exchange; terminal outcome as one census item. Record independent IDs for each and do not call one scheduled cell one provider request. T_M should include provider wait and local orchestration if the named interval is agent-session time; retain monotonic start and stop values plus duration and session binding.

Internal retries in the current clean V4 records are not observable: model-turn records aggregate spans and do not retain transport attempt IDs. No evidence establishes zero HTTP retries. Any prospective protocol needs retry limits and attempt-level logs.

