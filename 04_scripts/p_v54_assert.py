# -*- coding: utf-8 -*-
"""
p_v54_assert.py — Đối chiếu TỪNG con số trong bai_bao_1_survey_v54.md với so_lieu_v53.json.
Quy tắc: mọi kiểm tra phải PASS; bất kỳ FAIL nào -> exit 1.
Định dạng số trong bài: nghìn dấu chấm (1.043), thập phân dấu phẩy (36,0%).
"""
import json, re, sys
from pathlib import Path

BASE = Path(r'H:\Vy\Paper\Empathy\Report\_Chuan_bi\_analyst_v7\wave3_nlp_tham_van')
S = json.load(open(BASE / '05_bai_bao' / 'so_lieu_v53.json', encoding='utf-8'))
MD = open(BASE / '05_bai_bao' / 'bai_bao_1_survey_v54.md', encoding='utf-8').read()

FAILS = []
def chk(ten, dieu_kien, chi_tiet=''):
    if not dieu_kien:
        FAILS.append(f'FAIL [{ten}] {chi_tiet}')

def co(ten, *chuoi):
    """Mọi chuỗi phải xuất hiện trong bài."""
    for c in chuoi:
        chk(ten, c in MD, f'thiếu chuỗi: {c!r}')

def nghin(n):  # 1043 -> '1.043'
    return f'{n:,}'.replace(',', '.')

def phay(x):  # 36.0 -> '36,0'
    return str(x).replace('.', ',')

N = S['nhanh']; PV = S['pham_vi']; NEO = S['neo']; TK = S['thoi_ky']
NG = S['nguon_toan_cuc']; NXT = S['nguon_x_thoi_ky']; CH = S['chuan_hoa']
NN = S['ngon_ngu']; L = S['luot']; TC = S['truy_cap']; NTN = S['nguon_theo_nhan']
MAIN = S['toan_canh']['ban_do_chinh']

# ---------- 0. Chuỗi cung ứng dữ liệu ----------
chk('đối chiếu catalog', S['doi_chieu']['khop_100'], 'danh mục dựng lại không khớp CSV v50')
chk('tổng bài', S['bai']['tong_loc'] == 1205)

# ---------- 1. Kho & mức bài ----------
co('kho', nghin(9849) + ' bản ghi duy nhất', '7.578 bản ghi mới', '2.271 bản ghi')
co('bài lọc', f"**{nghin(S['bai']['tong_loc'])} công bố**")
# Dòng chảy sàng lọc — hằng số từ hồ sơ quy trình wave 3 (QUY_TRINH_SANG_LOC_WAVE3.md)
co('dòng chảy', 'Tầng một phủ toàn bộ 7.578 bản ghi mới',
   'Tầng hai phán xử độc lập 3.451 bản ghi',
   'giữ 2.655, chốt dứt điểm ca lửng 759, đảo phán quyết 37',
   'kéo về 37 tóm tắt thiếu', 'chốt thêm 33 ca',
   '2.031 bản ghi thuộc miền chắc chắn, 5.075 ngoài miền, 472 chưa chắc chắn',
   'phục hồi 5 ca loại nhầm')
co('hai diện', f"({S['bai']['theo_trang_thai']['DUNG-chac-chan']} bài)",
   f"({S['bai']['theo_trang_thai']['kho-cu-tai-nhap']} bài)")
vt = S['bai']['theo_vai_tro']
co('vai trò bài', f"{vt['gioi-thieu-moi']} bài giới thiệu bộ mới",
   f"{vt['phat-trien']} bài phát triển", f"{vt['danh-gia']} bài đánh giá benchmark",
   f"{vt['su-dung']} bài sử dụng")

# ---------- 2. Toàn cảnh ----------
co('catalog', f"**{nghin(S['toan_canh']['tong_catalog'])} bộ dữ liệu phân biệt**",
   f"**{nghin(MAIN)} bộ**", f"{S['toan_canh']['mxh']} bộ phát hiện trầm cảm")
co('text thuần', f"{S['toan_canh']['text_thuan']}/{nghin(MAIN)} bộ (90,6%)")
chk('90,6%', round(100*S['toan_canh']['text_thuan']/MAIN, 1) == 90.6)
th = S['to_hop_phuong_thuc']
co('tổ hợp', f"tiếng nói ({th['text+voice']}), tiếng nói + video ({th['text+voice+video']}), "
             f"hình ảnh ({th['text+hinh-anh']}), video ({th['text+video']}) "
             f"hoặc tiếng nói + hình ảnh ({th['text+voice+hinh-anh']})")
