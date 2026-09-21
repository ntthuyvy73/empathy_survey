# -*- coding: utf-8 -*-
"""P1 WAVE 3 — DOI CHIEU tai nguyen (dataset/benchmark) trong nhom DUNG voi danh muc
123 bai da chot cua khao sat (included_resources.csv) + danh muc KNOWN cu.

Pham vi: final_trang_thai == DUNG-chac-chan va final_phan_loai thuoc
{dataset-moi, danh-gia-benchmark, dung-dataset-cu}.
Khop ten sau chuan hoa (bo hoa/thuong, '-', '_', khoang trang). Moi bai xep vao:
  - "BO MOI"            : co ten ung vien khong trung danh muc (hoac dataset-moi chua ro ten)
  - "trung-bo-da-chot"  : chi nhac ten da co -> bang chung su dung, khong phai tai nguyen moi
Xuat: search_exports/wave3_tai_nguyen_moi.csv + _notes/wave3_tai_nguyen_report.md
Chay: python wave3_doi_chieu_tai_nguyen.py"""
import csv
import os
import re
import sys
from collections import Counter
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract_datasets as XD

NOTES = os.path.dirname(os.path.abspath(__file__))
EXPORTS = os.path.join(os.path.dirname(NOTES), "bai_bao", "search_exports")
PL_SCOPE = {"dataset-moi", "danh-gia-benchmark", "dung-dataset-cu"}


