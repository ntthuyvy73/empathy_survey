# -*- coding: utf-8 -*-
"""P1 WAVE 3 — GOP TANG 2 vao ket qua cuoi cua quy trinh duyet AI 2 tang.

Doc: wave3_ai_screened.csv (tang 1 da gop) + <scratch>/tier2/tier2_XX_verdict.jsonl.
Ap phan quyet tang 2 DE LEN tang 1 cho cac bai thuoc dien tang 2; bai chi qua tang 1
(NGOAI ro rang) giu nguyen. Xac minh minh chung tang 2 nhu tang 1 (trich «...» phai
co that, cho phep 'doan A ... doan B'); trich sai -> ha xuong CHUA-CHAC-CHAN.

Xuat:
  search_exports/wave3_ai_final.csv    — 7578 dong, cot cuoi: final_trang_thai,
      final_phan_loai, final_R_de_xuat, final_minh_chung, tang_duyet (1|2),
      tang2_thay_doi (giu|lat-nguoc|nang-cap)
  _notes/wave3_ai_screen_report.md     — bao cao phuong phap + so lieu + bat dong 2 tang
ASSERT: du 7578 dong; moi bai co final_trang_thai; khong con '(chua duyet)'.
Chay: python wave3_ai_final.py <scratch_dir>"""
import csv
import json
import os
import re
import sys
import unicodedata
from collections import Counter
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NOTES = os.path.dirname(os.path.abspath(__file__))
EXPORTS = os.path.join(os.path.dirname(NOTES), "bai_bao", "search_exports")
SRC = os.path.join(EXPORTS, "wave3_ai_screened.csv")
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(NOTES, "_ai_screen")
T2 = os.path.join(SCRATCH, "tier2")

TT = {"DUNG-chac-chan", "NGOAI-chac-chan", "CHUA-CHAC-CHAN"}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def quote_ok(mc, title, abstract):
    m = re.search(r"«([^»]{3,400})»", mc or "")
    if not m:
        return False
    hay = norm(title + " " + (abstract or ""))
    frags = [norm(f) for f in re.split(r"\.{3}|…|\[[^\]]*\]", m.group(1))]
    frags = [f for f in frags if len(f) >= 8]
    return bool(frags) and all(f in hay for f in frags)


