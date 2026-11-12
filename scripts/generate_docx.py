"""
Script: scripts/generate_docx.py
Description: Converts Project_2_Report.md into a beautifully formatted Word Document (Project_2_Report.docx)
with styled headings, tables, callout blocks, and embedded figures.
"""

import os
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_PATH = os.path.join(BASE_DIR, "Project_2_Report.md")
DOCX_PATH = os.path.join(BASE_DIR, "Project_2_Report.docx")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

doc = Document()

# Set standard 1-inch margins
for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

# Color constants
C_NAVY = RGBColor(15, 23, 42)
C_BLUE = RGBColor(30, 64, 175)
C_GRAY = RGBColor(71, 85, 105)

def style_heading(p, font_size, color, bold=True):
    for r in p.runs:
        r.font.size = Pt(font_size)
        r.font.color.rgb = color
        r.font.bold = bold
        r.font.name = 'Calibri'

with open(MD_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_table = False
table_lines = []
in_code = False
code_lines = []

def process_table(t_lines):
    rows = [l.strip().strip('|').split('|') for l in t_lines if not re.match(r'^[|\s\-:]+$', l.strip())]
    if not rows: return
    num_rows = len(rows)
    num_cols = len(rows[0])
    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    for r_idx, row_data in enumerate(rows):
        for c_idx, cell_data in enumerate(row_data):
            if c_idx < num_cols:
                cell = table.cell(r_idx, c_idx)
                txt = cell_data.strip()
                cell.text = txt
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                
                # Header formatting
                if r_idx == 0:
                    shading = parse_xml(r'<w:shd {} w:fill="0F172A"/>'.format(nsdecls('w')))
                    cell._tc.get_or_add_tcPr().append(shading)
                    for r in p.runs:
                        r.font.bold = True
                        r.font.color.rgb = RGBColor(255, 255, 255)
                        r.font.size = Pt(9.5)
                else:
                    if r_idx % 2 == 0:
                        shading = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
                        cell._tc.get_or_add_tcPr().append(shading)
                    for r in p.runs:
                        r.font.size = Pt(9)
                        r.font.color.rgb = C_NAVY
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

for line in lines:
    raw = line.rstrip('\n')
    
    # Handle Code Blocks
    if raw.startswith('```'):
        if in_code:
            # End code block
            p = doc.add_paragraph('\n'.join(code_lines))
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            for r in p.runs:
                r.font.name = 'Consolas'
                r.font.size = Pt(8.5)
                r.font.color.rgb = C_NAVY
            in_code = False
            code_lines = []
        else:
            in_code = True
            code_lines = []
        continue
        
    if in_code:
        code_lines.append(raw)
        continue

    # Handle Markdown Tables
    if '|' in raw and not raw.startswith('```'):
        in_table = True
        table_lines.append(raw)
        continue
    else:
        if in_table:
            process_table(table_lines)
            in_table = False
            table_lines = []

    # Handle Images
    img_match = re.search(r'!\[.*?\]\((.*?)\)', raw)
    if img_match:
        img_src = img_match.group(1).replace('file:///', '').replace('/', os.sep)
        if not os.path.isabs(img_src):
            img_src = os.path.join(BASE_DIR, img_src)
        if os.path.exists(img_src):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(8)
            doc.add_picture(img_src, width=Inches(6.2))
        continue

    # Headings
    if raw.startswith('# '):
        p = doc.add_heading(raw[2:], level=1)
        style_heading(p, 20, C_NAVY)
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
    elif raw.startswith('## '):
        p = doc.add_heading(raw[3:], level=2)
        style_heading(p, 15, C_BLUE)
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
    elif raw.startswith('### '):
        p = doc.add_heading(raw[4:], level=3)
        style_heading(p, 12, C_NAVY)
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
    elif raw.startswith('#### '):
        p = doc.add_heading(raw[5:], level=4)
        style_heading(p, 11, C_GRAY)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
    elif raw.startswith('---'):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
    elif raw.startswith('- ') or raw.startswith('* '):
        p = doc.add_paragraph(raw[2:], style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        for r in p.runs:
            r.font.size = Pt(10)
    elif re.match(r'^\d+\.\s', raw):
        text = re.sub(r'^\d+\.\s', '', raw)
        p = doc.add_paragraph(text, style='List Number')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        for r in p.runs:
            r.font.size = Pt(10)
    else:
        txt = raw.strip()
        if txt:
            p = doc.add_paragraph(txt)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            for r in p.runs:
                r.font.size = Pt(10)

if in_table:
    process_table(table_lines)

doc.save(DOCX_PATH)
print(f"[SUCCESS] Generated Word Document at:\n  {DOCX_PATH}")
