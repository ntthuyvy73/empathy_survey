# -*- coding: utf-8 -*-
"""
p_v53_ban_do.py — Phân tích bản đồ v53: taxonomy ba trục F–T–D quanh trục lý thuyết lâm sàng.

Nguồn duy nhất: 03_phan_tich/wave3_ai_final_30cot.xlsx
  - sheet `text-dataset` (mức bài), lọc final_trang_thai ∈ {DUNG-chac-chan, kho-cu-tai-nhap}
  - danh mục mức bộ dữ liệu dựng lại từ cột `dataset` (tách ';', chuẩn hóa tên),
    đối chiếu bắt buộc khớp 100% với 05_bai_bao/danh_muc_v50_loc.csv (bản đã assert v50).

Đầu ra:
  - 05_bai_bao/so_lieu_v53.json  (mọi con số dùng trong bài)
  - 05_bai_bao/so_lieu_v53_doc.txt (bản đọc cho người)
  - 05_bai_bao/hinh/H1_ban_do_phan_tang.png, H2_timeline_nguon_goc.png,
    H3_truc_ly_thuyet.png, H4_tai_su_dung.png, H5_matran_tiepcan_nhanh.png
"""
import csv, json, sys, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

BASE = Path(r'H:\Vy\Paper\Empathy\Report\_Chuan_bi\_analyst_v7\wave3_nlp_tham_van')
XLSX = BASE / '03_phan_tich' / 'wave3_ai_final_30cot.xlsx'
CSV_V50 = BASE / '05_bai_bao' / 'danh_muc_v50_loc.csv'
OUT_JSON = BASE / '05_bai_bao' / 'so_lieu_v53.json'
OUT_TXT = BASE / '05_bai_bao' / 'so_lieu_v53_doc.txt'
HINH = BASE / '05_bai_bao' / 'hinh'
HINH.mkdir(exist_ok=True)

GIU = {'DUNG-chac-chan', 'kho-cu-tai-nhap'}
MXH = 'MXH-thong-ke'

# ---------- Trục T: phân tầng nhãn lý thuyết ----------
# T-b: khung quá trình giao tiếp / họ chiến lược vận hành hóa (không phải liệu pháp trọn vẹn)
# T-a: định hướng / liệu pháp
NHAN_CHUAN = {
    'ESC': ('ESC', 'T-b'),
    'Hill': ('Helping Skills', 'T-b'),
    'MI': ('MI', 'T-b'),
    'CBT': ('CBT', 'T-a'),
    'psychodynamic': ('tam-dong-hoc', 'T-a'),
    'client-centered': ('than-chu-trong-tam', 'T-a'),
    'mindfulness': ('chanh-niem', 'T-a'),
    'ACT': ('ACT', 'T-a'),
    'DBT': ('DBT', 'T-a'),
    'SFBT': ('SFBT', 'T-a'),
    'EFT': ('EFT', 'T-a'),
    'Schema': ('schema', 'T-a'),
    'EMS/schema-therapy': ('schema', 'T-a'),
    'Schema-Therapy': ('schema', 'T-a'),
}
TRANG = ['IPT', 'EMDR', 'MBCT', 'Gestalt', 'gia-dinh/he-thong']  # kiểm tra phải = 0

# ---------- Trục F: cấp 1 phạm vi ← cấp 2 nhánh ----------
PHAM_VI = {
    'ESC': 'ES', 'dong-dang': 'ES',
    'tham-van': 'CO',
    'tri-lieu': 'PT',
    'khung-hoang': 'BT', 'sang-loc-lam-sang': 'BT', 'chan-doan': 'BT',
    'dao-tao-ky-nang': 'BT', 'khac': 'BT',
}
TEN_PHAM_VI = {'ES': 'Hỗ trợ cảm xúc – đồng đẳng', 'CO': 'Tham vấn', 'PT': 'Trị liệu',
               'BT': 'Chức năng bổ trợ quanh liệu trình'}
THU_TU_NHANH = ['ESC', 'dong-dang', 'tham-van', 'tri-lieu',
                'khung-hoang', 'sang-loc-lam-sang', 'chan-doan', 'dao-tao-ky-nang', 'khac']

