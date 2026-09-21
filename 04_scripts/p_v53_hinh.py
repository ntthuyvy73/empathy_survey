# -*- coding: utf-8 -*-
"""
p_v53_hinh.py — Vẽ 5 hình cho bài v53 từ so_lieu_v53.json + danh_muc_v50_loc.csv.
Palette Okabe–Ito (an toàn mù màu, đã validate); "không rõ" = xám trung tính + vân trắng.
Times New Roman, 300 dpi, lưu 05_bai_bao/hinh/.
"""
import csv, json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

BASE = Path(r'H:\Vy\Paper\Empathy\Report\_Chuan_bi\_analyst_v7\wave3_nlp_tham_van')
S = json.load(open(BASE / '05_bai_bao' / 'so_lieu_v53.json', encoding='utf-8'))
HINH = BASE / '05_bai_bao' / 'hinh'

plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.size': 10.5,
    'axes.edgecolor': '#888888',
    'axes.linewidth': 0.8,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.facecolor': 'white',
})

# Màu nguồn gốc lời thoại (cố định, không xoay vòng)
MAU_NGUON = {
    'hoi-thoai-that': '#0072B2',
    'dong-vai': '#E69F00',
    'MXH-dien-dan': '#009E73',
    'tong-hop-LLM': '#D55E00',
    'hon-hop': '#CC79A7',
    'khong-ro': '#C9C9C9',
}
TEN_NGUON = {
    'hoi-thoai-that': 'Hội thoại thật', 'dong-vai': 'Đóng vai',
    'MXH-dien-dan': 'MXH/diễn đàn', 'tong-hop-LLM': 'Tổng hợp bằng LLM',
    'hon-hop': 'Hỗn hợp', 'khong-ro': 'Không rõ (tóm tắt không nêu)',
}
TT_NGUON = ['hoi-thoai-that', 'dong-vai', 'MXH-dien-dan', 'hon-hop', 'tong-hop-LLM', 'khong-ro']

TEN_NHANH = {
    'ESC': 'Hỗ trợ cảm xúc (ESC)', 'dong-dang': 'Đồng đẳng', 'tham-van': 'Tham vấn',
    'tri-lieu': 'Trị liệu', 'khung-hoang': 'Khủng hoảng', 'sang-loc-lam-sang': 'Sàng lọc lâm sàng',
    'chan-doan': 'Chẩn đoán', 'dao-tao-ky-nang': 'Đào tạo kỹ năng', 'khac': 'Khác',
}

def seg_bar(ax, y, vals, colors, hatches=None, h=0.62):
    """Thanh ngang xếp chồng, khe trắng giữa các đoạn."""
    x = 0
    for i, (v, c) in enumerate(zip(vals, colors)):
        if v <= 0:
            continue
        ht = hatches[i] if hatches else None
        ax.barh(y, v, left=x, height=h, color=c, edgecolor='white',
                linewidth=1.2, hatch=ht, zorder=3)
        x += v
    return x

