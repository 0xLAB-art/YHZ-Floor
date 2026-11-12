"""E2A — End-to-End Attribution with a Trusted Execution Observer.

This package implements the Stage 1 experiment frozen in
``E2A_PREREGISTRATION.md`` (version 1.1, pre-execution).

Component map (trust boundary in parentheses):

* ``canonical``   — canonical JSON, digests, Wilson intervals (pure helpers)
* ``remediation`` — loads the *audited* HEB-1 primitives by absolute path
                    (``protected_signing``, ``context_validator``) without
                    modifying or re-implementing them
* ``producers``   — UNTRUSTED scripted producer of program source
* ``observer``    — TRUSTED Execution Observer (TEO); separate process
* ``reference``   — TRUSTED independent reference adjudicator; separate process
* ``aggregator``  — TRUSTED final claim adjudicator; in-process (replay ledger)
* ``baseline``    — adapter around the FROZEN, UNMODIFIED Stage 01 components
* ``cases``       — the frozen 22-case inventory
* ``truth``       — INDEPENDENT ground-truth recomputation (adjudicator side)
* ``runner``      — single frozen execution of the case inventory
* ``adjudicate``  — metric computation from retained artifacts only
"""

__all__ = [
    "adjudicate",
    "aggregator",
    "baseline",
    "canonical",
    "cases",
    "observer",
    "producers",
    "producer_ref",
    "reference",
    "remediation",
    "runner",
    "truth",
]
