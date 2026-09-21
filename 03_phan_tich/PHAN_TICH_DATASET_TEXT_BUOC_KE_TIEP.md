# PHÂN TÍCH DATASET VĂN BẢN (TEXT) & CÁC BƯỚC HOÀN THIỆN SURVEY
_Lập 10/08/2026, từ `wave3_dataset_analysis.xlsx` (675 dataset, 7.578 bài wave 3)._
_Mọi con số ở mức abstract — thông số chi tiết cần xác nhận khi đọc toàn văn (bước 2)._

---

## 1. Bức tranh tổng thể: dataset TEXT là tuyệt đối chủ đạo

Trong 675 dataset duy nhất, bỏ 83 bộ nhóm MXH-thống-kê còn **592 bộ thuộc miền chính**:

| Lớp phương thức | Số bộ | Ghi chú |
|---|---|---|
| **Text thuần** | **488 (82%)** | LÕI PHÂN TÍCH của survey |
| Text + đa phương thức | 75 (13%) | text+voice 57 · text+voice+video 8 · text+hinh-anh 5 · text+video 4 · text+voice+hinh-anh 1 |
| Không có text (voice/video thuần) | 29 (5%) | voice 24, voice+video 4 — chỉ điểm danh, không phân tích sâu |

→ Khung survey hợp lý: **phân tích lõi 488 bộ text thuần**; nhóm text+X trình bày như
"lớp mở rộng đa phương thức" (điểm chung: lời thoại được chuyển văn bản vẫn là thành
phần phân tích chính); nhóm thuần voice/video chỉ nêu trong 1 đoạn giới hạn phạm vi.

## 2. Sáu phát hiện chính cho phần tổng quan của survey

**(1) Phân mảnh cực mạnh — thiếu benchmark chung.** 546/563 bộ text-core (97%) chỉ
xuất hiện trong đúng 1 bài của kho. Chỉ 3 bộ được tái sử dụng đáng kể:
EmpatheticDialogues (34 bài; 22 sử dụng + 7 đánh giá), DAIC-WOZ (6), ESConv (5).
→ Luận điểm survey: cộng đồng liên tục TẠO MỚI thay vì TÁI SỬ DỤNG; so sánh giữa các
nghiên cứu gần như bất khả thi vì không có benchmark lâm sàng chung.

**(2) Bùng nổ theo thời gian gắn với LLM.** Năm xuất hiện của bộ text-core:
1999–2015 lác đác (≤6/năm) → 2018: 23 → 2020: 36 → 2022: 45 → 2023: 69 → 2024: 76 →
**2025: 107 → 2026: 95** (nửa đầu năm). Hơn nửa toàn bộ dataset ra đời từ 2023.
→ Vẽ hình timeline; chia 3 thời kỳ: tiền-BERT (trước 2018), thời PLM (2018–2022),
thời LLM (2023–nay).

**(3) Nguồn gốc dữ liệu đang chuyển dịch.** Text thuần: hội thoại thật 235 (48%),
MXH/diễn đàn 56, hỗn hợp 46, đóng vai 33, **tổng hợp bằng LLM 28** (gần như toàn bộ
xuất hiện 2023+), không rõ 90. → Câu chuyện survey: căng thẳng giữa tính chân thực
lâm sàng (phiên thật, khó chia sẻ) và tính khả dụng (đóng vai/LLM sinh, chia sẻ được
nhưng nghi vấn giá trị lâm sàng).

**(4) Khoảng trống lý thuyết lâm sàng — đúng trọng tâm chị muốn.** Chỉ **178/563
(32%)** bộ text-core gắn được với một lý thuyết: ESC 67, CBT 47, MI 41,
psychodynamic 14, client-centered 10, mindfulness 4, SFBT 1, ACT 1. 68% không neo
vào trường phái nào. → Đây là ĐÓNG GÓP CHÍNH của survey: soi danh mục dataset qua
lăng kính lý thuyết lâm sàng và chỉ ra vùng trũng (DBT, ACT, SFBT, REBT gần như
không có dataset).

**(5) Tính mở không được công bố.** 442/563 (79%) abstract không nói gì về chia sẻ
dữ liệu; chỉ 34 bộ khẳng định open, 7 closed, 5 mixed. → Không được kết luận "đa số
đóng" từ abstract; bảng chính của survey phải kiểm toàn văn/kho lưu trữ cho từng bộ
lõi (bước 2). Đây cũng là phát hiện đáng viết: chuẩn công bố dữ liệu của miền còn kém.

**(6) Anh ngữ áp đảo, đa dạng ngôn ngữ thấp.** Trong số nêu rõ: en 140, zh 26, ko 13,
ja 13, de 6, nl 5, es 4…; 260 bộ không nêu (đa phần ngầm hiểu tiếng Anh — xác nhận ở
toàn văn). Đông Á (zh/ko/ja) là cụm phi-Anh ngữ lớn nhất. Không có tiếng Việt.

