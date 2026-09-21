# Wave 3 — Truy vấn NLP × tham vấn/trị liệu tâm lý (KHÔNG giới hạn năm)

Ngày soạn: 2026-07-31 · Ngày chốt: 2026-07-31

## Thiết kế truy vấn (khác gì wave 1/2)

| | Wave 1 (08/07) | Wave 2 (09/07) | **Wave 3 (31/07)** |
|---|---|---|---|
| Khối miền | A (tổng quát SKTT) | A1 học thuyết + A2 thang đo | **A3: tham vấn–trị liệu (43 term)** |
| Khối hội thoại/dataset | B bắt buộc | B bắt buộc | **BỎ** (bắt cả bài NLP không phải dataset) |
| Khối NLP | C hẹp (NLP/LLM/LM/text generation) | C hẹp | **C3 mở rộng (39 term): + ChatGPT/GPT/BERT/chatbot/agent/dialogue system/computational linguistics/sentiment analysis/topic model/word embeddings/ASR/deep learning…** |
| Năm | 2021 → cutoff | 2021 → cutoff | **KHÔNG sàn năm** → 2026-07-31 |

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
