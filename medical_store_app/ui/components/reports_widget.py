"""
Reports Widget for Medical Store Management Application
Provides comprehensive reporting interface with charts, tables, and filters
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QPushButton, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem,
    QTabWidget, QScrollArea, QGroupBox, QSplitter, QHeaderView,
    QProgressBar, QMessageBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate, QThread, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

from .base_components import StyledButton
from ...managers.report_manager import ReportManager, DateRange, ReportData


class ReportGenerationThread(QThread):
    """Thread for generating reports without blocking UI"""
    
    # Signals
    report_generated = Signal(object)  # ReportData
    error_occurred = Signal(str)  # Error message
    progress_updated = Signal(int)  # Progress percentage
    
    def __init__(self, report_manager: ReportManager, date_range: DateRange, report_type: str):
        super().__init__()
        self.report_manager = report_manager
        self.date_range = date_range
        self.report_type = report_type
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Run report generation in background thread"""
        try:
            self.progress_updated.emit(10)
            
            if self.report_type == "sales":
                self.progress_updated.emit(30)
                report = self.report_manager.generate_sales_report(self.date_range)
                self.progress_updated.emit(80)
                
                if report:
                    self.progress_updated.emit(100)
                    self.report_generated.emit(report)
                else:
                    self.error_occurred.emit("Failed to generate sales report")
                    
            elif self.report_type == "inventory":
                self.progress_updated.emit(30)
                report = self.report_manager.generate_inventory_report()
                self.progress_updated.emit(80)
                
                if report:
                    self.progress_updated.emit(100)
                    self.report_generated.emit(report)
                else:
                    self.error_occurred.emit("Failed to generate inventory report")
            else:
                self.error_occurred.emit(f"Unknown report type: {self.report_type}")
                
        except Exception as e:
            self.logger.error(f"Error in report generation thread: {e}")
            self.error_occurred.emit(str(e))


