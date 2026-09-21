# TỪ ĐIỂN 47 CỘT — `wave3_ai_final.csv`

_Cập nhật 04/08/2026 · 7.578 dòng, mỗi dòng = 1 bài báo duy nhất sau khử trùng._
_Nhóm 🔴 và ✍️ là hai nhóm chị làm việc chính; các nhóm khác phục vụ tra cứu/kiểm toán._

---

## 🔴 NHÓM KẾT QUẢ SÀNG LỌC CUỐI (cột 38–43) — căn cứ chính để dùng

| # | Cột | Ý nghĩa | Giá trị |
|---|---|---|---|
| 38 | `final_trang_thai` | **Phán quyết cuối** của quy trình duyệt AI 2 tầng: bài có đúng mục tiêu khảo sát (NLP × tham vấn–trị liệu) không | `DUNG-chac-chan` (2.031) · `NGOAI-chac-chan` (5.075) · `CHUA-CHAC-CHAN` (472) |
| 39 | `final_phan_loai` | **Loại bài theo đóng góp nghiên cứu** | `dataset-moi` (giới thiệu bộ dữ liệu mới) · `danh-gia-benchmark` · `dung-dataset-cu` · `phan-tich-ngon-ngu-lam-sang` (phân tích phiên trị liệu thật) · `phuong-phap-he-thong` · `thu-nghiem-nguoi-dung` (RCT/pilot) · `tong-quan` · `ngoai-mien` · `khong-du-thong-tin` |
| 40 | `final_R_de_xuat` | **Gợi ý mã loại** theo bảng R1–R9 của giao thức (luôn kèm dấu `?` — chỉ là gợi ý, không phải quyết định) | `R2?` ngoài miền (EC2) · `R4?` chẩn đoán/y khoa thể chất (EC7) · `R8?` không phải tài nguyên: tổng quan/hệ thống/thử nghiệm (EC5) · trống = bài ĐÚNG dạng tài nguyên |
| 41 | `final_minh_chung` | **Vì sao phán quyết như vậy**: câu trích NGUYÊN VĂN từ abstract trong «…» + 1 câu lý do. Mọi câu trích đã được script đối chiếu tự động với abstract gốc — trích sai là bị hạ xuống "chưa chắc" | văn bản |
| 42 | `tang_duyet` | Bài đi qua tầng duyệt nào | `1` = chỉ tầng 1 (NGOÀI rõ ràng, không tranh chấp) · `2` = tầng 2 phán quyết lại · `2-cuu-abstract` = duyệt lại sau khi kéo được abstract từ Crossref/OpenAlex |
| 43 | `tang2_thay_doi` | Tầng 2 so với tầng 1 | `giu` (đồng ý) · `nang-cap` (chốt dứt ca "chưa chắc") · `lat-nguoc` (đảo ĐÚNG↔NGOÀI — 37 ca, **cần chị soi**) · trống = chỉ qua tầng 1 |

## 📄 NHÓM THÔNG TIN BÀI BÁO (5, 15–20, 31, 44–45, 47)

| # | Cột | Ý nghĩa |
|---|---|---|
| 5 | `rec_id` | Mã định danh duy nhất của bài trong wave 3 (dạng `u3-XXXX`) — dùng để tra cứu chéo mọi file |
| 15 | `year` | Năm xuất bản (của bản ghi đại diện) |
| 16 | `nam_khac` | Nếu nhóm gộp có nhiều năm khác nhau (preprint ↔ bản xuất bản) thì liệt kê tại đây |
| 17 | `era` | `pre-2021` / `2021+` — phân kỳ trước/sau mốc wave 1 |
| 18 | `venue` | Tạp chí / hội nghị |
| 19 | `title` | Tiêu đề (bản sạch nhất trong nhóm gộp, đã bỏ ngoặc BibTeX/LaTeX) |
| 20 | `doi_url` | Link DOI (hoặc link nguồn nếu không có DOI) |
| 31 | `abstract` | Abstract gốc tiếng Anh (bản dài nhất trong nhóm gộp; có thể bị nguồn cắt cụt) |
| 44 | `abstract_bosung` | Abstract kéo thêm từ Crossref/OpenAlex cho bài vốn thiếu (37 bài) |
| 45 | `nguon_abstract_bosung` | Nguồn của abstract bổ sung: `crossref-doi` / `openalex-doi` / `crossref-title` / `openalex-title`… |
| 47 | `abstract_vi` | **Bản dịch tiếng Việt học thuật** của abstract — đã dịch đủ 2.503 bài nhóm ĐÚNG + CHƯA CHẮC; nhóm NGOÀI để trống (không dịch); `(khong co abstract)` = bài không có abstract; hậu tố `[Abstract gốc bị cắt]` = nguồn cắt cụt, chỉ dịch phần có thật |

