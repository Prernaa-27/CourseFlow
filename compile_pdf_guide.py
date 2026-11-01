# compile_pdf_guide.py
import os
import re
import html
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Omit header and footer on cover page if page == 1
        if self._pageNumber > 1:
            # Running Header
            self.drawString(40, 760, "CourseFlow (CFMS) — Complete Technical Understanding & Viva Guide")
            self.drawRightString(572, 760, "Software Engineering (CS301)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 754, 572, 754)
            
            # Running Footer
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(572, 30, page_text)
            self.drawString(40, 30, "Academic Year 2024–2025 | Outcome-Based Education (NBA / NAAC)")
            self.line(40, 40, 572, 40)
            
        self.restoreState()

def clean_inline_md(text):
    # Escape HTML first
    text = html.escape(text)
    # Code `code` first so asterisks inside code are not converted
    text = re.sub(r'`([^`]+?)`', r'<font face="Courier" size="7.5"><b>\1</b></font>', text)
    # Bold **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic *text* only if not standalone multiplication symbol
    text = re.sub(r'(?<!\*)\*([a-zA-Z0-9].*?[a-zA-Z0-9])\*(?!\*)', r'<i>\1</i>', text)
    return text

def safe_paragraph(text, style):
    try:
        return Paragraph(text, style)
    except Exception:
        plain = re.sub(r'<[^>]+>', '', text)
        return Paragraph(plain, style)

def parse_and_build_pdf(md_path, pdf_path):
    print(f"Reading {md_path} and compiling {pdf_path}...")
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#4338CA'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Heading3_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#4338CA'),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F8FAFC'),
        borderColor=colors.HexColor('#E2E8F0'),
        borderWidth=0.5,
        borderPadding=4,
        spaceBefore=4,
        spaceAfter=6
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1E293B')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white
    )

    story = []
    
    in_code_block = False
    code_lines = []
    
    in_table = False
    table_raw_rows = []

    def flush_table():
        nonlocal in_table, table_raw_rows
        if not table_raw_rows:
            in_table = False
            return
        
        # Process rows
        headers = table_raw_rows[0]
        data_rows = table_raw_rows[1:]
        
        # Filter separator row if present
        if data_rows and re.match(r'^[\s\-\|\:]+$', ''.join(data_rows[0])):
            data_rows = data_rows[1:]

        num_cols = len(headers)
        if num_cols == 0:
            in_table = False
            table_raw_rows = []
            return

        # Width calculation
        total_width = 532 # 612 - 80 margin
        col_width = total_width / num_cols
        col_widths = [col_width] * num_cols

        # Custom widths for certain common tables
        if num_cols == 8: # Test cases table
            col_widths = [45, 45, 75, 75, 85, 45, 45, 117]
        elif num_cols == 4:
            col_widths = [75, 120, 140, 197]
        elif num_cols == 2:
            col_widths = [160, 372]

        formatted_table_data = []
        
        # Header row
        header_cells = [safe_paragraph(clean_inline_md(c.strip()), table_header_style) for c in headers]
        formatted_table_data.append(header_cells)

        # Data rows
        for row in data_rows:
            # Pad row if uneven
            while len(row) < num_cols:
                row.append("")
            row = row[:num_cols]
            cells = [safe_paragraph(clean_inline_md(c.strip()), table_cell_style) for c in row]
            formatted_table_data.append(cells)

        t = Table(formatted_table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))

        story.append(Spacer(1, 4))
        story.append(t)
        story.append(Spacer(1, 6))

        in_table = False
        table_raw_rows = []

    def flush_code():
        nonlocal in_code_block, code_lines
        if code_lines:
            code_text = html.escape("".join(code_lines))
            story.append(safe_paragraph(f"<font face='Courier' size='7'>{code_text.replace(chr(10), '<br/>')}</font>", code_style))
            story.append(Spacer(1, 4))
        in_code_block = False
        code_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Handle code blocks
        if stripped.startswith("```"):
            if in_code_block:
                flush_code()
            else:
                if in_table: flush_table()
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Handle table rows
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                in_table = True
                table_raw_rows = []
            cells = [c for c in stripped.split("|")[1:-1]]
            table_raw_rows.append(cells)
            i += 1
            continue
        elif in_table:
            flush_table()

        # Blank line
        if not stripped:
            i += 1
            continue

        # Horizontal Rule
        if stripped == "---":
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceBefore=4, spaceAfter=8))
            i += 1
            continue

        # Headings
        if stripped.startswith("# "):
            title_text = clean_inline_md(stripped[2:])
            if i < 5: # Document main title
                story.append(safe_paragraph(title_text, title_style))
            else:
                story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#4338CA'), spaceBefore=10, spaceAfter=8))
                story.append(safe_paragraph(title_text, h1_style))
            i += 1
            continue

        if stripped.startswith("## "):
            sub_text = clean_inline_md(stripped[3:])
            if i < 8:
                story.append(safe_paragraph(sub_text, subtitle_style))
            else:
                story.append(safe_paragraph(sub_text, h2_style))
            i += 1
            continue

        if stripped.startswith("### "):
            h3_text = clean_inline_md(stripped[4:])
            story.append(safe_paragraph(h3_text, h3_style))
            i += 1
            continue

        if stripped.startswith("#### "):
            h4_text = clean_inline_md(stripped[5:])
            story.append(safe_paragraph(f"<b>{h4_text}</b>", h3_style))
            i += 1
            continue

        # Bullet lists
        if stripped.startswith("- ") or stripped.startswith("* "):
            bullet_text = clean_inline_md(stripped[2:])
            story.append(safe_paragraph(f"&bull;&nbsp; {bullet_text}", bullet_style))
            i += 1
            continue

        # Numbered lists (e.g. 1. , 2. )
        num_match = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if num_match:
            num = num_match.group(1)
            item_text = clean_inline_md(num_match.group(2))
            story.append(safe_paragraph(f"<b>{num}.</b>&nbsp; {item_text}", bullet_style))
            i += 1
            continue

        # Regular Body Paragraph
        p_text = clean_inline_md(stripped)
        story.append(safe_paragraph(p_text, body_style))
        i += 1

    if in_table:
        flush_table()
    if in_code_block:
        flush_code()

    print(f"Building PDF document with {len(story)} flowable elements...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated {pdf_path} successfully ({os.path.getsize(pdf_path)} bytes).")

if __name__ == "__main__":
    parse_and_build_pdf("COURSEFLOW_COMPLETE_PROJECT_GUIDE.md", "COURSEFLOW_COMPLETE_PROJECT_GUIDE.pdf")
