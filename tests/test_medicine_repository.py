"""
Unit tests for Medicine Repository
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import date, timedelta

from medical_store_app.config.database import DatabaseManager
from medical_store_app.repositories.medicine_repository import MedicineRepository
from medical_store_app.models.medicine import Medicine


class TestMedicineRepository:
    """Test cases for MedicineRepository"""
    
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
        """Create medicine repository instance"""
        return MedicineRepository(db_manager)
    
    @pytest.fixture
    def sample_medicine(self):
        """Create a sample medicine for testing"""
        return Medicine(
            name="Paracetamol",
            category="Pain Relief",
            batch_no="PAR001",
            expiry_date="2025-12-31",
            quantity=100,
            purchase_price=5.0,
            selling_price=8.0,
            barcode="PAR001234567"
        )
    
    @pytest.fixture
    def sample_medicines(self):
        """Create multiple sample medicines for testing"""
        from datetime import date, timedelta
        future_date1 = (date.today() + timedelta(days=365)).isoformat()
        future_date2 = (date.today() + timedelta(days=180)).isoformat()
        future_date3 = (date.today() + timedelta(days=90)).isoformat()
        
        return [
            Medicine(
                name="Paracetamol",
                category="Pain Relief",
                batch_no="PAR001",
                expiry_date=future_date1,
                quantity=100,
                purchase_price=5.0,
                selling_price=8.0,
                barcode="PAR001234567"
            ),
            Medicine(
                name="Amoxicillin",
                category="Antibiotic",
                batch_no="AMX001",
                expiry_date=future_date2,
                quantity=50,
                purchase_price=12.0,
                selling_price=18.0,
                barcode="AMX001234567"
            ),
            Medicine(
                name="Aspirin",
                category="Pain Relief",
                batch_no="ASP001",
                expiry_date=future_date3,
                quantity=5,  # Low stock
                purchase_price=3.0,
                selling_price=5.0,
                barcode="ASP001234567"
            )
        ]
    
    def test_save_medicine_success(self, repository, sample_medicine):
        """Test successful medicine save"""
        result = repository.save(sample_medicine)
        
        assert result is not None
        assert result.id is not None
        assert result.name == "Paracetamol"
        assert result.category == "Pain Relief"
        assert result.quantity == 100
    
    def test_save_medicine_with_duplicate_barcode(self, repository, sample_medicine):
        """Test saving medicine with duplicate barcode fails"""
        # Save first medicine
        result1 = repository.save(sample_medicine)
        assert result1 is not None
        
        # Try to save another medicine with same barcode
        duplicate_medicine = Medicine(
            name="Different Medicine",
            category="Different Category",
            batch_no="DIF001",
            expiry_date="2025-12-31",
            quantity=50,
            purchase_price=10.0,
            selling_price=15.0,
            barcode="PAR001234567"  # Same barcode
        )
        
        result2 = repository.save(duplicate_medicine)
        assert result2 is None
    
    def test_save_invalid_medicine(self, repository):
        """Test saving invalid medicine fails"""
        invalid_medicine = Medicine(
            name="",  # Invalid: empty name
            category="Pain Relief",
            batch_no="PAR001",
            expiry_date="2025-12-31",
            quantity=100,
            purchase_price=5.0,
            selling_price=8.0
        )
        
        result = repository.save(invalid_medicine)
        assert result is None
    
    def test_find_by_id_success(self, repository, sample_medicine):
        """Test finding medicine by ID"""
        # Save medicine first
        saved_medicine = repository.save(sample_medicine)
        assert saved_medicine is not None
        
        # Find by ID
        found_medicine = repository.find_by_id(saved_medicine.id)
        assert found_medicine is not None
        assert found_medicine.id == saved_medicine.id
        assert found_medicine.name == "Paracetamol"
    
    def test_find_by_id_not_found(self, repository):
        """Test finding non-existent medicine by ID"""
        result = repository.find_by_id(999)
        assert result is None
    
    def test_find_by_barcode_success(self, repository, sample_medicine):
        """Test finding medicine by barcode"""
        # Save medicine first
        saved_medicine = repository.save(sample_medicine)
        assert saved_medicine is not None
        
        # Find by barcode
        found_medicine = repository.find_by_barcode("PAR001234567")
        assert found_medicine is not None
        assert found_medicine.barcode == "PAR001234567"
        assert found_medicine.name == "Paracetamol"
    
    def test_find_by_barcode_not_found(self, repository):
        """Test finding non-existent medicine by barcode"""
        result = repository.find_by_barcode("NONEXISTENT")
        assert result is None
    
    def test_find_by_barcode_empty(self, repository):
        """Test finding medicine with empty barcode"""
        result = repository.find_by_barcode("")
        assert result is None
        
        result = repository.find_by_barcode(None)
        assert result is None
    
    def test_find_all(self, repository, sample_medicines):
        """Test finding all medicines"""
        # Save multiple medicines
        for medicine in sample_medicines:
            repository.save(medicine)
        
        # Find all
        all_medicines = repository.find_all()
        assert len(all_medicines) == 3
        
        # Check they are sorted by name
        names = [m.name for m in all_medicines]
        assert names == ["Amoxicillin", "Aspirin", "Paracetamol"]
    
    def test_search_by_name(self, repository, sample_medicines):
        """Test searching medicines by name"""
        # Save multiple medicines
        for medicine in sample_medicines:
            repository.save(medicine)
        
        # Search by partial name
        results = repository.search_by_name("Para")
        assert len(results) == 1
        assert results[0].name == "Paracetamol"
        
        # Search case insensitive
        results = repository.search_by_name("para")
        assert len(results) == 1
        assert results[0].name == "Paracetamol"
        
        # Search with no results
        results = repository.search_by_name("NonExistent")
        assert len(results) == 0
    
    def test_search_by_name_or_barcode(self, repository, sample_medicines):
        """Test searching medicines by name or barcode"""
        # Save multiple medicines
        for medicine in sample_medicines:
            repository.save(medicine)
        
        # Search by name
        results = repository.search("Paracetamol")
        assert len(results) == 1
        assert results[0].name == "Paracetamol"
        
        # Search by barcode
        results = repository.search("AMX001234567")
        assert len(results) == 1
        assert results[0].name == "Amoxicillin"
        
        # Search with partial match
        results = repository.search("001")
        assert len(results) == 3  # All have "001" in barcode
    
    def test_update_medicine_success(self, repository, sample_medicine):
        """Test successful medicine update"""
        # Save medicine first
        saved_medicine = repository.save(sample_medicine)
        assert saved_medicine is not None
        
        # Update medicine
        saved_medicine.name = "Updated Paracetamol"
        saved_medicine.quantity = 150
        saved_medicine.selling_price = 10.0
        
        result = repository.update(saved_medicine)
        assert result is True
        
        # Verify update
        updated_medicine = repository.find_by_id(saved_medicine.id)
        assert updated_medicine.name == "Updated Paracetamol"
        assert updated_medicine.quantity == 150
        assert updated_medicine.selling_price == 10.0
    
    def test_update_medicine_without_id(self, repository, sample_medicine):
        """Test updating medicine without ID fails"""
        sample_medicine.id = None
        result = repository.update(sample_medicine)
        assert result is False
    
    def test_update_nonexistent_medicine(self, repository, sample_medicine):
        """Test updating non-existent medicine"""
        sample_medicine.id = 999
        result = repository.update(sample_medicine)
        assert result is False
    
    def test_delete_medicine_success(self, repository, sample_medicine):
        """Test successful medicine deletion"""
        # Save medicine first
        saved_medicine = repository.save(sample_medicine)
        assert saved_medicine is not None
        
        # Delete medicine
        result = repository.delete(saved_medicine.id)
        assert result is True
        
        # Verify deletion
        deleted_medicine = repository.find_by_id(saved_medicine.id)
        assert deleted_medicine is None
    
    def test_delete_nonexistent_medicine(self, repository):
        """Test deleting non-existent medicine"""
        result = repository.delete(999)
        assert result is False
    
    def test_get_low_stock_medicines(self, repository, sample_medicines):
        """Test getting low stock medicines"""
        # Save multiple medicines
        for medicine in sample_medicines:
            repository.save(medicine)
        
        # Get low stock medicines (threshold = 10)
        low_stock = repository.get_low_stock_medicines(10)
        assert len(low_stock) == 1
        assert low_stock[0].name == "Aspirin"
        assert low_stock[0].quantity == 5
    
    def test_get_expired_medicines(self, repository):
        """Test getting expired medicines"""
        from datetime import date, timedelta
        
        # Create expired medicine - we need to bypass validation for testing
        # So we'll create a valid medicine first, then manually update the expiry date in DB
        expired_medicine = Medicine(
            name="Expired Medicine",
            category="Test",
            batch_no="EXP001",
            expiry_date=(date.today() + timedelta(days=30)).isoformat(),  # Valid for saving
            quantity=10,
            purchase_price=5.0,
            selling_price=8.0
        )

        # Create valid medicine
        valid_medicine = Medicine(
            name="Valid Medicine",
            category="Test",
            batch_no="VAL001",
            expiry_date=(date.today() + timedelta(days=365)).isoformat(),
            quantity=10,
            purchase_price=5.0,
            selling_price=8.0
        )

        # Save both medicines
        saved_expired = repository.save(expired_medicine)
        repository.save(valid_medicine)
        
        # Manually update the expired medicine's expiry date to past date
        repository.db_manager.execute_update(
            "UPDATE medicines SET expiry_date = ? WHERE id = ?",
            ("2020-01-01", saved_expired.id)
        )

        # Get expired medicines
        expired = repository.get_expired_medicines()
        assert len(expired) == 1
        assert expired[0].name == "Expired Medicine"
    
    def test_get_expiring_soon_medicines(self, repository):
        """Test getting medicines expiring soon"""
        # Create medicine expiring in 15 days
        expiring_date = (date.today() + timedelta(days=15)).isoformat()
        expiring_medicine = Medicine(
            name="Expiring Soon",
            category="Test",
            batch_no="EXP001",
            expiry_date=expiring_date,
            quantity=10,
            purchase_price=5.0,
            selling_price=8.0
        )
        
        # Create medicine expiring in 60 days
        future_date = (date.today() + timedelta(days=60)).isoformat()
        future_medicine = Medicine(
            name="Future Expiry",
            category="Test",
            batch_no="FUT001",
            expiry_date=future_date,
            quantity=10,
            purchase_price=5.0,
            selling_price=8.0
        )
        
        repository.save(expiring_medicine)
        repository.save(future_medicine)
        
        # Get medicines expiring in 30 days
        expiring_soon = repository.get_expiring_soon_medicines(30)
        assert len(expiring_soon) == 1
        assert expiring_soon[0].name == "Expiring Soon"
    
    def test_get_medicines_by_category(self, repository, sample_medicines):
        """Test getting medicines by category"""
        # Save multiple medicines
        for medicine in sample_medicines:
            repository.save(medicine)
        
        # Get medicines by category
        pain_relief = repository.get_medicines_by_category("Pain Relief")
        assert len(pain_relief) == 2
        names = [m.name for m in pain_relief]
        assert "Paracetamol" in names
        assert "Aspirin" in names
        
        antibiotics = repository.get_medicines_by_category("Antibiotic")
        assert len(antibiotics) == 1
        assert antibiotics[0].name == "Amoxicillin"
    
    def test_get_all_categories(self, repository, sample_medicines):
        """Test getting all unique categories"""
        # Save multiple medicines
        for medicine in sample_medicines:
            repository.save(medicine)
        
        categories = repository.get_all_categories()
        assert len(categories) == 2
        assert "Pain Relief" in categories
        assert "Antibiotic" in categories
    
    def test_update_stock_success(self, repository, sample_medicine):
        """Test successful stock update"""
        # Save medicine first
        saved_medicine = repository.save(sample_medicine)
        assert saved_medicine is not None
        assert saved_medicine.quantity == 100
        
        # Increase stock
        result = repository.update_stock(saved_medicine.id, 50)
        assert result is True
        
        # Verify stock update
        updated_medicine = repository.find_by_id(saved_medicine.id)
        assert updated_medicine.quantity == 150
        
        # Decrease stock
        result = repository.update_stock(saved_medicine.id, -30)
        assert result is True
        
        # Verify stock update
        updated_medicine = repository.find_by_id(saved_medicine.id)
        assert updated_medicine.quantity == 120
    
    def test_update_stock_negative_result(self, repository, sample_medicine):
        """Test stock update that would result in negative stock"""
        # Save medicine first
        saved_medicine = repository.save(sample_medicine)
        assert saved_medicine is not None
        assert saved_medicine.quantity == 100
        
        # Try to reduce stock below zero
        result = repository.update_stock(saved_medicine.id, -150)
        assert result is False
        
        # Verify stock unchanged
        unchanged_medicine = repository.find_by_id(saved_medicine.id)
        assert unchanged_medicine.quantity == 100
    
    def test_update_stock_nonexistent_medicine(self, repository):
        """Test updating stock for non-existent medicine"""
        result = repository.update_stock(999, 10)
        assert result is False
    
    def test_get_total_medicines_count(self, repository, sample_medicines):
        """Test getting total medicines count"""
        # Initially should be 0
        count = repository.get_total_medicines_count()
        assert count == 0
        
        # Save multiple medicines
        for medicine in sample_medicines:
            repository.save(medicine)
        
        # Should now be 3
        count = repository.get_total_medicines_count()
        assert count == 3
    
    def test_get_total_stock_value(self, repository, sample_medicines):
        """Test getting total stock value"""
        # Initially should be 0
        value = repository.get_total_stock_value()
        assert value == 0.0
        
        # Save multiple medicines
        for medicine in sample_medicines:
            repository.save(medicine)
        
        # Calculate expected value
        # Paracetamol: 100 * 8.0 = 800.0
        # Amoxicillin: 50 * 18.0 = 900.0
        # Aspirin: 5 * 5.0 = 25.0
        # Total: 1725.0
        expected_value = 800.0 + 900.0 + 25.0
        
        value = repository.get_total_stock_value()
        assert value == expected_value