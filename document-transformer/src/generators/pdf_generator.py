"""
PDF Generator for Document Transformation
Converts documents to high-quality PDF with print optimization
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
import logging

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from ..parser import ParsedDocument
from ..branding import BrandProfile
from ..templates import TemplateEngine, TemplateConfig
from .html_generator import HTMLGenerator

@dataclass
class PDFOptions:
    """PDF generation options"""
    page_size: str = "A4"
    margin_top: str = "2cm"
    margin_bottom: str = "2cm"
    margin_left: str = "2cm"
    margin_right: str = "2cm"
    orientation: str = "portrait"
    dpi: int = 300
    compress: bool = True
    optimize_images: bool = True
    embed_fonts: bool = True
    page_breaks: bool = True
    table_of_contents: bool = False
    header_footer: bool = True
    watermarks: bool = False

class PDFGenerator:
    """Generates high-quality PDF documents from parsed content"""

    def __init__(self, template_engine: TemplateEngine, output_dir: Path,
                 html_generator: HTMLGenerator = None):
        self.template_engine = template_engine
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize HTML generator if not provided
        if html_generator is None:
            html_generator = HTMLGenerator(template_engine, output_dir / "temp_html")
        self.html_generator = html_generator

        # Font configuration for WeasyPrint
        self.font_config = FontConfiguration()

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def generate_pdf(self, document: ParsedDocument, brand_profile: BrandProfile,
                    template_config: Optional[TemplateConfig] = None,
                    pdf_options: Optional[PDFOptions] = None,
                    output_filename: Optional[str] = None) -> str:
        """Generate PDF document"""

        # Use default PDF options if not provided
        if pdf_options is None:
            pdf_options = self._get_default_pdf_options(document)

        # Generate filename if not provided
        if output_filename is None:
            output_filename = self._generate_filename(document)

        # Generate HTML content first
        html_content = self._generate_pdf_html(document, brand_profile, template_config, pdf_options)

        # Create PDF-specific CSS
        pdf_css = self._generate_pdf_css(pdf_options, brand_profile)

        # Generate PDF
        output_path = self.output_dir / output_filename

        try:
            # Use WeasyPrint to convert HTML to PDF
            html_doc = HTML(string=html_content, base_url=str(self.output_dir))

            # Additional CSS for PDF optimization
            css_styles = [CSS(string=pdf_css)]

            # Generate PDF with options
            html_doc.write_pdf(
                target=str(output_path),
                stylesheets=css_styles,
                font_config=self.font_config,
                optimize_size=('fonts' if pdf_options.embed_fonts else None)
            )

            print(f"✅ Generated PDF: {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Error generating PDF: {e}")
            # Fallback: try using a simpler method
            return self._generate_pdf_fallback(document, brand_profile, output_filename)

    def _generate_pdf_html(self, document: ParsedDocument, brand_profile: BrandProfile,
                          template_config: Optional[TemplateConfig], pdf_options: PDFOptions) -> str:
        """Generate HTML optimized for PDF output"""

        # Get base HTML content
        if template_config is None:
            template_config = self.template_engine.get_template_for_document(document, brand_profile)

        html_content = self.template_engine.render_document(document, brand_profile, template_config)

        # Add PDF-specific optimizations
        html_content = self._add_pdf_optimizations(html_content, document, brand_profile, pdf_options)

        return html_content

    def _add_pdf_optimizations(self, html_content: str, document: ParsedDocument,
                             brand_profile: BrandProfile, pdf_options: PDFOptions) -> str:
        """Add PDF-specific optimizations to HTML"""

        # Add PDF-specific meta tags
        pdf_meta = f'''
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{document.metadata.title or document.metadata.company_name} PDF</title>
'''

        # Add PDF-specific CSS classes
        pdf_classes = '''
<!-- PDF Optimization -->
<style>
/* Print-specific styles */
@media print {
    body {
        margin: 0;
        padding: 0;
        font-size: 12pt;
        line-height: 1.4;
    }

    .document-wrapper {
        max-width: none;
        margin: 0;
        padding: 0;
    }

    /* Page breaks for sections */
    .content-section {
        page-break-inside: avoid;
        page-break-after: auto;
        margin-bottom: 2em;
    }

    .content-section h1, .content-section h2 {
        page-break-after: avoid;
        page-break-before: always;
    }

    .content-section h1:first-child,
    .content-section h2:first-child {
        page-break-before: avoid;
    }

    /* Table optimization */
    table {
        page-break-inside: avoid;
        font-size: 10pt;
    }

    .financial-table {
        page-break-inside: avoid;
        margin: 1em 0;
    }

    /* Team member optimization */
    .team-member {
        page-break-inside: avoid;
        display: inline-block;
        width: 48%;
        margin-right: 2%;
        vertical-align: top;
    }

    /* Image optimization */
    img {
        max-width: 100%;
        height: auto;
        page-break-inside: avoid;
    }

    /* Hide navigation and interactive elements */
    .floating-nav,
    .status-indicator,
    .table-of-contents,
    .document-footer {
        display: none;
    }

    /* Header and footer */
    .pdf-header,
    .pdf-footer {
        position: fixed;
        left: 0;
        right: 0;
        height: 1cm;
        font-size: 9pt;
        color: #666;
        text-align: center;
    }

    .pdf-header {
        top: 0;
        border-bottom: 1px solid #ddd;
    }

    .pdf-footer {
        bottom: 0;
        border-top: 1px solid #ddd;
    }

    /* Page content */
    .pdf-content {
        margin-top: 2cm;
        margin-bottom: 2cm;
    }
}

/* PDF-specific optimization */
.pdf-page {
    size: A4;
    margin: 2cm;
}

.pdf-section {
    orphans: 3;
    widows: 3;
}

.pdf-table {
    -pdf-page-break-inside: avoid;
}

.pdf-image {
    -pdf-page-break-inside: avoid;
    max-width: 100%;
    height: auto;
}
</style>
'''

        # Insert optimizations into HTML
        if '<head>' in html_content and '</head>' in html_content:
            head_end = html_content.find('</head>')
            html_content = (html_content[:head_end] +
                          pdf_meta + pdf_classes +
                          html_content[head_end:])

        # Add PDF wrapper classes
        html_content = html_content.replace(
            '<div class="document-wrapper">',
            '<div class="document-wrapper pdf-page">'
        )

        # Add page break instructions
        if pdf_options.page_breaks:
            html_content = self._add_smart_page_breaks(html_content, document)

        # Add header and footer if requested
        if pdf_options.header_footer:
            html_content = self._add_pdf_header_footer(html_content, brand_profile)

        return html_content

    def _generate_pdf_css(self, pdf_options: PDFOptions, brand_profile: BrandProfile) -> str:
        """Generate CSS specific to PDF generation"""

        css_rules = []

        # Page setup
        css_rules.extend([
            '@page {',
            f'  size: {pdf_options.page_size} {pdf_options.orientation};',
            f'  margin: {pdf_options.margin_top} {pdf_options.margin_right} {pdf_options.margin_bottom} {pdf_options.margin_left};',
            '}'
        ])

        # Brand colors
        colors = brand_profile.color_palette
        css_rules.extend([
            '@media print {',
            f'  :root {{',
            f'    --brand-primary: {colors.primary[0] if colors.primary else "#000000"};',
            f'    --brand-secondary: {colors.secondary[0] if colors.secondary else "#666666"};',
            f'  }}',
            '}'
        ])

        # Typography for print
        fonts = brand_profile.typography
        css_rules.extend([
            '@media print {',
            f'  body {{',
            f'    font-family: "{fonts.body_font}", serif;',
            f'    font-size: 11pt;',
            f'    line-height: 1.5;',
            f'    color: #000;',
            f'    background: #fff;',
            f'  }}',
            f'  h1 {{ font-size: 18pt; font-family: "{fonts.heading_font}", sans-serif; }}',
            f'  h2 {{ font-size: 16pt; font-family: "{fonts.heading_font}", sans-serif; }}',
            f'  h3 {{ font-size: 14pt; font-family: "{fonts.heading_font}", sans-serif; }}',
            f'  h4, h5, h6 {{ font-size: 12pt; font-family: "{fonts.heading_font}", sans-serif; }}',
            '}'
        ])

        # Table optimization
        css_rules.extend([
            '@media print {',
            '  table {',
            '    border-collapse: collapse;',
            '    width: 100%;',
            '    font-size: 9pt;',
            '  }',
            '  th, td {',
            '    border: 1px solid #000;',
            '    padding: 4px 6px;',
            '    text-align: left;',
            '  }',
            '  th {',
            '    background: #f0f0f0;',
            '    font-weight: bold;',
            '  }',
            '}'
        ])

        # Image optimization
        css_rules.extend([
            '@media print {',
            '  img {',
            '    max-width: 100%;',
            '    height: auto;',
            '    page-break-inside: avoid;',
            '  }',
            '}'
        ])

        # Page break rules
        if pdf_options.page_breaks:
            css_rules.extend([
                '@media print {',
                '  .content-section {',
                '    page-break-inside: avoid;',
                '    page-break-after: auto;',
                '  }',
                '  .financial-table {',
                '    page-break-inside: avoid;',
                '  }',
                '  .team-member {',
                '    page-break-inside: avoid;',
                '  }',
                '}'
            ])

        return '\n'.join(css_rules)

    def _get_default_pdf_options(self, document: ParsedDocument) -> PDFOptions:
        """Get default PDF options based on document type"""

        doc_type = document.metadata.document_type

        base_options = PDFOptions()

        if doc_type in ['financial_projections', 'market_research']:
            # Data-heavy documents need landscape orientation
            base_options.orientation = 'landscape' if len(document.tables) > 3 else 'portrait'
            base_options.page_breaks = True
        elif doc_type == 'pitch_deck':
            # Presentations might benefit from larger pages
            base_options.page_size = 'A4'
            base_options.page_breaks = True
        elif doc_type == 'investor_teaser':
            # Short documents can have smaller margins
            base_options.margin_top = '1.5cm'
            base_options.margin_bottom = '1.5cm'
        else:
            # Business plans need standard formatting
            base_options.page_breaks = True
            base_options.table_of_contents = True

        return base_options

    def _generate_filename(self, document: ParsedDocument) -> str:
        """Generate appropriate filename for PDF output"""

        company = document.metadata.company_name.lower().replace(' ', '_')
        project = document.metadata.project.lower().replace(' ', '_') if document.metadata.project else ""
        doc_type = document.metadata.document_type.lower().replace('_', '-')
        title = document.metadata.title.lower().replace(' ', '_')[:30] if document.metadata.title else ""

        parts = [part for part in [company, project, doc_type, title] if part]
        filename = "_".join(parts) + ".pdf"

        # Sanitize filename
        import re
        filename = re.sub(r'[^\w\-_\.]', '', filename)

        return filename

    def _add_smart_page_breaks(self, html_content: str, document: ParsedDocument) -> str:
        """Add intelligent page breaks to HTML"""

        # Add page break before major sections
        sections = document.sections
        for i, section in enumerate(sections):
            if section.level <= 2 and i > 0:  # Break before h1 and h2 (except first)
                section_id = section.title.replace(' ', '-').lower()
                html_content = html_content.replace(
                    f'<h{section.level}>{section.title}</h{section.level}>',
                    f'<div style="page-break-before: always;"></div>\n<h{section.level}>{section.title}</h{section.level}>'
                )

        # Avoid breaking inside tables
        html_content = html_content.replace(
            '<table class="financial-table">',
            '<div style="page-break-inside: avoid;"><table class="financial-table">'
        )
        html_content = html_content.replace(
            '</table>',
            '</table></div>'
        )

        return html_content

    def _add_pdf_header_footer(self, html_content: str, brand_profile: BrandProfile) -> str:
        """Add header and footer for PDF"""

        header_html = f'''
<div class="pdf-header">
    <div>{brand_profile.company_name}</div>
</div>'''

        footer_html = '''
<div class="pdf-footer">
    <div>Page <span class="page-number"></span> of <span class="page-count"></span></div>
</div>'''

        # Insert header after body tag
        html_content = html_content.replace('<body>', f'<body>{header_html}')

        # Insert footer before closing body tag
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', f'{footer_html}</body>')

        return html_content

    def _generate_pdf_fallback(self, document: ParsedDocument, brand_profile: BrandProfile,
                             output_filename: str) -> str:
        """Fallback method for PDF generation if WeasyPrint fails"""

        print("⚠️ Using fallback PDF generation method")

        # Create a simple HTML file and instruct user to print to PDF
        fallback_html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{document.metadata.title or document.metadata.company_name}</title>
    <style>
        body {{
            font-family: {brand_profile.typography.body_font}, sans-serif;
            line-height: 1.6;
            margin: 2cm;
            color: #000;
            background: #fff;
        }}
        h1, h2, h3 {{
            color: {brand_profile.color_palette.primary[0] if brand_profile.color_palette.primary else "#000"};
            page-break-after: avoid;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            page-break-inside: avoid;
        }}
        th, td {{
            border: 1px solid #000;
            padding: 8px;
            text-align: left;
        }}
        .section {{
            page-break-inside: avoid;
            margin-bottom: 2em;
        }}
        .instructions {{
            background: #f0f0f0;
            padding: 1em;
            border: 1px solid #ccc;
            margin-bottom: 2em;
        }}
    </style>
</head>
<body>
    <div class="instructions">
        <h3>PDF Generation Instructions</h3>
        <p>This document has been prepared for PDF export. To create a PDF:</p>
        <ol>
            <li>Press Ctrl+P (or Cmd+P on Mac) to open print dialog</li>
            <li>Select "Save as PDF" as the destination</li>
            <li>Adjust margins if needed</li>
            <li>Click "Save" to create your PDF</li>
        </ol>
    </div>

    <h1>{document.metadata.title or document.metadata.company_name}</h1>
    <p><strong>Company:</strong> {document.metadata.company_name}</p>
    <p><strong>Date:</strong> {document.metadata.last_modified or "N/A"}</p>
    <p><strong>Type:</strong> {document.metadata.document_type.replace('_', ' ').title()}</p>

    {self._convert_sections_to_simple_html(document.sections)}
    {self._convert_financial_data_to_simple_html(document.financial_data)}
    {self._convert_team_to_simple_html(document.team_members)}
</body>
</html>'''

        # Save HTML file
        html_path = self.output_dir / output_filename.replace('.pdf', '_fallback.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(fallback_html)

        print(f"📄 Created fallback HTML: {html_path}")
        print("💡 Open this file in your browser and print to PDF")

        return str(html_path)

    def _convert_sections_to_simple_html(self, sections) -> str:
        """Convert sections to simple HTML for fallback"""
        html = ""
        for section in sections:
            html += f'<div class="section">\n'
            html += f'<h{section.level}>{section.title}</h{section.level}>\n'
            html += f'<div>{section.content}</div>\n'
            html += f'</div>\n'
        return html

    def _convert_financial_data_to_simple_html(self, financial_data) -> str:
        """Convert financial data to simple HTML for fallback"""
        html = ""
        if financial_data:
            html += '<div class="section">\n<h2>Financial Data</h2>\n'
            for financial in financial_data:
                html += f'<h3>{financial.title}</h3>\n<table>\n'
                if financial.headers:
                    html += '<tr>\n'
                    for header in financial.headers:
                        html += f'<th>{header}</th>\n'
                    html += '</tr>\n'
                for row in financial.table_data:
                    html += '<tr>\n'
                    for cell in row:
                        html += f'<td>{cell}</td>\n'
                    html += '</tr>\n'
                html += '</table>\n'
            html += '</div>\n'
        return html

    def _convert_team_to_simple_html(self, team_members) -> str:
        """Convert team data to simple HTML for fallback"""
        html = ""
        if team_members:
            html += '<div class="section">\n<h2>Team</h2>\n'
            for member in team_members:
                html += f'<div style="margin-bottom: 1em;">\n'
                html += f'<h4>{member.name}</h4>\n'
                if member.title:
                    html += f'<p><strong>{member.title}</strong></p>\n'
                if member.bio:
                    html += f'<p>{member.bio}</p>\n'
                html += '</div>\n'
            html += '</div>\n'
        return html

    def generate_batch_pdf(self, documents: list, brand_profile: BrandProfile,
                          pdf_options: PDFOptions = None) -> list:
        """Generate PDFs for multiple documents"""

        output_paths = []

        for document, template_config in documents:
            try:
                output_path = self.generate_pdf(
                    document, brand_profile, template_config, pdf_options
                )
                output_paths.append(output_path)
            except Exception as e:
                print(f"❌ Error generating PDF for {document.metadata.title}: {e}")
                continue

        return output_paths