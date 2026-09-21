# -*- coding: utf-8 -*-
"""P1 WAVE 3 — RA SOAT + BO SUNG COT cho wave3_ai_final.csv:
  1. `minhchung_therapy` — vi sao co nhan therapy: trich «ngu canh ~70 ky tu» quanh
     TU KHOA da khop (tai lap dung logic THERAPY cua extract_datasets.py). Xac dinh
     may moc 100%, khong dung AI.
  2. Ra soat `link_data`/`link_host` — quet lai link tren title + abstract +
     abstract_bosung (37 abstract cuu ve chua tung duoc quet); hop nhat voi link cu;
     availability dang 'unstated' ma nay co link kho du lieu -> nang thanh 'open'.
  3. Them cot `abstract_vi` (rong) + xuat lo dich cho nhom DUNG + CHUA-CHAC
     (uu tien: bai pham vi tai nguyen -> DUNG khac -> CHUA-CHAC; bo bai khong co
     abstract, danh dau '(khong co abstract)').
Backup truoc khi sua: wave3_ai_final_truoc_cot.csv.
Chay: python wave3_them_cot.py <scratch_dir>"""
import csv
import json
import os
import re
import shutil
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract_datasets as XD
import wave3_unique_enrich as UE

NOTES = os.path.dirname(os.path.abspath(__file__))
EXPORTS = os.path.join(os.path.dirname(NOTES), "bai_bao", "search_exports")
SRC = os.path.join(EXPORTS, "wave3_ai_final.csv")
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(NOTES, "_ai_screen")
VI_DIR = os.path.join(SCRATCH, "dich_vi")
os.makedirs(VI_DIR, exist_ok=True)
BATCH = 70
PL_TAINGUYEN = {"dataset-moi", "danh-gia-benchmark", "dung-dataset-cu"}


def therapy_evidence(blob):
    """Voi moi nhan therapy, trich ngu canh quanh TU KHOA khop dau tien."""
    low = blob.lower()
    by_tag = {}
    for k, tag in XD.THERAPY.items():
        i = low.find(k)
        if i < 0:
            continue
        a, b = max(0, i - 35), min(len(blob), i + len(k) + 35)
        ctx = re.sub(r"\s+", " ", blob[a:b]).strip()
        # giu ban khop som nhat trong van ban cho moi nhan
        if tag not in by_tag or i < by_tag[tag][0]:
            by_tag[tag] = (i, k, ctx)
    return " | ".join(f"{tag}: tu khoa '{k}' trong «…{ctx}…»"
                      for tag, (_, k, ctx) in sorted(by_tag.items()))


def main():
    shutil.copy2(SRC, os.path.join(EXPORTS, "wave3_ai_final_truoc_cot.csv"))
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 7578

    n_ther, n_link_moi, n_avail_up = 0, 0, 0
    for r in rows:
        blob = (r.get("title") or "") + "  " + (r.get("abstract") or "") \
               + "  " + (r.get("abstract_bosung") or "")
        # 1. minh chung therapy
        r["minhchung_therapy"] = therapy_evidence(blob) if (r.get("therapy") or "").strip() else ""
        if r["minhchung_therapy"]:
            n_ther += 1
        # 2. ra soat link (quet lai toan bo blob, hop nhat voi link cu)
        links_new, hosts_new, regs_new = UE.extract_links(blob)
        old_links = [u for u in (r.get("link_data") or "").split("; ") if u]
        merged = old_links + [u for u in links_new if u not in old_links]
        if len(merged) > len(old_links):
            n_link_moi += 1
        r["link_data"] = "; ".join(merged)
        hosts = []
        for u in merged:
            h = next((lab for frag, lab in UE.DATA_HOSTS if frag in u.lower()), "khac")
            if h not in hosts:
                hosts.append(h)
        r["link_host"] = "; ".join(hosts)
        old_regs = [u for u in (r.get("link_dang_ky") or "").split("; ") if u]
        r["link_dang_ky"] = "; ".join(old_regs + [u for u in regs_new if u not in old_regs])
        if r.get("availability") == "unstated" and any(h != "khac" for h in hosts):
            r["availability"] = "open"
            n_avail_up += 1
        # 3. cot dich
        r.setdefault("abstract_vi", "")

    # ---- xuat lo dich: DUNG + CHUA-CHAC, co abstract ----
    def muc_uu_tien(r):
        if r["final_trang_thai"] == "DUNG-chac-chan":
            return 0 if r["final_phan_loai"] in PL_TAINGUYEN else 1
        return 2

    target = [r for r in rows if r["final_trang_thai"] in
              ("DUNG-chac-chan", "CHUA-CHAC-CHAN") and not (r.get("abstract_vi") or "").strip()]
    co_ab, khong_ab = [], 0
    for r in target:
        ab = (r.get("abstract") or "").strip() or (r.get("abstract_bosung") or "").strip()
        if len(ab) >= 60:
            co_ab.append((muc_uu_tien(r), r["rec_id"], ab[:1600]))
        else:
            r["abstract_vi"] = "(khong co abstract)"
            khong_ab += 1
    co_ab.sort(key=lambda x: x[0])
    for old in [f for f in os.listdir(VI_DIR) if f.startswith("vi_batch_") and "_out" not in f]:
        os.remove(os.path.join(VI_DIR, old))
    n_batch = 0
    for i in range(0, len(co_ab), BATCH):
        n_batch += 1
        with open(os.path.join(VI_DIR, f"vi_batch_{n_batch:02d}.jsonl"), "w",
                  encoding="utf-8") as f:
            for _, rid, ab in co_ab[i:i + BATCH]:
                f.write(json.dumps({"rec_id": rid, "abstract": ab}, ensure_ascii=False) + "\n")

    cols = list(rows[0].keys())
    with open(SRC, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"Da them/ra soat cot. Backup: wave3_ai_final_truoc_cot.csv")
    print(f"  minhchung_therapy: {n_ther} dong co nhan therapy deu co minh chung")
    print(f"  link_data: {n_link_moi} dong co LINK MOI sau khi quet lai "
          f"(gom abstract_bosung); availability unstated->open: {n_avail_up}")
    print(f"  Dich tieng Viet: {len(co_ab)} abstract -> {n_batch} lo trong {VI_DIR}")
    print(f"  Khong co abstract (danh dau san): {khong_ab}")
    hostc = Counter(h for r in rows for h in (r.get('link_host') or '').split('; ')
                    if h and h != 'khac')
    print(f"  Link theo kho (toan file): {dict(hostc.most_common(10))}")


if __name__ == "__main__":
    main()