def norm_key(s: str) -> str:
    # Quy tắc khóa của danh_muc_v50_loc.csv: chữ thường, giữ nguyên mọi ký tự chữ-số Unicode
    return ''.join(c for c in s.lower() if c.isalnum())

def era_cua_nam(y: int) -> str:
    if y < 2018: return 'tien-PLM'
    if y <= 2022: return 'PLM'
    return 'LLM'

def tach_nhan(raw: str):
    """Tách chuỗi ly_thuyet đa nhãn thành danh sách (nhãn chuẩn, tầng)."""
    out = []
    for p in str(raw).split(';'):
        p = p.strip()
        if not p or p.lower() in ('none', ''):
            continue
        if p not in NHAN_CHUAN:
            raise ValueError(f'Nhãn lý thuyết lạ: {p!r} trong {raw!r}')
        out.append(NHAN_CHUAN[p])
    return out

# ============================================================
# 1. MỨC BÀI — đọc sheet text-dataset, lọc
# ============================================================
wb = openpyxl.load_workbook(XLSX, read_only=True)
ws = wb['text-dataset']
rows = ws.iter_rows(values_only=True)
header = [str(h) if h is not None else '' for h in next(rows)]
papers_all = [dict(zip(header, r)) for r in rows]
papers_all = [p for p in papers_all if any(v not in (None, '') for v in p.values())]
papers = [p for p in papers_all if str(p.get('final_trang_thai', '')).strip() in GIU]

S = {}  # kho số liệu
S['bai'] = {
    'tong_sheet': len(papers_all),
    'tong_loc': len(papers),
    'theo_trang_thai': dict(Counter(str(p['final_trang_thai']).strip() for p in papers)),
    'theo_vai_tro': dict(Counter(str(p['lien_quan_dataset']).strip() for p in papers)),
}
assert S['bai']['tong_loc'] == 1205, S['bai']['tong_loc']

# ============================================================
# 2. MỨC BỘ DỮ LIỆU — nạp danh mục v50 (đã assert) + đối chiếu dựng lại từ xlsx
# ============================================================
with open(CSV_V50, encoding='utf-8-sig') as f:
    catalog = list(csv.DictReader(f))
for d in catalog:
    d['n_bai'] = int(d['n_bai'])
    for c in ('n_gioi_thieu', 'n_danh_gia', 'n_phat_trien', 'n_su_dung'):
        d[c] = int(d[c]) if d[c] else 0
    d['nam'] = int(d['nam_som_nhat'])
    d['era'] = era_cua_nam(d['nam'])
    d['nhan'] = tach_nhan(d.get('ly_thuyet', ''))
    d['pham_vi'] = PHAM_VI.get(d['nhom_mien'])

# --- Đối chiếu: dựng lại liên kết bài–bộ từ xlsx, khớp key và n_bai với CSV ---
links = defaultdict(set)   # key -> set(rec_id)
for p in papers:
    ds_raw = str(p.get('dataset') or '').strip()
    if not ds_raw or ds_raw.lower() == 'none':
        continue
    for ten in ds_raw.split(';'):
        ten = ten.strip()
        if ten:
            links[norm_key(ten)].add(str(p['rec_id']))
csv_keys = {d['key'] for d in catalog}
xlsx_keys = set(links)
S['doi_chieu'] = {
    'so_key_csv': len(csv_keys),
    'so_key_xlsx': len(xlsx_keys),
    'key_chi_co_csv': sorted(csv_keys - xlsx_keys)[:20],
    'key_chi_co_xlsx': sorted(xlsx_keys - csv_keys)[:20],
    'n_bai_lech': [],
}
if csv_keys == xlsx_keys:
    for d in catalog:
        if len(links[d['key']]) != d['n_bai']:
            S['doi_chieu']['n_bai_lech'].append((d['key'], d['n_bai'], len(links[d['key']])))
S['doi_chieu']['khop_100'] = (csv_keys == xlsx_keys and not S['doi_chieu']['n_bai_lech'])

main = [d for d in catalog if d['nhom_mien'] != MXH]
mxh = [d for d in catalog if d['nhom_mien'] == MXH]

def pct(a, b): return round(100.0 * a / b, 1)

