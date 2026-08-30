#!/usr/bin/env python3
"""Run a bounded, reproducible public-metadata search for the CBDC novelty audit."""

from __future__ import annotations

import base64
import csv
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


OUT = Path(__file__).resolve().parent
CUTOFF = "2026-08-29"
USER_AGENT = "CBDC-publication-novelty-audit/1.0 (mailto:zmzubraj@gmail.com)"
QUERIES = {
    "Q1_joint_assurance": "central bank digital currency composable assurance privacy AML interoperability operational resilience",
    "Q2_cross_border_atomicity": "cross-border CBDC atomic settlement independent ledgers compliance certificate",
    "Q3_privacy_integrity": "central bank digital currency privacy AML compliance by design selective disclosure",
    "Q4_policy_scale": "CBDC holding limits scalability operational resilience qualification pilot",
    "Q5_evidence_maturity": "CBDC evidence qualification framework prototype deployment validation",
    "Q6_architecture_agnostic": "CBDC architecture agnostic interoperability checkpoint reserve lock finalize",
}


def fetch(url: str) -> tuple[bytes, dict[str, str]]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json, application/xml;q=0.9, */*;q=0.8"})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
        headers = {key.lower(): value for key, value in response.headers.items()}
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {url}")
        return body, headers


def norm_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def doi_key(value: str | None) -> str | None:
    if not value:
        return None
    value = value.lower().strip()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value)
    return value or None


def openalex_records(payload: dict) -> list[dict]:
    records = []
    for item in payload.get("results", []):
        authors = []
        for authorship in item.get("authorships") or []:
            name = (authorship.get("author") or {}).get("display_name")
            if name:
                authors.append(name)
        location = item.get("primary_location") or {}
        source = location.get("source") or {}
        records.append({
            "source": "OpenAlex",
            "id": item.get("id"),
            "doi": doi_key(item.get("doi")),
            "title": item.get("title") or "",
            "year": item.get("publication_year"),
            "authors": authors,
            "container": source.get("display_name"),
            "type": item.get("type"),
            "url": item.get("doi") or item.get("id"),
            "cited_by_count": item.get("cited_by_count"),
        })
    return records


def crossref_records(payload: dict) -> list[dict]:
    records = []
    message = payload.get("message") or {}
    if payload.get("status") != "ok" or not isinstance(message.get("items"), list):
        raise RuntimeError("Crossref returned an invalid application-level response")
    for item in message["items"]:
        title = (item.get("title") or [""])[0]
        authors = [" ".join(filter(None, [author.get("given"), author.get("family")])) for author in item.get("author") or []]
        date_parts = ((item.get("published") or {}).get("date-parts") or [[None]])[0]
        records.append({
            "source": "Crossref",
            "id": item.get("DOI"),
            "doi": doi_key(item.get("DOI")),
            "title": title,
            "year": date_parts[0] if date_parts else None,
            "authors": authors,
            "container": (item.get("container-title") or [None])[0],
            "type": item.get("type"),
            "url": item.get("URL"),
            "cited_by_count": item.get("is-referenced-by-count"),
        })
    return records


def arxiv_records(body: bytes) -> list[dict]:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(body)
    records = []
    for entry in root.findall("a:entry", ns):
        identifier = (entry.findtext("a:id", default="", namespaces=ns) or "").strip()
        published = entry.findtext("a:published", default="", namespaces=ns)
        records.append({
            "source": "arXiv",
            "id": identifier,
            "doi": None,
            "title": " ".join((entry.findtext("a:title", default="", namespaces=ns) or "").split()),
            "year": int(published[:4]) if published[:4].isdigit() else None,
            "authors": [author.findtext("a:name", default="", namespaces=ns) for author in entry.findall("a:author", ns)],
            "container": "arXiv",
            "type": "preprint",
            "url": identifier,
            "cited_by_count": None,
        })
    return records


def deduplicate(records: list[dict]) -> tuple[list[dict], list[dict]]:
    kept: dict[str, dict] = {}
    duplicates: list[dict] = []
    for record in records:
        title_key = norm_title(record["title"])
        key = f"doi:{record['doi']}" if record.get("doi") else f"title:{title_key}"
        if not title_key:
            continue
        if key in kept:
            duplicates.append({"key": key, "kept_source": kept[key]["source"], "duplicate_source": record["source"], "title": record["title"]})
            kept[key]["query_ids"] = sorted(set(kept[key]["query_ids"] + record["query_ids"]))
            kept[key]["retrieved_from"] = sorted(set(kept[key]["retrieved_from"] + record["retrieved_from"]))
        else:
            kept[key] = record
    return sorted(kept.values(), key=lambda row: (-(row.get("year") or 0), row["title"].lower())), duplicates


def main() -> None:
    started = datetime.now(timezone.utc).isoformat()
    snapshots = []
    query_log = []
    records = []
    coverage_rows = []

    for query_id, query in QUERIES.items():
        for database in ("OpenAlex", "Crossref"):
            if database == "OpenAlex":
                params = {"search": query, "per-page": "25", "page": "1", "select": "id,doi,title,publication_year,authorships,primary_location,type,cited_by_count"}
                url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
            else:
                params = {"query.bibliographic": query, "rows": "25", "select": "DOI,title,author,published,type,URL,is-referenced-by-count,container-title"}
                url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
            fetched_at = datetime.now(timezone.utc).isoformat()
            body, headers = fetch(url)
            payload = json.loads(body)
            parsed = openalex_records(payload) if database == "OpenAlex" else crossref_records(payload)
            for record in parsed:
                record["query_ids"] = [query_id]
                record["retrieved_from"] = [database]
            records.extend(parsed)
            total = (payload.get("meta") or {}).get("count") if database == "OpenAlex" else (payload.get("message") or {}).get("total-results")
            snapshots.append({
                "query_id": query_id,
                "database": database,
                "url": url,
                "parameters": params,
                "fetched_at_utc": fetched_at,
                "sha256": hashlib.sha256(body).hexdigest(),
                "content_type": headers.get("content-type"),
                "raw_response_base64": base64.b64encode(body).decode("ascii"),
            })
            query_log.append({"query_id": query_id, "database": database, "query": query, "url": url, "fetched_at_utc": fetched_at, "reported_total": total, "bounded_records": len(parsed), "status": "SUCCESS"})
            coverage_rows.append({"query_id": query_id, "surface": database, "query": query, "reported_total": total, "screening_cap": 25, "retrieved": len(parsed), "coverage_status": "BOUNDED_TOP_RESULTS_ONLY", "cutoff": CUTOFF})
            time.sleep(0.25)

    for query_id in ("Q1_joint_assurance", "Q2_cross_border_atomicity", "Q3_privacy_integrity"):
        query = QUERIES[query_id]
        arxiv_query = f'all:"{query}"'
        params = {"search_query": arxiv_query, "start": "0", "max_results": "20", "sortBy": "relevance", "sortOrder": "descending"}
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
        fetched_at = datetime.now(timezone.utc).isoformat()
        body, headers = fetch(url)
        parsed = arxiv_records(body)
        for record in parsed:
            record["query_ids"] = [query_id]
            record["retrieved_from"] = ["arXiv"]
        records.extend(parsed)
        snapshots.append({"query_id": query_id, "database": "arXiv", "url": url, "parameters": params, "fetched_at_utc": fetched_at, "sha256": hashlib.sha256(body).hexdigest(), "content_type": headers.get("content-type"), "raw_response_base64": base64.b64encode(body).decode("ascii")})
        query_log.append({"query_id": query_id, "database": "arXiv", "query": arxiv_query, "url": url, "fetched_at_utc": fetched_at, "reported_total": None, "bounded_records": len(parsed), "status": "SUCCESS"})
        coverage_rows.append({"query_id": query_id, "surface": "arXiv", "query": arxiv_query, "reported_total": "", "screening_cap": 20, "retrieved": len(parsed), "coverage_status": "BOUNDED_TOP_RESULTS_ONLY", "cutoff": CUTOFF})
        time.sleep(0.5)

    unique, duplicates = deduplicate(records)
    completed = datetime.now(timezone.utc).isoformat()
    (OUT / "prior-art-query-log.json").write_text(json.dumps({"schema_version": 1, "cutoff": CUTOFF, "started_at_utc": started, "completed_at_utc": completed, "queries": query_log}, indent=2) + "\n")
    (OUT / "prior-art-raw-snapshots.json").write_text(json.dumps({"schema_version": 1, "retrievals": snapshots}, indent=2) + "\n")
    (OUT / "prior-art-dedup-report.json").write_text(json.dumps({"schema_version": 1, "input_records": len(records), "unique_records": len(unique), "duplicate_records": len(duplicates), "duplicates": duplicates, "normalized_records": unique}, indent=2) + "\n")
    with (OUT / "search-coverage.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(coverage_rows[0]))
        writer.writeheader()
        writer.writerows(coverage_rows)
    print(json.dumps({"status": "PASS", "queries": len(query_log), "input_records": len(records), "unique_records": len(unique), "duplicates": len(duplicates), "cutoff": CUTOFF}, indent=2))


if __name__ == "__main__":
    main()
