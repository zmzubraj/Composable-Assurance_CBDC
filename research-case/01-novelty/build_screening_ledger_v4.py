#!/usr/bin/env python3
"""Build an auditable AI-assisted title/abstract screening ledger.

This is a primary-screening aid, not an independent novelty determination.
Records lacking an abstract are never finally excluded merely because the title
does not expose a claim-relevant mechanism.
"""

from __future__ import annotations

import csv
import html
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent

CBDC_ANCHORS = (
    "cbdc",
    "central bank digital currency",
    "central bank digital currencies",
    "digital euro",
    "digital pound",
    "sovereign digital currency",
    "multi-cbdc",
    "m-cbdc",
)

AXIS_TERMS = {
    "qualification": (
        "assurance",
        "qualification",
        "evidence gate",
        "evidence maturity",
        "validation",
        "verification",
        "benchmark",
        "prototype",
        "evaluation framework",
        "formal method",
        "formal validation",
    ),
    "settlement_interoperability": (
        "cross-border",
        "cross border",
        "atomic settlement",
        "settlement",
        "interoperability",
        "interoperable",
        "independent ledger",
        "multiple ledger",
        "multi-ledger",
        "finality",
        "finalization",
        "checkpoint",
        "funds locking",
        "payment channel",
    ),
    "privacy": (
        "privacy",
        "anonymous",
        "anonymity",
        "unlinkability",
        "differential privacy",
        "zero-knowledge",
        "zero knowledge",
        "selective disclosure",
        "confidentiality",
    ),
    "financial_integrity": (
        "aml",
        "anti-money laundering",
        "sanction",
        "compliance",
        "kyc",
        "financial integrity",
        "travel rule",
        "illicit finance",
    ),
    "policy_limits": (
        "holding limit",
        "holding cap",
        "wallet limit",
        "transaction limit",
        "programmable limit",
        "policy rule",
        "adaptive limit",
    ),
    "resilience_scale": (
        "operational resilience",
        "cyber resilience",
        "scalability",
        "performance",
        "throughput",
        "fault tolerance",
        "failure mode",
        "stress test",
        "availability",
        "overload",
        "queueing",
        "queue",
    ),
}

GENERIC_CBDC_TERMS = (
    "monetary policy",
    "bank profitability",
    "bank run",
    "bank-run",
    "money demand",
    "transactional demand",
    "financial inclusion",
    "consumer adoption",
    "adoption intention",
    "welfare",
    "disintermediation",
    "interest rate",
    "macroeconomic",
    "economic growth",
)


def normalize(value: str) -> str:
    return " ".join(value.lower().replace("–", "-").replace("—", "-").split())


def classify_record(title: str, abstract: str) -> tuple[str, str, str]:
    title_norm = normalize(title)
    abstract_norm = normalize(abstract)
    combined = f"{title_norm} {abstract_norm}".strip()
    has_anchor = any(term in combined for term in CBDC_ANCHORS)
    axes = sorted(
        axis
        for axis, terms in AXIS_TERMS.items()
        if any(term in combined for term in terms)
    )
    axes_text = ";".join(axes)

    if not has_anchor:
        return "EXCLUDE_OUT_OF_SCOPE", axes_text, "No CBDC or named sovereign-digital-currency anchor in title/abstract"
    if not abstract_norm and not axes:
        return (
            "RETRIEVE_ABSTRACT_OR_FULL_TEXT",
            axes_text,
            "CBDC anchor present but metadata lacks enough mechanism detail for a safe exclusion",
        )

    high_interaction = (
        {"settlement_interoperability", "financial_integrity"} <= set(axes)
        or {"privacy", "financial_integrity"} <= set(axes)
        or ("qualification" in axes and len(axes) >= 3)
        or (
            "qualification" in axes
            and any(
                phrase in combined
                for phrase in ("evaluation and verification framework", "verification framework", "recommend and verify")
            )
        )
        or len(axes) >= 4
    )
    if high_interaction:
        return (
            "PRIORITY_FULL_TEXT",
            axes_text,
            "Multiple C001 assurance surfaces interact and may materially narrow or defeat the claim",
        )
    if axes:
        return (
            "INCLUDE_FULL_TEXT",
            axes_text,
            "At least one C001 assurance surface is present; full-text reconciliation required",
        )
    if any(term in combined for term in GENERIC_CBDC_TERMS):
        return (
            "EXCLUDE_GENERIC_CBDC",
            axes_text,
            "CBDC record is macroeconomic, adoption, welfare or banking-impact work without a C001 mechanism axis",
        )
    if not abstract_norm:
        return (
            "RETRIEVE_ABSTRACT_OR_FULL_TEXT",
            axes_text,
            "CBDC title is insufficient for a final title-only exclusion",
        )
    return (
        "EXCLUDE_NO_C001_OVERLAP",
        axes_text,
        "Title/abstract concerns CBDC but does not expose a claim-matched qualification or assurance mechanism",
    )


