# -*- coding: utf-8 -*-
"""P1 WAVE 3 (2026-07-31) — NLP x tham van/tri lieu tam ly, KHONG rang buoc nam.
Truy van = (BLOCK_A3_THERAPY) AND (BLOCK_C3_NLP); BO khoi B; BO san nam (tim tu dau
lich su den CUTOFF_DATE_W3). Rieng ACL Anthology: venue da la NLP nen chi can khop A3
(ghi kem co c3_hit de doi chieu do nhay). Tai dung ham thuan cua harvest_{arxiv,acl,
openalex,pubmed}.py nhu harvest_wave2.py da lam.
Xuat: search_exports/{arxiv,acl,openalex,pubmed}_w3.ris (KHONG dung ten wave 1/2)
      search_exports/acl_w3_flags.csv (co c3_hit tung entry ACL)
      search_exports/wave3_log.txt    (nhat ky so lieu tung nguon)
PubMed dung POST cho esearch (term dai); WoS/Scopus khong tu dong duoc -> in chuoi de
chay tay neu can. Moi CSDL trong try/except rieng. Chay: python harvest_wave3.py"""
import os
import re
import csv
import sys
import json
import time
import gzip
import urllib.parse
import urllib.request
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from p1_query_terms import (BLOCK_A3_THERAPY, BLOCK_C3_NLP, ARXIV_CATS,
                            YEAR_MIN_W3, CUTOFF_DATE_W3)
import harvest_arxiv as HA
import harvest_acl as HL
import harvest_openalex as HO
import harvest_pubmed as HP

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS = os.path.join(BASE, "bai_bao", "search_exports")
CUTOFF_YEAR = int(CUTOFF_DATE_W3[:4])
cutoff = date.fromisoformat(CUTOFF_DATE_W3)
YEAR_FLOOR = 0 if YEAR_MIN_W3 is None else YEAR_MIN_W3
results, logs = {}, []

MAX_PAGES_ARXIV = int(os.environ.get("P1_MAX_PAGES", "60"))     # 60*200 = 12000 tran
MAX_PAGES_OA = int(os.environ.get("P1_MAX_PAGES", "100"))       # 100*200 = 20000 tran


def block_regex(terms):
    alts = sorted((re.escape(t).replace(r"\ ", r"\s+") for t in terms), key=len, reverse=True)
    return re.compile(r"\b(?:" + "|".join(alts) + r")\b", re.IGNORECASE)


RE_A3, RE_C3 = block_regex(BLOCK_A3_THERAPY), block_regex(BLOCK_C3_NLP)


def write_ris(name, records, ris_fn):
    path = os.path.join(EXPORTS, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(ris_fn(r) for r in records))
    return path


def note(msg):
    print(msg)
    logs.append(msg)


# ------------------------------------------------------------------ arXiv
def run_arxiv():
    cats = "(" + " OR ".join(f"cat:{c}" for c in ARXIV_CATS) + ")"
    query = " AND ".join([HA.group(BLOCK_A3_THERAPY), HA.group(BLOCK_C3_NLP), cats])
    note(f"\n[arXiv] query len={len(query)} | khong san nam, den {CUTOFF_DATE_W3}")
    seen, kept, start, total = set(), [], 0, None
    for page in range(MAX_PAGES_ARXIV):
        raw = HA.fetch_page(query, start)
        total, entries = HA.parse_entries(raw)
        if not entries:
            break
        for r in entries:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            try:
                pd = date.fromisoformat(r["published"])
            except ValueError:
                continue
            if pd <= cutoff:                      # KHONG loc san nam
                kept.append(r)
        print(f"  trang {page+1}: +{len(entries)} (API total={total}); giu={len(kept)}")
        start += HA.PAGE_SIZE
        if total is not None and start >= total:
            break
        time.sleep(HA.DELAY)
    if total is not None and start < total:
        note(f"  !! CANH BAO: API total={total} > da duyet {start} (tran MAX_PAGES)")
    p = write_ris("arxiv_w3.ris", kept, HA.ris_record)
    results["arXiv"] = len(kept)
    note(f"  [arXiv] api_total={total} -> giu (den {CUTOFF_DATE_W3}, moi nam)={len(kept)} -> {p}")