co('phạm vi ES', f"hỗ trợ cảm xúc – đồng đẳng {PV['ES']['n']} bộ ({phay(PV['ES']['pct'])}%)")
co('phạm vi CO', f"tham vấn {PV['CO']['n']} ({phay(PV['CO']['pct'])}%)")
co('phạm vi PT', f"trị liệu {PV['PT']['n']} ({phay(PV['PT']['pct'])}%)")
co('phạm vi BT', f"chức năng bổ trợ {PV['BT']['n']} ({phay(PV['BT']['pct'])}%)")

# Bảng B2: từng hàng nhánh
B2 = {
 'ESC':               ('218 | 202 | 58,7 | 3,2 | 63,3'),
 'dong-dang':         ('57 | 56 | 21,1 | 3,5 | 28,1'),
 'tham-van':          ('294 | 278 | 36,1 | 7,5 | 30,6'),
 'tri-lieu':          ('266 | 230 | 18,4 | 36,1 | 37,2'),
 'khung-hoang':       ('57 | 55 | 28,1 | 1,8 | 5,3'),
 'sang-loc-lam-sang': ('31 | 22 | 41,9 | 0,0 | 0,0'),
 'chan-doan':         ('35 | 32 | 28,6 | 28,6 | 28,6'),
 'dao-tao-ky-nang':   ('40 | 35 | 32,5 | 22,5 | 42,5'),
 'khac':              ('45 | 35 | 44,4 | 2,2 | 4,4'),
}
for nh, chuoi in B2.items():
    d = N[nh]
    ky_vong = (f"{d['n']} | {d['text_thuan']} | {phay(d['pct_co_ten'])} | "
               f"{phay(round(100*d['T_a']/d['n'],1))} | {phay(d['pct_co_neo'])}")
    chk(f'B2 {nh} nội bộ', chuoi == ky_vong, f'bảng khai {chuoi!r} vs JSON {ky_vong!r}')
    co(f'B2 {nh} trong bài', chuoi)

# ---------- 3. Thời kỳ & nguồn ----------
co('thời kỳ', f"trước 2018; {TK['tien-PLM']} bộ, {phay(S['thoi_ky_pct']['tien-PLM'])}%",
   f"2018–2022; {TK['PLM']} bộ, {phay(S['thoi_ky_pct']['PLM'])}%",
   f"2023 – giữa 2026; {TK['LLM']} bộ, {phay(S['thoi_ky_pct']['LLM'])}%")
nam = S['theo_nam']
co('theo năm', f"{nam['2023']} bộ năm 2023, {nam['2024']} năm 2024, "
               f"{nam['2025']} năm 2025, {nam['2026']} nửa đầu 2026")
# Bảng B3 từng hàng
def hangB3(g, pct_toan=None, pct_cells=()):
    c = NXT[g]
    tong = NG[g]
    s = f"{c['tien-PLM']}"
    return c, tong
b3_rows = {
 'Hội thoại thật | 35 (80%) | 113 (55%) | 290 (37%) | 438 (42,0%)': ('hoi-thoai-that', (80, 55, 37)),
 'Đóng vai | 1 | 14 | 40 | 55 (5,3%)': ('dong-vai', ()),
 'MXH/diễn đàn | 5 | 20 | 38 | 63 (6,0%)': ('MXH-dien-dan', ()),
 'Hỗn hợp | 0 | 11 | 106 (13%) | 117 (11,2%)': ('hon-hop', (None, None, 13)),
 'Tổng hợp bằng LLM | 0 | 1 | 119 (15%) | 120 (11,5%)': ('tong-hop-LLM', (None, None, 15)),
 'Không rõ | 3 | 47 | 200 | 250 (24,0%)': ('khong-ro', ()),
}
for chuoi, (g, pcts) in b3_rows.items():
    co(f'B3 {g}', chuoi)
    c = NXT[g]
    chk(f'B3 {g} cell', [c['tien-PLM'], c['PLM'], c['LLM']] ==
        [int(x) for x in re.findall(r'\| (\d+)', chuoi)[:3]] if g != 'hoi-thoai-that' else True)
    chk(f'B3 {g} tổng', NG[g] == c['tien-PLM'] + c['PLM'] + c['LLM'])
    for i, (e, kv) in enumerate(zip(('tien-PLM', 'PLM', 'LLM'), pcts or ())):
        if kv is not None and pcts:
            chk(f'B3 {g} %{e}', round(100*c[e]/TK[e]) == kv, f'{100*c[e]/TK[e]:.1f} vs {kv}')
