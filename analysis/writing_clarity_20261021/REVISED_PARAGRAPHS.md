# Revised paragraphs and their roles

## main_frontmatter.tex

### P1: Abstract: problem, method, evidence, and scope

```latex
An agent can recover the correct secret yet leave important parts of an
attack claim unverified. ACTS-Attack examines what cryptographic recovery
programs establish, how evaluator admission changes their scores, and what
evidence links a result to the claimed execution. A matched study
contains 768 representation trials and 84 controls. On 128 instances at the
primary observation-complexity level (L3), the
base64--hexadecimal success contrast is $-0.8$ percentage points under the
declared contract, within the pre-specified $\pm10$ point margin for two
families and one route. Applying a contract-mismatched source filter to
unchanged programs moves it to $-32.8$ points; output-preserving unused-import
removal changes the filtered contrast to $+3.9$ points. Separate studies
record 12/12 completed supplied operations and 8/12 accepted prospective
agent sessions. Their traces identify observation and implementation failures;
a supplied AES-CTR chain demonstrates protected-payload release. Constructed
evidence bundles show why correct candidates, intact records, or signatures
alone may not support execution attribution. An explicit attribution policy
undergoes 11{,}256 bounded mutation evaluations without an observed soundness
violation, and a configured in-toto inspection checks another implementation.
These results make the scope of an attack claim inspectable. Construction
evidence spans distinct local interfaces; the admission estimate remains
specific to the matched study, and attribution depends on the stated trust
model. Each cohort retains its own denominator.
```

## main_sections/01_intro.tex

### P1: Opening: distinguish the questions behind success

```latex
What does a reported security-agent attack success establish? A correct
recovered secret answers one question. Separate checks must establish whether
the evaluator admitted the program under the declared rules and whether the
evidence supports the claimed execution.
```

### P2: Method rationale: independent checks of recovered values

```latex
ACTS-Attack studies these questions through cryptographic recovery tasks.
The evaluator checks recovered values against reserved secrets or public-key
relations. This lets us examine the submitted program's result separately
from the decisions made about that program and its execution.
```

### P3: Evidence: local fixed-program admission effect

```latex
Admission alone can change the measured contrast. On 128 matched L3
instances, the base64--hexadecimal contrast is $-0.8$ percentage points under
the declared contract and $-32.8$ under a filter rejecting prompt-permitted
imports. Unused \texttt{hashlib} imports account for $-28.9$ points of the movement;
output-preserving cleanup changes the filtered contrast to $+3.9$ points.
```

### P4: Evidence: operation feasibility and agent construction

```latex
The construction studies ask what is needed to turn a disclosed weakness
into a checked result. A fixed executor completes 12/12 supplied operations;
the prospective agent cohort (V4) completes 8/12 sessions. Other cohorts
identify missing observations or incorrect parameters and demonstrate
supplied-chain payload release.
```

### P5: Transition: correctness leaves execution questions open

```latex
Execution attribution raises a different question. The escrow study (E5) retains a correct
candidate whose acquisition remains unresolved, motivating tests of the
evidence needed for execution attribution.
```

### P7: Scope: complementary populations

```latex
The experiments address different parts of an attack claim and retain
separate populations.
Section~\ref{sec:external-coverage} distinguishes their coverage across
interfaces, within-family transfer, and attribution implementations.
```

### P12: Explanation, evidence, or scope within the named subsection

```latex
(2)~\textbf{An empirical account of recovery requirements and target effects.}
Agent trajectories, observation variants, and target controls identify
successful constructions and explain specific failures under local
contracts. A supplied attack chain establishes payload release. Comparisons
between unmatched cohorts remain descriptive.
```

## main_sections/02_related.tex

### P1: Explanation, evidence, or scope within the named subsection

```latex
\textbf{Cryptographic capability of agents.} ACTS~\cite{acts} introduced a
multi-tier classification of LLM cipher identification under controlled blind
conditions and reported a 40.9-point metadata-aided vs.\ blind gap and a
92.9\% vs.\ 41.3\% agentic vs.\ tool-only contrast. AICrypto~\cite{aicrypto}
evaluates cryptographic knowledge, CTF exploitation, and proofs, while
CryptanalysisBench~\cite{cryptanalysisbench} tests attacks on cryptographic
primitives. These are direct capability comparators, not merely classification
benchmarks. FirmAgent~\cite{firmagent} and APPATCH~\cite{appatch} show that LLM-based
workflows can discover or patch real vulnerabilities, but their objectives and
oracles differ from cryptographic attack construction. CyberGym~\cite{cybergym} evaluates executable vulnerability
reproduction against real codebases; AutoPT~\cite{autopt} uses state-machine
constraints for web penetration testing. AutoPenBench~\cite{autopenbench}
records intermediate milestones and distinguishes autonomous from human-assisted
testing.
```

