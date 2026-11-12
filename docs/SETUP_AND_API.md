# Setup & API configuration

Everything needed to point the runners at a model gateway and run a cohort.

## 1. Environment

- Linux, Python 3.10+ (the analyzers and gate are standard-library only; the runners need `requests` at most)
- No GPU, no database — records are flat files (`results.jsonl` per cohort)

```sh
python3 --version          # 3.10+
cd experiments/external_published_audit_20261110/
python3 -c "import json, hashlib, urllib.request; print('stdlib OK')"
```

## 2. API keys: environment only

**Never in files, never in git.** Every runner reads its key from `os.environ`:

```sh
export AGENTROUTER_API_KEY="sk-your-key-here"
python3 run_published_audit_sessions.py
```

The key is passed to the gateway as `Authorization: Bearer …` and is recorded nowhere — the per-call attestation stores the *model echo*, finish status, and token counts, never credentials. A sweep of the entire campaign tree for key-shaped strings returns zero hits (the `sk-` matches are base64 coincidences inside provider `encrypted_content` blobs).

## 3. Gateway behaviour you must know (measured, not assumed)

| Behaviour | Detail | Consequence |
|---|---|---|
| **Responses API only** | these model labels reject `/v1/chat/completions` outright ("please use /v1/responses") | the transport speaks `POST {base}/v1/responses` |
| **User-Agent required** | the gateway serves the Responses route behind a `claude-cli/2.0.0 (external, cli)` UA | the adapters set it; plain OpenAI-SDK calls without it fail |
| **Reasoning budget vs output budget** | `max_output_tokens` covers *hidden reasoning too* — a session can spend the whole allowance in reasoning with zero visible output | the allowance must be **declared and recorded** per cohort (the paper's headline finding) |
| **Temperature ignored** | the backend omits the field | runners never send it |
| **Content filter** | deterministic per task artifact, label-independent | filter-blocked tasks are *excluded from the scored set*, never scored as failures |
| **Slow-drip sockets** | connections hang mid-stream for 30+ minutes | every call runs under a hard 420 s wall cap (daemon thread + join) |

## 4. Per-call attestation (what every recorded call carries)

```json
{"model_echo": "gpt-6.1-sol",
 "finish_status": "completed",
 "usage": {"input_tokens": 1544, "output_tokens": 8120,
           "reasoning_tokens": 7340}}
```

The fingerprint audit re-checks every stored call echoes the registered label exactly (65/65 in the frontier cohort; 60/60 sessions landed in the M1 audit).

## 5. Budget and halt discipline

- Every cohort's registration states its query budget and token allowance **before the first call**.
- Budget rows append to `BUDGET_LEDGER.jsonl` (per-call cost estimates from the gateways' advertised rates).
- Halt rules are pre-registered (e.g. M1's halt threshold) — an infrastructure halt is recorded as *transport-unmeasured*, never as a model failure.
- The published invoice total for the whole campaign (~600 USD across gateways) is disclosed in the paper's §11.

## 6. Adding a new gateway/label

1. Probe the label first (an unregistered 13-in/21-out call is the campaign's calibration pattern — recorded, never counted as a session).
2. Register the route in the cohort's `_REGISTRATION.json` (label, base URL, allowance, seeds).
3. Record **any** deviation from the frozen protocol as an amendment *before* the run it governs.
4. Substitute labels are disclosed per-label and never pooled: the cross-vendor withdrawal row (Appendix E) is the worked example.
