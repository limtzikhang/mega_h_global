# invoice.py
import os
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_invoice_pdf(order_data, filepath):
    """
    Dynamically constructs a professional corporate transaction invoice PDF 
    and saves it to the specified local workspace directory path.
    """
    # Initialize ReportLab document document template
    doc = SimpleDocTemplate(
        filepath, 
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36,
        title=f"Invoice_{order_data.get('tracking_id')}"
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette Definitions
    primary_color = colors.HexColor("#0f172a")   # Slate Blue Corporate Core
    secondary_color = colors.HexColor("#475569") # Subdued Grey Details
    
    # Custom Typographic Paragraph Styles
    title_style = ParagraphStyle(
        'InvoiceTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=24, leading=28,
        textColor=primary_color, spaceAfter=6
    )
    company_style = ParagraphStyle(
        'CompanyMeta', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13,
        textColor=secondary_color, alignment=2 # Right align
    )
    meta_style = ParagraphStyle(
        'MetaText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=14,
        textColor=primary_color
    )
    th_style = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=12,
        textColor=colors.white, alignment=1 # Center align
    )
    td_style = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=12,
        alignment=1 # Center align
    )
    footnote_style = ParagraphStyle(
        'MedicalFootnote', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=7, leading=10,
        textColor=secondary_color, alignment=1 # Center align
    )
    
    story = []
    
    # 1. Header Layout Grid (Company Name Left, Billing Meta Info Right)
    header_data = [
        [
            Paragraph("<b>MEGA H GLOBAL SDN BHD</b><br/>Cellular Bio-Nutrition Solutions", meta_style),
            Paragraph("<b>OFFICIAL INVOICE</b><br/>Date: 2026-10-31<br/>Status: PAID", company_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[270, 270])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    # 2. Client & Consignment Metadata Tracking Block
    client_data = [
        [
            Paragraph(f"<b>Bill To:</b><br/>Account Node: {order_data.get('user_email')}", meta_style),
            Paragraph(f"<b>Shipment Details:</b><br/>Carrier: {order_data.get('carrier')}<br/>AWB Tracking: {order_data.get('tracking_id')}", meta_style)
        ]
    ]
    client_table = Table(client_data, colWidths=[270, 270])
    client_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 20))
    
    # 3. Itemized Financial Purchase Grid Table
    qty = order_data.get('quantity', 1)
    amt = order_data.get('amount_paid', 0.0)
    deliv = order_data.get('delivery_bottles', qty)
    
    # Avoid div-by-zero during safety loops
    price_per = amt / qty if qty > 0 else 0.0
    
    table_data = [
        [Paragraph("Product Description", th_style), Paragraph("Qty Ordered", th_style), Paragraph("Total Dispatched", th_style), Paragraph("Unit Price", th_style), Paragraph("Subtotal", th_style)],
        [Paragraph(f"<b>{order_data.get('product', 'MEGA H BOTTLE')}</b>", td_style), Paragraph(str(qty), td_style), Paragraph(f"{deliv} Bottles", td_style), Paragraph(f"RM {price_per:,.2f}", td_style), Paragraph(f"RM {amt:,.2f}", td_style)]
    ]
    
    item_table = Table(table_data, colWidths=[200, 75, 95, 80, 90])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(item_table)
    story.append(Spacer(1, 40))
    
    # 4. Mandatory Clinical Health Disclaimer Footnote Integration
    story.append(Spacer(1, 20))
    disclaimer_text = "This is for informational purposes only. For medical advice or diagnosis, consult a professional. AI responses may include mistakes."
    story.append(Paragraph(disclaimer_text, footnote_style))
    
    # Build complete compiled story elements buffer to target location file paths
    doc.build(story)
