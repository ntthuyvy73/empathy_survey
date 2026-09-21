# -*- coding: utf-8 -*-
"""P1 WAVE 3 — Phan tich noi dung cac ban ghi MOI (wave3_new_for_screening.csv):
  1. Tin hieu DATASET: ten da biet (tai dung KNOWN cua extract_datasets.py), ung vien
     moi (CamelCase/acronym + cau 'we introduce/present...'), hay chi nhac chung.
  2. TINH MO/DONG (tu abstract): open (github/huggingface/publicly available/we release...),
     conditional (upon request/DUA), closed (not publicly available/privacy...), unstated.
     LUU Y: abstract thuong KHONG noi ro -> 'unstated' chiem da so; muon chac phai doc
     toan van. KHONG tu suy dien — chi gan nhan khi co cum tu tin hieu.
  3. Truc tri lieu (CBT/MI/...) tai dung THERAPY cua extract_datasets.py.
  4. Thong ke era / nam / nguon; bang tong hop.
Xuat: search_exports/wave3_dataset_annotations.csv + bao cao _notes/wave3_report.md
Chay: python wave3_analysis.py"""
import os
import re
import csv
import sys
from collections import Counter
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract_datasets as XD          # tai dung KNOWN/THERAPY/known_hits/distinctive/INTRO

NOTES = os.path.dirname(os.path.abspath(__file__))
EXPORTS = os.path.join(os.path.dirname(NOTES), "bai_bao", "search_exports")
SRC = os.path.join(EXPORTS, "wave3_new_for_screening.csv")

OPEN_PAT = re.compile(
    r"github\.com|huggingface|zenodo|osf\.io|gitlab\.com|"
    r"publicly (?:available|released|accessible)|open[- ]sourced?|freely available|"
    r"openly available|made (?:publicly )?available|"
    r"we (?:release|publish|open[- ]source)|will be (?:released|made (?:publicly )?available)|"
    r"code (?:and data )?(?:is|are|will be) available|data(?:set)? (?:is|are|will be) available|"
    r"available (?:at|on|via) (?:https?://|our)", re.I)
COND_PAT = re.compile(
    r"upon (?:reasonable )?request|on (?:reasonable )?request|by request|"
    r"data use agreement|available from the (?:corresponding )?author", re.I)
CLOSED_PAT = re.compile(
    r"not (?:be )?(?:publicly |openly )?(?:available|released|shared)|"
    r"cannot be (?:shared|released|made available)|proprietary|confidential|"
    r"privacy (?:concerns|restrictions|reasons)", re.I)
DATA_MENTION = re.compile(r"\b(dataset|datasets|corpus|corpora|benchmark|benchmarks)\b", re.I)


def availability(blob):
    o, c, cl = bool(OPEN_PAT.search(blob)), bool(COND_PAT.search(blob)), bool(CLOSED_PAT.search(blob))
    flags = "+".join([x for x, b in [("open", o), ("cond", c), ("closed", cl)] if b])
    if o and cl:
        return "mixed", flags
    if o:
        return "open", flags
    if c:
        return "conditional", flags
    if cl:
        return "closed", flags
    return "unstated", flags


