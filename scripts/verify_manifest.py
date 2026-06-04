#!/usr/bin/env python3
from pathlib import Path
import csv, hashlib, sys
root = Path(__file__).resolve().parents[1]
manifest = root / 'FILE_MANIFEST.csv'
missing = []
mismatch = []
with manifest.open(newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        p = root / row['path']
        if not p.exists():
            missing.append(row['path'])
            continue
        data = p.read_bytes()
        h = hashlib.sha256(data).hexdigest()
        if h != row['sha256'] or str(len(data)) != str(row['size_bytes']):
            mismatch.append(row['path'])
if missing or mismatch:
    if missing:
        print('MISSING:')
        for x in missing: print('  '+x)
    if mismatch:
        print('MISMATCH:')
        for x in mismatch: print('  '+x)
    sys.exit(1)
print(f'PASS: manifest verified ({sum(1 for _ in csv.DictReader(manifest.open(newline="", encoding="utf-8")))} files)')
