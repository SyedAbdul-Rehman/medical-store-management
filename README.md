# Medical Store Management System

A comprehensive desktop application for managing medical store operations, built with Python and PySide6.

## 🚀 Features

### ✅ Completed Features
- **Modern UI Framework**: Professional desktop interface with PySide6
- **Responsive Layout**: Main window with header, collapsible sidebar, and content areas
- **Navigation System**: Smooth sidebar navigation with icons and animations
- **Medicine Management UI**: Complete inventory management with Add/Edit/Delete operations
- **Enhanced Inventory Features**: Low-stock alerts, expiry monitoring, advanced filtering
- **Billing System UI**: Complete sales interface with product search, cart, and checkout
- **Transaction Processing**: Payment handling, receipt generation, inventory updates
- **User Authentication System**: Login/logout, role-based access control, user management
- **Dashboard & Overview**: Key metrics cards, sales charts, quick action buttons
- **Reports & Analytics**: Sales reports, data visualization, export functionality (CSV/Excel/PDF)
- **Reusable Components**: Validated form components, styled buttons, tables, and dialogs
- **Database Integration**: SQLite database with proper schema and migrations
- **Settings Management**: Configurable application settings
- **Backup & Restore System**: Comprehensive version control and recovery utilities
- **Comprehensive Testing**: Full test coverage for all components

### 🔄 In Development
- Settings management interface
- Advanced features and optimizations
- Performance enhancements
- Deployment preparation

## 🛠️ Technology Stack

- **Frontend**: PySide6 (Qt for Python)
- **Backend**: Python 3.13+
- **Database**: SQLite
- **Testing**: pytest
- **Architecture**: MVC pattern with repository pattern

## 📋 Requirements

- Python 3.13 or higher
- PySide6
- SQLite (included with Python)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SyedAbdul-Rehman/medical-store-management.git
   cd medical-store-management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python medical_store_app/main.py
   ```

## 🧪 Testing

Run the test suite to ensure everything is working correctly:

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_main_window.py -v

# Run with coverage
python -m pytest --cov=medical_store_app
```

## 📁 Project Structure

```
medical_store_app/
├── config/                 # Configuration management
│   ├── database.py        # Database connection and setup
│   └── settings.py        # Application settings
├── models/                # Data models
│   ├── base.py           # Base model class
│   ├── medicine.py       # Medicine model
│   ├── sale.py           # Sales model
│   └── user.py           # User model
├── repositories/          # Data access layer
│   ├── medicine_repository.py
│   ├── sales_repository.py
│   ├── settings_repository.py
│   └── user_repository.py
├── managers/              # Business logic layer
│   ├── auth_manager.py
│   ├── medicine_manager.py
│   └── sales_manager.py
├── ui/                    # User interface
│   ├── components/        # Reusable UI components
│   │   ├── base_components.py
│   │   └── sidebar.py
│   ├── dialogs/          # Dialog windows
│   │   └── base_dialog.py
│   └── main_window.py    # Main application window
├── utils/                 # Utility functions
├── data/                  # Database files
├── logs/                  # Application logs
└── main.py               # Application entry point

tests/                     # Test files
├── test_main_window.py
├── test_sidebar.py
├── test_base_components.py
├── test_base_dialog.py
└── ...

.kiro/specs/              # Development specifications
├── requirements.md
├── design.md
└── tasks.md
```

## 🎨 UI Components

### Main Window
- **Header**: Application title, user info, and controls
- **Sidebar**: Collapsible navigation menu with smooth animations
- **Content Area**: Dynamic content based on selected navigation item

### Medicine Management
- **Medicine Table**: Sortable, filterable table with search functionality
- **Add/Edit Forms**: Validated forms with error handling
- **Alert System**: Low-stock and expiry date monitoring
- **Advanced Filtering**: Category-based and multi-criteria search

### Billing System
- **Product Search**: Name and barcode lookup with stock information
- **Shopping Cart**: Item management with quantity and price calculations
- **Checkout**: Payment processing with multiple payment methods
- **Receipt Generation**: Professional receipts with transaction details

