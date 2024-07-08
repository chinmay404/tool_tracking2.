from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
from io import BytesIO
from .models import *
from .qr_gen import generate_multi_uuid_qr
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from .models import SaleOrder, SaleOrderGroup
from .qr_gen import generate_multi_uuid_qr, generate_qr_code ,single_qr
from reportlab.platypus import Image as PlatypusImage  

def pdf(grn_number):
    sale_order = get_object_or_404(SaleOrder, grn_number=grn_number)
    # uuids = sale_order.uuids
    bill_no = sale_order.bill_no
    img_data = generate_multi_uuid_qr(grn_number)

    pdf_data = BytesIO()
    img = Image.open(img_data)

    c = canvas.Canvas(pdf_data, pagesize=letter)
    img_width, img_height = 100, 100
    c.drawInlineImage(img, x=100, y=500, width=img_width, height=img_height)

    c.setFont("Helvetica", 12)
    text_lines = [
        f"Bill No: {sale_order.bill_no}",
        f"GRN Number: {sale_order.grn_number}",
        f"PO Number: {sale_order.po_number}",
        f"Vehicle No: {sale_order.vehicle_no}",
        f"Status: {sale_order.status}",
        f"Total Quantity: {sale_order.total_quantity}",
        "Products:",
    ]

    for sale_order_product in sale_order.saleorderproduct_set.all():
        product_info = f" - {sale_order_product.product.name}: {sale_order_product.quantity}"
        text_lines.append(product_info)

    y_position = 450
    for line in text_lines:
        c.drawString(100, y_position, line)
        y_position -= 15

    c.showPage()
    c.save()

    pdf_data.seek(0)
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bill_NO -{bill_no}.pdf"'
    return response


def generate_pdf(request, group_id):
    # Fetch SaleOrderGroup
    sale_order_group = get_object_or_404(SaleOrderGroup, pk=group_id)

    # Create response object
    response = HttpResponse(content_type='application/pdf')

    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Add SaleOrderGroup info to PDF
    style = getSampleStyleSheet()
    header_style = style['Heading1']
    normal_style = style['Normal']

    elements.append(Paragraph(
        f"<strong>Sale Order Group ID:</strong> <font color='red'>G-{sale_order_group.group_id}</font>", header_style))
    elements.append(Paragraph(
        f"<strong>Unit:</strong> <font color='red'>{sale_order_group.unit}</font>", normal_style))
    elements.append(
        Paragraph(f"<strong>Status:</strong> {sale_order_group.status}", normal_style))
    elements.append(Spacer(1, 12))

    # Generate QR code and add to PDF
    print(group_id)

    qr_data = generate_qr_code(group_id,dotted_style=True)
    platypus_image = PlatypusImage(qr_data, width=100, height=100)  # Correct usage
    elements.append(platypus_image)
    elements.append(Spacer(1, 12))
    sale_order_header = [
        "Bill No",
        "UUID",
        "PO Number",
        "Vehicle No",
        "Driver Name",
        "Status",
    ]

    # Create table data for SaleOrders
    sale_order_data = []
    for sale_order in SaleOrder.objects.filter(group_id=sale_order_group.group_id):
        sale_order_row = [
            sale_order.order_no,
            sale_order.uuid,
            sale_order.po_number,
            sale_order.vehicle_no,
            sale_order.driver_name,
            sale_order.status,
        ]
        sale_order_data.append(sale_order_row)

    # Create table style for SaleOrders
    sale_order_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    # Create table for SaleOrders
    sale_order_table = Table([sale_order_header] + sale_order_data)
    sale_order_table.setStyle(sale_order_table_style)
    elements.append(sale_order_table)
    elements.append(Spacer(1, 12))

    # Add heading for SaleOrderProducts
    elements.append(
        Paragraph("<strong>Sale Order Products:</strong>", header_style))
    elements.append(Spacer(1, 12))

    # Create table headers for SaleOrderProducts
    product_header = [
        "SaleOrder No",
        "Product",
        "Material Code",
        "Quantity"
    ]

    # Create table data for SaleOrderProducts
    product_data = []
    for sale_order in SaleOrder.objects.filter(group_id=sale_order_group.group_id):
        sale_order_products = sale_order.saleorderproduct_set.all()
        for sale_order_product in sale_order_products:
            product_row = [
                sale_order_product.sale_order.order_no,
                sale_order_product.product.name,
                sale_order_product.product.MaterialCode,
                sale_order_product.quantity
            ]
            product_data.append(product_row)

    # Create table style for SaleOrderProducts
    product_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    # Create table for SaleOrderProducts
    product_table = Table([product_header] + product_data)
    product_table.setStyle(product_table_style)
    elements.append(product_table)

    # Build PDF document
    doc.build(elements)

    return response