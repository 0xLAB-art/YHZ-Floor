# Invalidated prior H1 report

The original `h1_results.jsonl` and `h1_analysis.json` are retained as provenance but are invalid for confirmatory interpretation.

Reasons:

1. The underdetermined records used placeholder observations (`insufficient_observations: true`) rather than genuine insufficient cryptographic observations.
2. The generated arm IDs used `A_*_UNDETERMINED`, while the frozen registry uses `A_*_UNDET`.
3. Therefore the reported 30/30 abstention result was not a valid preregistered H1 underdetermination result.

Corrected evidence is under `revalidation_v2/` and uses registry-valid arm IDs and genuine insufficient observations.
