#!/usr/bin/env python3
"""
Reset Database and Create Demo Data Script
Clears existing data and creates fresh demo data for Pakistani medical store
"""

import sys
import os
import random
from datetime import datetime, date, timedelta
from pathlib import Path

# Add the parent directory to the path so we can import the medical store modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from medical_store_app.config.database import DatabaseManager
from medical_store_app.repositories.medicine_repository import MedicineRepository
from medical_store_app.repositories.sales_repository import SalesRepository
from medical_store_app.repositories.settings_repository import SettingsRepository
from medical_store_app.repositories.user_repository import UserRepository
from medical_store_app.models.medicine import Medicine
from medical_store_app.models.sale import Sale, SaleItem


class DemoDataCreator:
    """Creates fresh demo data for the medical store application"""
    
    def __init__(self):
        """Initialize the demo data creator"""
        self.db_manager = DatabaseManager()
        self.db_manager.initialize()
        
        # Initialize repositories
        self.medicine_repo = MedicineRepository(self.db_manager)
        self.sales_repo = SalesRepository(self.db_manager)
        self.settings_repo = SettingsRepository(self.db_manager)
        self.user_repo = UserRepository(self.db_manager)
        
        print("Demo data creator initialized successfully")
    
    def clear_existing_data(self):
        """Clear existing medicines and sales data (keep users and settings)"""
        print("Clearing existing medicines and sales data...")
        
        try:
            # Clear sales first (due to foreign key constraints)
            with self.db_manager.get_cursor() as cursor:
                cursor.execute("DELETE FROM sales")
                print("Cleared existing sales data")
                
                # Clear medicines
                cursor.execute("DELETE FROM medicines")
                print("Cleared existing medicines data")
                
        except Exception as e:
            print(f"Error clearing data: {e}")
            raise
    
    def setup_pakistani_settings(self):
        """Set up Pakistani store settings"""
        print("Setting up Pakistani store settings...")
        
        # Store information
        store_settings = {
            'store_name': 'Shifa Medical Store',
            'store_address': 'Main Bazaar, Lahore, Punjab, Pakistan',
            'store_phone': '+92-42-1234567',
            'store_email': 'info@shifamedical.pk',
            'store_website': 'www.shifamedical.pk'
        }
        
        # Business settings
        business_settings = {
            'currency': 'PKR',
            'tax_rate': 17.0,  # GST rate in Pakistan
            'low_stock_threshold': 20,
            'enable_barcode_scanning': True,
            'auto_backup': True,
            'backup_frequency_days': 7
        }
        
        # Save store settings
        for key, value in store_settings.items():
            self.settings_repo.set(key, value, f'{key} setting')
        
        # Save business settings
        for key, value in business_settings.items():
            if isinstance(value, bool):
                self.settings_repo.set_bool(key, value, f'{key} setting')
            elif isinstance(value, (int, float)):
                self.settings_repo.set(key, str(value), f'{key} setting')
            else:
                self.settings_repo.set(key, value, f'{key} setting')
        
        print("Pakistani store settings configured successfully")
    
    def create_demo_medicines(self):
        """Create a comprehensive list of demo medicines"""
        print("Creating demo medicines...")
        
        # Comprehensive list of medicines with realistic Pakistani medical store data
        medicines_data = [
            # Pain Relief & Fever
            {"name": "Panadol 500mg", "category": "Pain Relief", "batch_no": "PAN2024001", "expiry_date": "2025-12-31", "quantity": 500, "purchase_price": 2.50, "selling_price": 3.00, "barcode": "PAD500001"},
            {"name": "Aspirin 75mg", "category": "Pain Relief", "batch_no": "ASP2024001", "expiry_date": "2025-11-30", "quantity": 300, "purchase_price": 1.80, "selling_price": 2.20, "barcode": "ASP075001"},
            {"name": "Brufen 400mg", "category": "Pain Relief", "batch_no": "BRU2024001", "expiry_date": "2025-10-15", "quantity": 250, "purchase_price": 4.50, "selling_price": 5.50, "barcode": "BRU400001"},
            {"name": "Disprin", "category": "Pain Relief", "batch_no": "DIS2024001", "expiry_date": "2025-09-30", "quantity": 400, "purchase_price": 3.20, "selling_price": 4.00, "barcode": "DIS001001"},
            {"name": "Ponstan 250mg", "category": "Pain Relief", "batch_no": "PON2024001", "expiry_date": "2025-08-20", "quantity": 180, "purchase_price": 6.80, "selling_price": 8.50, "barcode": "PON250001"},
            
            # Antibiotics
            {"name": "Augmentin 625mg", "category": "Antibiotics", "batch_no": "AUG2024001", "expiry_date": "2026-07-15", "quantity": 120, "purchase_price": 15.50, "selling_price": 19.00, "barcode": "AUG625001"},
            {"name": "Amoxil 250mg", "category": "Antibiotics", "batch_no": "AMX2024001", "expiry_date": "2026-06-30", "quantity": 200, "purchase_price": 8.20, "selling_price": 10.50, "barcode": "AMX250001"},
            {"name": "Zithromax 250mg", "category": "Antibiotics", "batch_no": "ZIT2024001", "expiry_date": "2026-05-25", "quantity": 80, "purchase_price": 25.00, "selling_price": 32.00, "barcode": "ZIT250001"},
            {"name": "Cephalexin 500mg", "category": "Antibiotics", "batch_no": "CEP2024001", "expiry_date": "2026-04-10", "quantity": 150, "purchase_price": 12.50, "selling_price": 16.00, "barcode": "CEP500001"},
            {"name": "Flagyl 400mg", "category": "Antibiotics", "batch_no": "FLA2024001", "expiry_date": "2026-03-20", "quantity": 100, "purchase_price": 7.80, "selling_price": 10.00, "barcode": "FLA400001"},
            
            # Cardiovascular
            {"name": "Concor 2.5mg", "category": "Cardiovascular", "batch_no": "CON2024001", "expiry_date": "2025-12-15", "quantity": 90, "purchase_price": 18.50, "selling_price": 23.00, "barcode": "CON025001"},
            {"name": "Norvasc 5mg", "category": "Cardiovascular", "batch_no": "NOR2024001", "expiry_date": "2025-11-10", "quantity": 110, "purchase_price": 22.00, "selling_price": 28.00, "barcode": "NOR005001"},
            {"name": "Lipitor 20mg", "category": "Cardiovascular", "batch_no": "LIP2024001", "expiry_date": "2025-10-05", "quantity": 75, "purchase_price": 35.00, "selling_price": 45.00, "barcode": "LIP020001"},
            {"name": "Cardace 2.5mg", "category": "Cardiovascular", "batch_no": "CAR2024001", "expiry_date": "2025-09-15", "quantity": 85, "purchase_price": 16.50, "selling_price": 21.00, "barcode": "CAR025001"},
            
            # Diabetes
            {"name": "Glucophage 500mg", "category": "Diabetes", "batch_no": "GLU2024001", "expiry_date": "2025-08-30", "quantity": 200, "purchase_price": 12.00, "selling_price": 15.50, "barcode": "GLU500001"},
            {"name": "Diamicron 80mg", "category": "Diabetes", "batch_no": "DIA2024001", "expiry_date": "2026-07-25", "quantity": 120, "purchase_price": 28.00, "selling_price": 36.00, "barcode": "DIA080001"},
            {"name": "Januvia 100mg", "category": "Diabetes", "batch_no": "JAN2024001", "expiry_date": "2026-06-20", "quantity": 60, "purchase_price": 85.00, "selling_price": 110.00, "barcode": "JAN100001"},
            
            # Respiratory
            {"name": "Ventolin Inhaler", "category": "Respiratory", "batch_no": "VEN2024001", "expiry_date": "2025-12-20", "quantity": 50, "purchase_price": 45.00, "selling_price": 58.00, "barcode": "VEN001001"},
            {"name": "Mucolite Syrup", "category": "Respiratory", "batch_no": "MUC2024001", "expiry_date": "2025-11-15", "quantity": 80, "purchase_price": 18.50, "selling_price": 24.00, "barcode": "MUC001001"},
            {"name": "Rynex Syrup", "category": "Respiratory", "batch_no": "RYN2024001", "expiry_date": "2025-10-10", "quantity": 70, "purchase_price": 22.00, "selling_price": 28.50, "barcode": "RYN001001"},
            
            # Gastrointestinal
            {"name": "Motilium 10mg", "category": "Gastrointestinal", "batch_no": "MOT2024001", "expiry_date": "2026-08-15", "quantity": 150, "purchase_price": 8.50, "selling_price": 11.00, "barcode": "MOT010001"},
            {"name": "Nexium 40mg", "category": "Gastrointestinal", "batch_no": "NEX2024001", "expiry_date": "2026-07-10", "quantity": 100, "purchase_price": 32.00, "selling_price": 42.00, "barcode": "NEX040001"},
            {"name": "Loperamide 2mg", "category": "Gastrointestinal", "batch_no": "LOP2024001", "expiry_date": "2026-06-05", "quantity": 200, "purchase_price": 4.50, "selling_price": 6.00, "barcode": "LOP002001"},
            
            # Vitamins & Supplements
            {"name": "Centrum Multivitamin", "category": "Vitamins", "batch_no": "CEN2024001", "expiry_date": "2025-12-25", "quantity": 80, "purchase_price": 35.00, "selling_price": 45.00, "barcode": "CEN001001"},
            {"name": "Calcium D3", "category": "Vitamins", "batch_no": "CAL2024001", "expiry_date": "2025-11-20", "quantity": 150, "purchase_price": 18.00, "selling_price": 23.50, "barcode": "CAL001001"},
            {"name": "Iron Tablets", "category": "Vitamins", "batch_no": "IRO2024001", "expiry_date": "2025-10-25", "quantity": 200, "purchase_price": 8.50, "selling_price": 11.50, "barcode": "IRO001001"},
            
            # Pediatrics
            {"name": "Calpol Syrup", "category": "Pediatrics", "batch_no": "CAL2024002", "expiry_date": "2025-10-15", "quantity": 100, "purchase_price": 16.00, "selling_price": 21.00, "barcode": "CAL002001"},
            {"name": "Gripe Water", "category": "Pediatrics", "batch_no": "GRI2024001", "expiry_date": "2025-09-10", "quantity": 80, "purchase_price": 12.50, "selling_price": 16.50, "barcode": "GRI001001"},
            {"name": "ORS Sachets", "category": "Pediatrics", "batch_no": "ORS2024001", "expiry_date": "2026-08-05", "quantity": 300, "purchase_price": 2.00, "selling_price": 3.00, "barcode": "ORS001001"},
            
            # First Aid
            {"name": "Bandages", "category": "First Aid", "batch_no": "BAN2024001", "expiry_date": "2026-12-31", "quantity": 200, "purchase_price": 5.00, "selling_price": 7.50, "barcode": "BAN001001"},
            {"name": "Antiseptic Solution", "category": "First Aid", "batch_no": "ANS2024001", "expiry_date": "2026-11-30", "quantity": 150, "purchase_price": 12.00, "selling_price": 16.00, "barcode": "ANS001001"},
        ]
        
        created_medicines = []
        for med_data in medicines_data:
            try:
                medicine = Medicine(**med_data)
                saved_medicine = self.medicine_repo.save(medicine)
                if saved_medicine:
                    created_medicines.append(saved_medicine)
                    print(f"✓ Created: {saved_medicine.name}")
                else:
                    print(f"✗ Failed: {med_data['name']}")
            except Exception as e:
                print(f"✗ Error creating {med_data['name']}: {e}")
        
        print(f"Successfully created {len(created_medicines)} medicines")
        return created_medicines
    
    def create_demo_sales(self, medicines, days_back=365):
        """Create demo sales data for the specified number of days"""
        print(f"Creating demo sales data for {days_back} days...")
        
        if not medicines:
            print("No medicines available for creating sales")
            return []
        
        created_sales = []
        start_date = date.today() - timedelta(days=days_back)
        
        # Create sales for each day with varying patterns
        for day_offset in range(0, days_back, 7):  # Create sales for every 7th day to speed up
            current_date = start_date + timedelta(days=day_offset)
            
            # Determine number of sales for this day
            num_sales = random.randint(3, 8)
            
            # Create sales for this day
            for sale_num in range(num_sales):
                try:
                    sale = self._create_single_sale(medicines, current_date)
                    if sale:
                        created_sales.append(sale)
                        if len(created_sales) % 10 == 0:
                            print(f"Created {len(created_sales)} sales...")
                except Exception as e:
                    print(f"Error creating sale for {current_date}: {e}")
        
        print(f"Successfully created {len(created_sales)} sales transactions")
        return created_sales
    
    def _create_single_sale(self, medicines, sale_date):
        """Create a single sale transaction"""
        # Select random medicines for this sale (1-3 items to keep it simple)
        num_items = random.randint(1, 3)
        selected_medicines = random.sample(medicines, min(num_items, len(medicines)))
        
        sale_items = []
        subtotal = 0.0
        
        for medicine in selected_medicines:
            # Random quantity (1-2 for most items)
            quantity = random.randint(1, 2)
            
            # Check if medicine has enough stock
            if medicine.quantity >= quantity:
                total_price = quantity * medicine.selling_price
                
                sale_item = SaleItem(
                    medicine_id=medicine.id,
                    name=medicine.name,
                    quantity=quantity,
                    unit_price=medicine.selling_price,
                    total_price=total_price,
                    batch_no=medicine.batch_no
                )
                sale_items.append(sale_item)
                subtotal += total_price
        
        if not sale_items:
            return None
        
        # Random discount (0-5% occasionally)
        discount = 0.0
        if random.random() < 0.1:  # 10% chance of discount
            discount = round(subtotal * random.uniform(0.02, 0.05), 2)
        
        # Tax rate (17% GST in Pakistan)
        tax_rate = 17.0 if random.random() < 0.8 else 0.0  # 80% chance of tax
        tax = round((subtotal - discount) * (tax_rate / 100), 2)
        
        total = round(subtotal - discount + tax, 2)
        
        # Random payment method
        payment_methods = ["cash", "card", "upi"]
        payment_weights = [0.8, 0.15, 0.05]  # Cash is most common
        payment_method = random.choices(payment_methods, weights=payment_weights)[0]
        
        # Random customer names (sometimes)
        customer_names = [
            None, None, None, None,  # Most sales without customer name
            "Ahmed Ali", "Fatima Khan", "Muhammad Hassan", "Ayesha Malik", 
            "Ali Raza", "Zainab Sheikh"
        ]
        customer_name = random.choice(customer_names)
        
        # Create sale
        sale = Sale(
            date=sale_date.isoformat(),
            items=sale_items,
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            total=total,
            payment_method=payment_method,
            cashier_id=1,  # Default admin user
            customer_name=customer_name
        )
        
        # Save sale
        saved_sale = self.sales_repo.save(sale)
        return saved_sale
    
    def create_all_demo_data(self):
        """Create all demo data"""
        print("Starting fresh demo data creation...")
        print("=" * 60)
        
        # Clear existing data first
        self.clear_existing_data()
        
        # Set up Pakistani settings
        self.setup_pakistani_settings()
        
        # Create medicines
        medicines = self.create_demo_medicines()
        
        # Create sales data for the past year (reduced frequency for speed)
        if medicines:
            sales = self.create_demo_sales(medicines, days_back=365)
        
        print("=" * 60)
        print("✅ Demo data creation completed successfully!")
        print(f"📦 Created {len(medicines)} medicines")
        print(f"💰 Created {len(sales) if 'sales' in locals() else 0} sales transactions")
        print("🇵🇰 Store configured for Pakistani Rupees (PKR)")
        print("📊 Tax rate set to 17% (GST)")
        print("🏪 Store name: Shifa Medical Store")
        print("\n🚀 You can now run the application to see the demo data!")


def main():
    """Main function to create demo data"""
    try:
        print("🔄 Initializing demo data creator...")
        creator = DemoDataCreator()
        creator.create_all_demo_data()
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Demo data creation cancelled by user")
        return 1
        
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())