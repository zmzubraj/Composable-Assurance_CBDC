# Provisional JFMI compliance checklist - v8

**Status:** provisional trial target, not the confirmed final journal  
**Official requirements checked:** 29 August 2026  
**Official source:** [Risk Journals Submission Guidelines](https://www.risk.net/static/risk-journals-submission-guidelines)  
**Scope source:** [Journal of Financial Market Infrastructures](https://www.risk.net/static/about-the-journal-of-financial-market-infrastructures)

The journal-neutral v8 master remains authoritative. This folder is a reversible adaptation prepared because JFMI is being tried, not because venue selection is final.

| Requirement | Current disposition | Evidence / required action |
|---|---|---|
| Paper is not published or under consideration elsewhere | AUTHOR CONFIRMED | Confirmed by the author on 29 August 2026; the final portal declaration remains a human action. |
| Submission PDF excludes author names and affiliations | PASS | Blinded DOCX/PDF and metadata are checked by `verify_jfmi_v8.py`. |
| Separate title page | PARTIAL | Confirmed name, email and ORCID are populated; affiliation, postal address and corresponding-author status remain unresolved. |
| Running title no more than 50 characters | PASS | `Composable CBDC assurance` is 25 characters. |
| Word, figure and table counts on title page | PASS mechanically | Counts are generated from the blinded source; author must verify portal values. |
| Abstract 150-200 words, standalone | PASS | 185 words and no citations. |
| Four to six keywords | PASS | Six keywords. |
| Three to four key messages, each no more than 85 characters | PASS | Four messages; lengths are recorded in `JFMI_VERIFICATION_V8.json`. |
| Concise descriptive title | AUTHOR CONFIRMED | `Composable assurance for sovereign digital currency (CBDC): An evidence-gated qualification framework`. |
| Main text contains introduction, literature, data/method, results, discussion, conclusion and future research | PASS substantively | Sections use a systems-paper organization but cover every required function. |
| Acknowledgements | BLOCKED ON AUTHOR APPROVAL | Actual AI assistance is disclosed, but the author answered `No` to approval of the proposed wording. The factual use cannot be silently omitted. |
| Declarations of Interest | PARTIAL | Funding is confirmed as self-funded; the conflict-of-interest statement remains unresolved. |
| Author-date in-text citations | PASS | All 44 numeric citations are converted in the JFMI branch. |
| APA-style alphabetized reference list | PASS mechanically | Forty-four references are alphabetized and DOI/URLs retained where available. |
| Research paper guidance of no more than 10,000 words | PASS | Current main text is under the guidance limit. |
| Figures and tables embedded in main PDF | PASS | Sixteen figures and twenty-two numbered tables remain embedded. |
| Separate editable vector figures | PASS mechanically | Sixteen source-generated SVG files, each checked for parseability and absence of embedded raster images. |
| AI use acknowledged and author remains responsible | BLOCKED ON AUTHOR APPROVAL | The provisional disclosure is explicitly marked unapproved; compliant wording must be approved before submission. |
| Supplementary code and data | PREPARED / DEPOSIT GATE | Reproducibility package exists and code is MIT licensed; public repository URL and DOI/Zenodo deposit remain open. |
| Main PDF created from submitted source | PASS mechanically | DOCX and PDF are regenerated in the same build. |
| Final rendered-page review | PENDING | Repeat after all author fields and declarations are approved. |
| Submission portal review and final click | HUMAN GATE | Not authorized or performed. |
| Cover letter | OPTIONAL / GATED TEMPLATE | The checked instructions do not list a cover letter as mandatory. A clearly marked optional template is prepared but retains the manually deferred conflict/AI and correspondence gates. |
| Submission-file inventory | PASS mechanically / FAIL-CLOSED | `JFMI_SUBMISSION_INVENTORY_V8.json` maps every prepared file to requirement, identity class and status, with `submission_ready=false`. |

## Files

- `output/jfmi_provisional/Composable_Assurance_CBDC_JFMI_Blinded_Manuscript_v8.docx`
- `output/jfmi_provisional/Composable_Assurance_CBDC_JFMI_Blinded_Manuscript_v8.pdf`
- `output/jfmi_provisional/Composable_Assurance_CBDC_JFMI_Title_Page_TEMPLATE_v8.docx`
- `output/jfmi_provisional/Composable_Assurance_CBDC_JFMI_Figure_Table_Legends_v8.docx`
- `output/jfmi_provisional/editable_figures/Figure_01.svg` through `Figure_16.svg`
- `docs/JFMI_VERIFICATION_V8.json`
- `docs/JFMI_SCOPE_FIT_V8.md`
- `docs/CITATION_LIVE_VALIDATION_V8.md`
- `docs/COMPLETION_EVIDENCE_MATRIX_V8.md`
- `docs/AUTHOR_DECISION_SHEET_V8.md`
- `docs/JFMI_SUBMISSION_INVENTORY_V8.json`
- `output/jfmi_provisional/Composable_Assurance_CBDC_JFMI_Cover_Letter_TEMPLATE_v8.docx/.pdf`

This checklist establishes mechanical preparation only. It does not represent journal confirmation, peer-review completion, acceptance, or submission authority.
