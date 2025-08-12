"""
Database configuration and connection management for Medical Store Management Application
Handles SQLite database initialization, connection management, and table creation
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, Any, Dict
from contextlib import contextmanager


class DatabaseManager:
    """Manages SQLite database connection and initialization"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        self.logger = logging.getLogger(__name__)
        
        if db_path is None:
            # Default database location in application directory
            app_dir = Path(__file__).parent.parent
            data_dir = app_dir / "data"
            data_dir.mkdir(exist_ok=True)
            self.db_path = str(data_dir / "medical_store.db")
        else:
            self.db_path = db_path
            
        self._connection: Optional[sqlite3.Connection] = None
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get database connection, creating if necessary
        
        Returns:
            SQLite database connection
        """
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=30.0
                )
                # Enable foreign key constraints
                self._connection.execute("PRAGMA foreign_keys = ON")
                # Set row factory for dict-like access
                self._connection.row_factory = sqlite3.Row
                self.logger.info(f"Database connection established: {self.db_path}")
            except sqlite3.Error as e:
                self.logger.error(f"Failed to connect to database: {e}")
                raise
        
        return self._connection
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager for database cursor with automatic commit/rollback
        
        Yields:
            SQLite cursor object
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database operation failed, rolled back: {e}")
            raise
        finally:
            cursor.close()
    
    def initialize(self) -> bool:
        """
        Initialize database with required tables
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing database tables...")
            
            with self.get_cursor() as cursor:
                # Create medicines table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS medicines (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        batch_no TEXT NOT NULL,
                        expiry_date TEXT NOT NULL,
                        quantity INTEGER NOT NULL DEFAULT 0,
                        purchase_price REAL NOT NULL DEFAULT 0.0,
                        selling_price REAL NOT NULL DEFAULT 0.0,
                        barcode TEXT UNIQUE,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create sales table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sales (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        items TEXT NOT NULL,
                        subtotal REAL NOT NULL DEFAULT 0.0,
                        discount REAL NOT NULL DEFAULT 0.0,
                        tax REAL NOT NULL DEFAULT 0.0,
                        total REAL NOT NULL DEFAULT 0.0,
                        payment_method TEXT NOT NULL DEFAULT 'cash',
                        cashier_id INTEGER,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (cashier_id) REFERENCES users(id)
                    )
                """)
                
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL CHECK (role IN ('admin', 'cashier')),
                        is_active BOOLEAN DEFAULT 1,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        last_login TEXT
                    )
                """)
                
                # Create settings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        description TEXT,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create default admin user if no users exist
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                
                if user_count == 0:
                    # Import here to avoid circular imports
                    import hashlib
                    default_password = "admin123"
                    password_hash = hashlib.sha256(default_password.encode()).hexdigest()
                    
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, role, is_active)
                        VALUES (?, ?, ?, ?)
                    """, ("admin", password_hash, "admin", 1))
                    
                    self.logger.info("Default admin user created (username: admin, password: admin123)")
                
                # Insert default settings if they don't exist
                default_settings = [
                    ("store_name", "Medical Store", "Store name for receipts and reports"),
                    ("store_address", "", "Store address"),
                    ("store_phone", "", "Store contact phone"),
                    ("currency", "USD", "Currency symbol"),
                    ("tax_rate", "0.0", "Default tax rate percentage"),
                    ("low_stock_threshold", "10", "Low stock alert threshold"),
                ]
                
                for key, value, description in default_settings:
                    cursor.execute("""
                        INSERT OR IGNORE INTO settings (key, value, description)
                        VALUES (?, ?, ?)
                    """, (key, value, description))
            
            self.logger.info("Database initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            self.logger.info("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = ()) -> Any:
        """
        Execute a query and return results
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Query results
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_single(self, query: str, params: tuple = ()) -> Any:
        """
        Execute a query and return single result
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Single query result or None
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute an update/insert/delete query
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount