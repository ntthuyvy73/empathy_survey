# -*- coding: utf-8 -*-
"""P1 WAVE 3 — CHUAN BI duyet AI tung bai (tang 1 cua quy trinh 2 tang).
Chia wave3_screening_sorted.csv (7578 bai) thanh cac lo JSONL ~150 bai de cac agent
doc-va-phan-xu tung bai theo rubric. Truong dua vao lo: rec_id, title, year, venue,
dataset, link_host, band, abstract (cat 1100 ky tu — du de phan xu muc TA).
Xuat: <scratch>/batches/batch_XX.jsonl + batch_manifest.json (de merge doi chieu du lo).
Chay: python wave3_ai_screen_prep.py <scratch_dir>"""
import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NOTES = os.path.dirname(os.path.abspath(__file__))
EXPORTS = os.path.join(os.path.dirname(NOTES), "bai_bao", "search_exports")
SRC = os.path.join(EXPORTS, "wave3_screening_sorted.csv")
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(NOTES, "_ai_screen")
BATCH_DIR = os.path.join(SCRATCH, "batches")
os.makedirs(BATCH_DIR, exist_ok=True)
BATCH_SIZE = 150

with open(SRC, encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))
assert rows, "File rong!"
ids = [r["rec_id"] for r in rows]
assert len(ids) == len(set(ids)), "rec_id trung!"

batches, manifest = [], {}
for i in range(0, len(rows), BATCH_SIZE):
    chunk = rows[i:i + BATCH_SIZE]
    name = f"batch_{i//BATCH_SIZE + 1:02d}.jsonl"
    path = os.path.join(BATCH_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        for r in chunk:
            f.write(json.dumps({
                "rec_id": r["rec_id"],
                "title": r["title"],
                "year": r.get("year", ""),
                "venue": (r.get("venue") or "")[:120],
                "dataset_goi_y": r.get("dataset", ""),
                "link_host": r.get("link_host", ""),
                "band": r.get("band", ""),
                "abstract": (r.get("abstract") or "")[:1100],
            }, ensure_ascii=False) + "\n")
    manifest[name] = [r["rec_id"] for r in chunk]
    batches.append((name, len(chunk)))

with open(os.path.join(SCRATCH, "batch_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False)
os.makedirs(os.path.join(SCRATCH, "verdicts"), exist_ok=True)

total = sum(n for _, n in batches)
assert total == len(rows), f"Lech: {total} != {len(rows)}"
print(f"Da chia {len(rows)} bai -> {len(batches)} lo trong {BATCH_DIR}")
print(f"Lo cuoi: {batches[-1]}")