def invert_abstract(index: Any) -> str:
    if not isinstance(index, dict):
        return ""
    positioned: list[tuple[int, str]] = []
    for word, positions in index.items():
        if not isinstance(positions, list):
            continue
        for position in positions:
            if isinstance(position, int):
                positioned.append((position, str(word)))
    return " ".join(word for _, word in sorted(positioned))


def clean_markup(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


def raw_abstracts(query_log: dict[str, Any]) -> dict[str, str]:
    abstracts: dict[str, str] = {}
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    for query in query_log.get("queries", []):
        if not isinstance(query, dict):
            continue
        source = str(query.get("source", ""))
        path = Path(str(query.get("raw_path", "")))
        if not path.is_file():
            continue
        if source == "arxiv_api":
            root = ET.fromstring(path.read_bytes())
            for entry in root.findall("atom:entry", namespace):
                record_id = (entry.findtext("atom:id", default="", namespaces=namespace) or "").strip()
                summary = " ".join((entry.findtext("atom:summary", default="", namespaces=namespace) or "").split())
                if record_id and summary:
                    abstracts.setdefault(record_id, summary)
        elif source == "openalex_works":
            payload = json.loads(path.read_text(encoding="utf-8"))
            for item in payload.get("results", []):
                if not isinstance(item, dict):
                    continue
                record_id = str(item.get("id") or "")
                abstract = invert_abstract(item.get("abstract_inverted_index"))
                if record_id and abstract:
                    abstracts.setdefault(record_id, abstract)
        elif source == "crossref_rest_v1":
            payload = json.loads(path.read_text(encoding="utf-8"))
            for item in payload.get("message", {}).get("items", []):
                if not isinstance(item, dict):
                    continue
                record_id = str(item.get("DOI") or item.get("URL") or "")
                abstract = clean_markup(item.get("abstract"))
                if record_id and abstract:
                    abstracts.setdefault(record_id, abstract)
    return abstracts


def main() -> None:
    query_log = json.loads((ROOT / "prior-art-query-log.json").read_text(encoding="utf-8"))
    dedup = json.loads((ROOT / "prior-art-dedup-report.json").read_text(encoding="utf-8"))
    abstracts = raw_abstracts(query_log)
    records = dedup.get("unique_records", [])
    if not isinstance(records, list) or not records:
        raise SystemExit("ERROR: canonical unique-record set is empty")

    fieldnames = [
        "record_id",
        "query_id",
        "source",
        "title",
        "published_at",
        "url",
        "doi",
        "abstract_available",
        "abstract_characters",
        "decision",
        "novelty_axes",
        "reason",
        "evidence_basis",
        "full_text_status",
        "review_status",
        "reviewed_at",
        "claim_ids",
        "scientific_verification_performed",
    ]
    rows: list[dict[str, Any]] = []
    for record in records:
        record_id = str(record.get("record_id", ""))
        abstract = abstracts.get(record_id, "")
        decision, axes, reason = classify_record(str(record.get("title", "")), abstract)
        rows.append(
            {
                "record_id": record_id,
                "query_id": str(record.get("query_id", "")),
                "source": str(record.get("source", "")),
                "title": str(record.get("title", "")),
                "published_at": str(record.get("published_at", "")),
                "url": str(record.get("url", "")),
                "doi": str(record.get("doi", "")),
                "abstract_available": str(bool(abstract)).lower(),
                "abstract_characters": len(abstract),
                "decision": decision,
                "novelty_axes": axes,
                "reason": reason,
                "evidence_basis": "TITLE_AND_ABSTRACT" if abstract else "TITLE_ONLY",
                "full_text_status": "NOT_REVIEWED",
                "review_status": "AI_ASSISTED_PRIMARY_SCREEN_DRAFT",
                "reviewed_at": date.today().isoformat(),
                "claim_ids": "C001",
                "scientific_verification_performed": "false",
            }
        )

    output_path = ROOT / "title-abstract-screening.csv"
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(str(row["decision"]) for row in rows)
    summary = {
        "status": "DRAFT_PRIMARY_SCREEN_COMPLETE",
        "run_id": query_log.get("run_id", ""),
        "unique_records": len(rows),
        "abstracts_available": sum(row["abstract_available"] == "true" for row in rows),
        "decisions": dict(sorted(counts.items())),
        "scientific_verification_performed": False,
        "independent_challenge_performed": False,
        "novelty_verdict": "UNRESOLVED",
        "limitations": [
            "Rule-based AI-assisted primary screen requires accountable verification",
            "Included records still require full-text reconciliation",
            "Citation chaining and independent search challenge remain incomplete",
        ],
    }
    (ROOT / "title-abstract-screening-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