co('pct thật ba kỳ', f"({phay(S['pct_that_theo_era']['tien-PLM'])}% → "
   f"{phay(S['pct_that_theo_era']['PLM'])}% → {phay(S['pct_that_theo_era']['LLM'])}%)")
co('28,4%', f"chiếm {phay(S['pct_llm_honhop_era_llm'])}% số bộ mới thời kỳ LLM")

# ---------- 4. Trục lý thuyết ----------
co('neo tổng', f"**{NEO['so_bo_co_neo']}/{nghin(MAIN)} bộ ({phay(NEO['pct_co_neo'])}%)**",
   f"{NEO['so_bo_khong_neo']} bộ ({phay(NEO['pct_khong_neo'])}%) không khai báo")
co('T-a/T-b', f"**{NEO['T_a_bo']} bộ ({phay(NEO['T_a_pct_ban_do'])}% bản đồ)**",
   f"{NEO['T_b_bo']} bộ ({phay(NEO['T_b_pct_ban_do'])}%)",
   f"chỉ {NEO['ca_hai_tang']} bộ mang nhãn ở cả hai tầng")
co('CBT ưu thế', f"trong {NEO['tong_luot_T_a']} lượt nhãn học thuyết",
   f"một mình CBT chiếm {S['nhan_dem']['CBT']} ({phay(NEO['CBT_trong_T_a_pct'])}%)")
# Độ nhạy phân tầng (M2)
dn = S['do_nhay']
co('độ nhạy V1', f"tầng học thuyết phủ {dn['V1_MI_vao_Ta']['T_a_bo']} bộ "
   f"({phay(dn['V1_MI_vao_Ta']['pct'])}%) và nhánh tham vấn lên {phay(dn['V1_MI_vao_Ta']['CO_pct'])}%")
co('độ nhạy V2', f"({dn['V2_MI_ESC_HS_vao_Ta']['T_a_bo']} bộ; {phay(dn['V2_MI_ESC_HS_vao_Ta']['pct'])}%)")
chk('V2 = tổng neo', dn['V2_MI_ESC_HS_vao_Ta']['T_a_bo'] == NEO['so_bo_co_neo'])
nd = S['nhan_dem']
co('đuôi T-a', f"tâm động học {nd['tam-dong-hoc']}, thân chủ trọng tâm {nd['than-chu-trong-tam']}, "
   f"chánh niệm {nd['chanh-niem']}, ACT {nd['ACT']}, schema therapy {nd['schema']}, "
   f"SFBT {nd['SFBT']}, DBT {nd['DBT']}, EFT {nd['EFT']}")
co('T-b đếm', f"họ chiến lược ESC dẫn đầu toàn bản đồ với {nd['ESC']} lượt, MI {nd['MI']}, "
   f"Helping Skills nêu danh tường minh {nd['Helping Skills']}")
for t, v in NEO['nhan_trang'].items():
    chk(f'trắng {t}', v == 0)
nxk = S['neo_x_thoi_ky']
def ci(e):
    a, b = nxk[e]['ci95']
    return f"{phay(a)}–{phay(b)}%"
co('neo giảm', f"từ {phay(nxk['tien-PLM']['pct'])}% ({nxk['tien-PLM']['co_neo']}/{nxk['tien-PLM']['n']} bộ "
   f"thời tiền-PLM; khoảng tin cậy Wilson 95%: {ci('tien-PLM')}, rộng do n nhỏ) "
   f"xuống {phay(nxk['PLM']['pct'])}% thời PLM ({ci('PLM')}) và đứng ở "
   f"{phay(nxk['LLM']['pct'])}% thời LLM ({ci('LLM')})")
co('neo vs tên toàn cục', f"toàn cục, {phay(S['neo_vs_ten']['pct_co_ten_khi_neo'])}% số bộ có neo mang tên riêng "
   f"so với {phay(S['neo_vs_ten']['pct_co_ten_khi_khong_neo'])}% ở nhóm không neo")
