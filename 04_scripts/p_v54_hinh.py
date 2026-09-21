# -*- coding: utf-8 -*-
"""
p_v54_hinh.py — Bộ 7 hình cho bài v54 (đánh số theo thứ tự trích dẫn):
  H1_lich_su_ly_thuyet.png      — tái dùng hình v48 (đã chép sẵn, script không vẽ lại)
  H2_ban_do_phan_tang.png       — bản đồ phạm vi -> nhánh -> tầng neo
  H3_cay_hinh_thai.png          — CÂY hình thái văn bản (thuần/phân vai/kết hợp)   [MỚI]
  H4_timeline_nguon_goc.png     — timeline ba thời kỳ × nguồn gốc
  H5_matran_tiepcan_nhanh.png   — ma trận tiếp cận × nhánh
  H6_cay_truc_ly_thuyet.png     — CÂY trục lý thuyết: tầng -> dòng -> hệ đo + ví dụ [MỚI]
  H7_tai_su_dung.png            — tái sử dụng theo vai trò bài
Palette Okabe–Ito; "không rõ" xám + vân; Times New Roman; 300 dpi.
"""
import csv, json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, FancyBboxPatch

BASE = Path(r'H:\Vy\Paper\Empathy\Report\_Chuan_bi\_analyst_v7\wave3_nlp_tham_van')
S = json.load(open(BASE / '05_bai_bao' / 'so_lieu_v53.json', encoding='utf-8'))
HINH = BASE / '05_bai_bao' / 'hinh'

plt.rcParams.update({
    'font.family': 'Times New Roman', 'font.size': 10.5,
    'axes.edgecolor': '#888888', 'axes.linewidth': 0.8,
    'savefig.dpi': 300, 'savefig.bbox': 'tight', 'savefig.facecolor': 'white',
})

MAU_NGUON = {'hoi-thoai-that': '#0072B2', 'dong-vai': '#E69F00', 'MXH-dien-dan': '#009E73',
             'tong-hop-LLM': '#D55E00', 'hon-hop': '#CC79A7', 'khong-ro': '#C9C9C9'}
TEN_NGUON = {'hoi-thoai-that': 'Hội thoại thật', 'dong-vai': 'Đóng vai',
             'MXH-dien-dan': 'MXH/diễn đàn', 'tong-hop-LLM': 'Tổng hợp bằng LLM',
             'hon-hop': 'Hỗn hợp', 'khong-ro': 'Không rõ (tóm tắt không nêu)'}
TT_NGUON = ['hoi-thoai-that', 'dong-vai', 'MXH-dien-dan', 'hon-hop', 'tong-hop-LLM', 'khong-ro']
TEN_NHANH = {'ESC': 'Hỗ trợ cảm xúc (ESC)', 'dong-dang': 'Đồng đẳng', 'tham-van': 'Tham vấn',
             'tri-lieu': 'Trị liệu', 'khung-hoang': 'Khủng hoảng',
             'sang-loc-lam-sang': 'Sàng lọc lâm sàng', 'chan-doan': 'Chẩn đoán',
             'dao-tao-ky-nang': 'Đào tạo kỹ năng', 'khac': 'Khác'}

def pvn(x):  # 90.6 -> '90,6'
    return str(x).replace('.', ',')

def seg_bar(ax, y, vals, colors, hatches=None, h=0.62):
    x = 0
    for i, (v, c) in enumerate(zip(vals, colors)):
        if v <= 0:
            continue
        ht = hatches[i] if hatches else None
        ax.barh(y, v, left=x, height=h, color=c, edgecolor='white',
                linewidth=1.2, hatch=ht, zorder=3)
        x += v
    return x

# ---------- khối vẽ hộp + nối cho hai hình cây ----------
def hop(ax, x, y, w, h, text, fc, ec, fs=9.6, bold_first=True, dashed=False, lw=1.1):
    box = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.008,rounding_size=0.012',
                         facecolor=fc, edgecolor=ec, linewidth=lw,
                         linestyle=(0, (4, 2.5)) if dashed else 'solid', zorder=3)
    ax.add_patch(box)
    dong = text.split('\n')
    n = len(dong)
    for i, t in enumerate(dong):
        yy = y + h * (1 - (i + 0.62) / (n + 0.15))
        ax.text(x + 0.012, yy, t, fontsize=fs if i == 0 else fs - 1.1,
                fontweight='bold' if (i == 0 and bold_first) else 'normal',
                va='center', ha='left', color='#1a1a1a', zorder=4)
    return (x, y, w, h)