### User Authentication
- **Login Dialog**: Secure authentication with username/password
- **Role-Based Access**: Admin and cashier role restrictions
- **User Management**: Add/edit users, role assignment, password management
- **Session Management**: Secure login/logout functionality

### Dashboard & Reports
- **Dashboard Cards**: Key metrics (Total Sales, Medicines, Low Stock, Expired)
- **Sales Charts**: Visual data representation with trend analysis
- **Quick Actions**: Direct navigation to frequently used features
- **Reports Generation**: Sales reports with date range filtering
- **Export Options**: CSV, Excel, and PDF export capabilities

### Reusable Components
- **ValidatedLineEdit**: Text input with built-in validation
- **ValidatedComboBox**: Dropdown with validation
- **ValidatedSpinBox**: Number input with validation
- **StyledButton**: Consistent button styling (primary, secondary, danger, outline)
- **StyledTable**: Professional data tables
- **FormContainer**: Organized form layouts with validation

### Dialog System
- **BaseDialog**: Consistent dialog foundation
- **FormDialog**: Form-based dialogs with validation
- **ConfirmationDialog**: User confirmation prompts
- **MessageDialog**: Info, warning, error, and success messages
- **ProgressDialog**: Long-running operation feedback

## 🗄️ Database Schema

The application uses SQLite with the following main tables:
- **users**: User authentication and roles
- **medicines**: Medicine inventory and details
- **sales**: Transaction records
- **sale_items**: Individual sale line items
- **settings**: Application configuration

## 🔧 Configuration

Application settings are managed through:
- **Database**: `medical_store_app/data/medical_store.db`
- **Logs**: `medical_store_app/logs/medical_store.log`
- **Settings**: Stored in database settings table

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Use type hints where appropriate
- Maintain the MVC architecture pattern

## 🐛 Known Issues

- High DPI scaling warnings on some systems (cosmetic only)
- Animation performance may vary on older hardware

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Syed Abdul Rehman**
- GitHub: [@SyedAbdul-Rehman](https://github.com/SyedAbdul-Rehman)

## 🙏 Acknowledgments

- PySide6 team for the excellent Qt Python bindings
- SQLite team for the reliable database engine
- pytest team for the testing framework

---

## 📊 Development Status

### Phase 1: Foundation ✅ Complete
- [x] Project setup and core architecture
- [x] Database schema and business logic
- [x] Main application window and navigation

### Phase 2: Medicine Management ✅ Complete
- [x] Medicine CRUD operations (UI + Backend)
- [x] Inventory alerts and monitoring
- [x] Advanced search and filtering

### Phase 3: Billing System ✅ Complete
- [x] Product search and selection
- [x] Shopping cart with calculations
- [x] Transaction processing and receipts
- [x] Inventory updates after sales

### Phase 4: User Authentication ✅ Complete
- [x] Login dialog and authentication flow
- [x] Role-based access control throughout UI
- [x] User management interface for admins
- [x] Admin/cashier access restrictions

### Phase 5: Dashboard & Reports ✅ Complete
- [x] Dashboard with key metrics cards
- [x] Sales charts and data visualization
- [x] Quick action buttons and navigation
- [x] Sales reports with date range filtering
- [x] Export functionality (CSV, Excel, PDF)

### Phase 6: Next Development 🔄
- [ ] Settings management interface
- [ ] Advanced features and optimizations
- [ ] Performance enhancements
- [ ] Deployment preparation

### Future Enhancements 🚀
- [ ] Multi-language support
- [ ] Advanced reporting and analytics
- [ ] Backup and restore functionality
- [ ] Network/multi-user support
- [ ] Barcode scanning integration
- [ ] Print receipt customization

---

**Status**: Active Development | **Version**: 1.0.0-rc2 | **Last Updated**: January 2025

### 🎉 Major Milestones Achieved
- ✅ **Complete Medicine Management System** - Full inventory control
- ✅ **Complete Billing System** - End-to-end sales processing
- ✅ **User Authentication System** - Secure login and role-based access
- ✅ **Dashboard & Reports System** - Analytics and data visualization
- ✅ **Professional UI Framework** - Modern, responsive interface
- ✅ **Comprehensive Testing** - High-quality, reliable codebase