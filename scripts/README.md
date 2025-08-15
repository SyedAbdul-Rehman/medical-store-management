# Demo Data Scripts

This directory contains scripts for adding demo data to the Medical Store Management System.

## add_demo_data.py

Adds comprehensive demo data including:

### Users
- **admin** (Administrator)
  - Username: `admin`
  - Password: `admin123`
  - Full access to all features

- **cashier1** (Cashier)
  - Username: `cashier1` 
  - Password: `cashier123`
  - Access to billing and inventory viewing

- **cashier2** (Cashier)
  - Username: `cashier2`
  - Password: `cashier123`
  - Access to billing and inventory viewing

### Medicines (22 items)
- **Pain Relief**: Paracetamol, Ibuprofen, Aspirin
- **Antibiotics**: Amoxicillin, Azithromycin, Ciprofloxacin
- **Vitamins**: Vitamin C, Vitamin D3, Multivitamin Complex
- **Cold & Flu**: Cough Syrup, Throat Lozenges, Nasal Decongestant
- **Digestive Health**: Antacid Tablets, Probiotics Capsules
- **First Aid**: Antiseptic Solution, Adhesive Bandages, Hydrogen Peroxide
- **Low Stock Items**: Emergency Inhaler (5 units), Insulin Pen (3 units)
- **Near-Expiry Items**: Items expiring within 15 days

### Sales Data
- 7 days of historical sales data
- Multiple transactions per day
- Various payment methods (cash, card, UPI)
- Realistic sales patterns

## Usage

```bash
# Run from the project root directory
python scripts/add_demo_data.py
```

The script will:
1. Check if demo data already exists
2. Add users with hashed passwords
3. Add medicines with various categories and stock levels
4. Generate realistic sales transactions
5. Update medicine stock levels based on sales
6. Display a summary of added data

## Features Demonstrated

- **Dashboard Metrics**: Total sales, medicine count, low stock alerts
- **Sales Chart**: 7-day sales trend visualization  
- **Quick Actions**: Alert buttons for low stock and near-expiry items
- **User Authentication**: Login with different user roles
- **Inventory Management**: Various stock levels and categories
- **Sales Processing**: Historical transaction data

## Notes

- The script is safe to run multiple times (checks for existing data)
- Expired medicines are not added (validation prevents this)
- Sales transactions automatically update medicine stock levels
- All passwords are properly hashed for security
- Foreign key constraints are properly handled