# ============================================================
# H1 — BẢN ĐỒ PHÂN TẦNG: phạm vi -> nhánh -> tầng neo lý thuyết
# ============================================================
def ve_H1():
    khoi = [
        ('Hỗ trợ cảm xúc – đồng đẳng (ES)', ['ESC', 'dong-dang']),
        ('Tham vấn (CO)', ['tham-van']),
        ('Trị liệu (PT)', ['tri-lieu']),
        ('Chức năng bổ trợ quanh liệu trình (BT)', ['khung-hoang', 'sang-loc-lam-sang',
                                                    'chan-doan', 'dao-tao-ky-nang', 'khac']),
    ]
    pv_n = {'Hỗ trợ cảm xúc – đồng đẳng (ES)': S['pham_vi']['ES'],
            'Tham vấn (CO)': S['pham_vi']['CO'],
            'Trị liệu (PT)': S['pham_vi']['PT'],
            'Chức năng bổ trợ quanh liệu trình (BT)': S['pham_vi']['BT']}
    fig, ax = plt.subplots(figsize=(9.6, 6.6))
    y = 0
    yticks, ylabels = [], []
    mau = ['#0072B2', '#E69F00', '#C9C9C9']
    hatch = [None, None, '///']
    for ten_khoi, ds_nhanh in khoi:
        n_pv = pv_n[ten_khoi]
        pct_vn = str(n_pv['pct']).replace('.', ',')
        ax.text(-8, y, f'{ten_khoi} — {n_pv["n"]} bộ ({pct_vn}%)',
                ha='left', va='center', fontsize=11, fontweight='bold', color='#222222')
        y -= 1
        for nh in ds_nhanh:
            d = S['nhanh'][nh]
            khong_neo = d['n'] - d['T_a'] - d['T_b_thuan']
            seg_bar(ax, y, [d['T_a'], d['T_b_thuan'], khong_neo], mau, hatch)
            ax.text(d['n'] + 4, y, f"{d['n']} bộ · neo {d['pct_co_neo']:.0f}%",
                    va='center', fontsize=9.5, color='#333333')
            yticks.append(y); ylabels.append(TEN_NHANH[nh])
            y -= 1
        y -= 0.55
    ax.set_yticks(yticks); ax.set_yticklabels(ylabels, fontsize=10.5)
    ax.set_xlim(0, 340)
    ax.set_ylim(y + 0.2, 0.8)
    ax.set_xlabel('Số bộ dữ liệu', fontsize=10.5)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.xaxis.grid(True, color='#DDDDDD', linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    leg = [Patch(facecolor='#0072B2', edgecolor='white', label='Neo học thuyết trị liệu (tầng T-a)'),
           Patch(facecolor='#E69F00', edgecolor='white', label='Chỉ neo khung quá trình/chiến lược (tầng T-b)'),
           Patch(facecolor='#C9C9C9', edgecolor='white', hatch='///', label='Không khai báo tiếp cận')]
    ax.legend(handles=leg, loc='lower right', frameon=False, fontsize=9.5,
              bbox_to_anchor=(1.0, -0.02))
    fig.savefig(HINH / 'H1_ban_do_phan_tang.png')
    plt.close(fig)

# ============================================================
# H2 — TIMELINE ba thời kỳ × nguồn gốc lời thoại
# ============================================================
def ve_H2():
    with open(BASE / '05_bai_bao' / 'danh_muc_v50_loc.csv', encoding='utf-8-sig') as f:
        cat = [d for d in csv.DictReader(f) if d['nhom_mien'] != 'MXH-thong-ke']
    for d in cat:
        d['nam'] = int(d['nam_som_nhat'])
    nams = list(range(1999, 2027))
    fig, ax = plt.subplots(figsize=(10.2, 4.6))
    bottom = {n: 0 for n in nams}
    for g in TT_NGUON:
        vals = []
        for n in nams:
            v = sum(1 for d in cat if d['nam'] == n and d['nguon_du_lieu'] == g)
            vals.append(v)
        ax.bar(nams, vals, bottom=[bottom[n] for n in nams], width=0.78,
               color=MAU_NGUON[g], edgecolor='white', linewidth=0.7,
               hatch='///' if g == 'khong-ro' else None,
               label=TEN_NGUON[g], zorder=3)
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
    ax.set_xlim(1998.2, 2026.8)
    ax.set_ylim(0, 300)
    ax.set_xticks([1999, 2004, 2010, 2015, 2018, 2021, 2024, 2026])
    ax.set_ylabel('Số bộ dữ liệu mới theo năm xuất hiện sớm nhất', fontsize=10)
    ax.spines[['top', 'right']].set_visible(False)
    ax.yaxis.grid(True, color='#DDDDDD', linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc='center left', bbox_to_anchor=(0.015, 0.52), frameon=False, fontsize=9, ncol=1)
    fig.savefig(HINH / 'H2_timeline_nguon_goc.png')
    plt.close(fig)

# ============================================================
# H3 — TRỤC LÝ THUYẾT: mỗi dòng học thuyết/khung × nguồn dữ liệu + hệ mã văn bản
# ============================================================
HE_MA = {
    'ESC': 'họ chiến lược ESC [văn bản]', 'MI': 'MISC/MITI [văn bản]',
    'Helping Skills': 'hệ mã Hill [văn bản]', 'CBT': 'CTRS [văn bản]',
    'tam-dong-hoc': 'CPPS [ngoài văn bản]', 'than-chu-trong-tam': 'thang thấu cảm [ngoài văn bản]',
    'chanh-niem': 'MBI:TAC [ngoài văn bản]', 'ACT': 'ACT-FM [ngoài văn bản]',
    'DBT': 'DBT-ACS [ngoài văn bản]',
    'schema': 'chưa có', 'SFBT': 'chưa có', 'EFT': 'chưa có',
    'IPT': 'CSPRS [ngoài văn bản]', 'MBCT': 'MBI:TAC [ngoài văn bản]',
    'EMDR': 'EFRS [ngoài văn bản]',
    'Gestalt': 'chưa có', 'gia-dinh/he-thong': 'chưa có',
}
TEN_NHAN = {
    'ESC': 'Chiến lược hỗ trợ cảm xúc (ESC)', 'MI': 'Phỏng vấn tạo động lực (MI)',
    'Helping Skills': 'Helping Skills (Hill)', 'CBT': 'CBT',
    'tam-dong-hoc': 'Tâm động học', 'than-chu-trong-tam': 'Thân chủ trọng tâm',
    'chanh-niem': 'Chánh niệm', 'ACT': 'ACT', 'schema': 'Schema therapy',
    'SFBT': 'SFBT', 'DBT': 'DBT', 'EFT': 'EFT',
    'IPT': 'IPT', 'MBCT': 'MBCT', 'EMDR': 'EMDR',
    'Gestalt': 'Gestalt', 'gia-dinh/he-thong': 'Hệ thống/gia đình',
}
def ve_H3():
    nsn = S['nguon_theo_nhan']
    tb = ['ESC', 'MI', 'Helping Skills']
    ta = ['CBT', 'tam-dong-hoc', 'than-chu-trong-tam', 'chanh-niem', 'ACT',
          'schema', 'SFBT', 'DBT', 'EFT']
    trang = ['IPT', 'MBCT', 'EMDR', 'Gestalt', 'gia-dinh/he-thong']
    fig, ax = plt.subplots(figsize=(10.0, 7.0))
    y = 0
    yticks, ylabels = [], []
    def khoi(ten):
        nonlocal y
        ax.text(-4, y, ten, ha='left', va='center', fontsize=10.5,
                fontweight='bold', color='#222222')
        y -= 1
    def hang(nh, co_du_lieu=True):
        nonlocal y
        if co_du_lieu:
            d = nsn[nh]
            vals = [d['that'], d['dong_vai'], d['mxh'], d['hon_hop'], d['sinh_llm'], d['khong_ro']]
            cols = [MAU_NGUON[g] for g in TT_NGUON]
            hat = [None, None, None, None, None, '///']
            seg_bar(ax, y, vals, cols, hat, h=0.6)
            ax.text(d['n'] + 2.5, y, f"{d['n']}", va='center', fontsize=9.5, color='#333333')
        else:
            ax.text(1.5, y, '0 — không nhận diện được trong bản đồ', va='center',
                    fontsize=9.5, color='#8A8A8A', style='italic')
        ax.text(163, y, HE_MA[nh], va='center', fontsize=9.5, color='#222222')
        yticks.append(y); ylabels.append(TEN_NHAN[nh])
        y -= 1
    khoi('Tầng T-b — khung quá trình giao tiếp và họ chiến lược')
    for nh in tb: hang(nh)
    y -= 0.5
    khoi('Tầng T-a — định hướng / liệu pháp')
    for nh in ta: hang(nh)
    y -= 0.5
    khoi('Liệu pháp có bằng chứng chưa có bộ dữ liệu nào trong bản đồ')
    for nh in trang: hang(nh, co_du_lieu=False)
    ax.text(163, 0.9, 'Hệ đo hành vi/fidelity', fontsize=9.5, fontweight='bold', color='#222222')
    ax.set_yticks(yticks); ax.set_yticklabels(ylabels, fontsize=10.5)
    ax.set_xlim(0, 210)
    ax.set_ylim(y + 0.3, 1.6)
    ax.set_xticks([0, 25, 50, 75, 100, 125, 150])
    ax.set_xlabel('Số bộ dữ liệu mang nhãn (một bộ có thể mang nhiều nhãn)', fontsize=10)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.xaxis.grid(True, color='#DDDDDD', linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    leg = [Patch(facecolor=MAU_NGUON[g], edgecolor='white',
                 hatch='///' if g == 'khong-ro' else None, label=TEN_NGUON[g]) for g in TT_NGUON]
    fig.legend(handles=leg, loc='lower center', frameon=False, fontsize=9.2, ncol=3,
               title='Nguồn gốc lời thoại', title_fontsize=9.5,
               bbox_to_anchor=(0.5, -0.065))
    fig.text(0.5, -0.115, '[văn bản]: hệ mã cấp lượt/phiên chấm trực tiếp trên transcript · '
             '[ngoài văn bản]: công cụ fidelity cần quan sát viên được đào tạo hoặc tín hiệu ngoài transcript\n'
             '"chưa có": không có công cụ đo trong danh mục tham chiếu của bài',
             ha='center', fontsize=8.8, color='#555555')
    fig.savefig(HINH / 'H4_truc_ly_thuyet.png')
    plt.close(fig)

# ============================================================
# H4 — TÁI SỬ DỤNG: các bộ có tên dẫn đầu, tách vai trò bài
# ============================================================
def ve_H4():
    top = S['top_tai_su_dung']
    vai = [('gt', 'Giới thiệu', '#0072B2'), ('dg', 'Đánh giá benchmark', '#009E73'),
           ('pt', 'Phát triển/mở rộng', '#E69F00'), ('sd', 'Sử dụng', '#CC79A7')]
    fig, ax = plt.subplots(figsize=(9.4, 5.0))
    ys = range(len(top), 0, -1)
    for i, (d, y) in enumerate(zip(top, ys)):
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
    ax.xaxis.grid(True, color='#DDDDDD', linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    leg = [Patch(facecolor=c, edgecolor='white', label=t) for _, t, c in vai]
    ax.legend(handles=leg, loc='lower right', frameon=False, fontsize=9.5,
              title='Vai trò của công bố', title_fontsize=10)
    fig.savefig(HINH / 'H5_tai_su_dung.png')
    plt.close(fig)

# ============================================================
# H5 — MA TRẬN tiếp cận × nhánh chức năng
# ============================================================
def ve_H5():
    m = S['matran_nhan_nhanh']
    hang_tt = ['ESC', 'MI', 'Helping Skills', 'CBT', 'tam-dong-hoc', 'than-chu-trong-tam',
               'chanh-niem', 'ACT', 'schema', 'SFBT', 'DBT', 'EFT']
    cot_tt = ['ESC', 'dong-dang', 'tham-van', 'tri-lieu', 'khung-hoang',
              'sang-loc-lam-sang', 'chan-doan', 'dao-tao-ky-nang', 'khac']
    import numpy as np
    M = np.array([[m[r].get(c, 0) for c in cot_tt] for r in hang_tt], dtype=float)
    fig, ax = plt.subplots(figsize=(9.6, 5.6))
    show = np.ma.masked_where(M == 0, M)
    im = ax.imshow(show, cmap='Blues', vmin=0, vmax=60, aspect='auto')
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = int(M[i, j])
            if v:
                ax.text(j, i, str(v), ha='center', va='center', fontsize=9.5,
                        color='white' if v >= 40 else '#1a1a1a')
    ax.set_xticks(range(len(cot_tt)))
    ax.set_xticklabels([TEN_NHANH[c].replace('Hỗ trợ cảm xúc (ESC)', 'ESC') for c in cot_tt],
                       rotation=28, ha='right', fontsize=9.5)
    ax.set_yticks(range(len(hang_tt)))
    ax.set_yticklabels([TEN_NHAN[r] for r in hang_tt], fontsize=10)
    ax.axhline(2.5, color='#555555', linewidth=0.9)
    ax.text(8.45, -0.72, 'Tầng T-b', fontsize=9.5, fontweight='bold', color='#222222', ha='right')
    ax.text(8.45, 2.82, 'Tầng T-a', fontsize=9.5, fontweight='bold', color='#222222', ha='right')
    for e in ('top', 'right', 'left', 'bottom'):
        ax.spines[e].set_visible(False)
    ax.set_xticks([x - 0.5 for x in range(1, len(cot_tt))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(hang_tt))], minor=True)
    ax.grid(which='minor', color='white', linewidth=1.4)
    ax.tick_params(which='both', length=0)
    cb = fig.colorbar(im, ax=ax, shrink=0.72, pad=0.015)
    cb.set_label('Số bộ dữ liệu', fontsize=9.5)
    cb.outline.set_visible(False)
    fig.savefig(HINH / 'H3_matran_tiepcan_nhanh.png')
    plt.close(fig)

ve_H1(); ve_H2(); ve_H3(); ve_H4(); ve_H5()
print('OK -> 5 hinh v53')