## 📊 NHÓM DATASET & LINK DỮ LIỆU (6–10, 21–24, 46)

| # | Cột | Ý nghĩa |
|---|---|---|
| 6 | `bucket` | Rổ tín hiệu dataset theo heuristic vòng đầu: `known-dataset` / `candidate-new` / `mentions-data` / `no-data-signal` (đã bị `final_phan_loai` thay thế phần lớn, giữ để đối chiếu) |
| 7 | `dataset` | Tên bộ dữ liệu nhắc trong bài (đã biết + ứng viên). Hậu tố **`(?)`** = tên trùng từ tiếng Anh thường (CARE, PEER, SPLIT…) — **phải kiểm tay**, có thể là thang đo/tên thử nghiệm |
| 8 | `link_data` | **Link dữ liệu/mã nguồn** nêu trong abstract (GitHub, Hugging Face, Zenodo, OSF…). Đã loại link giấy phép, nhà xuất bản, DOI/arXiv/ACL (trích dẫn), rác quảng cáo |
| 9 | `link_host` | Nơi lưu tương ứng: `github` / `huggingface` / `zenodo` / `osf` / … / `khac` (tên miền lạ — có thể là trang dự án riêng, vẫn giữ để xem) |
| 10 | `availability` | **Tính mở/đóng của DỮ LIỆU/TÀI NGUYÊN bài công bố** (KHÔNG phải open-access của bài báo): `open` (có link kho hoặc tuyên bố phát hành) · `conditional` (upon request/DUA) · `closed` (tuyên bố không chia sẻ) · `mixed` (vừa mở vừa đóng, vd mã mở dữ liệu đóng) · `unstated` (abstract không nói — KHÔNG có nghĩa là đóng) |
| 21 | `dataset_da_biet` | Tách riêng: tên khớp danh mục đã biết (123 bài đã chốt + KNOWN) |
| 22 | `dataset_ung_vien` | Tách riêng: tên lạ nghi là bộ mới (heuristic, cần xác nhận) |
| 23 | `link_dang_ky` | Link đăng ký thử nghiệm/đề cương (ClinicalTrials, PROSPERO, ISRCTN…) — hữu ích nhưng KHÔNG phải link dữ liệu |
| 24 | `therapy` | Nhãn trường phái/học thuyết trị liệu nhắc trong bài: `CBT` / `MI` / `ESC` / `mindfulness` / `client-centered` / `psychodynamic` / `DBT` / `ACT` / `SFBT` / `REBT` / `Hill` (khớp từ khóa mức abstract — lọc thô rồi xác nhận, đừng đếm thẳng vào bảng số liệu) |
| 46 | `minhchung_therapy` | **Vì sao có nhãn therapy**: liệt kê từ khóa đã khớp + trích «ngữ cảnh ~70 ký tự» quanh nó, cho từng nhãn. Sinh bằng script thuần — chính xác tuyệt đối theo nghĩa "từ khóa này có thật ở chỗ này" |

## 🗃️ NHÓM DẤU VẾT KHỬ TRÙNG (11–14, 25–26)