class ReportChartWidget(QWidget):
    """Chart widget for displaying report data"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self._setup_ui()
        self._setup_chart()
    
    def _setup_ui(self):
        """Set up chart widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(300)
        
        layout.addWidget(self.canvas)
    
    def _setup_chart(self):
        """Set up matplotlib chart"""
        self.figure.patch.set_facecolor('white')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('white')
        
        # Style spines
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#E1E5E9')
        self.ax.spines['bottom'].set_color('#E1E5E9')
        
        # Set grid
        self.ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        self.ax.set_axisbelow(True)
        
        self.figure.tight_layout(pad=2.0)
    
    def plot_sales_trend(self, daily_data: List[Dict[str, Any]], title: str = "Sales Trend"):
        """Plot sales trend chart"""
        try:
            self.ax.clear()
            
            if not daily_data:
                self.ax.text(0.5, 0.5, 'No data available', 
                           horizontalalignment='center', verticalalignment='center',
                           transform=self.ax.transAxes, fontsize=12, color='#666666')
                self.canvas.draw()
                return
            
            # Prepare data
            dates = []
            revenues = []
            transactions = []
            
            for item in daily_data:
                try:
                    date_obj = datetime.strptime(item['date'], '%Y-%m-%d').date()
                    dates.append(date_obj)
                    revenues.append(item['revenue'])
                    transactions.append(item['transactions'])
                except (ValueError, KeyError) as e:
                    self.logger.warning(f"Invalid data item: {item}, error: {e}")
                    continue
            
            if not dates:
                self.ax.text(0.5, 0.5, 'Invalid data format', 
                           horizontalalignment='center', verticalalignment='center',
                           transform=self.ax.transAxes, fontsize=12, color='#666666')
                self.canvas.draw()
                return
            
            # Create dual-axis plot
            ax2 = self.ax.twinx()
            
            # Plot revenue (primary axis)
            line1 = self.ax.plot(dates, revenues, 
                               color='#2D9CDB', linewidth=2.5, 
                               marker='o', markersize=5, label='Revenue ($)')
            self.ax.fill_between(dates, revenues, alpha=0.2, color='#2D9CDB')
            
            # Plot transactions (secondary axis)
            line2 = ax2.plot(dates, transactions, 
                           color='#27AE60', linewidth=2, 
                           marker='s', markersize=4, label='Transactions')
            
            # Format axes
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
            plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Set labels and title
            self.ax.set_xlabel('Date', fontsize=11, color='#333333')
            self.ax.set_ylabel('Revenue ($)', fontsize=11, color='#2D9CDB')
            ax2.set_ylabel('Transactions', fontsize=11, color='#27AE60')
            self.ax.set_title(title, fontsize=14, fontweight='bold', color='#333333', pad=20)
            
            # Style axes
            self.ax.tick_params(colors='#666666', labelsize=9)
            ax2.tick_params(colors='#666666', labelsize=9)
            
            # Color y-axis labels
            self.ax.tick_params(axis='y', colors='#2D9CDB')
            ax2.tick_params(axis='y', colors='#27AE60')
            
            # Style spines
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            ax2.spines['top'].set_visible(False)
            ax2.spines['left'].set_visible(False)
            
            # Legend
            lines1, labels1 = self.ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            self.ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=False)
            
            self.figure.tight_layout(pad=2.0)
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting sales trend: {e}")
            self.ax.clear()
            self.ax.text(0.5, 0.5, f'Error: {str(e)}', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=self.ax.transAxes, fontsize=12, color='#E74C3C')
            self.canvas.draw()
    
    def plot_payment_methods(self, payment_data: List[Dict[str, Any]], title: str = "Payment Methods"):
        """Plot payment methods pie chart"""
        try:
            self.ax.clear()
            
            if not payment_data:
                self.ax.text(0.5, 0.5, 'No payment data available', 
                           horizontalalignment='center', verticalalignment='center',
                           transform=self.ax.transAxes, fontsize=12, color='#666666')
                self.canvas.draw()
                return
            
            # Prepare data
            methods = []
            revenues = []
            colors = ['#2D9CDB', '#27AE60', '#F2C94C', '#E74C3C', '#9B59B6']
            
            for i, item in enumerate(payment_data):
                methods.append(item['method'].title())
                revenues.append(item['revenue'])
            
            # Create pie chart
            wedges, texts, autotexts = self.ax.pie(revenues, labels=methods, autopct='%1.1f%%',
                                                  colors=colors[:len(methods)], startangle=90)
            
            # Style text
            for text in texts:
                text.set_fontsize(10)
                text.set_color('#333333')
            
            for autotext in autotexts:
                autotext.set_fontsize(9)
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            self.ax.set_title(title, fontsize=14, fontweight='bold', color='#333333', pad=20)
            
            self.figure.tight_layout(pad=2.0)
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting payment methods: {e}")
            self.ax.clear()
            self.ax.text(0.5, 0.5, f'Error: {str(e)}', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=self.ax.transAxes, fontsize=12, color='#E74C3C')
            self.canvas.draw()