def main():
    import glob
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    by_id = {r["rec_id"]: r for r in rows}

    t2 = {}
    n_files = 0
    for fp in sorted(glob.glob(os.path.join(T2, "tier2_*_verdict.jsonl"))):
        n_files += 1
        with open(fp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if d.get("rec_id") in by_id:
                    t2[d["rec_id"]] = d
    # nhung bai thuoc dien tang 2 (theo cot ai_kiem_tra) ma CHUA co phan quyet tang 2
    can_t2 = [r["rec_id"] for r in rows if (r.get("ai_kiem_tra") or "").startswith("can-tang-2")]
    thieu = [i for i in can_t2 if i not in t2]
    print(f"File tier2: {n_files} | phan quyet tang 2 doc duoc: {len(t2)} | "
          f"dien tang 2: {len(can_t2)} | THIEU: {len(thieu)}")
    if thieu:
        print("  vi du thieu:", thieu[:10])
        print("  => Chay not cac lo tier2 con thieu roi chay lai script nay.")

    stats = Counter()
    n_demote = 0
    disagreements = []
    for r in rows:
        v = t2.get(r["rec_id"])
        if v:
            tt = (v.get("trang_thai") or "").strip()
            if tt not in TT:
                tt = "CHUA-CHAC-CHAN"
            mc = (v.get("minh_chung") or "").strip()
            if tt != "CHUA-CHAC-CHAN" and not quote_ok(mc, r.get("title", ""),
                                                      r.get("abstract")):
                n_demote += 1
                mc += " [minh chung tang 2 khong xac minh duoc -> ha xuong chua chac]"
                tt = "CHUA-CHAC-CHAN"
            r["final_trang_thai"] = tt
            r["final_phan_loai"] = (v.get("phan_loai") or "").strip() or r.get("ai_phan_loai", "")
            r["final_R_de_xuat"] = (v.get("R_de_xuat") or "").strip()
            r["final_minh_chung"] = mc
            r["tang_duyet"] = "2"
            r["tang2_thay_doi"] = (v.get("thay_doi") or "").strip()
            # bat dong THAT SU = lat nguoc giua hai phan quyet chac chan (DUNG<->NGOAI);
            # nang cap tu CHUA-CHAC-CHAN la chuc nang binh thuong cua tang 2, khong tinh
            if {r.get("ai_trang_thai"), tt} == {"DUNG-chac-chan", "NGOAI-chac-chan"}:
                disagreements.append((r["rec_id"], r["ai_trang_thai"], tt,
                                      r.get("title", "")[:70]))
        else:
            # chi qua tang 1
            r["final_trang_thai"] = r.get("ai_trang_thai") or "CHUA-CHAC-CHAN"
            if r["final_trang_thai"] == "(chua duyet)":
                r["final_trang_thai"] = "CHUA-CHAC-CHAN"
            r["final_phan_loai"] = r.get("ai_phan_loai", "")
            r["final_R_de_xuat"] = r.get("ai_R_de_xuat", "")
            r["final_minh_chung"] = r.get("ai_minh_chung", "")
            r["tang_duyet"] = "1"
            r["tang2_thay_doi"] = ""
        stats[r["final_trang_thai"]] += 1

    assert len(rows) == 7578, f"Lech tong: {len(rows)}"
    assert all(r["final_trang_thai"] in TT for r in rows), "Con trang thai la!"

    cols = list(rows[0].keys())
    out = os.path.join(EXPORTS, "wave3_ai_final.csv")
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    # ------------------- bao cao -------------------
    c_pl = Counter(r["final_phan_loai"] for r in rows
                   if r["final_trang_thai"] == "DUNG-chac-chan")
    c_td = Counter(r["tang2_thay_doi"] for r in rows if r["tang_duyet"] == "2")
    n_t2 = sum(1 for r in rows if r["tang_duyet"] == "2")
    L = [f"# Wave 3 — Kết quả duyệt AI hai tầng ({len(rows)} bài, chạy xong {date.today()})",
         "\n## Quy trình",
         "- **Tầng 1** (model Sonnet): 51 agent đọc từng abstract theo rubric "
         "`wave3_ai_screen_rubric.md`, bắt buộc trích minh chứng nguyên văn; câu trích được "
         "đối chiếu tự động với abstract gốc, trích sai bị hạ xuống CHƯA-CHẮC-CHẮN.",
         f"- **Tầng 2** (model Opus — thay cho Fable vì tài khoản hết hạn mức Fable giữa "
         f"chừng): phán quyết lại {n_t2} bài gồm toàn bộ bài ĐÚNG, toàn bộ CHƯA-CHẮC, bài "
         "NGOÀI có tín hiệu ngược (có tên dataset/band A), và bài lỗi kỹ thuật tầng 1. "
         "Minh chứng tầng 2 cũng được đối chiếu tự động.",
         "- Bài NGOÀI rõ ràng không tranh chấp chỉ qua tầng 1 (cột `tang_duyet`=1).",
         "\n## Kết quả cuối (cột `final_trang_thai`)",
         "| Trạng thái | Số bài |", "|---|---|"]
    for k, v in stats.most_common():
        L.append(f"| {k} | {v} |")
    L.append("\n## Bài ĐÚNG mục tiêu — phân loại (`final_phan_loai`)")
    L.append("| Phân loại | Số bài |")
    L.append("|---|---|")
    for k, v in c_pl.most_common():
        L.append(f"| {k} | {v} |")
    L.append(f"\n## Tầng 2 đối chiếu tầng 1 ({n_t2} bài)")
    L.append("| thay_doi | Số bài |")
    L.append("|---|---|")
    for k, v in c_td.most_common():
        L.append(f"| {k or '(trống)'} | {v} |")
    L.append(f"- Bất đồng DUNG↔NGOAI giữa 2 tầng: **{len(disagreements)}** — 20 ví dụ đầu:")
    for rec, a, b, t in disagreements[:20]:
        L.append(f"  - `{rec}`: tầng 1 {a} → tầng 2 {b} · {t}")
    L.append(f"- Minh chứng tầng 2 không xác minh được (hạ xuống chưa chắc): {n_demote}")
    L.append("\n## Cách dùng")
    L.append("- File: `search_exports/wave3_ai_final.csv` — mỗi bài 1 dòng, cột "
             "`final_trang_thai` / `final_phan_loai` / `final_minh_chung` (trích nguyên văn "
             "trong «…») / `tang_duyet` / `tang2_thay_doi`; kèm mọi cột cũ (dataset, "
             "link_data, band, R gợi ý…).")
    L.append("- Đây vẫn là **sàng lọc mức tiêu đề+abstract có minh chứng**, không thay "
             "quyết định cuối của Vy: cột `decision_ta` vẫn để Vy điền, đặc biệt với nhóm "
             "CHƯA-CHẮC-CHẮN và các bất đồng 2 tầng liệt kê ở trên.")
    md = os.path.join(NOTES, "wave3_ai_screen_report.md")
    with open(md, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

    print("\n=== KET QUA CUOI ===")
    for k, v in stats.most_common():
        print(f"  {k:18s}: {v}")
    print(f"  Tang 2 da duyet: {n_t2} | thay doi: {dict(c_td)}")
    print(f"  Bat dong DUNG<->NGOAI: {len(disagreements)} | minh chung t2 rot: {n_demote}")
    print(f"  Xuat: {out}")
    print(f"  Bao cao: {md}")


if __name__ == "__main__":
    main()
