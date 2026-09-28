"""Fail closed on secret-scan findings outside four immutable evidence digests."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EVIDENCE_PATH = "docs/verification/sentient-identity-20260928.json"
KNOWN_DIGESTS = {
    2: ("base_sha", (212, 23, 177, 43, 109, 225, 121, 113, 95, 26, 1, 122, 52, 232, 212, 94, 21, 129, 180, 186)),
    4: ("source_manifest_sha256", (61, 235, 121, 179, 44, 4, 177, 65, 138, 132, 219, 88, 46, 1, 197, 247, 236, 21, 186, 55)),
    26: ("wheel_sha256", (2, 51, 125, 65, 54, 239, 8, 6, 76, 170, 142, 216, 250, 49, 164, 85, 105, 201, 56, 158)),
    56: ("git_source_manifest_sha256", (104, 157, 45, 51, 189, 135, 94, 135, 252, 228, 193, 151, 147, 63, 74, 82, 119, 159, 205, 112)),
}


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_secret_scan.py REPORT_JSON")
    report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise TypeError("invalid secret scan report")
    results = report.get("results")
    if not isinstance(results, dict):
        raise TypeError("secret scan report has no results map")

    evidence_lines = Path(EVIDENCE_PATH).read_text(encoding="utf-8").splitlines()
    allowed = 0
    findings: list[tuple[str, int, str]] = []
    for raw_path, items in results.items():
        if not isinstance(raw_path, str) or not isinstance(items, list):
            raise TypeError("invalid secret scan results")
        path = raw_path.replace("\\", "/")
        for item in items:
            if not isinstance(item, dict):
                raise TypeError("invalid secret scan finding")
            line = item.get("line_number")
            kind = item.get("type")
            fingerprint = item.get("hashed_secret")
            fingerprint_bytes: tuple[int, ...] = ()
            if isinstance(fingerprint, str):
                try:
                    fingerprint_bytes = tuple(bytes.fromhex(fingerprint))
                except ValueError:
                    pass
            known = (
                KNOWN_DIGESTS.get(line)
                if path == EVIDENCE_PATH and type(line) is int
                else None
            )
            key = None
            if known is not None and isinstance(line, int) and 1 <= line <= len(evidence_lines):
                match = re.match(r'\s*"([^"]+)"\s*:', evidence_lines[line - 1])
                key = match.group(1) if match else None
            if (
                known is not None
                and key == known[0]
                and kind == "Hex High Entropy String"
                and fingerprint_bytes == known[1]
            ):
                allowed += 1
            else:
                findings.append((path, line if isinstance(line, int) else -1, str(kind)))
    print(f"Known evidence digests: {allowed}; unrecognized findings: {len(findings)}")
    for path, line, kind in findings:
        print(f"{path}:{line}: {kind}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