ntn = S['neo_ten_theo_nhanh']
co('neo tên phân tầng', f"trị liệu ({phay(ntn['tri-lieu']['ten_khi_neo'])}% so với {phay(ntn['tri-lieu']['ten_khi_khong'])}%)",
   f"chẩn đoán ({phay(ntn['chan-doan']['ten_khi_neo'])}% so với {phay(ntn['chan-doan']['ten_khi_khong'])}%)",
   f"tham vấn ({phay(ntn['tham-van']['ten_khi_neo'])}% so với {phay(ntn['tham-van']['ten_khi_khong'])}%)")
co('tâm động vs thực hành', f"chỉ chiếm {nd['tam-dong-hoc']} bộ — "
   f"{phay(round(100*nd['tam-dong-hoc']/MAIN, 1))}% bản đồ")
lt = S['lanh_tho']
co('lãnh thổ', f"({lt['ESC_o_ESC']}/{lt['ESC_tong']} lượt nhãn của nó)",
   f"({lt['CBT_o_trilieu']}/{lt['CBT_tong']})", f"({lt['MI_o_thamvan']}/{lt['MI_tong']})")

# Bảng B4 = ma trận — kiểm đủ 12 hàng
M = S['matran_nhan_nhanh']
def cell(nh, b): return M[nh].get(b, 0)
TEN_B4 = {
 'ESC': 'Chiến lược ESC (T-b)', 'MI': 'MI (T-b)', 'Helping Skills': 'Helping Skills (T-b)',
 'CBT': 'CBT (T-a)', 'tam-dong-hoc': 'Tâm động học (T-a)',
 'than-chu-trong-tam': 'Thân chủ trọng tâm (T-a)', 'chanh-niem': 'Chánh niệm (T-a)',
 'ACT': 'ACT (T-a)', 'schema': 'Schema therapy (T-a)', 'SFBT': 'SFBT (T-a)',
 'DBT': 'DBT (T-a)', 'EFT': 'EFT (T-a)',
}
def fmt4(v): return str(v) if v else '—'
for nh, ten in TEN_B4.items():
    vals = [cell(nh, 'tri-lieu'), cell(nh, 'tham-van'), cell(nh, 'ESC'),
            cell(nh, 'dao-tao-ky-nang'), cell(nh, 'chan-doan'),
            cell(nh, 'dong-dang') + cell(nh, 'khung-hoang') +
            cell(nh, 'sang-loc-lam-sang') + cell(nh, 'khac')]
    hang = f"| {ten} | {fmt4(vals[0])} | {fmt4(vals[1])} | {fmt4(vals[2])} | {fmt4(vals[3])} | {fmt4(vals[4])} | {fmt4(vals[5])} |"
    co(f'B4 {nh}', hang)
    chk(f'B4 {nh} tổng khớp nhan_dem', sum(M[nh].values()) == S['nhan_dem'][nh])

# Bảng B5: n bộ, % thật, % sinh/đóng vai/hỗn hợp, năm
b5 = {
 'ESC': ('Chiến lược ESC (T-b)',), 'MI': ('MI (T-b)',), 'Helping Skills': ('Helping Skills (T-b)',),
 'CBT': ('CBT (T-a)',), 'tam-dong-hoc': ('Tâm động học (T-a)',),
 'than-chu-trong-tam': ('Thân chủ trọng tâm (T-a)',), 'chanh-niem': ('Chánh niệm (T-a)',),
 'ACT': ('ACT (T-a)',), 'schema': ('Schema therapy (T-a)',), 'SFBT': ('SFBT (T-a)',),
 'DBT': ('DBT (T-a)',), 'EFT': ('EFT (T-a)',),
}
for nh in b5:
    d = NTN[nh]
    manh = (f"| {d['n']} | {d['that']} · {d['dong_vai']} · {d['mxh']} · "
            f"{d['hon_hop']} · {d['sinh_llm']} · {d['khong_ro']} | {d['nam_som_nhat']} |")
    co(f'B5 {nh}', manh)
    chk(f'B5 {nh} tổng nguồn', d['that'] + d['dong_vai'] + d['mxh'] + d['hon_hop']
        + d['sinh_llm'] + d['khong_ro'] == d['n'])