# ------------------------------------------------------------------ ACL (offline)
def run_acl():
    HL.download_if_needed()
    kept, n, n_c3 = [], 0, 0
    with gzip.open(HL.GZ, "rt", encoding="utf-8", errors="replace") as f:
        for block in HL.iter_entries(f):
            n += 1
            title = HL.get_field(block, "title")
            ab = HL.get_field(block, "abstract")
            if not title:
                continue
            hay = title + "  " + ab
            if not RE_A3.search(hay):             # venue NLP -> chi can A3
                continue
            ym = re.search(r"(19|20)\d{2}", HL.get_field(block, "year"))
            if not ym or int(ym.group(0)) > CUTOFF_YEAR:
                continue                          # KHONG loc san nam
            key = re.search(r"^@\w+\s*\{\s*([^,]+),", block)
            au = [a.strip() for a in re.split(r"\s+and\s+", HL.get_field(block, "author")) if a.strip()]
            jn = HL.get_field(block, "journal")
            c3 = bool(RE_C3.search(hay))
            n_c3 += c3
            kept.append(dict(key=key.group(1).strip() if key else "", title=title, abstract=ab,
                             year=int(ym.group(0)), authors=au, journal=jn,
                             venue=jn or HL.get_field(block, "booktitle"),
                             url=HL.get_field(block, "url"), c3_hit=c3))
    kept.sort(key=lambda r: (r["year"], r["key"]), reverse=True)
    p = write_ris("acl_w3.ris", kept, HL.ris_record)
    with open(os.path.join(EXPORTS, "acl_w3_flags.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["acl_key", "year", "c3_hit", "title"])
        for r in kept:
            w.writerow([r["key"], r["year"], "yes" if r["c3_hit"] else "no", r["title"]])
    results["ACL"] = len(kept)
    note(f"\n[ACL] quet {n} entry -> khop A3 (moi nam)={len(kept)} "
         f"(trong do khop them C3={n_c3}) -> {p}")


# ------------------------------------------------------------------ OpenAlex
def oa_fetch_query(q_groups, tag):
    """Chay 1 truy van OpenAlex (khong san nam), tra ve dict oid->record."""
    q = " AND ".join(q_groups)
    got = {}
    cursor, pages, total = "*", 0, None
    while pages < MAX_PAGES_OA:
        filt = (f"title_and_abstract.search:{urllib.parse.quote(q)}"
                f",to_publication_date:{CUTOFF_DATE_W3}"
                f",type:{HO.TYPE_FILTER},language:{HO.LANG_FILTER}")
        url = (f"{HO.API}?filter={filt}&per-page={HO.PER_PAGE}"
               f"&cursor={urllib.parse.quote(cursor, safe='')}&mailto={HO.MAILTO}")
        req = urllib.request.Request(url, headers={"User-Agent": "P1-oa-w3/1.0"})
        for _ in range(4):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.load(r)
                break
            except Exception as e:  # noqa: BLE001
                print(f"    ! loi ({e}); thu lai sau 4s")
                time.sleep(4)
        else:
            raise RuntimeError(f"OpenAlex fail ({tag})")
        if total is None:
            total = data["meta"]["count"]
            note(f"  [OpenAlex/{tag}] server khop={total}")
        res = data.get("results") or []
        if not res:
            break
        for w in res:
            oid = (w.get("id") or "").rsplit("/", 1)[-1]
            if oid in got:
                continue
            title = w.get("title") or ""
            ab = HO.reconstruct(w.get("abstract_inverted_index"))
            yr = w.get("publication_year")
            if not (title and yr and yr <= CUTOFF_YEAR):
                continue
            hay = title + "  " + ab
            if not (RE_A3.search(hay) and RE_C3.search(hay)):   # xac thuc client A3&C3
                continue
            src = (w.get("primary_location") or {}).get("source") or {}
            got[oid] = dict(oa_id=oid, title=title, abstract=ab, year=yr,
                            type=w.get("type") or "",
                            authors=[a["author"]["display_name"] for a in (w.get("authorships") or [])
                                     if a.get("author")],
                            venue=src.get("display_name") or "",
                            doi=(w.get("doi") or "").replace("https://doi.org/", ""),
                            url=w.get("doi") or (w.get("id") or ""))
        pages += 1
        print(f"  trang {pages}: doc {len(res)}; giu client={len(got)}")
        cursor = data["meta"].get("next_cursor")
        if not cursor:
            break
        time.sleep(0.2)
    if total is not None and pages >= MAX_PAGES_OA:
        note(f"  !! CANH BAO OpenAlex/{tag}: co the tran MAX_PAGES ({MAX_PAGES_OA})")
    return got


def run_openalex():
    note(f"\n[OpenAlex] khong san nam, den {CUTOFF_DATE_W3} | type={HO.TYPE_FILTER}")
    try:
        got = oa_fetch_query([HO.oa_group(BLOCK_A3_THERAPY), HO.oa_group(BLOCK_C3_NLP)], "full")
        if not got:
            raise RuntimeError("0 ket qua — thu chia nho A3")
    except Exception as e:  # noqa: BLE001
        note(f"  ! truy van gop loi ({e}) -> chia A3 lam 2 nua, hop ket qua")
        half = (len(BLOCK_A3_THERAPY) + 1) // 2
        got = {}
        for i, chunk in enumerate([BLOCK_A3_THERAPY[:half], BLOCK_A3_THERAPY[half:]], 1):
            got.update(oa_fetch_query([HO.oa_group(chunk), HO.oa_group(BLOCK_C3_NLP)], f"nua{i}"))
    kept = sorted(got.values(), key=lambda r: (r["year"], r["title"]), reverse=True)
    p = write_ris("openalex_w3.ris", kept, HO.ris_record)
    results["OpenAlex"] = len(kept)
    note(f"  [OpenAlex] giu sau loc client A3&C3 (moi nam)={len(kept)} -> {p}")


# ------------------------------------------------------------------ PubMed
def pm_esearch_post(term):
    """esearch bang POST (term dai qua GET de bi 414/chan)."""
    body = urllib.parse.urlencode({
        "db": "pubmed", "term": term, "retmax": 0, "usehistory": "y",
        "datetype": "pdat", "mindate": "1800/01/01",
        "maxdate": CUTOFF_DATE_W3.replace("-", "/"),
        "retmode": "json", "tool": HP.TOOL, "email": HP.EMAIL}).encode()
    req = urllib.request.Request(f"{HP.EUTILS}/esearch.fcgi", data=body,
                                 headers={"User-Agent": "P1-pubmed-w3/1.0"})
    for _ in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.load(r)["esearchresult"]
            return int(d["count"]), d["webenv"], d["querykey"]
        except Exception as e:  # noqa: BLE001
            print(f"    ! loi ({e}); thu lai sau 4s")
            time.sleep(4)
    raise RuntimeError("esearch POST that bai")


def run_pubmed():
    term = " AND ".join([HP.pm_group(BLOCK_A3_THERAPY), HP.pm_group(BLOCK_C3_NLP)])
    note(f"\n[PubMed] term len={len(term)} | 1800..{CUTOFF_DATE_W3}")
    count, webenv, qkey = pm_esearch_post(term)
    note(f"  [PubMed] esearch count={count}")
    recs, start = [], 0
    target = min(count, HP.MAX_RECORDS)
    while start < target:
        batch = HP.efetch(webenv, qkey, start)
        if not batch:
            break
        recs.extend(batch)
        print(f"  efetch {start}-{start+len(batch)} ({len(recs)}/{target})")
        start += HP.BATCH
        time.sleep(0.34)
    recs.sort(key=lambda r: r["year"], reverse=True)
    p = write_ris("pubmed_w3.ris", recs, HP.ris_record)
    results["PubMed"] = len(recs)
    note(f"  [PubMed] tai ve={len(recs)} (esearch_count={count}) -> {p}")


if __name__ == "__main__":
    t0 = time.time()
    for name, fn in [("ACL", run_acl), ("OpenAlex", run_openalex),
                     ("PubMed", run_pubmed), ("arXiv", run_arxiv)]:
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            results[name] = f"FAIL: {type(e).__name__}: {e}"
            note(f"  !! {name} that bai: {e}")
    note("\n================= TONG WAVE 3 =================")
    note(f"  Cua so: KHONG san nam .. {CUTOFF_DATE_W3} | A3({len(BLOCK_A3_THERAPY)} term) "
         f"AND C3({len(BLOCK_C3_NLP)} term); ACL chi A3")
    for k in ("ACL", "OpenAlex", "PubMed", "arXiv"):
        note(f"  {k:9s}: {results.get(k)}")
    note(f"  (WoS/Scopus: khong tu dong duoc — neu can, chay tay chuoi A3 AND C3 tren giao dien)")
    note(f"  Thoi gian chay: {time.time()-t0:.0f}s")
    with open(os.path.join(EXPORTS, "wave3_log.txt"), "w", encoding="utf-8") as f:
        f.write(f"run_date={date.today()}\ncutoff={CUTOFF_DATE_W3}\nyear_floor=NONE\n"
                f"A3_terms={len(BLOCK_A3_THERAPY)}\nC3_terms={len(BLOCK_C3_NLP)}\n"
                + "\n".join(logs) + "\n")
    print("\nTiep theo: python p1_wave3_delta.py")