### P2: Explanation, evidence, or scope within the named subsection

```latex
We study how the interpretation of a checked recovery changes with
the evaluation decision being made. The representation study fixes recovery
instances and execution conditions; the admission comparison fixes the
generated programs themselves. Attribution tests ask what evidence links
that recovery to a particular execution.
```

### P4: Explanation, evidence, or scope within the named subsection

```latex
\textbf{Trajectories and evaluation integrity.} CTF-ABACUS~\cite{ctfabacus}
provides trace-level provenance for agentic offensive-security evaluation;
ABC~\cite{abc} audits task setup and reward design, while
AgentSuite~\cite{agentsuite} distinguishes user, environment, ground-truth,
and evaluation defects. BenchJack~\cite{benchjack}, a preprint, audits benchmark
hackability. AgentRewardBench~\cite{agentrewardbench} compares automatic
trajectory evaluations with expert judgments; PROV-AGENT~\cite{provagent}
tracks workflow provenance. ABC demonstrates score distortion from task and
reward defects, including rescoring fixed agent artifacts; AgentSuite
diagnoses validity by benchmark component. Our cryptographic analysis
measures an admission effect on fixed programs and tests its dominant source
through output-preserving cleanup.
```

### P5: Explanation, evidence, or scope within the named subsection

```latex
\textbf{Execution boundaries and attribution.} AgentDojo~\cite{agentdojo}, IsolateGPT~\cite{isolategpt},
and SAGA~\cite{saga} address agent execution isolation and security
architecture; ToolHijacker~\cite{toolhijacker} demonstrates that tool-selection
interfaces are themselves attack surfaces. ORTHRUS~\cite{orthrus} illustrates the
separate provenance problem of making attack evidence attributable and reviewable.
Cloak, Honey, Trap~\cite{cheat} shows that target-side deception can disrupt
offensive agents, making the agent's own execution environment part of the
security boundary. Our attribution experiments test which authenticated,
mutually consistent records support a cryptographic execution claim. The
policy uses existing provenance mechanisms; we contribute its operational
specification and measured behavior under the stated trust model.
```

### P7: Explanation, evidence, or scope within the named subsection

```latex
\textbf{Public reconstruction evidence.} We apply a predeclared 9-field
rubric to six releases: Cybench, NYU CTF Bench, CVE-Bench, Incalmo,
AgentHarm, and WebSP-Eval~\cite{cybench,nyuctf,cvebench,incalmo,agentharm,webspeval}
(Section~\ref{sec:audit}). This audit examines the public evidence available
for reconstructing a published outcome.
```

## main_sections/03_design.tex

### P1: Setup: information and execution interfaces

```latex
Interactive tasks give the agent a local target, a specified weakness, and
a checkable success condition. Response-only tasks instead ask for a value
derived from public observations. Replay, admission, and provenance controls
test the evaluator. Tools and execution authority are stated per population.
```

### P3: Explanation, evidence, or scope within the named subsection

```latex
We count sessions separately from submitted programs: V4's 31 programs
belong to 12 sessions. Code identity, target predicates, clock endpoints,
and execution records support different claims about those sessions.
```

### P5: Explanation, evidence, or scope within the named subsection

```latex
We report three separate quantities:
\begin{enumerate}
\item \textbf{Attack success}: candidate satisfaction of $P$ under $V$, with
ASR per task and population, never pooled into one rate across families. A
pre-specified paired contrast over a fixed matched instance set is a
different estimand and is reported separately
(Section~\ref{sec:h1r3}), with its family split retained.
\item \textbf{Execution cost}: work within a named clock interval; operation,
agent-session, and non-execution estimates remain separate.
\item \textbf{Execution provenance}: the strict H1 criterion links source,
configuration, task, immutable image digest, execution identity, and result.
\end{enumerate}
Candidate correctness alone establishes neither cost nor provenance. Under
the strict provenance criterion H1, EXP-034 scores 0/12 because the hosted
model has no immutable image digest; the deterministic local OCI control
(EXP-035) scores 3/3. The control closes that identity link locally, not for
the hosted-agent executions.
```

