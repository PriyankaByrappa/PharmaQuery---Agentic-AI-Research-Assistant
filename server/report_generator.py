"""PDF Report Generator using ReportLab."""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from typing import Dict, Any, List
from datetime import datetime
import os
from config import REPORTS_DIR


class ReportGenerator:
    """Generates PDF reports from analysis results."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Add custom title style
        if 'CustomTitle' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER
            ))
        
        # Add section header style
        if 'SectionHeader' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=12,
                spaceBefore=20
            ))
        
        # Modify existing BodyText style instead of adding a new one
        body_style = self.styles['BodyText']
        body_style.fontSize = 10
        body_style.leading = 14
        body_style.alignment = TA_JUSTIFY
    
    def generate_report(self, analysis_id: str, query: str, 
                        opportunities: List[Dict[str, Any]],
                        agent_outputs: Dict[str, Dict[str, Any]]) -> str:
        """
        Generate a comprehensive PDF report.
        
        Returns:
            Path to generated PDF file
        """
        filename = f"report_{analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = REPORTS_DIR / filename
        
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        
        # Title Page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("Drug Repurposing Opportunity Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Analysis ID: {analysis_id}", self.styles['BodyText']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                              self.styles['BodyText']))
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        story.append(Paragraph(f"<b>Query:</b> {query}", self.styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            f"This report presents {len(opportunities)} ranked repurposing opportunities "
            f"based on comprehensive analysis across market, patent, clinical, and literature domains.",
            self.styles['BodyText']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Top Opportunities Summary Table
        top_opps = opportunities[:5]
        summary_data = [["Rank", "Opportunity", "Composite Score"]]
        for i, opp in enumerate(top_opps, 1):
            title = opp.get("title", "N/A")[:50] + "..." if len(opp.get("title", "")) > 50 else opp.get("title", "N/A")
            score = opp.get("scores", {}).get("composite", 0)
            summary_data.append([str(i), title, f"{score:.2f}"])
        
        summary_table = Table(summary_data, colWidths=[0.5*inch, 4*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(PageBreak())
        
        # Detailed Opportunities
        story.append(Paragraph("Ranked Opportunities", self.styles['SectionHeader']))
        
        for i, opp in enumerate(opportunities, 1):
            story.append(Paragraph(f"{i}. {opp.get('title', 'N/A')}", 
                                 self.styles['SectionHeader']))
            
            # Description
            if opp.get("description"):
                story.append(Paragraph(f"<b>Description:</b> {opp.get('description')}", 
                                     self.styles['BodyText']))
                story.append(Spacer(1, 0.1*inch))
            
            # Scores
            scores = opp.get("scores", {})
            score_text = (
                f"<b>Scores:</b> Market: {scores.get('market', 0):.2f}, "
                f"Patent: {scores.get('patent', 0):.2f}, "
                f"Clinical: {scores.get('clinical', 0):.2f}, "
                f"Literature: {scores.get('literature', 0):.2f}, "
                f"<b>Composite: {scores.get('composite', 0):.2f}</b>"
            )
            story.append(Paragraph(score_text, self.styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))
            
            # Justification
            if opp.get("justification"):
                story.append(Paragraph(f"<b>Justification:</b> {opp.get('justification')}", 
                                     self.styles['BodyText']))
                story.append(Spacer(1, 0.1*inch))
            
            # Pros
            pros = opp.get("pros", [])
            if pros:
                pros_text = "<b>Pros:</b> " + "; ".join(pros)
                story.append(Paragraph(pros_text, self.styles['BodyText']))
                story.append(Spacer(1, 0.1*inch))
            
            # Cons
            cons = opp.get("cons", [])
            if cons:
                cons_text = "<b>Cons:</b> " + "; ".join(cons)
                story.append(Paragraph(cons_text, self.styles['BodyText']))
                story.append(Spacer(1, 0.1*inch))
            
            # Risk Factors
            risks = opp.get("risk_factors", [])
            if risks:
                risks_text = "<b>Risk Factors:</b> " + "; ".join(risks)
                story.append(Paragraph(risks_text, self.styles['BodyText']))
                story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.3*inch))
            
            if i < len(opportunities):
                story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        
        # Agent Analysis Summary
        story.append(Paragraph("Agent Analysis Summary", self.styles['SectionHeader']))
        
        for agent_type, output in agent_outputs.items():
            story.append(Paragraph(f"{agent_type.capitalize()} Agent", 
                                 self.styles['SectionHeader']))
            
            evidence = output.get("evidence", {})
            scores = output.get("scores", {})
            
            # Key findings
            findings = []
            if agent_type == "market":
                findings.append(f"Market Size: ${evidence.get('market_size', 0):,}")
                findings.append(f"CAGR: {evidence.get('cagr', 0)}%")
                findings.append(f"Competitors: {', '.join(evidence.get('competitors', []))}")
            elif agent_type == "patent":
                findings.append(f"Active Patents: {evidence.get('active_patents', 0)}")
                findings.append(f"Expiring Patents: {evidence.get('expiring_patents', 0)}")
                findings.append(f"FTO: {evidence.get('freedom_to_operate', False)}")
            elif agent_type == "clinical":
                findings.append(f"Ongoing Trials: {evidence.get('ongoing_trials', 0)}")
                findings.append(f"Gaps: {', '.join(evidence.get('gaps', []))}")
            elif agent_type == "literature":
                findings.append(f"Black Box Warnings: {evidence.get('black_box_warnings', 0)}")
                findings.append(f"Scientific Rationale: {evidence.get('scientific_rationale', 'N/A')}")
            
            for finding in findings:
                story.append(Paragraph(f"• {finding}", self.styles['BodyText']))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)

