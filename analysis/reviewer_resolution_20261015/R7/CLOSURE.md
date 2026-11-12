# R7: role diagrams versus access enforcement

Disposition: **addressed**. Figure1 now says task oracle, truth ownership with varying access, assumed trust, agent-controlled interaction and remaining host access. It no longer asserts that all generated actions stay inside task interfaces or that truth is outside the agent path. Figure2 now distinguishes verification roles from access isolation, forwarding from blinding, and key ownership from enforced secrecy. Its footer calls for separate host/access checks.

FIGURE_LABEL_PATCH.json preserves both pre-change sources and the exact13 text replacements. Replaying only those replacements reproduces each current source byte-for-byte. Drawing commands, coordinates, colors, fonts, arrows and data remain unchanged. This corrects semantics within the original style; it does not redesign the figures or claim to solve R14's reduced-size legibility concern.

The regenerated Figure2 was visually inspected. Main/combined builds and the20-check preservation/reporting regression pass at13/5/18 pages. Figure1's actual access interpretation is supplied by the authority table and source trace from R6. No new isolation experiment was represented as historical evidence.