def noi(ax, b1, b2, color='#8A8A8A', lw=1.1):
    """Nối khuỷu từ cạnh phải hộp b1 sang cạnh trái hộp b2."""
    x1 = b1[0] + b1[2]; y1 = b1[1] + b1[3] / 2
    x2 = b2[0];          y2 = b2[1] + b2[3] / 2
    xm = (x1 + x2) / 2
    ax.plot([x1, xm, xm, x2], [y1, y1, y2, y2], color=color, lw=lw, zorder=2,
            solid_capstyle='round')

# ============================================================
# H2 — BẢN ĐỒ PHÂN TẦNG (giữ thiết kế cũ, tên file mới)
# ============================================================
def ve_H2():
    khoi = [('Hỗ trợ cảm xúc – đồng đẳng (ES)', ['ESC', 'dong-dang']),
            ('Tham vấn (CO)', ['tham-van']),
            ('Trị liệu (PT)', ['tri-lieu']),
            ('Chức năng bổ trợ quanh liệu trình (BT)',
             ['khung-hoang', 'sang-loc-lam-sang', 'chan-doan', 'dao-tao-ky-nang', 'khac'])]
    pv = {'Hỗ trợ cảm xúc – đồng đẳng (ES)': 'ES', 'Tham vấn (CO)': 'CO',
          'Trị liệu (PT)': 'PT', 'Chức năng bổ trợ quanh liệu trình (BT)': 'BT'}
    fig, ax = plt.subplots(figsize=(9.6, 6.6))
    y = 0; yticks = []; ylabels = []
    mau = ['#0072B2', '#E69F00', '#C9C9C9']; hatch = [None, None, '///']
    for ten_khoi, ds in khoi:
        n_pv = S['pham_vi'][pv[ten_khoi]]
        ax.text(-8, y, f'{ten_khoi} — {n_pv["n"]} bộ ({pvn(n_pv["pct"])}%)',
                ha='left', va='center', fontsize=11, fontweight='bold', color='#222222')
        y -= 1
        for nh in ds:
            d = S['nhanh'][nh]
            khong = d['n'] - d['T_a'] - d['T_b_thuan']
            seg_bar(ax, y, [d['T_a'], d['T_b_thuan'], khong], mau, hatch)
            ax.text(d['n'] + 4, y, f"{d['n']} bộ · neo {d['pct_co_neo']:.0f}%",
                    va='center', fontsize=9.5, color='#333333')
            yticks.append(y); ylabels.append(TEN_NHANH[nh]); y -= 1
        y -= 0.55
    ax.set_yticks(yticks); ax.set_yticklabels(ylabels, fontsize=10.5)
    ax.set_xlim(0, 340); ax.set_ylim(y + 0.2, 0.8)
    ax.set_xlabel('Số bộ dữ liệu', fontsize=10.5)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.xaxis.grid(True, color='#DDDDDD', linewidth=0.6, zorder=0); ax.set_axisbelow(True)
    leg = [Patch(facecolor='#0072B2', edgecolor='white', label='Neo học thuyết trị liệu (tầng T-a)'),
           Patch(facecolor='#E69F00', edgecolor='white', label='Chỉ neo khung quá trình/chiến lược (tầng T-b)'),
           Patch(facecolor='#C9C9C9', edgecolor='white', hatch='///', label='Không khai báo tiếp cận')]
    ax.legend(handles=leg, loc='lower right', frameon=False, fontsize=9.5,
              bbox_to_anchor=(1.0, -0.02))
    fig.savefig(HINH / 'H2_ban_do_phan_tang.png'); plt.close(fig)

