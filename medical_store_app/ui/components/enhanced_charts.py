"""
Enhanced Chart Components for Medical Store Management Application
Provides professional, detailed, and optimized chart visualizations
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import numpy as np

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches


class ProfessionalChartWidget(QWidget):
    """Enhanced chart widget with professional styling and multiple chart types"""
    
    # Signals
    chart_clicked = Signal(str, dict)  # chart_type, data_point
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.current_chart_type = None
        self.current_data = None
        
        # Professional color palette
        self.colors = {
            'primary': '#2D9CDB',
            'secondary': '#27AE60', 
            'accent': '#F2C94C',
            'warning': '#E67E22',
            'danger': '#E74C3C',
            'info': '#9B59B6',
            'success': '#1ABC9C',
            'dark': '#2C3E50',
            'light': '#ECF0F1',
            'muted': '#95A5A6'
        }
        
        self.gradient_colors = [
            '#2D9CDB', '#27AE60', '#F2C94C', '#E67E22', 
            '#E74C3C', '#9B59B6', '#1ABC9C', '#34495E'
        ]
        
        self._setup_ui()
        self._setup_chart()
    
    def _setup_ui(self):
        """Set up enhanced chart widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Chart controls header
        controls_layout = QHBoxLayout()
        
        # Chart title
        self.chart_title = QLabel("Sales Analytics")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Bold)
        self.chart_title.setFont(title_font)
        self.chart_title.setStyleSheet("color: #2C3E50; margin-bottom: 8px;")
        controls_layout.addWidget(self.chart_title)
        
        controls_layout.addStretch()
        
        # Chart type selector
        self.chart_type_combo = QComboBox()
        # Default sales charts
        self.sales_chart_items = [
            ("📈 Sales Trend", "trend"),
            ("💰 Revenue Analysis", "revenue_analysis"),
            ("🏪 Payment Methods", "payment_pie"),
            ("📊 Payment Comparison", "payment_bar"),
            ("📅 Daily Performance", "daily_performance"),
            ("🎯 Top Medicines", "top_medicines")
        ]
        
        # Inventory charts
        self.inventory_chart_items = [
            ("📦 Inventory Overview", "inventory_overview"),
            ("⚠️ Stock Status", "stock_status"),
            ("📊 Category Analysis", "category_analysis"),
            ("🏷️ Stock Value Distribution", "stock_value"),
            ("📉 Low Stock Alert", "low_stock"),
            ("⏰ Expiry Analysis", "expiry_analysis")
        ]
        
        # Load default sales charts
        self._load_chart_items(self.sales_chart_items)
        self.chart_type_combo.currentTextChanged.connect(self._on_chart_type_changed)
        self.chart_type_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                background-color: white;
                min-width: 180px;
            }
            QComboBox:hover {
                border-color: #2D9CDB;
            }
        """)
        controls_layout.addWidget(self.chart_type_combo)
        
        layout.addLayout(controls_layout)
        
        # Chart canvas
        self.figure = Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(400)
        
        # Enable interactive features
        self.canvas.mpl_connect('button_press_event', self._on_chart_click)
        
        layout.addWidget(self.canvas)
    
    def _setup_chart(self):
        """Set up professional chart styling"""
        # Set figure background
        self.figure.patch.set_facecolor('#FAFBFC')
        
        # Configure matplotlib for better appearance
        plt.style.use('default')
        
        # Set default font
        plt.rcParams.update({
            'font.family': 'sans-serif',
            'font.sans-serif': ['Segoe UI', 'Arial', 'DejaVu Sans'],
            'font.size': 10,
            'axes.titlesize': 14,
            'axes.labelsize': 11,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 10,
            'figure.titlesize': 16
        })
    
    def _on_chart_type_changed(self):
        """Handle chart type change"""
        if self.current_data:
            self._refresh_current_chart()
    
    def _on_chart_click(self, event):
        """Handle chart click events"""
        if event.inaxes and self.current_data:
            # Emit signal with click information
            self.chart_clicked.emit(self.current_chart_type or "unknown", {
                'x': event.xdata,
                'y': event.ydata,
                'button': event.button
            })
    
    def _load_chart_items(self, chart_items: List[Tuple[str, str]]):
        """Load chart items into combo box"""
        self.chart_type_combo.clear()
        for display_name, chart_type in chart_items:
            self.chart_type_combo.addItem(display_name, chart_type)
    
    def update_chart_data(self, chart_data: Dict[str, Any]):
        """Update chart with new data"""
        self.current_data = chart_data
        
        # Check if this is inventory data and switch chart types accordingly
        if chart_data.get('report_type') == 'inventory':
            self._load_chart_items(self.inventory_chart_items)
        else:
            self._load_chart_items(self.sales_chart_items)
        
        self._refresh_current_chart()
    
    def _refresh_current_chart(self):
        """Refresh the current chart with updated data"""
        if not self.current_data:
            self._show_no_data_message()
            return
        
        chart_type = self.chart_type_combo.currentData()
        
        # Sales charts
        if chart_type == "trend":
            self._plot_sales_trend()
        elif chart_type == "revenue_analysis":
            self._plot_revenue_analysis()
        elif chart_type == "payment_pie":
            self._plot_payment_methods_pie()
        elif chart_type == "payment_bar":
            self._plot_payment_methods_bar()
        elif chart_type == "daily_performance":
            self._plot_daily_performance()
        elif chart_type == "top_medicines":
            self._plot_top_medicines()
        # Inventory charts
        elif chart_type == "inventory_overview":
            self._plot_inventory_overview()
        elif chart_type == "stock_status":
            self._plot_stock_status()
        elif chart_type == "category_analysis":
            self._plot_category_analysis()
        elif chart_type == "stock_value":
            self._plot_stock_value_distribution()
        elif chart_type == "low_stock":
            self._plot_low_stock_alert()
        elif chart_type == "expiry_analysis":
            self._plot_expiry_analysis()
        else:
            # Default based on data type
            if self.current_data and self.current_data.get('report_type') == 'inventory':
                self._plot_inventory_overview()
            else:
                self._plot_sales_trend()
    
    def _show_no_data_message(self):
        """Show no data available message"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, '📊 No Data Available\n\nGenerate a report to view charts', 
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=16, color='#7F8C8D',
               bbox=dict(boxstyle="round,pad=0.5", facecolor='#ECF0F1', alpha=0.8))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.canvas.draw()
    
    def _plot_sales_trend(self):
        """Plot enhanced sales trend chart"""
        try:
            daily_data = self.current_data.get('daily_breakdown', [])
            if not daily_data:
                self._show_no_data_message()
                return
            
            self.figure.clear()
            
            # Create subplots for better layout
            gs = self.figure.add_gridspec(2, 2, height_ratios=[3, 1], width_ratios=[3, 1])
            ax_main = self.figure.add_subplot(gs[0, 0])
            ax_trend = self.figure.add_subplot(gs[0, 1])
            ax_summary = self.figure.add_subplot(gs[1, :])
            
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
                except (ValueError, KeyError):
                    continue
            
            if not dates:
                self._show_no_data_message()
                return
            
            # Main trend chart
            ax_main.set_facecolor('#FAFBFC')
            
            # Plot revenue with gradient fill
            line1 = ax_main.plot(dates, revenues, color=self.colors['primary'], 
                               linewidth=3, marker='o', markersize=6, 
                               markerfacecolor='white', markeredgecolor=self.colors['primary'],
                               markeredgewidth=2, label='Revenue ($)')
            
            # Add gradient fill
            ax_main.fill_between(dates, revenues, alpha=0.3, color=self.colors['primary'])
            
            # Add trend line
            if len(dates) > 1:
                z = np.polyfit(range(len(revenues)), revenues, 1)
                p = np.poly1d(z)
                trend_line = [p(i) for i in range(len(revenues))]
                ax_main.plot(dates, trend_line, '--', color=self.colors['warning'], 
                           linewidth=2, alpha=0.8, label='Trend')
            
            # Style main chart
            ax_main.set_title('Sales Revenue Trend', fontsize=14, fontweight='bold', 
                            color=self.colors['dark'], pad=20)
            ax_main.set_xlabel('Date', fontsize=11, color=self.colors['dark'])
            ax_main.set_ylabel('Revenue ($)', fontsize=11, color=self.colors['primary'])
            
            # Format dates
            ax_main.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax_main.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//7)))
            plt.setp(ax_main.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Style axes
            ax_main.spines['top'].set_visible(False)
            ax_main.spines['right'].set_visible(False)
            ax_main.spines['left'].set_color('#BDC3C7')
            ax_main.spines['bottom'].set_color('#BDC3C7')
            ax_main.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            ax_main.tick_params(colors=self.colors['muted'], labelsize=9)
            
            # Legend
            ax_main.legend(loc='upper left', frameon=False, fontsize=10)
            
            # Trend indicator chart
            ax_trend.set_facecolor('#FAFBFC')
            
            # Calculate trend metrics
            if len(revenues) > 1:
                recent_avg = np.mean(revenues[-3:]) if len(revenues) >= 3 else revenues[-1]
                overall_avg = np.mean(revenues)
                trend_pct = ((recent_avg - overall_avg) / overall_avg * 100) if overall_avg > 0 else 0
                
                # Trend gauge
                colors_trend = [self.colors['success'] if trend_pct > 0 else self.colors['danger']]
                ax_trend.barh([0], [abs(trend_pct)], color=colors_trend, alpha=0.7)
                ax_trend.set_xlim(0, max(20, abs(trend_pct) * 1.2))
                ax_trend.set_ylim(-0.5, 0.5)
                ax_trend.set_title(f'Trend: {trend_pct:+.1f}%', fontsize=12, fontweight='bold')
                ax_trend.set_xlabel('Change %', fontsize=10)
                ax_trend.tick_params(axis='y', which='both', left=False, labelleft=False)
            
            # Summary statistics
            ax_summary.set_facecolor('#FAFBFC')
            ax_summary.axis('off')
            
            # Calculate statistics
            total_revenue = sum(revenues)
            avg_revenue = np.mean(revenues)
            max_revenue = max(revenues)
            min_revenue = min(revenues)
            total_transactions = sum(transactions)
            
            # Create summary boxes
            summary_data = [
                ('Total Revenue', f'${total_revenue:,.2f}', self.colors['primary']),
                ('Average Daily', f'${avg_revenue:,.2f}', self.colors['secondary']),
                ('Peak Day', f'${max_revenue:,.2f}', self.colors['success']),
                ('Lowest Day', f'${min_revenue:,.2f}', self.colors['warning']),
                ('Total Transactions', f'{total_transactions:,}', self.colors['info'])
            ]
            
            box_width = 0.18
            for i, (label, value, color) in enumerate(summary_data):
                x_pos = i * 0.2 + 0.1
                
                # Create colored box
                rect = Rectangle((x_pos - box_width/2, 0.3), box_width, 0.4, 
                               facecolor=color, alpha=0.1, edgecolor=color, linewidth=2)
                ax_summary.add_patch(rect)
                
                # Add text
                ax_summary.text(x_pos, 0.6, value, ha='center', va='center', 
                              fontsize=11, fontweight='bold', color=color)
                ax_summary.text(x_pos, 0.2, label, ha='center', va='center', 
                              fontsize=9, color=self.colors['dark'])
            
            ax_summary.set_xlim(0, 1)
            ax_summary.set_ylim(0, 1)
            
            self.figure.tight_layout(pad=2.0)
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting sales trend: {e}")
            self._show_error_chart(str(e))
    
    def _plot_revenue_analysis(self):
        """Plot detailed revenue analysis chart"""
        try:
            daily_data = self.current_data.get('daily_breakdown', [])
            if not daily_data:
                self._show_no_data_message()
                return
            
            self.figure.clear()
            
            # Create 2x2 subplot layout
            gs = self.figure.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
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
                except (ValueError, KeyError):
                    continue
            
            if not dates:
                self._show_no_data_message()
                return
            
            # 1. Revenue vs Transactions Scatter
            ax1 = self.figure.add_subplot(gs[0, 0])
            scatter = ax1.scatter(transactions, revenues, c=range(len(revenues)), 
                                cmap='viridis', s=100, alpha=0.7, edgecolors='white', linewidth=2)
            ax1.set_xlabel('Transactions', fontsize=10)
            ax1.set_ylabel('Revenue ($)', fontsize=10)
            ax1.set_title('Revenue vs Transactions', fontsize=12, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            
            # Add trend line
            if len(transactions) > 1:
                z = np.polyfit(transactions, revenues, 1)
                p = np.poly1d(z)
                ax1.plot(transactions, p(transactions), '--', color=self.colors['danger'], linewidth=2)
            
            # 2. Daily Revenue Distribution
            ax2 = self.figure.add_subplot(gs[0, 1])
            ax2.hist(revenues, bins=min(10, len(revenues)), color=self.colors['secondary'], 
                    alpha=0.7, edgecolor='white', linewidth=1)
            ax2.set_xlabel('Revenue ($)', fontsize=10)
            ax2.set_ylabel('Frequency', fontsize=10)
            ax2.set_title('Revenue Distribution', fontsize=12, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            
            # 3. Average Transaction Value
            ax3 = self.figure.add_subplot(gs[1, 0])
            avg_values = [r/t if t > 0 else 0 for r, t in zip(revenues, transactions)]
            bars = ax3.bar(range(len(avg_values)), avg_values, color=self.colors['accent'], 
                          alpha=0.8, edgecolor='white', linewidth=1)
            ax3.set_xlabel('Day', fontsize=10)
            ax3.set_ylabel('Avg Transaction ($)', fontsize=10)
            ax3.set_title('Average Transaction Value', fontsize=12, fontweight='bold')
            ax3.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'${height:.0f}', ha='center', va='bottom', fontsize=8)
            
            # 4. Performance Metrics
            ax4 = self.figure.add_subplot(gs[1, 1])
            ax4.axis('off')
            
            # Calculate metrics
            total_revenue = sum(revenues)
            avg_transaction = np.mean(avg_values) if avg_values else 0
            best_day_idx = revenues.index(max(revenues)) if revenues else 0
            growth_rate = ((revenues[-1] - revenues[0]) / revenues[0] * 100) if len(revenues) > 1 and revenues[0] > 0 else 0
            
            metrics_text = f"""
            📊 Performance Metrics
            
            💰 Total Revenue: ${total_revenue:,.2f}
            📈 Avg Transaction: ${avg_transaction:.2f}
            🏆 Best Day: {dates[best_day_idx].strftime('%m/%d')}
            📊 Growth Rate: {growth_rate:+.1f}%
            🎯 Peak Revenue: ${max(revenues):,.2f}
            """
            
            ax4.text(0.1, 0.9, metrics_text, transform=ax4.transAxes, fontsize=11,
                    verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", 
                    facecolor=self.colors['light'], alpha=0.8))
            
            self.figure.suptitle('Revenue Analysis Dashboard', fontsize=16, fontweight='bold', 
                               color=self.colors['dark'], y=0.95)
            
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting revenue analysis: {e}")
            self._show_error_chart(str(e))
    
    def _plot_payment_methods_pie(self):
        """Plot enhanced payment methods pie chart"""
        try:
            payment_data = self.current_data.get('payment_methods', [])
            if not payment_data:
                self._show_no_data_message()
                return
            
            self.figure.clear()
            
            # Create main pie chart and details
            gs = self.figure.add_gridspec(1, 2, width_ratios=[2, 1])
            ax_pie = self.figure.add_subplot(gs[0, 0])
            ax_details = self.figure.add_subplot(gs[0, 1])
            
            # Prepare data
            methods = []
            revenues = []
            transactions = []
            
            for item in payment_data:
                methods.append(item['method'].title())
                revenues.append(item['revenue'])
                transactions.append(item['transactions'])
            
            # Create enhanced pie chart
            wedges, texts, autotexts = ax_pie.pie(
                revenues, labels=methods, autopct='%1.1f%%',
                colors=self.gradient_colors[:len(methods)], startangle=90,
                explode=[0.05] * len(methods),  # Slightly separate slices
                shadow=True, textprops={'fontsize': 11}
            )
            
            # Enhance text styling
            for text in texts:
                text.set_fontsize(12)
                text.set_fontweight('bold')
                text.set_color(self.colors['dark'])
            
            for autotext in autotexts:
                autotext.set_fontsize(10)
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax_pie.set_title('Payment Methods Distribution', fontsize=14, 
                           fontweight='bold', color=self.colors['dark'], pad=20)
            
            # Details panel
            ax_details.axis('off')
            
            total_revenue = sum(revenues)
            total_transactions = sum(transactions)
            
            details_text = "💳 Payment Details\n\n"
            
            for i, (method, revenue, trans) in enumerate(zip(methods, revenues, transactions)):
                percentage = (revenue / total_revenue * 100) if total_revenue > 0 else 0
                avg_transaction = revenue / trans if trans > 0 else 0
                
                color_box = "█"  # Unicode block character
                details_text += f"{color_box} {method}\n"
                details_text += f"   Revenue: ${revenue:,.2f} ({percentage:.1f}%)\n"
                details_text += f"   Transactions: {trans:,}\n"
                details_text += f"   Avg: ${avg_transaction:.2f}\n\n"
            
            details_text += f"📊 Total: ${total_revenue:,.2f}\n"
            details_text += f"🧾 Transactions: {total_transactions:,}"
            
            ax_details.text(0.05, 0.95, details_text, transform=ax_details.transAxes,
                          fontsize=10, verticalalignment='top',
                          bbox=dict(boxstyle="round,pad=0.5", facecolor=self.colors['light'], alpha=0.8))
            
            self.figure.tight_layout(pad=2.0)
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting payment methods pie: {e}")
            self._show_error_chart(str(e))
    
    def _plot_payment_methods_bar(self):
        """Plot payment methods comparison bar chart"""
        try:
            payment_data = self.current_data.get('payment_methods', [])
            if not payment_data:
                self._show_no_data_message()
                return
            
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # Prepare data
            methods = [item['method'].title() for item in payment_data]
            revenues = [item['revenue'] for item in payment_data]
            transactions = [item['transactions'] for item in payment_data]
            
            # Create grouped bar chart
            x = np.arange(len(methods))
            width = 0.35
            
            # Normalize transactions for better comparison
            max_revenue = max(revenues) if revenues else 1
            normalized_transactions = [(t / max(transactions)) * max_revenue for t in transactions] if transactions else []
            
            bars1 = ax.bar(x - width/2, revenues, width, label='Revenue ($)', 
                          color=self.colors['primary'], alpha=0.8, edgecolor='white', linewidth=2)
            bars2 = ax.bar(x + width/2, normalized_transactions, width, label='Transactions (scaled)', 
                          color=self.colors['secondary'], alpha=0.8, edgecolor='white', linewidth=2)
            
            # Add value labels on bars
            for bar, value in zip(bars1, revenues):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'${value:,.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            for bar, value in zip(bars2, transactions):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{value}', ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # Styling
            ax.set_xlabel('Payment Methods', fontsize=12, fontweight='bold')
            ax.set_ylabel('Amount', fontsize=12, fontweight='bold')
            ax.set_title('Payment Methods Comparison', fontsize=14, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(methods)
            ax.legend(loc='upper right', frameon=False)
            
            # Style axes
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(True, alpha=0.3, axis='y')
            
            self.figure.tight_layout(pad=2.0)
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting payment methods bar: {e}")
            self._show_error_chart(str(e))
    
    def _plot_daily_performance(self):
        """Plot comprehensive daily performance dashboard"""
        try:
            daily_data = self.current_data.get('daily_breakdown', [])
            if not daily_data:
                self._show_no_data_message()
                return
            
            self.figure.clear()
            
            # Create complex layout
            gs = self.figure.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
            
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
                except (ValueError, KeyError):
                    continue
            
            if not dates:
                self._show_no_data_message()
                return
            
            # 1. Main performance line chart (top row, spans 2 columns)
            ax1 = self.figure.add_subplot(gs[0, :2])
            
            # Dual axis for revenue and transactions
            ax1_twin = ax1.twinx()
            
            line1 = ax1.plot(dates, revenues, color=self.colors['primary'], linewidth=3, 
                           marker='o', markersize=6, label='Revenue ($)')
            line2 = ax1_twin.plot(dates, transactions, color=self.colors['secondary'], linewidth=2, 
                                marker='s', markersize=5, label='Transactions')
            
            ax1.set_ylabel('Revenue ($)', color=self.colors['primary'], fontweight='bold')
            ax1_twin.set_ylabel('Transactions', color=self.colors['secondary'], fontweight='bold')
            ax1.set_title('Daily Performance Overview', fontsize=14, fontweight='bold', pad=15)
            
            # Format dates
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Combined legend
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1_twin.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=False)
            
            ax1.grid(True, alpha=0.3)
            
            # 2. Performance gauge (top right)
            ax2 = self.figure.add_subplot(gs[0, 2])
            
            # Calculate performance score (0-100)
            avg_revenue = np.mean(revenues)
            max_revenue = max(revenues)
            performance_score = (avg_revenue / max_revenue * 100) if max_revenue > 0 else 0
            
            # Create gauge
            theta = np.linspace(0, np.pi, 100)
            r = 1
            
            # Background arc
            ax2.plot(r * np.cos(theta), r * np.sin(theta), color='#ECF0F1', linewidth=8)
            
            # Performance arc
            perf_theta = np.linspace(0, np.pi * (performance_score / 100), int(performance_score))
            if len(perf_theta) > 0:
                color = self.colors['success'] if performance_score > 70 else \
                       self.colors['warning'] if performance_score > 40 else self.colors['danger']
                ax2.plot(r * np.cos(perf_theta), r * np.sin(perf_theta), color=color, linewidth=8)
            
            ax2.text(0, -0.3, f'{performance_score:.0f}%', ha='center', va='center', 
                    fontsize=16, fontweight='bold', color=self.colors['dark'])
            ax2.text(0, -0.5, 'Performance', ha='center', va='center', 
                    fontsize=10, color=self.colors['muted'])
            
            ax2.set_xlim(-1.2, 1.2)
            ax2.set_ylim(-0.7, 1.2)
            ax2.axis('off')
            ax2.set_title('Performance Score', fontsize=12, fontweight='bold')
            
            # 3. Revenue heatmap (middle left)
            ax3 = self.figure.add_subplot(gs[1, 0])
            
            # Create heatmap data
            revenue_matrix = np.array(revenues).reshape(-1, 1)
            im = ax3.imshow(revenue_matrix.T, cmap='RdYlGn', aspect='auto')
            ax3.set_xticks(range(len(dates)))
            ax3.set_xticklabels([d.strftime('%m/%d') for d in dates], rotation=45, ha='right')
            ax3.set_yticks([])
            ax3.set_title('Revenue Heatmap', fontsize=12, fontweight='bold')
            
            # 4. Transaction pattern (middle center)
            ax4 = self.figure.add_subplot(gs[1, 1])
            
            bars = ax4.bar(range(len(transactions)), transactions, 
                          color=[self.colors['success'] if t > np.mean(transactions) else self.colors['warning'] 
                                for t in transactions], alpha=0.8)
            ax4.axhline(y=np.mean(transactions), color=self.colors['danger'], linestyle='--', linewidth=2)
            ax4.set_title('Transaction Pattern', fontsize=12, fontweight='bold')
            ax4.set_ylabel('Transactions')
            
            # 5. Growth indicators (middle right)
            ax5 = self.figure.add_subplot(gs[1, 2])
            ax5.axis('off')
            
            # Calculate growth metrics
            if len(revenues) > 1:
                daily_growth = [(revenues[i] - revenues[i-1]) / revenues[i-1] * 100 
                               if revenues[i-1] > 0 else 0 for i in range(1, len(revenues))]
                avg_growth = np.mean(daily_growth) if daily_growth else 0
                
                growth_text = f"""
                📈 Growth Metrics
                
                Daily Avg: {avg_growth:+.1f}%
                Best Growth: {max(daily_growth):+.1f}%
                Worst: {min(daily_growth):+.1f}%
                
                🎯 Trend: {'📈 Up' if avg_growth > 0 else '📉 Down' if avg_growth < 0 else '➡️ Stable'}
                """
                
                ax5.text(0.1, 0.9, growth_text, transform=ax5.transAxes, fontsize=10,
                        verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", 
                        facecolor=self.colors['light'], alpha=0.8))
            
            # 6. Summary statistics (bottom row)
            ax6 = self.figure.add_subplot(gs[2, :])
            ax6.axis('off')
            
            # Create summary dashboard
            total_revenue = sum(revenues)
            total_transactions = sum(transactions)
            avg_daily_revenue = np.mean(revenues)
            best_day = dates[revenues.index(max(revenues))]
            
            summary_boxes = [
                ('Total Revenue', f'${total_revenue:,.2f}', self.colors['primary']),
                ('Total Transactions', f'{total_transactions:,}', self.colors['secondary']),
                ('Daily Average', f'${avg_daily_revenue:,.2f}', self.colors['success']),
                ('Best Day', f'{best_day.strftime("%m/%d")}', self.colors['warning']),
                ('Days Analyzed', f'{len(dates)}', self.colors['info'])
            ]
            
            box_width = 0.18
            for i, (label, value, color) in enumerate(summary_boxes):
                x_pos = i * 0.2 + 0.1
                
                # Create colored box
                rect = Rectangle((x_pos - box_width/2, 0.4), box_width, 0.3, 
                               facecolor=color, alpha=0.1, edgecolor=color, linewidth=2)
                ax6.add_patch(rect)
                
                # Add text
                ax6.text(x_pos, 0.6, value, ha='center', va='center', 
                        fontsize=12, fontweight='bold', color=color)
                ax6.text(x_pos, 0.3, label, ha='center', va='center', 
                        fontsize=10, color=self.colors['dark'])
            
            ax6.set_xlim(0, 1)
            ax6.set_ylim(0, 1)
            
            self.figure.suptitle('Daily Performance Dashboard', fontsize=16, fontweight='bold', 
                               color=self.colors['dark'], y=0.98)
            
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting daily performance: {e}")
            self._show_error_chart(str(e))
    
    def _plot_top_medicines(self):
        """Plot top medicines analysis"""
        try:
            medicines_data = self.current_data.get('top_medicines', [])
            if not medicines_data:
                self._show_no_data_message()
                return
            
            self.figure.clear()
            
            # Create layout for medicines analysis
            gs = self.figure.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
            # Prepare data (top 10)
            top_medicines = medicines_data[:10]
            names = [med['name'] for med in top_medicines]
            revenues = [med['total_revenue'] for med in top_medicines]
            quantities = [med['total_quantity'] for med in top_medicines]
            transactions = [med['transactions'] for med in top_medicines]
            
            # 1. Revenue bar chart (top left)
            ax1 = self.figure.add_subplot(gs[0, 0])
            
            bars = ax1.barh(range(len(names)), revenues, 
                           color=self.gradient_colors[:len(names)], alpha=0.8)
            ax1.set_yticks(range(len(names)))
            ax1.set_yticklabels([name[:15] + '...' if len(name) > 15 else name for name in names])
            ax1.set_xlabel('Revenue ($)')
            ax1.set_title('Top Medicines by Revenue', fontsize=12, fontweight='bold')
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax1.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                        f'${width:,.0f}', ha='left', va='center', fontsize=9)
            
            ax1.grid(True, alpha=0.3, axis='x')
            
            # 2. Quantity vs Revenue scatter (top right)
            ax2 = self.figure.add_subplot(gs[0, 1])
            
            scatter = ax2.scatter(quantities, revenues, s=[t*10 for t in transactions], 
                                c=range(len(revenues)), cmap='viridis', alpha=0.7, 
                                edgecolors='white', linewidth=2)
            ax2.set_xlabel('Quantity Sold')
            ax2.set_ylabel('Revenue ($)')
            ax2.set_title('Quantity vs Revenue', fontsize=12, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            
            # Add trend line
            if len(quantities) > 1:
                z = np.polyfit(quantities, revenues, 1)
                p = np.poly1d(z)
                ax2.plot(quantities, p(quantities), '--', color=self.colors['danger'], linewidth=2)
            
            # 3. Medicine performance matrix (bottom left)
            ax3 = self.figure.add_subplot(gs[1, 0])
            
            # Create performance matrix
            performance_data = []
            for med in top_medicines[:5]:  # Top 5 for readability
                avg_per_transaction = med['total_revenue'] / med['transactions'] if med['transactions'] > 0 else 0
                performance_data.append([med['total_quantity'], med['total_revenue'], avg_per_transaction])
            
            if performance_data:
                performance_matrix = np.array(performance_data)
                # Normalize for heatmap
                normalized_matrix = (performance_matrix - performance_matrix.min(axis=0)) / \
                                  (performance_matrix.max(axis=0) - performance_matrix.min(axis=0) + 1e-8)
                
                im = ax3.imshow(normalized_matrix.T, cmap='RdYlGn', aspect='auto')
                ax3.set_xticks(range(len(names[:5])))
                ax3.set_xticklabels([name[:10] + '...' if len(name) > 10 else name for name in names[:5]], 
                                   rotation=45, ha='right')
                ax3.set_yticks(range(3))
                ax3.set_yticklabels(['Quantity', 'Revenue', 'Avg/Trans'])
                ax3.set_title('Performance Matrix', fontsize=12, fontweight='bold')
            
            # 4. Summary statistics (bottom right)
            ax4 = self.figure.add_subplot(gs[1, 1])
            ax4.axis('off')
            
            if medicines_data:
                total_med_revenue = sum(med['total_revenue'] for med in medicines_data)
                total_med_quantity = sum(med['total_quantity'] for med in medicines_data)
                avg_price = total_med_revenue / total_med_quantity if total_med_quantity > 0 else 0
                
                top_medicine = medicines_data[0]
                
                summary_text = f"""
                💊 Medicine Analytics
                
                🏆 Top Seller: {top_medicine['name'][:20]}
                💰 Revenue: ${top_medicine['total_revenue']:,.2f}
                📦 Quantity: {top_medicine['total_quantity']:,}
                
                📊 Overall Stats:
                Total Revenue: ${total_med_revenue:,.2f}
                Total Quantity: {total_med_quantity:,}
                Avg Price: ${avg_price:.2f}
                
                📈 Medicines Analyzed: {len(medicines_data)}
                """
                
                ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=10,
                        verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", 
                        facecolor=self.colors['light'], alpha=0.8))
            
            self.figure.suptitle('Top Medicines Analysis', fontsize=16, fontweight='bold', 
                               color=self.colors['dark'], y=0.95)
            
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting top medicines: {e}")
            self._show_error_chart(str(e))
    
    def _show_error_chart(self, error_message: str):
        """Show error message in chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, f'❌ Chart Error\n\n{error_message}', 
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=14, color=self.colors['danger'],
               bbox=dict(boxstyle="round,pad=0.5", facecolor='#FADBD8', alpha=0.8))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.canvas.draw()
    
    def set_chart_title(self, title: str):
        """Set the main chart title"""
        self.chart_title.setText(title)
    
    def get_current_chart_type(self) -> str:
        """Get the currently selected chart type"""
        return self.chart_type_combo.currentData() or "trend"
    
    # Inventory Chart Methods
    
    def _plot_inventory_overview(self):
        """Plot comprehensive inventory overview dashboard"""
        try:
            summary = self.current_data.get('inventory_summary', {})
            if not summary:
                self._show_no_data_message()
                return
            
            self.figure.clear()
            
            # Create 2x2 layout for overview
            gs = self.figure.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
            # 1. Key Metrics (top left)
            ax1 = self.figure.add_subplot(gs[0, 0])
            ax1.axis('off')
            
            metrics_text = f"""
            📦 Inventory Overview
            
            💊 Total Medicines: {summary.get('total_medicines', 0):,}
            💰 Stock Value: ${summary.get('total_stock_value', 0):,.2f}
            💵 Selling Value: ${summary.get('total_selling_value', 0):,.2f}
            📈 Potential Profit: ${summary.get('potential_profit', 0):,.2f}
            
            ⚠️ Low Stock: {summary.get('low_stock_count', 0)}
            ⏰ Expired: {summary.get('expired_count', 0)}
            """
            
            ax1.text(0.05, 0.95, metrics_text, transform=ax1.transAxes, fontsize=12,
                    verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", 
                    facecolor=self.colors['light'], alpha=0.8))
            
            # 2. Stock Status Pie Chart (top right)
            ax2 = self.figure.add_subplot(gs[0, 1])
            
            total_medicines = summary.get('total_medicines', 0)
            low_stock = summary.get('low_stock_count', 0)
            expired = summary.get('expired_count', 0)
            good_stock = total_medicines - low_stock - expired
            
            if total_medicines > 0:
                sizes = [good_stock, low_stock, expired]
                labels = ['Good Stock', 'Low Stock', 'Expired']
                colors = [self.colors['success'], self.colors['warning'], self.colors['danger']]
                
                # Filter out zero values
                filtered_data = [(size, label, color) for size, label, color in zip(sizes, labels, colors) if size > 0]
                if filtered_data:
                    sizes, labels, colors = zip(*filtered_data)
                    
                    wedges, texts, autotexts = ax2.pie(sizes, labels=labels, autopct='%1.1f%%',
                                                      colors=colors, startangle=90)
                    
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
            
            ax2.set_title('Stock Status Distribution', fontsize=12, fontweight='bold')
            
            # 3. Value Analysis (bottom left)
            ax3 = self.figure.add_subplot(gs[1, 0])
            
            stock_value = summary.get('total_stock_value', 0)
            selling_value = summary.get('total_selling_value', 0)
            profit = summary.get('potential_profit', 0)
            
            categories = ['Stock Value', 'Selling Value', 'Potential Profit']
            values = [stock_value, selling_value, profit]
            colors = [self.colors['primary'], self.colors['secondary'], self.colors['success']]
            
            bars = ax3.bar(categories, values, color=colors, alpha=0.8)
            ax3.set_title('Value Analysis', fontsize=12, fontweight='bold')
            ax3.set_ylabel('Amount ($)')
            
            # Add value labels
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'${value:,.0f}', ha='center', va='bottom', fontsize=10)
            
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # 4. Alert Summary (bottom right)
            ax4 = self.figure.add_subplot(gs[1, 1])
            ax4.axis('off')
            
            alert_text = "🚨 Alerts & Actions\n\n"
            
            if low_stock > 0:
                alert_text += f"⚠️ {low_stock} medicines need restocking\n\n"
            
            if expired > 0:
                alert_text += f"⏰ {expired} medicines are expired\n\n"
            
            if low_stock == 0 and expired == 0:
                alert_text += "✅ All inventory is in good condition!\n\n"
            
            # Calculate profit margin
            profit_margin = (profit / stock_value * 100) if stock_value > 0 else 0
            alert_text += f"📊 Profit Margin: {profit_margin:.1f}%"
            
            ax4.text(0.05, 0.95, alert_text, transform=ax4.transAxes, fontsize=11,
                    verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", 
                    facecolor='#FFF3CD' if (low_stock > 0 or expired > 0) else '#D4EDDA', 
                    alpha=0.8))
            
            self.figure.suptitle('Inventory Overview Dashboard', fontsize=16, fontweight='bold', 
                               color=self.colors['dark'], y=0.95)
            
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting inventory overview: {e}")
            self._show_error_chart(str(e))
    
    def _plot_stock_status(self):
        """Plot detailed stock status analysis"""
        try:
            low_stock = self.current_data.get('low_stock_medicines', [])
            expired = self.current_data.get('expired_medicines', [])
            summary = self.current_data.get('inventory_summary', {})
            
            self.figure.clear()
            
            if not low_stock and not expired:
                # Show good status
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, '✅ All Stock in Good Condition!\n\nNo low stock or expired items found.', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=18, color=self.colors['success'],
                       bbox=dict(boxstyle="round,pad=0.5", facecolor='#D4EDDA', alpha=0.8))
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                self.canvas.draw()
                return
            
            # Create layout for stock issues
            gs = self.figure.add_gridspec(2, 2, hspace=0.4, wspace=0.3)
            
            # 1. Low Stock Items (top left)
            ax1 = self.figure.add_subplot(gs[0, 0])
            
            if low_stock:
                names = [item['name'][:15] + '...' if len(item['name']) > 15 else item['name'] for item in low_stock[:10]]
                quantities = [item['quantity'] for item in low_stock[:10]]
                
                bars = ax1.barh(range(len(names)), quantities, color=self.colors['warning'], alpha=0.8)
                ax1.set_yticks(range(len(names)))
                ax1.set_yticklabels(names)
                ax1.set_xlabel('Quantity')
                ax1.set_title(f'Low Stock Items ({len(low_stock)})', fontsize=12, fontweight='bold')
                
                # Add quantity labels
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    ax1.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                            f'{width}', ha='left', va='center', fontsize=9)
            else:
                ax1.text(0.5, 0.5, 'No Low Stock Items', ha='center', va='center', 
                        transform=ax1.transAxes, fontsize=12, color=self.colors['success'])
                ax1.set_title('Low Stock Items', fontsize=12, fontweight='bold')
            
            ax1.grid(True, alpha=0.3, axis='x')
            
            # 2. Expired Items (top right)
            ax2 = self.figure.add_subplot(gs[0, 1])
            
            if expired:
                exp_names = [item['name'][:15] + '...' if len(item['name']) > 15 else item['name'] for item in expired[:10]]
                exp_quantities = [item['quantity'] for item in expired[:10]]
                
                bars = ax2.barh(range(len(exp_names)), exp_quantities, color=self.colors['danger'], alpha=0.8)
                ax2.set_yticks(range(len(exp_names)))
                ax2.set_yticklabels(exp_names)
                ax2.set_xlabel('Quantity')
                ax2.set_title(f'Expired Items ({len(expired)})', fontsize=12, fontweight='bold')
                
                # Add quantity labels
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    ax2.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                            f'{width}', ha='left', va='center', fontsize=9)
            else:
                ax2.text(0.5, 0.5, 'No Expired Items', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=12, color=self.colors['success'])
                ax2.set_title('Expired Items', fontsize=12, fontweight='bold')
            
            ax2.grid(True, alpha=0.3, axis='x')
            
            # 3. Action Priority Matrix (bottom)
            ax3 = self.figure.add_subplot(gs[1, :])
            ax3.axis('off')
            
            action_text = "🎯 Recommended Actions\n\n"
            
            if low_stock:
                action_text += f"📋 RESTOCK PRIORITY:\n"
                for i, item in enumerate(low_stock[:5]):
                    action_text += f"   {i+1}. {item['name']} (Qty: {item['quantity']}, Batch: {item['batch_no']})\n"
                if len(low_stock) > 5:
                    action_text += f"   ... and {len(low_stock) - 5} more items\n"
                action_text += "\n"
            
            if expired:
                action_text += f"🗑️ DISPOSAL REQUIRED:\n"
                for i, item in enumerate(expired[:5]):
                    action_text += f"   {i+1}. {item['name']} (Expired: {item['expiry_date']}, Qty: {item['quantity']})\n"
                if len(expired) > 5:
                    action_text += f"   ... and {len(expired) - 5} more items\n"
            
            ax3.text(0.05, 0.95, action_text, transform=ax3.transAxes, fontsize=10,
                    verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", 
                    facecolor='#FFF3CD', alpha=0.8))
            
            self.figure.suptitle('Stock Status Analysis', fontsize=16, fontweight='bold', 
                               color=self.colors['dark'], y=0.95)
            
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting stock status: {e}")
            self._show_error_chart(str(e))
    
    def _plot_category_analysis(self):
        """Plot category-wise inventory analysis"""
        try:
            categories = self.current_data.get('category_breakdown', [])
            if not categories:
                self._show_no_data_message()
                return
            
            self.figure.clear()
            
            # Create 2x2 layout
            gs = self.figure.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
            # Prepare data
            cat_names = [cat['category'] for cat in categories]
            cat_counts = [cat['count'] for cat in categories]
            cat_quantities = [cat['total_quantity'] for cat in categories]
            cat_values = [cat['stock_value'] for cat in categories]
            
            # 1. Medicine Count by Category (top left)
            ax1 = self.figure.add_subplot(gs[0, 0])
            
            bars1 = ax1.bar(range(len(cat_names)), cat_counts, 
                           color=self.gradient_colors[:len(cat_names)], alpha=0.8)
            ax1.set_xticks(range(len(cat_names)))
            ax1.set_xticklabels([name[:10] + '...' if len(name) > 10 else name for name in cat_names], 
                               rotation=45, ha='right')
            ax1.set_ylabel('Medicine Count')
            ax1.set_title('Medicines by Category', fontsize=12, fontweight='bold')
            
            # Add value labels
            for bar, value in zip(bars1, cat_counts):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value}', ha='center', va='bottom', fontsize=9)
            
            # 2. Stock Value by Category (top right)
            ax2 = self.figure.add_subplot(gs[0, 1])
            
            wedges, texts, autotexts = ax2.pie(cat_values, labels=cat_names, autopct='%1.1f%%',
                                              colors=self.gradient_colors[:len(cat_names)], startangle=90)
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            ax2.set_title('Stock Value Distribution', fontsize=12, fontweight='bold')
            
            # 3. Quantity vs Value Scatter (bottom left)
            ax3 = self.figure.add_subplot(gs[1, 0])
            
            scatter = ax3.scatter(cat_quantities, cat_values, s=100, 
                                c=range(len(categories)), cmap='viridis', alpha=0.7,
                                edgecolors='white', linewidth=2)
            
            ax3.set_xlabel('Total Quantity')
            ax3.set_ylabel('Stock Value ($)')
            ax3.set_title('Quantity vs Value', fontsize=12, fontweight='bold')
            ax3.grid(True, alpha=0.3)
            
            # Add category labels
            for i, (qty, val, name) in enumerate(zip(cat_quantities, cat_values, cat_names)):
                ax3.annotate(name[:8], (qty, val), xytext=(5, 5), 
                           textcoords='offset points', fontsize=8)
            
            # 4. Category Summary (bottom right)
            ax4 = self.figure.add_subplot(gs[1, 1])
            ax4.axis('off')
            
            total_medicines = sum(cat_counts)
            total_quantity = sum(cat_quantities)
            total_value = sum(cat_values)
            
            summary_text = f"""
            📊 Category Summary
            
            📦 Total Categories: {len(categories)}
            💊 Total Medicines: {total_medicines:,}
            📦 Total Quantity: {total_quantity:,}
            💰 Total Value: ${total_value:,.2f}
            
            🏆 Top Category: {cat_names[cat_values.index(max(cat_values))]}
            💰 Highest Value: ${max(cat_values):,.2f}
            📦 Most Medicines: {cat_names[cat_counts.index(max(cat_counts))]}
            """
            
            ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=10,
                    verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", 
                    facecolor=self.colors['light'], alpha=0.8))
            
            self.figure.suptitle('Category Analysis', fontsize=16, fontweight='bold', 
                               color=self.colors['dark'], y=0.95)
            
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting category analysis: {e}")
            self._show_error_chart(str(e))
    
    def _plot_stock_value_distribution(self):
        """Plot stock value distribution analysis"""
        try:
            categories = self.current_data.get('category_breakdown', [])
            summary = self.current_data.get('inventory_summary', {})
            
            if not categories:
                self._show_no_data_message()
                return
            
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # Prepare data
            cat_names = [cat['category'] for cat in categories]
            cat_values = [cat['stock_value'] for cat in categories]
            
            # Create horizontal bar chart
            bars = ax.barh(range(len(cat_names)), cat_values, 
                          color=self.gradient_colors[:len(cat_names)], alpha=0.8)
            
            ax.set_yticks(range(len(cat_names)))
            ax.set_yticklabels(cat_names)
            ax.set_xlabel('Stock Value ($)')
            ax.set_title('Stock Value Distribution by Category', fontsize=14, fontweight='bold', pad=20)
            
            # Add value labels and percentages
            total_value = sum(cat_values)
            for i, bar in enumerate(bars):
                width = bar.get_width()
                percentage = (width / total_value * 100) if total_value > 0 else 0
                ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                       f'${width:,.0f} ({percentage:.1f}%)', 
                       ha='left', va='center', fontsize=10, fontweight='bold')
            
            # Add average line
            avg_value = total_value / len(cat_values) if cat_values else 0
            ax.axvline(x=avg_value, color=self.colors['danger'], linestyle='--', 
                      linewidth=2, label=f'Average: ${avg_value:,.0f}')
            
            ax.legend(loc='lower right')
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add summary text
            summary_text = f"Total Stock Value: ${total_value:,.2f} | Average per Category: ${avg_value:,.2f}"
            ax.text(0.5, -0.1, summary_text, transform=ax.transAxes, ha='center', 
                   fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['light'], alpha=0.8))
            
            self.figure.tight_layout(pad=2.0)
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting stock value distribution: {e}")
            self._show_error_chart(str(e))
    
    def _plot_low_stock_alert(self):
        """Plot low stock alert dashboard"""
        try:
            low_stock = self.current_data.get('low_stock_medicines', [])
            
            if not low_stock:
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, '✅ No Low Stock Items!\n\nAll medicines are adequately stocked.', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=18, color=self.colors['success'],
                       bbox=dict(boxstyle="round,pad=0.5", facecolor='#D4EDDA', alpha=0.8))
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                self.canvas.draw()
                return
            
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # Prepare data (top 15 for readability)
            items = low_stock[:15]
            names = [item['name'][:20] + '...' if len(item['name']) > 20 else item['name'] for item in items]
            quantities = [item['quantity'] for item in items]
            
            # Create color coding based on urgency (lower quantity = more urgent)
            max_qty = max(quantities) if quantities else 1
            colors = [self.colors['danger'] if qty <= max_qty * 0.3 else 
                     self.colors['warning'] if qty <= max_qty * 0.6 else 
                     self.colors['accent'] for qty in quantities]
            
            # Create horizontal bar chart
            bars = ax.barh(range(len(names)), quantities, color=colors, alpha=0.8)
            
            ax.set_yticks(range(len(names)))
            ax.set_yticklabels(names)
            ax.set_xlabel('Current Stock Quantity')
            ax.set_title(f'Low Stock Alert - {len(low_stock)} Items Need Attention', 
                        fontsize=14, fontweight='bold', pad=20)
            
            # Add quantity labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                urgency = "URGENT" if width <= max_qty * 0.3 else "MEDIUM" if width <= max_qty * 0.6 else "LOW"
                ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                       f'{width} ({urgency})', ha='left', va='center', fontsize=9, fontweight='bold')
            
            # Add legend
            legend_elements = [
                mpatches.Patch(color=self.colors['danger'], label='Urgent (≤30% of max)'),
                mpatches.Patch(color=self.colors['warning'], label='Medium (≤60% of max)'),
                mpatches.Patch(color=self.colors['accent'], label='Low Priority')
            ]
            ax.legend(handles=legend_elements, loc='lower right')
            
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add summary
            urgent_count = sum(1 for qty in quantities if qty <= max_qty * 0.3)
            medium_count = sum(1 for qty in quantities if max_qty * 0.3 < qty <= max_qty * 0.6)
            
            summary_text = f"🚨 {urgent_count} Urgent | ⚠️ {medium_count} Medium Priority | Total: {len(low_stock)} Items"
            ax.text(0.5, -0.15, summary_text, transform=ax.transAxes, ha='center', 
                   fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFF3CD', alpha=0.8))
            
            self.figure.tight_layout(pad=2.0)
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting low stock alert: {e}")
            self._show_error_chart(str(e))
    
    def _plot_expiry_analysis(self):
        """Plot expiry analysis dashboard"""
        try:
            expired = self.current_data.get('expired_medicines', [])
            
            if not expired:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, '✅ No Expired Items!\n\nAll medicines are within their expiry dates.', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=18, color=self.colors['success'],
                       bbox=dict(boxstyle="round,pad=0.5", facecolor='#D4EDDA', alpha=0.8))
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                self.canvas.draw()
                return
            
            self.figure.clear()
            
            # Create layout
            gs = self.figure.add_gridspec(2, 2, hspace=0.4, wspace=0.3)
            
            # 1. Expired Items List (top)
            ax1 = self.figure.add_subplot(gs[0, :])
            
            # Show top 10 expired items
            items = expired[:10]
            names = [item['name'][:25] + '...' if len(item['name']) > 25 else item['name'] for item in items]
            quantities = [item['quantity'] for item in items]
            
            bars = ax1.barh(range(len(names)), quantities, color=self.colors['danger'], alpha=0.8)
            ax1.set_yticks(range(len(names)))
            ax1.set_yticklabels(names)
            ax1.set_xlabel('Quantity')
            ax1.set_title(f'Expired Items - {len(expired)} Total', fontsize=14, fontweight='bold')
            
            # Add expiry dates as labels
            for i, (bar, item) in enumerate(zip(bars, items)):
                width = bar.get_width()
                ax1.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                        f'{width} (Exp: {item["expiry_date"]})', 
                        ha='left', va='center', fontsize=9)
            
            ax1.grid(True, alpha=0.3, axis='x')
            
            # 2. Category Breakdown (bottom left)
            ax2 = self.figure.add_subplot(gs[1, 0])
            
            # Group by category
            category_counts = {}
            for item in expired:
                cat = item['category']
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            if category_counts:
                cats = list(category_counts.keys())
                counts = list(category_counts.values())
                
                wedges, texts, autotexts = ax2.pie(counts, labels=cats, autopct='%1.0f',
                                                  colors=self.gradient_colors[:len(cats)], startangle=90)
                
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
            
            ax2.set_title('Expired by Category', fontsize=12, fontweight='bold')
            
            # 3. Action Summary (bottom right)
            ax3 = self.figure.add_subplot(gs[1, 1])
            ax3.axis('off')
            
            total_expired_qty = sum(item['quantity'] for item in expired)
            
            action_text = f"""
            🗑️ Disposal Required
            
            📦 Total Items: {len(expired)}
            📊 Total Quantity: {total_expired_qty:,}
            
            🏷️ Categories Affected: {len(category_counts)}
            
            ⚠️ IMMEDIATE ACTION:
            Remove all expired items
            from inventory to prevent
            accidental dispensing.
            
            📋 Update inventory records
            after disposal.
            """
            
            ax3.text(0.05, 0.95, action_text, transform=ax3.transAxes, fontsize=10,
                    verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", 
                    facecolor='#F8D7DA', alpha=0.8))
            
            self.figure.suptitle('Expiry Analysis', fontsize=16, fontweight='bold', 
                               color=self.colors['dark'], y=0.95)
            
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error plotting expiry analysis: {e}")
            self._show_error_chart(str(e))