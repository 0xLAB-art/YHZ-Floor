# C3 (registered follow-up) — P010X1 incident disclosure to the gateway operator

**Status:** DRAFT DELIVERED TO THE AUTHOR FOR SENDING (the commitment is the
disclosure itself; the author sends it under their own account).
**Commitment text (Section 11):** "The P010X1 incident disclosed to the
gateway operator."

---

**Subject:** Disclosure: cross-vendor label drift incident on your platform (registered research cohort, 2026-10; resolved and documented)

Dear gateway operator,

We are an independent research team evaluating AI-agent security claims
(IEEE S&P 2027 submission, pre-registered protocols, frozen analysis). We
are disclosing a labeling incident we encountered on your platform, per our
registered follow-up commitments.

**What happened.** On 2026-10-19, one of our registered cohorts (64 sessions
on a single task family) was registered as a cross-vendor comparison: the
preregistration named label `gpt-oss:120b-cloud` as served through your
cloud route. Runtime metadata shows the primary label was delivered — all
97 raw provider responses echo `claude-sonnet-4-6` on the primary route —
so the cohort's vendor claims were withdrawn at analysis time and its
numbers retained as same-label evidence. Our post-run fingerprint audit
(every raw response checked against the attested name) is part of our
registered protocol and is how the drift was detected; no summary-rate
comparison would have surfaced it.

**What we are asking.** Nothing. No dispute, no credit request. We are
disclosing the incident because (a) our registered commitments commit us to
it, and (b) you may want to check whether a route can deliver a different
model than the one a client attests at call time. If you publish
per-request label attestations (e.g., a response header naming the served
model), our future cohorts would prefer it and would cite it.

**What we shipped.** The incident, its detection, and the withdrawal are in
our frozen record (PROVENANCE_CORRECTION.md in the cohort namespace; the
paper's Section 5 and Appendix E document the withdrawal and the fingerprint
audit). The cohort's numbers stand as same-label evidence.

**Contact:** the corresponding author (youss efhamdi329@gmail.com).

— The research team (independent; no production systems involved; all
fixtures local and purpose-built)

---

**Author checklist before sending:** (1) confirm the operator's disclosure
address; (2) attach PROVENANCE_CORRECTION.md; (3) send under the author's
own account; (4) record the sent date in this file (below).

**Sent:** [pending author action]