# ============================================================
# H3 — CÂY HÌNH THÁI VĂN BẢN (MỚI)
# ============================================================
def ve_H3():
    c = S['cay_hinh_thai']; tt = c['text_thuan']; kh = c['ket_hop']
    n_main = S['toan_canh']['ban_do_chinh']
    fig, ax = plt.subplots(figsize=(10.8, 6.4))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    XANH_N, XANH_V = '#DCEAF6', '#0072B2'
    CAM_N, CAM_V = '#FCEFD9', '#B97E00'
    XAM_N, XAM_V = '#F0F0F0', '#8A8A8A'

    goc = hop(ax, 0.005, 0.44, 0.205, 0.15,
              f'Bộ dữ liệu chứa văn bản\nbản đồ chính · {n_main:,} bộ'.replace(',', '.'),
              '#FFFFFF', '#444444', fs=10.4)
    thuan = hop(ax, 0.285, 0.60, 0.215, 0.13,
                f'Văn bản thuần\n{tt["n"]} bộ · {pvn(round(100*tt["n"]/n_main,1))}% bản đồ',
                XANH_N, XANH_V, fs=10.2)
    kethop = hop(ax, 0.285, 0.16, 0.215, 0.13,
                 f'Văn bản kết hợp\n{kh["n"]} bộ · {pvn(round(100*kh["n"]/n_main,1))}% bản đồ',
                 CAM_N, CAM_V, fs=10.2)
    noi(ax, goc, thuan); noi(ax, goc, kethop)

    la1 = hop(ax, 0.575, 0.80, 0.415, 0.155,
              f'Hội thoại đa lượt, phân vai hai bên\n{tt["da_luot"]} bộ · {pvn(round(100*tt["da_luot"]/tt["n"],1))}% nhóm thuần\nví dụ: ESConv, AnnoMI, EmpatheticDialogues',
              XANH_N, XANH_V, fs=9.8)
    la2 = hop(ax, 0.575, 0.60, 0.415, 0.155,
              f'Cặp hỏi–đáp đơn lượt (hai vai, một lượt mỗi bên)\n{tt["don_luot"]} bộ · {pvn(round(100*tt["don_luot"]/tt["n"],1))}% nhóm thuần\nví dụ: CounselChat, MentalChat16K',
              XANH_N, XANH_V, fs=9.8)
    la3 = hop(ax, 0.575, 0.455, 0.415, 0.10,
              f'Không rõ cấu trúc lượt từ tóm tắt\n{tt["khong_ro"]} bộ · {pvn(round(100*tt["khong_ro"]/tt["n"],1))}% nhóm thuần',
              XAM_N, XAM_V, fs=9.8)
    for la in (la1, la2, la3):
        noi(ax, thuan, la, color=XANH_V)

    th = kh['to_hop']
    ys = [0.345, 0.270, 0.195, 0.120]
    texts = [f'+ tiếng nói · {th["text+voice"]} bộ',
             f'+ tiếng nói + video · {th["text+voice+video"]} bộ',
             f'+ hình ảnh · {th["text+hinh-anh"]} bộ  ·  + video · {th["text+video"]} bộ',
             f'+ tiếng nói + hình ảnh · {th["text+voice+hinh-anh"]} bộ']
    for yc, text in zip(ys, texts):
        la = hop(ax, 0.575, yc - 0.031, 0.33, 0.062, text, CAM_N, CAM_V,
                 fs=9.6, bold_first=False)
        noi(ax, kethop, la, color=CAM_V)
    ax.text(0.575, 0.062, f'{kh["da_luot"]}/{kh["n"]} bộ kết hợp là hội thoại đa lượt — '
            'gốc phiên ghi âm/ghi hình được chuyển văn bản.',
            fontsize=9.0, color='#555555')
    ax.text(0.005, 0.018, 'Nhóm đối chiếu ngoài bản đồ chính: 103 bộ bài đăng mạng xã hội — '
            'văn bản không phân vai hội thoại (mục 4.6).', fontsize=9.0, color='#555555',
            style='italic')
    fig.savefig(HINH / 'H3_cay_hinh_thai.png'); plt.close(fig)

