"""PDF report generation. The disclaimer is rendered on every report and is
not optional -- see DISCLAIMER.md for why.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import RISK_ACTION, RISK_REVIEW, RISK_SAFE, ComplianceReport

RISK_MEANINGS = {
    RISK_SAFE: "No restrictions triggered in this context; OK to use as-is.",
    RISK_REVIEW: "An obligation may apply; verify before treating as clear.",
    RISK_ACTION: "An obligation is triggered or the license is unresolved; route to legal counsel.",
}


class PDFReporter:
    """Generates a professional PDF compliance-guidance report."""

    def __init__(self):
        styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            "ReportTitle", parent=styles["Title"], fontSize=18, spaceAfter=6
        )
        self.subtitle_style = ParagraphStyle(
            "ReportSubtitle", parent=styles["Normal"], fontSize=11, textColor=colors.grey,
            spaceAfter=14,
        )
        self.disclaimer_style = ParagraphStyle(
            "Disclaimer", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#7a1f1f"),
            borderColor=colors.HexColor("#7a1f1f"), borderWidth=0.5, borderPadding=6,
            spaceAfter=16, backColor=colors.HexColor("#fdf0f0"),
        )
        self.heading_style = ParagraphStyle(
            "SectionHeading", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6
        )
        self.body_style = styles["Normal"]
        self.footer_style = ParagraphStyle(
            "Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey
        )

    def generate_report(self, compliance_report: ComplianceReport, output_path: str) -> str:
        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
        )
        story = []

        story.append(Paragraph("Open Source License Compliance Report", self.title_style))
        story.append(Paragraph("Guidance and gap identification -- not a compliance certification", self.subtitle_style))
        story.append(Paragraph(f"<b>DISCLAIMER:</b> {compliance_report.disclaimer}", self.disclaimer_style))

        context = compliance_report.context
        story.append(Paragraph("Product Summary", self.heading_style))
        story.append(
            Paragraph(
                f"Product: {compliance_report.product_name or '-'}<br/>"
                f"Scan Date: {compliance_report.scan_date.isoformat()}<br/>"
                f"Use Case: {context.use_case if context else '-'}<br/>"
                f"Total Dependencies: {len(compliance_report.dependencies)}<br/>"
                f"Scope note: direct dependencies only; transitive dependencies are not scanned.",
                self.body_style,
            )
        )

        story.append(Spacer(1, 8))
        story.append(Paragraph("Risk Summary", self.heading_style))
        summary_data = [["Risk Level", "Count", "Meaning"]]
        for level in (RISK_SAFE, RISK_REVIEW, RISK_ACTION):
            summary_data.append(
                [level, str(compliance_report.risk_summary.get(level, 0)), RISK_MEANINGS[level]]
            )
        story.append(self._table(summary_data, col_widths=[3.5 * cm, 1.5 * cm, 9.5 * cm], header=True))

        story.append(Spacer(1, 8))
        story.append(Paragraph("Applicable Regulations", self.heading_style))
        if compliance_report.regulatory_references:
            for reg in compliance_report.regulatory_references:
                story.append(Paragraph(reg, self.body_style))
        else:
            story.append(Paragraph("None identified from the supplied context.", self.body_style))

        story.append(Spacer(1, 8))
        story.append(Paragraph("Detailed Dependency List", self.heading_style))
        dep_data = [["Library", "Version", "License", "Risk", "Notes"]]
        for dep in compliance_report.dependencies:
            risk = dep.risk_level_for_context(context) if context else RISK_ACTION
            notes = "Needs legal review" if risk in (RISK_REVIEW, RISK_ACTION) else ""
            dep_data.append(
                [dep.name, dep.version, dep.license.name if dep.license else "Unknown", risk, notes]
            )
        story.append(
            self._table(dep_data, col_widths=[3.5 * cm, 2 * cm, 4 * cm, 2.5 * cm, 2.5 * cm], header=True)
        )

        if compliance_report.actions_required:
            story.append(Spacer(1, 8))
            story.append(Paragraph("Actions Required", self.heading_style))
            for action in compliance_report.actions_required:
                story.append(Paragraph(f"• {action}", self.body_style))

        story.append(Spacer(1, 0.5 * cm))
        story.append(
            Paragraph("For questions about this report, consult your legal counsel.", self.footer_style)
        )

        doc.build(story)
        return output_path

    def _table(self, data, col_widths=None, header=False):
        table = Table(data, colWidths=col_widths)
        style = [
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
        if header:
            style.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")))
            style.append(("TEXTCOLOR", (0, 0), (-1, 0), colors.white))
            style.append(("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"))
        table.setStyle(TableStyle(style))
        return table
