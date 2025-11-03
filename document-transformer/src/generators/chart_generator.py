"""
Chart and Data Visualization Generator for Documents
Creates professional charts and graphs for financial data and business metrics
"""

import io
import base64
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import logging

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("Matplotlib not available - chart generation disabled")

from ..parser import FinancialData
from ..branding import BrandProfile, ColorPalette

@dataclass
class ChartConfig:
    """Configuration for chart generation"""
    chart_type: str = "bar"  # bar, line, pie, area
    width: int = 800
    height: int = 400
    dpi: int = 300
    style: str = "professional"
    show_grid: bool = True
    show_legend: bool = True
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None

class ChartGenerator:
    """Generates professional charts for financial data and business metrics"""

    def __init__(self, brand_profile: BrandProfile):
        self.brand_profile = brand_profile
        self.logger = logging.getLogger(__name__)

        # Setup matplotlib style if available
        if MATPLOTLIB_AVAILABLE:
            self._setup_matplotlib_style()

    def _setup_matplotlib_style(self):
        """Setup matplotlib with brand-specific styling"""

        # Brand colors
        colors = self.brand_profile.color_palette
        self.primary_colors = colors.primary or ['#1976D2', '#2196F3', '#64B5F6']
        self.secondary_colors = colors.secondary or ['#424242', '#616161', '#757575']
        self.accent_color = colors.accent or '#2196F3'

        # Set style
        plt.style.use('default')

        # Configure font
        font_family = self.brand_profile.typography.body_font or 'Inter'
        plt.rcParams['font.family'] = font_family
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['legend.fontsize'] = 10

        # Configure grid
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3

    def generate_financial_chart(self, financial_data: FinancialData,
                                config: Optional[ChartConfig] = None) -> str:
        """Generate a chart from financial table data"""

        if not MATPLOTLIB_AVAILABLE:
            return self._generate_fallback_chart(financial_data, config)

        if config is None:
            config = ChartConfig()

        try:
            # Parse financial data
            parsed_data = self._parse_financial_table(financial_data.table_data)

            if not parsed_data:
                return self._generate_fallback_chart(financial_data, config)

            # Create figure
            fig, ax = plt.subplots(figsize=(config.width/100, config.height/100),
                               dpi=config.dpi)

            # Generate chart based on data type
            if self._is_revenue_data(parsed_data):
                self._create_revenue_chart(ax, parsed_data, config)
            elif self._is_growth_data(parsed_data):
                self._create_growth_chart(ax, parsed_data, config)
            elif self._is_comparison_data(parsed_data):
                self._create_comparison_chart(ax, parsed_data, config)
            else:
                self._create_generic_chart(ax, parsed_data, config)

            # Apply styling
            self._apply_chart_styling(ax, config)

            # Convert to base64 string
            image_base64 = self._fig_to_base64(fig)
            plt.close(fig)

            return image_base64

        except Exception as e:
            self.logger.error(f"Error generating chart: {e}")
            return self._generate_fallback_chart(financial_data, config)

    def _parse_financial_table(self, table_data: List[List[str]]) -> Dict[str, Any]:
        """Parse financial table data into structured format"""

        if not table_data or len(table_data) < 2:
            return {}

        headers = table_data[0]
        rows = table_data[1:]

        # Try to identify column types
        parsed = {
            'headers': headers,
            'rows': rows,
            'data_columns': [],
            'label_column': None
        }

        # Find label column (usually first column with text)
        for i, header in enumerate(headers):
            if self._is_text_column(rows, i):
                parsed['label_column'] = i
                break

        # Find data columns (numeric columns)
        for i, header in enumerate(headers):
            if i != parsed['label_column'] and self._is_numeric_column(rows, i):
                parsed['data_columns'].append(i)

        return parsed

    def _is_text_column(self, rows: List[List[str]], col_index: int) -> bool:
        """Check if column contains text data"""
        if col_index >= len(rows[0]):
            return False

        non_numeric_count = 0
        for row in rows[:5]:  # Check first 5 rows
            if col_index < len(row):
                try:
                    float(row[col_index].replace(',', '').replace('$', ''))
                except:
                    non_numeric_count += 1

        return non_numeric_count > len(rows[:5]) * 0.7

    def _is_numeric_column(self, rows: List[List[str]], col_index: int) -> bool:
        """Check if column contains numeric data"""
        if col_index >= len(rows[0]):
            return False

        numeric_count = 0
        for row in rows[:5]:  # Check first 5 rows
            if col_index < len(row):
                try:
                    value = row[col_index].replace(',', '').replace('$', '').replace('%', '')
                    float(value)
                    numeric_count += 1
                except:
                    continue

        return numeric_count > len(rows[:5]) * 0.5

    def _is_revenue_data(self, parsed_data: Dict) -> bool:
        """Check if data represents revenue/financial metrics"""
        headers = [h.lower() for h in parsed_data.get('headers', [])]
        revenue_keywords = ['revenue', 'sales', 'income', 'earnings', 'turnover']
        return any(keyword in ' '.join(headers) for keyword in revenue_keywords)

    def _is_growth_data(self, parsed_data: Dict) -> bool:
        """Check if data represents growth metrics"""
        headers = [h.lower() for h in parsed_data.get('headers', [])]
        growth_keywords = ['growth', 'cagr', 'increase', 'change', 'variance']
        return any(keyword in ' '.join(headers) for keyword in growth_keywords)

    def _is_comparison_data(self, parsed_data: Dict) -> bool:
        """Check if data represents comparison between items"""
        return len(parsed_data.get('data_columns', [])) >= 2

    def _create_revenue_chart(self, ax, parsed_data: Dict, config: ChartConfig):
        """Create revenue/financial chart"""

        labels = []
        values = []

        for row in parsed_data['rows']:
            if parsed_data['label_column'] is not None and len(parsed_data['data_columns']) > 0:
                label = row[parsed_data['label_column']]
                try:
                    value = float(row[parsed_data['data_columns'][0]].replace(',', '').replace('$', ''))
                    labels.append(label)
                    values.append(value)
                except:
                    continue

        if labels and values:
            bars = ax.bar(labels, values, color=self.primary_colors[0], alpha=0.8)

            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'${value:,.0f}', ha='center', va='bottom', fontsize=9)

    def _create_growth_chart(self, ax, parsed_data: Dict, config: ChartConfig):
        """Create growth chart (line chart)"""

        labels = []
        values = []

        for row in parsed_data['rows']:
            if parsed_data['label_column'] is not None and len(parsed_data['data_columns']) > 0:
                label = row[parsed_data['label_column']]
                try:
                    value = float(row[parsed_data['data_columns'][0]].replace('%', ''))
                    labels.append(label)
                    values.append(value)
                except:
                    continue

        if labels and values:
            line = ax.plot(labels, values, color=self.primary_colors[0],
                          marker='o', linewidth=2, markersize=6)

            # Add value labels
            for i, (label, value) in enumerate(zip(labels, values)):
                ax.annotate(f'{value}%', (i, value), textcoords="offset points",
                           xytext=(0,10), ha='center', fontsize=9)

    def _create_comparison_chart(self, ax, parsed_data: Dict, config: ChartConfig):
        """Create comparison chart with multiple data series"""

        labels = []
        data_series = [[] for _ in parsed_data['data_columns']]

        for row in parsed_data['rows']:
            if parsed_data['label_column'] is not None:
                label = row[parsed_data['label_column']]
                labels.append(label)

                for i, col_idx in enumerate(parsed_data['data_columns']):
                    try:
                        value = float(row[col_idx].replace(',', '').replace('$', '').replace('%', ''))
                        data_series[i].append(value)
                    except:
                        data_series[i].append(0)

        # Create grouped bar chart
        x = np.arange(len(labels))
        width = 0.8 / len(data_series)

        for i, (series, header) in enumerate(zip(data_series,
                                                [parsed_data['headers'][j] for j in parsed_data['data_columns']])):
            ax.bar(x + i * width, series, width, label=header,
                  color=self.primary_colors[i % len(self.primary_colors)], alpha=0.8)

        ax.set_xticks(x + width * (len(data_series) - 1) / 2)
        ax.set_xticklabels(labels, rotation=45, ha='right')

    def _create_generic_chart(self, ax, parsed_data: Dict, config: ChartConfig):
        """Create a generic chart for any financial data"""
        self._create_comparison_chart(ax, parsed_data, config)

    def _apply_chart_styling(self, ax, config: ChartConfig):
        """Apply professional styling to chart"""

        # Set title
        if config.title:
            ax.set_title(config.title, fontweight='bold', color=self.accent_color)

        # Set labels
        if config.x_label:
            ax.set_xlabel(config.x_label)
        if config.y_label:
            ax.set_ylabel(config.y_label)

        # Apply brand colors
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.secondary_colors[0])
        ax.spines['bottom'].set_color(self.secondary_colors[0])

        # Grid styling
        if config.show_grid:
            ax.grid(True, alpha=0.3, linestyle='--')

        # Legend
        if config.show_legend and ax.get_legend():
            ax.legend(frameon=False, bbox_to_anchor=(1.05, 1), loc='upper left')

    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""

        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)

        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()

        return image_base64

    def _generate_fallback_chart(self, financial_data: FinancialData,
                                config: Optional[ChartConfig] = None) -> str:
        """Generate fallback chart representation when matplotlib is not available"""

        # Create simple text-based chart representation
        chart_text = f"📊 {financial_data.title or 'Financial Data'}\n\n"

        if financial_data.table_data and len(financial_data.table_data) > 1:
            # Create simple ASCII chart
            rows = financial_data.table_data[1:6]  # Show first 5 data rows

            for row in rows:
                if len(row) > 1:
                    label = row[0]
                    try:
                        # Try to extract numeric value from second column
                        value_str = row[1].replace(',', '').replace('$', '').replace('%', '')
                        value = float(value_str)

                        # Create simple bar visualization
                        bar_length = min(50, int(value / 1000000))  # Scale to millions
                        bar = '█' * bar_length
                        chart_text += f"{label:20} {bar} ${value:,.0f}\n"
                    except:
                        chart_text += f"{label:20} {row[1]}\n"

        # Convert to base64 for consistency
        fallback_html = f'''
        <div class="chart-fallback" style="padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h4>{financial_data.title or 'Financial Data Chart'}</h4>
            <pre style="font-family: monospace; white-space: pre-wrap;">{chart_text}</pre>
            <p style="font-size: 12px; color: #666; margin-top: 10px;">
                *Install matplotlib for enhanced chart visualization: pip install matplotlib
            </p>
        </div>
        '''

        return fallback_html

    def generate_dashboard_charts(self, financial_data_list: List[FinancialData]) -> List[str]:
        """Generate multiple charts for a dashboard view"""

        charts = []

        for i, financial_data in enumerate(financial_data_list[:4]):  # Max 4 charts
            config = ChartConfig(
                title=financial_data.title or f"Financial Chart {i+1}",
                chart_type="auto"  # Auto-detect best chart type
            )

            chart = self.generate_financial_chart(financial_data, config)
            charts.append(chart)

        return charts

    def create_sparkline(self, values: List[float], width: int = 100, height: int = 30) -> str:
        """Create small sparkline chart for inline display"""

        if not MATPLOTLIB_AVAILABLE or not values:
            return ""

        try:
            fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=150)

            # Remove all axes for clean sparkline
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

            # Plot sparkline
            ax.plot(values, color=self.accent_color, linewidth=2)

            # Add dot at end
            ax.plot(len(values)-1, values[-1], 'o', color=self.accent_color, markersize=4)

            # Convert to base64
            image_base64 = self._fig_to_base64(fig)
            plt.close(fig)

            return image_base64

        except Exception as e:
            self.logger.error(f"Error creating sparkline: {e}")
            return ""

    def get_chart_summary_stats(self, financial_data: FinancialData) -> Dict[str, float]:
        """Calculate summary statistics for financial data"""

        stats = {}

        if not financial_data.table_data or len(financial_data.table_data) < 2:
            return stats

        # Extract numeric values
        values = []
        for row in financial_data.table_data[1:]:
            if len(row) > 1:
                try:
                    value = float(row[1].replace(',', '').replace('$', '').replace('%', ''))
                    values.append(value)
                except:
                    continue

        if values:
            stats['min'] = min(values)
            stats['max'] = max(values)
            stats['avg'] = sum(values) / len(values)
            stats['total'] = sum(values)

            # Calculate growth if multiple values
            if len(values) > 1:
                stats['growth'] = ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0

        return stats