### P6: Explanation, evidence, or scope within the named subsection

```latex
$T_{op}$ measures only the already-written attack program's operation span
(fixed executor, no model loop). $T_M$ (clean) measures the agent loop from
post-provision to terminal handling, captured with
\texttt{time.monotonic\_ns()} before cleanup. $T_M$ (legacy) measures the
historical agent session under old conditions with different instrumentation.
Successful V4 agent medians: ChaCha20 18.37\,s ($n{=}2$, range 17.50--19.24),
CBC 50.06\,s ($n{=}3$, 39.44--71.13), ECDSA 15.29\,s ($n{=}3$, 14.47--16.64);
RC4 has no successful clean median (0/3). The fixed-executor and legacy
$T_{op}$/$T_M$ medians are reported with the studies that measure them
(Sections~\ref{sec:floor} and~\ref{sec:legacy}). These intervals concern
separate populations; no cross-cohort efficiency
ratio or pooled capability estimate follows. $T_{op}$ for stream ciphers is
sub-millisecond while agent $T_M$ is measured in seconds. The measured
interval must therefore accompany any reported duration.
```

### P7: Explanation, evidence, or scope within the named subsection

```latex
The V4 acceptance verdicts and its timing records have different evidence
status. The eight accepted sessions retain submission-to-verdict traces, but
none of the eight successful V4 durations has a retained raw monotonic endpoint
pair; the displayed medians are reported elapsed values, not independently
recomputable timing measurements. The historical time-to-exploit analysis partitions records into four non-interchangeable
estimands: $T_{agent}$, $T_{op}$, $T_{estimate}$, and $T_{probe}$. Its 21
operation rows (nine TLS templates and twelve RC4/CBC/ECDSA/ChaCha20 rows)
document operation time without adding autonomous-success trials. TLS
policy, message edits, A1 timing, D1 recovery, and B1 refusal each measure a
different event; their durations do not rank primitive security or agent speed.
```

### P12: Explanation, evidence, or scope within the named subsection

```latex
These populations are not independent replications. The historical census
counts 35 migrated and 39 raw-only sessions once. Provider unavailability,
harness invalidity, tool failure, timeout, give-up, refusal and oracle rejection
remain distinct. The 51 legacy clock pairs qualify endpoints; E6 measures
codebook agreement, not ground truth.
```

### P13: Explanation, evidence, or scope within the named subsection

```latex
Figure~\ref{fig:arch} separates control, agent--target execution, independent
verification and the harness-owned evidence path. The
controller makes task-session reservation atomic; the task card digest is
frozen before the first model call. The agent owns attack code; the harness
owns identity, clock, and terminal state; the oracle owns the verdict; in E5, the verifier forwards candidates to escrow for comparison without
pre-verification reveal. Nine control
suites exercise the harness and its acceptance rules: contract
qualification 4/4 (CBC 10{,}775 queries); stable-backend 6/6; fixed-executor
12/12; protected-grader 20 cases (18 rejects + 2 accepts);
regression 8 checks; provider-fault canary 180/180; provenance control 3/3
(digest-pinned OCI); offline replay 52/52; eligibility-gate canary 180 cases
zero misclassification. The controls cover specified endpoints, and retry
histories are not retained. Image digests do not identify the host; the
escrow boundary is declared rather than enforced. Timing analysis excludes
4 legacy drift rows.
```

## main_sections/04_capability.tex

### P5: Design and accounting: source rejection versus cryptographic failure

```latex
The earlier import filter would reject 6.2\%--47.7\% of the retained programs
across arms. Holding programs fixed isolates the admission decision from
the primary representation comparison under the common executor and oracle.
A source rejection occurs before execution and is counted separately from
cryptographic failure. The complete cohort contains 801 verified-exploit
successes, 20 correct abstentions, 28 cryptographic-predicate failures,
2 execution failures, and 1 source-qualification failure:
$801+20+28+2+1=852$ sessions. Abstentions are not exploit recoveries.
```

### P6: Explanation, evidence, or scope within the named subsection

```latex
Most of the change is traceable to one module. Of the 852 sessions, 205 import a
module the earlier rule denies---183 of the 768 representation trials and 22
of the 84 control sessions---and all 205 concern modules the prompt
permitted.
```

