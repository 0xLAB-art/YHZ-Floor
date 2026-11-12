# C3 target-interface qualification

Two local target images were absent under the frozen card names, so they were
built under new qualification tags without modifying the frozen cards or
historical results.

| Target | Qualification tag | Observed image digest | Frozen card digest | Smoke result |
|---|---|---|---|---|
| TLS hybrid policy | `acts-lab/tls_policy_hybrid:qualification-20261018` | `sha256:b4961e031d7c234131e405961d9d97d841b6ab24ad4ebddd2ac5f386c644059e` | `sha256:a4f7d0fa795c089b2e5353d5d978d48242321d7fb13a5a435314ee0f3aadb0f5` | health, `/params`, and `/exchange` passed |
| SSH weak algorithm | `acts-lab/ssh_weak_algo_negotiation:qualification-20261018` | `sha256:6922954178e477e20f1540fedd034e054e25fc4fe8896d70f925a7a9802e2648` | `sha256:3eddacb703ca629756d74fc652d6a8335abe4d8a4b0f3fd8b50fd35a09baadc7` | health, `/params`, and legacy `/exchange` passed |

The smoke checks used only synthetic local values and did not invoke a model,
the reserved oracle, external services, or a portable secret manifest. The
different image digests invalidate direct equivalence to the frozen cards;
therefore no model-backed C3 result is added from this qualification. The
next legitimate C3 arm requires a new frozen image/relay/oracle bundle and
must retain the historical cohorts separately.
