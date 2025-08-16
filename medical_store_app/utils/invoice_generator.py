import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors

class InvoiceGenerator:
    """Generate professional PDF invoices for sales"""
    
    def __init__(self, sale, store_info, currency_symbol):
        self.sale = sale
        self.store_info = store_info
        self.currency_symbol = currency_symbol
        self.file_path = os.path.join('/tmp', f'invoice_{self.sale.id}.pdf')
        self.width, self.height = letter
        self.styles = self._create_styles()
        
    def _create_styles(self):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Header1',
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=14
        ))
        styles.add(ParagraphStyle(
            name='Header2',
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=10
        ))
        styles.add(ParagraphStyle(
            name='Body',
            fontSize=10,
            leading=12
        ))
        styles.add(ParagraphStyle(
            name='Right',
            fontSize=10,
            alignment=TA_RIGHT
        ))
        return styles
        
    def generate(self):
        """Generate and save the PDF invoice"""
        pdf = canvas.Canvas(self.file_path, pagesize=letter)
        
        # Header
        pdf.setTitle(f"Invoice #{self.sale.id}")
        self._draw_header(pdf)
        
        # Store and Customer Info
        self._draw_info_section(pdf)
        
        # Items Table
        self._draw_items_table(pdf)
        
        # Totals
        self._draw_totals(pdf)
        
        # Footer
        self._draw_footer(pdf)
        
        pdf.save()
        return self.file_path
        
    def _draw_header(self, pdf):
        header = Paragraph(f"<b>{self.store_info['name']}</b>", self.styles['Header1'])
        header.wrapOn(pdf, self.width-100, self.height)
        header.drawOn(pdf, 50, self.height - 50)
        
        details = [
            f"Address: {self.store_info['address']}",
            f"Phone: {self.store_info['phone']}",
            f"Email: {self.store_info['email']}"
        ]
        info_text = "<br/>".join(details)
        info = Paragraph(info_text, self.styles['Header2'])
        info.wrapOn(pdf, self.width-100, self.height)
        info.drawOn(pdf, 50, self.height - 90)
        
    def _draw_info_section(self, pdf):
        y_pos = self.height - 150
        # Invoice Info
        info_data = [
            ["Invoice Number:", self.sale.id],
            ["Invoice Date:", datetime.strptime(self.sale.date, "%Y-%m-%d").strftime("%d/%m/%Y")],
            ["Cashier ID:", self.sale.cashier_id or "N/A"]
        ]
        if self.sale.customer_name:
            info_data.append(["Customer:", self.sale.customer_name])
            
        table = Table(info_data, colWidths=[100, 100])
        table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        table.wrapOn(pdf, 200, 50)
        table.drawOn(pdf, 50, y_pos)
        
    def _draw_items_table(self, pdf):
        y_pos = self.height - 250
        headers = ['Item', 'Batch No', 'Quantity', 'Unit Price', 'Total']
        data = [headers]
        
        for item in self.sale.items:
            data.append([
                item.name,
                item.batch_no or 'N/A',
                str(item.quantity),
                f"{self.currency_symbol}{item.unit_price:.2f}",
                f"{self.currency_symbol}{item.total_price:.2f}"
            ])
            
        table = Table(data, colWidths=[150, 80, 60, 80, 80], repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        table.wrapOn(pdf, self.width-100, 100)
        table.drawOn(pdf, 50, y_pos)
        
    def _draw_totals(self, pdf):
        y_pos = self.height - 450
        totals = [
            ["Subtotal:", f"{self.currency_symbol}{self.sale.subtotal:.2f}"],
            ["Discount:", f"-{self.currency_symbol}{self.sale.discount:.2f}"],
            ["Tax:", f"{self.currency_symbol}{self.sale.tax:.2f}"],
            ["Total:", f"<b>{self.currency_symbol}{self.sale.total:.2f}</b>"]
        ]
        
        table = Table(totals, colWidths=[100, 100])
        table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (-1,-1), (-1,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        table.wrapOn(pdf, 200, 50)
        table.drawOn(pdf, self.width-250, y_pos)
        
    def _draw_footer(self, pdf):
        footer_text = "Thank you for your business! Please retain this receipt for your records."
        footer = Paragraph(footer_text, self.styles['Body'])
        footer.wrapOn(pdf, self.width-100, 50)
        footer.drawOn(pdf, 50, 50)
