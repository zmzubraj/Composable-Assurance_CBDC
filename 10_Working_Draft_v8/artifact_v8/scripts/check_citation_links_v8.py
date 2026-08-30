#!/usr/bin/env python3
"""Create a dated, non-semantic availability snapshot for cited primary URLs."""

from __future__ import annotations

import json
import re
import ssl
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "CITATION_AUDIT_V8.md"
OUTPUT = ROOT / "docs" / "CITATION_LINK_CHECK_V8.json"
USER_AGENT = "CBDC-publication-reproducibility-check/8.0 (+local research QA)"
TIMEOUT_SECONDS = 20


def extract_rows() -> list[tuple[int, str]]:
    text = SOURCE.read_text(encoding="utf-8")
    rows: list[tuple[int, str]] = []
    for line in text.splitlines():
        match = re.match(r"\|\s*(\d+)\s*\|.*?\]\((https://[^)]+)\)", line)
        if match:
            rows.append((int(match.group(1)), match.group(2)))
    if [number for number, _ in rows] != list(range(1, 45)):
        raise RuntimeError("expected exactly one ordered primary URL for references 1-44")
    return rows


def probe(number: int, url: str) -> dict[str, object]:
    context = ssl.create_default_context()
    attempts: list[dict[str, object]] = []
    for method in ("HEAD", "GET"):
        headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf,*/*;q=0.8"}
        if method == "GET":
            headers["Range"] = "bytes=0-4095"
        request = Request(url, headers=headers, method=method)
        try:
            with urlopen(request, timeout=TIMEOUT_SECONDS, context=context) as response:
                status = int(response.status)
                result = {
                    "reference": number,
                    "requested_url": url,
                    "final_url": response.geturl(),
                    "http_status": status,
                    "content_type": response.headers.get_content_type(),
                    "method": method,
                    "disposition": "REACHABLE" if 200 <= status < 400 else "HTTP_ERROR",
                    "attempts": attempts + [{"method": method, "status": status}],
                }
                return result
        except HTTPError as exc:
            attempts.append({"method": method, "status": int(exc.code), "error": str(exc.reason)})
            if method == "GET" or exc.code not in {403, 405, 406, 429, 501}:
                break
        except (URLError, TimeoutError, OSError) as exc:
            attempts.append({"method": method, "error": f"{type(exc).__name__}: {exc}"})
            if method == "GET":
                break
    curl = subprocess.run(
        [
            "curl",
            "--location",
            "--silent",
            "--show-error",
            "--output",
            "/dev/null",
            "--max-time",
            "30",
            "--connect-timeout",
            "10",
            "--range",
            "0-4095",
            "--user-agent",
            USER_AGENT,
            "--write-out",
            "%{http_code}\t%{url_effective}\t%{content_type}",
            url,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    curl_fields = curl.stdout.strip().split("\t", 2)
    if len(curl_fields) == 3 and curl_fields[0].isdigit():
        curl_status = int(curl_fields[0])
        attempts.append(
            {
                "method": "CURL_RANGE_GET",
                "status": curl_status,
                "returncode": curl.returncode,
                "stderr": curl.stderr.strip() or None,
            }
        )
        if 200 <= curl_status < 400:
            return {
                "reference": number,
                "requested_url": url,
                "final_url": curl_fields[1],
                "http_status": curl_status,
                "content_type": curl_fields[2] or None,
                "method": "CURL_RANGE_GET",
                "disposition": "REACHABLE",
                "attempts": attempts,
            }
    elif curl.stderr.strip():
        attempts.append(
            {
                "method": "CURL_RANGE_GET",
                "returncode": curl.returncode,
                "error": curl.stderr.strip(),
            }
        )

    last = attempts[-1]
    status = last.get("status")
    disposition = "ACCESS_RESTRICTED" if status in {401, 403, 406, 429} else "UNREACHABLE"
    return {
        "reference": number,
        "requested_url": url,
        "final_url": None,
        "http_status": status,
        "content_type": None,
        "method": None,
        "disposition": disposition,
        "attempts": attempts,
    }


def main() -> None:
    rows = extract_rows()
    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(probe, number, url): number for number, url in rows}
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: int(item["reference"]))
    counts: dict[str, int] = {}
    for result in results:
        disposition = str(result["disposition"])
        counts[disposition] = counts.get(disposition, 0) + 1
    payload = {
        "schema_version": 1,
        "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": str(SOURCE.relative_to(ROOT)),
        "user_agent": USER_AGENT,
        "timeout_seconds": TIMEOUT_SECONDS,
        "reference_count": len(results),
        "summary": counts,
        "interpretation_boundary": (
            "HTTP reachability is a maintenance signal only. It does not verify bibliographic "
            "metadata, claim support, novelty, scientific validity, or unrestricted full-text access."
        ),
        "results": results,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "reference_count": len(results), "summary": counts}, indent=2))


if __name__ == "__main__":
    main()