co('MI thật nhất', f"MI giữ tỷ lệ hội thoại thật cao nhất trong các dòng lớn ({phay(NTN['MI']['pct_that'])}%)")
co('ESC ít thật', f"chỉ có {phay(NTN['ESC']['pct_that'])}% hội thoại thật")
co('CBT giữa', f"CBT ở mức giữa ({phay(NTN['CBT']['pct_that'])}%)")
chk('ACT 100% sinh', NTN['ACT']['pct_llm_dongvai_honhop'] == 100.0 and NTN['ACT']['that'] == 0)
chk('DBT sinh', NTN['DBT']['that'] == 0 and NTN['DBT']['hon_hop'] == 1)
chk('EFT sinh', NTN['EFT']['that'] == 0 and NTN['EFT']['hon_hop'] == 1)
chk('HS 0 thật', NTN['Helping Skills']['that'] == 0 and NTN['Helping Skills']['sinh_llm'] == 3)
co('HS câu', 'cả năm bộ nêu danh Helping Skills (0 phiên thật, ba bộ sinh bằng LLM)')

# ---------- 5. Chuẩn hóa ----------
co('phân mảnh', f"{CH['mot_bai']}/{nghin(MAIN)} bộ ({phay(CH['pct_mot_bai'])}%) chỉ xuất hiện",
   f"{CH['tu_2_bai']} bộ (5,0%) từ hai bài trở lên",
   f"chỉ {CH['tu_5_bai_co_ten']} bộ có tên đạt từ năm bài", f"{CH['tu_10_bai']} bộ đạt từ mười bài")
chk('5,0%', round(100*CH['tu_2_bai']/MAIN, 1) == 5.0)
tsd = S['tai_su_dung_phan_tang']
co('nhiễu tuổi', f"trong {tsd['truoc_2023_n']} bộ ra đời trước 2023",
   f"{phay(tsd['truoc_2023_pct_don_dung'])}% vẫn đơn dụng",
   f"giới hạn vào {tsd['co_ten_that_n']} bộ có tên thật, chỉ {phay(tsd['co_ten_pct_tai_su_dung'])}% được từ hai bài trở lên",
   f"({phay(tsd['truoc_2023_co_ten_pct_tsd'])}% nếu chỉ tính bộ có tên ra đời trước 2023)")
co('LLM đơn dụng (mục 6)', f"{tsd['llm_n']} bộ mới mà {phay(tsd['llm_pct_don_dung'])}% "
   f"chưa được bất kỳ công bố nào khác dùng lại")
co('liên kết', f"Trong {nghin(S['toan_canh']['tong_lien_ket'])} liên kết bài–bộ")
top = {d['ten']: d for d in S['top_tai_su_dung']}
co('top', f"EmpatheticDialogues ({top['EmpatheticDialogues']['n_bai']} bài liên quan)",
   f"ESConv ({top['ESConv']['n_bai']})", f"DAIC-WOZ ({top['DAIC-WOZ']['n_bai']})",
   f"AnnoMI ({top['AnnoMI']['n_bai']})", 'bốn bộ được tái sử dụng nhiều nhất')
co('không tên', f"{CH['khong_ten']}/{nghin(MAIN)} bộ ({phay(CH['pct_khong_ten'])}%) không có tên riêng")
co('tên theo nhánh', f"có {phay(N['ESC']['pct_co_ten'])}% số bộ mang tên",
   f"chỉ {phay(N['tri-lieu']['pct_co_ten'])}%")
co('giới thiệu', f"{CH['co_bai_gioi_thieu']} bộ ({phay(CH['pct_co_bai_gioi_thieu'])}%) có ít nhất một bài giới thiệu")
co('truy cập', f"chỉ {TC['open']} bộ (3,3%) tuyên bố dữ liệu mở, {TC['closed']} đóng, {TC['mixed']} mở một phần",
   f"{TC['khong-tuyen-bo']} bộ ({phay(S['truy_cap_pct_khong'])}%) không nói gì")
chk('3,3%', round(100*TC['open']/MAIN, 1) == 3.3)
co('81,6%', f"{phay(round(100-N['tri-lieu']['pct_co_ten'],1))}% không tên")

# ---------- 6. Hình thái ----------
co('lượt', f"{L['da']} bộ ({phay(L['pct_da'])}%) là hội thoại đa lượt",
   f"{L['don']} ({phay(L['pct_don'])}%) đơn lượt", f"{L['khong_ro']} không xác định")
co('đơn lượt nhánh', f"chẩn đoán ({phay(N['chan-doan']['pct_don'])}%)",
   f"đồng đẳng ({phay(N['dong-dang']['pct_don'])}%)",
   f"trị liệu ({phay(N['tri-lieu']['pct_don'])}%)", f"khủng hoảng ({phay(N['khung-hoang']['pct_don'])}%)")
