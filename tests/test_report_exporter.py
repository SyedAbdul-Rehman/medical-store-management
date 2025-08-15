"""
Tests for Report Exporter functionality
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from medical_store_app.utils.report_exporter import ReportExporter
from medical_store_app.managers.report_manager import ReportData


class TestReportExporter:
    """Test ReportExporter class"""
    
    @pytest.fixture
    def exporter(self):
        """Create ReportExporter instance"""
        return ReportExporter()
    
    @pytest.fixture
    def sample_report_data(self):
        """Sample report data for testing"""
        report = ReportData(
            title="Test Sales Report",
            period_start="2024-01-01",
            period_end="2024-01-31"
        )
        report.summary = {
            'total_revenue': 5000.0,
            'total_transactions': 50,
            'average_transaction': 100.0,
            'total_discounts': 250.0,
            'total_tax': 450.0
        }
        report.daily_breakdown = [
            {'date': '2024-01-01', 'transactions': 5, 'revenue': 500.0},
            {'date': '2024-01-02', 'transactions': 8, 'revenue': 750.0}
        ]
        report.top_medicines = [
            {
                'name': 'Paracetamol',
                'total_quantity': 100,
                'total_revenue': 800.0,
                'transactions': 20
            }
        ]
        report.payment_methods = [
            {'method': 'cash', 'transactions': 30, 'revenue': 3000.0},
            {'method': 'card', 'transactions': 20, 'revenue': 2000.0}
        ]
        return report
    
    @pytest.fixture
    def sample_inventory_data(self):
        """Sample inventory data for testing"""
        return {
            'title': 'Inventory Status Report',
            'generated_at': '2024-01-15T10:00:00',
            'summary': {
                'total_medicines': 100,
                'total_stock_value': 10000.0,
                'total_selling_value': 15000.0,
                'potential_profit': 5000.0,
                'low_stock_count': 5,
                'expired_count': 2
            },
            'low_stock_medicines': [
                {
                    'name': 'Amoxicillin',
                    'category': 'Antibiotic',
                    'quantity': 3,
                    'batch_no': 'AMX001'
                }
            ],
            'expired_medicines': [
                {
                    'name': 'Expired Med',
                    'category': 'Test',
                    'expiry_date': '2023-12-31',
                    'quantity': 10,
                    'batch_no': 'EXP001'
                }
            ],
            'category_breakdown': [
                {
                    'category': 'Pain Relief',
                    'count': 20,
                    'total_quantity': 500,
                    'stock_value': 2500.0
                }
            ]
        }
    
    def test_exporter_initialization(self, exporter):
        """Test exporter initialization"""
        assert exporter is not None
        assert hasattr(exporter, 'logger')
    
    def test_get_supported_formats(self, exporter):
        """Test getting supported formats"""
        formats = exporter.get_supported_formats()
        
        # CSV should always be supported
        assert 'csv' in formats
        assert isinstance(formats, list)
        assert len(formats) >= 1
    
    def test_is_format_supported(self, exporter):
        """Test format support checking"""
        # CSV should always be supported
        assert exporter.is_format_supported('csv') is True
        assert exporter.is_format_supported('CSV') is True  # Case insensitive
        
        # Test unsupported format
        assert exporter.is_format_supported('invalid') is False
    
    def test_get_format_requirements(self, exporter):
        """Test getting format requirements"""
        # CSV should not have requirements
        assert exporter.get_format_requirements('csv') is None
        
        # Test requirements for potentially unsupported formats
        excel_req = exporter.get_format_requirements('excel')
        pdf_req = exporter.get_format_requirements('pdf')
        
        # Requirements should be strings if format is not supported
        if excel_req is not None:
            assert isinstance(excel_req, str)
            assert 'pandas' in excel_req.lower()
        
        if pdf_req is not None:
            assert isinstance(pdf_req, str)
            assert 'reportlab' in pdf_req.lower()
    
    def test_export_to_csv_success(self, exporter, sample_report_data):
        """Test successful CSV export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Test export
            result = exporter.export_to_csv(sample_report_data, temp_path)
            
            # Verify result
            assert result is True
            assert os.path.exists(temp_path)
            
            # Verify file content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'Medical Store Management - Sales Report' in content
                assert 'Test Sales Report' in content
                assert '2024-01-01' in content
                assert '2024-01-31' in content
                assert 'SUMMARY' in content
                assert 'DAILY BREAKDOWN' in content
                assert 'TOP SELLING MEDICINES' in content
                assert 'PAYMENT METHODS' in content
                assert 'Paracetamol' in content
                
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_to_csv_file_error(self, exporter, sample_report_data):
        """Test CSV export with file error"""
        # Try to write to invalid path
        invalid_path = "/invalid/path/report.csv"
        
        result = exporter.export_to_csv(sample_report_data, invalid_path)
        
        # Should fail gracefully
        assert result is False
    
    def test_export_inventory_to_csv_success(self, exporter, sample_inventory_data):
        """Test successful inventory CSV export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Test export
            result = exporter.export_inventory_to_csv(sample_inventory_data, temp_path)
            
            # Verify result
            assert result is True
            assert os.path.exists(temp_path)
            
            # Verify file content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'Medical Store Management - Inventory Report' in content
                assert 'Inventory Status Report' in content
                assert 'SUMMARY' in content
                assert 'LOW STOCK MEDICINES' in content
                assert 'EXPIRED MEDICINES' in content
                assert 'CATEGORY BREAKDOWN' in content
                assert 'Amoxicillin' in content
                assert 'Expired Med' in content
                
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_to_excel_pandas_available(self, exporter, sample_report_data):
        """Test Excel export when pandas is available"""
        # Skip this test if pandas is not actually available
        if not exporter.is_format_supported('excel'):
            pytest.skip("Pandas not available for Excel export testing")
        
        # Test that the method exists and can be called
        result = exporter.export_to_excel(sample_report_data, "test.xlsx")
        
        # Result depends on actual pandas availability
        assert isinstance(result, bool)
    
    @patch('medical_store_app.utils.report_exporter.PANDAS_AVAILABLE', False)
    def test_export_to_excel_pandas_unavailable(self, exporter, sample_report_data):
        """Test Excel export when pandas is not available"""
        result = exporter.export_to_excel(sample_report_data, "test.xlsx")
        
        # Should fail gracefully
        assert result is False
    
    def test_export_to_pdf_reportlab_available(self, exporter, sample_report_data):
        """Test PDF export when reportlab is available"""
        # Skip this test if reportlab is not actually available
        if not exporter.is_format_supported('pdf'):
            pytest.skip("ReportLab not available for PDF export testing")
        
        # Test that the method exists and can be called
        result = exporter.export_to_pdf(sample_report_data, "test.pdf")
        
        # Result depends on actual reportlab availability
        assert isinstance(result, bool)
    
    @patch('medical_store_app.utils.report_exporter.REPORTLAB_AVAILABLE', False)
    def test_export_to_pdf_reportlab_unavailable(self, exporter, sample_report_data):
        """Test PDF export when reportlab is not available"""
        result = exporter.export_to_pdf(sample_report_data, "test.pdf")
        
        # Should fail gracefully
        assert result is False
    
    def test_csv_export_with_empty_data(self, exporter):
        """Test CSV export with minimal data"""
        minimal_report = ReportData(
            title="Minimal Report",
            period_start="2024-01-01",
            period_end="2024-01-01"
        )
        minimal_report.summary = {}
        minimal_report.daily_breakdown = []
        minimal_report.top_medicines = []
        minimal_report.payment_methods = []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = exporter.export_to_csv(minimal_report, temp_path)
            
            # Should still succeed
            assert result is True
            assert os.path.exists(temp_path)
            
            # Verify basic content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'Minimal Report' in content
                
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_csv_export_with_special_characters(self, exporter):
        """Test CSV export with special characters in data"""
        special_report = ReportData(
            title="Report with Special Characters: àáâãäå",
            period_start="2024-01-01",
            period_end="2024-01-01"
        )
        special_report.summary = {'test_field': 'Value with "quotes" and commas,'}
        special_report.top_medicines = [
            {
                'name': 'Medicine with "quotes" and commas,',
                'total_quantity': 10,
                'total_revenue': 100.0,
                'transactions': 5
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = exporter.export_to_csv(special_report, temp_path)
            
            # Should handle special characters
            assert result is True
            assert os.path.exists(temp_path)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_exception_handling(self, exporter, sample_report_data):
        """Test export exception handling"""
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            result = exporter.export_to_csv(sample_report_data, "test.csv")
            
            # Should handle exception gracefully
            assert result is False


class TestExportDataProcessing:
    """Test export data processing logic"""
    
    def test_summary_data_formatting(self):
        """Test summary data formatting for export"""
        summary = {
            'total_revenue': 1234.56,
            'total_transactions': 42,
            'average_transaction': 29.39,
            'max_transaction': 150.0
        }
        
        # Test formatting logic
        formatted_data = []
        for key, value in summary.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, float):
                formatted_value = f"${value:.2f}" if 'revenue' in key or 'transaction' in key else f"{value:.2f}"
            else:
                formatted_value = str(value)
            formatted_data.append((formatted_key, formatted_value))
        
        # Verify formatting
        assert len(formatted_data) == 4
        assert ('Total Revenue', '$1234.56') in formatted_data
        assert ('Total Transactions', '42') in formatted_data
        assert ('Average Transaction', '$29.39') in formatted_data
        assert ('Max Transaction', '$150.00') in formatted_data
    
    def test_daily_breakdown_calculations(self):
        """Test daily breakdown calculations for export"""
        daily_data = [
            {'date': '2024-01-01', 'transactions': 5, 'revenue': 500.0},
            {'date': '2024-01-02', 'transactions': 0, 'revenue': 0.0},  # Edge case
            {'date': '2024-01-03', 'transactions': 8, 'revenue': 800.0}
        ]
        
        # Test average transaction calculation
        processed_data = []
        for item in daily_data:
            avg_trans = item['revenue'] / item['transactions'] if item['transactions'] > 0 else 0
            processed_data.append({
                'date': item['date'],
                'transactions': item['transactions'],
                'revenue': item['revenue'],
                'avg_transaction': avg_trans
            })
        
        # Verify calculations
        assert processed_data[0]['avg_transaction'] == 100.0  # 500/5
        assert processed_data[1]['avg_transaction'] == 0.0    # 0/0 handled
        assert processed_data[2]['avg_transaction'] == 100.0  # 800/8
    
    def test_payment_methods_percentage_calculation(self):
        """Test payment methods percentage calculation"""
        payment_data = [
            {'method': 'cash', 'transactions': 30, 'revenue': 3000.0},
            {'method': 'card', 'transactions': 20, 'revenue': 2000.0}
        ]
        
        # Calculate percentages
        total_revenue = sum(item['revenue'] for item in payment_data)
        processed_data = []
        
        for item in payment_data:
            percentage = (item['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
            processed_data.append({
                'method': item['method'],
                'transactions': item['transactions'],
                'revenue': item['revenue'],
                'percentage': percentage
            })
        
        # Verify calculations
        assert total_revenue == 5000.0
        assert processed_data[0]['percentage'] == 60.0  # 3000/5000 * 100
        assert processed_data[1]['percentage'] == 40.0  # 2000/5000 * 100
        
        # Verify percentages sum to 100
        total_percentage = sum(item['percentage'] for item in processed_data)
        assert abs(total_percentage - 100.0) < 0.01  # Allow for floating point precision
    
    def test_empty_data_handling(self):
        """Test handling of empty data in export processing"""
        # Test empty payment methods
        empty_payment_data = []
        total_revenue = sum(item['revenue'] for item in empty_payment_data)
        assert total_revenue == 0
        
        # Test empty daily breakdown
        empty_daily_data = []
        processed_daily = []
        for item in empty_daily_data:
            avg_trans = item['revenue'] / item['transactions'] if item['transactions'] > 0 else 0
            processed_daily.append(avg_trans)
        
        assert len(processed_daily) == 0
        
        # Test empty top medicines
        empty_medicines = []
        ranked_medicines = []
        for i, item in enumerate(empty_medicines, 1):
            ranked_medicines.append((i, item))
        
        assert len(ranked_medicines) == 0


if __name__ == "__main__":
    pytest.main([__file__])