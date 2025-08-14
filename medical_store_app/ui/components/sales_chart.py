"""
Sales Chart Widget for Medical Store Management Application
Provides mini sales chart showing last 7 days performance
"""

import logging
from typing import Dict, List
from datetime import datetime, date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class SalesChartWidget(QWidget):
    """Mini sales chart widget for dashboard"""
    
    # Signals
    chart_clicked = Signal()  # Emitted when chart is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.sales_data = {}
        
        self._setup_ui()
        self._setup_chart()
        self._apply_styling()
    
    def _setup_ui(self):
        """Set up the chart widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Sales Trend (Last 7 Days)")
        title_label.setObjectName("chartTitle")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setWeight(QFont.Medium)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Chart container
        self.chart_frame = QFrame()
        self.chart_frame.setFrameStyle(QFrame.Box)
        self.chart_frame.setLineWidth(1)
        chart_layout = QVBoxLayout(self.chart_frame)
        chart_layout.setContentsMargins(8, 8, 8, 8)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(200)
        self.canvas.setMaximumHeight(250)
        
        chart_layout.addWidget(self.canvas)
        layout.addWidget(self.chart_frame)
    
    def _setup_chart(self):
        """Set up the matplotlib chart"""
        # Configure matplotlib for better appearance
        plt.style.use('default')
        
        # Create subplot
        self.ax = self.figure.add_subplot(111)
        
        # Set chart styling
        self.figure.patch.set_facecolor('white')
        self.ax.set_facecolor('white')
        
        # Remove top and right spines
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        # Style remaining spines
        self.ax.spines['left'].set_color('#E1E5E9')
        self.ax.spines['bottom'].set_color('#E1E5E9')
        
        # Set grid
        self.ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        self.ax.set_axisbelow(True)
        
        # Set initial empty data
        self._plot_empty_chart()
        
        # Tight layout
        self.figure.tight_layout(pad=1.0)
    
    def _plot_empty_chart(self):
        """Plot empty chart with placeholder"""
        self.ax.clear()
        
        # Set up empty chart
        self.ax.text(0.5, 0.5, 'No sales data available', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=self.ax.transAxes, fontsize=12, color='#666666')
        
        self.ax.set_xlim(0, 7)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel('Days', fontsize=10, color='#333333')
        self.ax.set_ylabel('Sales ($)', fontsize=10, color='#333333')
        
        # Style axes
        self.ax.tick_params(colors='#666666', labelsize=9)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#E1E5E9')
        self.ax.spines['bottom'].set_color('#E1E5E9')
        
        self.canvas.draw()
    
    def update_chart_data(self, sales_data: Dict[str, float]):
        """
        Update chart with new sales data
        
        Args:
            sales_data: Dictionary with date strings as keys and sales totals as values
        """
        try:
            self.sales_data = sales_data
            
            if not sales_data:
                self._plot_empty_chart()
                return
            
            # Clear previous plot
            self.ax.clear()
            
            # Prepare data for plotting
            dates = []
            values = []
            
            for date_str, total in sorted(sales_data.items()):
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                    dates.append(date_obj)
                    values.append(total)
                except ValueError:
                    self.logger.warning(f"Invalid date format: {date_str}")
                    continue
            
            if not dates:
                self._plot_empty_chart()
                return
            
            # Create the plot
            line = self.ax.plot(dates, values, 
                              color='#2D9CDB', 
                              linewidth=2.5, 
                              marker='o', 
                              markersize=4,
                              markerfacecolor='#2D9CDB',
                              markeredgecolor='white',
                              markeredgewidth=1)
            
            # Fill area under the curve
            self.ax.fill_between(dates, values, alpha=0.2, color='#2D9CDB')
            
            # Format x-axis to show dates nicely
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            
            # Rotate date labels for better readability
            plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Set labels
            self.ax.set_xlabel('Date', fontsize=10, color='#333333')
            self.ax.set_ylabel('Sales ($)', fontsize=10, color='#333333')
            
            # Style axes
            self.ax.tick_params(colors='#666666', labelsize=9)
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            self.ax.spines['left'].set_color('#E1E5E9')
            self.ax.spines['bottom'].set_color('#E1E5E9')
            
            # Set grid
            self.ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            self.ax.set_axisbelow(True)
            
            # Auto-scale y-axis with some padding
            if values:
                max_val = max(values)
                if max_val > 0:
                    self.ax.set_ylim(0, max_val * 1.1)
                else:
                    self.ax.set_ylim(0, 100)
            
            # Tight layout
            self.figure.tight_layout(pad=1.0)
            
            # Refresh canvas
            self.canvas.draw()
            
            self.logger.info(f"Chart updated with {len(dates)} data points")
            
        except Exception as e:
            self.logger.error(f"Error updating chart data: {str(e)}")
            self._plot_empty_chart()
    
    def get_chart_summary(self) -> Dict[str, float]:
        """
        Get summary statistics from current chart data
        
        Returns:
            Dictionary with summary statistics
        """
        try:
            if not self.sales_data:
                return {'total': 0.0, 'average': 0.0, 'max': 0.0, 'min': 0.0}
            
            values = list(self.sales_data.values())
            return {
                'total': sum(values),
                'average': sum(values) / len(values) if values else 0.0,
                'max': max(values) if values else 0.0,
                'min': min(values) if values else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting chart summary: {str(e)}")
            return {'total': 0.0, 'average': 0.0, 'max': 0.0, 'min': 0.0}
    
    def _apply_styling(self):
        """Apply widget styling"""
        chart_style = """
            QWidget {
                background-color: white;
            }
            QLabel#chartTitle {
                color: #333333;
                font-weight: 500;
                margin-bottom: 5px;
            }
            QFrame {
                background-color: white;
                border: 1px solid #E1E5E9;
                border-radius: 8px;
            }
        """
        self.setStyleSheet(chart_style)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            self.chart_clicked.emit()
        super().mousePressEvent(event)


class SalesChartCard(QFrame):
    """Sales chart card widget for dashboard integration"""
    
    # Signals
    card_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
        self._setup_styling()
    
    def _setup_ui(self):
        """Set up the card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create chart widget
        self.chart_widget = SalesChartWidget()
        self.chart_widget.chart_clicked.connect(self.card_clicked.emit)
        
        layout.addWidget(self.chart_widget)
    
    def _setup_styling(self):
        """Set up card styling"""
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        
        card_style = """
            QFrame {
                background-color: white;
                border: 1px solid #E1E5E9;
                border-radius: 8px;
                margin: 4px;
            }
            QFrame:hover {
                border-color: #2D9CDB;
                box-shadow: 0 2px 8px rgba(45, 156, 219, 0.1);
            }
        """
        self.setStyleSheet(card_style)
        
        # Make clickable
        self.setCursor(Qt.PointingHandCursor)
    
    def update_chart_data(self, sales_data: Dict[str, float]):
        """Update chart data"""
        self.chart_widget.update_chart_data(sales_data)
    
    def get_chart_summary(self) -> Dict[str, float]:
        """Get chart summary"""
        return self.chart_widget.get_chart_summary()
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            self.card_clicked.emit()
        super().mousePressEvent(event)