# ============================================================
# 3. TOÀN CẢNH — trục F
# ============================================================
S['toan_canh'] = {
    'tong_catalog': len(catalog), 'mxh': len(mxh), 'ban_do_chinh': len(main),
    'text_thuan': sum(1 for d in main if d['phuong_thuc'] == 'text'),
    'text_ket_hop': sum(1 for d in main if d['phuong_thuc'] != 'text'),
    'tong_lien_ket': sum(d['n_bai'] for d in main),
}
def hop_phuong_thuc(pt):
    return 'text+voice' if pt in ('text+voice', 'voice+text') else pt
S['to_hop_phuong_thuc'] = dict(Counter(hop_phuong_thuc(d['phuong_thuc']) for d in main if d['phuong_thuc'] != 'text'))

nhanh_tk = {}
for nh in THU_TU_NHANH:
    ds = [d for d in main if d['nhom_mien'] == nh]
    nhanh_tk[nh] = {
        'n': len(ds),
        'text_thuan': sum(1 for d in ds if d['phuong_thuc'] == 'text'),
        'ket_hop': sum(1 for d in ds if d['phuong_thuc'] != 'text'),
        'co_ten': sum(1 for d in ds if d['co_ten'] == 'co'),
        'pct_co_ten': pct(sum(1 for d in ds if d['co_ten'] == 'co'), len(ds)),
        'co_neo': sum(1 for d in ds if d['nhan']),
        'pct_co_neo': pct(sum(1 for d in ds if d['nhan']), len(ds)),
        'T_a': sum(1 for d in ds if any(t == 'T-a' for _, t in d['nhan'])),
        'T_b_thuan': sum(1 for d in ds if d['nhan'] and all(t == 'T-b' for _, t in d['nhan'])),
        'don_luot': sum(1 for d in ds if d['don_da_luot'] == 'don-luot'),
        'da_luot': sum(1 for d in ds if d['don_da_luot'] == 'da-luot'),
        'pct_don': pct(sum(1 for d in ds if d['don_da_luot'] == 'don-luot'), len(ds)),
    }
S['nhanh'] = nhanh_tk
S['pham_vi'] = {}
for pv in ('ES', 'CO', 'PT', 'BT'):
    ds = [d for d in main if d['pham_vi'] == pv]
    S['pham_vi'][pv] = {
        'n': len(ds), 'pct': pct(len(ds), len(main)),
        'co_neo': sum(1 for d in ds if d['nhan']),
        'pct_co_neo': pct(sum(1 for d in ds if d['nhan']), len(ds)),
    }

# --- Cây hình thái văn bản (cho hình cây v54) ---
tt = [d for d in main if d['phuong_thuc'] == 'text']
kh = [d for d in main if d['phuong_thuc'] != 'text']
S['cay_hinh_thai'] = {
    'text_thuan': {
        'n': len(tt),
        'da_luot': sum(1 for d in tt if d['don_da_luot'] == 'da-luot'),
        'don_luot': sum(1 for d in tt if d['don_da_luot'] == 'don-luot'),
        'khong_ro': sum(1 for d in tt if d['don_da_luot'] == 'khong-ro'),
    },
    'ket_hop': {
        'n': len(kh),
        'to_hop': dict(Counter(hop_phuong_thuc(d['phuong_thuc']) for d in kh)),
        'da_luot': sum(1 for d in kh if d['don_da_luot'] == 'da-luot'),
    },
}

# ============================================================
# 4. TRỤC D6 — thời kỳ; D1 — nguồn gốc
# ============================================================
S['thoi_ky'] = {e: sum(1 for d in main if d['era'] == e) for e in ('tien-PLM', 'PLM', 'LLM')}
S['thoi_ky_pct'] = {e: pct(v, len(main)) for e, v in S['thoi_ky'].items()}
S['theo_nam'] = dict(sorted(Counter(d['nam'] for d in main).items()))

NGUON = ['hoi-thoai-that', 'dong-vai', 'MXH-dien-dan', 'hon-hop', 'tong-hop-LLM', 'khong-ro']
S['nguon_toan_cuc'] = {g: sum(1 for d in main if d['nguon_du_lieu'] == g) for g in NGUON}
S['nguon_x_thoi_ky'] = {g: {e: sum(1 for d in main if d['nguon_du_lieu'] == g and d['era'] == e)
                            for e in ('tien-PLM', 'PLM', 'LLM')} for g in NGUON}
