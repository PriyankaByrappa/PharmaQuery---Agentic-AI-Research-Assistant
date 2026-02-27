"""Research Report Generator — Creates downloadable PDF reports from analysis results.

Uses ReportLab to generate well-formatted academic-style reports with scoring dimensions,
annotations, opportunities, and faculty recommendations.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import io


class ResearchReportGenerator:
    """Generates PDF reports for research paper analysis."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        if 'ReportTitle' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='ReportTitle',
                parent=self.styles['Heading1'],
                fontSize=22,
                textColor=colors.HexColor('#1a1a2e'),
                spaceAfter=20,
                alignment=TA_CENTER,
                leading=28,
            ))

        if 'Section' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='Section',
                parent=self.styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#16213e'),
                spaceAfter=10,
                spaceBefore=16,
            ))

        if 'SubSection' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='SubSection',
                parent=self.styles['Heading3'],
                fontSize=11,
                textColor=colors.HexColor('#0f3460'),
                spaceAfter=6,
                spaceBefore=10,
            ))

        body = self.styles['BodyText']
        body.fontSize = 10
        body.leading = 14
        body.alignment = TA_JUSTIFY

    def generate_report(self, analysis_id: str, result: Dict[str, Any]) -> bytes:
        """
        Generate a PDF report and return bytes.

        Args:
            analysis_id: Unique analysis identifier.
            result: The full result dict from ResearchAgent.

        Returns:
            PDF content as bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                                topMargin=0.75 * inch, bottomMargin=0.75 * inch)
        story = []

        # ── Title Page ──
        story.append(Spacer(1, 1.5 * inch))
        story.append(Paragraph("Research Paper Analysis Report", self.styles['ReportTitle']))
        story.append(Spacer(1, 0.3 * inch))

        meta_style = ParagraphStyle('Meta', parent=self.styles['BodyText'],
                                     alignment=TA_CENTER, textColor=colors.grey,
                                     fontSize=9)
        story.append(Paragraph(f"Analysis ID: {analysis_id}", meta_style))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            meta_style
        ))
        story.append(Spacer(1, 0.4 * inch))
        story.append(HRFlowable(width="100%", color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 0.5 * inch))

        # ── Quality Score ──
        total_score = result.get("research_score", 0)
        story.append(Paragraph("Quality Assessment", self.styles['Section']))

        level = "Excellent" if total_score > 75 else "Strong" if total_score > 55 else "Needs Improvement"
        story.append(Paragraph(
            f"<b>Overall Quality Score:</b> {total_score}/100 — <i>{level}</i>",
            self.styles['BodyText']
        ))
        story.append(Spacer(1, 0.15 * inch))

        # Dimension table
        dims = result.get("score_dimensions", {})
        if dims:
            dim_data = [["Dimension", "Score"]]
            for key, val in dims.items():
                dim_data.append([key.replace("_", " ").title(), f"{val}%"])

            dim_table = Table(dim_data, colWidths=[3.5 * inch, 1.5 * inch])
            dim_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ]))
            story.append(dim_table)
        story.append(Spacer(1, 0.3 * inch))

        # ── Annotations ──
        annotations = result.get("annotations", [])
        if annotations:
            story.append(Paragraph("Document Annotations", self.styles['Section']))
            for i, anno in enumerate(annotations, 1):
                tag = anno.get("tag", "")
                content = anno.get("content", "")[:120]
                reasoning = anno.get("reasoning", "")
                suggestion = anno.get("suggestion", "")

                story.append(Paragraph(f"<b>#{i} [{tag}]</b>", self.styles['SubSection']))
                story.append(Paragraph(f"<i>\"{content}\"</i>", self.styles['BodyText']))
                story.append(Paragraph(f"<b>Reasoning:</b> {reasoning}", self.styles['BodyText']))
                if suggestion:
                    story.append(Paragraph(f"<b>Suggestion:</b> {suggestion}", self.styles['BodyText']))
                story.append(Spacer(1, 0.1 * inch))

        story.append(Spacer(1, 0.2 * inch))

        # ── Opportunities ──
        opportunities = result.get("top_opportunities", [])
        if opportunities:
            story.append(Paragraph("Research Opportunities", self.styles['Section']))

            opp_data = [["#", "Title", "Source", "Relevance", "Deadline"]]
            for i, opp in enumerate(opportunities, 1):
                opp_data.append([
                    str(i),
                    opp.get("title", "")[:55],
                    opp.get("source", ""),
                    f"{opp.get('relevance_score', 0)}%",
                    opp.get("deadline", "N/A"),
                ])

            opp_table = Table(opp_data, colWidths=[0.3 * inch, 2.8 * inch, 1.2 * inch, 0.8 * inch, 1.2 * inch])
            opp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ]))
            story.append(opp_table)

            # Why matched details
            for i, opp in enumerate(opportunities, 1):
                why = opp.get("why_matched", "")
                if why:
                    story.append(Spacer(1, 0.05 * inch))
                    story.append(Paragraph(
                        f"<b>#{i}:</b> {why}",
                        ParagraphStyle('why', parent=self.styles['BodyText'],
                                       fontSize=8, textColor=colors.grey)
                    ))

        story.append(Spacer(1, 0.3 * inch))

        # ── Faculty Recommendations ──
        faculty = result.get("faculty_recommendations", [])
        if faculty:
            story.append(Paragraph("Suggested Faculty", self.styles['Section']))

            fac_data = [["Name", "Institution", "Research Area"]]
            for f in faculty:
                fac_data.append([
                    f.get("name", ""),
                    f.get("inst", ""),
                    f.get("area", ""),
                ])

            fac_table = Table(fac_data, colWidths=[2 * inch, 1.5 * inch, 2.5 * inch])
            fac_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ]))
            story.append(fac_table)
            story.append(Spacer(1, 0.1 * inch))

            for f in faculty:
                why = f.get("why", "")
                if why:
                    story.append(Paragraph(
                        f"<b>{f.get('name', '')}:</b> {why}",
                        ParagraphStyle('fwhy', parent=self.styles['BodyText'],
                                       fontSize=8, textColor=colors.grey)
                    ))
                    story.append(Spacer(1, 0.05 * inch))

        story.append(Spacer(1, 0.3 * inch))

        # ── Confidence ──
        conf = result.get("confidence_result", {})
        if conf:
            story.append(Paragraph("AI Confidence Assessment", self.styles['Section']))
            story.append(Paragraph(
                f"<b>Confidence Level:</b> {conf.get('level', 'N/A')}",
                self.styles['BodyText']
            ))
            story.append(Paragraph(conf.get('summary', ''), self.styles['BodyText']))
            story.append(Spacer(1, 0.1 * inch))

            conf_data = [
                ["Model Certainty", f"{conf.get('model_certainty', 0)}%"],
                ["Data Completeness", f"{conf.get('data_completeness', 0)}%"],
                ["Document Clarity", f"{conf.get('document_clarity', 0)}%"],
                ["Signal Consistency", f"{conf.get('signal_consistency', 0)}%"],
            ]
            conf_table = Table(conf_data, colWidths=[3 * inch, 1.5 * inch])
            conf_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
            ]))
            story.append(conf_table)

        # ── Footer ──
        story.append(Spacer(1, 0.5 * inch))
        story.append(HRFlowable(width="100%", color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 0.1 * inch))
        footer_style = ParagraphStyle('Footer', parent=self.styles['BodyText'],
                                       fontSize=7, textColor=colors.grey, alignment=TA_CENTER)
        story.append(Paragraph(
            "Generated by PharmaQuery Research Intelligence Platform. "
            "AI signals are intended to guide refinement, not serve as absolute final judgment.",
            footer_style
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer.read()
