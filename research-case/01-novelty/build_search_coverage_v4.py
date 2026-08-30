#!/usr/bin/env python3
"""Build the schema-v4 search-coverage ledger from canonical snapshot metadata."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def normalize_title(value: str) -> str:
    return " ".join(value.lower().split())


def dedup_marker(record: dict, keys: list[str]) -> tuple[str, ...]:
    values = []
    for key in keys:
        if key == "title_norm":
            values.append(normalize_title(str(record.get("title", ""))))
        else:
            values.append(str(record.get(key, "")))
    return tuple(values)


def exact_query(item: dict) -> str:
    params = item.get("params") if isinstance(item.get("params"), dict) else {}
    return str(
        params.get("query.bibliographic")
        or params.get("search")
        or params.get("search_query")
        or ""
    )


def main() -> None:
    query_log = json.loads((ROOT / "prior-art-query-log.json").read_text(encoding="utf-8"))
    raw = json.loads((ROOT / "prior-art-raw-snapshots.json").read_text(encoding="utf-8"))
    dedup = json.loads((ROOT / "prior-art-dedup-report.json").read_text(encoding="utf-8"))
    counts = Counter(str(record["query_id"]) for record in raw["records"])
    screening_path = ROOT / "title-abstract-screening.csv"
    screening: dict[str, str] = {}
    if screening_path.is_file():
        with screening_path.open(encoding="utf-8", newline="") as handle:
            screening = {
                str(row["record_id"]): str(row["decision"])
                for row in csv.DictReader(handle)
            }
    dedup_keys = list(dedup.get("deduplication", {}).get("keys", ["title_norm", "source", "published_at"]))
    kept_by_marker = {
        dedup_marker(record, dedup_keys): str(record.get("record_id", ""))
        for record in dedup.get("unique_records", [])
        if isinstance(record, dict)
    }
    screened_counts: Counter[str] = Counter()
    included_counts: Counter[str] = Counter()
    retained_decisions = {"PRIORITY_FULL_TEXT", "INCLUDE_FULL_TEXT", "RETRIEVE_ABSTRACT_OR_FULL_TEXT"}
    for record in raw["records"]:
        query_id = str(record["query_id"])
        kept_id = kept_by_marker.get(dedup_marker(record, dedup_keys), "")
        decision = screening.get(kept_id, "")
        if decision:
            screened_counts[query_id] += 1
        if decision in retained_decisions:
            included_counts[query_id] += 1
    fieldnames = [
        "query_id",
        "surface",
        "query",
        "searched_at",
        "result_count",
        "screened_count",
        "included_count",
        "access_status",
        "date_range",
        "filters",
        "known_item_recovery",
        "backward_citations",
        "forward_citations",
        "author_lab_follow_up",
        "access_limit",
        "last_new_predecessor",
        "residual_risk",
        "owner",
        "verifier",
    ]
    rows = []
    for item in sorted(query_log["queries"], key=lambda row: str(row["query_id"])):
        query_id = str(item["query_id"])
        rows.append(
            {
                "query_id": query_id,
                "surface": item["source"],
                "query": exact_query(item),
                "searched_at": item.get("checked_date", query_log.get("generated_at", "")),
                "result_count": counts[query_id],
                "screened_count": screened_counts[query_id],
                "included_count": included_counts[query_id],
                "access_status": "PUBLIC_METADATA_CAPTURED;AI_ASSISTED_PRIMARY_SCREEN_DRAFT" if screening else "PUBLIC_METADATA_CAPTURED",
                "date_range": "UNBOUNDED_API_DEFAULT_THROUGH_2026-08-29",
                "filters": "BOUNDED_TOP_25_RESULTS",
                "known_item_recovery": "PARTIAL_TARGETED_ITEMS_TRACKED_IN_EVIDENCE_LEDGER",
                "backward_citations": "NOT_PERFORMED",
                "forward_citations": "NOT_PERFORMED",
                "author_lab_follow_up": "NOT_PERFORMED",
                "access_limit": "PUBLIC_METADATA_ONLY; FULL_TEXT_AND_PROPRIETARY_INDEXES_NOT_EXHAUSTIVE",
                "last_new_predecessor": "PRIORITY_CANDIDATES_RETAINED_FOR_FULL_TEXT_RECONCILIATION" if screening else "NOT_ASSESSED_IN_MECHANICAL_CAPTURE",
                "residual_risk": "ACCOUNTABLE_SCREEN_VERIFICATION_FULL_TEXT_RECONCILIATION_CITATION_CHAINING_AND_INDEPENDENT_CHALLENGE_INCOMPLETE",
                "owner": "primary_novelty_search",
                "verifier": "UNASSIGNED",
            }
        )
    with (ROOT / "search-coverage.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(
        json.dumps(
            {
                "status": "BUILT_DRAFT",
                "rows": len(rows),
                "screened_records_claimed": sum(screened_counts.values()),
                "screening_basis": "AI_ASSISTED_PRIMARY_SCREEN_DRAFT" if screening else "NOT_PERFORMED",
                "scientific_verification_performed": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
