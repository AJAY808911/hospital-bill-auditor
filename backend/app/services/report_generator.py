"""
Downloadable Audit Report PDF Generator using ReportLab.
Produces a structured, formatted pre-claim audit report.
"""
import io
from decimal import Decimal
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

def format_currency_inr(val: float) -> str:
    """Formats a float as standard INR currency string (₹ XX,XX,XXX.XX)."""
    return f"Rs. {val:,.2f}"

class ReportGeneratorService:
    @classmethod
    def generate_pdf_report(cls, audit_data: dict) -> bytes:
        """
        Generates a PDF bytes object from an audit record dictionary.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
            alignment=TA_CENTER,
        )

        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            alignment=TA_CENTER,
        )

        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=10,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            "BodySmall",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#334155"),
        )

        bold_small_style = ParagraphStyle(
            "BoldSmall",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#1e293b"),
        )

        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7,
            leading=10,
            textColor=colors.HexColor("#dc2626"),
        )

        elements = []

        # 1. Header & Title
        elements.append(Paragraph("HOSPITAL BILL AUDITOR", title_style))
        elements.append(Paragraph("Pre-Claim Health Insurance Admissibility & Deduction Audit Report", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=12))

        # 2. Metadata Grid (Audit Info, Patient, Policy)
        meta_data = [
            [
                Paragraph(f"<b>Audit Reference:</b> AUD-{audit_data.get('id', 'N/A')}", body_style),
                Paragraph(f"<b>Patient Name:</b> {audit_data.get('patient_name', 'Patient')}", body_style),
            ],
            [
                Paragraph(f"<b>Hospital:</b> {audit_data.get('hospital_name', 'Hospital')}", body_style),
                Paragraph(f"<b>Bill Number:</b> {audit_data.get('bill_number', 'N/A')}", body_style),
            ],
            [
                Paragraph(f"<b>Policy Name:</b> {audit_data.get('policy_name', 'Default Policy')}", body_style),
                Paragraph(f"<b>Stay Duration:</b> {audit_data.get('length_of_stay_days', 5)} Days", body_style),
            ],
            [
                Paragraph(f"<b>Audit Date:</b> {str(audit_data.get('created_at', ''))[:19]}", body_style),
                Paragraph(f"<b>Audit Status:</b> {audit_data.get('status', 'AUDIT_CLEAN')}", bold_small_style),
            ],
        ]
        meta_table = Table(meta_data, colWidths=[260, 260])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 14))

        # 3. High-Level Financial Summary Cards Box
        total_billed = float(audit_data.get("total_billed", 0.0))
        total_payable = float(audit_data.get("total_estimated_payable", 0.0))
        total_shortfall = float(audit_data.get("total_estimated_shortfall", 0.0))
        pct_payable = (total_payable / total_billed * 100) if total_billed > 0 else 0

        summary_data = [
            [
                Paragraph("<b>TOTAL BILLED</b>", bold_small_style),
                Paragraph("<b>ESTIMATED PAYABLE</b>", bold_small_style),
                Paragraph("<b>ESTIMATED SHORTFALL</b>", bold_small_style),
                Paragraph("<b>EST. COVERAGE %</b>", bold_small_style),
            ],
            [
                Paragraph(f"<font size=11 color='#1e293b'><b>{format_currency_inr(total_billed)}</b></font>", bold_small_style),
                Paragraph(f"<font size=11 color='#16a34a'><b>{format_currency_inr(total_payable)}</b></font>", bold_small_style),
                Paragraph(f"<font size=11 color='#dc2626'><b>{format_currency_inr(total_shortfall)}</b></font>", bold_small_style),
                Paragraph(f"<font size=11 color='#2563eb'><b>{pct_payable:.1f}%</b></font>", bold_small_style),
            ],
        ]
        summary_table = Table(summary_data, colWidths=[130, 130, 130, 130])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#ffffff")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 14))

        # 4. Item-by-Item Breakdown Table
        elements.append(Paragraph("Itemized Audit Breakdown", heading_style))
        
        items_header = [
            Paragraph("<b>#</b>", bold_small_style),
            Paragraph("<b>Item Description</b>", bold_small_style),
            Paragraph("<b>Category</b>", bold_small_style),
            Paragraph("<b>Billed</b>", bold_small_style),
            Paragraph("<b>Estimated Payable</b>", bold_small_style),
            Paragraph("<b>Deduction</b>", bold_small_style),
            Paragraph("<b>Audit Reason / Rule</b>", bold_small_style),
        ]
        items_rows = [items_header]

        raw_items = audit_data.get("items", [])
        for idx, it in enumerate(raw_items, start=1):
            billed_val = float(it.get("billed_amount", 0.0))
            pay_val = float(it.get("payable_amount", 0.0))
            ded_val = float(it.get("deduction_amount", 0.0))
            reason = it.get("deduction_reason", "")
            
            items_rows.append([
                Paragraph(str(idx), body_style),
                Paragraph(f"<b>{it.get('description', '')}</b>", body_style),
                Paragraph(it.get("category_label") or it.get("category", ""), body_style),
                Paragraph(format_currency_inr(billed_val), body_style),
                Paragraph(f"<font color='#16a34a'>{format_currency_inr(pay_val)}</font>", body_style),
                Paragraph(f"<font color='#dc2626'>{format_currency_inr(ded_val)}</font>", body_style),
                Paragraph(reason, body_style),
            ])

        items_table = Table(items_rows, colWidths=[20, 120, 80, 65, 75, 65, 95])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 14))

        # 5. Policy Assumptions & Explanation
        elements.append(Paragraph("Policy Rules & Applied Assumptions", heading_style))
        assumptions = audit_data.get("assumptions", [])
        if not assumptions:
            assumptions = ["Standard policy rules applied with zero discrepancy."]

        assumption_paragraphs = []
        for ass in assumptions:
            assumption_paragraphs.append(Paragraph(f"• {ass}", body_style))
        
        elements.extend(assumption_paragraphs)
        elements.append(Spacer(1, 12))

        # 6. Statutory Disclaimer Box
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=8))
        disclaimer_text = (
            "<b>STATUTORY DISCLAIMER:</b> This pre-claim audit estimation is generated by the Hospital Bill Auditor software "
            "for educational and preliminary estimation purposes only. It is NOT a binding insurance claim settlement, "
            "legal advice, or guaranteed claim disbursement. Insurer claim settlement teams determine final admissible amounts "
            "subject to policy terms, condition exclusions, cashless pre-authorization, and medical necessity verification."
        )
        elements.append(Paragraph(disclaimer_text, disclaimer_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