# ============================================================
# H4 — TIMELINE (giữ thiết kế, tên mới)
# ============================================================
def ve_H4():
    with open(BASE / '05_bai_bao' / 'danh_muc_v50_loc.csv', encoding='utf-8-sig') as f:
        cat = [d for d in csv.DictReader(f) if d['nhom_mien'] != 'MXH-thong-ke']
    for d in cat:
        d['nam'] = int(d['nam_som_nhat'])
    nams = list(range(1999, 2027))
    fig, ax = plt.subplots(figsize=(10.2, 4.6))
    bottom = {n: 0 for n in nams}
    for g in TT_NGUON:
        vals = [sum(1 for d in cat if d['nam'] == n and d['nguon_du_lieu'] == g) for n in nams]
        ax.bar(nams, vals, bottom=[bottom[n] for n in nams], width=0.78,
               color=MAU_NGUON[g], edgecolor='white', linewidth=0.7,
               hatch='///' if g == 'khong-ro' else None, label=TEN_NGUON[g], zorder=3)
        for n, v in zip(nams, vals):
            bottom[n] += v
    for x in (2017.5, 2022.5):
        ax.axvline(x, color='#555555', linewidth=0.9, linestyle=(0, (4, 3)), zorder=4)
    tk = S['thoi_ky']
    ax.text(2012.5, 278, f'Tiền-PLM (<2018) — {tk["tien-PLM"]} bộ · 4,2%', ha='center',
            fontsize=9.5, color='#333333')
    ax.text(2020.0, 278, f'PLM (2018–2022)\n{tk["PLM"]} bộ · 19,8%', ha='center',
            fontsize=9.5, color='#333333')
    ax.text(2024.6, 278, f'LLM (2023–giữa 2026)\n{tk["LLM"]} bộ · 76,0%', ha='center',
            fontsize=9.5, color='#333333')
    ax.set_xlim(1998.2, 2026.8); ax.set_ylim(0, 300)
    ax.set_xticks([1999, 2004, 2010, 2015, 2018, 2021, 2024, 2026])
    ax.set_ylabel('Số bộ dữ liệu mới theo năm xuất hiện sớm nhất', fontsize=10)
    ax.spines[['top', 'right']].set_visible(False)
    ax.yaxis.grid(True, color='#DDDDDD', linewidth=0.6, zorder=0); ax.set_axisbelow(True)
    ax.legend(loc='center left', bbox_to_anchor=(0.015, 0.52), frameon=False, fontsize=9)
    fig.savefig(HINH / 'H4_timeline_nguon_goc.png'); plt.close(fig)

# ============================================================
# H5 — MA TRẬN (giữ thiết kế, tên mới)
# ============================================================
TEN_NHAN = {'ESC': 'Chiến lược hỗ trợ cảm xúc (ESC)', 'MI': 'Phỏng vấn tạo động lực (MI)',
            'Helping Skills': 'Helping Skills (Hill)', 'CBT': 'CBT',
            'tam-dong-hoc': 'Tâm động học', 'than-chu-trong-tam': 'Thân chủ trọng tâm',
            'chanh-niem': 'Chánh niệm', 'ACT': 'ACT', 'schema': 'Schema therapy',
            'SFBT': 'SFBT', 'DBT': 'DBT', 'EFT': 'EFT'}
def ve_H5():
    import numpy as np
    m = S['matran_nhan_nhanh']
    hang = ['ESC', 'MI', 'Helping Skills', 'CBT', 'tam-dong-hoc', 'than-chu-trong-tam',
            'chanh-niem', 'ACT', 'schema', 'SFBT', 'DBT', 'EFT']
    cot = ['ESC', 'dong-dang', 'tham-van', 'tri-lieu', 'khung-hoang',
           'sang-loc-lam-sang', 'chan-doan', 'dao-tao-ky-nang', 'khac']
    M = np.array([[m[r].get(c, 0) for c in cot] for r in hang], dtype=float)
    fig, ax = plt.subplots(figsize=(9.6, 5.6))
    im = ax.imshow(np.ma.masked_where(M == 0, M), cmap='Blues', vmin=0, vmax=60, aspect='auto')
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = int(M[i, j])
            if v:
                ax.text(j, i, str(v), ha='center', va='center', fontsize=9.5,
                        color='white' if v >= 40 else '#1a1a1a')
    ax.set_xticks(range(len(cot)))
    ax.set_xticklabels([TEN_NHANH[c].replace('Hỗ trợ cảm xúc (ESC)', 'ESC') for c in cot],
                       rotation=28, ha='right', fontsize=9.5)
    ax.set_yticks(range(len(hang)))
    ax.set_yticklabels([TEN_NHAN[r] for r in hang], fontsize=10)
    ax.axhline(2.5, color='#555555', linewidth=0.9)
    ax.text(8.45, -0.72, 'Tầng T-b', fontsize=9.5, fontweight='bold', color='#222222', ha='right')
    ax.text(8.45, 2.82, 'Tầng T-a', fontsize=9.5, fontweight='bold', color='#222222', ha='right')
    for e in ('top', 'right', 'left', 'bottom'):
        ax.spines[e].set_visible(False)
    ax.set_xticks([x - 0.5 for x in range(1, len(cot))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(hang))], minor=True)
    ax.grid(which='minor', color='white', linewidth=1.4)
    ax.tick_params(which='both', length=0)
    cb = fig.colorbar(im, ax=ax, shrink=0.72, pad=0.015)
    cb.set_label('Số bộ dữ liệu', fontsize=9.5); cb.outline.set_visible(False)
    fig.savefig(HINH / 'H5_matran_tiepcan_nhanh.png'); plt.close(fig)