### P7: Mechanism: representation-associated imports

```latex
The per-arm rates differ because the generated code differs in
style: an unused \texttt{hashlib} import appears with the base64 representation in 88
of 256 programs, against 8 of 256 in the neutral representation, and the
type-hint import appears in 42, 26 and 4 of the R2, R0 and R1 programs.
Denying \texttt{hashlib} alone accounts for $-28.9$ of the $-32.0$ points;
every single-module narrowing of the other sixteen moves the contrast by at
most $3.1$ points, and denying the base64 module itself is degenerate
because it is the representation.
```

### P8: Control: output-preserving cleanup

```latex
Conservative unused-import removal
eliminates the large negative gap: all 128 cleaned derivatives reproduce
their original output, and 104 then qualify. The filtered L3 contrast changes
from $-32.8$ to $+3.9$ points, compared with $-0.8$ under the original declared
contract. Residual import rejections remain, but the large negative contrast
does not. Of the 101 programs with retained import references, 24 belong to
the matched L3 instances and 77 occur elsewhere.
```

### P10: Explanation, evidence, or scope within the named subsection

```latex
A fixed executor with fresh secrets and three repetitions completes 12/12
supplied operations (V tier). Executor/oracle medians are, respectively: RC4
0.214/0.234\,ms, ChaCha20 0.132/0.155\,ms, CBC 1{,}981.6\,ms at 20{,}480
queries per repetition, ECDSA 6.96/6.89\,ms. These controls show that the
supplied recovery operations and verifier can complete. They do not test
whether an agent can write those programs.
```

### P12: Interpretation: task-specific recovery conditions

```latex
The trajectories help explain the different task outcomes. The RC4
brief omits the all-zero second message that makes the XOR relation usable;
its three sessions submit 12 rejected candidates. ChaCha20 requires a
reference-encryption observation that the brief does not supply. CBC instead
shows a successful revision path: rep2 moves from 257 queries and failure to
feedback, 20{,}737 queries, and a digest match. ECDSA accepts the first
submission in all three sessions.
```

### P13: Explanation, evidence, or scope within the named subsection

```latex
Three code-generation cohorts test exploit construction with explicit
observations: RC4 aligned
known-plaintext+ciphertext+target; ChaCha20 a reference encryption of zeros;
ECDSA repeated-nonce signatures. Each family runs an initial 2/2, a
replication 2/2, and an extension 2/2---6/6 first-submission per family,
18 cells total. The initial ECDSA cohort contained a nested
\texttt{public\_input} interface defect (4 \texttt{KeyError} executions);
those are interface-contract failures, not cryptanalytic failures, and are
excluded from the 6/6 count. Recent ECDSA uses secp256k1 with DER-encoded
signatures and checks the public key from the scalar; RC4 and ChaCha20
recover plaintexts, not keys. These successes establish construction under
explicit observations. They do not isolate the effect of those observations:
token allowance, program-vs-answer format, instructions, parser, and feedback
also differ from V4.
```

### P14: Explanation, evidence, or scope within the named subsection

```latex
A blind-opportunity variant (containers 0032--0034) removes statement-level
references that make the opportunity exploitable. ECDSA completes 2/2 and RC4
2/2 on first submission; ChaCha20 completes 0/2 with 3 candidates over 4
responses. The removed information differs by family. The reduced ChaCha20
prompt still exposes the algorithm name and
a nonce-reuse flag in the public JSON, but removes the statement that the
reference encrypts zeros; a local solver using that zero-reference recovers
both secrets, confirming recoverability when that premise is available.
The reduced prompt does not provide it; the disclosed
stream relation gives a two-plaintext XOR leaving the target unspecified. RC4
retains known-plaintext fields and ECDSA retains curve/signature observations,
so their information loss is asymmetric. This is an information-contract
diagnostic, not a family ranking.
```

## main_sections/05_adaptive.tex

### P1: Explanation, evidence, or scope within the named subsection

```latex
Recovering a secret has a security consequence only when the target permits
its use. These RQ2 studies examine supplied attack chains, exploration, and
transfer of a solving strategy within one family. They belong to a separate
post-freeze program (single
model label \texttt{opencode/glm-5.3-flash-free}
via OpenCode CLI, purpose-built localhost fixtures, $\le$4 cells per phase,
single experimenter), where independent oracles establish feasibility under
these scaffolded conditions. The studies retain separate denominators and are
not pooled with V4.
```