S['pct_that_theo_era'] = {e: pct(S['nguon_x_thoi_ky']['hoi-thoai-that'][e], S['thoi_ky'][e])
                          for e in ('tien-PLM', 'PLM', 'LLM')}
llm_hh_moi = S['nguon_x_thoi_ky']['tong-hop-LLM']['LLM'] + S['nguon_x_thoi_ky']['hon-hop']['LLM']
S['pct_llm_honhop_era_llm'] = pct(llm_hh_moi, S['thoi_ky']['LLM'])

# ============================================================
# 5. TRỤC T — neo lý thuyết (phân tích trung tâm)
# ============================================================
neo = [d for d in main if d['nhan']]
S['neo'] = {
    'so_bo_co_neo': len(neo), 'pct_co_neo': pct(len(neo), len(main)),
    'so_bo_khong_neo': len(main) - len(neo),
    'pct_khong_neo': pct(len(main) - len(neo), len(main)),
}
dem_nhan = Counter()
for d in main:
    for nh, _ in d['nhan']:
        dem_nhan[nh] += 1
S['nhan_dem'] = dict(dem_nhan.most_common())
S['tong_luot_nhan'] = sum(dem_nhan.values())

Ta_bo = [d for d in main if any(t == 'T-a' for _, t in d['nhan'])]
Tb_bo = [d for d in main if any(t == 'T-b' for _, t in d['nhan'])]
S['neo']['T_a_bo'] = len(Ta_bo)
S['neo']['T_a_pct_ban_do'] = pct(len(Ta_bo), len(main))
S['neo']['T_b_bo'] = len(Tb_bo)
S['neo']['T_b_pct_ban_do'] = pct(len(Tb_bo), len(main))
S['neo']['ca_hai_tang'] = sum(1 for d in main if any(t == 'T-a' for _, t in d['nhan'])
                              and any(t == 'T-b' for _, t in d['nhan']))
tong_luot_Ta = sum(v for k, v in dem_nhan.items()
                   if k in {'CBT', 'tam-dong-hoc', 'than-chu-trong-tam', 'chanh-niem',
                            'ACT', 'DBT', 'SFBT', 'EFT', 'schema'})
S['neo']['tong_luot_T_a'] = tong_luot_Ta
S['neo']['CBT_trong_T_a_pct'] = pct(dem_nhan['CBT'], tong_luot_Ta)
tong_luot_Tb = dem_nhan['ESC'] + dem_nhan['MI'] + dem_nhan['Helping Skills']
S['neo']['tong_luot_T_b'] = tong_luot_Tb

# nhãn trắng — phải bằng 0
for t in TRANG:
    assert dem_nhan.get(t, 0) == 0
S['neo']['nhan_trang'] = {t: 0 for t in TRANG}

# neo × thời kỳ
S['neo_x_thoi_ky'] = {e: {'n': S['thoi_ky'][e],
                          'co_neo': sum(1 for d in main if d['era'] == e and d['nhan']),
                          'pct': pct(sum(1 for d in main if d['era'] == e and d['nhan']), S['thoi_ky'][e])}
                      for e in ('tien-PLM', 'PLM', 'LLM')}

# ma trận nhãn × nhánh
matran = {}
for nh in dem_nhan:
    matran[nh] = {b: 0 for b in THU_TU_NHANH}
for d in main:
    for nh, _ in d['nhan']:
        matran[nh][d['nhom_mien']] += 1
S['matran_nhan_nhanh'] = matran
S['lanh_tho'] = {
    'ESC_o_ESC': matran['ESC']['ESC'], 'ESC_tong': dem_nhan['ESC'],
    'CBT_o_trilieu': matran['CBT']['tri-lieu'], 'CBT_tong': dem_nhan['CBT'],
    'MI_o_thamvan': matran['MI']['tham-van'], 'MI_tong': dem_nhan['MI'],
}

