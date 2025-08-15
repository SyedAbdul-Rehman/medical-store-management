"""
Demo Data Script for Medical Store Management Application
Adds sample medicines, users, and sales data for testing and demonstration
"""

import sys
import os
from datetime import date, timedelta
import random

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from medical_store_app.config.database import DatabaseManager
from medical_store_app.repositories.medicine_repository import MedicineRepository
from medical_store_app.repositories.user_repository import UserRepository
from medical_store_app.repositories.sales_repository import SalesRepository
from medical_store_app.models.medicine import Medicine
from medical_store_app.models.user import User
from medical_store_app.models.sale import Sale, SaleItem


def create_demo_medicines():
    """Create demo medicine data"""
    demo_medicines = [
        # Pain Relief
        {
            'name': 'Paracetamol 500mg',
            'category': 'Pain Relief',
            'batch_no': 'PR001',
            'expiry_date': (date.today() + timedelta(days=365)).isoformat(),
            'quantity': 150,
            'purchase_price': 2.50,
            'selling_price': 5.00,
            'barcode': '1234567890001'
        },
        {
            'name': 'Ibuprofen 400mg',
            'category': 'Pain Relief',
            'batch_no': 'PR002',
            'expiry_date': (date.today() + timedelta(days=300)).isoformat(),
            'quantity': 80,
            'purchase_price': 3.00,
            'selling_price': 6.50,
            'barcode': '1234567890002'
        },
        {
            'name': 'Aspirin 325mg',
            'category': 'Pain Relief',
            'batch_no': 'PR003',
            'expiry_date': (date.today() + timedelta(days=200)).isoformat(),
            'quantity': 120,
            'purchase_price': 1.80,
            'selling_price': 4.00,
            'barcode': '1234567890003'
        },
        
        # Antibiotics
        {
            'name': 'Amoxicillin 500mg',
            'category': 'Antibiotics',
            'batch_no': 'AB001',
            'expiry_date': (date.today() + timedelta(days=180)).isoformat(),
            'quantity': 60,
            'purchase_price': 8.00,
            'selling_price': 15.00,
            'barcode': '1234567890004'
        },
        {
            'name': 'Azithromycin 250mg',
            'category': 'Antibiotics',
            'batch_no': 'AB002',
            'expiry_date': (date.today() + timedelta(days=240)).isoformat(),
            'quantity': 45,
            'purchase_price': 12.00,
            'selling_price': 22.00,
            'barcode': '1234567890005'
        },
        {
            'name': 'Ciprofloxacin 500mg',
            'category': 'Antibiotics',
            'batch_no': 'AB003',
            'expiry_date': (date.today() + timedelta(days=150)).isoformat(),
            'quantity': 35,
            'purchase_price': 10.50,
            'selling_price': 18.00,
            'barcode': '1234567890006'
        },
        
        # Vitamins & Supplements
        {
            'name': 'Vitamin C 1000mg',
            'category': 'Vitamins',
            'batch_no': 'VT001',
            'expiry_date': (date.today() + timedelta(days=450)).isoformat(),
            'quantity': 200,
            'purchase_price': 5.00,
            'selling_price': 10.00,
            'barcode': '1234567890007'
        },
        {
            'name': 'Vitamin D3 2000IU',
            'category': 'Vitamins',
            'batch_no': 'VT002',
            'expiry_date': (date.today() + timedelta(days=400)).isoformat(),
            'quantity': 180,
            'purchase_price': 6.50,
            'selling_price': 12.50,
            'barcode': '1234567890008'
        },
        {
            'name': 'Multivitamin Complex',
            'category': 'Vitamins',
            'batch_no': 'VT003',
            'expiry_date': (date.today() + timedelta(days=350)).isoformat(),
            'quantity': 90,
            'purchase_price': 8.00,
            'selling_price': 16.00,
            'barcode': '1234567890009'
        },
        
        # Cold & Flu
        {
            'name': 'Cough Syrup 100ml',
            'category': 'Cold & Flu',
            'batch_no': 'CF001',
            'expiry_date': (date.today() + timedelta(days=120)).isoformat(),
            'quantity': 75,
            'purchase_price': 4.50,
            'selling_price': 9.00,
            'barcode': '1234567890010'
        },
        {
            'name': 'Throat Lozenges',
            'category': 'Cold & Flu',
            'batch_no': 'CF002',
            'expiry_date': (date.today() + timedelta(days=180)).isoformat(),
            'quantity': 150,
            'purchase_price': 2.00,
            'selling_price': 4.50,
            'barcode': '1234567890011'
        },
        {
            'name': 'Nasal Decongestant',
            'category': 'Cold & Flu',
            'batch_no': 'CF003',
            'expiry_date': (date.today() + timedelta(days=90)).isoformat(),
            'quantity': 40,
            'purchase_price': 6.00,
            'selling_price': 11.50,
            'barcode': '1234567890012'
        },
        
        # Digestive Health
        {
            'name': 'Antacid Tablets',
            'category': 'Digestive Health',
            'batch_no': 'DH001',
            'expiry_date': (date.today() + timedelta(days=300)).isoformat(),
            'quantity': 100,
            'purchase_price': 3.50,
            'selling_price': 7.00,
            'barcode': '1234567890013'
        },
        {
            'name': 'Probiotics Capsules',
            'category': 'Digestive Health',
            'batch_no': 'DH002',
            'expiry_date': (date.today() + timedelta(days=250)).isoformat(),
            'quantity': 65,
            'purchase_price': 15.00,
            'selling_price': 28.00,
            'barcode': '1234567890014'
        },
        
        # First Aid
        {
            'name': 'Antiseptic Solution 100ml',
            'category': 'First Aid',
            'batch_no': 'FA001',
            'expiry_date': (date.today() + timedelta(days=500)).isoformat(),
            'quantity': 85,
            'purchase_price': 3.00,
            'selling_price': 6.50,
            'barcode': '1234567890015'
        },
        {
            'name': 'Adhesive Bandages Pack',
            'category': 'First Aid',
            'batch_no': 'FA002',
            'expiry_date': (date.today() + timedelta(days=600)).isoformat(),
            'quantity': 120,
            'purchase_price': 2.50,
            'selling_price': 5.50,
            'barcode': '1234567890016'
        },
        {
            'name': 'Hydrogen Peroxide 3%',
            'category': 'First Aid',
            'batch_no': 'FA003',
            'expiry_date': (date.today() + timedelta(days=400)).isoformat(),
            'quantity': 50,
            'purchase_price': 2.00,
            'selling_price': 4.50,
            'barcode': '1234567890017'
        },
        
        # Low Stock Items (for testing alerts)
        {
            'name': 'Emergency Inhaler',
            'category': 'Respiratory',
            'batch_no': 'RS001',
            'expiry_date': (date.today() + timedelta(days=90)).isoformat(),
            'quantity': 5,  # Low stock
            'purchase_price': 25.00,
            'selling_price': 45.00,
            'barcode': '1234567890018'
        },
        {
            'name': 'Insulin Pen',
            'category': 'Diabetes',
            'batch_no': 'DB001',
            'expiry_date': (date.today() + timedelta(days=60)).isoformat(),
            'quantity': 3,  # Low stock
            'purchase_price': 35.00,
            'selling_price': 65.00,
            'barcode': '1234567890019'
        },
        
        # Near-expiry Items (for testing alerts)
        {
            'name': 'Near-Expiry Cough Drops',
            'category': 'Cold & Flu',
            'batch_no': 'NE001',
            'expiry_date': (date.today() + timedelta(days=15)).isoformat(),  # Expires soon
            'quantity': 25,
            'purchase_price': 1.50,
            'selling_price': 3.50,
            'barcode': '1234567890020'
        },
        {
            'name': 'Near-Expiry Pain Relief Gel',
            'category': 'Pain Relief',
            'batch_no': 'NE002',
            'expiry_date': (date.today() + timedelta(days=10)).isoformat(),  # Expires soon
            'quantity': 15,
            'purchase_price': 4.00,
            'selling_price': 8.50,
            'barcode': '1234567890021'
        }
    ]
    
    return demo_medicines


