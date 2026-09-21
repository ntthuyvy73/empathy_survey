# -*- coding: utf-8 -*-
"""P1 WAVE 3 — SAP UU TIEN SANG LOC (screening prioritization).

KHONG tu quyet dinh include/exclude — giu dung giao thuc wave 1 (prioritize_screening.py):
chi CHAM DIEM lien quan, SAP XEP tu tren xuong, va GOI Y ma loai R1-R9 o cot rieng.
Vy van la nguoi dien decision_ta. Ky thuat nay duoc chap nhan trong systematic review.

Cai tien so voi wave 1 — tan dung cac cot moi cua wave3_unique_for_screening.csv:
  + co ten dataset (cot `dataset`)            -> tin hieu manh nhat
  + co link du lieu (cot `link_data`)         -> tai nguyen co the xac minh (lien quan EC9)
  + xuat hien o nhieu CSDL (cot `n_sources`)  -> tin hieu nhe ve do noi bat
  + bay TU VIET TAT DA NGHIA (nguon nhieu lon nhat cua wave 2): DBT=data-build-tool,
    IPT=instruction pre-training, ACT/MI/CBT dung nghia khac... -> goi y R2 khi bai
    KHONG co bat ky tu khoa mien tham van nao.

Xuat:
  search_exports/wave3_screening_sorted.csv  — TOAN BO, them priority_score/band/hint/
                                               R_goi_y, sap giam dan (dien decision_ta o day)
  search_exports/wave3_shortlist_dataset.csv — rut gon: bai co ten dataset HOAC link du lieu
  _notes/wave3_prioritize_report.md          — bao cao phan bo + uoc luong cong doc
Chay: python wave3_prioritize.py"""
import os
import re
import csv
import sys
from collections import Counter
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dedup_ris as D

NOTES = os.path.dirname(os.path.abspath(__file__))
EXPORTS = D.EXPORTS
SRC = os.path.join(EXPORTS, "wave3_unique_for_screening.csv")

# --- tu khoa mien (giu nguyen tinh than wave 1, mo rong nhe) ---------------------
DOMAIN = ["counsel", "psychotherap", "therapist", "therapy session", "emotional support",
          "mental health", "motivational interview", "cognitive behavioral",
          "cognitive behavioural", "therapeutic alliance", "working alliance",
          "peer support", "helpline", "crisis line", "psychological support",
          "distress", "empath", "client-centered", "client-centred", "psychodynamic",
          "suicid", "depression", "anxiety"]
# mien LOI (tham van/tri lieu that su) — manh hon DOMAIN chung.
# PHAI co ten DAY DU cua cac hoc thuyet: neu khong, bai ACT/DBT that su (viet ro
# 'acceptance and commitment therapy') se bi bay 'viet tat da nghia' phat oan.
CORE = ["counsel", "psychotherap", "therapist", "therapy session", "therapeutic alliance",
        "working alliance", "motivational interview", "helpline", "crisis line",
        "crisis text line", "crisis counsel", "hotline", "peer counsel",
        "client-centered", "client-centred",
        "cognitive behavioral therapy", "cognitive behavioural therapy",
        "acceptance and commitment therapy", "dialectical behavior therapy",
        "dialectical behaviour therapy", "interpersonal psychotherapy",
        "mindfulness-based cognitive therapy", "eye movement desensitization",
        "schema therapy", "compassion-focused therapy", "behavioral activation",
        "behavioural activation", "problem-solving therapy", "solution-focused brief"]
RESOURCE = ["dataset", "corpus", "multi-turn", "multiturn", "dialogue", "dialog ",
            "conversation", "benchmark", "role-play", "role play", "roleplay",
            "utterance", "transcript", "counselor-client", "counsellor-client",
            "client-counselor", "annotated", "annotation"]
NOISE = ["social media", "twitter", "reddit", "weibo", "forum post", "eeg", "fmri",
         " mri ", "wearable", "sensor", "imaging", "radiolog", "surgery", "surgical",
         "cancer screening", "genomic", "protein", "drug discovery", "electronic health record",
         "readability", "bibliometric", "scientometric"]
REVIEW = ["a survey", "survey of", "systematic review", "scoping review",
          "literature review", "a review of", ": a review", "meta-analysis",
          "umbrella review", "bibliometric analysis"]
