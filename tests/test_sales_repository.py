"""
Unit tests for Sales Repository
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import date, timedelta

from medical_store_app.config.database import DatabaseManager
from medical_store_app.repositories.sales_repository import SalesRepository
from medical_store_app.repositories.medicine_repository import MedicineRepository
from medical_store_app.models.sale import Sale, SaleItem
from medical_store_app.models.medicine import Medicine


class TestSalesRepository:
    """Test cases for SalesRepository"""
    
    @pytest.fixture
    def db_manager(self):
        """Create a temporary database for testing"""
        # Create temporary database file
        db_fd, db_path = tempfile.mkstemp()
        os.close(db_fd)
        
        db_manager = DatabaseManager(db_path)
        db_manager.initialize()
        
        yield db_manager
        
        # Cleanup
        db_manager.close()
        os.unlink(db_path)
    
    @pytest.fixture
    def repository(self, db_manager):
        """Create sales repository instance"""
        return SalesRepository(db_manager)
    
    @pytest.fixture
    def medicine_repository(self, db_manager):
        """Create medicine repository instance for testing stock updates"""
        return MedicineRepository(db_manager)
    
    @pytest.fixture
    def sample_sale(self):
        """Create a sample sale for testing"""
        sale = Sale(
            date=date.today().isoformat(),
            payment_method="cash",
            cashier_id=None  # Use None to avoid foreign key constraint
        )
        
        # Add items to sale
        sale.add_item(
            medicine_id=1,
            name="Paracetamol",
            quantity=2,
            unit_price=8.0
        )
        sale.add_item(
            medicine_id=2,
            name="Amoxicillin",
            quantity=1,
            unit_price=18.0
        )
        
        return sale
    
    @pytest.fixture
    def sample_medicines(self, medicine_repository):
        """Create sample medicines in database for testing"""
        future_date = (date.today() + timedelta(days=365)).isoformat()
        
        medicines = [
            Medicine(
                name="Paracetamol",
                category="Pain Relief",
                batch_no="PAR001",
                expiry_date=future_date,
                quantity=100,
                purchase_price=5.0,
                selling_price=8.0,
                barcode="PAR001234567"
            ),
            Medicine(
                name="Amoxicillin",
                category="Antibiotic",
                batch_no="AMX001",
                expiry_date=future_date,
                quantity=50,
                purchase_price=12.0,
                selling_price=18.0,
                barcode="AMX001234567"
            )
        ]
        
        saved_medicines = []
        for medicine in medicines:
            saved = medicine_repository.save(medicine)
            if saved:
                saved_medicines.append(saved)
        
        return saved_medicines
    
    def test_save_sale_success(self, repository, sample_sale):
        """Test successful sale save"""
        result = repository.save(sample_sale)
        
        assert result is not None
        assert result.id is not None
        assert result.total == 34.0  # (2 * 8.0) + (1 * 18.0)
        assert len(result.items) == 2
    
    def test_save_invalid_sale(self, repository):
        """Test saving invalid sale fails"""
        invalid_sale = Sale(
            date="",  # Invalid: empty date
            payment_method="cash"
        )
        
        result = repository.save(invalid_sale)
        assert result is None
    
    def test_save_sale_without_items(self, repository):
        """Test saving sale without items fails"""
        sale_without_items = Sale(
            date=date.today().isoformat(),
            payment_method="cash"
        )
        
        result = repository.save(sale_without_items)
        assert result is None
    
    def test_find_by_id_success(self, repository, sample_sale):
        """Test finding sale by ID"""
        # Save sale first
        saved_sale = repository.save(sample_sale)
        assert saved_sale is not None
        
        # Find by ID
        found_sale = repository.find_by_id(saved_sale.id)
        assert found_sale is not None
        assert found_sale.id == saved_sale.id
        assert found_sale.total == 34.0
        assert len(found_sale.items) == 2
    
    def test_find_by_id_not_found(self, repository):
        """Test finding non-existent sale by ID"""
        result = repository.find_by_id(999)
        assert result is None
    
    def test_find_all(self, repository, sample_sale):
        """Test finding all sales"""
        # Save multiple sales
        sale1 = repository.save(sample_sale)
        
        # Create another sale
        sale2 = Sale(
            date=date.today().isoformat(),
            payment_method="card",
            cashier_id=None
        )
        sale2.add_item(3, "Aspirin", 1, 5.0)
        saved_sale2 = repository.save(sale2)
        
        # Find all
        all_sales = repository.find_all()
        assert len(all_sales) == 2
        
        # Should be ordered by date DESC, created_at DESC
        assert all_sales[0].id == saved_sale2.id  # More recent
        assert all_sales[1].id == sale1.id
    
    def test_find_all_with_limit(self, repository, sample_sale):
        """Test finding all sales with limit"""
        # Save multiple sales
        for i in range(5):
            sale = Sale(
                date=date.today().isoformat(),
                payment_method="cash"
            )
            sale.add_item(1, "Test Medicine", 1, 10.0)
            repository.save(sale)
        
        # Find with limit
        limited_sales = repository.find_all(limit=3)
        assert len(limited_sales) == 3
    
    def test_find_by_date_range(self, repository):
        """Test finding sales by date range"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        # Create sales on different dates
        sale_yesterday = Sale(date=yesterday.isoformat(), payment_method="cash")
        sale_yesterday.add_item(1, "Medicine A", 1, 10.0)
        repository.save(sale_yesterday)
        
        sale_today = Sale(date=today.isoformat(), payment_method="cash")
        sale_today.add_item(1, "Medicine B", 1, 15.0)
        repository.save(sale_today)
        
        sale_tomorrow = Sale(date=tomorrow.isoformat(), payment_method="cash")
        sale_tomorrow.add_item(1, "Medicine C", 1, 20.0)
        repository.save(sale_tomorrow)
        
        # Find sales for today only
        today_sales = repository.find_by_date_range(today.isoformat(), today.isoformat())
        assert len(today_sales) == 1
        assert today_sales[0].items[0].name == "Medicine B"
        
        # Find sales for yesterday to today
        range_sales = repository.find_by_date_range(yesterday.isoformat(), today.isoformat())
        assert len(range_sales) == 2
    
    def test_find_by_cashier(self, repository, db_manager):
        """Test finding sales by cashier"""
        # First create test users to avoid foreign key constraint
        with db_manager.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, is_active)
                VALUES (?, ?, ?, ?)
            """, ("cashier1", "hash1", "cashier", 1))
            cashier1_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, is_active)
                VALUES (?, ?, ?, ?)
            """, ("cashier2", "hash2", "cashier", 1))
            cashier2_id = cursor.lastrowid
        
        # Create sales by different cashiers
        sale1 = Sale(date=date.today().isoformat(), payment_method="cash", cashier_id=cashier1_id)
        sale1.add_item(1, "Medicine A", 1, 10.0)
        repository.save(sale1)
        
        sale2 = Sale(date=date.today().isoformat(), payment_method="cash", cashier_id=cashier2_id)
        sale2.add_item(1, "Medicine B", 1, 15.0)
        repository.save(sale2)
        
        sale3 = Sale(date=date.today().isoformat(), payment_method="cash", cashier_id=cashier1_id)
        sale3.add_item(1, "Medicine C", 1, 20.0)
        repository.save(sale3)
        
        # Find sales by cashier 1
        cashier1_sales = repository.find_by_cashier(cashier1_id)
        assert len(cashier1_sales) == 2
        
        # Find sales by cashier 2
        cashier2_sales = repository.find_by_cashier(cashier2_id)
        assert len(cashier2_sales) == 1
    
    def test_get_daily_sales(self, repository):
        """Test getting daily sales"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Create sales on different dates
        sale_yesterday = Sale(date=yesterday.isoformat(), payment_method="cash")
        sale_yesterday.add_item(1, "Medicine A", 1, 10.0)
        repository.save(sale_yesterday)
        
        sale_today1 = Sale(date=today.isoformat(), payment_method="cash")
        sale_today1.add_item(1, "Medicine B", 1, 15.0)
        repository.save(sale_today1)
        
        sale_today2 = Sale(date=today.isoformat(), payment_method="card")
        sale_today2.add_item(1, "Medicine C", 1, 20.0)
        repository.save(sale_today2)
        
        # Get today's sales
        today_sales = repository.get_daily_sales(today.isoformat())
        assert len(today_sales) == 2
        
        # Get yesterday's sales
        yesterday_sales = repository.get_daily_sales(yesterday.isoformat())
        assert len(yesterday_sales) == 1
        
        # Get sales for default date (today)
        default_sales = repository.get_daily_sales()
        assert len(default_sales) == 2
    
    def test_get_sales_analytics(self, repository):
        """Test getting sales analytics"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Create test sales
        sale1 = Sale(date=yesterday.isoformat(), payment_method="cash")
        sale1.add_item(1, "Medicine A", 2, 10.0)
        sale1.discount = 2.0
        sale1.tax = 1.8
        sale1.calculate_totals()
        repository.save(sale1)
        
        sale2 = Sale(date=today.isoformat(), payment_method="card")
        sale2.add_item(1, "Medicine B", 1, 15.0)
        sale2.tax = 1.5
        sale2.calculate_totals()
        repository.save(sale2)
        
        # Get analytics
        analytics = repository.get_sales_analytics(
            yesterday.isoformat(),
            today.isoformat()
        )
        
        assert analytics['summary']['total_transactions'] == 2
        assert analytics['summary']['total_revenue'] == 36.3  # 19.8 + 16.5 (corrected calculation)
        assert analytics['summary']['total_discounts'] == 2.0
        assert analytics['summary']['total_tax'] == 3.3  # 1.8 + 1.5
        
        assert len(analytics['daily_breakdown']) == 2
        assert len(analytics['payment_methods']) == 2
    
    def test_get_top_selling_medicines(self, repository):
        """Test getting top selling medicines"""
        today = date.today()
        
        # Create sales with different medicines
        sale1 = Sale(date=today.isoformat(), payment_method="cash")
        sale1.add_item(1, "Paracetamol", 5, 8.0)  # Revenue: 40.0
        sale1.add_item(2, "Amoxicillin", 2, 18.0)  # Revenue: 36.0
        repository.save(sale1)
        
        sale2 = Sale(date=today.isoformat(), payment_method="cash")
        sale2.add_item(1, "Paracetamol", 3, 8.0)  # Additional revenue: 24.0, Total: 64.0
        sale2.add_item(3, "Aspirin", 10, 5.0)  # Revenue: 50.0
        repository.save(sale2)
        
        # Get top selling medicines
        top_medicines = repository.get_top_selling_medicines(
            today.isoformat(),
            today.isoformat(),
            limit=3
        )
        
        assert len(top_medicines) == 3
        
        # Should be sorted by revenue (descending)
        assert top_medicines[0]['name'] == "Paracetamol"
        assert top_medicines[0]['total_revenue'] == 64.0
        assert top_medicines[0]['total_quantity'] == 8
        
        assert top_medicines[1]['name'] == "Aspirin"
        assert top_medicines[1]['total_revenue'] == 50.0
        
        assert top_medicines[2]['name'] == "Amoxicillin"
        assert top_medicines[2]['total_revenue'] == 36.0
    
    def test_update_medicine_stock_after_sale(self, repository, medicine_repository, sample_medicines):
        """Test updating medicine stock after sale"""
        # Create a sale
        sale = Sale(date=date.today().isoformat(), payment_method="cash")
        sale.add_item(sample_medicines[0].id, "Paracetamol", 5, 8.0)
        sale.add_item(sample_medicines[1].id, "Amoxicillin", 3, 18.0)
        saved_sale = repository.save(sale)
        
        # Update stock
        result = repository.update_medicine_stock_after_sale(saved_sale)
        assert result is True
        
        # Verify stock was reduced
        updated_medicine1 = medicine_repository.find_by_id(sample_medicines[0].id)
        assert updated_medicine1.quantity == 95  # 100 - 5
        
        updated_medicine2 = medicine_repository.find_by_id(sample_medicines[1].id)
        assert updated_medicine2.quantity == 47  # 50 - 3
    
    def test_update_medicine_stock_insufficient_quantity(self, repository, medicine_repository, sample_medicines):
        """Test updating medicine stock with insufficient quantity"""
        # Create a sale with more quantity than available
        sale = Sale(date=date.today().isoformat(), payment_method="cash")
        sale.add_item(sample_medicines[0].id, "Paracetamol", 150, 8.0)  # More than available (100)
        saved_sale = repository.save(sale)
        
        # Try to update stock
        result = repository.update_medicine_stock_after_sale(saved_sale)
        assert result is False
        
        # Verify stock was not changed
        unchanged_medicine = medicine_repository.find_by_id(sample_medicines[0].id)
        assert unchanged_medicine.quantity == 100  # Unchanged
    
    def test_get_total_sales_count(self, repository, sample_sale):
        """Test getting total sales count"""
        # Initially should be 0
        count = repository.get_total_sales_count()
        assert count == 0
        
        # Save sales
        repository.save(sample_sale)
        
        sale2 = Sale(date=date.today().isoformat(), payment_method="card")
        sale2.add_item(1, "Test Medicine", 1, 10.0)
        repository.save(sale2)
        
        # Should now be 2
        count = repository.get_total_sales_count()
        assert count == 2
    
    def test_get_total_revenue(self, repository):
        """Test getting total revenue"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Initially should be 0
        revenue = repository.get_total_revenue()
        assert revenue == 0.0
        
        # Create sales
        sale1 = Sale(date=yesterday.isoformat(), payment_method="cash")
        sale1.add_item(1, "Medicine A", 1, 10.0)
        repository.save(sale1)
        
        sale2 = Sale(date=today.isoformat(), payment_method="cash")
        sale2.add_item(1, "Medicine B", 1, 15.0)
        repository.save(sale2)
        
        # Total revenue
        total_revenue = repository.get_total_revenue()
        assert total_revenue == 25.0
        
        # Revenue for specific date range
        today_revenue = repository.get_total_revenue(today.isoformat(), today.isoformat())
        assert today_revenue == 15.0
    
    def test_get_recent_sales(self, repository):
        """Test getting recent sales"""
        # Create multiple sales
        for i in range(5):
            sale = Sale(date=date.today().isoformat(), payment_method="cash")
            sale.add_item(1, f"Medicine {i}", 1, 10.0 + i)
            repository.save(sale)
        
        # Get recent sales
        recent_sales = repository.get_recent_sales(limit=3)
        assert len(recent_sales) == 3
        
        # Should be ordered by created_at DESC (most recent first)
        assert recent_sales[0].items[0].name == "Medicine 4"  # Last created
        assert recent_sales[1].items[0].name == "Medicine 3"
        assert recent_sales[2].items[0].name == "Medicine 2"
    
    def test_delete_sale_success(self, repository, sample_sale):
        """Test successful sale deletion"""
        # Save sale first
        saved_sale = repository.save(sample_sale)
        assert saved_sale is not None
        
        # Delete sale
        result = repository.delete(saved_sale.id)
        assert result is True
        
        # Verify deletion
        deleted_sale = repository.find_by_id(saved_sale.id)
        assert deleted_sale is None
    
    def test_delete_nonexistent_sale(self, repository):
        """Test deleting non-existent sale"""
        result = repository.delete(999)
        assert result is False