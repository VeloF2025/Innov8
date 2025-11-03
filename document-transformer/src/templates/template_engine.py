"""
Dynamic Template Engine for Document Generation
Handles template selection, customization, and rendering
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from dataclasses import dataclass

from ..branding import BrandProfile, DesignStyle
from ..parser import ParsedDocument, ContentSection

@dataclass
class TemplateConfig:
    """Template configuration"""
    name: str
    description: str
    document_types: List[str]
    design_styles: List[DesignStyle]
    template_file: str
    css_file: str
    variables: Dict[str, Any] = None

class TemplateEngine:
    """Dynamic template engine for document generation"""

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.templates_dir.mkdir(exist_ok=True)

        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Register custom filters
        self._register_filters()

        # Load available templates
        self.templates = self._load_templates()

        # Create default templates if they don't exist
        self._ensure_default_templates()

    def _register_filters(self):
        """Register custom Jinja2 filters"""

        def format_currency(value, currency='USD'):
            """Format currency values"""
            try:
                if isinstance(value, str):
                    value = float(value.replace(',', '').replace('$', ''))
                return f"${value:,.2f}"
            except:
                return value

        def format_number(value):
            """Format numbers with commas"""
            try:
                if isinstance(value, str):
                    value = float(value.replace(',', ''))
                return f"{value:,.0f}"
            except:
                return value

        def format_percentage(value):
            """Format percentage values"""
            try:
                if isinstance(value, str):
                    value = float(value.replace('%', ''))
                return f"{value}%"
            except:
                return value

        def truncate_words(text, length=50):
            """Truncate text to specified number of words"""
            if not text:
                return ""
            words = text.split()
            if len(words) <= length:
                return text
            return ' '.join(words[:length]) + '...'

        def slugify(text):
            """Convert text to URL-friendly slug"""
            import re
            text = text.lower()
            text = re.sub(r'[^\w\s-]', '', text)
            text = re.sub(r'[-\s]+', '-', text)
            return text.strip('-')

        # Register filters
        self.jinja_env.filters['currency'] = format_currency
        self.jinja_env.filters['number'] = format_number
        self.jinja_env.filters['percentage'] = format_percentage
        self.jinja_env.filters['truncate_words'] = truncate_words
        self.jinja_env.filters['slugify'] = slugify

    def _load_templates(self) -> Dict[str, TemplateConfig]:
        """Load available template configurations"""

        templates = {}

        # Define built-in templates
        builtin_templates = {
            'modern_corporate': TemplateConfig(
                name='Modern Corporate',
                description='Clean, professional design for modern businesses',
                document_types=['business_plan', 'investor_teaser', 'company_overview'],
                design_styles=[DesignStyle.MODERN_CORPORATE, DesignStyle.PROFESSIONAL_CLASSIC],
                template_file='modern_corporate.html',
                css_file='modern_corporate.css',
                variables={
                    'primary_color': '#1976D2',
                    'secondary_color': '#424242',
                    'font_family': 'Inter, sans-serif'
                }
            ),
            'startup_vibrant': TemplateConfig(
                name='Startup Vibrant',
                description='Energetic design for startups and tech companies',
                document_types=['pitch_deck', 'investor_teaser'],
                design_styles=[DesignStyle.STARTUP_VIBRANT],
                template_file='startup_vibrant.html',
                css_file='startup_vibrant.css',
                variables={
                    'primary_color': '#6200EA',
                    'secondary_color': '#FF6B6B',
                    'font_family': 'Montserrat, sans-serif'
                }
            ),
            'professional_classic': TemplateConfig(
                name='Professional Classic',
                description='Traditional design for established companies',
                document_types=['business_plan', 'financial_projections', 'market_research'],
                design_styles=[DesignStyle.PROFESSIONAL_CLASSIC],
                template_file='professional_classic.html',
                css_file='professional_classic.css',
                variables={
                    'primary_color': '#1B5E20',
                    'secondary_color': '#37474F',
                    'font_family': 'Georgia, serif'
                }
            ),
            'creative_minimal': TemplateConfig(
                name='Creative Minimal',
                description='Minimalist design for creative industries',
                document_types=['investor_teaser', 'pitch_deck', 'company_overview'],
                design_styles=[DesignStyle.CREATIVE_MINIMAL],
                template_file='creative_minimal.html',
                css_file='creative_minimal.css',
                variables={
                    'primary_color': '#9C27B0',
                    'secondary_color': '#616161',
                    'font_family': 'Inter, sans-serif'
                }
            ),
            'financial_report': TemplateConfig(
                name='Financial Report',
                description='Optimized for financial documents and data tables',
                document_types=['financial_projections', 'market_research'],
                design_styles=[DesignStyle.PROFESSIONAL_CLASSIC, DesignStyle.MODERN_CORPORATE],
                template_file='financial_report.html',
                css_file='financial_report.css',
                variables={
                    'primary_color': '#388E3C',
                    'secondary_color': '#455A64',
                    'font_family': 'Roboto, sans-serif'
                }
            )
        }

        templates.update(builtin_templates)
        return templates

    def _ensure_default_templates(self):
        """Create default template files if they don't exist"""

        # Create HTML templates
        html_templates = {
            'base.html': self._get_base_template(),
            'modern_corporate.html': self._get_modern_corporate_template(),
            'startup_vibrant.html': self._get_startup_vibrant_template(),
            'professional_classic.html': self._get_professional_classic_template(),
            'creative_minimal.html': self._get_creative_minimal_template(),
            'financial_report.html': self._get_financial_report_template()
        }

        # Create CSS files
        css_templates = {
            'base.css': self._get_base_css(),
            'modern_corporate.css': self._get_modern_corporate_css(),
            'startup_vibrant.css': self._get_startup_vibrant_css(),
            'professional_classic.css': self._get_professional_classic_css(),
            'creative_minimal.css': self._get_creative_minimal_css(),
            'financial_report.css': self._get_financial_report_css()
        }

        # Write HTML templates
        for filename, content in html_templates.items():
            file_path = self.templates_dir / filename
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

        # Create CSS directory and write CSS files
        css_dir = self.templates_dir / 'css'
        css_dir.mkdir(exist_ok=True)

        for filename, content in css_templates.items():
            file_path = css_dir / filename
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

    def get_template_for_document(self, document: ParsedDocument, brand_profile: BrandProfile) -> TemplateConfig:
        """Select the best template for a document based on type and brand profile"""

        document_type = document.metadata.document_type
        design_style = brand_profile.design_style

        # Find templates that match document type and design style
        matching_templates = []
        for template_name, template_config in self.templates.items():
            if document_type in template_config.document_types:
                if design_style in template_config.design_styles:
                    matching_templates.append(template_config)

        # If no exact match, find templates that match document type only
        if not matching_templates:
            for template_name, template_config in self.templates.items():
                if document_type in template_config.document_types:
                    matching_templates.append(template_config)

        # If still no match, use modern_corporate as default
        if not matching_templates:
            matching_templates = [self.templates['modern_corporate']]

        # Return the first (best) match
        return matching_templates[0]

    def render_document(self, document: ParsedDocument, brand_profile: BrandProfile,
                       template_config: Optional[TemplateConfig] = None) -> str:
        """Render a document using the appropriate template"""

        # Select template if not provided
        if template_config is None:
            template_config = self.get_template_for_document(document, brand_profile)

        # Load template
        template = self.jinja_env.get_template(template_config.template_file)

        # Prepare template variables
        template_vars = self._prepare_template_variables(document, brand_profile, template_config)

        # Render template
        rendered_content = template.render(**template_vars)

        return rendered_content

    def _prepare_template_variables(self, document: ParsedDocument, brand_profile: BrandProfile,
                                  template_config: TemplateConfig) -> Dict[str, Any]:
        """Prepare variables for template rendering"""

        variables = {
            # Document data
            'document': document,
            'title': document.metadata.title or document.metadata.company_name,
            'company': document.metadata.company_name,
            'industry': document.metadata.industry,
            'document_type': document.metadata.document_type,
            'sections': document.sections,
            'financial_data': document.financial_data,
            'team_members': document.team_members,
            'tables': document.tables,
            'metadata': document.metadata,

            # Brand profile data
            'brand': brand_profile,
            'brand_colors': brand_profile.color_palette,
            'brand_fonts': brand_profile.typography,
            'brand_layout': brand_profile.layout,
            'brand_assets': brand_profile.brand_assets,

            # Template configuration
            'template_config': template_config,
            'template_vars': template_config.variables or {},

            # Helper functions
            'has_financial_data': len(document.financial_data) > 0,
            'has_team_members': len(document.team_members) > 0,
            'has_tables': len(document.tables) > 0,
            'section_count': len(document.sections),
            'word_count': len(' '.join([s.content for s in document.sections]).split()),

            # Current date
            'current_date': self._get_current_date()
        }

        # Merge template variables
        if template_config.variables:
            variables.update(template_config.variables)

        return variables

    def _get_current_date(self) -> str:
        """Get current date in a nice format"""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")

    def list_templates(self) -> List[str]:
        """List all available templates"""
        return list(self.templates.keys())

    def get_template_info(self, template_name: str) -> Optional[TemplateConfig]:
        """Get information about a specific template"""
        return self.templates.get(template_name)

    # Template definitions
    def _get_base_template(self) -> str:
        """Base template that other templates extend"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if title %}{{ title }} - {{ company }}{% else %}{{ company }} Document{% endif %}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Georgia:wght@300;400;700&family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        {{ css_content|safe }}
    </style>
</head>
<body>
    <div class="document-wrapper">
        {% block header %}
        <header class="document-header">
            {% if brand_assets.logo_path %}
            <div class="logo">
                <img src="{{ brand_assets.logo_path }}" alt="{{ company }} Logo" />
            </div>
            {% endif %}
            <div class="company-info">
                <h1 class="company-name">{{ company }}</h1>
                {% if brand.tagline %}
                <p class="tagline">{{ brand.tagline }}</p>
                {% endif %}
            </div>
        </header>
        {% endblock %}

        {% block content %}{% endblock %}

        {% block footer %}
        <footer class="document-footer">
            <div class="footer-content">
                <p>Generated on {{ current_date }} | {{ document_type|title }}</p>
                {% if brand.website %}
                <p><a href="{{ brand.website }}">{{ brand.website }}</a></p>
                {% endif %}
            </div>
        </footer>
        {% endblock %}
    </div>

    <script>
        // Basic interactivity
        document.addEventListener('DOMContentLoaded', function() {
            // Smooth scrolling for table of contents
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({ behavior: 'smooth' });
                    }
                });
            });
        });
    </script>
</body>
</html>'''

    def _get_modern_corporate_template(self) -> str:
        """Modern corporate template"""
        return '''{% extends "base.html" %}

{% block content %}
<div class="content-container">
    {% if title %}
    <div class="document-title">
        <h1>{{ title }}</h1>
        {% if metadata.status %}
        <span class="status-badge status-{{ metadata.status }}">{{ metadata.status|title }}</span>
        {% endif %}
    </div>
    {% endif %}

    {% if has_sections %}
    <nav class="table-of-contents">
        <h3>Table of Contents</h3>
        <ul>
            {% for section in sections %}
            <li><a href="#{{ section.title|slugify }}">{{ section.title }}</a></li>
            {% if section.subsections %}
                {% for subsection in section.subsections %}
                <li><a href="#{{ subsection.title|slugify }}">{{ subsection.title }}</a></li>
                {% endfor %}
            {% endif %}
            {% endfor %}
        </ul>
    </nav>
    {% endif %}

    <main class="document-content">
        {% for section in sections %}
        <section id="{{ section.title|slugify }}" class="content-section">
            <h{{ section.level }} class="section-title">{{ section.title }}</h{{ section.level }}>
            <div class="section-content">
                {{ section.content|nl2br|safe }}
            </div>

            {% if loop.first and has_team_members %}
            <div class="team-section">
                <h3>Leadership Team</h3>
                <div class="team-grid">
                    {% for member in team_members %}
                    <div class="team-member">
                        <h4>{{ member.name }}</h4>
                        <p class="member-title">{{ member.title }}</p>
                        {% if member.bio %}
                        <p class="member-bio">{{ member.bio }}</p>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </section>
        {% endfor %}

        {% if has_financial_data %}
        <section id="financial-data" class="content-section">
            <h2>Financial Information</h2>
            {% for financial in financial_data %}
            <div class="financial-table-container">
                <h3>{{ financial.title }}</h3>
                <table class="financial-table">
                    <thead>
                        <tr>
                            {% for header in financial.headers %}
                            <th>{{ header }}</th>
                            {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in financial.table_data %}
                        <tr>
                            {% for cell in row %}
                            <td>{{ cell }}</td>
                            {% endfor %}
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endfor %}
        </section>
        {% endif %}
    </main>
</div>
{% endblock %}'''

    def _get_startup_vibrant_template(self) -> str:
        """Startup vibrant template"""
        return '''{% extends "base.html" %}

{% block content %}
<div class="content-container">
    {% if title %}
    <div class="hero-section">
        <h1 class="hero-title">{{ title }}</h1>
        {% if brand.tagline %}
        <p class="hero-subtitle">{{ brand.tagline }}</p>
        {% endif %}
        {% if metadata.status %}
        <div class="status-indicator">
            <span class="pulse-dot"></span>
            <span>{{ metadata.status|title }}</span>
        </div>
        {% endif %}
    </div>
    {% endif %}

    {% if has_sections %}
    <nav class="floating-nav">
        <h4>Quick Navigation</h4>
        <div class="nav-items">
            {% for section in sections %}
            <a href="#{{ section.title|slugify }}" class="nav-item">{{ section.title }}</a>
            {% endfor %}
        </div>
    </nav>
    {% endif %}

    <main class="document-content">
        {% for section in sections %}
        <section id="{{ section.title|slugify }}" class="content-section">
            <div class="section-header">
                <h{{ section.level }} class="section-title">{{ section.title }}</h{{ section.level }}>
                <div class="section-accent"></div>
            </div>
            <div class="section-content">
                {{ section.content|nl2br|safe }}
            </div>

            {% if loop.first and has_team_members %}
            <div class="team-showcase">
                <h3>Meet Our Team</h3>
                <div class="team-grid">
                    {% for member in team_members %}
                    <div class="team-card">
                        <div class="member-avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <h4>{{ member.name }}</h4>
                        <p class="member-title">{{ member.title }}</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </section>
        {% endfor %}
    </main>
</div>
{% endblock %}'''

    def _get_professional_classic_template(self) -> str:
        """Professional classic template"""
        return '''{% extends "base.html" %}

{% block content %}
<div class="content-container">
    <div class="document-header-classic">
        {% if title %}
        <h1 class="document-title">{{ title }}</h1>
        {% endif %}
        <div class="document-meta">
            <span class="meta-item">{{ company }}</span>
            {% if industry %}
            <span class="meta-item">{{ industry|title }}</span>
            {% endif %}
            <span class="meta-item">{{ current_date }}</span>
        </div>
    </div>

    {% if has_sections %}
    <div class="toc-classic">
        <h2>Table of Contents</h2>
        <ul class="toc-list">
            {% for section in sections %}
            <li class="toc-item">
                <a href="#{{ section.title|slugify }}">{{ section.title }}</a>
                <span class="toc-page">{{ loop.index }}</span>
            </li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}

    <main class="document-content-classic">
        {% for section in sections %}
        <section id="{{ section.title|slugify }}" class="section-classic">
            <h{{ section.level }} class="section-title-classic">{{ section.title }}</h{{ section.level }}>
            <div class="section-content-classic">
                {{ section.content|nl2br|safe }}
            </div>
        </section>
        {% endfor %}

        {% if has_team_members %}
        <section class="team-classic">
            <h2>Management Team</h2>
            <div class="team-list-classic">
                {% for member in team_members %}
                <div class="team-member-classic">
                    <h4>{{ member.name }}</h4>
                    <p class="member-title-classic">{{ member.title }}</p>
                    {% if member.experience %}
                    <p class="member-experience">{{ member.experience }}</p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </section>
        {% endif %}
    </main>
</div>
{% endblock %}'''

    def _get_creative_minimal_template(self) -> str:
        """Creative minimal template"""
        return '''{% extends "base.html" %}

{% block content %}
<div class="content-container">
    {% if title %}
    <div class="title-minimal">
        <h1>{{ title }}</h1>
        <div class="title-line"></div>
    </div>
    {% endif %}

    <main class="content-minimal">
        {% for section in sections %}
        <section id="{{ section.title|slugify }}" class="section-minimal">
            <h{{ section.level }} class="section-title-minimal">{{ section.title }}</h{{ section.level }}>
            <div class="section-content-minimal">
                {{ section.content|nl2br|safe }}
            </div>
        </section>
        {% endfor %}

        {% if has_team_members %}
        <section class="team-minimal">
            <h2 class="section-title-minimal">Team</h2>
            <div class="team-minimal-grid">
                {% for member in team_members %}
                <div class="team-member-minimal">
                    <h3>{{ member.name }}</h3>
                    <p>{{ member.title }}</p>
                </div>
                {% endfor %}
            </div>
        </section>
        {% endif %}
    </main>
</div>
{% endblock %}'''

    def _get_financial_report_template(self) -> str:
        """Financial report template"""
        return '''{% extends "base.html" %}

{% block content %}
<div class="content-container">
    <div class="financial-header">
        {% if title %}
        <h1>{{ title }}</h1>
        {% endif %}
        <div class="financial-meta">
            <span>{{ company }}</span>
            <span>{{ current_date }}</span>
            {% if metadata.status %}
            <span class="status-{{ metadata.status }}">{{ metadata.status|title }}</span>
            {% endif %}
        </div>
    </div>

    {% if has_sections %}
    <nav class="financial-nav">
        <h3>Document Sections</h3>
        <ul>
            {% for section in sections %}
            <li><a href="#{{ section.title|slugify }}">{{ section.title }}</a></li>
            {% endfor %}
        </ul>
    </nav>
    {% endif %}

    <main class="financial-content">
        {% for section in sections %}
        <section id="{{ section.title|slugify }}" class="financial-section">
            <h{{ section.level }}>{{ section.title }}</h{{ section.level }}>
            <div class="financial-content-text">
                {{ section.content|nl2br|safe }}
            </div>
        </section>
        {% endfor %}

        {% if has_financial_data %}
        <section id="financial-tables" class="financial-section">
            <h2>Financial Data</h2>
            {% for financial in financial_data %}
            <div class="financial-report-table">
                <h3>{{ financial.title }}</h3>
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                {% for header in financial.headers %}
                                <th>{{ header }}</th>
                                {% endfor %}
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in financial.table_data %}
                            <tr>
                                {% for cell in row %}
                                <td>{{ cell }}</td>
                                {% endfor %}
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
            {% endfor %}
        </section>
        {% endif %}
    </main>
</div>
{% endblock %}'''

    # CSS definitions
    def _get_base_css(self) -> str:
        """Base CSS styles"""
        return '''/* Base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
    color: #333;
    background: #fff;
}

.document-wrapper {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    line-height: 1.3;
}

p {
    margin-bottom: 1em;
}

/* Links */
a {
    color: #1976D2;
    text-decoration: none;
    transition: color 0.3s ease;
}

a:hover {
    color: #0D47A1;
    text-decoration: underline;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5em 0;
}

th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    font-weight: 600;
    background-color: #f5f5f5;
}

/* Responsive */
@media print {
    .document-wrapper {
        max-width: none;
        margin: 0;
        padding: 0;
    }
}'''

    def _get_modern_corporate_css(self) -> str:
        """Modern corporate CSS"""
        return '''/* Modern Corporate Styles */
:root {
    --primary-color: #1976D2;
    --secondary-color: #424242;
    --accent-color: #2196F3;
    --background-color: #ffffff;
    --text-color: #212121;
    --light-gray: #f5f5f5;
    --border-color: #e0e0e0;
}

body {
    background: var(--background-color);
    color: var(--text-color);
}

.document-header {
    border-bottom: 3px solid var(--primary-color);
    padding: 2rem 0;
    margin-bottom: 3rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.logo img {
    max-height: 60px;
    max-width: 200px;
}

.company-info h1 {
    color: var(--primary-color);
    font-size: 2.5rem;
    font-weight: 700;
}

.tagline {
    color: var(--secondary-color);
    font-size: 1.1rem;
    font-style: italic;
}

.document-title {
    margin-bottom: 2rem;
    text-align: center;
}

.document-title h1 {
    color: var(--primary-color);
    font-size: 2.2rem;
    margin-bottom: 1rem;
}

.status-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 500;
}

.status-draft {
    background: #FFF3E0;
    color: #F57C00;
}

.status-final {
    background: #E8F5E8;
    color: #2E7D32;
}

.table-of-contents {
    background: var(--light-gray);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    border-left: 4px solid var(--primary-color);
}

.table-of-contents h3 {
    color: var(--primary-color);
    margin-bottom: 1rem;
}

.table-of-contents ul {
    list-style: none;
}

.table-of-contents li {
    margin-bottom: 0.5rem;
}

.table-of-contents a {
    color: var(--secondary-color);
    font-weight: 500;
}

.content-section {
    margin-bottom: 3rem;
}

.section-title {
    color: var(--primary-color);
    border-bottom: 2px solid var(--accent-color);
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
}

.team-section {
    margin-top: 2rem;
    padding: 2rem;
    background: var(--light-gray);
    border-radius: 8px;
}

.team-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-top: 1rem;
}

.team-member {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.team-member h4 {
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}

.member-title {
    color: var(--secondary-color);
    font-weight: 500;
}

.financial-table-container {
    margin: 2rem 0;
}

.financial-table {
    width: 100%;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    overflow: hidden;
}

.financial-table th {
    background: var(--primary-color);
    color: white;
}

.financial-table td {
    border-bottom: 1px solid var(--border-color);
}

.document-footer {
    border-top: 1px solid var(--border-color);
    padding-top: 2rem;
    margin-top: 3rem;
    text-align: center;
    color: var(--secondary-color);
    font-size: 0.9rem;
}

@media (max-width: 768px) {
    .document-header {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }

    .company-info h1 {
        font-size: 2rem;
    }

    .team-grid {
        grid-template-columns: 1fr;
    }
}'''

    def _get_startup_vibrant_css(self) -> str:
        """Startup vibrant CSS"""
        return '''/* Startup Vibrant Styles */
:root {
    --primary-color: #6200EA;
    --secondary-color: #FF6B6B;
    --accent-color: #00D4AA;
    --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --background-color: #ffffff;
    --text-color: #2D3748;
}

.hero-section {
    background: var(--gradient-primary);
    color: white;
    padding: 4rem 2rem;
    text-align: center;
    border-radius: 16px;
    margin-bottom: 3rem;
    position: relative;
    overflow: hidden;
}

.hero-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="1" fill="white" opacity="0.1"/><circle cx="10" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
    opacity: 0.3;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 1rem;
    position: relative;
    z-index: 1;
}

.hero-subtitle {
    font-size: 1.3rem;
    opacity: 0.9;
    margin-bottom: 2rem;
    position: relative;
    z-index: 1;
}

.status-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    position: relative;
    z-index: 1;
}

.pulse-dot {
    width: 12px;
    height: 12px;
    background: var(--accent-color);
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.2); opacity: 0.7; }
}

.floating-nav {
    position: fixed;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    z-index: 1000;
    max-width: 200px;
}

.floating-nav h4 {
    color: var(--primary-color);
    margin-bottom: 1rem;
    font-size: 0.9rem;
}

.nav-items {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.nav-item {
    display: block;
    padding: 0.5rem 0;
    color: var(--text-color);
    font-weight: 500;
    transition: color 0.3s ease;
}

.nav-item:hover {
    color: var(--primary-color);
}

.section-header {
    margin-bottom: 2rem;
    position: relative;
}

.section-title {
    color: var(--primary-color);
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.section-accent {
    height: 4px;
    background: var(--gradient-secondary);
    border-radius: 2px;
    width: 80px;
}

.team-showcase {
    margin-top: 3rem;
    padding: 3rem 2rem;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 16px;
    text-align: center;
}

.team-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.team-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.team-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(0,0,0,0.15);
}

.member-avatar {
    width: 80px;
    height: 80px;
    background: var(--gradient-primary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1.5rem;
    font-size: 2rem;
    color: white;
}

.team-card h4 {
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}

.member-title {
    color: var(--secondary-color);
    font-weight: 600;
}

@media (max-width: 1024px) {
    .floating-nav {
        display: none;
    }
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 2rem;
    }

    .team-grid {
        grid-template-columns: 1fr;
    }
}'''

    def _get_professional_classic_css(self) -> str:
        """Professional classic CSS"""
        return '''/* Professional Classic Styles */
:root {
    --primary-color: #1B5E20;
    --secondary-color: #37474F;
    --accent-color: #388E3C;
    --background-color: #FFFEF7;
    --text-color: #263238;
    --border-color: #CFD8DC;
    --paper-color: #FFFFFF;
}

body {
    background: var(--background-color);
    font-family: 'Georgia', serif;
}

.document-header-classic {
    text-align: center;
    padding: 3rem 0;
    border-bottom: 2px solid var(--border-color);
    margin-bottom: 2rem;
}

.document-title {
    color: var(--primary-color);
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.document-meta {
    display: flex;
    justify-content: center;
    gap: 2rem;
    color: var(--secondary-color);
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.toc-classic {
    background: var(--paper-color);
    border: 1px solid var(--border-color);
    padding: 2rem;
    margin-bottom: 3rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.toc-classic h2 {
    color: var(--primary-color);
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
}

.toc-list {
    list-style: none;
}

.toc-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px dotted var(--border-color);
}

.toc-item:last-child {
    border-bottom: none;
}

.toc-item a {
    color: var(--text-color);
    text-decoration: none;
    font-weight: 500;
}

.toc-item a:hover {
    color: var(--accent-color);
}

.toc-page {
    color: var(--secondary-color);
    font-weight: 400;
}

.document-content-classic {
    background: var(--paper-color);
    padding: 3rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.section-classic {
    margin-bottom: 2.5rem;
    text-align: justify;
}

.section-title-classic {
    color: var(--primary-color);
    font-size: 1.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid var(--accent-color);
    padding-left: 1rem;
}

.section-content-classic {
    line-height: 1.8;
    text-align: justify;
    text-indent: 2em;
    margin-bottom: 1em;
}

.section-content-classic p:first-of-type {
    text-indent: 0;
}

.team-classic {
    background: var(--paper-color);
    padding: 3rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.team-classic h2 {
    color: var(--primary-color);
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.5rem;
    margin-bottom: 2rem;
}

.team-list-classic {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.team-member-classic {
    padding: 1.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--background-color);
}

.team-member-classic h4 {
    color: var(--primary-color);
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
}

.member-title-classic {
    color: var(--secondary-color);
    font-style: italic;
    margin-bottom: 0.5rem;
}

.member-experience {
    color: var(--text-color);
    font-size: 0.9rem;
    line-height: 1.5;
}

@media (max-width: 768px) {
    .document-meta {
        flex-direction: column;
        gap: 0.5rem;
    }

    .document-content-classic,
    .team-classic,
    .toc-classic {
        padding: 2rem;
    }

    .team-list-classic {
        grid-template-columns: 1fr;
    }
}'''

    def _get_creative_minimal_css(self) -> str:
        """Creative minimal CSS"""
        return '''/* Creative Minimal Styles */
:root {
    --primary-color: #9C27B0;
    --secondary-color: #616161;
    --accent-color: #E1BEE7;
    --background-color: #FFFFFF;
    --text-color: #212121;
    --light-gray: #FAFAFA;
    --border-color: #E0E0E0;
}

body {
    font-family: 'Inter', sans-serif;
    font-weight: 300;
    background: var(--background-color);
    color: var(--text-color);
}

.title-minimal {
    text-align: center;
    margin-bottom: 4rem;
}

.title-minimal h1 {
    font-size: 2.5rem;
    font-weight: 200;
    letter-spacing: 0.1em;
    color: var(--text-color);
    margin-bottom: 1rem;
}

.title-line {
    width: 100px;
    height: 2px;
    background: var(--primary-color);
    margin: 0 auto;
}

.content-minimal {
    max-width: 800px;
    margin: 0 auto;
}

.section-minimal {
    margin-bottom: 4rem;
}

.section-title-minimal {
    font-size: 1.8rem;
    font-weight: 300;
    letter-spacing: 0.05em;
    color: var(--primary-color);
    margin-bottom: 2rem;
    text-align: center;
}

.section-content-minimal {
    font-size: 1.1rem;
    line-height: 1.8;
    color: var(--text-color);
    text-align: center;
    max-width: 600px;
    margin: 0 auto;
}

.section-content-minimal p {
    margin-bottom: 1.5rem;
}

.team-minimal {
    padding: 3rem 0;
    text-align: center;
}

.team-minimal-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 3rem;
    max-width: 600px;
    margin: 0 auto;
}

.team-member-minimal {
    text-align: center;
}

.team-member-minimal h3 {
    font-weight: 400;
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}

.team-member-minimal p {
    color: var(--secondary-color);
    font-size: 0.9rem;
}

.document-header {
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 2rem;
    margin-bottom: 3rem;
    text-align: center;
}

.company-name {
    font-weight: 200;
    letter-spacing: 0.1em;
}

.document-footer {
    border-top: 1px solid var(--border-color);
    padding-top: 2rem;
    margin-top: 4rem;
    text-align: center;
    color: var(--secondary-color);
    font-size: 0.9rem;
}

@media (max-width: 768px) {
    .title-minimal h1 {
        font-size: 2rem;
    }

    .section-content-minimal {
        font-size: 1rem;
    }

    .team-minimal-grid {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
}'''

    def _get_financial_report_css(self) -> str:
        """Financial report CSS"""
        return '''/* Financial Report Styles */
:root {
    --primary-color: #388E3C;
    --secondary-color: #455A64;
    --accent-color: #4CAF50;
    --background-color: #FFFFFF;
    --text-color: #212121;
    --light-gray: #F5F5F5;
    --border-color: #E0E0E0;
    --success-color: #4CAF50;
    --warning-color: #FF9800;
    --error-color: #F44336;
}

body {
    font-family: 'Roboto', sans-serif;
    background: var(--background-color);
    color: var(--text-color);
}

.financial-header {
    background: var(--light-gray);
    border-bottom: 3px solid var(--primary-color);
    padding: 2rem;
    margin-bottom: 2rem;
    text-align: center;
}

.financial-header h1 {
    color: var(--primary-color);
    font-size: 2rem;
    margin-bottom: 1rem;
    font-weight: 500;
}

.financial-meta {
    display: flex;
    justify-content: center;
    gap: 2rem;
    font-size: 0.9rem;
    color: var(--secondary-color);
}

.financial-nav {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
}

.financial-nav h3 {
    color: var(--primary-color);
    margin-bottom: 1rem;
    font-weight: 500;
}

.financial-nav ul {
    list-style: none;
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.financial-nav li {
    padding: 0.5rem 1rem;
    background: var(--light-gray);
    border-radius: 20px;
}

.financial-nav a {
    color: var(--text-color);
    text-decoration: none;
    font-weight: 500;
}

.financial-nav a:hover {
    color: var(--primary-color);
}

.financial-content {
    max-width: 1000px;
    margin: 0 auto;
}

.financial-section {
    margin-bottom: 3rem;
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.financial-section h2 {
    color: var(--primary-color);
    border-bottom: 2px solid var(--accent-color);
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
    font-weight: 500;
}

.financial-content-text {
    line-height: 1.7;
    text-align: justify;
}

.financial-content-text p {
    margin-bottom: 1rem;
}

.financial-report-table {
    margin-bottom: 2rem;
}

.financial-report-table h3 {
    color: var(--secondary-color);
    margin-bottom: 1rem;
    font-weight: 500;
}

.table-container {
    overflow-x: auto;
    border: 1px solid var(--border-color);
    border-radius: 8px;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
}

.data-table th {
    background: var(--primary-color);
    color: white;
    padding: 1rem;
    text-align: left;
    font-weight: 500;
    font-size: 0.9rem;
}

.data-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-color);
    font-size: 0.9rem;
}

.data-table tr:hover {
    background: var(--light-gray);
}

.data-table tr:last-child td {
    border-bottom: none;
}

/* Status indicators */
.status-draft {
    background: #FFF3E0;
    color: #F57C00;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
}

.status-final {
    background: #E8F5E8;
    color: #2E7D32;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
}

.status-review {
    background: #E3F2FD;
    color: #1976D2;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
}

/* Print optimizations */
@media print {
    .financial-nav {
        display: none;
    }

    .financial-section {
        break-inside: avoid;
        box-shadow: none;
        border: 1px solid var(--border-color);
    }

    .data-table {
        page-break-inside: avoid;
    }
}

@media (max-width: 768px) {
    .financial-meta {
        flex-direction: column;
        gap: 0.5rem;
    }

    .financial-nav ul {
        flex-direction: column;
        gap: 0.5rem;
    }

    .financial-section {
        padding: 1rem;
    }

    .data-table th,
    .data-table td {
        padding: 0.5rem;
        font-size: 0.8rem;
    }
}'''