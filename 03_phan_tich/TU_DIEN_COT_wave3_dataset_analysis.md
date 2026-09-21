# TỪ ĐIỂN CỘT — wave3_ai_final_30cot.xlsx (cập nhật 10/08/2026)

_Từ 10/08/2026 mọi sheet gộp về MỘT file `wave3_ai_final_30cot.xlsx` theo yêu cầu
(file `wave3_dataset_analysis.xlsx` cũ đã bỏ). Sheet `muc_bai` chỉ còn 30 cột Vy
đã chọn giữ; sheet `danh_muc_dataset` thêm 2 cột đầu: `chon_loi` (Vy tick x để chọn
bộ vào bảng chính survey) và `co_ten` (co/khong — bộ có tên riêng hay "(chua dat ten")._

File có **3 sheet**: `muc_bai` (mức BÀI BÁO), `danh_muc_dataset` (mức DATASET — đơn vị
phân tích chính), `MXH_thong_ke` (danh sách riêng để thống kê theo năm).

---

## Sheet 1: `muc_bai` — 7.578 dòng, mỗi dòng 1 BÀI BÁO — 47 cột

Nội dung `wave3_ai_final.csv` SAU KHI LOẠI 10 cột heuristic đã bị vòng rà soát
thay thế (loại 08/08/2026 theo yêu cầu; bản CSV trong `search_exports` vẫn giữ đủ
57 cột làm kho lưu trữ/kiểm toán): `priority_score`, `band`, `R_goi_y`, `hint`,
`bucket`, `dataset_da_biet`, `dataset_ung_vien`, `minhchung_therapy`,
`dataset_cu_heuristic`, `therapy_cu_heuristic`.

### Tóm tắt 40 cột cũ còn giữ, theo nhóm

**📄 Thông tin bài báo:** `rec_id` (mã duy nhất `u3-XXXX`, khóa tra cứu chéo mọi
file/sheet) · `year`, `nam_khac`, `era` (pre-2021 / 2021+) · `venue`, `title`,
`doi_url` · `abstract` (gốc tiếng Anh) · `abstract_bosung` +
`nguon_abstract_bosung` (abstract cứu từ Crossref/OpenAlex) · `abstract_vi`
(dịch tiếng Việt, đủ nhóm ĐÚNG + CHƯA CHẮC).

**📊 Dataset & link:** `dataset` (ĐÃ RÀ LẠI ở vòng dataset — xem bảng dưới) ·
`link_data` + `link_host` (link GitHub/HF/Zenodo… và nơi lưu) · `availability`
(mở/đóng của DỮ LIỆU: open/conditional/closed/mixed/unstated) · `link_dang_ky`
(ClinicalTrials/PROSPERO — không phải link dữ liệu) · `therapy` (ĐÃ RÀ LẠI).

**🗃️ Dấu vết khử trùng:** `n_sources`, `sources` (bài xuất hiện ở CSDL nào) ·
`n_ban_ghi` (số bản ghi thô đã gộp) · `source_chinh` · `gan_trung_voi` (cặp tiêu
đề gần giống, chị tự quyết) · `canh_bao_sieu_du_lieu` (15 dòng OpenAlex gắn sai
tiêu đề vào DOI đúng).

**✍️ Chờ chị điền — mọi script đều giữ nguyên:** `decision_ta`, `decision_ft`,
`include_group` (main/adjacent/eval), `notes`.

**🔎 Duyệt AI tầng 1 — kiểm toán:** `ai_trang_thai`, `ai_phan_loai`,
`ai_R_de_xuat`, `ai_minh_chung`, `ai_lo`, `ai_kiem_tra`.

**🔴 Kết quả sàng lọc cuối:** `final_trang_thai` (DUNG-chac-chan 2.031 /
NGOAI-chac-chan 5.075 / CHUA-CHAC-CHAN 472) · `final_phan_loai` (loại đóng góp:
dataset-moi, danh-gia-benchmark, dung-dataset-cu, …) · `final_R_de_xuat` (gợi ý mã
loại R kèm `?`) · `final_minh_chung` (trích nguyên văn «…» + lý do) · `tang_duyet` ·
`tang2_thay_doi` (giu/nang-cap/lat-nguoc).

