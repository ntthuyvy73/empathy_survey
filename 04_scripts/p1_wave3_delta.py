# -*- coding: utf-8 -*-
"""P1 WAVE 3 — Tach ban ghi MOI cua wave 3 so voi toan bo pool da biet:
  pool = all_dedup.ris (wave 1) + *_w2.ris/.nbib (wave 2) + citation_expert.csv
         + included_resources.csv (123 bai da chot).
Khu trung NOI BO wave 3 (mot bai o nhieu CSDL) roi doi chieu pool theo doi -> an ->
tieu de chuan hoa (tai dung parse + norm cua dedup_ris.py). Kem ASSERT tu kiem:
tong doc vao = moi + trung noi bo + trung pool; khong ban ghi nao vuot nam cutoff.
SPOT-CHECK do phu: kiem tra cac bai kinh dien truoc-2021 co mat trong pool w3 khong
(Althoff 2016, EmpatheticDialogues 2019, EPITOME 2020, PsyQA 2021, SMILE 2023...).
Xuat: search_exports/wave3_new_for_screening.csv (GIU quyet dinh cu neu chay lai)
Chay: python p1_wave3_delta.py"""
import os
import re
import csv
import sys
import glob
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dedup_ris as D
from p1_query_terms import CUTOFF_DATE_W3

EXPORTS = D.EXPORTS
CUTOFF_YEAR = int(CUTOFF_DATE_W3[:4])

# cac bai kinh dien de spot-check do phu (tieu de chuan hoa mot phan, khop chua-day-du)
SPOTCHECK = {
    "althoff-2016": "large scale analysis of counseling conversations",
    "empatheticdialogues-2019": "towards empathetic open domain conversation",
    "epitome-2020": "computational approach to understanding empathy",
    "xiao-2015-rate-my-therapist": "rate my therapist",
    "psyqa-2021": "psyqa a chinese dataset",
    "smile-2023": "single turn to multi turn inclusive language expansion",
    "esconv-2021": "towards emotional support dialog systems",
    "annomi-2022": "anno mi",
}


def read_csv_rows(path):
    if not os.path.exists(path):
        return []
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    return []


def sync_from_wave3_folder():
    """NOI DUY NHAT Vy bo file wave 3 (ke ca xuat tay WoS/PubMed/Scopus):
    _analyst_v7/wave3_nlp_tham_van/02_ket_qua_tho/. Truoc khi chay, dong bo moi
    *_w3.ris/.nbib tu do sang search_exports (noi pool wave 1/2 nam) — copy khi
    file chua co hoac kich thuoc khac (lay ban o 02_ket_qua_tho lam chuan)."""
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "..", "..", ".."))
    drop = os.path.join(root, "wave3_nlp_tham_van", "02_ket_qua_tho")
    if not os.path.isdir(drop):
        return
    import shutil
    n_sync = 0
    for f in (glob.glob(os.path.join(drop, "*_w3.ris"))
              + glob.glob(os.path.join(drop, "*_w3.nbib"))):
        dst = os.path.join(EXPORTS, os.path.basename(f))
        if (not os.path.exists(dst)) or os.path.getsize(dst) != os.path.getsize(f):
            shutil.copy2(f, dst)
            n_sync += 1
    print(f"Dong bo tu 02_ket_qua_tho -> search_exports: {n_sync} file cap nhat")


