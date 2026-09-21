# Dùng file nào? (cập nhật 02/08/2026)

## ✅✅ MỚI NHẤT: `wave3_ai_final.csv` — kết quả duyệt AI 2 tầng TỪNG BÀI

**7.578 bài, mỗi bài đã được AI đọc abstract và phán quyết, kèm minh chứng trích nguyên văn.**

| Cột | Nghĩa |
|---|---|
| `final_trang_thai` | `DUNG-chac-chan` (2.011) · `NGOAI-chac-chan` (5.062) · `CHUA-CHAC-CHAN` (505) |
| `final_phan_loai` | dataset-moi (81) · danh-gia-benchmark (127) · phan-tich-ngon-ngu-lam-sang (241) · phuong-phap-he-thong (572) · thu-nghiem-nguoi-dung (566) · tong-quan (398) · dung-dataset-cu (26)… |
| `final_minh_chung` | Trích **nguyên văn** từ abstract trong «…» + lý do — đã đối chiếu tự động với abstract gốc |
| `final_R_de_xuat` | Gợi ý mã loại R2?/R4?/R8? (luôn có dấu `?`) |
| `tang_duyet` | 1 = chỉ tầng 1 (Sonnet); 2 = đã qua tầng 2 (Opus) phán quyết lại |
| `tang2_thay_doi` | giu / nang-cap / lat-nguoc so với tầng 1 |

Quy trình: tầng 1 (Sonnet, 51 lô) đọc từng bài; câu trích minh chứng được script đối chiếu
với abstract — trích sai tự động hạ xuống "chưa chắc". Tầng 2 (Opus — thay Fable vì hết
hạn mức giữa chừng) phán quyết lại 3.451 bài (toàn bộ ĐÚNG + chưa chắc + tín hiệu ngược).
Đọc kèm: `wave3_ai_screen_report.md` (số liệu + 37 ca hai tầng lật nhau) và
`wave3_ai_screen_rubric.md` (rubric phân xử — một phần Methods).

⚠️ 505 bài CHUA-CHAC-CHAN (đa số thiếu abstract) và 37 ca lật ngược là nhóm chị cần tự
quyết. Quyết định cuối vẫn là của chị — cột `decision_ta` để trống chờ điền.

## File nền tảng trước đó — bắt đầu từ đây nếu muốn tự sàng bằng tay

**`wave3_screening_sorted.csv`** — **7.578 bài duy nhất, ĐÃ SẮP THEO ƯU TIÊN**.
Giống hệt file `wave3_unique_for_screening.csv` nhưng thêm 4 cột ở đầu và sắp xếp
từ liên quan nhất xuống:

| Cột | Nghĩa |
|---|---|
| `priority_score` | Điểm liên quan (cao = đọc trước) |
| `band` | A đọc trước (666) · B cần đọc (1.723) · C ít khả năng (4.243) · D nhiều khả năng loại (946) |
| `R_goi_y` | Gợi ý mã loại R2/R8 — **luôn có dấu `?`, chỉ là gợi ý**, không phải quyết định |
| `hint` | Vì sao được điểm đó |

Chị chỉ cần đọc kỹ **nhóm A + B = 2.389 bài** (32%); 581/641 bài có tên dataset đều nằm trong đó.
Đọc kèm **`wave3_prioritize_report.md`**.

**`wave3_shortlist_dataset.csv`** (772 bài) — rút gọn: chỉ bài có tên dataset hoặc có link
dữ liệu. Đây là nơi khả năng tìm ra tài nguyên mới cho khảo sát cao nhất.

⚠️ **186 bài không có abstract** (nguồn chỉ trả tiêu đề) được kéo hết về nhóm B và đánh dấu
`THIEU-ABSTRACT-can-doc-tay` — đừng loại chúng theo điểm, phải tra toàn văn.

## Bảng dữ liệu gốc (không sắp xếp)

**`wave3_unique_for_screening.csv`** — **7.578 bài báo duy nhất**, mỗi bài một dòng.

Cột đáng chú ý:

| Cột | Nội dung |
|---|---|
| `dataset` | Tên bộ dữ liệu nhắc trong bài. Hậu tố **`(?)`** = tên trùng từ tiếng Anh thường, **cần chị xác nhận** (có thể là thang đo/tên thử nghiệm chứ không phải dataset) |
| `link_data` | Link dữ liệu/mã nguồn nêu trong abstract (GitHub, Hugging Face, Zenodo, OSF…) |
| `link_host` | Nơi lưu tương ứng; `khac` = tên miền lạ, có thể là trang dự án riêng |
| `link_dang_ky` | Link đăng ký thử nghiệm/đề cương (ClinicalTrials, PROSPERO…) — **không phải** link dữ liệu |
| `n_sources`, `sources` | Bài này xuất hiện ở mấy CSDL và là những CSDL nào |
| `n_ban_ghi` | Số bản ghi thô đã gộp lại thành dòng này |
| `gan_trung_voi` | Cảnh báo có bài khác tiêu đề gần giống (script **không** tự gộp) — 26 cặp |
| `canh_bao_sieu_du_lieu` | 15 dòng: CSDL nguồn gắn **sai tiêu đề vào DOI đúng** (lỗi của OpenAlex). Cột này lưu tiêu đề rác đã bị loại; tiêu đề giữ lại chọn theo bỏ phiếu đa số |
| `nam_khac` | Nhóm có nhiều năm khác nhau (preprint ↔ bản xuất bản) |
| `decision_ta`, `decision_ft`, `include_group`, `notes` | **Cột trống để chị điền**; chạy lại script vẫn giữ nguyên |

Đọc kèm: **`wave3_unique_report.md`** (báo cáo phân tích) và **`wave3_duplicate_groups.csv`** (nhật ký: nhóm nào gộp từ những bản ghi nào — dùng để kiểm tra khi nghi ngờ).

## ⛔ File CŨ — không dùng để sàng lọc nữa

- `wave3_new_for_screening.csv` (7.834 dòng) — bản khử trùng **yếu**, còn sót trùng: cùng một bài bị đếm 2 lần khi tiêu đề có ngoặc nhọn BibTeX (`{A}rabic`), ký hiệu LaTeX (`$\psi$`), hoặc hậu tố `(Preprint)`.
- `wave3_dataset_annotations.csv` + `wave3_report.md` — phân tích trên bản cũ đó.

Giữ lại chỉ để đối chiếu lịch sử. Chênh lệch: 7.834 → **7.578** (gộp thêm 256 bài trùng sót,
đồng thời **tách lại** những bài từng bị gộp nhầm qua tiêu đề chung chung như "WITHDRAWN").

## Chạy lại khi có dữ liệu mới

```
cd "vy\New folder\ket_qua_phan_tich\_notes"
python p1_wave3_delta.py          # đồng bộ file mới từ 02_ket_qua_tho + khử trùng cơ bản
python wave3_unique_enrich.py     # khử trùng mạnh + cột dataset/link
python wave3_prioritize.py        # sắp ưu tiên  ← ra file chính để sàng lọc
```

Quyết định chị đã điền (`decision_ta`, `decision_ft`, `include_group`, `notes`) được
giữ nguyên qua các lần chạy lại — script khớp theo tiêu đề chuẩn hóa.
