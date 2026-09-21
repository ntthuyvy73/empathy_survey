# -*- coding: utf-8 -*-
"""WAVE 3 vong DATASET — chuan bi lo cho agent trich xuat theo wave3_ds_rubric.md.

Dien phan tich:
  (a) final_trang_thai = DUNG-chac-chan  (2.031)
  (b) final_trang_thai = CHUA-CHAC-CHAN  (472)
  (c) 35 bai Vy lat nguoc: vy_xac_minh = DUNG-chac-chan trong nhom NGOAI
  (d) NGOAI-vot-lai: NGOAI (Vy da xac nhan) nhung co tin hieu dataset
      (bucket != no-data-signal HOAC dataset != '') — de agent phan xu lai theo mien
      MO RONG (chan doan/sang loc lam sang -> vao; MXH -> danh sach rieng)
Xuat: <scratch>/ds_extract/ds_batch_XX.jsonl (~80 bai/lo) + manifest.
Chay: python wave3_ds_prep.py <scratch_dir>"""
import csv
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NOTES = os.path.dirname(os.path.abspath(__file__))
EXPORTS = os.path.join(os.path.dirname(NOTES), "bai_bao", "search_exports")
SRC = os.path.join(EXPORTS, "wave3_ai_final.csv")
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(NOTES, "_ai_screen")
DS = os.path.join(SCRATCH, "ds_extract")
os.makedirs(DS, exist_ok=True)
BATCH = 80


def main():
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 7578

    target, nhom_dem = [], Counter()
    for r in rows:
        tt = r["final_trang_thai"]
        vy = (r.get("vy_xac_minh") or "").strip()
        if tt == "DUNG-chac-chan":
            nhom = "DUNG"
        elif tt == "CHUA-CHAC-CHAN":
            nhom = "CHUA_CHAC"
        elif tt == "NGOAI-chac-chan" and vy == "DUNG-chac-chan":
            nhom = "VY_LAT_NGUOC"
        elif tt == "NGOAI-chac-chan" and (
                (r.get("bucket") or "no-data-signal") != "no-data-signal"
                or (r.get("dataset") or "").strip()):
            nhom = "NGOAI_VOT_LAI"
        else:
            continue
        nhom_dem[nhom] += 1
        ab = (r.get("abstract") or "").strip() or (r.get("abstract_bosung") or "").strip()
        target.append(dict(
            rec_id=r["rec_id"], nhom_nguon=nhom, title=r["title"],
            year=r.get("year", ""), venue=(r.get("venue") or "")[:100],
            abstract=ab[:1400],
            therapy_cu=r.get("therapy", ""), dataset_cu=r.get("dataset", ""),
            phan_loai_cu=r.get("final_phan_loai", "")))

    print(f"Dien phan tich: {sum(nhom_dem.values())} bai | {dict(nhom_dem)}")
    # thu tu: VY_LAT_NGUOC + DUNG-tai-nguyen truoc, roi DUNG khac, CHUA_CHAC, NGOAI_VOT_LAI
    uu_tien = {"VY_LAT_NGUOC": 0, "DUNG": 1, "CHUA_CHAC": 2, "NGOAI_VOT_LAI": 3}
    target.sort(key=lambda t: (uu_tien[t["nhom_nguon"]],
                               0 if t["phan_loai_cu"] in ("dataset-moi", "danh-gia-benchmark",
                                                          "dung-dataset-cu") else 1))
    for old in [f for f in os.listdir(DS) if f.startswith("ds_batch_") and "_out" not in f]:
        os.remove(os.path.join(DS, old))
    manifest = {}
    n_b = 0
    for i in range(0, len(target), BATCH):
        n_b += 1
        name = f"ds_batch_{n_b:02d}.jsonl"
        with open(os.path.join(DS, name), "w", encoding="utf-8") as f:
            for t in target[i:i + BATCH]:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")
        manifest[name] = [t["rec_id"] for t in target[i:i + BATCH]]
    with open(os.path.join(DS, "ds_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False)
    print(f"Da chia {len(target)} bai -> {n_b} lo (~{BATCH}/lo) trong {DS}")


if __name__ == "__main__":
    main()