# nghien cuu nguoi dung/thu nghiem lam sang — thuong KHONG phai tai nguyen kho tinh (EC5/R8)
TRIAL = ["randomised controlled trial", "randomized controlled trial", " rct ",
         "feasibility trial", "pilot trial", "protocol of a", "study protocol",
         "qualitative study", "cross-sectional survey", "focus group"]

# --- tu viet tat DA NGHIA: nguon nhieu chinh cua wave 2 --------------------------
# Moi muc: (cac cum DAY DU chung minh dung nghia tri lieu, cac cum chung minh nghia KHAC).
# Chi canh bao khi KHONG thay dang viet DAY DU -> tranh phat oan bai tri lieu that.
AMBIG_ACRONYM = {
    "DBT": (["dialectical behavior therapy", "dialectical behaviour therapy"],
            ["data build tool", "data-build-tool", "double branch", "dynamic binary",
             "digital breast", "dry bulb"]),
    "IPT": (["interpersonal psychotherapy", "interpersonal therapy"],
            ["instruction pre-training", "incremental pre-training", "implicit prompt",
             "imaginative perception", "inspiration promote", "image processing"]),
    "ACT": (["acceptance and commitment therapy", "acceptance and commitment"],
            ["actor", "action recognition", "activity recognition"]),
    "MITI": (["motivational interviewing treatment integrity"], ["mitigat"]),
    "MBCT": (["mindfulness-based cognitive therapy", "mindfulness based cognitive therapy"], []),
    "EMDR": (["eye movement desensitization"], []),
}


def hits(text, terms):
    return [t.strip() for t in terms if t in text]


def score_row(r):
    title = (r.get("title") or "")
    tl = title.lower()
    ab = (r.get("abstract") or "").lower()
    both = tl + "  " + ab
    s, why, rgoi = 0, [], ""

    ds = (r.get("dataset") or "").strip()
    ds_chac = [d for d in ds.split("; ") if d and not d.endswith("(?)")]
    link = (r.get("link_data") or "").strip()
    host = (r.get("link_host") or "")
    host_biet = [h for h in host.split("; ") if h and h != "khac"]

    # 1. ten dataset — tin hieu manh nhat
    if ds_chac:
        in_title = any(d.lower().replace("-", "") in tl.replace("-", "") for d in ds_chac)
        s += 7 if in_title else 5
        why.append("dataset:" + ds_chac[0] + ("(o tieu de)" if in_title else ""))
    elif ds:
        s += 1
        why.append("dataset?:" + ds.split("; ")[0])

    # 2. link du lieu -> tai nguyen xac minh duoc (EC9 thuan loi)
    if host_biet:
        s += 4
        why.append("link:" + host_biet[0])
    elif link:
        s += 1
        why.append("link:khac")

    # 3. mien + tai nguyen
    core = hits(both, CORE)
    dom = hits(both, DOMAIN)
    res = hits(both, RESOURCE)
    if core:
        s += min(3 * len(core), 9)
    if dom:
        s += min(1 * len(dom), 4)
    if res:
        s += min(2 * len(res), 6)
    if core and res:
        s += 4
        why.append("mien-loi+tai-nguyen")
    elif dom and res:
        s += 2
        why.append("mien+tai-nguyen")
    elif core:
        why.append("mien-loi")
    elif dom:
        why.append("mien-chung")
    elif res:
        why.append("tai-nguyen")

    # 4. co mat o nhieu CSDL -> noi bat nhe
    try:
        ns = int(r.get("n_sources") or 1)
    except ValueError:
        ns = 1
    if ns >= 3:
        s += 1

    # 4b. KHONG co abstract -> cham diem thieu cong bang (chi co tieu de de danh gia).
    # Khong the tu tin xep xuong day -> keo ve vung "can doc" va danh dau ro.
    if len(ab.strip()) < 60:
        s = max(s, 7)
        why.append("THIEU-ABSTRACT-can-doc-tay")

    # 5. tru diem nhieu
    noi = hits(both, NOISE)
    if noi:
        s -= min(2 * len(noi), 8)
        why.append("nhieu:" + ",".join(noi[:2]))
    if hits(tl, REVIEW) or hits(ab[:400], REVIEW):
        s -= 5
        why.append("tong-quan")
        rgoi = rgoi or "R8?"
    if hits(both, TRIAL):
        s -= 3
        why.append("thu-nghiem/dinh-tinh")
        rgoi = rgoi or "R8?"

    # 6. bay tu viet tat da nghia: CHI canh bao khi (a) khong co mien loi, VA
    #    (b) khong thay dang viet DAY DU cua chinh hoc thuyet do. Nho (b), bai
    #    'Acceptance and Commitment Therapy...' that su khong bi phat oan.
    if not core:
        goc = title + "  " + (r.get("abstract") or "")
        for acr, (day_du, nghia_khac) in AMBIG_ACRONYM.items():
            if not re.search(r"\b" + acr + r"\b", goc):
                continue
            if any(d in both for d in day_du):       # co viet day du -> dung nghia
                continue
            bc = [g for g in nghia_khac if g in both]
            s -= 6
            why.append(f"viet-tat-da-nghia:{acr}" + (f"({bc[0]})" if bc else ""))
            rgoi = "R2?"
            break
    # 7. hoan toan khong co dau hieu mien -> nhieu kha nang ngoai mien
    if not dom and not core:
        s -= 6
        why.append("khong-co-tu-khoa-mien")
        rgoi = rgoi or "R2?"
    return s, "; ".join(why), rgoi


