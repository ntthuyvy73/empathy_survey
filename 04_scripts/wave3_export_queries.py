# -*- coding: utf-8 -*-
"""P1 WAVE 3 — Xuat CHUOI TRUY VAN cho tung CSDL vao folder rieng wave3_nlp_tham_van/
01_truy_van/. Sinh TU DONG tu p1_query_terms.py (nguon su that duy nhat) — khong chep
tay de tranh sai lech. Gom: chuoi WoS + Scopus (dan tay tren giao dien, KHONG gioi han
nam), term PubMed [tiab], query arXiv API, query OpenAlex, mo ta loc ACL offline.
Chay: python wave3_export_queries.py"""
import os
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from p1_query_terms import (BLOCK_A3_THERAPY, BLOCK_C3_NLP, ARXIV_CATS, CUTOFF_DATE_W3)
import harvest_arxiv as HA
import harvest_openalex as HO
import harvest_pubmed as HP

# folder dich: _analyst_v7/wave3_nlp_tham_van/01_truy_van
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", ".."))
DEST = os.path.join(ROOT, "wave3_nlp_tham_van", "01_truy_van")
os.makedirs(DEST, exist_ok=True)


def quoted_group(terms):
    return "(" + " OR ".join(f'"{t}"' for t in terms) + ")"


