# Retained release selection and evidence-search boundary

## Selection

The frozen E1_SELECTION_REGISTER.md lists Cybench, NYU CTF Bench, CVE-Bench,
Incalmo, AgentHarm and WebSP-Eval. Inclusion required a public paper and
inspectable end-to-end security-agent artifact. Search surfaces named by
the register are ICLR/NeurIPS Datasets and Benchmarks, ICML, IEEE S&P, PETS
and arXiv. Selection was purposive across task classes. Classes overlap:
two included releases concern CTF solving, so the register is not evidence
of a disjoint one-release-per-stratum sample. InterCode-CTF was an unused
spare; no replacement is inferred.

The register's26 September scope cutoff,27–29 September worksheet
inspections/rechecks and5 October archive acquisition identify different
stages. They do not establish a synchronized snapshot at cutoff. The
register asserts a scope freeze before a second audit, but planned second
auditor steps are not treated as completed independent human validation.
A complete executed query/candidate-pool log is unavailable. This protocol
reconstructs the retained scope; it is not a retrospective preregistration
or a systematic literature search with a known selection denominator.

## Search and stopping

1. Inspect the retained worksheet's paper/artifact references and the named
   source snapshot. Check declared output locations and logging behavior,
   release/tree exclusions and archive-contained results. Bind findings to
   archive/source identity, not the latest public head.
2. Separate code capable of writing logs from actual released logs. A task
   dataset, ground-truth definition or example command is not a published
   evaluation trajectory. An example trajectory is not automatically the
   complete evaluation grid.
3. Follow output references far enough to classify the available object.
   An LFS pointer establishes a path/object reference; unavailable payload
   contents remain unresolved. Do not infer that original outputs never
   existed or that no other public/private copy exists.
4. Stop the retained-snapshot assessment at the documented material and
   unresolved search links. Report the inspected scope and missing witness,
   rather than manufacturing a failed live replay. The original two-day
   timebox is a planned rule, not a complete measured search-effort log.

## Worked decisions

| Decision | Rule and witness | Supported scope and unresolved extension |
|---|---|---|
| Positive timing evidence for Incalmo example | Archive results.json has experiment/execution/setup durations; the first equals the sum of the other two. The worksheet separately supplies the paper's trial/finished-limit boundary. | A reported example contains component timing; no reconstructed full-grid runtime or shared clock endpoint claim follows. |
| Partial trace/reconstruction coverage for Incalmo | Same retained example has50 infected hosts,48 exfiltrated files and614 action entries. | One concrete execution is inspectable. Coverage of the paper's entire evaluation grid remains unverified, so logger capability/example existence is insufficient for complete reconstruction. |
| Unresolved Cybench outcome reconstruction | Five output members in the retained archive are Git-LFS pointers. | Paths and object references exist; missing payload contents prevent verifying those candidate trajectories here. This does not refute a published success or establish global nonpublication. |

`release_examples.py` reopens the archives read-only and checks the numeric
relations/pointer objects. Its five assertions validate those primitive
observations, not the entire54-cell semantic audit. The original Y/P/N
matrix and F9-driven0/6 conjunction are preserved as historical descriptions,
not fresh replication failures or an ecosystem quality statistic.