def create_demo_users():
    """Create demo user data"""
    demo_users = [
        {
            'username': 'admin',
            'password': 'admin123',  # Will be hashed
            'full_name': 'System Administrator',
            'role': 'admin',
            'email': 'admin@medstore.com',
            'phone': '+1-555-0001'
        },
        {
            'username': 'cashier1',
            'password': 'cashier123',  # Will be hashed
            'full_name': 'John Smith',
            'role': 'cashier',
            'email': 'john.smith@medstore.com',
            'phone': '+1-555-0002'
        },
        {
            'username': 'cashier2',
            'password': 'cashier123',  # Will be hashed
            'full_name': 'Sarah Johnson',
            'role': 'cashier',
            'email': 'sarah.johnson@medstore.com',
            'phone': '+1-555-0003'
        }
    ]
    
    return demo_users


def create_demo_sales(medicine_repo):
    """Create demo sales data for the last 7 days"""
    demo_sales = []
    
    # Get some medicines for sales
    medicines = medicine_repo.find_all()
    if not medicines:
        print("No medicines found. Please add medicines first.")
        return demo_sales
    
    # Create sales for the last 7 days
    for days_ago in range(7):
        sale_date = (date.today() - timedelta(days=days_ago)).isoformat()
        
        # Create 1-3 sales per day
        num_sales = random.randint(1, 3)
        
        for sale_num in range(num_sales):
            # Select random medicines for this sale
            num_items = random.randint(1, 4)
            selected_medicines = random.sample(medicines, min(num_items, len(medicines)))
            
            sale_items = []
            subtotal = 0.0
            
            for medicine in selected_medicines:
                if medicine.quantity > 0:  # Only sell if in stock
                    quantity = random.randint(1, min(3, medicine.quantity))
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
            
            if sale_items:  # Only create sale if we have items
                # Random discount (0-10%)
                discount = round(subtotal * random.uniform(0, 0.1), 2)
                
                # Tax (8%)
                tax = round((subtotal - discount) * 0.08, 2)
                
                # Total
                total = round(subtotal - discount + tax, 2)
                
                # Random payment method
                payment_methods = ['cash', 'card', 'upi']
                payment_method = random.choice(payment_methods)
                
                # No cashier ID for now (users might not be created)
                cashier_id = None
                
                sale = Sale(
                    date=sale_date,
                    items=sale_items,
                    subtotal=subtotal,
                    discount=discount,
                    tax=tax,
                    total=total,
                    payment_method=payment_method,
                    cashier_id=cashier_id,
                    customer_name=f"Customer {random.randint(1000, 9999)}"
                )
                
                demo_sales.append(sale)
    
    return demo_sales


