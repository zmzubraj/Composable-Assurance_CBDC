# Live citation availability validation — v8

**Checked:** 29 August 2026  
**Scope:** the primary verification URL for each of the 44 references in `CITATION_AUDIT_V8.md`  
**Machine-readable snapshot:** `CITATION_LINK_CHECK_V8.json`

## Result

| Disposition | Count | Interpretation |
|---|---:|---|
| `REACHABLE` | 37 | The primary URL returned an HTTP success/redirect response through the reproducible checker. |
| `ACCESS_RESTRICTED` | 6 | The publisher endpoint returned HTTP 403 to automated requests; this is not evidence that the item is absent. |
| `UNREACHABLE` | 1 | The ISO catalogue endpoint timed out during the local probe; current official search indexing independently exposed the same page and description. |

## Restricted-endpoint fallbacks

- References 6 and 8: DOI redirects were blocked by the ACM endpoint, but Crossref REST metadata returned the exact DOI, title, authors, venue, date, and pages for `10.1145/1132863.1132867` and `10.1145/3293611.3331591`.
- References 33, 34, and 37: current IMF publication/search pages exposed the cited titles, authorship or institutional metadata, issue identifiers, dates, and DOI records despite direct automated HTTP 403 responses from some IMF/eLibrary endpoints.
- Reference 40: the SSRN DOI endpoint returned HTTP 403 to the automated checker; the SSRN paper page and Crossref metadata exposed the exact title, authors, posting date and DOI.
- Reference 29: the official ISO 20022 indexed page confirmed that the catalogue provides current approved message-definition versions. The manuscript already limits the claim by requiring an implementation to freeze exact message and schema versions.
- Reference 44: the CEV DOI resolved successfully in the fresh link snapshot; its bibliographic metadata and framework scope were also checked against the public arXiv record and IEEE publication details.

## Reproduction

```bash
python scripts/check_citation_links_v8.py
```

The checker performs an HTTPS `HEAD`, bounded `GET`, and `curl` range fallback with a declared user agent. It records redirects, content type, HTTP status, access restrictions, errors, and the exact UTC check time.

## Interpretation boundary

Link availability is a maintenance check only. It does not establish that a source supports every manuscript claim, prove novelty, replace full-text screening, or independently replicate results. `CITATION_AUDIT_V8.md` remains the semantic bibliographic audit, and a submission-time refresh remains necessary.
