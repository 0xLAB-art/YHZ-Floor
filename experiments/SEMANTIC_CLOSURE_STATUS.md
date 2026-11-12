# Semantic closure status

Current synthesis counts are 1,132 catalog statements, 81 families, 9,290
graph nodes, and 14,671 edges. These are catalog and relation units, not
physical trials or causal links.

The current checkpoint is not semantically closed. The relation checkpoint
reports 30,472 source rows as `NOT_SEMANTICALLY_CLOSED`, 475 as
catalog-referenced scoped review, 932 as structured full parse, and 32 as
full-text loaded targeted semantic review. It also reports five missing
primary-source statements and a non-passed title/headline gate. The five named
published-source gaps are now resolved at published-source level by the
earlier ACTS multi-tier benchmark: its full text covers perturbation
robustness, structural ML, feature ablations, live-versus-deterministic
heuristic behavior, and PQC/classical byte-signal comparisons. Local
historical reconciliation of that source with the repository records remains
open.

Remaining closure work:

- unique result-like files and snapshot/capsule lineage outside the completed
  reviewer/qualification/evaluation surfaces;
- semantic reconciliation of the now-located ACTS source with local historical
  records and corrected H1 V2;
- nested archive and historic semantic gaps, including WebSP linkage and
  Cybench CSV time units;
- final title/headline selection only after the source gaps and counterexample
  review are closed.

The retained observation index contains 33,746 records and warns that its
status counts do not define physical-run totals or permit population pooling.
The next work therefore targets remaining archive/WebSP/Cybench semantic joins
and source reconciliation, not a blind full-corpus rerun.

Primary artifacts:

- `docs/scientific_synthesis/2026-10-17-exhaustive-relation-discovery/working/relationship_checkpoint_counts.json`
- `docs/scientific_synthesis/2026-10-17-exhaustive-relation-discovery/working/retained_observation_index_summary.json`
- `docs/scientific_synthesis/2026-10-17-exhaustive-relation-discovery/00_README_PROGRESS.md`