# nguồn gốc lời thoại bên trong từng dòng nhãn chính
def nguon_theo_nhan(nhan):
    ds = [d for d in main if any(n == nhan for n, _ in d['nhan'])]
    c = Counter(d['nguon_du_lieu'] for d in ds)
    tong = len(ds)
    return {'n': tong,
            'that': c.get('hoi-thoai-that', 0), 'pct_that': pct(c.get('hoi-thoai-that', 0), tong),
            'sinh_llm': c.get('tong-hop-LLM', 0), 'dong_vai': c.get('dong-vai', 0),
            'hon_hop': c.get('hon-hop', 0), 'mxh': c.get('MXH-dien-dan', 0),
            'khong_ro': c.get('khong-ro', 0),
            'pct_llm_dongvai_honhop': pct(c.get('tong-hop-LLM', 0) + c.get('dong-vai', 0) + c.get('hon-hop', 0), tong),
            'nam_som_nhat': min(d['nam'] for d in ds)}
S['nguon_theo_nhan'] = {nh: nguon_theo_nhan(nh) for nh in dem_nhan}

# neo có tên vs không tên
S['neo_vs_ten'] = {
    'pct_co_ten_khi_neo': pct(sum(1 for d in neo if d['co_ten'] == 'co'), len(neo)),
    'pct_co_ten_khi_khong_neo': pct(sum(1 for d in main if not d['nhan'] and d['co_ten'] == 'co'),
                                    len(main) - len(neo)),
}

# --- Độ nhạy phân tầng (M2): các con số đầu bài dưới cách xếp tầng thay thế ---
def bo_co_nhan_trong(d, tap):
    return any(nh in tap for nh, _ in d['nhan'])
TA_GOC = {'CBT', 'tam-dong-hoc', 'than-chu-trong-tam', 'chanh-niem', 'ACT', 'DBT',
          'SFBT', 'EFT', 'schema'}
def do_nhay(tap_Ta):
    bo = [d for d in main if bo_co_nhan_trong(d, tap_Ta)]
    tv = [d for d in main if d['nhom_mien'] == 'tham-van']
    tl = [d for d in main if d['nhom_mien'] == 'tri-lieu']
    return {'T_a_bo': len(bo), 'pct': pct(len(bo), len(main)),
            'CO_pct': pct(sum(1 for d in tv if bo_co_nhan_trong(d, tap_Ta)), len(tv)),
            'PT_pct': pct(sum(1 for d in tl if bo_co_nhan_trong(d, tap_Ta)), len(tl))}
S['do_nhay'] = {
    'V0_goc': do_nhay(TA_GOC),
    'V1_MI_vao_Ta': do_nhay(TA_GOC | {'MI'}),
    'V2_MI_ESC_HS_vao_Ta': do_nhay(TA_GOC | {'MI', 'ESC', 'Helping Skills'}),
}

# --- Khoảng tin cậy Wilson 95% cho tỷ lệ neo theo thời kỳ (M4d) ---
def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n
    den = 1 + z*z/n
    centre = (p + z*z/(2*n)) / den
    half = z * ((p*(1-p)/n + z*z/(4*n*n)) ** 0.5) / den
    return (round(100*(centre - half), 1), round(100*(centre + half), 1))
for e in ('tien-PLM', 'PLM', 'LLM'):
    k, n = S['neo_x_thoi_ky'][e]['co_neo'], S['neo_x_thoi_ky'][e]['n']
    S['neo_x_thoi_ky'][e]['ci95'] = wilson(k, n)

# --- Neo × tên phân tầng theo nhánh (M7 — kiểm tra Simpson) ---
S['neo_ten_theo_nhanh'] = {}
for nh in THU_TU_NHANH:
    ds = [d for d in main if d['nhom_mien'] == nh]
    neo_nh = [d for d in ds if d['nhan']]
    khong_nh = [d for d in ds if not d['nhan']]
    if len(neo_nh) >= 10 and len(khong_nh) >= 10:
        S['neo_ten_theo_nhanh'][nh] = {
            'ten_khi_neo': pct(sum(1 for d in neo_nh if d['co_ten'] == 'co'), len(neo_nh)),
            'ten_khi_khong': pct(sum(1 for d in khong_nh if d['co_ten'] == 'co'), len(khong_nh)),
            'n_neo': len(neo_nh), 'n_khong': len(khong_nh)}