**✅ `vy_xac_minh`:** kết quả CHỊ tự kiểm nhóm NGOÀI trong Excel (5.075 dòng
đã điền; trong đó 35 ca chị lật ngược thành DUNG-chac-chan — 35 ca này đã được đưa
vào diện phân tích dataset).

### 7 cột mới của vòng dataset

Chỉ điền cho 3.253 bài thuộc diện phân tích (DUNG + CHUA-CHAC + 35 ca chị lật ngược
+ 715 bài NGOÀI có tín hiệu dữ liệu được vớt lại xét theo miền mở rộng); bài NGOÀI
còn lại để trống:

| Cột | Ý nghĩa |
|---|---|
| `dataset` | **ĐÃ RÀ LẠI**: tên dataset của bài do người rà đọc abstract xác định (thay bản cũ vốn khớp từ khóa tự động). Nhiều dataset phân cách bằng `;`. Bộ mới chưa đặt tên ghi `(chua dat ten: mô tả ngắn)`. Giá trị cũ lưu trong cột `dataset_cu_heuristic` của bản CSV |
| `therapy` | **ĐÃ RÀ LẠI**: nhãn lý thuyết lâm sàng bài sử dụng (CBT, MI, ESC, mindfulness, client-centered, psychodynamic, DBT, ACT, SFBT, REBT, Hill…). Đã gỡ các nhãn trùng từ khóa giả (vd "CBT" = Children's Book Test). Giá trị cũ lưu trong cột `therapy_cu_heuristic` của bản CSV |
| `lien_quan_dataset` | Vai trò của bài đối với dataset: `gioi-thieu-moi` (phát hành bộ mới) · `danh-gia` (benchmark/đánh giá trên bộ nêu tên) · `phat-trien` (mở rộng/chú giải thêm/dịch bộ có sẵn) · `su-dung` (dùng bộ nêu tên làm thực nghiệm) · `khong` (không nêu bộ nào) |
| `nhom_mien` | Miền NỘI DUNG của dataset: `tham-van` · `tri-lieu` · `ESC` (hỗ trợ cảm xúc/đồng cảm, gồm EmpatheticDialogues, ESConv) · `chan-doan` · `sang-loc-lam-sang` (phỏng vấn/hội thoại sàng lọc kiểu DAIC-WOZ) · `khung-hoang` (hotline/crisis text) · `dong-dang` (peer support SKTT) · `dao-tao-ky-nang` (huấn luyện tham vấn viên/bệnh nhân mô phỏng) · `MXH-thong-ke` (phát hiện trầm cảm/tự sát từ bài đăng MXH — KHÔNG vào phân tích chính) · `khac` |
| `phuong_thuc` | Phương thức CỦA DATASET: tổ hợp `text`, `voice`, `video`, `hinh-anh`, `sinh-ly` nối bằng `+` (vd `text+voice`). Luôn phải có text hoặc voice (điều kiện chứa ngôn ngữ) |
| `don_da_luot` | `da-luot` (hội thoại nhiều lượt) · `don-luot` (câu/cặp đơn) · `khong-ro` |
| `ngon_ngu` | Mã ngôn ngữ của dataset: `en`, `zh`, `ko`, `ja`, `vi`… nhiều thì nối `+` (vd `en+zh`); `khong-ro` |
| `nguon_du_lieu` | Nguồn gốc dữ liệu: `hoi-thoai-that` (phiên thật) · `dong-vai` (diễn viên/đóng vai) · `tong-hop-LLM` (sinh bằng LLM) · `MXH-dien-dan` · `hon-hop` · `khong-ro` |
| `ds_minh_chung` | Trích nguyên văn ≤25 từ trong «…» từ abstract + lý do — căn cứ cho `dataset` và `nhom_mien`. Bắt buộc khi `lien_quan_dataset` ≠ `khong` |

**Cách lọc nhanh:** bài thuộc diện phân tích dataset = `lien_quan_dataset` khác rỗng và
khác `khong`; trong đó loại `nhom_mien = MXH-thong-ke` nếu chỉ muốn miền chính.

---

## Sheet 2: `danh_muc_dataset` — 675 dòng, mỗi dòng 1 DATASET (đơn vị phân tích)

Gộp từ sheet 1: các bài nhắc cùng một tên dataset (chuẩn hóa chữ thường, bỏ ký tự
đặc biệt) được gom về 1 dòng. Trường mô tả lấy theo **đa số** các bài nhắc bộ đó.

| Cột | Ý nghĩa |
|---|---|
| `ten_dataset` | Tên đại diện của dataset (biến thể viết phổ biến nhất giữa các bài). Hai bộ trùng tên "HEAL" đã tách thủ công thành 2 dòng riêng |
| `nhom_mien` | Miền nội dung (đa số phiếu giữa các bài) — cùng bộ giá trị như sheet 1 |
| `phuong_thuc` | Phương thức (đa số phiếu) |
| `don_da_luot` | Đơn/đa lượt (đa số phiếu) |
| `ngon_ngu` | Ngôn ngữ (đa số phiếu) |
| `nguon_du_lieu` | Nguồn gốc dữ liệu (đa số phiếu) |
| `ly_thuyet` | HỢP (union) tất cả nhãn lý thuyết lâm sàng từ các bài dùng bộ này, phân cách `;` |
| `nam_som_nhat` | Năm sớm nhất trong các bài nhắc bộ này — xấp xỉ năm dataset xuất hiện trong kho wave 3 (lưu ý: bộ ra đời trước 2021 có thể chỉ được nhắc bởi bài sau này) |
| `n_bai` | Tổng số bài trong kho wave 3 có liên quan bộ này |
| `n_gioi_thieu` | Số bài phát hành bộ này (lien_quan_dataset = gioi-thieu-moi) |
| `n_danh_gia` | Số bài benchmark/đánh giá trên bộ này |
| `n_phat_trien` | Số bài mở rộng/chú giải thêm/dịch bộ này |
| `n_su_dung` | Số bài dùng bộ này làm thực nghiệm |
| `bai_gioi_thieu` | rec_id (kèm năm) của tối đa 4 bài giới-thiệu/phát-triển — để truy về bài gốc trong sheet `muc_bai` |
| `link` | Tối đa 3 link dữ liệu (GitHub/HF/Zenodo/OSF…) gom từ cột `link_data` của các bài |
| `availability` | Tính mở/đóng của dữ liệu (đa số phiếu từ cột availability của các bài) |
| `cac_bai` | rec_id của tối đa 20 bài liên quan — tra ngược sang sheet `muc_bai` |

**Lưu ý:** 83 dòng `nhom_mien = MXH-thong-ke` vẫn nằm trong sheet này (vì có bài
giới thiệu chúng) — lọc bỏ nhóm này khi phân tích miền chính.

---

## Sheet 3: `MXH_thong_ke` — 81 dòng, mỗi dòng 1 BÀI thuộc nhóm MXH

Danh sách riêng theo yêu cầu: dataset phát hiện trầm cảm/tự sát/rối loạn từ bài đăng
mạng xã hội, diễn đàn — chỉ để đếm số lượng theo năm, không vào phân tích chính.
Đã xếp tăng dần theo năm.

| Cột | Ý nghĩa |
|---|---|
| `rec_id` | Mã bài — tra ngược sang sheet `muc_bai` |
| `year` | Năm công bố bài (dùng để đếm theo năm) |
| `ds_ten` | Tên dataset MXH trong bài |
| `title` | Tiêu đề bài |
| `minh_chung` | Trích nguyên văn từ abstract — căn cứ xếp vào nhóm MXH |

Phân bố theo năm (07/08/2026): 2017: 2 · 2018: 4 · 2019: 2 · 2020: 11 · 2021: 5 ·
2022: 5 · 2023: 10 · 2024: 14 · 2025: 17 · 2026: 11.