# ============================================================
# H6 — CÂY TRỤC LÝ THUYẾT (MỚI)
# ============================================================
def ve_H6():
    nsn = S['nguon_theo_nhan']; NEO = S['neo']
    fig, ax = plt.subplots(figsize=(11.4, 9.6))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    XANH_N, XANH_V = '#DCEAF6', '#0072B2'
    CAM_N, CAM_V = '#FCEFD9', '#B97E00'
    XAM_N, XAM_V = '#F0F0F0', '#8A8A8A'
    DO_V = '#C24A00'

    goc = hop(ax, 0.003, 0.50, 0.155, 0.10, 'Bản đồ chính\n1.043 bộ dữ liệu văn bản',
              '#FFFFFF', '#444444', fs=10.2)
    tb = hop(ax, 0.215, 0.80, 0.215, 0.095,
             f'Tầng T-b — khung quá trình\n{NEO["T_b_bo"]} bộ · {pvn(NEO["T_b_pct_ban_do"])}% bản đồ',
             CAM_N, CAM_V, fs=10.0)
    ta = hop(ax, 0.215, 0.40, 0.215, 0.095,
             f'Tầng T-a — học thuyết trị liệu\n{NEO["T_a_bo"]} bộ · {pvn(NEO["T_a_pct_ban_do"])}% bản đồ',
             XANH_N, XANH_V, fs=10.0)
    kn = hop(ax, 0.215, 0.06, 0.215, 0.115,
             f'Không khai báo tiếp cận\n{NEO["so_bo_khong_neo"]} bộ · {pvn(NEO["pct_khong_neo"])}%\nđọc: thiếu minh bạch,\nkhông hẳn phi lý thuyết',
             XAM_N, XAM_V, fs=10.0)
    for b in (tb, ta, kn):
        noi(ax, goc, b)
    ax.text(0.218, 0.775, f'({NEO["ca_hai_tang"]} bộ mang nhãn ở cả hai tầng)',
            fontsize=8.8, color='#555555')

    MAXN = 150.0
    def la(yc, dong1, nh, dong2, mau_n, mau_v, tag=''):
        d = nsn[nh]
        h = 0.068
        # dòng trắng cuối giữ chỗ cho thanh tỷ lệ, tránh thanh chạm chân chữ
        b = hop(ax, 0.51, yc - h / 2, 0.478, h, f'{dong1} · {d["n"]} bộ\n{dong2}\n ',
                mau_n, mau_v, fs=9.7)
        ax.plot([0.516, 0.516 + 0.455 * d['n'] / MAXN],
                [yc - h / 2 + 0.007] * 2, color=mau_v, lw=2.6,
                solid_capstyle='round', zorder=5)
        if tag:
            ax.text(0.982, yc + h / 2 - 0.012, tag, fontsize=8.7, color=DO_V,
                    ha='right', style='italic', zorder=6)
        return b

    noi(ax, tb, la(0.948, 'Chiến lược hỗ trợ cảm xúc (ESC)', 'ESC',
        'hệ mã: họ chiến lược ESC [văn bản] — ví dụ: ESConv, EmpatheticDialogues',
        CAM_N, CAM_V), color=CAM_V)
    noi(ax, tb, la(0.862, 'Phỏng vấn tạo động lực (MI)', 'MI',
        'hệ mã: MISC/MITI [văn bản] — ví dụ: AnnoMI, BiMISC, KMI, PhaseMI',
        CAM_N, CAM_V), color=CAM_V)
    noi(ax, tb, la(0.776, 'Helping Skills (Hill)', 'Helping Skills',
        'hệ mã Hill [văn bản] — đi vào NLP qua biến thể chiến lược ESC',
        CAM_N, CAM_V, tag='0 phiên thật'), color=CAM_V)

    cfg = [
        ('CBT', 'CBT', 'hệ mã: CTRS [văn bản] — ví dụ: Cactus (lọc CTRS), DiaCBT (khái niệm hóa ca)', ''),
        ('Tâm động học', 'tam-dong-hoc', 'CPPS [cần quan sát viên] — mới có bài phân tích phiên (AutoPsyC)', ''),
        ('Thân chủ trọng tâm', 'than-chu-trong-tam', 'thang thấu cảm [cần quan sát viên]', ''),
        ('Chánh niệm', 'chanh-niem', 'MBI:TAC [ngoài văn bản]', ''),
        ('ACT', 'ACT', 'ACT-FM [ngoài văn bản]', '0 phiên thật'),
        ('Schema therapy', 'schema', 'chưa có hệ đo trong danh mục tham chiếu', ''),
        ('SFBT', 'SFBT', 'chưa có hệ đo trong danh mục tham chiếu', ''),
        ('DBT', 'DBT', 'DBT-ACS [ngoài văn bản]', '0 phiên thật'),
        ('EFT', 'EFT', 'chưa có hệ đo trong danh mục tham chiếu', '0 phiên thật'),
    ]
    y0 = 0.70
    for i, (ten, nh, hm, tag) in enumerate(cfg):
        noi(ax, ta, la(y0 - 0.0755 * i, ten, nh, hm, XANH_N, XANH_V, tag=tag), color=XANH_V)

    hop(ax, 0.51, 0.004, 0.478, 0.052,
        'Chưa có bộ nào trong phạm vi truy vấn: IPT · MBCT · EMDR · Gestalt · hệ thống/gia đình\n'
        '(hệ đo CSPRS, MBI:TAC, EFRS đều cần quan sát viên hoặc tín hiệu ngoài văn bản)',
        '#FFFFFF', DO_V, fs=9.2, bold_first=False, dashed=True)
    fig.text(0.5, 0.048, 'Thanh màu trong mỗi ô: độ dài tỷ lệ số bộ mang nhãn (một bộ có thể mang nhiều nhãn).',
             ha='center', fontsize=9.0, color='#555555')
    fig.savefig(HINH / 'H6_cay_truc_ly_thuyet.png'); plt.close(fig)

