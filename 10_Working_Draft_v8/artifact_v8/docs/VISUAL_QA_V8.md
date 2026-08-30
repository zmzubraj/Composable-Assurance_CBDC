# Visual QA — v8 diagram remediation

**Date:** 2026-08-29  
**Scope:** Author-draft title/identity block plus Figures 2, 3 and 14 in the author draft and provisional blinded manuscript.

## Source changes

- Added consistent centered multi-line text, line spacing and internal whitespace to diagram boxes.
- Title page: set the full publishing title to an explicit 18 pt bold Arial two-line composition, centered it, added balanced space before/after, and placed the author, email and ORCID on a shared center axis with separate contact lines. The deferred-field notice remains absent from the manuscript-facing page.
- Figure 2: separated inbound signed-evidence paths from outbound terminal-certificate paths; placed labels away from connectors and box text.
- Figure 3: corrected vertical arrows to run from each source-box bottom edge to the next target-box top edge; routed cross-lane messages through row gutters; split PREPARE delivery into two outward arrows.
- Figure 14: enlarged and evenly spaced stages, centered the lower-bound equation, increased lower-row box width and improved banner padding.
- Reference layout: compacted only the reference-list typography after adding reference 44, removing a nearly empty orphan page while preserving readable final-size text and hanging indents.
- Preserved the scientific meaning, labels, color semantics and editable SVG outputs.

## Verification evidence

| Check | Result |
|---|---|
| Author title-page rendered inspection | PASS — title has a clear two-line hierarchy; author and email/ORCID lines are centered and evenly spaced |
| Automated title-page contract | PASS — centered two-line title at explicit 18 pt; 12.5 pt author; two centered 10 pt contact lines; deferred-field notice absent |
| Source PNG inspection at native output size | PASS — no clipping, overlap or connector-through-text in the three remediated figures |
| Author PDF rendered-page inspection | PASS — pages 3, 4 and 14 |
| Provisional blinded PDF rendered-page inspection | PASS — pages 3, 4 and 13 |
| Reference pagination | PASS — author and provisional blinded manuscripts both end cleanly on page 17; no two- or three-reference orphan page remains |
| Directionality | PASS — arrowheads terminate at the intended target edge; return paths are visually distinct |
| Box text | PASS — horizontally and vertically centered with consistent multi-line spacing |
| Editable vector preservation | PASS — corresponding SVG files regenerated and accepted by the JFMI verifier |
| Full pipeline | PASS — 14 tests, neutral verifier PASS, JFMI verifier PASS_WITH_AUTHOR_GATES |

This is local rendered-page QA. Final portal-preview inspection remains an accountable-human submission gate after a journal is confirmed.