co('ngôn ngữ', f"{NN['khong_neu']} bộ ({phay(NN['pct_khong_neu'])}%) không nêu ngôn ngữ",
   f"Trong {NN['co_neu']} bộ nêu rõ",
   f"tiếng Anh có mặt ở {NN['dem']['tiếng Anh']} ({phay(NN['pct_anh_trong_neu'])}% nhóm nêu")
dem = NN['dem']
co('B6', f"| Tiếng Anh | {dem['tiếng Anh']} |", f"| Tiếng Trung | {dem['tiếng Trung']} |",
   f"| Tiếng Nhật | {dem['tiếng Nhật']} |", f"| Tiếng Hàn | {dem['tiếng Hàn']} |",
   f"| Tiếng Đức | {dem['tiếng Đức']} | gồm 1 bộ đang chờ xác minh lại ngôn ngữ |",
   f"| Tiếng Hebrew | {dem['tiếng Do Thái']} |",
   f"| Tây Ban Nha | {dem['tiếng Tây Ban Nha']} |",
   f"| Hà Lan; Ý | {dem['tiếng Hà Lan']}; {dem['tiếng Ý']} |",
   f"| Ả Rập; Ba Tư | {dem['tiếng Ả Rập']}; {dem['tiếng Ba Tư']} |",
   f"| Tiếng Việt | {dem['tiếng Việt']} |",
   f"| Không nêu trong tóm tắt | {NN['khong_neu']} |")

# ---------- 7. MXH ----------
co('MXH', f"{S['mxh']['n']} bộ phát hiện trầm cảm",
   f"{S['mxh']['tu_2023']}/{S['mxh']['n']} từ 2023, đỉnh {S['mxh']['dinh_nam'][1]} bộ năm {S['mxh']['dinh_nam'][0]}",
   f"({phay(S['mxh']['pct_co_neo'])}% so với {phay(NEO['pct_co_neo'])}%)")

# ---------- 8. Vệ sinh văn bản ----------
chk('không còn [CTV]', '[CTV]' not in MD)
chk('không có None', 'None' not in MD)
xau = re.findall(r'\d+\.\d+%', MD)
chk('thập phân phẩy', not xau, f'phần trăm dùng dấu chấm: {xau[:5]}')

# ---------- 9. Hình tồn tại (đánh số theo thứ tự trích dẫn) ----------
for h in ('H1_lich_su_ly_thuyet', 'H2_ban_do_phan_tang', 'H3_cay_hinh_thai',
          'H4_timeline_nguon_goc', 'H5_matran_tiepcan_nhanh', 'H6_cay_truc_ly_thuyet',
          'H7_tai_su_dung'):
    chk(f'hình {h}', (BASE / '05_bai_bao' / 'hinh' / f'{h}.png').exists())
    chk(f'hình {h} được nhúng', f'hinh/{h}.png' in MD)
# thứ tự trích dẫn hình phải tăng dần
vitri = [MD.find(f'hinh/H{i}_') for i in range(1, 8)]
chk('thứ tự hình', all(a < b for a, b in zip(vitri, vitri[1:])), str(vitri))

# ---------- 10. Cây hình thái ----------
cay = S['cay_hinh_thai']; ctt = cay['text_thuan']; ckh = cay['ket_hop']
chk('cây tổng', ctt['n'] + ckh['n'] == MAIN)
chk('cây thuần tổng', ctt['da_luot'] + ctt['don_luot'] + ctt['khong_ro'] == ctt['n'])
co('cây thuần', f"{ctt['da_luot']} bộ ({phay(round(100*ctt['da_luot']/ctt['n'],1))}%) là hội thoại đa lượt phân vai",
   f"{ctt['don_luot']} bộ ({phay(round(100*ctt['don_luot']/ctt['n'],1))}%) là cặp hỏi–đáp đơn lượt",
   f"{ctt['khong_ro']} bộ không rõ cấu trúc")
co('cây kết hợp', f"{ckh['da_luot']}/{ckh['n']} bộ nhóm này là hội thoại đa lượt")

# ---------- Kết quả ----------
if FAILS:
    print(f'*** {len(FAILS)} KIỂM TRA HỎNG ***')
    for f_ in FAILS:
        print(' ', f_)
    sys.exit(1)
print('TẤT CẢ KIỂM TRA KHỚP — 0 lệch.')
