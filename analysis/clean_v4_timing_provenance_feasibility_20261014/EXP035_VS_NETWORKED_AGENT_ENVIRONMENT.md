# EXP-035 environment versus networked real-agent environment

EXP-035 V2 built a Python OCI image from a digest-pinned base, froze final image digest `sha256:f8cddd76e34aed0e04ee3f41a958a213cf72f6658996beb41888418101a41040`, recorded source/config/runtime identity, and executed read-only with network disabled. Its manifest and per-run records link environment, task, execution, candidate, oracle verdict and clock endpoints. The unchanged H1 check passed 3/3. This was a deterministic provenance control, not an agent/provider experiment.

The existing V4 runtime records Python/platform/OS/OpenSSL/GCC/Docker strings and hashes frozen code/config inputs, but no final OCI digest. It retains the task artifact digest, transcript and terminal result. It therefore captures execution identity without the immutable environment link and has H1=0/12.

Reuse: base-image digest pinning, multi-stage build discipline, manifest-before-run, runtime/source/config/task/oracle hashes, read-only filesystem, stable run IDs, candidate/result binding, and unchanged H1 checker. Change: the live agent must have constrained provider egress; the environment cannot remain network-disabled. Add provider transport capture, transport retry accounting, route policy, and monotonic boundary values. Mount task inputs and generated code under explicit read/write mounts. Keep oracle grading local where possible and separate from model/provider network.

Before use, verify the actual EXP-035 image digest with offline local image inspection where available; a manifest digest alone is a recorded identity, not proof that a local image is present. Its frozen design remains evidence of feasibility for local deterministic H1, not proof that the same image can execute a live hosted model call.

