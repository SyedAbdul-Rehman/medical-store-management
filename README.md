# 🏥 Medical Store Management System

A comprehensive medical store management application built with Python and PySide6, designed specifically for Pakistani medical stores with PKR currency support.

## ✨ Features

### 🏪 Store Management
- **Multi-currency Support**: Pakistani Rupee (PKR), USD, EUR, GBP, INR, and more
- **Store Configuration**: Complete store details, contact information, and branding
- **Tax Management**: Configurable tax rates (17% GST for Pakistan by default)
- **User Management**: Admin and cashier roles with different access levels

### 💊 Medicine Management
- **Comprehensive Inventory**: Track medicines with batch numbers, expiry dates, and stock levels
- **Category Management**: Organize medicines by categories (Pain Relief, Antibiotics, etc.)
- **Stock Alerts**: Configurable low stock and expiry date warnings
- **Barcode Support**: Barcode scanning and generation for medicines
- **Batch Tracking**: Track medicine batches for safety and compliance

### 💰 Billing & Sales
- **Point of Sale**: Intuitive billing interface with product search
- **Receipt Generation**: Professional receipts with store branding
- **Payment Methods**: Cash, Card, UPI, Cheque, and Bank Transfer support
- **Tax Calculations**: Automatic tax calculation with configurable rates
- **Discount Management**: Apply discounts to individual sales
- **Customer Management**: Optional customer information tracking

### 📊 Reports & Analytics
- **Sales Reports**: Daily, weekly, monthly, and custom date range reports
- **Inventory Reports**: Stock levels, low stock alerts, and expiry tracking
- **Financial Analytics**: Revenue tracking, profit analysis, and tax summaries
- **Top Selling Items**: Identify best-performing medicines
- **Interactive Charts**: Visual representation of sales and inventory data

### 🔧 System Features
- **Database Management**: SQLite database with automatic backups
- **Settings Management**: Comprehensive configuration system
- **Multi-language Ready**: Prepared for Urdu/English localization
- **Print Support**: Receipt and report printing capabilities
- **Data Export**: Export reports to various formats

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/medical-store-management.git
   cd medical-store-management
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create demo data (optional)**
   ```bash
   python scripts/reset_and_create_demo_data.py
   ```

5. **Run the application**
   ```bash
   python -m medical_store_app.main
   ```

### Default Login Credentials
- **Admin**: Username: `admin`, Password: `admin123`
- **Cashier**: Username: `cashier`, Password: `cashier123`

## 🏗️ Project Structure

```
medical-store-management/
├── medical_store_app/           # Main application package
│   ├── config/                  # Configuration and database setup
│   ├── models/                  # Data models (Medicine, Sale, User, etc.)
│   ├── repositories/            # Data access layer
│   ├── managers/                # Business logic layer
│   ├── ui/                      # User interface components
│   │   ├── components/          # Reusable UI components
│   │   └── dialogs/             # Dialog windows
│   └── utils/                   # Utility functions
├── scripts/                     # Utility scripts
├── tests/                       # Test files
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🇵🇰 Pakistani Store Configuration

The application comes pre-configured for Pakistani medical stores:

- **Currency**: Pakistani Rupee (₨)
- **Tax Rate**: 17% (GST)
- **Store Name**: Shifa Medical Store
- **Location**: Lahore, Punjab, Pakistan
- **Medicine Categories**: Common Pakistani pharmacy categories
- **Sample Data**: 31+ medicines commonly found in Pakistani stores

## 🛠️ Development

### Setting up Development Environment

1. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run tests**
   ```bash
   python -m pytest tests/ -v
   ```

3. **Code formatting**
   ```bash
   black medical_store_app/
   ```

### Database Schema

The application uses SQLite with the following main tables:
- `medicines` - Medicine inventory
- `sales` - Sales transactions
- `users` - User accounts
- `settings` - Application configuration

## 📱 Screenshots

### Dashboard
- Real-time sales overview
- Inventory summary
- Quick action buttons
- Sales charts and analytics

### Medicine Management
- Add/edit/delete medicines
- Stock level monitoring
- Expiry date tracking
- Category-based filtering

### Billing System
- Product search and selection
- Shopping cart management
- Tax and discount calculations
- Receipt generation

### Reports
- Sales analytics
- Inventory reports
- Financial summaries
- Export capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/medical-store-management/issues) page
2. Create a new issue with detailed information
3. Include screenshots and error messages if applicable

## 🙏 Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython/) for the GUI framework
- Uses [SQLite](https://www.sqlite.org/) for data storage
- Inspired by real-world medical store requirements in Pakistan

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Added PKR currency support and Pakistani localization
- **v1.2.0** - Enhanced reporting and analytics features

---

**Made with ❤️ for Pakistani medical stores**