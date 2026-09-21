# RUNBOOK — Vòng hoàn thiện chính xác cao (Opus trích xuất → Fable kiểm định)
_Lập 11/08/2026. Dành cho phiên hẹn giờ tự chạy. Làm theo đúng thứ tự, không bỏ bước._

## Mục tiêu
Hoàn thiện các ô blanks/khong-ro của 1.250 bài trong sheet `text-dataset`
(file `H:\Vy\Paper\Empathy\Report\_Chuan_bi\_analyst_v7\wave3_nlp_tham_van\03_phan_tich\wave3_ai_final_30cot.xlsx`)
cho các cột: ngon_ngu (734), availability (1.212), nguon_du_lieu (291), don_da_luot (86).
Chuẩn Q1: mọi giá trị phải kèm minh chứng «trích nguyên văn» + nguồn (abstract/URL).
KHÔNG chạy vòng "sàng lọc 2 tầng sl_*" (Vy đã hủy).

## Thư mục làm việc
DS = C:\Users\ntthu\AppData\Local\Temp\claude\H--Vy-Paper-Empathy-Report--Chuan-bi--analyst-v7\ad01b8ac-860b-4c9c-a6d5-9991cfddf4d3\scratchpad\ai_screen\ds_extract
- Đầu vào: ht_batch_01.jsonl … ht_batch_50.jsonl + ht_manifest.json (mỗi dòng: rec_id,
  title, doi_url, dataset, abstract, thieu=[các cột cần điền]).
- Tầng 1 (Opus) ghi: ht_batch_XX_out.jsonl
- Tầng 2 (Fable) ghi: hv_batch_XX_out.jsonl (kiểm định lô XX tương ứng)

## Quy trình mỗi lần phiên hẹn giờ nổ
1. KIỂM KÊ: đối chiếu ht_batch_*_out.jsonl và hv_batch_*_out.jsonl với ht_manifest.json
   (đếm rec_id hợp lệ từng lô; lô thiếu một phần → chạy bù đúng phần thiếu, ghi *_out2
   rồi ghép như quy trình cũ).
2. TẦNG 1 — Agent model **opus**, tối đa 8 lô song song, phóng thay thế khi lô xong.
   Prompt tầng 1 (giữ nguyên): đọc lô ht_batch_XX.jsonl; với TỪNG bài CHỈ xét các trường
   trong "thieu": (a) đọc sâu abstract, được suy luận CÓ CĂN CỨ từ ngữ cảnh (Weibo→tiếng
   Trung, Reddit→tiếng Anh, "available at github"→open) và nêu căn cứ; (b) không đủ →
   WebFetch doi_url/arXiv/Semantic Scholar (≤2 lần thử/bài). Giá trị hợp lệ: ngon_ngu =
   TÊN ĐẦY ĐỦ tiếng Việt; don_da_luot = da-luot|don-luot|khong-ro; nguon_du_lieu =
   hoi-thoai-that|dong-vai|tong-hop-LLM|MXH-dien-dan|hon-hop|khong-ro; availability =
   open|conditional|closed|mixed|unstated. Ra JSONL đúng thứ tự: {"rec_id", <trường đã
   xét>, "minh_chung":"«trích ≤25 từ» — nguồn: abstract HOẶC <URL>"}. Cấm đoán vô căn cứ.
3. TẦNG 2 — Agent model **fable**, chỉ chạy cho lô đã có ht_batch_XX_out.jsonl mà chưa có
   hv_batch_XX_out.jsonl. Prompt tầng 2: đọc CẢ ht_batch_XX.jsonl (gốc) và
   ht_batch_XX_out.jsonl (phán quyết Opus); với TỪNG bài: đối chiếu minh chứng với
   abstract/nguồn — giá trị đúng thì giữ, sai thì SỬA (tự tra lại web nếu cần), ca Opus
   để khong-ro/unstated thì tự xác định lại (đọc abstract + mở nguồn); ra JSONL
   hv_batch_XX_out.jsonl đúng thứ tự: {"rec_id", <trường>, "kiem_dinh":"giu|sua|bo-sung",
   "minh_chung":"«trích» — nguồn"}. Giá trị cuối = bản của Fable.
4. GỘP (chỉ khi ĐỦ 50/50 lô hv): giá trị cuối lấy từ hv (fallback ht nếu hv thiếu trường);
   cập nhật các cột tương ứng của sheet `all` theo rec_id; nối minh chứng vào ds_minh_chung
   với nhãn " | HT(Opus->Fable): "; dựng lại sheet text-dataset (lọc phuong_thuc chứa
   text từ all) và danh_muc_text-dataset (schema: chon_loi, co_ten, ten_dataset,
   nhom_mien, phuong_thuc, don_da_luot, ngon_ngu, nguon_du_lieu, ly_thuyet, nam_som_nhat,
   n_bai, n_gioi_thieu, n_danh_gia, n_phat_trien, n_su_dung, bai_gioi_thieu, link,
   availability, cac_bai; gộp theo tên chuẩn hóa ≥2 ký tự; MXH-thong-ke xếp cuối).
   Tham khảo code mẫu: scratchpad\sua_3_van_de.py (phần dựng lại 2 sheet).
   Lưu ý file xlsx có thể đang mở trong Excel (PermissionError) → báo Vy đóng file.
5. HOÀN TẤT: khi bước 4 xong và file đã lưu — XÓA LỊCH TỰ CHẠY (scheduled task tên
   "wave3-ht-tu-chay") rồi gửi file + báo cáo tóm tắt cho Vy. Nếu chưa xong mà phiên sắp
   cạn → cứ để lịch nổ lần sau chạy tiếp, KHÔNG xóa lịch.

## Nguyên tắc bất di bất dịch (theo Vy)
- Không bịa số/không đoán vô căn cứ; khong-ro/unstated chỉ dùng khi đã tra mà không thấy.
- Không tạo cột mới, không tạo file mới ngoài quy ước trên; một file Excel duy nhất.
- Chạm giới hạn phiên → phần đã ghi trên đĩa là chân lý; lần sau cứu–gộp–chạy bù.
