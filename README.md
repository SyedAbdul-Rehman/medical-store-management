# 🏥 Medical Store Management System

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![Framework](https://img.shields.io/badge/Framework-PySide6-orange.svg)
![Database](https://img.shields.io/badge/Database-SQLite-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A comprehensive, open-source medical store management application built with Python and PySide6. This application is designed to streamline the daily operations of a medical store, from inventory management to billing and reporting.

## ✨ Features

### 🏪 Store Management
- **Multi-currency Support**: Easily configurable for different currencies.
- **Store Configuration**: Manage store details, contact information, and branding.
- **Tax Management**: Set and manage tax rates.
- **User Management**: Admin and cashier roles with role-based access control.

### 💊 Medicine Management
- **Comprehensive Inventory**: Track medicines with batch numbers, expiry dates, and stock levels.
- **Category Management**: Organize medicines into custom categories.
- **Stock Alerts**: Receive notifications for low stock and expiring medicines.
- **Barcode Support**: Use a barcode scanner for quick billing and inventory checks.

### 💰 Billing & Sales
- **Point of Sale (POS)**: An intuitive interface for quick billing.
- **Receipt Generation**: Print or save professional receipts.
- **Multiple Payment Methods**: Supports cash, card, and other payment options.
- **Discount Management**: Apply discounts to sales.

### 📊 Reports & Analytics
- **Sales Reports**: Generate reports for different time periods.
- **Inventory Reports**: Track stock levels, low stock, and expiry dates.
- **Financial Analytics**: Monitor revenue and profit.
- **Interactive Charts**: Visualize sales and inventory data.

### 🔧 System Features
- **Database Management**: Uses SQLite for easy setup and portability.
- **Backup & Restore**: Secure your data with manual and automatic backups.
- **Data Export**: Export reports to PDF and CSV formats.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- `pip` (Python package installer)

### Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/medical-store-management.git
    cd medical-store-management
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python -m medical_store_app.main
    ```

### Default Login Credentials
-   **Admin**:
    -   **Username**: `admin`
    -   **Password**: `admin123`
-   **Cashier**:
    -   **Username**: `cashier`
    -   **Password**: `cashier123`

## 🛠️ Technologies Used

-   **Backend**: Python
-   **GUI Framework**: PySide6 (the official Python bindings for Qt)
-   **Database**: SQLite
-   **Styling**: Custom QSS (Qt Style Sheets)

## 🏗️ Project Structure
```
medical-store-management/
├── medical_store_app/           # Main application package
│   ├── config/                  # Configuration and database setup
│   ├── models/                  # Data models
│   ├── repositories/            # Data access layer
│   ├── managers/                # Business logic layer
│   ├── ui/                      # User interface components
│   └── utils/                   # Utility functions
├── scripts/                     # Utility scripts
├── tests/                       # Test files
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes and commit them (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/your-feature-name`).
5.  Open a pull request.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

-   This project was built using the powerful **PySide6** framework.
-   The UI design was inspired by modern desktop application trends.
