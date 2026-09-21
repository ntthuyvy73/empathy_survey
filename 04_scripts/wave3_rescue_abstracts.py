# -*- coding: utf-8 -*-
"""P1 WAVE 3 — CUU 505 bai CHUA-CHAC-CHAN: keo abstract con thieu tu Crossref/OpenAlex.

Doc wave3_ai_final.csv, loc final_trang_thai == CHUA-CHAC-CHAN. Chia 2 nhom:
  (a) THIEU abstract (<60 ky tu) — nguyen nhan chinh: WoS chi tra tieu de.
      -> tra cuu: DOI (tu doi_url) qua Crossref API roi OpenAlex API; neu khong co DOI
         -> Crossref query.bibliographic theo tieu de+nam, CHI nhan khi tieu de khop
         manh (similarity >= 0.95 tren khoa chuan hoa) de khong lay nham bai.
  (b) CO abstract nhung van chua chac (mơ ho that su) — KHONG xu ly lai (Opus da doc,
      thong tin khong doi thi phan quyet khong doi); de Vy quyet.
Bai cuu duoc abstract -> chia lo JSONL cho agent Opus duyet bo sung (cung rubric).
Xuat: <scratch>/rescue/rescue_batch_XX.jsonl + rescue_recovered.csv + rescue_log.txt
Chay: python wave3_rescue_abstracts.py <scratch_dir>"""
import csv
import difflib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NOTES = os.path.dirname(os.path.abspath(__file__))
EXPORTS = os.path.join(os.path.dirname(NOTES), "bai_bao", "search_exports")
SRC = os.path.join(EXPORTS, "wave3_ai_final.csv")
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(NOTES, "_ai_screen")
RESCUE = os.path.join(SCRATCH, "rescue")
os.makedirs(RESCUE, exist_ok=True)
MAILTO = "ntthuyvy73@gmail.com"
BATCH = 120


def skey(t):
    s = (t or "").replace("{", "").replace("}", "")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"P1-rescue/1.0 (mailto:{MAILTO})"})
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception:  # noqa: BLE001
            time.sleep(1.5)
    return None


