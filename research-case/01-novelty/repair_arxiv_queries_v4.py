#!/usr/bin/env python3
"""Repair the six arXiv queries and rebuild the canonical deduplication layer.

The first schema-v4 capture sent ungrouped multi-word strings to arXiv. arXiv
parsed those strings as a broad OR expression. This source-specific repair keeps
the Crossref and OpenAlex evidence unchanged, replaces only the six arXiv raw
responses, and then deterministically rebuilds the normalized and deduplicated
artifacts. It never assigns a novelty verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "prior-art-raw"
BACKUP_DIR = ROOT / "pre-arxiv-query-repair-2026-08-29"

ARXIV_QUERIES = {
    "Q001": 'all:"central bank digital currency" AND (all:composable OR all:assurance OR all:interoperability OR all:privacy OR all:AML OR all:"anti-money laundering" OR all:"operational resilience")',
    "Q002": 'all:"central bank digital currency" AND (all:"cross-border" OR all:interoperability) AND (all:atomic OR all:settlement OR all:certificate OR all:ledger)',
    "Q003": 'all:"central bank digital currency" AND (all:privacy OR all:"differential privacy") AND (all:AML OR all:sanctions OR all:compliance OR all:"financial integrity")',
    "Q004": 'all:"central bank digital currency" AND (all:"holding limit" OR all:policy OR all:resilience OR all:scalability OR all:performance)',
    "Q005": 'all:"central bank digital currency" AND (all:evidence OR all:qualification OR all:validation OR all:prototype OR all:benchmark)',
    "Q006": 'all:"central bank digital currency" AND (all:"architecture agnostic" OR all:interoperability OR all:checkpoint OR all:finalization OR all:finality)',
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_arxiv_query(query: str) -> None:
    normalized = " ".join(query.split())
    if not normalized.startswith('all:"central bank digital currenc'):
        raise ValueError("arXiv query must begin with an exact CBDC phrase")
    if " AND " not in normalized:
        raise ValueError("arXiv query must use explicit AND scoping")
    if normalized.count("(") != normalized.count(")"):
        raise ValueError("arXiv query contains unbalanced parentheses")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fetch(url: str, *, mailto: str, retries: int = 3) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"cbdc-novelty-arxiv-query-repair/1.0 (mailto:{mailto})",
            "Accept": "application/atom+xml",
        },
    )
    last_error = ""
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read(20 * 1024 * 1024 + 1)
                if len(body) > 20 * 1024 * 1024:
                    raise RuntimeError("arXiv response exceeds the 20 MiB safety limit")
                if int(response.status) != 200:
                    raise RuntimeError(f"unexpected HTTP status {response.status}")
                return body
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}: {exc.reason}"
            if exc.code not in {429, 500, 502, 503, 504} or attempt == retries:
                break
        except (urllib.error.URLError, TimeoutError, OSError, RuntimeError) as exc:
            last_error = str(exc)
            if attempt == retries:
                break
        time.sleep(min(2 ** (attempt - 1), 8))
    raise RuntimeError(f"arXiv query failed after {retries} attempts: {last_error}")


def parse_arxiv(body: bytes, query_id: str) -> list[dict[str, str]]:
    root = ET.fromstring(body)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    records: list[dict[str, str]] = []
    for index, entry in enumerate(root.findall("atom:entry", namespace), start=1):
        record_id = (entry.findtext("atom:id", default="", namespaces=namespace) or f"{query_id}-{index}").strip()
        records.append(
            {
                "record_id": record_id,
                "query_id": query_id,
                "source": "arxiv_api",
                "title": " ".join((entry.findtext("atom:title", default="", namespaces=namespace) or "").split()),
                "published_at": (entry.findtext("atom:published", default="", namespaces=namespace) or "").strip(),
                "url": record_id,
                "doi": "",
            }
        )
    return records


def normalize_title(value: str) -> str:
    return " ".join(value.lower().split())


def deduplicate(records: list[dict[str, Any]], keys: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    seen: dict[tuple[Any, ...], dict[str, Any]] = {}
    duplicates: list[dict[str, Any]] = []
    ordered = sorted(
        records,
        key=lambda item: (
            str(item.get("query_id", "")),
            normalize_title(str(item.get("title", ""))),
            str(item.get("source", "")),
            str(item.get("record_id", "")),
        ),
    )
    for record in ordered:
        marker_values: list[str] = []
        for key in keys:
            marker_values.append(
                normalize_title(str(record.get("title", ""))) if key == "title_norm" else str(record.get(key, ""))
            )
        marker = tuple(marker_values)
        if marker in seen:
            duplicates.append(
                {
                    "duplicate_record_id": record.get("record_id", ""),
                    "kept_record_id": seen[marker].get("record_id", ""),
                    "dedup_key": list(marker),
                }
            )
        else:
            seen[marker] = record
    unique = list(seen.values())
    unique.sort(
        key=lambda item: (
            str(item.get("query_id", "")),
            normalize_title(str(item.get("title", ""))),
            str(item.get("source", "")),
            str(item.get("record_id", "")),
        )
    )
    return unique, duplicates


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def preserve_pre_repair_evidence() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("prior-art-query-log.json", "prior-art-raw-snapshots.json", "prior-art-dedup-report.json", "search-coverage.csv"):
        source = ROOT / name
        destination = BACKUP_DIR / name
        if source.is_file() and not destination.exists():
            shutil.copy2(source, destination)
    backup_raw = BACKUP_DIR / "prior-art-raw"
    backup_raw.mkdir(exist_ok=True)
    for raw_path in sorted(RAW_DIR.glob("Q???-arxiv_api.xml")):
        destination = backup_raw / raw_path.name
        if not destination.exists():
            shutil.copy2(raw_path, destination)


def repair(*, mailto: str, max_records: int) -> dict[str, Any]:
    if not 1 <= max_records <= 200:
        raise ValueError("max_records must be between 1 and 200")
    for query in ARXIV_QUERIES.values():
        validate_arxiv_query(query)

    query_path = ROOT / "prior-art-query-log.json"
    raw_path = ROOT / "prior-art-raw-snapshots.json"
    dedup_path = ROOT / "prior-art-dedup-report.json"
    query_log = load_json(query_path)
    raw_snapshot = load_json(raw_path)
    dedup_report = load_json(dedup_path)
    preserve_pre_repair_evidence()

    replacement_records: list[dict[str, str]] = []
    replacement_log: dict[str, dict[str, Any]] = {}
    for base_id, query in ARXIV_QUERIES.items():
        query_id = f"{base_id}-arxiv_api"
        endpoint = "https://export.arxiv.org/api/query"
        params = {"search_query": query, "start": 0, "max_results": max_records}
        url = endpoint + "?" + urllib.parse.urlencode(params)
        body = fetch(url, mailto=mailto)
        parsed = parse_arxiv(body, query_id)
        if not parsed:
            raise RuntimeError(f"corrected arXiv query returned no records: {query_id}")
        destination = RAW_DIR / f"{query_id}.xml"
        destination.write_bytes(body)
        replacement_records.extend(parsed)
        replacement_log[query_id] = {
            "query_id": query_id,
            "source": "arxiv_api",
            "endpoint": endpoint,
            "params": params,
            "request_url": url,
            "checked_date": utc_now(),
            "cache_hit": False,
            "status": 200,
            "response_sha256": sha256_bytes(body),
            "raw_path": str(destination),
            "query_semantics": "EXACT_CBDC_PHRASE_WITH_EXPLICIT_BOOLEAN_SCOPING",
            "legacy_query_replaced": True,
        }

    existing_records = [
        record
        for record in raw_snapshot.get("records", [])
        if isinstance(record, dict) and record.get("source") != "arxiv_api"
    ]
    all_records = existing_records + replacement_records
    all_records.sort(
        key=lambda item: (
            str(item.get("query_id", "")),
            normalize_title(str(item.get("title", ""))),
            str(item.get("source", "")),
            str(item.get("record_id", "")),
        )
    )

    query_log["queries"] = sorted(
        [
            replacement_log.get(str(item.get("query_id", "")), item)
            for item in query_log.get("queries", [])
            if isinstance(item, dict)
        ],
        key=lambda item: (str(item.get("query_id", "")), str(item.get("source", ""))),
    )
    query_log["generated_at"] = utc_now()
    query_log["arxiv_query_repair"] = {
        "status": "APPLIED",
        "reason": "legacy ungrouped arXiv strings were parsed as broad OR expressions",
        "backup_path": str(BACKUP_DIR),
        "scientific_verification_performed": False,
    }

    raw_snapshot["records"] = all_records
    raw_snapshot["generated_at"] = utc_now()
    raw_snapshot["arxiv_query_repair_applied"] = True

    keys = list(dedup_report.get("deduplication", {}).get("keys", ["title_norm", "source", "published_at"]))
    unique, duplicates = deduplicate(all_records, keys)
    dedup_report.update(
        {
            "generated_at": utc_now(),
            "input_record_count": len(all_records),
            "unique_record_count": len(unique),
            "duplicate_count": len(duplicates),
            "duplicates": duplicates,
            "unique_records": unique,
            "arxiv_query_repair_applied": True,
        }
    )

    write_json_atomic(query_path, query_log)
    write_json_atomic(raw_path, raw_snapshot)
    write_json_atomic(dedup_path, dedup_report)
    return {
        "status": "PASS",
        "repaired_queries": len(replacement_log),
        "arxiv_records": len(replacement_records),
        "input_records": len(all_records),
        "unique_records": len(unique),
        "duplicates": len(duplicates),
        "scientific_verification_performed": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-network", choices=("yes", "no"), default="no")
    parser.add_argument("--mailto", required=True)
    parser.add_argument("--max-records", type=int, default=25)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.allow_network != "yes":
        raise SystemExit("ERROR: live repair requires --allow-network yes")
    try:
        result = repair(mailto=args.mailto, max_records=args.max_records)
    except (ValueError, RuntimeError, json.JSONDecodeError, ET.ParseError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