class ReportTableWidget(QTableWidget):
    """Enhanced table widget for displaying report data"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self._setup_table()
    
    def _setup_table(self):
        """Set up table appearance and behavior"""
        # Table behavior
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setSortingEnabled(True)
        
        # Header behavior
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.verticalHeader().setVisible(False)
        
        # Styling
        table_style = """
            QTableWidget {
                background-color: white;
                border: 1px solid #E1E5E9;
                border-radius: 8px;
                gridline-color: #F0F0F0;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #F8F9FA;
                color: #333333;
                font-weight: bold;
                font-size: 11px;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #E1E5E9;
            }
            QHeaderView::section:hover {
                background-color: #E9ECEF;
            }
        """
        self.setStyleSheet(table_style)
    
    def populate_sales_summary(self, daily_data: List[Dict[str, Any]]):
        """Populate table with sales summary data"""
        try:
            if not daily_data:
                self.setRowCount(0)
                self.setColumnCount(0)
                return
            
            # Set up columns
            headers = ['Date', 'Transactions', 'Revenue ($)', 'Avg Transaction ($)']
            self.setColumnCount(len(headers))
            self.setHorizontalHeaderLabels(headers)
            self.setRowCount(len(daily_data))
            
            # Populate data
            for row, item in enumerate(daily_data):
                # Date
                date_item = QTableWidgetItem(item['date'])
                date_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 0, date_item)
                
                # Transactions
                trans_item = QTableWidgetItem(str(item['transactions']))
                trans_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 1, trans_item)
                
                # Revenue
                revenue_item = QTableWidgetItem(f"${item['revenue']:.2f}")
                revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.setItem(row, 2, revenue_item)
                
                # Average transaction
                avg_trans = item['revenue'] / item['transactions'] if item['transactions'] > 0 else 0
                avg_item = QTableWidgetItem(f"${avg_trans:.2f}")
                avg_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.setItem(row, 3, avg_item)
            
            # Resize columns to content
            self.resizeColumnsToContents()
            
        except Exception as e:
            self.logger.error(f"Error populating sales summary table: {e}")
    
    def populate_top_medicines(self, medicines_data: List[Dict[str, Any]]):
        """Populate table with top medicines data"""
        try:
            if not medicines_data:
                self.setRowCount(0)
                self.setColumnCount(0)
                return
            
            # Set up columns
            headers = ['Rank', 'Medicine Name', 'Quantity Sold', 'Revenue ($)', 'Transactions']
            self.setColumnCount(len(headers))
            self.setHorizontalHeaderLabels(headers)
            self.setRowCount(len(medicines_data))
            
            # Populate data
            for row, item in enumerate(medicines_data):
                # Rank
                rank_item = QTableWidgetItem(str(row + 1))
                rank_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 0, rank_item)
                
                # Medicine name
                name_item = QTableWidgetItem(item['name'])
                self.setItem(row, 1, name_item)
                
                # Quantity sold
                qty_item = QTableWidgetItem(str(item['total_quantity']))
                qty_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 2, qty_item)
                
                # Revenue
                revenue_item = QTableWidgetItem(f"${item['total_revenue']:.2f}")
                revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.setItem(row, 3, revenue_item)
                
                # Transactions
                trans_item = QTableWidgetItem(str(item['transactions']))
                trans_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 4, trans_item)
            
            # Resize columns to content
            self.resizeColumnsToContents()
            
        except Exception as e:
            self.logger.error(f"Error populating top medicines table: {e}")


class DateRangeSelector(QWidget):
    """Date range selector widget with predefined ranges and custom dates"""
    
    # Signals
    date_range_changed = Signal(object)  # DateRange
    
    def __init__(self, report_manager: ReportManager, parent=None):
        super().__init__(parent)
        self.report_manager = report_manager
        self.logger = logging.getLogger(__name__)
        self._setup_ui()
        self._load_predefined_ranges()
    
    def _setup_ui(self):
        """Set up date range selector UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Predefined ranges dropdown
        layout.addWidget(QLabel("Quick Range:"))
        self.range_combo = QComboBox()
        self.range_combo.setMinimumWidth(150)
        self.range_combo.currentTextChanged.connect(self._on_range_changed)
        layout.addWidget(self.range_combo)
        
        layout.addWidget(QLabel("or Custom:"))
        
        # Custom date range
        layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.dateChanged.connect(self._on_custom_date_changed)
        layout.addWidget(self.start_date)
        
        layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self._on_custom_date_changed)
        layout.addWidget(self.end_date)
        
        layout.addStretch()
    
    def _load_predefined_ranges(self):
        """Load predefined date ranges"""
        try:
            ranges = self.report_manager.get_predefined_date_ranges()
            
            self.range_combo.addItem("Custom", None)
            for name, date_range in ranges.items():
                display_name = name.replace('_', ' ').title()
                self.range_combo.addItem(display_name, date_range)
            
            # Set default to "Last 30 Days"
            index = self.range_combo.findText("Last 30 Days")
            if index >= 0:
                self.range_combo.setCurrentIndex(index)
            
        except Exception as e:
            self.logger.error(f"Error loading predefined ranges: {e}")
    
    def _on_range_changed(self):
        """Handle predefined range selection"""
        try:
            current_data = self.range_combo.currentData()
            if current_data:  # Not "Custom"
                date_range = current_data
                
                # Update date widgets to reflect the range
                start_qdate = QDate.fromString(date_range.start_date, Qt.ISODate)
                end_qdate = QDate.fromString(date_range.end_date, Qt.ISODate)
                
                self.start_date.setDate(start_qdate)
                self.end_date.setDate(end_qdate)
                
                self.date_range_changed.emit(date_range)
            
        except Exception as e:
            self.logger.error(f"Error handling range change: {e}")
    
    def _on_custom_date_changed(self):
        """Handle custom date range changes"""
        try:
            # Set combo to "Custom"
            self.range_combo.setCurrentIndex(0)
            
            # Create date range from custom dates
            start_date = self.start_date.date().toString(Qt.ISODate)
            end_date = self.end_date.date().toString(Qt.ISODate)
            
            date_range = DateRange(start_date, end_date)
            self.date_range_changed.emit(date_range)
            
        except Exception as e:
            self.logger.error(f"Error handling custom date change: {e}")
    
    def get_current_range(self) -> DateRange:
        """Get currently selected date range"""
        start_date = self.start_date.date().toString(Qt.ISODate)
        end_date = self.end_date.date().toString(Qt.ISODate)
        return DateRange(start_date, end_date)


