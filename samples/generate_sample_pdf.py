"""
Generates a realistic synthetic hospital bill PDF matching the Section 7 demonstration case.
Useful for live testing the PDF upload and extraction workflow.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

def create_sample_bill_pdf(output_path: str):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        "HospitalTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0f172a"),
    )
    sub_style = ParagraphStyle(
        "SubHeader",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#475569"),
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1e293b"),
    )
    bold_style = ParagraphStyle(
        "BodyBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0f172a"),
    )

    story = []

    # Hospital Header
    story.append(Paragraph("APOLLO MULTISPECIALITY HOSPITAL", header_style))
    story.append(Paragraph("In-Patient Final Tax Invoice / Discharge Billing Summary", sub_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2563eb"), spaceAfter=10))

    # Patient Details Grid
    meta_data = [
        [
            Paragraph("<b>Patient Name:</b> Ramesh Kumar", body_style),
            Paragraph("<b>Bill No:</b> INV-2026-DEMO-001", body_style),
        ],
        [
            Paragraph("<b>Age / Gender:</b> 52 Y / Male", body_style),
            Paragraph("<b>IPD Admission:</b> 15-Oct-2026", body_style),
        ],
        [
            Paragraph("<b>Attending Consultant:</b> Dr. S. Rao, MS", body_style),
            Paragraph("<b>Discharge Date:</b> 20-Oct-2026 (5 Days)", body_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Section 7 Bill Items
    story.append(Paragraph("Itemized Medical Charges", bold_style))
    story.append(Spacer(1, 5))

    items_data = [
        [
            Paragraph("<b>#</b>", bold_style),
            Paragraph("<b>Item Description / Particulars</b>", bold_style),
            Paragraph("<b>Qty / Days</b>", bold_style),
            Paragraph("<b>Rate (Rs.)</b>", bold_style),
            Paragraph("<b>Total Amount (Rs.)</b>", bold_style),
        ],
        [
            Paragraph("1", body_style),
            Paragraph("Room rent (Deluxe Ward - 5 Days)", body_style),
            Paragraph("5", body_style),
            Paragraph("5,000.00", body_style),
            Paragraph("25,000.00", body_style),
        ],
        [
            Paragraph("2", body_style),
            Paragraph("Doctor, nursing, and OT charges", body_style),
            Paragraph("1", body_style),
            Paragraph("60,000.00", body_style),
            Paragraph("60,000.00", body_style),
        ],
        [
            Paragraph("3", body_style),
            Paragraph("Pharmacy medicines and IV fluids", body_style),
            Paragraph("1", body_style),
            Paragraph("30,000.00", body_style),
            Paragraph("30,000.00", body_style),
        ],
        [
            Paragraph("4", body_style),
            Paragraph("Gloves, masks, and administrative fees", body_style),
            Paragraph("1", body_style),
            Paragraph("8,000.00", body_style),
            Paragraph("8,000.00", body_style),
        ],
        [
            Paragraph("5", body_style),
            Paragraph("Diagnostics and laboratory investigations", body_style),
            Paragraph("1", body_style),
            Paragraph("27,000.00", body_style),
            Paragraph("27,000.00", body_style),
        ],
        [
            Paragraph("", body_style),
            Paragraph("<b>TOTAL BILLED CHARGES:</b>", bold_style),
            Paragraph("", body_style),
            Paragraph("", body_style),
            Paragraph("<b>150,000.00</b>", bold_style),
        ]
    ]

    items_table = Table(items_data, colWidths=[25, 235, 75, 95, 110])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Authorized Signatory: Dr. S. Rao (Chief Medical Officer)", body_style))
    doc.build(story)

if __name__ == "__main__":
    create_sample_bill_pdf("samples/sample_hospital_bill.pdf")
    print("Sample hospital bill created at samples/sample_hospital_bill.pdf")

