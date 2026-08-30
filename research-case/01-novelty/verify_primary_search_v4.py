#!/usr/bin/env python3
"""Fail-closed mechanical verifier for the schema-v4 primary novelty-search package."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CASE = ROOT.parent


def load_json(name: str) -> dict:
    value = json.loads((ROOT / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{name} must contain a JSON object")
    return value


def load_csv(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def require_columns(name: str, headers: list[str], required: set[str]) -> None:
    missing = sorted(required - set(headers))
    assert not missing, f"{name} missing columns: {', '.join(missing)}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_input_manifest(summary: dict, root: Path) -> None:
    manifest = summary.get("input_manifest")
    assert isinstance(manifest, list) and manifest, "citation-chain input manifest must be nonempty"
    seen: set[str] = set()
    for item in manifest:
        assert isinstance(item, dict), "citation-chain manifest entry must be an object"
        relative = str(item.get("path", "")).strip()
        assert relative and relative not in seen, f"duplicate or blank citation-chain manifest path: {relative}"
        seen.add(relative)
        path = root / relative
        assert path.is_file(), f"citation-chain input missing: {path}"
        assert path.stat().st_size == int(item.get("bytes", -1)), f"citation-chain input size mismatch: {path}"
        assert sha256_file(path) == item.get("sha256"), f"citation-chain input hash mismatch: {path}"


def load_csv_at(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def verify_citation_chain_evidence(root: Path = ROOT) -> dict[str, object]:
    summary = json.loads((root / "citation-chain-summary.json").read_text(encoding="utf-8"))
    assert isinstance(summary, dict), "citation-chain summary must be an object"
    assert summary.get("normalized_deduplicated_rows") == 79
    assert summary.get("scientific_verification_performed") is False
    assert summary.get("independent_challenge_performed") is False
    assert summary.get("novelty_verdict") == "UNRESOLVED"
    verify_input_manifest(summary, root)

    ledger_headers, ledger = load_csv_at(root / "citation-chain-ledger.csv")
    require_columns(
        "citation-chain-ledger.csv",
        ledger_headers,
        {
            "chain_id",
            "seed_id",
            "direction",
            "title",
            "decision",
            "c001_impact",
            "metadata_status",
            "scientific_verification",
        },
    )
    assert len(ledger) == 79, "citation-chain ledger row count changed"
    assert len({row["chain_id"] for row in ledger}) == len(ledger), "citation-chain IDs must be unique"
    assert all(row["scientific_verification"] == "NOT_PERFORMED" for row in ledger)
    retained_forward = [
        row
        for row in ledger
        if row["seed_id"] == "CEV2022"
        and row["direction"] == "forward"
        and row["decision"] == "RETAIN_CBDC_CITATION"
    ]
    assert len(retained_forward) == 11, "retained CEV forward-citation count changed"

    feature_headers, features = load_csv_at(root / "cev-feature-reconciliation.csv")
    require_columns(
        "cev-feature-reconciliation.csv",
        feature_headers,
        {
            "feature_id",
            "comparison_axis",
            "cev_2022_full_text_evidence",
            "cev_scope",
            "c001_scope",
            "relationship",
            "disposition",
            "source_location",
            "verification_status",
        },
    )
    assert len(features) == 11, "CEV feature-reconciliation row count changed"
    assert {row["feature_id"] for row in features} == {f"CF{index:02d}" for index in range(1, 12)}
    assert all(row["verification_status"] == "PRIMARY_FULL_TEXT_REVIEWED" for row in features)

    cev_pdf = root / "full-text" / "cev-2022" / "2112.01122v3.pdf"
    cev_text = root / "full-text" / "cev-2022" / "2112.01122v3.txt"
    assert sha256_file(cev_pdf) == "a8c770974c6510e8d9fe55f33ebc8a1bab87b569eca6fd769d04b01e6d7b0fb4"
    assert sha256_file(cev_text) == "baf6a67bd35168c985d2cd8531b193b25b329ef6ce19c31378e91c550e60e4a4"

    _, reconciliation = load_csv_at(root / "priority-candidate-reconciliation.csv")
    cev_candidates = [row for row in reconciliation if row.get("candidate_id") == "P026"]
    assert len(cev_candidates) == 1, "CEV priority-candidate reconciliation missing or duplicated"
    assert cev_candidates[0]["full_text_status"] == "PRIMARY_FULL_TEXT_REVIEWED_AND_HASHED_CITATION_CHAIN_PARTIAL"
    assert cev_candidates[0]["independent_verification"] == "NOT_PERFORMED"

    _, evidence = load_csv_at(root / "evidence-ledger.csv")
    cev_evidence = [row for row in evidence if row.get("evidence_id") == "N017"]
    assert len(cev_evidence) == 1, "N017 evidence row missing or duplicated"
    assert cev_evidence[0]["access_status"] == "PRIMARY_FULL_TEXT_HASHED_AND_CITATION_CHAIN_PARTIAL"

    _, matrix = load_csv_at(root / "novelty-matrix.csv")
    cev_matrix = [row for row in matrix if row.get("predecessor_id") == "N017"]
    assert len(cev_matrix) == 1, "N017 novelty-matrix row missing or duplicated"
    assert cev_matrix[0]["access_status"] == "PRIMARY_FULL_TEXT_HASHED_AND_CITATION_CHAIN_PARTIAL"

    return {
        "citation_chain_rows": len(ledger),
        "cev_feature_rows": len(features),
        "retained_cev_forward_citations": len(retained_forward),
        "novelty_verdict": summary["novelty_verdict"],
        "scientific_verification_performed": summary["scientific_verification_performed"],
        "independent_challenge_performed": summary["independent_challenge_performed"],
    }


def main() -> None:
    query_log = load_json("prior-art-query-log.json")
    raw = load_json("prior-art-raw-snapshots.json")
    dedup = load_json("prior-art-dedup-report.json")

    shared = {"run_id", "adapter_id", "offline_only", "may_assert_novelty"}
    for key in shared:
        assert query_log.get(key) == raw.get(key) == dedup.get(key), f"inconsistent {key}"
    assert query_log.get("live_network_permitted") is True
    assert query_log.get("may_assert_novelty") is False
    assert query_log.get("arxiv_query_repair", {}).get("status") == "APPLIED"

    queries = query_log.get("queries")
    records = raw.get("records")
    unique = dedup.get("unique_records")
    duplicates = dedup.get("duplicates")
    assert isinstance(queries, list) and queries, "query log must be nonempty"
    assert isinstance(records, list) and records, "raw records must be nonempty"
    assert isinstance(unique, list) and unique, "unique records must be nonempty"
    assert isinstance(duplicates, list), "duplicates must be an array"

    query_ids = [str(item.get("query_id", "")).strip() for item in queries]
    assert all(query_ids) and len(query_ids) == len(set(query_ids)), "query IDs must be unique"
    query_id_set = set(query_ids)

    for query in queries:
        for field in ("source", "request_url", "response_sha256", "raw_path"):
            assert str(query.get(field, "")).strip(), f"{query['query_id']} missing {field}"
        raw_path = Path(str(query["raw_path"]))
        assert raw_path.is_file(), f"missing raw response: {raw_path}"
        digest = hashlib.sha256(raw_path.read_bytes()).hexdigest()
        assert digest == query["response_sha256"], f"raw hash mismatch: {raw_path}"
        if query.get("source") == "arxiv_api":
            search_query = str(query.get("params", {}).get("search_query", ""))
            assert search_query.startswith('all:"central bank digital currenc')
            assert " AND " in search_query
            assert query.get("query_semantics") == "EXACT_CBDC_PHRASE_WITH_EXPLICIT_BOOLEAN_SCOPING"

    record_markers: set[tuple[str, str, str]] = set()
    raw_ids: set[str] = set()
    counts: Counter[str] = Counter()
    for record in records:
        required = {"record_id", "query_id", "source", "title", "published_at", "url"}
        assert not (required - set(record)), "raw record lacks canonical metadata"
        query_id = str(record["query_id"])
        record_id = str(record["record_id"])
        source = str(record["source"])
        assert query_id in query_id_set, f"unknown query ID: {query_id}"
        marker = (query_id, source, record_id)
        assert record_id and marker not in record_markers, f"duplicate raw identity: {marker}"
        record_markers.add(marker)
        raw_ids.add(record_id)
        counts[query_id] += 1

    assert dedup.get("input_record_count") == len(records)
    assert dedup.get("unique_record_count") == len(unique)
    assert dedup.get("duplicate_count") == len(duplicates)
    assert len(records) == len(unique) + len(duplicates)
    unique_ids = {str(item.get("record_id", "")) for item in unique}
    assert unique_ids <= raw_ids
    for duplicate in duplicates:
        assert str(duplicate.get("duplicate_record_id", "")) in raw_ids
        assert str(duplicate.get("kept_record_id", "")) in unique_ids

    coverage_headers, coverage = load_csv("search-coverage.csv")
    require_columns(
        "search-coverage.csv",
        coverage_headers,
        {"query_id", "surface", "query", "searched_at", "result_count", "screened_count", "access_status"},
    )
    assert len(coverage) == len(queries), "coverage must contain one row per source-query retrieval"
    assert {row["query_id"] for row in coverage} == query_id_set
    for row in coverage:
        assert int(row["result_count"]) >= counts[row["query_id"]]
        assert 0 <= int(row["screened_count"]) <= int(row["result_count"])

    screening_headers, screening = load_csv("title-abstract-screening.csv")
    require_columns(
        "title-abstract-screening.csv",
        screening_headers,
        {
            "record_id",
            "query_id",
            "source",
            "title",
            "decision",
            "novelty_axes",
            "evidence_basis",
            "review_status",
            "claim_ids",
            "scientific_verification_performed",
        },
    )
    allowed_decisions = {
        "EXCLUDE_GENERIC_CBDC",
        "EXCLUDE_NO_C001_OVERLAP",
        "EXCLUDE_OUT_OF_SCOPE",
        "INCLUDE_FULL_TEXT",
        "PRIORITY_FULL_TEXT",
        "RETRIEVE_ABSTRACT_OR_FULL_TEXT",
    }
    screening_ids = [row["record_id"] for row in screening]
    assert len(screening) == len(unique), "screening ledger must cover every unique record"
    assert len(screening_ids) == len(set(screening_ids)), "screening record IDs must be unique"
    assert set(screening_ids) == unique_ids, "screening ledger must exactly match deduplicated records"
    assert all(row["decision"] in allowed_decisions for row in screening)
    assert all(row["claim_ids"] == "C001" for row in screening)
    assert all(row["scientific_verification_performed"] == "false" for row in screening)
    assert all(row["review_status"] == "AI_ASSISTED_PRIMARY_SCREEN_DRAFT" for row in screening)
    assert sum(int(row["screened_count"]) for row in coverage) == len(records)

    reconciliation_headers, reconciliation = load_csv("priority-candidate-reconciliation.csv")
    require_columns(
        "priority-candidate-reconciliation.csv",
        reconciliation_headers,
        {
            "candidate_id",
            "record_id",
            "screening_disposition",
            "c001_overlap",
            "material_difference_or_exclusion_reason",
            "access_status",
            "full_text_status",
            "claim_impact",
            "independent_verification",
        },
    )
    candidate_ids = [row["candidate_id"] for row in reconciliation]
    assert len(candidate_ids) == len(set(candidate_ids)), "candidate IDs must be unique"
    priority_ids = {row["record_id"] for row in screening if row["decision"] == "PRIORITY_FULL_TEXT"}
    assert {row["record_id"] for row in reconciliation} == priority_ids
    assert all(row["independent_verification"] == "NOT_PERFORMED" for row in reconciliation)

    evidence_headers, evidence = load_csv("evidence-ledger.csv")
    require_columns(
        "evidence-ledger.csv",
        evidence_headers,
        {"evidence_id", "claim_ids", "source_type", "title", "identifier", "decision", "reason", "checked_at"},
    )
    assert evidence and len({row["evidence_id"] for row in evidence}) == len(evidence)
    assert all(row["claim_ids"] == "C001" for row in evidence)

    matrix_headers, matrix = load_csv("novelty-matrix.csv")
    require_columns(
        "novelty-matrix.csv",
        matrix_headers,
        {"claim_id", "predecessor_id", "material_difference", "defeating_evidence", "residual_uncertainty"},
    )
    assert matrix and all(row["claim_id"] == "C001" for row in matrix)

    citation_chain = verify_citation_chain_evidence(ROOT)

    challenge = (ROOT / "independent-search-challenge.md").read_text(encoding="utf-8").upper()
    assert "NOT_PERFORMED" in challenge and "NOVELTY" in challenge and "UNRESOLVED" in challenge

    print(
        json.dumps(
            {
                "status": "PASS",
                "run_id": query_log["run_id"],
                "queries": len(queries),
                "raw_records": len(records),
                "unique_records": len(unique),
                "duplicates": len(duplicates),
                "screened_unique_records": len(screening),
                "priority_candidates_reconciled": len(reconciliation),
                "evidence_rows": len(evidence),
                "matrix_rows": len(matrix),
                **citation_chain,
                "novelty_verdict": "UNRESOLVED",
                "scientific_verification_performed": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