class ReportsWidget(QWidget):
    """Main reports widget with comprehensive reporting interface"""
    
    # Signals
    export_requested = Signal(str, object)  # format, report_data
    
    def __init__(self, report_manager: ReportManager, parent=None):
        super().__init__(parent)
        self.report_manager = report_manager
        self.logger = logging.getLogger(__name__)
        self.current_report = None
        self.generation_thread = None
        
        self._setup_ui()
        self._apply_styling()
        
        # Auto-generate initial report
        QTimer.singleShot(500, self._generate_initial_report)
    
    def _setup_ui(self):
        """Set up reports widget UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header section
        self._create_header_section(main_layout)
        
        # Controls section
        self._create_controls_section(main_layout)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Content tabs
        self._create_content_tabs(main_layout)
    
    def _create_header_section(self, parent_layout):
        """Create header section with title and export buttons"""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Sales & Analytics Reports")
        title_label.setObjectName("reportsTitle")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Export buttons
        self.export_csv_btn = StyledButton("Export CSV", button_type="outline")
        self.export_csv_btn.clicked.connect(lambda: self._request_export("csv"))
        self.export_csv_btn.setEnabled(False)
        header_layout.addWidget(self.export_csv_btn)
        
        self.export_excel_btn = StyledButton("Export Excel", button_type="outline")
        self.export_excel_btn.clicked.connect(lambda: self._request_export("excel"))
        self.export_excel_btn.setEnabled(False)
        header_layout.addWidget(self.export_excel_btn)
        
        self.export_pdf_btn = StyledButton("Export PDF", button_type="secondary")
        self.export_pdf_btn.clicked.connect(lambda: self._request_export("pdf"))
        self.export_pdf_btn.setEnabled(False)
        header_layout.addWidget(self.export_pdf_btn)
        
        parent_layout.addLayout(header_layout)
    
    def _create_controls_section(self, parent_layout):
        """Create controls section with date range and report type"""
        controls_frame = QFrame()
        controls_frame.setObjectName("controlsFrame")
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(16, 16, 16, 16)
        controls_layout.setSpacing(12)
        
        # First row: Report type and date range
        first_row = QHBoxLayout()
        
        # Report type selector
        first_row.addWidget(QLabel("Report Type:"))
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItem("Sales Report", "sales")
        self.report_type_combo.addItem("Inventory Report", "inventory")
        self.report_type_combo.currentTextChanged.connect(self._on_report_type_changed)
        first_row.addWidget(self.report_type_combo)
        
        first_row.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
        
        # Date range selector
        self.date_range_selector = DateRangeSelector(self.report_manager)
        self.date_range_selector.date_range_changed.connect(self._on_date_range_changed)
        first_row.addWidget(self.date_range_selector)
        
        first_row.addStretch()
        
        # Generate button
        self.generate_btn = StyledButton("Generate Report", button_type="primary")
        self.generate_btn.clicked.connect(self._generate_report)
        first_row.addWidget(self.generate_btn)
        
        controls_layout.addLayout(first_row)
        parent_layout.addWidget(controls_frame)
    
    def _create_content_tabs(self, parent_layout):
        """Create content tabs for different views"""
        self.tab_widget = QTabWidget()
        
        # Overview tab
        self.overview_tab = self._create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "Overview")
        
        # Charts tab
        self.charts_tab = self._create_charts_tab()
        self.tab_widget.addTab(self.charts_tab, "Charts")
        
        # Data table tab
        self.table_tab = self._create_table_tab()
        self.tab_widget.addTab(self.table_tab, "Data Table")
        
        parent_layout.addWidget(self.tab_widget) 
   
    def _create_overview_tab(self) -> QWidget:
        """Create overview tab with key metrics"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Summary cards
        self.summary_frame = QFrame()
        self.summary_frame.setObjectName("summaryFrame")
        summary_layout = QGridLayout(self.summary_frame)
        summary_layout.setSpacing(16)
        
        # Create summary labels (will be populated when report is generated)
        self.summary_labels = {}
        summary_items = [
            ("total_revenue", "Total Revenue", "$0.00"),
            ("total_transactions", "Total Transactions", "0"),
            ("avg_transaction", "Average Transaction", "$0.00"),
            ("best_day", "Best Day", "N/A")
        ]
        
        for i, (key, title, default_value) in enumerate(summary_items):
            card_frame = QFrame()
            card_frame.setObjectName("summaryCard")
            card_layout = QVBoxLayout(card_frame)
            card_layout.setContentsMargins(16, 12, 16, 12)
            
            title_label = QLabel(title)
            title_label.setObjectName("summaryCardTitle")
            card_layout.addWidget(title_label)
            
            value_label = QLabel(default_value)
            value_label.setObjectName("summaryCardValue")
            card_layout.addWidget(value_label)
            
            self.summary_labels[key] = value_label
            summary_layout.addWidget(card_frame, i // 2, i % 2)
        
        layout.addWidget(self.summary_frame)
        
        # Trends section
        trends_label = QLabel("Trends & Insights")
        trends_label.setObjectName("sectionHeader")
        layout.addWidget(trends_label)
        
        self.trends_text = QLabel("Generate a report to see trends and insights.")
        self.trends_text.setObjectName("trendsText")
        self.trends_text.setWordWrap(True)
        layout.addWidget(self.trends_text)
        
        layout.addStretch()
        return tab
    
    def _create_charts_tab(self) -> QWidget:
        """Create charts tab with visualizations"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Chart controls are now handled by the enhanced chart widget
        
        # Enhanced chart widget
        from .enhanced_charts import ProfessionalChartWidget
        self.chart_widget = ProfessionalChartWidget()
        layout.addWidget(self.chart_widget)
        
        return tab
    
    def _create_table_tab(self) -> QWidget:
        """Create table tab with detailed data"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Table selector
        table_controls = QHBoxLayout()
        table_controls.addWidget(QLabel("Table View:"))
        
        self.table_type_combo = QComboBox()
        self.table_type_combo.addItem("Daily Summary", "daily")
        self.table_type_combo.addItem("Top Medicines", "medicines")
        self.table_type_combo.currentTextChanged.connect(self._on_table_type_changed)
        table_controls.addWidget(self.table_type_combo)
        
        table_controls.addStretch()
        layout.addLayout(table_controls)
        
        # Table widget
        self.table_widget = ReportTableWidget()
        layout.addWidget(self.table_widget)
        
        return tab
    
    def _apply_styling(self):
        """Apply widget styling"""
        reports_style = """
            QWidget {
                background-color: #F8F9FA;
            }
            QLabel#reportsTitle {
                color: #333333;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QLabel#sectionHeader {
                color: #555555;
                font-weight: 500;
                font-size: 14px;
                margin: 10px 0px 5px 0px;
            }
            QFrame#controlsFrame {
                background-color: white;
                border: 1px solid #E1E5E9;
                border-radius: 8px;
            }
            QFrame#summaryFrame {
                background-color: transparent;
            }
            QFrame#summaryCard {
                background-color: white;
                border: 1px solid #E1E5E9;
                border-radius: 8px;
                margin: 4px;
            }
            QLabel#summaryCardTitle {
                color: #666666;
                font-size: 11px;
                font-weight: 500;
            }
            QLabel#summaryCardValue {
                color: #2D9CDB;
                font-size: 20px;
                font-weight: bold;
                margin-top: 4px;
            }
            QLabel#trendsText {
                color: #666666;
                font-size: 12px;
                padding: 16px;
                background-color: white;
                border: 1px solid #E1E5E9;
                border-radius: 8px;
            }
            QTabWidget::pane {
                border: 1px solid #E1E5E9;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F8F9FA;
                color: #666666;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #2D9CDB;
                border-bottom: 2px solid #2D9CDB;
            }
            QTabBar::tab:hover {
                background-color: #E9ECEF;
            }
        """
        self.setStyleSheet(reports_style)    

    def _generate_initial_report(self):
        """Generate initial report with default settings"""
        self._generate_report()
    
    def _generate_report(self):
        """Generate report based on current settings"""
        try:
            if self.generation_thread and self.generation_thread.isRunning():
                return  # Already generating
            
            report_type = self.report_type_combo.currentData()
            date_range = self.date_range_selector.get_current_range()
            
            # Validate date range
            validation_errors = date_range.validate()
            if validation_errors:
                QMessageBox.warning(self, "Invalid Date Range", 
                                  "\n".join(validation_errors))
                return
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.generate_btn.setEnabled(False)
            
            # Start generation thread
            self.generation_thread = ReportGenerationThread(
                self.report_manager, date_range, report_type
            )
            self.generation_thread.report_generated.connect(self._on_report_generated)
            self.generation_thread.error_occurred.connect(self._on_report_error)
            self.generation_thread.progress_updated.connect(self.progress_bar.setValue)
            self.generation_thread.finished.connect(self._on_generation_finished)
            self.generation_thread.start()
            
        except Exception as e:
            self.logger.error(f"Error starting report generation: {e}")
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
            self._on_generation_finished()
    
    def _on_report_generated(self, report_data):
        """Handle successful report generation"""
        try:
            self.current_report = report_data
            self._update_ui_with_report(report_data)
            
            # Enable export buttons
            self.export_csv_btn.setEnabled(True)
            self.export_excel_btn.setEnabled(True)
            self.export_pdf_btn.setEnabled(True)
            
        except Exception as e:
            self.logger.error(f"Error handling generated report: {e}")
    
    def _on_report_error(self, error_message):
        """Handle report generation error"""
        QMessageBox.critical(self, "Report Generation Error", error_message)
    
    def _on_generation_finished(self):
        """Handle generation thread completion"""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        if self.generation_thread:
            self.generation_thread.deleteLater()
            self.generation_thread = None
    
    def _update_ui_with_report(self, report_data):
        """Update UI with generated report data"""
        try:
            if isinstance(report_data, ReportData):
                self._update_sales_report_ui(report_data)
            elif isinstance(report_data, dict):
                self._update_inventory_report_ui(report_data)
            
        except Exception as e:
            self.logger.error(f"Error updating UI with report: {e}")
    
    def _update_sales_report_ui(self, report: ReportData):
        """Update UI with sales report data"""
        try:
            # Update overview tab
            summary = report.summary
            self.summary_labels["total_revenue"].setText(f"${summary.get('total_revenue', 0):.2f}")
            self.summary_labels["total_transactions"].setText(str(summary.get('total_transactions', 0)))
            
            avg_trans = summary.get('average_transaction', 0)
            self.summary_labels["avg_transaction"].setText(f"${avg_trans:.2f}")
            
            # Find best day
            best_day = "N/A"
            if report.daily_breakdown:
                best_day_data = max(report.daily_breakdown, key=lambda x: x['revenue'])
                best_day = f"{best_day_data['date']} (${best_day_data['revenue']:.2f})"
            self.summary_labels["best_day"].setText(best_day)
            
            # Update trends
            trends = report.trends
            if trends:
                revenue_change = trends.get('revenue_change', {})
                direction = revenue_change.get('direction', 'stable')
                percentage = revenue_change.get('percentage', 0)
                
                trend_text = f"Revenue is {direction}"
                if direction != 'stable':
                    trend_text += f" by {percentage:.1f}% compared to previous period"
                
                self.trends_text.setText(trend_text)
            else:
                self.trends_text.setText("No trend data available for comparison.")
            
            # Update charts
            self._update_charts_with_sales_data(report)
            
            # Update tables
            self._update_tables_with_sales_data(report)
            
        except Exception as e:
            self.logger.error(f"Error updating sales report UI: {e}")
    
    def _update_inventory_report_ui(self, report: Dict[str, Any]):
        """Update UI with inventory report data"""
        try:
            # Update overview tab with inventory data
            summary = report.get('summary', {})
            self.summary_labels["total_revenue"].setText(f"${summary.get('total_stock_value', 0):.2f}")
            self.summary_labels["total_transactions"].setText(str(summary.get('total_medicines', 0)))
            self.summary_labels["avg_transaction"].setText(f"{summary.get('low_stock_count', 0)} Low Stock")
            self.summary_labels["best_day"].setText(f"{summary.get('expired_count', 0)} Expired")
            
            # Update trends with inventory insights
            insights = []
            if summary.get('low_stock_count', 0) > 0:
                insights.append(f"{summary['low_stock_count']} medicines need restocking")
            if summary.get('expired_count', 0) > 0:
                insights.append(f"{summary['expired_count']} medicines are expired")
            
            if insights:
                self.trends_text.setText(". ".join(insights) + ".")
            else:
                self.trends_text.setText("Inventory is in good condition.")
            
            # Update charts with inventory data
            self._update_charts_with_inventory_data(report)
            
        except Exception as e:
            self.logger.error(f"Error updating inventory report UI: {e}")
    
    def _update_charts_with_inventory_data(self, report: Dict[str, Any]):
        """Update charts with inventory report data"""
        try:
            # Prepare inventory chart data
            chart_data = {
                'inventory_summary': report.get('summary', {}),
                'low_stock_medicines': report.get('low_stock_medicines', []),
                'expired_medicines': report.get('expired_medicines', []),
                'category_breakdown': report.get('category_breakdown', []),
                'report_type': 'inventory'
            }
            
            # Update chart title
            self.chart_widget.set_chart_title("Inventory Analytics")
            
            # Update chart data
            self.chart_widget.update_chart_data(chart_data)
            
        except Exception as e:
            self.logger.error(f"Error updating inventory charts: {e}")
    
    def _update_charts_with_sales_data(self, report: ReportData):
        """Update charts with sales report data"""
        try:
            # Prepare comprehensive chart data
            chart_data = {
                'daily_breakdown': report.daily_breakdown,
                'payment_methods': report.payment_methods,
                'top_medicines': report.top_medicines,
                'summary': report.summary,
                'trends': report.trends,
                'period_start': report.period_start,
                'period_end': report.period_end
            }
            
            # Update chart title
            self.chart_widget.set_chart_title(f"Sales Analytics ({report.period_start} to {report.period_end})")
            
            # Update chart data
            self.chart_widget.update_chart_data(chart_data)
            
        except Exception as e:
            self.logger.error(f"Error updating charts: {e}")
    
    def _update_tables_with_sales_data(self, report: ReportData):
        """Update tables with sales report data"""
        try:
            current_table_type = self.table_type_combo.currentData()
            
            if current_table_type == "daily":
                self.table_widget.populate_sales_summary(report.daily_breakdown)
            elif current_table_type == "medicines":
                self.table_widget.populate_top_medicines(report.top_medicines)
            
        except Exception as e:
            self.logger.error(f"Error updating tables: {e}")
    
    def _on_report_type_changed(self):
        """Handle report type change"""
        report_type = self.report_type_combo.currentData()
        
        # Enable/disable date range for inventory reports
        if report_type == "inventory":
            self.date_range_selector.setEnabled(False)
        else:
            self.date_range_selector.setEnabled(True)
    
    def _on_date_range_changed(self, date_range: DateRange):
        """Handle date range change"""
        # Auto-generate report when date range changes
        if hasattr(self, 'generate_btn'):
            QTimer.singleShot(100, self._generate_report)
    
    # Chart type changes are now handled by the enhanced chart widget
    
    def _on_table_type_changed(self):
        """Handle table type change"""
        if self.current_report and isinstance(self.current_report, ReportData):
            self._update_tables_with_sales_data(self.current_report)
    
    def _request_export(self, format_type: str):
        """Request report export in specified format"""
        if self.current_report:
            self.export_requested.emit(format_type, self.current_report)
        else:
            QMessageBox.information(self, "No Report", 
                                  "Please generate a report first before exporting.")