def write(name, text):
    p = os.path.join(DEST, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    print("  ->", p)


A3, C3 = quoted_group(BLOCK_A3_THERAPY), quoted_group(BLOCK_C3_NLP)

# ---------------- WoS (chay tay) ----------------
wos = f"""# Web of Science — Wave 3 (dan vao Advanced Search)
# Ngay soan: {date.today()} | Timespan: ALL YEARS (khong gioi han nam), den {CUTOFF_DATE_W3}
# Document types: Article + Proceedings Paper + Review (nhu wave 1)
# Sau khi chay: Export -> RIS (Full Record), toi da 1000 ban ghi/lan -> dat ten
# wos1_w3.ris, wos2_w3.ris... va bo vao wave3_nlp_tham_van/02_ket_qua_tho/
# (NOI DUY NHAT can bo file; p1_wave3_delta.py tu dong bo sang search_exports/)

TS={A3} AND TS={C3}
"""
write("wos_wave3_query.txt", wos)

# ---------------- Scopus (chay tay) ----------------
scopus = f"""# Scopus — Wave 3 (dan vao Advanced document search)
# Ngay soan: {date.today()} | KHONG gioi han nam | den {CUTOFF_DATE_W3}
# Luu y: TITLE-ABS-KEY tim ca keywords (rong hon [tiab] cua PubMed) — chap nhan de tang recall.
# Sau khi chay: Export RIS -> scopus_w3.ris -> bo vao wave3_nlp_tham_van/02_ket_qua_tho/
# (NOI DUY NHAT can bo file; script tu dong bo sang search_exports/)

TITLE-ABS-KEY{A3} AND TITLE-ABS-KEY{C3}
"""
write("scopus_wave3_query.txt", scopus)

# ---------------- PubMed (script da tu chay; kem term de kiem chung/chay tay) --------
term = " AND ".join([HP.pm_group(BLOCK_A3_THERAPY), HP.pm_group(BLOCK_C3_NLP)])
pubmed = f"""# PubMed — Wave 3: NCBI dang CHAN IP (giong wave 2) -> VY CHAY TAY tren web:
# 1. Dan term duoi day vao o tim kiem https://pubmed.ncbi.nlm.nih.gov/
# 2. KHONG dat gioi han nam (mac dinh la tat ca; cutoff {CUTOFF_DATE_W3})
# 3. Send to -> Citation manager -> All results -> tai ve .nbib
# 4. Dat ten pubmed_w3.nbib -> bo vao wave3_nlp_tham_van/02_ket_qua_tho/
#    (NOI DUY NHAT can bo file; script tu dong bo sang search_exports/)

{term}
"""
write("pubmed_wave3_term.txt", pubmed)

# ---------------- arXiv (script da tu chay) ----------------
cats = "(" + " OR ".join(f"cat:{c}" for c in ARXIV_CATS) + ")"
arxiv_q = " AND ".join([HA.group(BLOCK_A3_THERAPY), HA.group(BLOCK_C3_NLP), cats])
write("arxiv_wave3_query.txt",
      f"# arXiv API — Wave 3 (harvest_wave3.py DA TU CHAY; search_query nguyen van)\n"
      f"# Truong abs: (abstract), the loai {ARXIV_CATS}, khong san nam, sort submittedDate desc\n\n"
      f"{arxiv_q}\n")

# ---------------- OpenAlex (script da tu chay) ----------------
oa_q = " AND ".join([HO.oa_group(BLOCK_A3_THERAPY), HO.oa_group(BLOCK_C3_NLP)])
write("openalex_wave3_query.txt",
      f"# OpenAlex API — Wave 3 (harvest_wave3.py DA TU CHAY)\n"
      f"# filter=title_and_abstract.search:<q>,to_publication_date:{CUTOFF_DATE_W3},"
      f"type:{HO.TYPE_FILTER},language:{HO.LANG_FILTER}\n"
      f"# (khong co from_publication_date -> khong san nam); xac thuc lai client bang regex A3&C3\n\n"
      f"{oa_q}\n")

# ---------------- ACL (offline) ----------------
write("acl_wave3_ghichu.txt",
      "# ACL Anthology — Wave 3 (loc OFFLINE tren anthology+abstracts.bib.gz, DA CHAY)\n"
      "# Tieu chi: (title+abstract) khop >=1 term khoi A3; KHONG doi hoi C3 vi venue da la\n"
      "# NLP; co ghi co c3_hit tung entry (acl_w3_flags.csv) de doi chieu do nhay.\n"
      "# Khong gioi han nam (anthology co bai tu 1965).\n")

# ---------------- README tong ----------------
readme = f"""# Wave 3 — Truy vấn NLP × tham vấn/trị liệu tâm lý (KHÔNG giới hạn năm)

Ngày soạn: {date.today()} · Ngày chốt: {CUTOFF_DATE_W3}

## Thiết kế truy vấn (khác gì wave 1/2)

| | Wave 1 (08/07) | Wave 2 (09/07) | **Wave 3 (31/07)** |
|---|---|---|---|
| Khối miền | A (tổng quát SKTT) | A1 học thuyết + A2 thang đo | **A3: tham vấn–trị liệu ({len(BLOCK_A3_THERAPY)} term)** |
| Khối hội thoại/dataset | B bắt buộc | B bắt buộc | **BỎ** (bắt cả bài NLP không phải dataset) |
| Khối NLP | C hẹp (NLP/LLM/LM/text generation) | C hẹp | **C3 mở rộng ({len(BLOCK_C3_NLP)} term): + ChatGPT/GPT/BERT/chatbot/agent/dialogue system/computational linguistics/sentiment analysis/topic model/word embeddings/ASR/deep learning…** |
| Năm | 2021 → cutoff | 2021 → cutoff | **KHÔNG sàn năm** → {CUTOFF_DATE_W3} |

Lý do mở rộng C3: wave 1 từng bỏ sót SMILE (abstract chỉ nói "ChatGPT") và PsyQA
(bài 2021 trước kỷ nguyên LLM) — xem citation_expert.csv cột why_missed.

## Nguồn và cách chạy
- **Tự động (script `_notes/harvest_wave3.py`)**: arXiv, ACL Anthology (offline),
  OpenAlex → xuất `search_exports/*_w3.ris` + copy vào `02_ket_qua_tho/`.
- **Chạy tay (Vy)**: WoS (`wos_wave3_query.txt`), PubMed (`pubmed_wave3_term.txt`,
  vì NCBI chặn IP như wave 2), Scopus tùy chọn (`scopus_wave3_query.txt`).
  **QUY TẮC MỘT CỬA: mọi file chị xuất tay đều bỏ vào `02_ket_qua_tho/`** —
  `p1_wave3_delta.py` tự đồng bộ sang `search_exports/` trước khi khử trùng;
  sau đó chạy `python p1_wave3_delta.py` và `python wave3_analysis.py`.

## Chuỗi truy vấn từng CSDL (file trong folder này)
- `wos_wave3_query.txt` — dán vào WoS Advanced Search (TS=...)
- `scopus_wave3_query.txt` — dán vào Scopus (TITLE-ABS-KEY(...))
- `pubmed_wave3_term.txt` — term [tiab] đầy đủ (script đã tự chạy; để kiểm chứng)
- `arxiv_wave3_query.txt`, `openalex_wave3_query.txt` — query API nguyên văn (đã chạy)
- `acl_wave3_ghichu.txt` — mô tả lọc offline ACL

## Quy trình sau thu hoạch
1. `python p1_wave3_delta.py` — khử trùng nội bộ + so pool (wave1 all_dedup 4123 +
   wave2 + expert + 123 bài đã chốt) → `wave3_new_for_screening.csv` (chỉ bản ghi MỚI)
2. `python wave3_analysis.py` — phân tích abstract: tín hiệu dataset (known/candidate),
   mở/đóng (open/conditional/closed/unstated), học thuyết, era →
   `wave3_dataset_annotations.csv` + `wave3_report.md`
3. Bản sao toàn bộ kết quả nằm trong `02_ket_qua_tho/` và `03_phan_tich/` của folder này.
"""
write("README_wave3.md", readme)
print("\nXong — da xuat 7 file truy van vao", DEST)
