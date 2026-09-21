# -*- coding: utf-8 -*-
"""p_v53_docx.py — Chuyển bai_bao_1_survey_v53.md thành .docx (Times New Roman 12, A4).
Phỏng theo md2docx.py của dự án, thêm heading cấp 4 và cỡ chữ theo PROMPT."""
import os, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r'H:\Vy\Paper\Empathy\Report\_Chuan_bi\_analyst_v7\wave3_nlp_tham_van\05_bai_bao'
MD = os.path.join(BASE, 'bai_bao_1_survey_v53.md')
DOCX = os.path.join(BASE, 'bai_bao_1_survey_v53.docx')

INLINE_RE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)")

def add_runs(par, text, base_bold=False, size=None):
    for tok in INLINE_RE.split(text):
        if not tok:
            continue
        bold = base_bold; italic = False; code = False
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            bold = True; tok = tok[2:-2]
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            italic = True; tok = tok[1:-1]
        elif tok.startswith("`") and tok.endswith("`") and len(tok) > 2:
            code = True; tok = tok[1:-1]
        run = par.add_run(tok)
        run.bold = bold; run.italic = italic
        if code:
            run.font.name = "Consolas"
            rpr = run._element.get_or_add_rPr()
            rf = rpr.find(qn("w:rFonts"))
            if rf is None:
                rf = OxmlElement("w:rFonts"); rpr.append(rf)
            rf.set(qn("w:ascii"), "Consolas"); rf.set(qn("w:hAnsi"), "Consolas")
            run.font.size = Pt((size or 12) - 1)
        if size:
            run.font.size = Pt(size)

def set_cell_shading(cell, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(shd)

def style_setup(doc):
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"; st.font.size = Pt(12)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    st.paragraph_format.space_after = Pt(5)
    st.paragraph_format.line_spacing = 1.2
    for name, sz in [("Heading 1", 16), ("Heading 2", 13.5), ("Heading 3", 12.5), ("Heading 4", 12)]:
        h = doc.styles[name]
        h.font.name = "Times New Roman"; h.font.size = Pt(sz)
        h.font.bold = True; h.font.color.rgb = RGBColor(0, 0, 0)
        if h.element.rPr is not None and h.element.rPr.rFonts is not None:
            h.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    for sec in doc.sections:
        # A4 mặc định của python-docx; đặt lề
        sec.left_margin = Cm(2.5); sec.right_margin = Cm(2.0)
        sec.top_margin = Cm(2.2); sec.bottom_margin = Cm(2.2)

def parse_table_block(lines, i):
    rows = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        raw = lines[i].strip().strip("|")
        cells = [c.strip() for c in raw.split("|")]
        if not re.fullmatch(r"[\s:\-|]+", lines[i].strip()):
            rows.append(cells)
        i += 1
    return rows, i

def add_table(doc, rows):
    ncols = max(len(r) for r in rows)
    tsize = 10 if ncols <= 6 else (9 if ncols <= 8 else 8)
    table = doc.add_table(rows=len(rows), cols=ncols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    for ri, row in enumerate(rows):
        for ci in range(ncols):
            cell = table.cell(ri, ci)
            txt = row[ci] if ci < len(row) else ""
            par = cell.paragraphs[0]
            par.paragraph_format.space_after = Pt(1)
            add_runs(par, txt, base_bold=(ri == 0), size=tsize)
            if ri == 0:
                set_cell_shading(cell, "E8E8E8")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def convert(md_path, docx_path):
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    doc = Document()
    style_setup(doc)
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1; continue
        if s.startswith("|"):
            rows, i = parse_table_block(lines, i)
            if rows:
                add_table(doc, rows)
            continue
        mimg = re.match(r"^!\[(.*?)\]\((.*?)\)$", s)
        if mimg:
            rel = mimg.group(2)
            ipath = os.path.normpath(os.path.join(os.path.dirname(md_path), rel))
            if os.path.exists(ipath):
                doc.add_picture(ipath, width=Cm(16.0))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p = doc.add_paragraph(); add_runs(p, f"[THIẾU HÌNH: {rel}]")
            i += 1; continue
        if s.startswith("#### "):
            p = doc.add_paragraph(style="Heading 4"); add_runs(p, s[5:])
        elif s.startswith("### "):
            p = doc.add_paragraph(style="Heading 3"); add_runs(p, s[4:])
        elif s.startswith("## "):
            p = doc.add_paragraph(style="Heading 2"); add_runs(p, s[3:])
        elif s.startswith("# "):
            p = doc.add_paragraph(style="Heading 1"); add_runs(p, s[2:])
        elif re.match(r"^[-*] ", s):
            p = doc.add_paragraph(style="List Bullet"); add_runs(p, s[2:])
            p.paragraph_format.space_after = Pt(2)
        elif re.match(r"^\d+\.\s", s):
            m = re.match(r"^(\d+)\.\s+(.*)$", s)
            p = doc.add_paragraph(style="List Number"); add_runs(p, m.group(2))
            p.paragraph_format.space_after = Pt(2)
        elif s in ("---", "***", "___"):
            pass
        else:
            p = doc.add_paragraph(); add_runs(p, s)
        i += 1
    doc.save(docx_path)
    print("OK", docx_path)

convert(MD, DOCX)