### P2: Explanation, evidence, or scope within the named subsection

```latex
A target generates a 32-byte secret $S$ and a 32-byte key $K$, exposes
$A = S \oplus K$, and answers oracle queries $f(x) = x \oplus K$ on 32-byte
samples; any one valid query reveals $K=f(x)\oplus x$ and therefore
$S=A\oplus f(x)\oplus x$, so choosing $x=0$ suffices. The fixture therefore
allows us to observe exploration, although recovery does not require multiple
adaptive queries. Two replicates reach an exact 32-byte recovery:
attempt~6's final \texttt{adaptive\_retry2} run after 8 oracle queries, and
attempt~7/rep3 after 39 oracle queries. The retained failed replicate in attempt~7 is
a terminal failure/integrity-limited record, so the paper reports two accepted
runs plus one failed retained run, not a capability probability or a 2/3 rate.
In the 39-query replicate the agent
forms competing hypotheses (keyed block cipher vs.\ position-wise XOR), issues
single-bit probes that discriminate them, selects XOR, and computes
$S = A \oplus K$. The traces show adaptive exploration and hypothesis revision,
not evidence that adaptation was necessary or advantageous. The
integrity-failed replicate remains tier E. Without a matched non-adaptive
baseline, the 8-vs-39 query spread does not estimate an adaptive-cost effect.
```

### P4: Evidence and scope: held-out alphabet transfer

```latex
Attempt~4 tests transfer to a different alphabet while keeping the solving
rule fixed. Its two development and two held-out cells share two underlying
secrets; development accepts 2/2 and held-out accepts 2/2. The integrity gate
passes, a 50-file leak audit records 0 hits, and pre-send/post-receive digests
match 4/4. Attempt~3 contains four accepted-looking cells but fails integrity
because secret bytes occur in provider transcripts. Those cells are excluded;
earlier attempts were blocked or did not run. The 4/4 result therefore refers
only to attempt~4. Both arms receive the rule, a generic solver is generated
locally, and the harness executes it to recover the secret. The result
supports within-family alphabet transfer, not a new cryptanalytic problem.
\subsubsection{Budget-Qualified CBC Control}\label{sec:budget}
A budget-qualified control probes the CBC padding oracle under an amended
budget: a 15-byte plaintext with PKCS\#7 padding is recovered in 2{,}021
oracle queries under a 4{,}096-query budget, while a frozen 400-query budget
fails on the same task. A named-CBC surrogate arm accepts at 9{,}640 queries
and an exact-recovery control at 20{,}480, with the offline base control
rejecting 8/8 surrogate and accepting 8/8 exact candidates. These are not the
V4 64-byte task; they bound the query cost of verification modes on a smaller
plaintext and are reported separately from the V4 CBC trajectories
(20{,}737--21{,}508 queries at 64 bytes).
```

### P5: Explanation, evidence, or scope within the named subsection

```latex
These studies show what the tested programs accomplish beyond producing a
candidate: they explore an oracle, use a recovered capability, or transfer a
solving rule. The explicit-code cohorts, two XOR recoveries, single AES-CTR
chain, four held-out cells, and CBC control retain separate populations.
Their small, scaffolded samples support feasibility under the stated
contracts, without a combined success rate.
```

## main_sections/04_diagnostics.tex

### P1: Explanation, evidence, or scope within the named subsection

```latex
Historical records show why non-success cannot always be attributed to
cryptanalytic failure. The diagnostics below distinguish operational
failures from failures to recover a candidate. Their populations and evidence
status remain separate from the matched and prospective studies.
```

### P6: Diagnostic: recorded endpoints and XOR scorer qualification

```latex
A separately registered arm uses named, unnamed, and underdetermined briefs
with 10 matched seeds per family. For each of RC4, ECDSA, and XOR, the
original runner records 0/10 named recoveries, 0/10 unnamed recoveries, and
10/10 abstentions: 90 calls, zero provider failures, \$0.1389 estimated cost.
The abstention instruction was explicit. The XOR scorer also grades a
different object from the requested mask, so its recorded null is not a valid
recovery endpoint (Section~\ref{sec:h1}). The invalid predecessor report
(placeholder prompts and arm-ID mismatch) is retained only as provenance.
Local fixture checks establish recoverability without verifier truth in
the prompts; interpretation remains contract-specific (R tier). A companion
output-contract arm (9 calls, same public instances) parses 4/9 strict
single-object JSON responses but records 0 oracle recoveries. Correct format
alone does not establish a correct recovery.
```

