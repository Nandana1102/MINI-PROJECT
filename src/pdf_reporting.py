from __future__ import annotations

from functools import lru_cache
from html import escape
from io import BytesIO
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .translations import t


RowItems = Sequence[Tuple[str, str]]


@lru_cache(maxsize=8)
def _font_names_for_language(language: str) -> tuple[str, str, str]:
    if language != "hi":
        return ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique")

    candidates = [
        Path("C:/Windows/Fonts/Nirmala.ttc"),
        Path("C:/Windows/Fonts/Mangal.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"),
        Path("/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf"),
        Path("/usr/share/fonts/truetype/freefont/FreeSans.ttf"),
    ]

    for font_path in candidates:
        if not font_path.exists():
            continue
        font_name = f"LocalizedFont_{font_path.stem.replace(' ', '_')}"
        try:
            if font_name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
            return (font_name, font_name, font_name)
        except Exception:
            continue

    return ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique")


def _build_styles(language: str) -> tuple[ParagraphStyle, ParagraphStyle, ParagraphStyle, ParagraphStyle]:
    styles = getSampleStyleSheet()
    regular_font, bold_font, italic_font = _font_names_for_language(language)

    title_style = styles["Title"].clone(f"Title_{language}")
    title_style.fontName = bold_font

    heading_style = styles["Heading2"].clone(f"Heading_{language}")
    heading_style.fontName = bold_font

    body_style = styles["BodyText"].clone(f"Body_{language}")
    body_style.fontName = regular_font
    body_style.leading = 15

    italic_style = styles["Italic"].clone(f"Italic_{language}")
    italic_style.fontName = italic_font
    italic_style.leading = 15

    return title_style, heading_style, body_style, italic_style


def _paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    safe_text = escape(str(text)).replace("\n", "<br/>")
    return Paragraph(safe_text, style)


def _build_table(rows: RowItems, language: str):
    regular_font, bold_font, _ = _font_names_for_language(language)
    table_data = [[t("table_field", language), t("table_value", language)], *[[str(key), str(value)] for key, value in rows]]
    table = Table(table_data, colWidths=[2.2 * inch, 4.0 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), bold_font),
                ("FONTNAME", (0, 1), (-1, -1), regular_font),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def build_pdf_report_bytes(
    input_rows: RowItems,
    output_rows: RowItems,
    recommendations: Iterable[str],
    alerts: Iterable[str],
    additional_sections: Sequence[Tuple[str, str]] | None = None,
    language: str = "en",
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    title_style, heading_style, body_style, italic_style = _build_styles(language)
    story: List[object] = []

    story.append(_paragraph(t("report_title", language), title_style))
    story.append(Spacer(1, 12))

    story.append(_paragraph(t("pdf_input_details", language), heading_style))
    story.append(_build_table(input_rows, language))
    story.append(Spacer(1, 14))

    story.append(_paragraph(t("pdf_system_output", language), heading_style))
    story.append(_build_table(output_rows, language))
    story.append(Spacer(1, 14))

    story.append(_paragraph(t("pdf_alerts", language), heading_style))
    for item in alerts:
        story.append(_paragraph(f"- {item}", body_style))
    story.append(Spacer(1, 12))

    story.append(_paragraph(t("pdf_recommendations", language), heading_style))
    for item in recommendations:
        story.append(_paragraph(f"- {item}", body_style))
    story.append(Spacer(1, 12))

    if additional_sections:
        for section_title, section_body in additional_sections:
            story.append(_paragraph(section_title, heading_style))
            for line in str(section_body).split("\n"):
                if line.strip():
                    story.append(_paragraph(line, body_style))
            story.append(Spacer(1, 10))

    story.append(_paragraph(t("pdf_note", language), italic_style))
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