def strip_jats(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return re.sub(r"\s+", " ", s).strip()


def reconstruct(inv):
    if not inv:
        return ""
    pos = [(i, w) for w, idxs in inv.items() for i in idxs]
    pos.sort()
    return " ".join(w for _, w in pos)


def doi_of(row):
    m = re.search(r"10\.\d{4,9}/[^\s\"'<>]+", row.get("doi_url", "") or "")
    return m.group(0).rstrip(".,;)") if m else ""


def fetch_by_doi(doi):
    d = get_json("https://api.crossref.org/works/" + urllib.parse.quote(doi)
                 + f"?mailto={MAILTO}")
    if d and d.get("message", {}).get("abstract"):
        ab = strip_jats(d["message"]["abstract"])
        if len(ab) >= 80:
            return ab, "crossref-doi"
    d = get_json("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi)
                 + f"?mailto={MAILTO}")
    if d and d.get("abstract_inverted_index"):
        ab = reconstruct(d["abstract_inverted_index"])
        if len(ab) >= 80:
            return ab, "openalex-doi"
    return "", ""


def fetch_by_title(title, year):
    q = urllib.parse.quote(title[:200])
    d = get_json(f"https://api.crossref.org/works?query.bibliographic={q}&rows=3&mailto={MAILTO}")
    items = (d or {}).get("message", {}).get("items", [])
    for it in items:
        t2 = (it.get("title") or [""])[0]
        if difflib.SequenceMatcher(None, skey(title), skey(t2)).ratio() >= 0.95:
            if it.get("abstract"):
                ab = strip_jats(it["abstract"])
                if len(ab) >= 80:
                    return ab, "crossref-title"
            # thu OpenAlex bang DOI cua ban ghi khop
            if it.get("DOI"):
                ab, src = fetch_by_doi(it["DOI"])
                if ab:
                    return ab, src + "-via-title"
    # OpenAlex title search
    d = get_json("https://api.openalex.org/works?filter=title.search:"
                 + urllib.parse.quote(title[:150].replace(",", " ")) + f"&per-page=3&mailto={MAILTO}")
    for it in (d or {}).get("results", []):
        if difflib.SequenceMatcher(None, skey(title), skey(it.get("title") or "")).ratio() >= 0.95:
            ab = reconstruct(it.get("abstract_inverted_index"))
            if len(ab) >= 80:
                return ab, "openalex-title"
    return "", ""


def main():
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    chua = [r for r in rows if r["final_trang_thai"] == "CHUA-CHAC-CHAN"]
    thieu = [r for r in chua if len((r.get("abstract") or "").strip()) < 60]
    co_ab = len(chua) - len(thieu)
    co_doi = sum(1 for r in thieu if doi_of(r))
    print(f"CHUA-CHAC-CHAN: {len(chua)} | thieu abstract: {len(thieu)} "
          f"(co DOI: {co_doi}) | co abstract nhung mo ho: {co_ab} (de Vy quyet)")

    recovered, fails = [], []
    for i, r in enumerate(thieu, 1):
        doi = doi_of(r)
        ab, src = ("", "")
        if doi:
            ab, src = fetch_by_doi(doi)
        if not ab and (r.get("title") or "").strip():
            ab, src = fetch_by_title(r["title"], r.get("year", ""))
        if ab:
            recovered.append(dict(rec_id=r["rec_id"], title=r["title"], year=r.get("year", ""),
                                  doi=doi, abstract_bosung=ab[:2200], nguon=src))
        else:
            fails.append(r["rec_id"])
        if i % 25 == 0:
            print(f"  {i}/{len(thieu)} tra cuu... cuu duoc {len(recovered)}")
        time.sleep(0.12)

    out_csv = os.path.join(RESCUE, "rescue_recovered.csv")
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["rec_id", "title", "year", "doi",
                                          "nguon", "abstract_bosung"])
        w.writeheader()
        w.writerows(recovered)

    # chia lo cho agent duyet (kem phan quyet tang truoc de doi chieu)
    by_id = {r["rec_id"]: r for r in rows}
    for old in [f for f in os.listdir(RESCUE) if f.startswith("rescue_batch_")]:
        os.remove(os.path.join(RESCUE, old))
    n_batch = 0
    for i in range(0, len(recovered), BATCH):
        n_batch += 1
        with open(os.path.join(RESCUE, f"rescue_batch_{n_batch:02d}.jsonl"), "w",
                  encoding="utf-8") as f:
            for rec in recovered[i:i + BATCH]:
                r0 = by_id[rec["rec_id"]]
                f.write(json.dumps({
                    "rec_id": rec["rec_id"], "title": rec["title"], "year": rec["year"],
                    "venue": (r0.get("venue") or "")[:120],
                    "abstract": rec["abstract_bosung"][:1100],
                    "nguon_abstract": rec["nguon"],
                    "phan_quyet_truoc": r0.get("final_minh_chung", "")[:200],
                }, ensure_ascii=False) + "\n")

    with open(os.path.join(RESCUE, "rescue_log.txt"), "w", encoding="utf-8") as f:
        f.write(f"chua_chac={len(chua)}\nthieu_abstract={len(thieu)}\n"
                f"cuu_duoc={len(recovered)}\nkhong_tim_thay={len(fails)}\n"
                f"co_abstract_mo_ho_de_vy={co_ab}\nbatches={n_batch}\n"
                f"fails={','.join(fails)}\n")

    print(f"\n=== KET QUA TRA CUU ===")
    print(f"  Cuu duoc abstract: {len(recovered)}/{len(thieu)}")
    from collections import Counter
    print(f"  Theo nguon: {dict(Counter(r['nguon'] for r in recovered))}")
    print(f"  Khong tim thay: {len(fails)}")
    print(f"  Lo agent: {n_batch} (thu muc {RESCUE})")


if __name__ == "__main__":
    main()