def main():
    if not os.path.exists(SRC):
        sys.exit("Chua co wave3_new_for_screening.csv — chay p1_wave3_delta.py truoc.")
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    n = len(rows)
    ann = []
    known_counter, cand_counter, ther_counter = Counter(), Counter(), Counter()
    avail_counter, bucket_counter = Counter(), Counter()
    era_counter, yr_counter, src_counter = Counter(), Counter(), Counter()
    era_avail = Counter()

    for r in rows:
        title, ab = r.get("title", ""), r.get("abstract", "")
        blob = title + "  " + ab
        low = blob.lower()
        kn = XD.known_hits(blob)
        cands = []
        m = re.match(r"\s*([A-Za-z0-9][\w\- ]{1,30}?):", title)
        if m:
            cands += XD.distinctive(m.group(1))
        cands += re.findall(r"\(([A-Z][A-Za-z0-9\-]{2,})\)", blob)
        cands = sorted({c for c in cands if c.lower() not in XD.STOP and c.lower() not in
                        {k.replace(" ", "") for k in kn}})
        intro = bool(XD.INTRO.search(blob))
        ther = sorted({v for k, v in XD.THERAPY.items() if k in low})
        av, av_flags = availability(blob)
        has_data = bool(DATA_MENTION.search(blob))
        if kn:
            bucket = "known-dataset"
        elif intro and cands:
            bucket = "candidate-new"
        elif has_data:
            bucket = "mentions-data"
        else:
            bucket = "no-data-signal"
        for k in kn:
            known_counter[k] += 1
        if bucket == "candidate-new":
            for c in cands:
                cand_counter[c] += 1
        for t in ther:
            ther_counter[t] += 1
        avail_counter[av] += 1
        bucket_counter[bucket] += 1
        era = r.get("era", "")
        era_counter[era] += 1
        era_avail[(era, av)] += 1
        if r.get("year"):
            yr_counter[r["year"]] += 1
        src_counter[r.get("source", "")] += 1
        ann.append(dict(rec_id=r.get("rec_id", ""), bucket=bucket, availability=av,
                        avail_flags=av_flags, source=r.get("source", ""),
                        year=r.get("year", ""), era=era, known=";".join(kn),
                        candidates=";".join(cands), introducer=("yes" if intro else ""),
                        therapy=";".join(ther), venue=r.get("venue", ""),
                        title=title, doi_url=r.get("doi_url", "")))

    order = {"known-dataset": 0, "candidate-new": 1, "mentions-data": 2, "no-data-signal": 3}
    ann.sort(key=lambda a: (order[a["bucket"]], a["year"] or "0000"))
    out_csv = os.path.join(EXPORTS, "wave3_dataset_annotations.csv")
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["bucket", "availability", "avail_flags", "rec_id",
                                          "source", "year", "era", "known", "candidates",
                                          "introducer", "therapy", "venue", "title", "doi_url"])
        w.writeheader()
        w.writerows(ann)

    # ------------------------- bao cao markdown -------------------------
    L = []
    L.append(f"# Wave 3 — Phân tích {n} bản ghi MỚI (NLP × tham vấn–trị liệu, không giới hạn năm)")
    L.append(f"\n_Chạy: {date.today()} · Nguồn: `wave3_new_for_screening.csv` · "
             f"Chi tiết từng bài: `wave3_dataset_annotations.csv`_\n")
    L.append("## 1. Tổng quan")
    L.append(f"- Tổng bản ghi **mới** (chưa có trong pool wave 1/2/expert/123 bài đã chốt): **{n}**")
    L.append(f"- Theo nguồn: " + ", ".join(f"{k}: {v}" for k, v in src_counter.most_common()))
    L.append(f"- Theo thời kỳ: " + ", ".join(f"**{k}**: {v}" for k, v in sorted(era_counter.items())))
    L.append("\n### Phân bố theo năm (bản ghi mới)")
    L.append("| Năm | Số bài |")
    L.append("|---|---|")
    for y, c in sorted(yr_counter.items()):
        L.append(f"| {y} | {c} |")
    L.append("\n## 2. Tín hiệu dataset (từ tiêu đề + abstract)")
    L.append("| Rổ | Số bài | Giải thích |")
    L.append("|---|---|---|")
    expl = {"known-dataset": "nhắc tên dataset đã biết trong danh mục KNOWN",
            "candidate-new": "có câu 'we introduce/present…' + tên riêng lạ → khả năng bài giới thiệu bộ mới",
            "mentions-data": "có nói corpus/dataset/benchmark nhưng không rõ tên",
            "no-data-signal": "không thấy tín hiệu dataset trong abstract"}
    for b, c in sorted(bucket_counter.items(), key=lambda x: order[x[0]]):
        L.append(f"| {b} | {c} | {expl[b]} |")
    L.append(f"\n### Dataset đã biết được nhắc đến ({len(known_counter)} bộ)")
    L.append("| Dataset | Số bài mới nhắc |")
    L.append("|---|---|")
    for k, c in known_counter.most_common():
        L.append(f"| {k} | {c} |")
    L.append(f"\n### Ứng viên dataset MỚI (top 40 / {len(cand_counter)} tên)")
    L.append("| Tên ứng viên | Số bài |")
    L.append("|---|---|")
    for k, c in cand_counter.most_common(40):
        L.append(f"| {k} | {c} |")
    L.append("\n## 3. Tính mở/đóng của nguồn dữ liệu (suy từ abstract)")
    L.append("> Lưu ý: abstract thường không tuyên bố phát hành; nhãn `unstated` nghĩa là "
             "*abstract không nói*, không có nghĩa là đóng. Muốn kết luận cần đọc toàn văn.")
    L.append("\n| Nhãn | Số bài |")
    L.append("|---|---|")
    for k, c in avail_counter.most_common():
        L.append(f"| {k} | {c} |")
    L.append("\n| Thời kỳ | open | conditional | closed | mixed | unstated |")
    L.append("|---|---|---|---|---|---|")
    for era in sorted(era_counter):
        L.append(f"| {era} | " + " | ".join(str(era_avail.get((era, a), 0))
                 for a in ["open", "conditional", "closed", "mixed", "unstated"]) + " |")
    L.append("\n## 4. Trục học thuyết trị liệu được nhắc")
    L.append("| Học thuyết | Số bài |")
    L.append("|---|---|")
    for k, c in ther_counter.most_common():
        L.append(f"| {k} | {c} |")
    pre = [a for a in ann if a["era"] == "pre-2021" and a["bucket"] in
           ("known-dataset", "candidate-new")]
    L.append(f"\n## 5. Bài TRƯỚC 2021 có tín hiệu dataset ({len(pre)} bài) — giá trị chính "
             "của việc bỏ giới hạn năm")
    L.append("| Năm | Nguồn | Rổ | Tên | Tiêu đề |")
    L.append("|---|---|---|---|---|")
    for a in sorted(pre, key=lambda x: x["year"]):
        name = a["known"] or a["candidates"]
        L.append(f"| {a['year']} | {a['source']} | {a['bucket']} | {name[:40]} | "
                 f"{a['title'][:100]} |")
    opens = [a for a in ann if a["availability"] in ("open", "mixed")
             and a["bucket"] in ("known-dataset", "candidate-new")]
    L.append(f"\n## 6. Bài có tín hiệu dataset VÀ tín hiệu mở ({len(opens)} bài — ưu tiên đọc)")
    L.append("| Năm | Rổ | availability | Tên | Tiêu đề |")
    L.append("|---|---|---|---|---|")
    for a in sorted(opens, key=lambda x: (x["year"], x["title"])):
        name = a["known"] or a["candidates"]
        L.append(f"| {a['year']} | {a['bucket']} | {a['availability']} | {name[:36]} | "
                 f"{a['title'][:95]} |")
    from p1_query_terms import BLOCK_A3_THERAPY, BLOCK_C3_NLP, CUTOFF_DATE_W3
    L.append("\n## 7. Phương pháp & giới hạn")
    L.append(f"- Truy vấn wave 3: `(A3 tham vấn–trị liệu, {len(BLOCK_A3_THERAPY)} term) "
             f"AND (C3 NLP mở rộng, {len(BLOCK_C3_NLP)} term)`, **bỏ khối B**, "
             f"**không sàn năm**, chốt {CUTOFF_DATE_W3}. ACL chỉ cần khớp A3 (venue đã là "
             "NLP), có cột `c3_hit_acl` để đối chiếu.")
    # trang thai tung CSDL: doc TU FILE THUC TE co trong search_exports (khong ghi tay)
    import glob
    have = {os.path.basename(p) for p in glob.glob(os.path.join(EXPORTS, "*_w3.*"))}
    def stt(pat, cach, neu_thieu="**CHƯA có dữ liệu**"):
        hit = sorted(f for f in have if f.startswith(pat) and not f.endswith("_flags.csv"))
        return (f"đã chạy ({cach}) — {', '.join(hit)}" if hit else f"{neu_thieu} ({cach})")
    L.append("- Trạng thái từng CSDL (đọc từ file thực tế trong `search_exports/`):")
    for ten, pat, cach, thieu in [
            ("ACL Anthology", "acl_w3", "script, lọc offline bib.gz", "**CHƯA có dữ liệu**"),
            ("OpenAlex", "openalex_w3", "script, API", "**CHƯA có dữ liệu**"),
            ("arXiv", "arxiv_w3", "script, API", "**CHƯA có dữ liệu**"),
            ("Web of Science", "wos", "Vy xuất tay từ giao diện", "**CHƯA có dữ liệu**"),
            ("PubMed", "pubmed_w3", "Vy xuất tay — NCBI chặn IP nên script không gọi được",
             "**CHƯA có dữ liệu**"),
            ("Scopus", "scopus_w3", "không có tài khoản truy cập → **không chạy được**; "
             "OpenAlex đóng vai trò thay thế, giống wave 1 và wave 2", "KHÔNG áp dụng")]:
        L.append(f"  - {ten}: {stt(pat, cach, thieu)}")
    L.append("- Cột “mới theo nguồn” là **quy nguồn theo file gặp trước** (thứ tự chữ cái: "
             "acl → arxiv → openalex → pubmed → wos), không phải phần đóng góp độc quyền: "
             "một bài có mặt ở cả PubMed lẫn WoS được tính cho PubMed. Tổng số bài mới "
             "không đổi vì điều này.")
    L.append("- C3 đã thêm ChatGPT/GPT/BERT/chatbot/dialogue system/computational "
             "linguistics/sentiment analysis/topic model/word embeddings/deep learning… — "
             "khắc phục lỗi wave 1 bỏ sót SMILE/PsyQA (abstract không chứa cụm C hẹp).")
    L.append("- Nhãn open/closed chỉ dựa abstract (mức tín hiệu), chưa phải kết luận cấp "
             "toàn văn; `unstated` = abstract không nói.")
    L.append("- Danh mục KNOWN/THERAPY/STOP tái dùng nguyên trạng từ `extract_datasets.py` "
             "để nhất quán với vòng sàng lọc trước.")
    md = "\n".join(L) + "\n"
    out_md = os.path.join(NOTES, "wave3_report.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Phan tich {n} ban ghi moi:")
    print(f"  Ro dataset:   {dict(bucket_counter)}")
    print(f"  Mo/dong:      {dict(avail_counter)}")
    print(f"  Era:          {dict(era_counter)}")
    print(f"  Known top:    {known_counter.most_common(10)}")
    print(f"  Candidate top:{cand_counter.most_common(10)}")
    print(f"\nDa xuat: {out_csv}")
    print(f"Bao cao:  {out_md}")


if __name__ == "__main__":
    main()
