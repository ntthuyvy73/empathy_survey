# RUBRIC TRÍCH XUẤT DATASET — vòng phân tích lấy DATASET làm đơn vị (06/08/2026)

## Bối cảnh và mục tiêu
Khảo sát lấy **dataset làm đơn vị phân tích**. Miền đã MỞ RỘNG so với vòng sàng lọc trước:
tham vấn, trị liệu, hỗ trợ cảm xúc (ESC), **chẩn đoán**, **sàng lọc lâm sàng** — đều trong
ngữ cảnh sức khỏe tâm thần / lâm sàng tâm lý. Mục tiêu: bao quát "đang có những dataset
gì", soi theo lý thuyết lâm sàng.

## Điều kiện dataset được tính
1. **Bắt buộc chứa NGÔN NGỮ** (văn bản hoặc lời thoại). Bộ thuần EEG/hình ảnh/cảm biến
   không kèm ngôn ngữ → không tính.
2. Thuộc miền SKTT/lâm sàng tâm lý mở rộng ở trên.
3. **Ngoại lệ MXH**: dataset phát hiện trầm cảm/tự sát/rối loạn từ bài đăng mạng xã hội,
   diễn đàn (Reddit, Twitter, Weibo…) — KHÔNG vào phân tích chính, nhưng ghi vào
   **danh sách riêng** (nhom_mien = `MXH-thong-ke`) để thống kê số lượng theo năm.

## Trường trích xuất cho TỪNG BÀI (đọc kỹ abstract; không suy diễn ngoài văn bản)

| Trường | Giá trị cho phép | Ghi chú |
|---|---|---|
| `lien_quan_dataset` | `gioi-thieu-moi` · `danh-gia` · `phat-trien` · `su-dung` · `khong` | mới = bài phát hành bộ mới; đánh giá = benchmark/đánh giá mô hình TRÊN bộ nêu tên; phát triển = mở rộng/chú giải thêm/dịch bộ có sẵn; sử dụng = dùng bộ nêu tên làm thực nghiệm; `khong` = không nêu bộ nào (bài lý thuyết/tổng quan/thử nghiệm không rõ dữ liệu) |
| `ds_ten` | tên bộ, phân cách `;` | lấy đúng tên trong abstract (ESConv, DAIC-WOZ…); bộ mới chưa đặt tên → `(chua dat ten: mo ta ngan)` |
| `nhom_mien` | `tham-van` · `tri-lieu` · `ESC` · `chan-doan` · `sang-loc-lam-sang` · `khung-hoang` · `dong-dang` · `dao-tao-ky-nang` · `MXH-thong-ke` · `khac` | theo NỘI DUNG dataset, không theo ứng dụng bài. `khung-hoang` = hotline/crisis text; `dong-dang` = peer support SKTT; `dao-tao-ky-nang` = huấn luyện tham vấn viên/bệnh nhân mô phỏng; `sang-loc-lam-sang` = phỏng vấn/hội thoại sàng lọc (kiểu DAIC-WOZ) — KHÔNG phải bài đăng MXH |
| `phuong_thuc` | tổ hợp từ: `text`, `voice`, `video`, `hinh-anh`, `sinh-ly`; nối bằng `+` (vd `text+voice`) | phương thức CỦA DATASET; phải có `text` hoặc `voice` (điều kiện ngôn ngữ) |
| `don_da_luot` | `don-luot` · `da-luot` · `khong-ro` | hội thoại đa lượt hay câu/cặp đơn |
| `ngon_ngu` | mã: `en`, `zh`, `ko`, `ja`, `vi`, `de`,… ; nhiều thì `en+zh`; `khong-ro` | ngôn ngữ của dataset |
| `nguon_du_lieu` | `hoi-thoai-that` · `dong-vai` · `tong-hop-LLM` · `MXH-dien-dan` · `hon-hop` · `khong-ro` | phiên thật / diễn viên-đóng vai / sinh bằng LLM / thu từ MXH-diễn đàn |
| `therapy_ra_soat` | nhãn lý thuyết đúng của bài: `CBT`,`MI`,`ESC`,`mindfulness`,`client-centered`,`psychodynamic`,`DBT`,`ACT`,`SFBT`,`REBT`,`Hill`, hoặc `(khong)` | RÀ LẠI cột therapy cũ (vốn khớp từ khóa): xác nhận đúng, bỏ nhãn sai, thêm nhãn thiếu |
| `minh_chung` | trích nguyên văn ≤25 từ trong «…» + 1 mệnh đề | căn cứ cho ds_ten + nhom_mien; bắt buộc khi lien_quan_dataset ≠ `khong` |

## Quy tắc cứng
- Chỉ dùng title + abstract ĐƯỢC CẤP; cấm kiến thức ngoài; không rõ → `khong-ro`.
- Một bài nhiều dataset → liệt kê hết trong `ds_ten`, các trường mô tả lấy theo bộ CHÍNH
  (bộ được bài đóng góp/tập trung nhất) và ghi chú bộ phụ trong minh_chung.
- Bài NGOÀI-vớt-lại: nếu là chẩn đoán/sàng lọc lâm sàng có dataset ngôn ngữ → trích đầy đủ;
  nếu là MXH → `nhom_mien=MXH-thong-ke` + ds_ten + năm là đủ; nếu vẫn ngoài miền
  (y khoa thể chất, không ngôn ngữ) → `lien_quan_dataset=khong`.
