# Model-to-code feedback exploration, v1

Protocol: `P009-H1-EXP-CODE-FEEDBACK-v1`.

Two qualified synthetic ECDSA instances were presented to the model as a
model-generated-code task. Each session allowed two submissions and returned a
bounded verifier feedback message after rejection. All four provider responses
arrived successfully and all four submissions passed the static code policy,
but all four executions failed with `KeyError` before producing a candidate.

Root cause: the exploratory harness wrote the public observation under a
`public_input` wrapper while the prompt and generated programs expected the
public fields at the top level. This is an implementation-contract defect, not
evidence of cryptanalytic incapacity. The raw lane is retained and excluded
from model capability interpretation. Estimated accounting cost was $0.029844
on the provider's reported free route; no invoice cost is claimed.
