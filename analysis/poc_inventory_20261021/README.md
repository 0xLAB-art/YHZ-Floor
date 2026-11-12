# Recursive experiment PoC inventory

`extracted_recursive_v3/` is the complete inventory produced in this pass. The earlier `extracted/` and `extracted_recursive_v2/` folders are partial inventory passes; use v3 for analysis.

The crawler recursively covered the experiment, analysis, artifact, evaluation, snapshot, and evidence roots listed in `extracted_recursive_v3/SUMMARY.json`. It recorded standalone PoC source files, source files referenced by structured experiment records, code stored in structured fields, and Python or JSON code fences inside JSON/JSONL records. It scanned 8,364,491 JSON or JSONL records.

The manifest has 13,222 source occurrences: 5,004 file occurrences and 8,218 code occurrences embedded in records. These map to 3,081 unique SHA-256 objects under `extracted_recursive_v3/objects/`. Identical bytes are stored once, while every source occurrence remains a separate row in `manifest.csv`. `source_path` identifies the original file and, for embedded code, its JSON pointer or JSONL line and field.

No extracted program was executed. Inclusion means only that a file or record contained a source-like program; it does not establish that the program is a valid PoC, was used in a scored trial, executed, or succeeded. The crawler includes historic, exploratory, synthetic, failed, and duplicate records so that later evidence adjudication can distinguish them without losing provenance.

Unlabeled or unfenced code in free-form text outside JSON/JSONL records is not inferred. The aggregate count of 89 malformed JSON records or fenced JSON blocks is retained in the summary; these need case-level review before relying on any affected record. The `extracted/` and `extracted_recursive_v2/` directories are earlier pass outputs and should not be combined with v3 counts.
