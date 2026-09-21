# -*- coding: utf-8 -*-
"""P1 WAVE 3 — GOP phan quyet dot CUU ABSTRACT vao wave3_ai_final.csv.

Doc <scratch>/rescue/rescue_batch_XX_verdict.jsonl + rescue_recovered.csv.
Voi bai duoc cuu va co phan quyet moi:
  - cap nhat final_trang_thai / final_phan_loai / final_R_de_xuat / final_minh_chung
  - tang_duyet = "2-cuu-abstract"; them cot abstract_bosung + nguon_abstract_bosung
  - XAC MINH minh chung: cau trich «...» phai co that trong title + abstract_bosung
    (cho phep 'doan A ... doan B'); sai -> giu CHUA-CHAC-CHAN.
Bai khong cuu duoc giu nguyen. ASSERT: tong 7578; khong mat quyet dinh cu nao khac.
Xuat de len wave3_ai_final.csv (backup ban cu thanh wave3_ai_final_truoc_cuu.csv).
Chay: python wave3_rescue_merge.py <scratch_dir>"""
import csv
import glob
import json
import os
import re
import shutil
import sys
import unicodedata
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NOTES = os.path.dirname(os.path.abspath(__file__))
EXPORTS = os.path.join(os.path.dirname(NOTES), "bai_bao", "search_exports")
SRC = os.path.join(EXPORTS, "wave3_ai_final.csv")
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(NOTES, "_ai_screen")
RESCUE = os.path.join(SCRATCH, "rescue")
TT = {"DUNG-chac-chan", "NGOAI-chac-chan", "CHUA-CHAC-CHAN"}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def quote_ok(mc, hay_text):
    m = re.search(r"«([^»]{3,400})»", mc or "")
    if not m:
        return False
    hay = norm(hay_text)
    frags = [norm(f) for f in re.split(r"\.{3}|…|\[[^\]]*\]", m.group(1))]
    frags = [f for f in frags if len(f) >= 8]
    return bool(frags) and all(f in hay for f in frags)


def main():
    with open(os.path.join(RESCUE, "rescue_recovered.csv"), encoding="utf-8-sig",
              newline="") as f:
        rec_ab = {r["rec_id"]: r for r in csv.DictReader(f)}
    verdicts = {}
    for fp in sorted(glob.glob(os.path.join(RESCUE, "rescue_batch_*_verdict.jsonl"))):
        with open(fp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                verdicts[d.get("rec_id", "")] = d
    print(f"Bai da cuu abstract: {len(rec_ab)} | phan quyet dot cuu: {len(verdicts)}")
    thieu = [i for i in rec_ab if i not in verdicts]
    if thieu:
        print(f"  !! {len(thieu)} bai cuu duoc nhung CHUA co phan quyet: {thieu[:8]}")
        print("  => chay not lo rescue con thieu roi chay lai. Dung.")
        return

    shutil.copy2(SRC, os.path.join(EXPORTS, "wave3_ai_final_truoc_cuu.csv"))
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 7578

    stats, n_demote, n_up = Counter(), 0, 0
    for r in rows:
        r.setdefault("abstract_bosung", "")
        r.setdefault("nguon_abstract_bosung", "")
        v = verdicts.get(r["rec_id"])
        if not v:
            continue
        assert r["final_trang_thai"] == "CHUA-CHAC-CHAN", \
            f"{r['rec_id']} khong phai CHUA-CHAC ma bi dot cuu dung den!"
        ab = rec_ab[r["rec_id"]]["abstract_bosung"]
        tt = (v.get("trang_thai") or "").strip()
        if tt not in TT:
            tt = "CHUA-CHAC-CHAN"
        mc = (v.get("minh_chung") or "").strip()
        if tt != "CHUA-CHAC-CHAN" and not quote_ok(mc, r.get("title", "") + " " + ab):
            n_demote += 1
            mc += " [minh chung dot cuu khong xac minh duoc -> giu chua chac]"
            tt = "CHUA-CHAC-CHAN"
        if tt != "CHUA-CHAC-CHAN":
            n_up += 1
        r["final_trang_thai"] = tt
        r["final_phan_loai"] = (v.get("phan_loai") or "").strip() or r["final_phan_loai"]
        r["final_R_de_xuat"] = (v.get("R_de_xuat") or "").strip()
        r["final_minh_chung"] = mc
        r["tang_duyet"] = "2-cuu-abstract"
        r["abstract_bosung"] = ab
        r["nguon_abstract_bosung"] = rec_ab[r["rec_id"]]["nguon"]

    for r in rows:
        stats[r["final_trang_thai"]] += 1
    assert sum(stats.values()) == 7578

    cols = list(rows[0].keys())
    with open(SRC, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"\n=== SAU DOT CUU ===")
    for k, v2 in stats.most_common():
        print(f"  {k:18s}: {v2}")
    print(f"  Chot duoc them: {n_up} bai | minh chung rot (giu chua chac): {n_demote}")
    print(f"  Backup ban truoc cuu: wave3_ai_final_truoc_cuu.csv")
    print(f"  Da cap nhat: {SRC}")


if __name__ == "__main__":
    main()
