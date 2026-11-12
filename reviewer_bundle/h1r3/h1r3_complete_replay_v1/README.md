# H1-R3 complete program replay candidate

This local review candidate adds fresh program execution to retained-output adjudication. It does not regenerate hosted-model responses. Original evidence remains in the separately manifested retained/ directory.

Requirements: Linux, Python 3.10+, bubblewrap (bwrap), util-linux (prlimit), and permitted unprivileged user/mount/network namespaces. No API credentials or third-party Python packages are needed. Do not disable the sandbox when namespaces are unavailable; report the infrastructure limitation instead.

Extract the archive, enter its directory, and run:

```sh
python3 -B retained/replay.py --report /tmp/h1r3-retained-report.json
python3 -B execute_replay.py --root retained --output /tmp/h1r3-fresh-replay
```

The fresh-output directory must not already exist and must be outside retained/. Each session gets one source-admission check and each admitted program one execution, without retries or replacements. The sandbox mounts the Python runtime, exact program and public observation file. It does not mount the artifact tree, private fixture state, prompts, responses, original output or verifier. The independent oracle uses private truth only after the child terminates. Network, PID, IPC and user namespaces are separated; public files are read-only; CPU, memory, descriptor, file-size and wall-clock limits apply. Tests probe host-file exclusion, read-only public input and host-loopback separation. These describe the NEW replay, not historical enforcement or exhaustive kernel protection.

The unchanged original independent oracle reconstructs the relation and checks fresh outputs against synthetic target truth before comparison with recorded verdicts. Relocated historical certificates check retained-file integrity; they do not attest the new process. Fresh source/input hashes, stdout/stderr, parsed outputs, oracle verdicts and runner hash are retained separately. Syntax rejection is not counted as execution.

Observed: 852 session decisions, 851 admitted/executed programs, 849 zero-exit object outputs, 2 recurring execution failures and 1 recurring syntax rejection. Cryptographic checks give 801 recoveries, 20 correct abstentions and 31 rejections, agreeing with all 852 retained verdicts. The 28 completed but incorrect recoveries remain failures. Repeat execution does not enlarge the original model cohort or establish equivalence at other levels, routes or models.

Original file bytes, synthetic fixture secrets, local paths, execution identities and provider metadata are preserved. This is a LOCAL REVIEW CANDIDATE, not a published anonymous artifact. Redaction, licensing and publication remain separate work. No independent benchmark validation is included. Validation reports accompany the delivery outside the immutable package.