def norm_name(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def read_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    # danh muc da biet: dataset_key cua 123 bai da chot + KNOWN cu
    known = {}
    for r in read_rows(os.path.join(EXPORTS, "included_resources.csv")):
        k = (r.get("dataset_key") or "").strip()
        if k and not re.match(r"^rec\d+$", k):        # bo placeholder recNNNN
            known[norm_name(k)] = k
    for k in XD.KNOWN:
        known.setdefault(norm_name(k), k)
    print(f"Danh muc da biet: {len(known)} ten (123-da-chot + KNOWN cu)")

    rows = read_rows(os.path.join(EXPORTS, "wave3_ai_final.csv"))
    scope = [r for r in rows if r["final_trang_thai"] == "DUNG-chac-chan"
             and r["final_phan_loai"] in PL_SCOPE]
    print(f"Bai DUNG thuoc pham vi tai nguyen: {len(scope)} "
          f"({Counter(r['final_phan_loai'] for r in scope)})")

    out, moi_names = [], Counter()
    for r in scope:
        names = [n.replace("(?)", "").strip() for n in (r.get("dataset") or "").split(";")
                 if n.strip()]
        # them ten truoc dau ':' trong tieu de neu la dataset-moi va chua co ten
        if not names and r["final_phan_loai"] == "dataset-moi":
            m = re.match(r"\s*([A-Za-z0-9][\w\-]{2,30})\s*:", r["title"].replace("{", "").replace("}", ""))
            if m and m.group(1).lower() not in XD.STOP:
                names = [m.group(1)]
        trung = sorted({known[norm_name(n)] for n in names if norm_name(n) in known})
        moi = sorted({n for n in names if norm_name(n) not in known and len(norm_name(n)) >= 3})
        if r["final_phan_loai"] == "dataset-moi" and not moi and not trung:
            nhom = "BO-MOI-chua-ro-ten"
        elif moi:
            nhom = "BO-MOI"
            for n in moi:
                moi_names[n] += 1
        elif trung:
            nhom = "trung-bo-da-chot"
        else:
            nhom = "khong-ro-ten"
        out.append(dict(nhom=nhom, rec_id=r["rec_id"], year=r.get("year", ""),
                        era=r.get("era", ""), phan_loai=r["final_phan_loai"],
                        ten_moi="; ".join(moi), trung_da_chot="; ".join(trung),
                        availability=r.get("availability", ""),
                        link_data=r.get("link_data", ""), sources=r.get("sources", ""),
                        title=r["title"], minh_chung=r.get("final_minh_chung", "")[:250],
                        doi_url=r.get("doi_url", "")))

    order = {"BO-MOI": 0, "BO-MOI-chua-ro-ten": 1, "khong-ro-ten": 2, "trung-bo-da-chot": 3}
    out.sort(key=lambda x: (order[x["nhom"]], x["year"] or "0000"))
    out_csv = os.path.join(EXPORTS, "wave3_tai_nguyen_moi.csv")
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    c_nhom = Counter(x["nhom"] for x in out)
    bo_moi = [x for x in out if x["nhom"].startswith("BO-MOI")]
    pre = [x for x in bo_moi if x["era"] == "pre-2021"]
    co_link = [x for x in bo_moi if (x["link_data"] or "").strip()]

    L = [f"# Wave 3 — Tài nguyên (dataset/benchmark) MỚI so với 123 bài đã chốt",
         f"\n_Chạy: {date.today()} · Chi tiết: `wave3_tai_nguyen_moi.csv` "
         f"({len(out)} bài trong phạm vi)_\n",
         "## 1. Tổng quan",
         "| Nhóm | Số bài | Nghĩa |", "|---|---|---|",
         f"| BO-MOI | {c_nhom.get('BO-MOI', 0)} | có tên tài nguyên KHÔNG trùng danh mục đã chốt |",
         f"| BO-MOI-chua-ro-ten | {c_nhom.get('BO-MOI-chua-ro-ten', 0)} | AI xếp dataset-mới nhưng heuristic chưa bắt được tên — đọc abstract để đặt tên |",
         f"| trung-bo-da-chot | {c_nhom.get('trung-bo-da-chot', 0)} | chỉ nhắc bộ đã có trong khảo sát → bằng chứng mức độ sử dụng |",
         f"| khong-ro-ten | {c_nhom.get('khong-ro-ten', 0)} | benchmark/dùng-bộ-cũ không nêu tên rõ |",
         f"\n- Tên tài nguyên mới xuất hiện: **{len(moi_names)}** "
         f"(bài pre-2021: {len(pre)}; có link dữ liệu: {len(co_link)})",
         "\n## 2. Danh sách BỘ MỚI (theo năm)",
         "| Năm | Tên đề xuất | Phân loại | Mở/đóng | Link | Tiêu đề |", "|---|---|---|---|---|---|"]
    for x in bo_moi:
        L.append(f"| {x['year']} | {(x['ten_moi'] or '(đặt tên khi đọc)')[:36]} | "
                 f"{x['phan_loai']} | {x['availability']} | "
                 f"{(x['link_data'].split('; ')[0] if x['link_data'] else '-')[:40]} | "
                 f"{x['title'][:80]} |")
    L += ["\n## 3. Bộ đã chốt được wave 3 nhắc lại (mức độ sử dụng)",
          "| Bộ | Số bài mới nhắc |", "|---|---|"]
    c_trung = Counter(t for x in out for t in x["trung_da_chot"].split("; ") if t)
    for k, v in c_trung.most_common():
        L.append(f"| {k} | {v} |")
    L += ["\n## 4. Cách dùng & giới hạn",
          "- Nhóm **BO-MOI** là ứng viên bổ sung cho bảng tài nguyên của khảo sát — cần đọc "
          "toàn văn xác nhận (EC5/EC6/EC9: có phát hành thật không, đủ mô tả để mã hóa không).",
          "- Khớp tên là heuristic sau chuẩn hóa; một bộ có thể xuất hiện dưới tên khác "
          "(viết tắt ↔ tên đầy đủ) — khi đọc toàn văn nếu phát hiện trùng thì gán R6.",
          "- Danh mục đối chiếu = `dataset_key` trong `included_resources.csv` (123 bài đã "
          "chốt, bỏ khóa placeholder recNNNN) + danh mục KNOWN của vòng sàng lọc trước."]
    out_md = os.path.join(NOTES, "wave3_tai_nguyen_report.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

    print(f"\n=== KET QUA DOI CHIEU ===")
    for k, v in sorted(c_nhom.items(), key=lambda x: order[x[0]]):
        print(f"  {k:22s}: {v}")
    print(f"  Ten bo MOI: {len(moi_names)} | pre-2021: {len(pre)} | co link: {len(co_link)}")
    print(f"  Top ten moi: {moi_names.most_common(15)}")
    print(f"\n  CSV: {out_csv}")
    print(f"  Bao cao: {out_md}")


if __name__ == "__main__":
    main()