# ============================================================
# 6. CHUẨN HÓA — đặt tên, tái sử dụng, truy cập
# ============================================================
mot_bai = sum(1 for d in main if d['n_bai'] == 1)
S['chuan_hoa'] = {
    'mot_bai': mot_bai, 'pct_mot_bai': pct(mot_bai, len(main)),
    'tu_2_bai': sum(1 for d in main if d['n_bai'] >= 2),
    'tu_5_bai': sum(1 for d in main if d['n_bai'] >= 5),
    'tu_10_bai': sum(1 for d in main if d['n_bai'] >= 10),
    'khong_ten': sum(1 for d in main if d['co_ten'] != 'co'),
    'pct_khong_ten': pct(sum(1 for d in main if d['co_ten'] != 'co'), len(main)),
    'co_ten': sum(1 for d in main if d['co_ten'] == 'co'),
    'co_bai_gioi_thieu': sum(1 for d in main if d['n_gioi_thieu'] > 0),
    'pct_co_bai_gioi_thieu': pct(sum(1 for d in main if d['n_gioi_thieu'] > 0), len(main)),
}
# availability mức bộ: gộp từ mức bài qua liên kết (ưu tiên open > mixed > closed)
av_bai = {str(p['rec_id']): str(p.get('availability') or '').strip() for p in papers}
def av_cua_bo(d):
    vals = {av_bai.get(r, '') for r in links.get(d['key'], set())}
    vals = {v for v in vals if v and v != 'unstated'}
    if 'open' in vals: return 'open'
    if 'mixed' in vals: return 'mixed'
    if 'closed' in vals: return 'closed'
    return 'khong-tuyen-bo'
for d in catalog:
    d['av'] = av_cua_bo(d)
S['truy_cap'] = dict(Counter(d['av'] for d in main))
S['truy_cap_pct_khong'] = pct(S['truy_cap'].get('khong-tuyen-bo', 0), len(main))

# Mục giả 'khong-ro' (gộp các bài chỉ ghi tên bộ là không rõ) không phải bộ có tên thật:
# loại khỏi xếp hạng tái sử dụng và phép đếm "bộ có tên đạt >=5 bài" (nhất quán v50).
ten_that = [d for d in main if d['co_ten'] == 'co' and d['key'] != 'khongro']
S['chuan_hoa']['tu_5_bai_co_ten'] = sum(1 for d in ten_that if d['n_bai'] >= 5)
# --- Tái sử dụng phân tầng theo tuổi và theo nhóm có tên (M5) ---
truoc_2023 = [d for d in main if d['nam'] < 2023]
llm_era = [d for d in main if d['era'] == 'LLM']
S['tai_su_dung_phan_tang'] = {
    'truoc_2023_n': len(truoc_2023),
    'truoc_2023_pct_don_dung': pct(sum(1 for d in truoc_2023 if d['n_bai'] == 1), len(truoc_2023)),
    'llm_n': len(llm_era),
    'llm_pct_don_dung': pct(sum(1 for d in llm_era if d['n_bai'] == 1), len(llm_era)),
    'co_ten_that_n': len(ten_that),
    'co_ten_tu_2_bai': sum(1 for d in ten_that if d['n_bai'] >= 2),
    'co_ten_pct_tai_su_dung': pct(sum(1 for d in ten_that if d['n_bai'] >= 2), len(ten_that)),
}
tt_co_ten = [d for d in truoc_2023 if d['co_ten'] == 'co' and d['key'] != 'khongro']
S['tai_su_dung_phan_tang']['truoc_2023_co_ten_n'] = len(tt_co_ten)
S['tai_su_dung_phan_tang']['truoc_2023_co_ten_pct_tsd'] = pct(
    sum(1 for d in tt_co_ten if d['n_bai'] >= 2), len(tt_co_ten))
S['chuan_hoa']['ghi_chu_khongro'] = 'muc gia khong-ro n_bai=8 nam trong tu_5_bai tong nhung bi loai khoi bang/hinh tai su dung'
top = sorted(ten_that, key=lambda d: -d['n_bai'])[:12]
S['top_tai_su_dung'] = [{
    'ten': d['ten_dataset'], 'nhanh': d['nhom_mien'], 'nam': d['nam'],
    'nguon': d['nguon_du_lieu'], 'n_bai': d['n_bai'],
    'gt': d['n_gioi_thieu'], 'dg': d['n_danh_gia'], 'pt': d['n_phat_trien'], 'sd': d['n_su_dung'],
} for d in top]

