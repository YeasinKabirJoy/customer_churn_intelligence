"""Validate the Phase 1 project foundation without calculating business findings."""

from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "Telco-Customer-Churn.csv"
EXPECTED_SHA256 = "88BE4B93FBE0CC83421AF1C503794C97C342ECA914C1576DB7C276E61D61358A"
REQUIRED_DIRECTORIES = (
    "data/raw",
    "data/processed",
    "notebooks",
    "src",
    "sql",
    "reports/powerbi",
    "reports/tableau",
    "docs",
    "tests",
)


def sha256(path: Path) -> str:
    """Return the uppercase SHA-256 digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> int:
    failures: list[str] = []

    for relative_path in REQUIRED_DIRECTORIES:
        if not (PROJECT_ROOT / relative_path).is_dir():
            failures.append(f"Missing directory: {relative_path}")

    if not RAW_FILE.is_file():
        failures.append(f"Missing canonical raw file: {RAW_FILE.relative_to(PROJECT_ROOT)}")
    elif sha256(RAW_FILE) != EXPECTED_SHA256:
        failures.append("Raw file hash differs from the recorded source hash")

    print(f"Python: {sys.version.split()[0]}")
    print(f"SQLite: {sqlite3.sqlite_version}")

    if failures:
        print("Phase 1 foundation check: FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Raw file integrity: PASS")
    print("Required project structure: PASS")
    print("Phase 1 foundation check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
