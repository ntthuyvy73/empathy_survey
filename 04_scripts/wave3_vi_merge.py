# -*- coding: utf-8 -*-
"""P1 WAVE 3 — GOP ban dich tieng Viet (vi_batch_XX_out.jsonl) vao cot abstract_vi
cua wave3_ai_final.csv. Chay duoc NHIEU LAN (moi dot dich xong chay lai mot lan);
chi dien vao dong con trong, khong de len ban dich da co. Kiem tra: rec_id hop le,
ban dich khong rong va khong phai tieng Anh nguyen ban (heuristic: co ky tu co dau
tieng Viet hoac khac abstract goc).
Chay: python wave3_vi_merge.py <scratch_dir>"""
import csv
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NOTES = os.path.dirname(os.path.abspath(__file__))
EXPORTS = os.path.join(os.path.dirname(NOTES), "bai_bao", "search_exports")
SRC = os.path.join(EXPORTS, "wave3_ai_final.csv")
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(NOTES, "_ai_screen")
VI_DIR = os.path.join(SCRATCH, "dich_vi")


def co_dau_viet(s):
    return any(c in s for c in "ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ")


def main():
    vi = {}
    n_nghi_ngo = 0
    for fp in sorted(glob.glob(os.path.join(VI_DIR, "vi_batch_*_out.jsonl"))):
        with open(fp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                t = (d.get("abstract_vi") or "").strip()
                if d.get("rec_id") and len(t) >= 40:
                    if not co_dau_viet(t):
                        n_nghi_ngo += 1
                        t = "[NGHI NGO chua dich] " + t
                    vi[d["rec_id"]] = t
    print(f"Ban dich doc duoc: {len(vi)} (nghi ngo chua dich: {n_nghi_ngo})")

    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 7578
    n_fill, n_da_co = 0, 0
    for r in rows:
        r.setdefault("abstract_vi", "")
        if (r.get("abstract_vi") or "").strip():
            n_da_co += 1
            continue
        t = vi.get(r["rec_id"])
        if t:
            r["abstract_vi"] = t
            n_fill += 1
    with open(SRC, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    da = sum(1 for r in rows if (r.get("abstract_vi") or "").strip())
    can = sum(1 for r in rows if r["final_trang_thai"] in ("DUNG-chac-chan", "CHUA-CHAC-CHAN"))
    print(f"Dien moi: {n_fill} | da co tu truoc: {n_da_co}")
    print(f"Tien do abstract_vi: {da}/{can} dong thuoc dien DUNG+CHUA-CHAC")


if __name__ == "__main__":
    main()