# ============================================================
# H7 — TÁI SỬ DỤNG (giữ thiết kế, tên mới)
# ============================================================
def ve_H7():
    top = S['top_tai_su_dung']
    vai = [('gt', 'Giới thiệu', '#0072B2'), ('dg', 'Đánh giá benchmark', '#009E73'),
           ('pt', 'Phát triển/mở rộng', '#E69F00'), ('sd', 'Sử dụng', '#CC79A7')]
    fig, ax = plt.subplots(figsize=(9.4, 5.0))
    ys = range(len(top), 0, -1)
    for d, y in zip(top, ys):
        x = 0
        for k, _, c in vai:
            v = d[k]
            if v:
                ax.barh(y, v, left=x, height=0.62, color=c, edgecolor='white',
                        linewidth=1.2, zorder=3)
                x += v
        ax.text(x + 0.5, y, str(d['n_bai']), va='center', fontsize=9.5, color='#333333')
    ax.set_yticks(list(ys))
    ax.set_yticklabels([f"{d['ten']}  ({TEN_NHANH[d['nhanh']]} · {d['nam']})" for d in top],
                       fontsize=10)
    ax.set_xlabel('Số công bố trong kho liên quan đến bộ dữ liệu', fontsize=10)
    ax.set_xlim(0, 52)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.xaxis.grid(True, color='#DDDDDD', linewidth=0.6, zorder=0); ax.set_axisbelow(True)
    leg = [Patch(facecolor=c, edgecolor='white', label=t) for _, t, c in vai]
    ax.legend(handles=leg, loc='lower right', frameon=False, fontsize=9.5,
              title='Vai trò của công bố', title_fontsize=10)
    fig.savefig(HINH / 'H7_tai_su_dung.png'); plt.close(fig)

ve_H2(); ve_H3(); ve_H4(); ve_H5(); ve_H6(); ve_H7()
print('OK -> 6 hinh moi (H2..H7); H1 tai dung tu v48')