def main():
    sync_from_wave3_folder()
    # ---------------- 1. POOL da biet ----------------
    pool = D.parse_file(os.path.join(EXPORTS, "all_dedup.ris"), "pool_w1")
    n_pool_w1 = len(pool)
    w2_files = sorted(glob.glob(os.path.join(EXPORTS, "*_w2.ris"))
                      + glob.glob(os.path.join(EXPORTS, "*_w2.nbib")))
    for f in w2_files:
        rs = D.parse_nbib(f, "pool_w2") if f.lower().endswith(".nbib") \
            else D.parse_file(f, "pool_w2")
        pool.extend(rs)
    seen_doi = {r["ndoi"] for r in pool if r["ndoi"]}
    seen_an = {r["an"] for r in pool if r["an"]}
    seen_title = {r["ntitle"] for r in pool if r["ntitle"]}
    # them nguon chuyen gia + danh sach da chot (chi co title/doi)
    for row in read_csv_rows(os.path.join(EXPORTS, "citation_expert.csv")):
        t = D.norm_title(row.get("title", ""))
        if t:
            seen_title.add(t)
        m = re.search(r"10\.\d{4,9}/\S+", row.get("doi_url", "") or "")
        if m:
            seen_doi.add(D.norm_doi(m.group(0)))
    for row in read_csv_rows(os.path.join(EXPORTS, "included_resources.csv")):
        t = D.norm_title(row.get("title", ""))
        if t:
            seen_title.add(t)
    print(f"Pool da biet: wave1={n_pool_w1} + wave2({len(w2_files)} file)={len(pool)-n_pool_w1} "
          f"+ expert/included -> {len(seen_title)} title / {len(seen_doi)} doi")

    # ---------------- 2. WAVE 3 ----------------
    w3_files = sorted(glob.glob(os.path.join(EXPORTS, "*_w3.ris"))
                      + glob.glob(os.path.join(EXPORTS, "*_w3.nbib")))
    if not w3_files:
        sys.exit("Chua thay *_w3.ris — chay harvest_wave3.py truoc.")
    w3, per_src = [], {}
    for f in w3_files:
        src = D.source_of(f)
        rs = D.parse_nbib(f, src) if f.lower().endswith(".nbib") else D.parse_file(f, src)
        per_src[os.path.basename(f)] = len(rs)
        w3.extend(rs)
    print(f"Wave 3 files: {per_src}")
    print(f"Tong ban ghi wave 3 (truoc khu trung): {len(w3)}\n")

    # co C3 cua ACL (acl_w3_flags.csv) de mang sang CSV
    c3flag = {}
    for row in read_csv_rows(os.path.join(EXPORTS, "acl_w3_flags.csv")):
        c3flag[D.norm_title(row.get("title", ""))] = row.get("c3_hit", "")

    new, dup_pool, dup_internal, beyond_cutoff = [], 0, 0, []
    w3_doi, w3_title = set(), set()
    for r in w3:
        if (r["ndoi"] and r["ndoi"] in w3_doi) or (r["ntitle"] and r["ntitle"] in w3_title):
            dup_internal += 1
            continue
        if r["ndoi"]:
            w3_doi.add(r["ndoi"])
        if r["ntitle"]:
            w3_title.add(r["ntitle"])
        if ((r["ndoi"] and r["ndoi"] in seen_doi) or (r["an"] and r["an"] in seen_an)
                or (r["ntitle"] and r["ntitle"] in seen_title)):
            dup_pool += 1
            continue
        # WoS xuat tay co the chua early-access de nam sau cutoff -> loai theo protocol
        if r["year"] and int(r["year"]) > CUTOFF_YEAR:
            beyond_cutoff.append(r)
            continue
        new.append(r)
    if beyond_cutoff:
        print(f"Loai {len(beyond_cutoff)} ban ghi de nam > {CUTOFF_YEAR} (early access "
              f"ngoai cua so, ghi ro theo protocol):")
        for r in beyond_cutoff:
            print(f"    [{r['source']}] {r['year']} {r['title'][:80]}")

    # ---------------- 3. ASSERT tu kiem ----------------
    assert len(new) + dup_internal + dup_pool + len(beyond_cutoff) == len(w3), \
        f"Lech so: {len(new)}+{dup_internal}+{dup_pool}+{len(beyond_cutoff)} != {len(w3)}"
    assert not [r for r in new if r["year"] and int(r["year"]) > CUTOFF_YEAR]
    print(f"ASSERT OK: {len(new)} moi + {dup_internal} trung noi bo + {dup_pool} trung pool "
          f"+ {len(beyond_cutoff)} ngoai cua so = {len(w3)}")

    # spot-check do phu tren TOAN BO w3 (ke ca trung pool — muc dich la do truy van)
    # bo ngoac nhon BibTeX ({P}sy{QA} -> PsyQA) truoc khi chuan hoa, tranh bao thieu nham
    all_titles = " | ".join(sorted(w3_title | {
        D.norm_title((r["title"] or "").replace("{", "").replace("}", "")) for r in w3}))
    print("\nSPOT-CHECK do phu truy van wave 3 (bai kinh dien co xuat hien?):")
    for k, frag in SPOTCHECK.items():
        print(f"  [{'CO ' if frag in all_titles else 'THIEU'}] {k}")

    # ---------------- 4. Xuat CSV (giu quyet dinh cu) ----------------
    path = os.path.join(EXPORTS, "wave3_new_for_screening.csv")
    cols = ["rec_id", "source", "year", "era", "venue", "title", "doi_url", "c3_hit_acl",
            "decision_ta", "decision_ft", "include_group", "notes", "abstract"]
    norm = lambda s: re.sub(r"\W+", "", (s or "").lower())[:90]
    old = {}
    if os.path.exists(path):
        for r0 in read_csv_rows(path):
            old[(r0.get("source", ""), norm(r0.get("title")))] = r0
    new.sort(key=lambda r: (r["year"] or "0000", r["ntitle"]))
    n_keepdec = 0
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for i, r in enumerate(new, 1):
            o = old.get((r["source"], norm(r["title"])), {})
            if (o.get("decision_ft") or o.get("decision_ta") or "").strip():
                n_keepdec += 1
            era = ""
            if r["year"]:
                era = "pre-2021" if int(r["year"]) < 2021 else "2021+"
            w.writerow([f"w3-{i:04d}", r["source"], r["year"], era, r["venue"], r["title"],
                        r["doi_url"], c3flag.get(r["ntitle"], ""),
                        o.get("decision_ta", ""), o.get("decision_ft", ""),
                        o.get("include_group", ""), o.get("notes", ""), r["abstract"]])
    print(f"\n  (giu lai quyet dinh cu cho {n_keepdec} dong)")

    # ---------------- 5. Bao cao nhanh ----------------
    print(f"\n=== KET QUA WAVE 3 DELTA ===")
    print(f"  Tong doc vao:       {len(w3)}")
    print(f"  Trung noi bo w3:    {dup_internal}")
    print(f"  Trung pool cu:      {dup_pool}")
    print(f"  MOI that su:        {len(new)}")
    cnt_src = Counter(r["source"] for r in new)
    print(f"  Moi theo nguon:     {dict(cnt_src)}")
    cnt_era = Counter(("pre-2021" if r["year"] and int(r["year"]) < 2021 else "2021+")
                      for r in new if r["year"])
    print(f"  Moi theo era:       {dict(cnt_era)}")
    yr = Counter(r["year"] for r in new if r["year"])
    print("  Phan bo nam (moi):  " + ", ".join(f"{y}:{c}" for y, c in sorted(yr.items())))
    print(f"\n  Da xuat: {path}")
    print("Tiep theo: python wave3_analysis.py")


if __name__ == "__main__":
    main()
