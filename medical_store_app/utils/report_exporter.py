"""
Report Exporter for Medical Store Management Application
Handles exporting reports to various formats (CSV, Excel, PDF)
"""

import logging
import csv
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import io

def _check_pandas_available():
    """Dynamically check if pandas is available"""
    try:
        import pandas as pd
        return True
    except ImportError:
        return False

def _check_reportlab_available():
    """Dynamically check if reportlab is available"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        return True
    except ImportError:
        return False

from ..managers.report_manager import ReportData


class ReportExporter:
    """Class for exporting reports to various formats"""
    
    def __init__(self):
        """Initialize report exporter"""
        self.logger = logging.getLogger(__name__)
    
    def export_to_csv(self, report_data: ReportData, file_path: str) -> bool:
        """
        Export report data to CSV format
        
        Args:
            report_data: Report data to export
            file_path: Path to save the CSV file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            self.logger.info(f"Exporting report to CSV: {file_path}")
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header information
                writer.writerow(['Medical Store Management - Sales Report'])
                writer.writerow(['Report Title:', report_data.title])
                writer.writerow(['Period:', f"{report_data.period_start} to {report_data.period_end}"])
                writer.writerow(['Generated:', report_data.generated_at])
                writer.writerow([])  # Empty row
                
                # Write summary section
                writer.writerow(['SUMMARY'])
                for key, value in report_data.summary.items():
                    formatted_key = key.replace('_', ' ').title()
                    if isinstance(value, float):
                        formatted_value = f"${value:.2f}" if 'revenue' in key or 'transaction' in key else f"{value:.2f}"
                    else:
                        formatted_value = str(value)
                    writer.writerow([formatted_key, formatted_value])
                writer.writerow([])  # Empty row
                
                # Write daily breakdown section
                if report_data.daily_breakdown:
                    writer.writerow(['DAILY BREAKDOWN'])
                    writer.writerow(['Date', 'Transactions', 'Revenue ($)', 'Avg Transaction ($)'])
                    
                    for item in report_data.daily_breakdown:
                        avg_trans = item['revenue'] / item['transactions'] if item['transactions'] > 0 else 0
                        writer.writerow([
                            item['date'],
                            item['transactions'],
                            f"{item['revenue']:.2f}",
                            f"{avg_trans:.2f}"
                        ])
                    writer.writerow([])  # Empty row
                
                # Write top medicines section
                if report_data.top_medicines:
                    writer.writerow(['TOP SELLING MEDICINES'])
                    writer.writerow(['Rank', 'Medicine Name', 'Quantity Sold', 'Revenue ($)', 'Transactions'])
                    
                    for i, item in enumerate(report_data.top_medicines, 1):
                        writer.writerow([
                            i,
                            item['name'],
                            item['total_quantity'],
                            f"{item['total_revenue']:.2f}",
                            item['transactions']
                        ])
                    writer.writerow([])  # Empty row
                
                # Write payment methods section
                if report_data.payment_methods:
                    writer.writerow(['PAYMENT METHODS'])
                    writer.writerow(['Method', 'Transactions', 'Revenue ($)', 'Percentage'])
                    
                    total_revenue = sum(item['revenue'] for item in report_data.payment_methods)
                    for item in report_data.payment_methods:
                        percentage = (item['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
                        writer.writerow([
                            item['method'].title(),
                            item['transactions'],
                            f"{item['revenue']:.2f}",
                            f"{percentage:.1f}%"
                        ])
            
            self.logger.info(f"CSV export completed successfully: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def export_to_excel(self, report_data: ReportData, file_path: str) -> bool:
        """
        Export report data to Excel format
        
        Args:
            report_data: Report data to export
            file_path: Path to save the Excel file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            if not _check_pandas_available():
                self.logger.error("Pandas not available for Excel export")
                return False
            
            self.logger.info(f"Exporting report to Excel: {file_path}")
            
            import pandas as pd
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = []
                for key, value in report_data.summary.items():
                    formatted_key = key.replace('_', ' ').title()
                    if isinstance(value, float):
                        formatted_value = f"${value:.2f}" if 'revenue' in key or 'transaction' in key else f"{value:.2f}"
                    else:
                        formatted_value = str(value)
                    summary_data.append({'Metric': formatted_key, 'Value': formatted_value})
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Daily breakdown sheet
                if report_data.daily_breakdown:
                    daily_data = []
                    for item in report_data.daily_breakdown:
                        avg_trans = item['revenue'] / item['transactions'] if item['transactions'] > 0 else 0
                        daily_data.append({
                            'Date': item['date'],
                            'Transactions': item['transactions'],
                            'Revenue ($)': item['revenue'],
                            'Avg Transaction ($)': avg_trans
                        })
                    
                    daily_df = pd.DataFrame(daily_data)
                    daily_df.to_excel(writer, sheet_name='Daily Breakdown', index=False)
                
                # Top medicines sheet
                if report_data.top_medicines:
                    medicines_data = []
                    for i, item in enumerate(report_data.top_medicines, 1):
                        medicines_data.append({
                            'Rank': i,
                            'Medicine Name': item['name'],
                            'Quantity Sold': item['total_quantity'],
                            'Revenue ($)': item['total_revenue'],
                            'Transactions': item['transactions']
                        })
                    
                    medicines_df = pd.DataFrame(medicines_data)
                    medicines_df.to_excel(writer, sheet_name='Top Medicines', index=False)
                
                # Payment methods sheet
                if report_data.payment_methods:
                    payment_data = []
                    total_revenue = sum(item['revenue'] for item in report_data.payment_methods)
                    for item in report_data.payment_methods:
                        percentage = (item['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
                        payment_data.append({
                            'Method': item['method'].title(),
                            'Transactions': item['transactions'],
                            'Revenue ($)': item['revenue'],
                            'Percentage': f"{percentage:.1f}%"
                        })
                    
                    payment_df = pd.DataFrame(payment_data)
                    payment_df.to_excel(writer, sheet_name='Payment Methods', index=False)
            
            self.logger.info(f"Excel export completed successfully: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {e}")
            return False
    
    def export_to_pdf(self, report_data: ReportData, file_path: str) -> bool:
        """
        Export report data to PDF format
        
        Args:
            report_data: Report data to export
            file_path: Path to save the PDF file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            if not _check_reportlab_available():
                self.logger.error("ReportLab not available for PDF export")
                return False
            
            self.logger.info(f"Exporting report to PDF: {file_path}")
            
            # Import reportlab components
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.HexColor('#2D9CDB')
            )
            
            # Title
            story.append(Paragraph("Medical Store Management", title_style))
            story.append(Paragraph(report_data.title, title_style))
            story.append(Spacer(1, 12))
            
            # Report info
            info_data = [
                ['Period:', f"{report_data.period_start} to {report_data.period_end}"],
                ['Generated:', datetime.fromisoformat(report_data.generated_at).strftime('%Y-%m-%d %H:%M:%S')]
            ]
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Summary section
            story.append(Paragraph("Summary", heading_style))
            summary_data = [['Metric', 'Value']]
            for key, value in report_data.summary.items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, float):
                    formatted_value = f"${value:.2f}" if 'revenue' in key or 'transaction' in key else f"{value:.2f}"
                else:
                    formatted_value = str(value)
                summary_data.append([formatted_key, formatted_value])
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D9CDB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Daily breakdown section
            if report_data.daily_breakdown:
                story.append(Paragraph("Daily Breakdown", heading_style))
                daily_data = [['Date', 'Transactions', 'Revenue ($)', 'Avg Transaction ($)']]
                for item in report_data.daily_breakdown:
                    avg_trans = item['revenue'] / item['transactions'] if item['transactions'] > 0 else 0
                    daily_data.append([
                        item['date'],
                        str(item['transactions']),
                        f"${item['revenue']:.2f}",
                        f"${avg_trans:.2f}"
                    ])
                
                daily_table = Table(daily_data, colWidths=[1.5*inch, 1.2*inch, 1.5*inch, 1.5*inch])
                daily_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(daily_table)
                story.append(Spacer(1, 20))
            
            # Top medicines section
            if report_data.top_medicines:
                story.append(Paragraph("Top Selling Medicines", heading_style))
                medicines_data = [['Rank', 'Medicine Name', 'Qty Sold', 'Revenue ($)', 'Transactions']]
                for i, item in enumerate(report_data.top_medicines[:10], 1):  # Limit to top 10
                    medicines_data.append([
                        str(i),
                        item['name'],
                        str(item['total_quantity']),
                        f"${item['total_revenue']:.2f}",
                        str(item['transactions'])
                    ])
                
                medicines_table = Table(medicines_data, colWidths=[0.7*inch, 2.5*inch, 1*inch, 1.2*inch, 1*inch])
                medicines_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F2C94C')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Medicine names left-aligned
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(medicines_table)
                story.append(Spacer(1, 20))
            
            # Payment methods section
            if report_data.payment_methods:
                story.append(Paragraph("Payment Methods", heading_style))
                payment_data = [['Method', 'Transactions', 'Revenue ($)', 'Percentage']]
                total_revenue = sum(item['revenue'] for item in report_data.payment_methods)
                for item in report_data.payment_methods:
                    percentage = (item['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
                    payment_data.append([
                        item['method'].title(),
                        str(item['transactions']),
                        f"${item['revenue']:.2f}",
                        f"{percentage:.1f}%"
                    ])
                
                payment_table = Table(payment_data, colWidths=[1.5*inch, 1.2*inch, 1.5*inch, 1.2*inch])
                payment_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9B59B6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(payment_table)
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"PDF export completed successfully: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to PDF: {e}")
            return False
    
    def export_inventory_to_csv(self, inventory_data: Dict[str, Any], file_path: str) -> bool:
        """
        Export inventory report data to CSV format
        
        Args:
            inventory_data: Inventory report data to export
            file_path: Path to save the CSV file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            self.logger.info(f"Exporting inventory report to CSV: {file_path}")
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header information
                writer.writerow(['Medical Store Management - Inventory Report'])
                writer.writerow(['Report Title:', inventory_data.get('title', 'Inventory Status Report')])
                writer.writerow(['Generated:', inventory_data.get('generated_at', datetime.now().isoformat())])
                writer.writerow([])  # Empty row
                
                # Write summary section
                summary = inventory_data.get('summary', {})
                writer.writerow(['SUMMARY'])
                writer.writerow(['Total Medicines', summary.get('total_medicines', 0)])
                writer.writerow(['Total Stock Value', f"${summary.get('total_stock_value', 0):.2f}"])
                writer.writerow(['Total Selling Value', f"${summary.get('total_selling_value', 0):.2f}"])
                writer.writerow(['Potential Profit', f"${summary.get('potential_profit', 0):.2f}"])
                writer.writerow(['Low Stock Count', summary.get('low_stock_count', 0)])
                writer.writerow(['Expired Count', summary.get('expired_count', 0)])
                writer.writerow([])  # Empty row
                
                # Write low stock medicines section
                low_stock = inventory_data.get('low_stock_medicines', [])
                if low_stock:
                    writer.writerow(['LOW STOCK MEDICINES'])
                    writer.writerow(['Medicine Name', 'Category', 'Quantity', 'Batch No'])
                    for item in low_stock:
                        writer.writerow([
                            item['name'],
                            item['category'],
                            item['quantity'],
                            item['batch_no']
                        ])
                    writer.writerow([])  # Empty row
                
                # Write expired medicines section
                expired = inventory_data.get('expired_medicines', [])
                if expired:
                    writer.writerow(['EXPIRED MEDICINES'])
                    writer.writerow(['Medicine Name', 'Category', 'Expiry Date', 'Quantity', 'Batch No'])
                    for item in expired:
                        writer.writerow([
                            item['name'],
                            item['category'],
                            item['expiry_date'],
                            item['quantity'],
                            item['batch_no']
                        ])
                    writer.writerow([])  # Empty row
                
                # Write category breakdown section
                categories = inventory_data.get('category_breakdown', [])
                if categories:
                    writer.writerow(['CATEGORY BREAKDOWN'])
                    writer.writerow(['Category', 'Medicine Count', 'Total Quantity', 'Stock Value ($)'])
                    for item in categories:
                        writer.writerow([
                            item['category'],
                            item['count'],
                            item['total_quantity'],
                            f"{item['stock_value']:.2f}"
                        ])
            
            self.logger.info(f"Inventory CSV export completed successfully: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting inventory to CSV: {e}")
            return False
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported export formats
        
        Returns:
            List of supported format strings
        """
        formats = ['csv']
        
        if _check_pandas_available():
            formats.append('excel')
        
        if _check_reportlab_available():
            formats.append('pdf')
        
        return formats
    
    def is_format_supported(self, format_type: str) -> bool:
        """
        Check if export format is supported
        
        Args:
            format_type: Format to check ('csv', 'excel', 'pdf')
            
        Returns:
            True if format is supported, False otherwise
        """
        return format_type.lower() in self.get_supported_formats()
    
    def get_format_requirements(self, format_type: str) -> Optional[str]:
        """
        Get requirements message for unsupported formats
        
        Args:
            format_type: Format to check
            
        Returns:
            Requirements message or None if supported
        """
        format_type = format_type.lower()
        
        if format_type == 'excel' and not _check_pandas_available():
            return "Excel export requires pandas and openpyxl packages. Install with: pip install pandas openpyxl"
        
        if format_type == 'pdf' and not _check_reportlab_available():
            return "PDF export requires reportlab package. Install with: pip install reportlab"
        
        return None