from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
from backend.config import Config
from backend.utils.helpers import to_local


def fmt_local(value):
    """Render a stored naive-UTC timestamp in local time for the invoice."""
    if not value:
        return 'N/A'
    return to_local(value).strftime('%d %b %Y, %I:%M %p')

def generate_receipt_pdf(booking):
    os.makedirs(Config.RECEIPT_FOLDER, exist_ok=True)
    filename = f"receipt_{booking.booking_id}.pdf"
    filepath = os.path.join(Config.RECEIPT_FOLDER, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, alignment=TA_CENTER, textColor=colors.HexColor('#1a5c8e'), spaceAfter=6)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], fontSize=14, alignment=TA_CENTER, textColor=colors.HexColor('#4a90d9'), spaceAfter=20)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, leading=14)
    bold_style = ParagraphStyle('Bold', parent=normal_style, fontName='Helvetica-Bold')
    right_style = ParagraphStyle('Right', parent=normal_style, alignment=TA_RIGHT)
    center_style = ParagraphStyle('Center', parent=normal_style, alignment=TA_CENTER)
    small_style = ParagraphStyle('Small', parent=normal_style, fontSize=8, textColor=colors.grey)

    elements = []

    elements.append(Paragraph("ParkEase", title_style))
    elements.append(Paragraph("Smart Parking Management System", subtitle_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("GSTIN: 27AAECP1234Q1Z5", center_style))
    elements.append(Paragraph("ParkEase Technologies Pvt. Ltd.", center_style))
    elements.append(Paragraph("123 Tech Park, Bengaluru - 560001", center_style))
    elements.append(Spacer(1, 15))

    header_data = [
        ['RECEIPT', ''],
        ['Booking ID:', booking.booking_id],
        ['Date:', to_local(datetime.utcnow()).strftime('%d %b %Y, %I:%M %p')],
        ['Status:', booking.payment_status.upper()],
    ]
    header_table = Table(header_data, colWidths=[100*mm, 80*mm])
    header_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1a5c8e')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 14),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 15))

    from backend.models import User, Facility
    user = User.query.get(booking.user_id)
    facility = Facility.query.get(booking.facility_id)

    user_data = [
        ['Customer Details', ''],
        ['Name:', user.full_name if user else 'N/A'],
        ['Email:', user.email if user else 'N/A'],
        ['Phone:', user.phone if user else 'N/A'],
        ['Vehicle:', f"{booking.vehicle_no} ({booking.vehicle_type})"],
    ]
    user_table = Table(user_data, colWidths=[100*mm, 80*mm])
    user_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#f0f4f8')),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(user_table)
    elements.append(Spacer(1, 10))

    facility_data = [
        ['Parking Facility Details', ''],
        ['Facility:', facility.name if facility else 'N/A'],
        ['Address:', f"{facility.street}, {facility.area}, {facility.city} - {facility.pincode}" if facility else 'N/A'],
        ['Slots:', ', '.join(booking.get_slot_codes())],
    ]
    facility_table = Table(facility_data, colWidths=[100*mm, 80*mm])
    facility_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#f0f4f8')),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(facility_table)
    elements.append(Spacer(1, 10))

    timing_data = [
        ['Parking Duration', ''],
        ['Start:', fmt_local(booking.start_time)],
        ['End:', fmt_local(booking.end_time)],
        ['Duration:', f"{booking.duration_value} {booking.duration_unit}"],
    ]
    if booking.check_in_time:
        timing_data.append(['Check-in:', fmt_local(booking.check_in_time)])
    if booking.check_out_time:
        timing_data.append(['Check-out:', fmt_local(booking.check_out_time)])

    timing_table = Table(timing_data, colWidths=[100*mm, 80*mm])
    timing_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#f0f4f8')),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(timing_table)
    elements.append(Spacer(1, 15))

    price_data = [
        ['Description', 'Amount (₹)'],
        ['Base Price', f"{booking.base_price:,.2f}"],
    ]
    if booking.discount > 0:
        price_data.append([f'Discount ({booking.discount_reason})', f"-{booking.discount:,.2f}"])
    price_data.append(['Subtotal', f"{booking.base_price - booking.discount:,.2f}"])
    price_data.append([f'GST ({int(Config.GST_RATE * 100)}%)', f"{booking.gst:,.2f}"])
    price_data.append(['Total Amount', f"{booking.total_amount:,.2f}"])

    price_table = Table(price_data, colWidths=[140*mm, 40*mm])
    price_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5c8e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f0f8')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(price_table)
    elements.append(Spacer(1, 20))

    payment_data = [
        ['Payment Details', ''],
        ['Method:', booking.payment_method.title() if booking.payment_method else 'N/A'],
        ['Transaction ID:', booking.transaction_id or 'N/A'],
        ['Paid At:', fmt_local(booking.paid_at)],
    ]
    payment_table = Table(payment_data, colWidths=[100*mm, 80*mm])
    payment_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#f0f4f8')),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Thank you for choosing ParkEase!", ParagraphStyle('Thanks', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, textColor=colors.HexColor('#1a5c8e'))))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("For support, contact: support@parkease.com | +91-80-1234-5678", small_style))
    elements.append(Paragraph("This is a computer-generated receipt. No signature required.", small_style))

    doc.build(elements)
    return filepath