| # | Cột | Ý nghĩa |
|---|---|---|
| 11 | `n_sources` | Bài xuất hiện ở bao nhiêu CSDL (1–4) — bài nhiều nguồn thường nổi bật hơn |
| 12 | `sources` | Danh sách CSDL tìm thấy bài (WoS; OpenAlex; PubMed; arXiv; ACL) |
| 13 | `n_ban_ghi` | Số bản ghi thô đã gộp thành dòng này (khử trùng bằng DOI + arXiv-id + tiêu đề chuẩn hóa mạnh) |
| 14 | `source_chinh` | Nguồn của bản ghi đại diện (bản có DOI + abstract dài nhất) |
| 25 | `gan_trung_voi` | Cảnh báo: có bài khác tiêu đề GẦN giống (lệch vài ký tự, similarity ≥0.93) — script KHÔNG tự gộp, chị tự quyết (26 cặp) |
| 26 | `canh_bao_sieu_du_lieu` | 15 dòng: CSDL nguồn gắn SAI tiêu đề vào DOI đúng (lỗi của OpenAlex). Cột này lưu tiêu đề rác đã bị loại; tiêu đề giữ lại chọn theo bỏ phiếu đa số |

## ✍️ NHÓM CHỜ CHỊ ĐIỀN (27–30) — quyết định cuối là của chị

| # | Cột | Ý nghĩa |
|---|---|---|
| 27 | `decision_ta` | Quyết định sàng lọc mức tiêu đề+abstract: `include` / `exclude` / `check-fulltext` |
| 28 | `decision_ft` | Quyết định sau khi đọc toàn văn: `include` / `exclude` |
| 29 | `include_group` | Nhóm nếu include: `main` / `adjacent` / `eval` (theo quy ước 3 nhóm của khảo sát) |
| 30 | `notes` | Ghi chú tự do (kèm mã R khi loại, để bước lập PRISMA đếm được) |

_Chạy lại bất kỳ script wave 3 nào cũng **giữ nguyên** 4 cột này._

## 🗄️ NHÓM LỊCH SỬ — có thể bỏ qua khi làm việc (1–4, 32–37)

| # | Cột | Ý nghĩa |
|---|---|---|
| 1 | `priority_score` | Điểm ưu tiên đọc của bước heuristic (trước khi có duyệt AI) — đã hết vai trò |
| 2 | `band` | Nhóm ưu tiên A/B/C/D theo điểm trên — đã hết vai trò |
| 3 | `R_goi_y` | Gợi ý mã loại của bước heuristic — đã bị `final_R_de_xuat` thay thế |
| 4 | `hint` | Giải thích điểm heuristic (từ khóa nào cộng/trừ điểm) |
| 32 | `ai_trang_thai` | Phán quyết **tầng 1** (giữ để kiểm toán — so với cột 38 xem tầng 2 sửa gì) |
| 33 | `ai_phan_loai` | Phân loại tầng 1 |
| 34 | `ai_R_de_xuat` | Mã loại gợi ý tầng 1 |
| 35 | `ai_minh_chung` | Minh chứng tầng 1 (câu trích «…» đã xác minh; ghi chú `[...-> ha xuong chua chac]` nếu trích không đạt) |
| 36 | `ai_lo` | Bài thuộc lô duyệt tầng 1 nào (batch_XX) — truy vết được file phán quyết gốc |
| 37 | `ai_kiem_tra` | Cờ đưa vào tầng 2: `can-tang-2` + lý do (`tin-hieu-nguoc`, `minh-chung-khong-khop`, `chua-duyet-tang-1`) |

---

## Cách dùng nhanh cho từng mục đích

| Muốn | Lọc/dùng cột |
|---|---|
| Bài nền cho survey | `final_trang_thai = DUNG-chac-chan` (2.031 bài) |
| Bảng dataset/benchmark | thêm `final_phan_loai ∈ {dataset-moi, danh-gia-benchmark, dung-dataset-cu}` — hoặc dùng thẳng file `wave3_tai_nguyen_moi.csv` đã đối chiếu |
| Phần lịch sử | thêm `era = pre-2021` (313 bài ĐÚNG) |
| Ma trận học thuyết × loại bài | `therapy` × `final_phan_loai` (kiểm `minhchung_therapy` trước khi đếm) |
| Nhóm cần chị tự quyết | `final_trang_thai = CHUA-CHAC-CHAN` (472) và `tang2_thay_doi = lat-nguoc` (37) |
| Đọc nhanh bằng tiếng Việt | `abstract_vi` (đủ cho toàn bộ nhóm ĐÚNG + CHƯA CHẮC) |
| Kiểm chứng một phán quyết | `final_minh_chung` → nghi ngờ thì mở `abstract`/`abstract_vi` đối chiếu |
