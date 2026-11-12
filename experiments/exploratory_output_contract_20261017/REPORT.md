# Prospective output-contract exploration

Protocol: `P009-H1-EXP-OUTPUT-CONTRACT-v1`.

Nine calls used the already qualified RC4, ECDSA, and XOR local public
instances for seeds 1--3. The only changed factor was an explicit instruction
to return exactly one JSON object on one line, with no prose, markdown,
calculations, or additional keys. The study was prospective and additive, but
not randomized against model sampling and therefore non-confirmatory.

All nine provider calls returned successfully with no provider failure. Four of
nine responses were strict JSON objects containing the required candidate field;
five were not strict JSON or lacked that field. Local qualified fixture/oracle
scoring found zero recoveries. This is a negative diagnostic result: the output
contract alone did not establish a model-to-oracle attack path. The next
discriminating factor should change tool access or feedback while preserving the
same target opportunity and oracle boundary.
