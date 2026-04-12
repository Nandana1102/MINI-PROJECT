from __future__ import annotations

from io import BytesIO
from typing import Iterable, List, Sequence, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


RowItems = Sequence[Tuple[str, str]]


def _build_table(rows: RowItems):
    table_data = [["Field", "Value"], *[[str(key), str(value)] for key, value in rows]]
    table = Table(table_data, colWidths=[2.2 * inch, 4.0 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
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
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story: List[object] = []

    story.append(Paragraph("Health Risk Assessment Report", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Input Details", styles["Heading2"]))
    story.append(_build_table(input_rows))
    story.append(Spacer(1, 14))

    story.append(Paragraph("System Output", styles["Heading2"]))
    story.append(_build_table(output_rows))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Health Alerts", styles["Heading2"]))
    for item in alerts:
        story.append(Paragraph(f"• {item}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Personalized Recommendations", styles["Heading2"]))
    for item in recommendations:
        story.append(Paragraph(f"• {item}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    if additional_sections:
        for section_title, section_body in additional_sections:
            story.append(Paragraph(section_title, styles["Heading2"]))
            for line in str(section_body).split("\n"):
                if line.strip():
                    story.append(Paragraph(line, styles["BodyText"]))
            story.append(Spacer(1, 10))

    story.append(Paragraph("Note: This report is for academic demonstration and not a clinical diagnosis.", styles["Italic"]))
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
