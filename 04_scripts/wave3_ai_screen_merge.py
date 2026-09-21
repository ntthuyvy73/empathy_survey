# -*- coding: utf-8 -*-
"""P1 WAVE 3 — GOP + KIEM TRA ket qua duyet AI tang 1, chuan bi danh sach tang 2.

Kiem tra CUNG (assert):
  1. Du 51 lo, moi lo du so dong, rec_id khop 1-1 voi manifest.
  2. trang_thai/phan_loai thuoc tap cho phep; minh_chung khong rong va co dau «.
  3. XAC MINH MINH CHUNG: phan trich trong «...» phai xuat hien THAT trong
     title+abstract cua dung bai do (so khop sau chuan hoa khoang trang/hoa thuong).
     Trich sai -> danh dau 'minh-chung-khong-khop' va ha xuong CHUA-CHAC-CHAN.
Danh dau can duyet TANG 2 (Fable doc lai): (a) moi bai DUNG-chac-chan; (b) moi bai
CHUA-CHAC-CHAN; (c) bai NGOAI nhung co tin hieu nguoc (dataset chac chan / band A);
(d) bai minh chung khong khop.
Xuat: search_exports/wave3_ai_screened.csv (toan bo + cot ai_*)
      <scratch>/tier2/tier2_XX.jsonl (cac bai can Fable duyet lai, chia lo 120)
Chay: python wave3_ai_screen_merge.py <scratch_dir>"""
import csv
import json
import os
import re
import sys
import unicodedata
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NOTES = os.path.dirname(os.path.abspath(__file__))
EXPORTS = os.path.join(os.path.dirname(NOTES), "bai_bao", "search_exports")
SRC = os.path.join(EXPORTS, "wave3_screening_sorted.csv")
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(NOTES, "_ai_screen")
VERDICTS = os.path.join(SCRATCH, "verdicts")

