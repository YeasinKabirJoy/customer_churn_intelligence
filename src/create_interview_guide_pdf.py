"""Create a polished PDF from the complete Markdown interview guide."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "complete_interview_guide.md"
OUTPUT_DIR = ROOT / "output" / "pdf"
OUTPUT = OUTPUT_DIR / "Telecom_Customer_Churn_Interview_Guide.pdf"

NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#138A8A")
ORANGE = colors.HexColor("#E28A2B")
PALE = colors.HexColor("#EDF4F7")
GRAY = colors.HexColor("#637381")
LIGHT_BORDER = colors.HexColor("#D8E3E9")


def register_fonts() -> tuple[str, str, str]:
    font_dir = Path("C:/Windows/Fonts")
    candidates = [
        ("Arial", "arial.ttf", "Arial-Bold", "arialbd.ttf", "Consolas", "consola.ttf"),
        ("DejaVu", "DejaVuSans.ttf", "DejaVu-Bold", "DejaVuSans-Bold.ttf", "DejaVuMono", "DejaVuSansMono.ttf"),
    ]
    for regular_name, regular_file, bold_name, bold_file, mono_name, mono_file in candidates:
        if all((font_dir / f).exists() for f in (regular_file, bold_file, mono_file)):
            pdfmetrics.registerFont(TTFont(regular_name, font_dir / regular_file))
            pdfmetrics.registerFont(TTFont(bold_name, font_dir / bold_file))
            pdfmetrics.registerFont(TTFont(mono_name, font_dir / mono_file))
            pdfmetrics.registerFontFamily(regular_name, normal=regular_name, bold=bold_name)
            return regular_name, bold_name, mono_name
    return "Helvetica", "Helvetica-Bold", "Courier"


BODY_FONT, BOLD_FONT, MONO_FONT = register_fonts()


def ascii_punctuation(text: str) -> str:
    replacements = {
        "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-",
        "\u2212": "-", "\u00d7": "x", "\u2192": "->", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u00a0": " ",
    }
    return "".join(replacements.get(char, char) for char in text)


def inline_markup(text: str) -> str:
    text = html.escape(ascii_punctuation(text.strip()))
    text = re.sub(r"`([^`]+)`", r'<font name="%s" color="#17324D">\1</font>' % MONO_FONT, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    return text


def make_styles():
    sample = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("Title", fontName=BOLD_FONT, fontSize=27, leading=32, textColor=NAVY, alignment=TA_CENTER, spaceAfter=12),
        "subtitle": ParagraphStyle("Subtitle", fontName=BODY_FONT, fontSize=12, leading=17, textColor=GRAY, alignment=TA_CENTER),
        "h1": ParagraphStyle("H1", fontName=BOLD_FONT, fontSize=18, leading=23, textColor=NAVY, spaceBefore=14, spaceAfter=8, keepWithNext=True),
        "h2": ParagraphStyle("H2", fontName=BOLD_FONT, fontSize=14, leading=18, textColor=TEAL, spaceBefore=12, spaceAfter=6, keepWithNext=True),
        "h3": ParagraphStyle("H3", fontName=BOLD_FONT, fontSize=11.2, leading=14.5, textColor=NAVY, spaceBefore=9, spaceAfter=4, keepWithNext=True),
        "body": ParagraphStyle("Body", parent=sample["BodyText"], fontName=BODY_FONT, fontSize=9.25, leading=13.2, textColor=colors.HexColor("#263746"), spaceAfter=6, allowWidows=0, allowOrphans=0),
        "bullet": ParagraphStyle("Bullet", fontName=BODY_FONT, fontSize=9.1, leading=12.6, textColor=colors.HexColor("#263746"), leftIndent=13, firstLineIndent=0, spaceAfter=2),
        "code": ParagraphStyle("Code", fontName=MONO_FONT, fontSize=7.3, leading=10.2, textColor=colors.HexColor("#183147"), backColor=colors.HexColor("#F4F7F9"), borderColor=LIGHT_BORDER, borderWidth=.6, borderPadding=7, leftIndent=2, rightIndent=2, spaceBefore=3, spaceAfter=7),
        "quote": ParagraphStyle("Quote", fontName=BODY_FONT, fontSize=9.2, leading=13, textColor=NAVY, leftIndent=12, rightIndent=8, borderColor=ORANGE, borderWidth=0, borderLeftWidth=3, borderPadding=7, backColor=colors.HexColor("#FFF7ED"), spaceAfter=7),
        "small": ParagraphStyle("Small", fontName=BODY_FONT, fontSize=8, leading=10.5, textColor=GRAY),
        "toc": ParagraphStyle("TOC", fontName=BOLD_FONT, fontSize=20, leading=24, textColor=NAVY, spaceAfter=14),
    }
    return styles


STYLES = make_styles()


class InterviewDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(filename, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=19 * mm, bottomMargin=18 * mm, title="Telecom Customer Churn Intelligence - Complete Interview Guide", author="Telecom Customer Churn Intelligence Project")
        body_frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates([
            PageTemplate(id="cover", frames=body_frame, onPage=self.cover_page),
            PageTemplate(id="content", frames=body_frame, onPage=self.content_page),
        ])

    def cover_page(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, A4[1] - 34 * mm, A4[0], 34 * mm, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, 0, A4[0], 7 * mm, fill=1, stroke=0)
        canvas.restoreState()

    def content_page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LIGHT_BORDER)
        canvas.setLineWidth(.5)
        canvas.line(18 * mm, A4[1] - 13 * mm, A4[0] - 18 * mm, A4[1] - 13 * mm)
        canvas.setFont(BODY_FONT, 7.5)
        canvas.setFillColor(GRAY)
        canvas.drawString(18 * mm, A4[1] - 10 * mm, "Telecom Customer Churn Intelligence - Interview Guide")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            level = getattr(flowable, "_toc_level", None)
            if level is not None:
                text = flowable.getPlainText()
                key = f"heading-{self.seq.nextf('heading')}"
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=level, closed=False)
                self.notify("TOCEntry", (level, text, self.page, key))


def table_from_lines(lines: list[str]):
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return Spacer(1, 1)
    count = max(len(row) for row in rows)
    normalized = [row + [""] * (count - len(row)) for row in rows]
    data = [[Paragraph(inline_markup(cell), STYLES["small"]) for cell in row] for row in normalized]
    widths = [170 * mm / count] * count
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("GRID", (0, 0), (-1, -1), .4, LIGHT_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def parse_markdown(markdown_text: str):
    lines = markdown_text.splitlines()
    story = []
    index = 0
    list_buffer: list[tuple[str, str]] = []

    def flush_list():
        nonlocal list_buffer
        if not list_buffer:
            return
        ordered = all(kind == "number" for kind, _ in list_buffer)
        for position, (_, text) in enumerate(list_buffer, start=1):
            prefix = f"{position}." if ordered else "•"
            story.append(Paragraph(f"{prefix}&nbsp;&nbsp;{inline_markup(text)}", STYLES["bullet"]))
        story.append(Spacer(1, 4))
        list_buffer = []

    while index < len(lines):
        raw = lines[index]
        line = raw.rstrip()
        if line.startswith("```"):
            flush_list()
            code_lines = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                code_lines.append(ascii_punctuation(lines[index]))
                index += 1
            story.append(Preformatted("\n".join(code_lines), STYLES["code"], maxLineLength=105))
        elif line.startswith("|") and index + 1 < len(lines) and lines[index + 1].startswith("|"):
            flush_list()
            table_lines = []
            while index < len(lines) and lines[index].startswith("|"):
                table_lines.append(lines[index])
                index += 1
            index -= 1
            story.append(table_from_lines(table_lines))
            story.append(Spacer(1, 6))
        elif line.startswith("# "):
            flush_list()
            p = Paragraph(inline_markup(line[2:]), STYLES["h1"]); p._toc_level = 0; story.append(p)
        elif line.startswith("## "):
            flush_list()
            p = Paragraph(inline_markup(line[3:]), STYLES["h2"]); p._toc_level = 0; story.append(p)
        elif line.startswith("### "):
            flush_list()
            p = Paragraph(inline_markup(line[4:]), STYLES["h3"]); p._toc_level = 1; story.append(p)
        elif line.startswith("> "):
            flush_list(); story.append(Paragraph(inline_markup(line[2:]), STYLES["quote"]))
        elif re.match(r"^\s*-\s+", line):
            list_buffer.append(("bullet", re.sub(r"^\s*-\s+", "", line)))
        elif re.match(r"^\s*\d+\.\s+", line):
            list_buffer.append(("number", re.sub(r"^\s*\d+\.\s+", "", line)))
        elif line.strip() in {"---", ""}:
            flush_list()
            if line.strip() == "---":
                story.append(Spacer(1, 5))
        else:
            flush_list(); story.append(Paragraph(inline_markup(line), STYLES["body"]))
        index += 1
    flush_list()
    return story


def build_pdf() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    markdown_text = SOURCE.read_text(encoding="utf-8")
    document = InterviewDocTemplate(str(OUTPUT))
    story = [
        Spacer(1, 42 * mm),
        Paragraph("Telecom Customer Churn Intelligence", STYLES["title"]),
        Paragraph("Complete Beginner-to-Intermediate Interview Guide", STYLES["subtitle"]),
        Spacer(1, 11 * mm),
        Table([[Paragraph("155 interview questions", STYLES["body"]), Paragraph("40 SQL and Python exercises", STYLES["body"])], [Paragraph("15-day study plan", STYLES["body"]), Paragraph("Project-specific speaking scripts", STYLES["body"])]], colWidths=[75 * mm, 75 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE), ("BOX", (0, 0), (-1, -1), .7, LIGHT_BORDER), ("INNERGRID", (0, 0), (-1, -1), .4, LIGHT_BORDER), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)])),
        Spacer(1, 18 * mm),
        Paragraph("Prepared from the complete project interview guide", STYLES["subtitle"]),
        NextPageTemplate("content"),
        PageBreak(),
        Paragraph("Table of Contents", STYLES["toc"]),
    ]
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle("TOC0", fontName=BOLD_FONT, fontSize=10, leading=14, textColor=NAVY, leftIndent=0, firstLineIndent=0, spaceBefore=4),
        ParagraphStyle("TOC1", fontName=BODY_FONT, fontSize=8.2, leading=11, textColor=GRAY, leftIndent=10, firstLineIndent=0),
    ]
    story.extend([toc, PageBreak()])
    parsed = parse_markdown(markdown_text)
    if parsed and isinstance(parsed[0], Paragraph) and parsed[0].getPlainText().startswith("Complete Beginner"):
        parsed = parsed[1:]
    story.extend(parsed)
    document.multiBuild(story)
    print(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    build_pdf()

