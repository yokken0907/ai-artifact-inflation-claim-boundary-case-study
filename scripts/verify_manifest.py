#!/usr/bin/env python3
"""Verify FILE_MANIFEST.csv against files in this package.

The manifest intentionally excludes FILE_MANIFEST.csv and FILE_MANIFEST.json.
"""
from __future__ import annotations
import csv
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "FILE_MANIFEST.csv"
EXCLUDED = {"FILE_MANIFEST.csv", "FILE_MANIFEST.json"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not MANIFEST.exists():
        print("FAIL: FILE_MANIFEST.csv not found")
        return 1
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    expected = {row["path"]: row for row in rows}
    actual_files = []
    for p in ROOT.rglob("*"):
        if p.is_file():
            rel = p.relative_to(ROOT).as_posix()
            if rel not in EXCLUDED:
                actual_files.append(rel)
    ok = True
    for rel in sorted(actual_files):
        p = ROOT / rel
        if rel not in expected:
            print(f"FAIL: missing from manifest: {rel}")
            ok = False
            continue
        row = expected[rel]
        size = p.stat().st_size
        digest = sha256(p)
        if int(row["size_bytes"]) != size:
            print(f"FAIL: size mismatch: {rel}")
            ok = False
        if row["sha256"] != digest:
            print(f"FAIL: sha256 mismatch: {rel}")
            ok = False
    for rel in sorted(expected):
        if rel not in actual_files:
            print(f"FAIL: manifest entry missing on disk: {rel}")
            ok = False
    if ok:
        print(f"PASS: manifest verified ({len(actual_files)} files)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