def main():
    """Main function to add demo data"""
    print("Adding demo data to Medical Store Management System...")
    
    try:
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize()
        
        # Initialize repositories
        medicine_repo = MedicineRepository(db_manager)
        user_repo = UserRepository(db_manager)
        sales_repo = SalesRepository(db_manager)
        
        # Check if data already exists
        existing_medicines = medicine_repo.find_all()
        existing_users = user_repo.find_all()
        
        if existing_medicines or existing_users:
            response = input("Demo data may already exist. Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Demo data addition cancelled.")
                return
        
        # Add demo users
        print("\nAdding demo users...")
        demo_users = create_demo_users()
        users_added = 0
        
        for user_data in demo_users:
            try:
                # Check if user already exists
                existing_user = user_repo.find_by_username(user_data['username'])
                if existing_user:
                    print(f"  User '{user_data['username']}' already exists, skipping...")
                    continue
                
                user = User(
                    username=user_data['username'],
                    full_name=user_data['full_name'],
                    role=user_data['role'],
                    email=user_data['email'],
                    phone=user_data['phone']
                )
                
                # Set password (will be hashed automatically)
                user.set_password(user_data['password'])
                
                saved_user = user_repo.save(user)
                if saved_user:
                    print(f"  ✓ Added user: {user_data['username']} ({user_data['role']})")
                    users_added += 1
                else:
                    print(f"  ✗ Failed to add user: {user_data['username']}")
                    
            except Exception as e:
                print(f"  ✗ Error adding user {user_data['username']}: {str(e)}")
        
        print(f"Added {users_added} users.")
        
        # Add demo medicines
        print("\nAdding demo medicines...")
        demo_medicines = create_demo_medicines()
        medicines_added = 0
        
        for medicine_data in demo_medicines:
            try:
                # Check if medicine already exists by barcode
                if medicine_data.get('barcode'):
                    existing_medicine = medicine_repo.find_by_barcode(medicine_data['barcode'])
                    if existing_medicine:
                        print(f"  Medicine with barcode '{medicine_data['barcode']}' already exists, skipping...")
                        continue
                
                medicine = Medicine(
                    name=medicine_data['name'],
                    category=medicine_data['category'],
                    batch_no=medicine_data['batch_no'],
                    expiry_date=medicine_data['expiry_date'],
                    quantity=medicine_data['quantity'],
                    purchase_price=medicine_data['purchase_price'],
                    selling_price=medicine_data['selling_price'],
                    barcode=medicine_data.get('barcode')
                )
                
                saved_medicine = medicine_repo.save(medicine)
                if saved_medicine:
                    status = ""
                    if medicine_data['quantity'] <= 10:
                        status += " [LOW STOCK]"
                    if date.fromisoformat(medicine_data['expiry_date']) < date.today():
                        status += " [EXPIRED]"
                    
                    print(f"  ✓ Added: {medicine_data['name']} (Qty: {medicine_data['quantity']}){status}")
                    medicines_added += 1
                else:
                    print(f"  ✗ Failed to add medicine: {medicine_data['name']}")
                    
            except Exception as e:
                print(f"  ✗ Error adding medicine {medicine_data['name']}: {str(e)}")
        
        print(f"Added {medicines_added} medicines.")
        
        # Add demo sales
        print("\nAdding demo sales data...")
        demo_sales = create_demo_sales(medicine_repo)
        sales_added = 0
        
        for sale in demo_sales:
            try:
                saved_sale = sales_repo.save(sale)
                if saved_sale:
                    # Update medicine stock
                    sales_repo.update_medicine_stock_after_sale(saved_sale)
                    sales_added += 1
                    print(f"  ✓ Added sale: {sale.date} - ${sale.total:.2f} ({len(sale.items)} items)")
                else:
                    print(f"  ✗ Failed to add sale for {sale.date}")
                    
            except Exception as e:
                print(f"  ✗ Error adding sale for {sale.date}: {str(e)}")
        
        print(f"Added {sales_added} sales transactions.")
        
        # Summary
        print(f"\n{'='*50}")
        print("DEMO DATA SUMMARY")
        print(f"{'='*50}")
        print(f"Users added: {users_added}")
        print(f"Medicines added: {medicines_added}")
        print(f"Sales transactions added: {sales_added}")
        print(f"\nDemo data has been successfully added!")
        print(f"\nLogin credentials:")
        print(f"  Admin: username='admin', password='admin123'")
        print(f"  Cashier: username='cashier1', password='cashier123'")
        print(f"  Cashier: username='cashier2', password='cashier123'")
        
        # Show some statistics
        total_medicines = len(medicine_repo.find_all())
        low_stock_medicines = len(medicine_repo.get_low_stock_medicines(10))
        expired_medicines = len(medicine_repo.get_expired_medicines())
        
        print(f"\nInventory Status:")
        print(f"  Total medicines: {total_medicines}")
        print(f"  Low stock items: {low_stock_medicines}")
        print(f"  Expired items: {expired_medicines}")
        
    except Exception as e:
        print(f"Error adding demo data: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()