Cấu trúc dữ liệu bổ trợ: đa lượt 291 vs đơn lượt 124 (đa lượt chiếm ưu thế — phù hợp
trọng tâm hội thoại tham vấn/trị liệu); phân bố nhánh miền của text thuần: trị liệu
138, tham vấn 124, ESC 82, đồng đẳng 43, khủng hoảng 30, đào tạo kỹ năng 22,
chẩn đoán 17, sàng lọc lâm sàng 10, khác 22.

## 3. Các bước kế tiếp (đề xuất thứ tự)

**B1 — Chị chốt danh mục lõi (việc của chị, ~1–2 buổi).**
Mở sheet `danh_muc_dataset`, lọc `nhom_mien ≠ MXH-thong-ke` và `phuong_thuc` chứa
"text". Duyệt từ trên xuống (đã xếp theo nhánh miền, n_bai giảm dần), đánh dấu vào
cột mới `chon_loi` (x = vào bảng chính survey). Gợi ý tiêu chí: (a) có bài giới
thiệu trong kho (287 bộ) HOẶC được ≥2 bài dùng; (b) thuộc 5 nhánh lâm sàng trọng
tâm (tham vấn, trị liệu, ESC, khủng hoảng, sàng lọc lâm sàng); (c) mô tả đủ rõ
trong `ds_minh_chung`. Ước lượng còn ~120–180 bộ lõi.

**B2 — Kiểm toàn văn nhóm lõi (tôi hỗ trợ trích xuất, chị cung cấp PDF).**
Với từng bộ lõi xác nhận từ toàn văn: kích thước (số phiên/cặp thoại), đơn vị chú
giải, giấy phép + availability thực tế (link kho), ngôn ngữ, lý thuyết lâm sàng,
quy trình đạo đức (IRB/ẩn danh). Mục tiêu: xóa phần lớn `khong-ro` trước khi lên
bảng. Đây là bước bắt buộc vì 79% availability đang trống từ abstract.

**B3 — Dựng khung bảng/hình cho survey (tôi làm nháp, chị duyệt).**
- Bảng B-a: dataset lõi theo nhánh miền (tên, năm, nguồn gốc, đơn/đa lượt, ngôn ngữ,
  kích thước, lý thuyết, mở/đóng, link) — mỗi nhánh một khối.
- Bảng B-b: ma trận lý thuyết lâm sàng × dataset (làm nổi vùng trũng DBT/ACT/SFBT).
- Hình H-a: timeline số dataset mới theo năm, tô theo nguồn gốc (thật/đóng vai/LLM)
  — kể câu chuyện chuyển dịch (3).
- Hình H-b: sơ đồ phân loại (taxonomy) nhánh miền + lớp phương thức.
- Hộp thảo luận: 6 phát hiện ở mục 2.

**B4 — Phụ lục MXH.** Sheet `MXH_thong_ke` (81 bài) đếm theo năm — đã có sẵn số:
2017:2 · 2018:4 · 2019:2 · 2020:11 · 2021:5 · 2022:5 · 2023:10 · 2024:14 · 2025:17 ·
2026:11. Chỉ cần 1 đoạn + 1 hình cột nhỏ, nêu rõ lý do loại khỏi phân tích chính
(không phải hội thoại lâm sàng).

**B5 — Cập nhật Methods + PRISMA.** Bổ sung nhánh wave 3 vào lưu đồ: 16.987 bản ghi
thô → 9.851 duy nhất → 7.578 mới → sàng lọc 2 tầng → 3.253 vào vòng dataset → 701
bài gắn dataset → 675 bộ (592 miền chính, 563 text-core) → danh mục lõi sau B1–B2.
Ghi rõ đơn vị phân tích là DATASET, tiêu chí bắt buộc chứa ngôn ngữ, MXH tách riêng.

**B6 — Viết mục survey.** Sau B1–B3, tôi soạn nháp mục "Tổng quan tài nguyên dữ liệu
văn bản" theo cấu trúc: mở đầu phạm vi → taxonomy → phân tích theo nhánh (mỗi nhánh:
bộ tiêu biểu + xu hướng) → 6 phát hiện xuyên suốt → hạn chế (trích từ abstract, thiên
lệch tiếng Anh của truy vấn).

## 4. Lưu ý phương pháp (ghi vào phần hạn chế của survey)
- Trường thông tin trích từ ABSTRACT; `khong-ro` nghĩa là "abstract không nói",
  không phải "không có" — đã xử lý bằng B2 cho nhóm lõi.
- 546 bộ chỉ-1-bài có thể gồm bộ nội bộ không bao giờ phát hành; bảng chính chỉ nên
  giữ bộ có mô tả/phát hành rõ.
- Ranh giới ESC đã thống nhất (EmpatheticDialogues/ESConv thuộc miền, nhánh ESC);
  2 bộ trùng tên HEAL đã tách; tên dataset hiển thị theo biến thể phổ biến nhất.
