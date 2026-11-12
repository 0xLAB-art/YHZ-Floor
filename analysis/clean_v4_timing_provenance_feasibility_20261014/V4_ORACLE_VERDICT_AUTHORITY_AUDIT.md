# V4 oracle verdict authority audit

## Authority path

The retained transcript records the submitted candidate in a `run` event and an adjacent task-specific oracle verdict in that same session event. The raw terminal record binds `run_id`, task card, oracle implementation hash, terminal status, and oracle verdict. `SUCCESS` is assigned only when the classifier receives `verdict == "success"`; `ORACLE_FAIL` is assigned when it receives `verdict == "failure"`. The fallback branch also returns `ORACLE_FAIL` for an unmapped graded outcome, so a status label alone is not sufficient evidence of explicit rejection.

## Row audit

| run_id | status | Transcript explicit verdict | Candidate event | Result |
|---|---|---|---:|---|
| qedd7c9aab5dcad7ed9f33482__chacha20_nonce_reuse__T1_known__rep1 | SUCCESS | accepted; task-specific checks true | 1 | explicit verdict retained |
| qaef4f421945ab6cf6bf8ba2f__chacha20_nonce_reuse__T1_known__rep2 | SUCCESS | accepted; task-specific checks true | 2 | explicit verdict retained |
| qb043d10ca94bb987b03fd142__cbc_padding_oracle__T1_known__rep1 | SUCCESS | accepted; task-specific checks true | 1 | explicit verdict retained |
| qf86aba4885ba256ad42fb17a__cbc_padding_oracle__T1_known__rep2 | SUCCESS | accepted; task-specific checks true | 1 | explicit verdict retained |
| q83ce3aca8c16001d24a2a383__cbc_padding_oracle__T1_known__rep3 | SUCCESS | accepted; task-specific checks true | 1 | explicit verdict retained |
| qb868b7c841e0cd44e83089eb__ecdsa_nonce_reuse__T1_known__rep1 | SUCCESS | accepted; task-specific checks true | 1 | explicit verdict retained |
| qdde825bc566a03f633adaf41__ecdsa_nonce_reuse__T1_known__rep2 | SUCCESS | accepted; task-specific checks true | 1 | explicit verdict retained |
| q94a788081121781914024471__ecdsa_nonce_reuse__T1_known__rep3 | SUCCESS | accepted; task-specific checks true | 1 | explicit verdict retained |
| qdcc68216073fea3769477764__rc4_keystream_reuse__T1_known__rep1 | ORACLE_FAIL | rejected; task-specific check false | 4 | explicit verdict retained |
| q8286a82902dfcb9e9926d1e7__rc4_keystream_reuse__T1_known__rep2 | ORACLE_FAIL | rejected; task-specific check false | 4 | explicit verdict retained |
| q520cf45cb28471ef0e45c05f__rc4_keystream_reuse__T1_known__rep3 | ORACLE_FAIL | rejected; task-specific check false | 4 | explicit verdict retained |
| qd715de7678c1048de48e6e60__chacha20_nonce_reuse__T1_known__rep3 | ORACLE_FAIL | rejected; task-specific check false | 4 | explicit verdict retained |

Result: sessions with at least one explicit accepted verdict: 8/8. Sessions with explicit rejection verdict(s): 4/4. Each failure session has four submitted candidates and four explicit task-specific rejection events; successes have a final accepted event, with any preceding rejected candidate events retained.

The transcript `run` record includes the submitted candidate and nested oracle response; task condition, replicate, model, and session-end record bind the exchange to the scheduled run. The raw record does not carry a separate oracle request UUID or candidate digest, so the link is same-session execution evidence rather than an independently addressable oracle transaction. No terminal label is changed. The classifier's fallback semantic is not needed to explain any of the observed ORACLE_FAIL rows.