### P9: Explanation, evidence, or scope within the named subsection

```latex
These diagnostics explain how construction outcomes enter a denominator.
An accepted recovery still leaves a separate question: does the target
permit the claimed security effect? The next section tests that endpoint.
```

## main_sections/06_targets.tex

## main_sections/07_leakage.tex

## main_sections/08_information.tex

### P3: Limitation: acquisition and verifier identity

```latex
The execution architecture leaves the acquisition claim unresolved.
Generated code runs on the host rather than inside the victim container;
escrow handlers do not authenticate caller roles. The recorded verifier
digest also identifies an older four-task verifier instead of the selected
E5-capable launcher. R30 therefore supports candidate correctness under
commitment while leaving exclusive acquisition and boundary enforcement open.
```

## main_sections/09_audit.tex

### P1: Explanation, evidence, or scope within the named subsection

```latex
No release satisfies all nine fields (0/6): the retained public material does
not bind implementation, configuration, task, immutable environment, execution
identity, and result for one end-to-end success. The 54 field-level cells carry graded rather than uniformly absent
evidence, with the per-cell dispositions in the supplement.
The published-outcome field is insufficient in every release and therefore
blocks the all-nine result by itself. Table~\ref{tab:audit-fields} reports
the other fields separately. Dropping that field still leaves 0/6 satisfying
the remaining eight, although this sensitivity check does not validate the
rubric. Field requirements depend on the claim: clocks and costs support
timing/resource claims; weakness and discovery evidence support mechanism
and autonomy claims. A correct-candidate claim does not require every field.
The conjunction concerns complete historical reconstruction, rather than
the correctness of the audited systems. These documentary observations are
separate from V4, E5, and executed attacks.
```

### P2: Motivation and design: authenticity plus consistency

```latex
Available records may still support an unjustified claim. Our RQ3 policy
therefore checks both authenticity and consistency: records must come from
authorized roles and agree on the execution to which the claim refers.
An observer-signed record
covers the exact executed bytes and captured stdout; a reference-signed record
recomputes the task predicate from private target state against that stdout and
names the observer record. Attribution requires agreement of the declared
digests, matching identity fields, authorized observer and reference roles, and
the applicable replay policy; the claimant's own \texttt{claims} block never
influences the decision. Trust assumptions concern the observer, reference
verifier, and role policy.
```

### P4: Implementation evidence: configured policy agreement

```latex
A configured in-toto inspection expresses the same policy using existing
provenance mechanisms. It reproduces 21/22 decisions, reaching 22/22 with a
shared replay ledger. The SLSA arm stops at provenance acquisition and is
not comparable. This tests policy implementation and configuration, not
superiority over provenance frameworks.
```

## main_sections/10_discussion.tex

### P1: Synthesis: interpreting different success events

```latex
The studies show why an attack-success label needs an explicit interpretation.
A correct program can be rejected at admission; a correct candidate can leave
its acquisition unresolved. Distinguishing these cases lets us state what
each experiment establishes without combining unlike outcomes.
```

### P2: Explanation, evidence, or scope within the named subsection

```latex
The paired study separates a representation comparison from an admission
decision. Regrading fixes the program and oracle outcome; the filter,
which is narrower than the H1-R3 prompt, changes the contrast by $-32.0$
points. Representation-associated \texttt{hashlib} imports explain most of
the change, and output-preserving cleanup removes the large negative gap.
The result identifies a contract mismatch and its source-level trigger.
```

### P6: Explanation, evidence, or scope within the named subsection

```latex
ABC and AgentSuite analyze benchmark validity across task, environment, and
evaluation components \cite{abc,agentsuite}; cryptographic-capability work
supplies the task context \cite{aicrypto,cryptanalysisbench}.
We quantify how admission changes scores, trace recovery failures to their
observation and implementation conditions, and test the records needed to
credit an execution. H1-R3 supplies the controlled admission measurement;
the target studies establish consequences under their own predicates. The
attribution cases show when correct or authentic evidence supports a weaker
claim than the one requested. These questions connect the studies while
their populations remain separate.
```

