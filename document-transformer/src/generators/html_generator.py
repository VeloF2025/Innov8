"""
HTML Generator for Document Transformation
Converts parsed documents to responsive HTML with CSS styling
"""

import re
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import asdict
import mimetypes

from ..parser import ParsedDocument, ContentSection, FinancialData, TeamMember
from ..branding import BrandProfile, ColorPalette, Typography
from ..templates import TemplateEngine, TemplateConfig
from .chart_generator import ChartGenerator

class HTMLGenerator:
    """Generates responsive HTML documents from parsed markdown"""

    def __init__(self, template_engine: TemplateEngine, output_dir: Path):
        self.template_engine = template_engine
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_html(self, document: ParsedDocument, brand_profile: BrandProfile,
                     template_config: Optional[TemplateConfig] = None,
                     output_filename: Optional[str] = None) -> str:
        """Generate HTML document"""

        # Select template if not provided
        if template_config is None:
            template_config = self.template_engine.get_template_for_document(document, brand_profile)

        # Generate filename if not provided
        if output_filename is None:
            output_filename = self._generate_filename(document)

        # Render document
        html_content = self._render_document(document, brand_profile, template_config)

        # Process embedded content
        html_content = self._process_embedded_content(html_content, document, brand_profile)

        # Add responsive enhancements
        html_content = self._add_responsive_enhancements(html_content)

        # Add SEO and metadata
        html_content = self._add_seo_metadata(html_content, document, brand_profile)

        # Write HTML file
        output_path = self.output_dir / output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_path)

    def _render_document(self, document: ParsedDocument, brand_profile: BrandProfile,
                        template_config: TemplateConfig) -> str:
        """Render document using template engine"""

        return self.template_engine.render_document(document, brand_profile, template_config)

    def _process_embedded_content(self, html_content: str, document: ParsedDocument,
                                brand_profile: BrandProfile) -> str:
        """Process embedded images, links, and other content"""

        # Process images
        html_content = self._process_images(html_content, document)

        # Process links
        html_content = self._process_links(html_content, document)

        # Process financial data visualization
        html_content = self._process_financial_data(html_content, document, brand_profile)

        # Process team member sections
        html_content = self._process_team_sections(html_content, document)

        # Add custom CSS from brand profile
        html_content = self._inject_custom_css(html_content, brand_profile)

        return html_content

    def _process_images(self, html_content: str, document: ParsedDocument) -> str:
        """Process and optimize images in the HTML"""

        if not document.images:
            return html_content

        # Add image styling classes
        html_content = html_content.replace('<img', '<img class="document-image" loading="lazy"')

        # Wrap images in figure elements with captions
        for i, img_src in enumerate(document.images):
            img_tag = f'src="{img_src}"'
            if img_tag in html_content:
                # Create figure with caption
                figure_html = f'''<figure class="document-figure">
                    <img src="{img_src}" alt="Document image {i+1}" class="document-image" loading="lazy">
                    <figcaption>Image {i+1}</figcaption>
                </figure>'''
                html_content = html_content.replace(f'<img {img_tag}', figure_html)

        return html_content

    def _process_links(self, html_content: str, document: ParsedDocument) -> str:
        """Process external links with proper attributes"""

        if not document.links:
            return html_content

        for link in document.links:
            # Add external link attributes
            if link in html_content:
                html_content = html_content.replace(
                    f'href="{link}"',
                    f'href="{link}" target="_blank" rel="noopener noreferrer" class="external-link"'
                )

        return html_content

    def _process_financial_data(self, html_content: str, document: ParsedDocument, brand_profile: BrandProfile) -> str:
        """Enhance financial data with charts and visualizations"""

        if not document.financial_data:
            return html_content

        # Initialize chart generator
        chart_generator = ChartGenerator(brand_profile)

        # Generate charts for each financial table
        for i, financial in enumerate(document.financial_data):
            chart_html = self._generate_enhanced_chart_html(financial, chart_generator, i)

            # Insert chart after financial table
            table_pattern = f'<h3>{financial.title}</h3>'
            if table_pattern in html_content:
                html_content = html_content.replace(
                    table_pattern,
                    table_pattern + chart_html
                )

        # Add summary statistics
        summary_html = self._generate_financial_summary(document.financial_data, chart_generator)
        html_content = html_content.replace(
            '</div>\n</div>\n</body>',
            f'{summary_html}\n</div>\n</div>\n</body>'
        )

        return html_content

    def _generate_enhanced_chart_html(self, financial: FinancialData, chart_generator: ChartGenerator, index: int) -> str:
        """Generate enhanced HTML chart with visualization"""

        # Generate chart
        chart_data = chart_generator.generate_financial_chart(financial)

        # Generate statistics
        stats = chart_generator.get_chart_summary_stats(financial)

        # Build HTML
        if chart_data.startswith('<div'):  # Fallback HTML
            chart_html = chart_data
        else:  # Base64 encoded image
            chart_html = f'''<div class="chart-container" id="chart-{index}">
                <h4>{financial.title}</h4>
                <div class="chart-image">
                    <img src="data:image/png;base64,{chart_data}"
                         alt="{financial.title} Chart"
                         style="width: 100%; max-width: 800px; height: auto;">
                </div>
            </div>'''

        # Add statistics if available
        if stats:
            stats_html = f'''<div class="chart-stats">
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-label">Total:</span>
                        <span class="stat-value">${stats.get('total', 0):,.0f}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Average:</span>
                        <span class="stat-value">${stats.get('avg', 0):,.0f}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Growth:</span>
                        <span class="stat-value">{stats.get('growth', 0):.1f}%</span>
                    </div>
                </div>
            </div>'''

            chart_html = chart_html.replace('</div>', f'{stats_html}</div>')

        return chart_html

    def _generate_financial_summary(self, financial_data_list: List[FinancialData], chart_generator: ChartGenerator) -> str:
        """Generate a financial summary dashboard"""

        if not financial_data_list:
            return ""

        # Calculate overall statistics
        all_stats = {}
        total_revenue = 0
        total_expenses = 0

        for financial in financial_data_list:
            stats = chart_generator.get_chart_summary_stats(financial)
            if 'revenue' in financial.title.lower():
                total_revenue += stats.get('total', 0)
            if 'expense' in financial.title.lower():
                total_expenses += stats.get('total', 0)

        # Generate summary HTML
        summary_html = f'''
        <div class="financial-summary-dashboard">
            <h3>Financial Overview</h3>
            <div class="summary-grid">
                <div class="summary-card">
                    <h4>Total Revenue</h4>
                    <div class="summary-value">${total_revenue:,.0f}</div>
                </div>
                <div class="summary-card">
                    <h4>Total Expenses</h4>
                    <div class="summary-value">${total_expenses:,.0f}</div>
                </div>
                <div class="summary-card">
                    <h4>Net Profit</h4>
                    <div class="summary-value">${total_revenue - total_expenses:,.0f}</div>
                </div>
                <div class="summary-card">
                    <h4>Profit Margin</h4>
                    <div class="summary-value">{((total_revenue - total_expenses) / total_revenue * 100) if total_revenue > 0 else 0:.1f}%</div>
                </div>
            </div>
        </div>'''

        return summary_html

    def _process_team_sections(self, html_content: str, document: ParsedDocument) -> str:
        """Enhance team member sections with avatars and better layout"""

        if not document.team_members:
            return html_content

        # Add avatar placeholders for team members
        for member in document.team_members:
            member_html = f'<h4>{member.name}</h4>'
            if member_html in html_content:
                enhanced_member = f'''<div class="team-avatar">
                    <div class="avatar-circle">
                        {member.name[:2].upper()}
                    </div>
                </div>
                <h4>{member.name}</h4>'''
                html_content = html_content.replace(member_html, enhanced_member)

        return html_content

    def _inject_custom_css(self, html_content: str, brand_profile: BrandProfile) -> str:
        """Inject custom CSS based on brand profile"""

        custom_css = self._generate_custom_css(brand_profile)

        # Find or create style tag
        if '<style>' in html_content and '</style>' in html_content:
            # Append to existing style tag
            style_start = html_content.find('<style>')
            style_end = html_content.find('</style>') + len('</style>')
            existing_css = html_content[style_start:style_end]
            enhanced_css = existing_css.replace('</style>', f'{custom_css}</style>')
            html_content = html_content[:style_start] + enhanced_css + html_content[style_end:]
        elif '</head>' in html_content:
            # Insert before closing head tag
            html_content = html_content.replace(
                '</head>',
                f'<style>\n{custom_css}\n</style>\n</head>'
            )
        else:
            # Add at the beginning
            html_content = f'<style>\n{custom_css}\n</style>\n{html_content}'

        return html_content

    def _generate_custom_css(self, brand_profile: BrandProfile) -> str:
        """Generate custom CSS based on brand profile"""

        css_rules = []

        # Color palette CSS
        colors = brand_profile.color_palette
        css_rules.extend([
            f':root {{',
            f'  --brand-primary: {colors.primary[0] if colors.primary else "#1976D2"};',
            f'  --brand-secondary: {colors.secondary[0] if colors.secondary else "#424242"};',
            f'  --brand-accent: {colors.accent or "#2196F3"};',
            f'  --brand-background: {colors.background or "#FFFFFF"};',
            f'  --brand-text: {colors.text or "#000000"};',
            f'}}'
        ])

        # Typography CSS
        fonts = brand_profile.typography
        css_rules.extend([
            f'body {{',
            f'  font-family: "{fonts.body_font}", sans-serif;',
            f'  line-height: {fonts.line_height};',
            f'  letter-spacing: {fonts.letter_spacing}em;',
            f'}}',
            f'h1, h2, h3, h4, h5, h6 {{',
            f'  font-family: "{fonts.heading_font}", sans-serif;',
            f'}}'
        ])

        # Add custom font imports if needed
        if fonts.heading_font not in ['Arial', 'Helvetica', 'Georgia', 'Times New Roman']:
            css_rules.append(
                f'@import url("https://fonts.googleapis.com/css2?family={fonts.heading_font.replace(" ", "+")}&display=swap");'
            )

        # Layout CSS
        layout = brand_profile.layout
        css_rules.extend([
            f'.content-container {{',
            f'  max-width: {layout.max_width}px;',
            f'  margin: 0 auto;',
            f'  padding: {layout.margins["top"]}px {layout.margins["left"]}px;',
            f'}}'
        ])

        # Team avatar CSS
        css_rules.extend([
            f'.team-avatar {{',
            f'  text-align: center;',
            f'  margin-bottom: 1rem;',
            f'}}',
            f'.avatar-circle {{',
            f'  width: 80px;',
            f'  height: 80px;',
            f'  border-radius: 50%;',
            f'  background: var(--brand-primary);',
            f'  color: white;',
            f'  display: flex;',
            f'  align-items: center;',
            f'  justify-content: center;',
            f'  font-size: 1.5rem;',
            f'  font-weight: bold;',
            f'  margin: 0 auto;',
            f'}}'
        ])

        # Chart CSS
        css_rules.extend([
            f'.chart-container {{',
            f'  margin: 2rem 0;',
            f'  padding: 1.5rem;',
            f'  border: 1px solid #e0e0e0;',
            f'  border-radius: 8px;',
            f'  background: #f9f9f9;',
            f'}}',
            f'.chart-container h4 {{',
            f'  color: var(--brand-primary);',
            f'  margin-bottom: 1rem;',
            f'}}'
        ])

        return '\n'.join(css_rules)

    def _generate_chart_script(self, financial_data: List[FinancialData]) -> str:
        """Generate JavaScript for financial charts"""

        return '''
<script>
// Financial data visualization
function createFinancialChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Simple bar chart implementation
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, width, height);

    // Draw data bars (simplified example)
    const barWidth = 50;
    const barSpacing = 20;
    const maxValue = 100; // This should be calculated from actual data

    for (let i = 0; i < data.length && i < 10; i++) {
        const barHeight = (data[i] / maxValue) * (height - 40);
        const x = 40 + i * (barWidth + barSpacing);
        const y = height - barHeight - 20;

        ctx.fillStyle = '#1976D2';
        ctx.fillRect(x, y, barWidth, barHeight);

        // Add value labels
        ctx.fillStyle = '#333';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(data[i], x + barWidth/2, y - 5);
    }
}

// Initialize charts when page loads
document.addEventListener('DOMContentLoaded', function() {
    const charts = document.querySelectorAll('.chart-container canvas');
    charts.forEach(function(canvas) {
        const index = canvas.id.replace('canvas-', '');
        // Sample data - replace with actual financial data
        const sampleData = [65, 75, 85, 90, 95, 88, 92, 96];
        createFinancialChart(canvas.id, sampleData);
    });
});
</script>'''

    def _add_responsive_enhancements(self, html_content: str) -> str:
        """Add responsive design enhancements"""

        responsive_css = '''
/* Responsive Design Enhancements */
@media (max-width: 1200px) {
    .content-container {
        max-width: 95%;
        padding: 20px;
    }
}

@media (max-width: 768px) {
    .content-container {
        max-width: 100%;
        padding: 15px;
    }

    h1 { font-size: 1.8rem; }
    h2 { font-size: 1.5rem; }
    h3 { font-size: 1.3rem; }

    .team-grid {
        grid-template-columns: 1fr !important;
        gap: 1rem !important;
    }

    .financial-table {
        font-size: 0.8rem;
    }

    .financial-table th,
    .financial-table td {
        padding: 8px 4px;
    }

    .chart-container {
        padding: 1rem;
    }

    .chart-container canvas {
        width: 100% !important;
        height: auto !important;
    }
}

@media (max-width: 480px) {
    .content-container {
        padding: 10px;
    }

    h1 { font-size: 1.5rem; }
    h2 { font-size: 1.3rem; }

    .document-table {
        font-size: 0.7rem;
    }

    .avatar-circle {
        width: 60px !important;
        height: 60px !important;
        font-size: 1.2rem !important;
    }
}

/* Print styles */
@media print {
    .document-wrapper {
        max-width: none;
        margin: 0;
        padding: 0;
    }

    .floating-nav,
    .status-indicator,
    .chart-container {
        display: none;
    }

    .content-section {
        page-break-inside: avoid;
    }

    .financial-table {
        page-break-inside: avoid;
    }
}

/* Accessibility enhancements */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    body {
        background: #121212;
        color: #e0e0e0;
    }

    .content-container {
        background: #1e1e1e;
    }

    .financial-table th {
        background: #2d2d2d;
        color: #e0e0e0;
    }
}
'''

        # Add responsive CSS
        if '<style>' in html_content and '</style>' in html_content:
            style_end = html_content.find('</style>')
            html_content = (html_content[:style_end] +
                          responsive_css +
                          html_content[style_end:])
        elif '</head>' in html_content:
            html_content = html_content.replace(
                '</head>',
                f'<style>\n{responsive_css}\n</style>\n</head>'
            )

        # Add responsive meta tag
        if '<meta name="viewport"' not in html_content:
            html_content = html_content.replace(
                '<head>',
                '<head>\n<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            )

        return html_content

    def _add_seo_metadata(self, html_content: str, document: ParsedDocument,
                         brand_profile: BrandProfile) -> str:
        """Add SEO and metadata to HTML"""

        metadata = []

        # Basic meta tags
        title = document.metadata.title or f"{document.metadata.company_name} Document"
        metadata.append(f'<title>{title} - {brand_profile.company_name}</title>')
        metadata.append('<meta charset="UTF-8">')
        metadata.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')

        # Description
        if document.sections:
            description = document.sections[0].content[:200] + "..." if len(document.sections[0].content) > 200 else document.sections[0].content
            metadata.append(f'<meta name="description" content="{description}">')

        # Keywords
        keywords = [
            document.metadata.document_type,
            document.metadata.industry,
            document.metadata.company_name,
            'business document', 'professional'
        ]
        metadata.append(f'<meta name="keywords" content="{", ".join(keywords)}">')

        # Author
        if document.metadata.author:
            metadata.append(f'<meta name="author" content="{document.metadata.author}">')

        # Open Graph tags
        metadata.append('<meta property="og:title" content="' + title + '">')
        metadata.append('<meta property="og:site_name" content="' + brand_profile.company_name + '">')
        metadata.append('<meta property="og:type" content="article">')

        # Twitter Card
        metadata.append('<meta name="twitter:card" content="summary_large_image">')
        metadata.append('<meta name="twitter:title" content="' + title + '">')

        # Insert meta tags
        head_end = html_content.find('</head>')
        if head_end != -1:
            meta_html = '\n'.join(metadata) + '\n'
            html_content = html_content[:head_end] + meta_html + html_content[head_end:]

        return html_content

    def _generate_filename(self, document: ParsedDocument) -> str:
        """Generate appropriate filename for HTML output"""

        company = document.metadata.company_name.lower().replace(' ', '_')
        project = document.metadata.project.lower().replace(' ', '_') if document.metadata.project else ""
        doc_type = document.metadata.document_type.lower().replace('_', '-')
        title = document.metadata.title.lower().replace(' ', '_')[:30] if document.metadata.title else ""

        parts = [part for part in [company, project, doc_type, title] if part]
        filename = "_".join(parts) + ".html"

        # Sanitize filename
        filename = re.sub(r'[^\w\-_\.]', '', filename)

        return filename

    def generate_batch_html(self, documents: List[tuple], brand_profile: BrandProfile) -> List[str]:
        """Generate HTML for multiple documents"""

        output_paths = []

        for document, template_config in documents:
            try:
                output_path = self.generate_html(document, brand_profile, template_config)
                output_paths.append(output_path)
                print(f"✅ Generated HTML: {output_path}")
            except Exception as e:
                print(f"❌ Error generating HTML for {document.metadata.title}: {e}")
                continue

        return output_paths

    def create_index_page(self, generated_documents: List[str], brand_profile: BrandProfile,
                         output_filename: str = "index.html") -> str:
        """Create an index page listing all generated documents"""

        index_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand_profile.company_name} Document Library</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --brand-primary: {brand_profile.color_palette.primary[0] if brand_profile.color_palette.primary else "#1976D2"};
            --brand-secondary: {brand_profile.color_palette.secondary[0] if brand_profile.color_palette.secondary else "#424242"};
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: {brand_profile.typography.body_font}, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            text-align: center;
        }}

        .header h1 {{
            color: var(--brand-primary);
            margin-bottom: 0.5rem;
        }}

        .document-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }}

        .document-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .document-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}

        .document-title {{
            color: var(--brand-primary);
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}

        .document-info {{
            color: var(--brand-secondary);
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }}

        .document-link {{
            display: inline-block;
            background: var(--brand-primary);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            text-decoration: none;
            transition: background 0.3s ease;
        }}

        .document-link:hover {{
            background: var(--brand-secondary);
            color: white;
        }}

        @media (max-width: 768px) {{
            .document-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{brand_profile.company_name} Document Library</h1>
            <p>Generated professional documents</p>
        </header>

        <div class="document-grid">
            {self._generate_document_cards(generated_documents)}
        </div>
    </div>
</body>
</html>'''

        output_path = self.output_dir / output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(index_content)

        return str(output_path)

    def _generate_document_cards(self, document_paths: List[str]) -> str:
        """Generate HTML cards for document list"""

        cards = []

        for doc_path in document_paths:
            doc_name = Path(doc_path).stem
            # Try to extract readable name from filename
            readable_name = doc_name.replace('_', ' ').title()

            # Get file stats
            try:
                file_stat = Path(doc_path).stat()
                file_size = file_stat.st_size / 1024  # KB
                modified_time = file_stat.st_mtime
            except:
                file_size = 0
                modified_time = 0

            card = f'''<div class="document-card">
                <h3 class="document-title">{readable_name}</h3>
                <div class="document-info">
                    <p>Size: {file_size:.1f} KB</p>
                    <p>Type: HTML Document</p>
                </div>
                <a href="{doc_path}" class="document-link">View Document</a>
            </div>'''

            cards.append(card)

        return '\n'.join(cards)