import os
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

class InvoiceGenerator:
    def __init__(self, sale, store_info, currency_symbol="Rs."):
        self.sale = sale
        self.store_info = store_info
        self.currency_symbol = currency_symbol
        self.output_path = os.path.join(tempfile.gettempdir(), f"invoice_{sale.id}.pdf")
        
    def generate(self):
        try:
            # Create PDF canvas
            c = canvas.Canvas(self.output_path, pagesize=letter)
            
            # Set up document coordinates
            width, height = letter
            margin = 0.5 * inch
            current_height = height - margin
            
            # Add store header
            self._draw_header(c, current_height)
            current_height -= 1.5 * inch
            
            # Add customer/sale info
            self._draw_sale_info(c, current_height)
            current_height -= 1.0 * inch
            
            # Add items table
            self._draw_items_table(c, current_height)
            
            # Add totals
            self._draw_totals(c, 1.5 * inch)
            
            # Save PDF
            c.save()
            return self.output_path
            
        except Exception as e:
            raise Exception(f"Invoice generation failed: {str(e)}") from e

    def _draw_header(self, c, y_pos):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0.5 * inch, y_pos, self.store_info.get('name', 'Medical Store'))
        
        c.setFont("Helvetica", 10)
        y_pos -= 0.25 * inch
        c.drawString(0.5 * inch, y_pos, self.store_info.get('address', ''))
        
        y_pos -= 0.25 * inch
        contact_info = f"{self.store_info.get('phone', '')} | {self.store_info.get('email', '')}"
        c.drawString(0.5 * inch, y_pos, contact_info)
        
        c.line(0.5 * inch, y_pos - 0.1 * inch, width - 0.5 * inch, y_pos - 0.1 * inch)

    def _draw_sale_info(self, c, y_pos):
        c.setFont("Helvetica", 10)
        c.drawRightString(width - 0.5 * inch, y_pos, f"Invoice #: {self.sale.id}")
        y_pos -= 0.25 * inch
        c.drawRightString(width - 0.5 * inch, y_pos, f"Date: {self.sale.date}")
        
        if self.sale.customer_name:
            y_pos -= 0.5 * inch
            c.drawString(0.5 * inch, y_pos, f"Customer: {self.sale.customer_name}")

    def _draw_items_table(self, c, y_pos):
        styles = getSampleStyleSheet()
        styleN = styles["BodyText"]
        styleN.alignment = 1  # Center alignment
        
        data = [["Item", "Price", "Qty", "Total"]]
        for item in self.sale.items:
            data.append([
                item.name,
                f"{self.currency_symbol}{item.unit_price:.2f}",
                str(item.quantity),
                f"{self.currency_symbol}{item.total_price:.2f}"
            ])
            
        table = Table(data, colWidths=[3*inch, inch, inch, inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        
        table.wrapOn(c, width, height)
        table.drawOn(c, 0.5 * inch, y_pos - table._height)

    def _draw_totals(self, c, y_pos):
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(width - 0.5 * inch, y_pos, 
                        f"Total: {self.currency_symbol}{self.sale.total:.2f}")
