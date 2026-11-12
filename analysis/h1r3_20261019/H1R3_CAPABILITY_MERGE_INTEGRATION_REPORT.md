# H1-R3 integration into capability_merge_20261016

## Result

Integrated the verified H1-R3 matched representation experiment into the versioned candidate:

`/mnt/nvme5/ACTS-Attack/sp2027/paper/capability_merge_20261016_h1r3_20261019/`

The original `capability_merge_20261016` directory was not modified.

## Scientific content added

- H1-R3: 852 scheduled sessions; terminal accounting 821 SUCCESS, 28 CRYPTOGRAPHIC_PREDICATE, 2 EXECUTION, 1 SOURCE_SYNTAX.
- Primary pooled L3: R0 125/128, R1 126/128, R2 123/128.
- R1-R0: tau=0.008, 95% CI [-0.023, 0.039], Holm exact McNemar p=1.000.
- R2-R0: tau=-0.008, 95% CI [-0.047, 0.031], Holm exact McNemar p=1.000.
- Both primary contrasts are equivalent within the preregistered +/-0.10 margin; this is contract-specific negative evidence, not proof of representation irrelevance or a universal capability estimate.
- Lower-level ECDSA asymmetries are retained as secondary/inconclusive; traces identify algebraic nonce-recovery slips but do not establish their arm-dependent cause.

## Candidate source changes

- `main_content.tex`: original SHA-256 `e7a0844870aef29ea402abb1c5bd7286f682f47571b36b517f0068d133ceab46`; candidate SHA-256 `e7a0844870aef29ea402abb1c5bd7286f682f47571b36b517f0068d133ceab46`; changed=False
- `main_sections/08_information.tex`: original SHA-256 `6a3797e51a8af1599473d71393cfbdccda1a4f88c4e1ff34dc799456dbea6f40`; candidate SHA-256 `ba38fa3b5d637d544316513176050a87b9793b4165c2086e326896824d016836`; changed=True
- `main_sections/09_audit.tex`: original SHA-256 `83fae77ac4e06be086c1bc55765a7890af4ec851cccc35e19af4cbe3a812550a`; candidate SHA-256 `8c59db6b196f2327cbf18883f656f6330737e5a99928ca9edf52c090c1e7e953`; changed=True
- `main_sections/11_limits.tex`: original SHA-256 `a1f1dbee34aea9fd499bc3dd1a0838c66313d914ab9e06a3bb8bc4806e33a4b0`; candidate SHA-256 `df640483fa311e3604c91ba9c56637ff97f40e2d0647542119a87bf1a333912c`; changed=True
- `main_sections/12_conclusion.tex`: original SHA-256 `cca10aa6c3943c7b7ab196b1aaac7d33c99afb07b5bafdfb2b834891af0a52a4`; candidate SHA-256 `cca10aa6c3943c7b7ab196b1aaac7d33c99afb07b5bafdfb2b834891af0a52a4`; changed=False
- `supplement_compact_content.tex`: original SHA-256 `37171dc013445640ae0da9a008d85103d11cd915bcbf52ad1b6bf869b2fdcbf6`; candidate SHA-256 `40dd928e683d8b4056bb29b7238a929e93f7a8c3067d063bef35c278f16f6e41`; changed=True
- `supp_sections/S26_h1r3.tex`: NEW candidate file; SHA-256 `25f9afe7523d1463d624e846a16245c63409d73fd682a732421ec3ea84b1e6d6`
- `main_sections/08_h1r3.tex`: NEW candidate file; SHA-256 `02fdfc2042dcdfd20ed8b1bd6ae8b24787612f7defdd2b3980f2c502d185af5c`

## Build verification

- `main_content.pdf`: 13 pages; SHA-256 `0e8995bd9bd2a2db850d8a7aa087e812f749a07119c490a926ed48c1594d8003`
- `submission.pdf`: 15 pages; SHA-256 `4d3d699410b534db592eeef44e952ddc76a420d23f3edd125ae489d4ceaec3e1`
- `supplement.pdf`: 4 pages; SHA-256 `3f1de5d989eb65b0afb284e8141bf388e0e5a9602dd4b380e29bf23d04b64f4a`
- main second pass: no fatal errors, undefined references, or overfull boxes.
- submission second pass: no fatal errors, undefined references, or overfull boxes.
- supplement second pass: no fatal errors, undefined references, or overfull boxes.

## Interpretation

H1-R3 strengthens the paper by adding a predeclared, independently adjudicated matched negative result and by separating the pooled primary estimand from exploratory stratified failures. It does not justify promoting representation sensitivity as a supported novelty claim.

## Preservation

- No provider/model calls were made during integration.
- No manuscript/result-lock file in the original directory was edited.
- The earlier candidate derived from the wrong root `main.tex` is not used as the authoritative paper candidate.