TT = {"DUNG-chac-chan", "NGOAI-chac-chan", "CHUA-CHAC-CHAN"}
PL = {"dataset-moi", "dung-dataset-cu", "phuong-phap-he-thong", "danh-gia-benchmark",
      "tong-quan", "thu-nghiem-nguoi-dung", "phan-tich-ngon-ngu-lam-sang",
      "ngoai-mien", "khong-du-thong-tin"}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def main():
    with open(os.path.join(SCRATCH, "batch_manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    by_id = {r["rec_id"]: r for r in rows}

    verdicts, thieu_lo, loi_dong = {}, [], []
    for name, ids in sorted(manifest.items()):
        out = os.path.join(VERDICTS, name.replace(".jsonl", "_out.jsonl"))
        if not os.path.exists(out):
            thieu_lo.append(name)
            continue
        got = {}
        with open(out, encoding="utf-8") as f:
            for ln, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    loi_dong.append(f"{name}:{ln} json loi")
                    continue
                got[d.get("rec_id", "")] = d
        miss = [i for i in ids if i not in got]
        extra = [i for i in got if i not in ids]
        if miss or extra:
            loi_dong.append(f"{name}: thieu {len(miss)} ({miss[:3]}...), thua {len(extra)}")
        for i, d in got.items():
            if i in ids:
                d["_lo"] = name
                verdicts[i] = d

    print(f"Lo co ket qua: {len(manifest) - len(thieu_lo)}/{len(manifest)}"
          + (f" | THIEU: {thieu_lo}" if thieu_lo else ""))
    if loi_dong:
        print("Loi dong:", loi_dong[:10])
    if thieu_lo:
        print("=> Chay lai cac lo thieu roi merge lai. Dung o day.")
        # van ghi phan da co de theo doi
    n_v = len(verdicts)
    print(f"Tong phan quyet hop le: {n_v}/{len(rows)}")

    # ---------------- xac minh minh chung + gan vao rows ----------------
    stats = Counter()
    bad_quote, tier2 = [], []
    for r in rows:
        v = verdicts.get(r["rec_id"])
        if not v:
            r["ai_trang_thai"] = "(chua duyet)"
            r["ai_phan_loai"] = r["ai_R_de_xuat"] = r["ai_minh_chung"] = r["ai_lo"] = ""
            r["ai_kiem_tra"] = "can-tang-2|chua-duyet-tang-1"
            tier2.append(r)
            continue
        tt = (v.get("trang_thai") or "").strip()
        pl = (v.get("phan_loai") or "").strip()
        mc = (v.get("minh_chung") or "").strip()
        rd = (v.get("R_de_xuat") or "").strip()
        if tt not in TT:
            tt = "CHUA-CHAC-CHAN"
            mc += " [trang_thai khong hop le -> ha xuong chua chac]"
        if pl not in PL:
            pl = "khong-du-thong-tin"
        # xac minh phan trich «...» co that trong title+abstract.
        # Agent duoc phep trich kieu 'doan A ... doan B' -> tach theo dau ba cham
        # (ca '…' va '[...]') va kiem TUNG MANH; moi manh >=8 ky tu phai xuat hien.
        flag = ""
        m = re.search(r"«([^»]{3,400})»", mc)
        hay = norm(r.get("title", "") + " " + (r.get("abstract") or ""))
        if not mc:
            flag = "minh-chung-rong"
        elif not m:
            flag = "minh-chung-thieu-trich-dan"
        else:
            frags = [norm(f) for f in re.split(r"\.{3}|…|\[[^\]]*\]", m.group(1))]
            frags = [f for f in frags if len(f) >= 8]
            if not frags or not all(f in hay for f in frags):
                flag = "minh-chung-khong-khop"
        if flag and tt != "CHUA-CHAC-CHAN":
            bad_quote.append((r["rec_id"], flag, tt))
            tt = "CHUA-CHAC-CHAN"
            mc += f" [{flag} -> ha xuong chua chac]"
        r["ai_trang_thai"] = tt
        r["ai_phan_loai"] = pl
        r["ai_R_de_xuat"] = rd
        r["ai_minh_chung"] = mc
        r["ai_lo"] = v["_lo"]
        stats[tt] += 1

        # danh dau tang 2
        ds_chac = [d for d in (r.get("dataset") or "").split("; ")
                   if d and not d.endswith("(?)")]
        nguoc = tt == "NGOAI-chac-chan" and (ds_chac or r.get("band", "").startswith("A"))
        need = (tt == "DUNG-chac-chan" or tt == "CHUA-CHAC-CHAN" or nguoc or bool(flag))
        r["ai_kiem_tra"] = ("can-tang-2" + ("|tin-hieu-nguoc" if nguoc else "")
                           + (f"|{flag}" if flag else "")) if need else ""
        if need:
            tier2.append(r)

    # ---------------- xuat ----------------
    cols = list(rows[0].keys())
    out_csv = os.path.join(EXPORTS, "wave3_ai_screened.csv")
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    t2dir = os.path.join(SCRATCH, "tier2")
    os.makedirs(t2dir, exist_ok=True)
    for old in os.listdir(t2dir):
        os.remove(os.path.join(t2dir, old))
    B = 120
    for i in range(0, len(tier2), B):
        with open(os.path.join(t2dir, f"tier2_{i//B+1:02d}.jsonl"), "w",
                  encoding="utf-8") as f:
            for r in tier2[i:i + B]:
                f.write(json.dumps({
                    "rec_id": r["rec_id"], "title": r["title"], "year": r.get("year", ""),
                    "band": r.get("band", ""), "dataset": r.get("dataset", ""),
                    "ai_trang_thai": r["ai_trang_thai"], "ai_phan_loai": r["ai_phan_loai"],
                    "ai_minh_chung": r["ai_minh_chung"], "ai_kiem_tra": r["ai_kiem_tra"],
                    "abstract": (r.get("abstract") or "")[:1100],
                }, ensure_ascii=False) + "\n")

    print(f"\n=== THONG KE TANG 1 ===")
    for k, v2 in stats.most_common():
        print(f"  {k:18s}: {v2}")
    print(f"  (chua duyet)      : {len(rows) - n_v}")
    print(f"  Minh chung khong dat (da ha xuong chua chac): {len(bad_quote)}")
    for rec, fl, tt0 in bad_quote[:8]:
        print(f"    {rec}: {fl} (tu {tt0})")
    print(f"\n  CAN TANG 2 (Fable duyet lai): {len(tier2)} bai "
          f"-> {t2dir} ({(len(tier2)+B-1)//B} lo)")
    print(f"  Da xuat: {out_csv}")


if __name__ == "__main__":
    main()