# ============================================================
# 7. TRỤC D2, D3 — cấu trúc lượt, ngôn ngữ
# ============================================================
S['luot'] = {
    'da': sum(1 for d in main if d['don_da_luot'] == 'da-luot'),
    'don': sum(1 for d in main if d['don_da_luot'] == 'don-luot'),
    'khong_ro': sum(1 for d in main if d['don_da_luot'] == 'khong-ro'),
}
S['luot']['pct_da'] = pct(S['luot']['da'], len(main))
S['luot']['pct_don'] = pct(S['luot']['don'], len(main))

khong_neu_ngon_ngu = sum(1 for d in main if d['ngon_ngu'].strip() == 'khong-ro')
S['ngon_ngu'] = {'khong_neu': khong_neu_ngon_ngu,
                 'pct_khong_neu': pct(khong_neu_ngon_ngu, len(main)),
                 'co_neu': len(main) - khong_neu_ngon_ngu}
dem_ng = Counter()
for d in main:
    v = d['ngon_ngu'].strip()
    if v == 'khong-ro':
        continue
    for part in v.split('+'):
        p2 = part.strip()
        if p2:
            dem_ng[p2] += 1
S['ngon_ngu']['dem'] = dict(dem_ng.most_common())
S['ngon_ngu']['pct_anh_trong_neu'] = pct(dem_ng.get('tiếng Anh', 0), S['ngon_ngu']['co_neu'])

# ============================================================
# 8. NHÓM ĐỐI CHIẾU MXH
# ============================================================
S['mxh'] = {
    'n': len(mxh),
    'tu_2023': sum(1 for d in mxh if d['nam'] >= 2023),
    'dinh_nam': max(Counter(d['nam'] for d in mxh).items(), key=lambda kv: kv[1]),
    'co_neo': sum(1 for d in mxh if d['nhan']),
    'pct_co_neo': pct(sum(1 for d in mxh if d['nhan']), len(mxh)),
    'co_ten': sum(1 for d in mxh if d['co_ten'] == 'co'),
    'pct_co_ten': pct(sum(1 for d in mxh if d['co_ten'] == 'co'), len(mxh)),
}

# ============================================================
# 9. GHI JSON + TXT
# ============================================================
with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(S, f, ensure_ascii=False, indent=1, default=str)

with open(OUT_TXT, 'w', encoding='utf-8') as f:
    def w(*a): f.write(' '.join(str(x) for x in a) + '\n')
    w('=== ĐỐI CHIẾU CATALOG (phải khớp 100%):', S['doi_chieu']['khop_100'])
    if not S['doi_chieu']['khop_100']:
        w('  csv-only:', S['doi_chieu']['key_chi_co_csv'])
        w('  xlsx-only:', S['doi_chieu']['key_chi_co_xlsx'])
        w('  n_bai lệch:', S['doi_chieu']['n_bai_lech'][:20])
    for k in ('bai', 'toan_canh', 'to_hop_phuong_thuc', 'pham_vi', 'thoi_ky', 'thoi_ky_pct',
              'theo_nam', 'nguon_toan_cuc', 'nguon_x_thoi_ky', 'pct_that_theo_era',
              'pct_llm_honhop_era_llm', 'neo', 'nhan_dem', 'tong_luot_nhan',
              'neo_x_thoi_ky', 'lanh_tho', 'nguon_theo_nhan', 'neo_vs_ten',
              'do_nhay', 'neo_ten_theo_nhanh', 'tai_su_dung_phan_tang',
              'chuan_hoa', 'truy_cap', 'truy_cap_pct_khong', 'top_tai_su_dung',
              'luot', 'ngon_ngu', 'mxh'):
        w(f'\n=== {k} ===')
        w(json.dumps(S[k], ensure_ascii=False, indent=1, default=str))
    w('\n=== NHÁNH ===')
    for nh, v in S['nhanh'].items():
        w(nh, json.dumps(v, ensure_ascii=False))
    w('\n=== MA TRẬN nhãn × nhánh ===')
    for nh, row in S['matran_nhan_nhanh'].items():
        w(f'{nh:22}', {k: v for k, v in row.items() if v})

print('KHOP_CATALOG =', S['doi_chieu']['khop_100'])
print('OK -> so_lieu_v53.json')