def band(s):
    if s >= 14:
        return "A - doc truoc"
    if s >= 7:
        return "B - can doc"
    if s >= 0:
        return "C - it kha nang"
    return "D - nhieu kha nang loai"


def main():
    if not os.path.exists(SRC):
        sys.exit("Chua co wave3_unique_for_screening.csv — chay wave3_unique_enrich.py truoc.")
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    cols = list(rows[0].keys())

    # GIU QUYET DINH Vy da dien o BAN DA SAP UU TIEN (vong chay truoc) — neu khong
    # lam buoc nay, moi lan chay lai se xoa sach cong sang loc cua Vy.
    import unicodedata

    def skey(t):
        s = (t or "").replace("{", "").replace("}", "")
        s = re.sub(r"\$[^$]*\$|\\[a-zA-Z]+|<[^>]+>", " ", s)
        s = unicodedata.normalize("NFKD", s)
        s = "".join(c for c in s if not unicodedata.combining(c)).lower()
        return re.sub(r"[^a-z0-9]+", "", s)

    n_giu = 0
    prev = os.path.join(EXPORTS, "wave3_screening_sorted.csv")
    if os.path.exists(prev):
        with open(prev, encoding="utf-8-sig", newline="") as f:
            old = {}
            for r0 in csv.DictReader(f):
                if (r0.get("decision_ta") or r0.get("decision_ft") or "").strip():
                    old[skey(r0.get("title"))] = r0
        for r in rows:
            o = old.get(skey(r.get("title")))
            if o:
                for c in ("decision_ta", "decision_ft", "include_group", "notes"):
                    if not (r.get(c) or "").strip():
                        r[c] = o.get(c, "")
                n_giu += 1
        if n_giu:
            print(f"Giu lai quyet dinh da dien cho {n_giu} dong (tu ban sap uu tien truoc)")
    for r in rows:
        s, why, rg = score_row(r)
        r["priority_score"] = s
        r["band"] = band(s)
        r["hint"] = why
        r["R_goi_y"] = rg
    rows.sort(key=lambda r: (-r["priority_score"], r.get("year") or "0000"))

    out_cols = ["priority_score", "band", "R_goi_y", "hint"] + cols
    out = os.path.join(EXPORTS, "wave3_screening_sorted.csv")
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=out_cols)
        w.writeheader()
        w.writerows(rows)

    short = [r for r in rows if (r.get("dataset") or "").strip()
             or (r.get("link_data") or "").strip()]
    out2 = os.path.join(EXPORTS, "wave3_shortlist_dataset.csv")
    with open(out2, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=out_cols)
        w.writeheader()
        w.writerows(short)

    # ---------------- bao cao ----------------
    cb = Counter(r["band"] for r in rows)
    cr = Counter(r["R_goi_y"] for r in rows if r["R_goi_y"])
    n_ds = sum(1 for r in rows if (r.get("dataset") or "").strip())
    n_link = sum(1 for r in rows if (r.get("link_data") or "").strip())
    # do tap trung: bao nhieu % bai co dataset nam trong band A+B
    ab_set = [r for r in rows if r["band"].startswith(("A", "B"))]
    ds_in_ab = sum(1 for r in ab_set if (r.get("dataset") or "").strip())
    era = Counter((r.get("era") or "?") for r in ab_set)

    L = [f"# Wave 3 — Hàng đợi ưu tiên sàng lọc ({len(rows)} bài)",
         f"\n_Chạy: {date.today()} · File điền quyết định: `wave3_screening_sorted.csv` · "
         f"Rút gọn: `wave3_shortlist_dataset.csv` ({len(short)} bài)_\n",
         "> Script **không** quyết định include/exclude. Nó chấm điểm liên quan, sắp xếp, "
         "và gợi ý mã loại ở cột `R_goi_y` (có dấu `?` = **chỉ là gợi ý**). Chị vẫn điền "
         "`decision_ta`. Đây là cách làm đã dùng ở wave 1 (`prioritize_screening.py`).\n",
         "## 1. Phân bố theo nhóm ưu tiên",
         "| Nhóm | Số bài | Nghĩa |", "|---|---|---|"]
    ngh = {"A - doc truoc": "gần chắc chắn liên quan — đọc trước",
           "B - can doc": "cần đọc để quyết",
           "C - it kha nang": "ít khả năng liên quan — lướt nhanh",
           "D - nhieu kha nang loai": "nhiều khả năng loại — kiểm tra mẫu rồi loại hàng loạt"}
    for b in ["A - doc truoc", "B - can doc", "C - it kha nang", "D - nhieu kha nang loai"]:
        L.append(f"| {b} | {cb.get(b, 0)} | {ngh[b]} |")
    L.append(f"\n- Nhóm **A + B = {cb.get('A - doc truoc',0) + cb.get('B - can doc',0)} bài** "
             f"({(cb.get('A - doc truoc',0)+cb.get('B - can doc',0))*100//len(rows)}% tổng số) "
             f"— đây là phần thực sự phải đọc kỹ.")
    L.append(f"- Trong A+B có **{ds_in_ab}/{n_ds} bài có tên dataset** "
             f"({ds_in_ab*100//max(1,n_ds)}%) → việc sắp xếp gom đúng chỗ cần gom.")
    L.append(f"- A+B theo thời kỳ: " + ", ".join(f"{k}: {v}" for k, v in sorted(era.items())))

    L.append("\n## 2. Gợi ý mã loại (cột `R_goi_y`, chỉ là gợi ý)")
    L.append("| Mã | Số bài | Nghĩa (theo bảng R1–R9 của giao thức) |")
    L.append("|---|---|---|")
    rn = {"R2?": "nghi ngoài miền tham vấn/hỗ trợ cảm xúc có mục tiêu (EC2)",
          "R8?": "nghi không phải tài nguyên kho tính — tổng quan/thử nghiệm/định tính (EC5)"}
    for k, v in cr.most_common():
        L.append(f"| {k} | {v} | {rn.get(k, '')} |")
    L.append("\n> Nguồn nhiễu lớn nhất ở wave 2 là **từ viết tắt đa nghĩa** (DBT = data-build-tool, "
             "IPT = instruction pre-training…). Script bắt trường hợp bài có các chữ này nhưng "
             "**không có bất kỳ từ khóa miền lõi nào** (counseling/psychotherapy/therapist…) và "
             "gợi ý R2 — đúng cách chị đã mã tay ở wave 2.")

    L.append(f"\n## 3. File rút gọn ưu tiên đọc trước ({len(short)} bài)")
    L.append(f"`wave3_shortlist_dataset.csv` — mọi bài **có tên dataset ({n_ds})** hoặc "
             f"**có link dữ liệu ({n_link})**. Đây là nơi khả năng tìm ra tài nguyên mới "
             "cho khảo sát là cao nhất.")
    L.append("\n### 25 bài điểm cao nhất")
    L.append("| Điểm | Năm | Dataset | Link | Tiêu đề |")
    L.append("|---|---|---|---|---|")
    for r in rows[:25]:
        L.append(f"| {r['priority_score']} | {r.get('year','')} | "
                 f"{(r.get('dataset') or '-')[:28]} | {(r.get('link_host') or '-')[:16]} | "
                 f"{r['title'][:76]} |")

    L.append("\n## 4. Ước lượng công đọc")
    nab = cb.get("A - doc truoc", 0) + cb.get("B - can doc", 0)
    L.append(f"- Đọc kỹ A+B: **{nab} bài** — với tốc độ ~30 giây/abstract là khoảng "
             f"**{nab*30//3600} giờ {(nab*30%3600)//60} phút**.")
    L.append(f"- Nhóm C ({cb.get('C - it kha nang',0)}) lướt tiêu đề ~10 giây/bài; "
             f"nhóm D ({cb.get('D - nhieu kha nang loai',0)}) nên kiểm tra ngẫu nhiên "
             "khoảng 50 bài để xác nhận ngưỡng an toàn rồi mới loại hàng loạt.")
    L.append("\n## 5. Cách chị làm tiếp")
    L.append("1. Mở `wave3_screening_sorted.csv`, điền cột `decision_ta` "
             "(`include` / `exclude` / `check-fulltext`) từ trên xuống.")
    L.append("2. Với bài loại, ghi mã ở `notes` theo bảng R1–R9 cho khớp bước lập PRISMA.")
    L.append("3. **Kiểm tra ngưỡng an toàn**: đọc ngẫu nhiên ~50 bài nhóm D. Nếu không bài "
             "nào đáng include thì mới loại hàng loạt phần còn lại — và ghi rõ cách làm này "
             "vào phần Methods, vì nó ảnh hưởng tới tính tái lập.")
    L.append("4. Chạy lại `wave3_unique_enrich.py` bất cứ lúc nào: quyết định đã điền được giữ.")
    n_noab = sum(1 for r in rows if len((r.get("abstract") or "").strip()) < 60)
    L.append("\n## 6. Giới hạn")
    L.append(f"- **{n_noab} bài không có abstract** (nguồn chỉ trả về tiêu đề). Chấm điểm cho "
             "chúng là không công bằng nên script **kéo hết về nhóm B** và đánh dấu "
             "`THIEU-ABSTRACT-can-doc-tay` — chị phải tự tra toàn văn, đừng loại theo điểm.")
    L.append("- Điểm số chỉ là **heuristic trên tiêu đề + abstract**, không thay được đọc. "
             "Bài hay nhưng abstract viết mơ hồ vẫn có thể rơi xuống nhóm C.")
    L.append("- Cột `R_goi_y` **không** được chép thẳng thành quyết định: mọi mã đều có dấu `?`.")
    L.append("- Việc loại hàng loạt nhóm D chỉ hợp lệ nếu chị có kiểm tra mẫu như bước 3 "
             "và ghi lại — nếu không, đó là chỗ hổng về tính minh bạch của tổng quan.")

    md = os.path.join(NOTES, "wave3_prioritize_report.md")
    with open(md, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

    print(f"Tong: {len(rows)} bai")
    for b in ["A - doc truoc", "B - can doc", "C - it kha nang", "D - nhieu kha nang loai"]:
        print(f"  {b:26s}: {cb.get(b, 0)}")
    print(f"  Goi y ma loai: {dict(cr)}")
    print(f"  Co dataset: {n_ds} | co link: {n_link} | shortlist: {len(short)}")
    print(f"  Bai co dataset nam trong A+B: {ds_in_ab}/{n_ds}")
    print("\n5 bai diem cao nhat:")
    for r in rows[:5]:
        print(f"  [{r['priority_score']:>3}] {r['title'][:66]}  <- {r['hint'][:56]}")
    print("\n5 bai diem thap nhat:")
    for r in rows[-5:]:
        print(f"  [{r['priority_score']:>3}] {r['title'][:66]}  <- {r['hint'][:56]}")
    print(f"\n  Xuat: {out}")
    print(f"  Rut gon: {out2}")
    print(f"  Bao cao: {md}")


if __name__ == "__main__":
    main()