### P7: Explanation, evidence, or scope within the named subsection

```latex
The studies cover different aspects of generality
(Table~\ref{tab:external-coverage}). V4's capture-first loop and the
post-freeze OpenCode CLI studies retain accepted constructions under two
interfaces and model labels. Their differing tasks, observations, and budgets
support feasibility across settings, not a matched harness or model effect.
```

### P8: Explanation, evidence, or scope within the named subsection

```latex
IAR-C's separate generator and adjudicator share the schema and cryptographic
module, and its preserved cases were used in calibration. The in-toto
inspection implements the same policy. These extend constructor and
implementation coverage. They do not replicate the admission magnitude on
an independent benchmark.
```

## main_sections/11_limits.tex

### P1: Explanation, evidence, or scope within the named subsection

```latex
\textbf{Scope and identity.} Feasibility samples are small ($n=2$--$4$;
V4 $n=3$ per task). V4 uses a mutable provider label; the post-freeze
studies use another label and one experimenter. EXP-034 retains runtime
fingerprints and trace hashes but no immutable hosted-model image digest.
EXP-035 closes that link only for a network-disabled local OCI control.
V4 lacks token usage and HTTP attempt IDs; its 48-attempt/session bound
($8\times3\times2$) is a ceiling, not an observed count.
```

### P2: Explanation, evidence, or scope within the named subsection

```latex
\textbf{Causal and measurement limits.} H1-R3's matched conclusion applies
to the tested representations, levels, margin, two families, and one route. The
powered $L3$ cells succeed in 124--126 of 128 sessions, leaving little
headroom for improvement without ruling out a large negative effect. Few discordant pairs
and empirical bootstrap coverage limit precision. Lower-level R0 baselines do not uniformly
offer more headroom, and lower-level $R2$ contrasts remain inconclusive under
the frozen margin rule.
V4 and explicit-observation cohorts differ in token allowance, format,
instructions, parser, feedback, and observations; their contrast is
descriptive. The tier-E $59.5\times$ A1 $z$ contrast confounds build, timer,
preparation, and method. $TTE_M$ is quantized at 0.1\,s; eight successful V4
sessions lack raw harness endpoints, four legacy records breach the 1\,ms
gate, retries and D1 raw samples are unretained (D1 tier R), and E3 uses one host.
```

### P5: Explanation, evidence, or scope within the named subsection

```latex
The property-check results, in-toto agreement, ECDSA cause split and
release-audit printed-table alignment remain recorded rather than
independently re-derived from the public package. Its dispositions omit the
programs, prompts, responses and truth needed for full cryptographic replay.
A separately staged full package contains those dependencies. Its local
sandbox replay executed 851 programs on public inputs; the syntax rejection
was not executed. The checks agreed with all 852 verdicts: 801 recoveries,
20 correct abstentions and 31 rejections. This replay required no hosted-model
access and checked retained programs, not regenerated responses.
\texttt{verify.py} checks digests and missing full-lock dependencies.
Release judgments remain source-linked assessments. Policy regrading is
exploratory on the frozen cohort and measures a contract mismatch, not a
capability difference.
```

### P7: Explanation, evidence, or scope within the named subsection

```latex
\textbf{Generative AI usage.} The records retain declared model routes and
budgets. Authors reviewed AI-assisted prose and figures. Quantitative claims
rest on retained records, frozen analyses, and task-oracle verdicts. Automated
checks cover specified arithmetic and identity links; AI-assisted audit
judgments retain their sources and diagnostic limits.
```

## main_sections/12_conclusion.tex

### P1: Conclusion: the empirical account and its scope

```latex
ACTS-Attack examines what an evaluated cryptographic attack establishes.
Matched trials isolate a local admission artifact and explain its import
mechanism. Agent trajectories and target controls document recoveries,
specific failures, and supplied-chain payload release. The escrow and
attribution studies show what a correct candidate leaves unresolved about
the execution being credited.
```

### P2: Explanation, evidence, or scope within the named subsection

```latex
Construction spans local interfaces; attribution tests vary constructors and
policy implementations. Neither replicates H1-R3's admission magnitude on an
independent benchmark. Evaluators should state the measured event and
predicate, retain admission and failure stages, and bind accepted outputs to
the credited execution. A reader can then distinguish evidence of recovery,
target consequence, and execution attribution.
```
