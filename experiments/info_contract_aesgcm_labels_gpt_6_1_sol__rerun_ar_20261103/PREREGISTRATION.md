# P016-INFO-CONTRACT-2X2-AESGCM-WITHIN-ROUTE-LABELS-v1-RERUN-AR-v1 — pre-registered before first call

Re-run of the transport-damaged P016 labels arm `gpt_6_1_sol` on the AgentRouter route.
- seeds: 16 (byte-identical to `gpt_6_1_sol/_LAUNCH.json`)
- label: `gpt-6.1-sol`
- token floor: 2800 (the arm's registered floor; adapter `provider_adapter_agentrouter_p016_floor2800.py`, sha-pinned)
- runner: frozen `run_info_contract_2x2_aesgcm.py` (sha256 verified against the launch record)
- fixture/prompts/oracle/predicate: unchanged
- transport delta only: P023-generation adapter (registered retry, no stream_options bug)
