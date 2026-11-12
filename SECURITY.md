# Security policy

This repository is an **evidence bundle for a security-measurement study**; it contains no production software, no live targets, and no secrets.

## What the retained programs are

Retained attack programs in `reviewer_bundle/h1r3/` target **local, self-contained fixtures** built for the study — containers with reserved secrets and a reference oracle on the same host. There is no reachable production target: the fixtures bind to loopback, carry no external endpoints, and the oracle ships alongside the program.

## Handling guidance

- Execute retained programs only inside the provided sandboxed replay (`reviewer_bundle/h1r3/h1r3_complete_replay_v1/execute_replay.py` uses bubblewrap + prlimit namespaces) or your own equivalent isolation.
- The synthetic fixture secrets and test signing keys shipped for evaluation are evaluation materials, not credentials to anything.
- Escrow-style secrets are revealed only after a verification attempt, mirroring the study's own protocol.

## What this bundle deliberately excludes

- No API keys or credentials: every runner reads keys from the process environment; a campaign-wide scan for key-shaped strings returns zero hits (the `sk-` matches are base64 coincidences inside provider `encrypted_content` blobs).
- No author-identity material: the direct-identifier scan reports 0 hits; rendered author fields are empty.
- No undeclared capability claims: the records are audit-only; nothing here grades an agent or enables one.

## Reporting

During double-blind review, report anything suspicious through the venue's submission system so it reaches the authors anonymously. After review, use the repository's issue tracker.
