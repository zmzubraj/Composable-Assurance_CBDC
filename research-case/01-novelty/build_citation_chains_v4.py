#!/usr/bin/env python3
"""Normalize captured CEV/SSRN citation-chain metadata without making scientific claims."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHAIN_ROOT = ROOT / "citation-chains"
LEDGER = ROOT / "citation-chain-ledger.csv"
SUMMARY = ROOT / "citation-chain-summary.json"

FIELDS = [
    "chain_id", "seed_id", "seed_title", "direction", "source", "work_id", "title",
    "year", "doi", "decision", "c001_impact", "metadata_status", "scientific_verification",
]

CBDC_TERMS = (
    "cbdc", "central bank digital currency", "central bank digital currencies",
    "multi-cbdc", "digital euro", "e-krona", "e-cny",
)
TECHNICAL_TERMS = (
    "consensus", "byzantine", "sharding", "privacy", "double spending", "blockchain",
    "distributed ledger", "digital payment", "operating architecture",
)


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def classify_title(title: str, direction: str) -> tuple[str, str]:
    lowered = clean(title).casefold()
    is_cbdc = any(term in lowered for term in CBDC_TERMS)
    if direction == "forward":
        if is_cbdc:
            return "RETAIN_CBDC_CITATION", "CHECKS_LATER_INTERPRETATION_OF_CEV"
        return "EXCLUDE_NON_CBDC_CITATION", "NO_C001_IMPACT"
    if is_cbdc:
        return "RETAIN_CBDC_PREDECESSOR", "CHECKS_PRE_CEV_CBDC_SCOPE"
    if any(term in lowered for term in TECHNICAL_TERMS):
        return "RETAIN_TECHNICAL_FOUNDATION", "CONTEXT_FOR_CEV_METHOD_ONLY"
    return "CONTEXTUAL_REFERENCE", "NO_DIRECT_C001_IMPACT"


def normalize_crossref_reference(ref: dict, seed_id: str, direction: str) -> dict[str, str]:
    title = clean(ref.get("article-title") or ref.get("journal-title") or ref.get("series-title") or ref.get("key"))
    decision, impact = classify_title(title, direction)
    return {
        "seed_id": seed_id,
        "direction": direction,
        "source": "crossref_reference_list",
        "work_id": clean(ref.get("key")),
        "title": title,
        "year": clean(ref.get("year")),
        "doi": clean(ref.get("DOI")).lower(),
        "decision": decision,
        "c001_impact": impact,
        "metadata_status": "REFERENCE_METADATA_ONLY",
        "scientific_verification": "NOT_PERFORMED",
    }


def normalize_openalex_work(work: dict, seed_id: str, direction: str) -> dict[str, str]:
    title = clean(work.get("display_name") or work.get("title"))
    decision, impact = classify_title(title, direction)
    return {
        "seed_id": seed_id,
        "direction": direction,
        "source": "openalex_works",
        "work_id": clean(work.get("id")),
        "title": title,
        "year": clean(work.get("publication_year")),
        "doi": clean(work.get("doi")).removeprefix("https://doi.org/").lower(),
        "decision": decision,
        "c001_impact": impact,
        "metadata_status": "PUBLIC_METADATA",
        "scientific_verification": "NOT_PERFORMED",
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_manifest(paths: list[Path], base: Path) -> list[dict[str, object]]:
    return [
        {"path": str(path.relative_to(base)), "bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in sorted(paths)
    ]


def dedup(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    retained: list[dict[str, str]] = []
    for row in rows:
        normalized_title = re.sub(r"[^a-z0-9]+", "", row["title"].casefold())
        match = None
        for current in retained:
            current_title = re.sub(r"[^a-z0-9]+", "", current["title"].casefold())
            if current["seed_id"] != row["seed_id"] or current["direction"] != row["direction"]:
                continue
            if (row["doi"] and current["doi"] == row["doi"]) or (normalized_title and current_title == normalized_title):
                match = current
                break
        if match is None:
            retained.append(dict(row))
            continue
        prefer_row = (
            (not match["doi"] and bool(row["doi"]))
            or (match["source"] != "openalex_works" and row["source"] == "openalex_works")
        )
        if prefer_row:
            replacement = dict(row)
            if not replacement["doi"]:
                replacement["doi"] = match["doi"]
            retained[retained.index(match)] = replacement
        elif not match["doi"] and row["doi"]:
            match["doi"] = row["doi"]
    return sorted(retained, key=lambda row: (row["seed_id"], row["direction"], row["year"], row["title"].casefold()))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> tuple[list[dict[str, str]], dict[str, object]]:
    seeds = {
        "CEV2022": {
            "title": "CEV Framework: A Central Bank Digital Currency Evaluation and Verification Framework With a Focus on Consensus Algorithms and Operating Architectures",
            "dir": CHAIN_ROOT / "cev-2022",
            "openalex_backward": "openalex-backward.json",
            "openalex_forward": "openalex-forward.json",
        },
        "SSRN539": {
            "title": "CBDC Cross-Border Settlement Prototype: Programmable Compliance for Cross-Border CBDC Settlement Using ISO 20022 and FATF Travel Rule Automation",
            "dir": CHAIN_ROOT / "ssrn-5394110",
        },
    }
    rows: list[dict[str, str]] = []
    inputs: list[Path] = []
    for seed_id, seed in seeds.items():
        directory = seed["dir"]
        crossref_path = directory / "crossref-work.json"
        openalex_path = directory / "openalex-work.json"
        inputs.extend([crossref_path, openalex_path])
        message = load_json(crossref_path)["message"]
        for ref in message.get("reference", []):
            rows.append(normalize_crossref_reference(ref, seed_id, "backward"))
        backward_name = seed.get("openalex_backward")
        if backward_name:
            backward_path = directory / str(backward_name)
            inputs.append(backward_path)
            for work in load_json(backward_path).get("results", []):
                rows.append(normalize_openalex_work(work, seed_id, "backward"))
        forward_name = seed.get("openalex_forward")
        if forward_name:
            forward_path = directory / str(forward_name)
            inputs.append(forward_path)
            for work in load_json(forward_path).get("results", []):
                rows.append(normalize_openalex_work(work, seed_id, "forward"))

    rows = dedup(rows)
    for index, row in enumerate(rows, start=1):
        row["chain_id"] = f"CH{index:03d}"
        row["seed_title"] = seeds[row["seed_id"]]["title"]
    counts = Counter((row["seed_id"], row["direction"], row["decision"]) for row in rows)
    summary = {
        "schema_version": 1,
        "cutoff": "2026-08-29",
        "seeds": [
            {
                "seed_id": "CEV2022",
                "doi": "10.1109/ACCESS.2022.3183092",
                "openalex_id": "W4285238892",
                "captured_backward_openalex_records": 26,
                "captured_backward_crossref_references": 48,
                "captured_forward_openalex_records": 24,
            },
            {
                "seed_id": "SSRN539",
                "doi": "10.2139/ssrn.5394110",
                "openalex_id": "W4413502560",
                "captured_backward_openalex_records": 0,
                "captured_backward_crossref_references": 8,
                "captured_forward_openalex_records": 0,
            },
        ],
        "normalized_deduplicated_rows": len(rows),
        "decision_counts": [
            {"seed_id": key[0], "direction": key[1], "decision": key[2], "count": value}
            for key, value in sorted(counts.items())
        ],
        "input_manifest": hash_manifest(inputs, ROOT),
        "scientific_verification_performed": False,
        "independent_challenge_performed": False,
        "novelty_verdict": "UNRESOLVED",
        "limitations": [
            "OpenAlex returned 26 of 35 CEV referenced-work identifiers with public metadata.",
            "Crossref reference entries are variably structured and do not prove full-text claim support.",
            "OpenAlex forward links include false-positive citations and are draft-screened by title only.",
            "SSRN 5394110 has no OpenAlex citation links and no public abstract; its eight Crossref references do not substitute for the unavailable full text.",
        ],
    }
    return rows, summary


def main() -> None:
    rows, summary = build()
    with LEDGER.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ledger": str(LEDGER), "summary": str(SUMMARY), "rows": len(rows), "novelty_verdict": "UNRESOLVED"}, indent=2))


if __name__ == "__main__":
    main()
