# PREREGISTRATION — P010L5: fifth-label replication (free/kimi-k3 on APINEX)

**Namespace:** info_contract_label5_20261030/
**Frozen:** 2026-10-30, before any experiment call.
**Label:** free/kimi-k3 (Moonshot AI) on https://api.apinex.bond — a completely
different model family AND provider from every prior cohort (Claude/Anthropic
via apmix, GPT/agentrouter; now Moonshot/apinex).

## Design
Frozen P010 runner byte-for-byte (SHA a08eab6f...), driven via sys.modules
injection of provider_adapter_apinex.py (new transport: OpenAI-compatible
/v1/chat/completions, User-Agent required by Cloudflare). Seeds 221-228,
4 cells x 8 seeds = 32 sessions, <=2 turns, token floor 2800.

## Deviations
- D1: provider injection (sys.modules shim, frozen runner untouched)
- D2: token floor 1400 -> 2800 (reasoning-family label)
- D3: label binding via APINEX_LABEL_MODEL + pre-freeze fingerprint probe +
  post-run fingerprint audit (the X1 discipline)

## Pre-freeze evidence (NOT evidence)
HEALTH.json: all 4 APINEX models respond, model field echoes requested label.

## Statistics
Identical to P010L3/L4. Separate population, never pooled.
