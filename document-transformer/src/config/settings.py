"""
Configuration settings for the Document Transformer
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

class Config:
    """Main configuration class for the document transformer"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.src_dir = self.base_dir / "src"
        self.templates_dir = self.base_dir / "src" / "templates"
        self.assets_dir = self.base_dir / "assets"
        self.outputs_dir = self.base_dir / "outputs"
        self.brand_profiles_dir = self.base_dir / "brand-profiles"
        self.companies_dir = self.base_dir.parent / "companies"

        # Output directories
        self.html_output = self.outputs_dir / "html"
        self.pdf_output = self.outputs_dir / "pdf"
        self.pptx_output = self.outputs_dir / "presentations"
        self.docx_output = self.outputs_dir / "documents"

        # Ensure output directories exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for dir_path in [self.outputs_dir, self.html_output, self.pdf_output,
                        self.pptx_output, self.docx_output, self.brand_profiles_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    # Document type detection patterns
    DOCUMENT_TYPES = {
        'investor_teaser': {
            'keywords': ['teaser', 'investment', 'funding', 'pitch', 'elevator'],
            'sections': ['problem', 'solution', 'market', 'team', 'ask'],
            'max_length': 2000  # characters
        },
        'pitch_deck': {
            'keywords': ['pitch', 'deck', 'presentation', 'slides'],
            'sections': ['problem', 'solution', 'market size', 'business model', 'team', 'traction'],
            'max_length': 3000
        },
        'financial_projections': {
            'keywords': ['financial', 'projections', 'revenue', 'expenses', 'forecast', 'model'],
            'sections': ['revenue', 'expenses', 'profit', 'cash flow', 'assumptions'],
            'has_tables': True
        },
        'business_plan': {
            'keywords': ['business plan', 'strategy', 'operations', 'planning'],
            'sections': ['executive summary', 'company description', 'market analysis', 'organization', 'products', 'marketing', 'financials'],
            'max_length': 10000
        },
        'market_research': {
            'keywords': ['market research', 'analysis', 'competition', 'industry', 'trends'],
            'sections': ['market size', 'competition', 'trends', 'opportunities', 'threats'],
            'has_tables': True
        },
        'company_overview': {
            'keywords': ['company', 'about', 'overview', 'profile'],
            'sections': ['mission', 'vision', 'history', 'leadership', 'operations']
        }
    }

    # Industry-specific themes
    INDUSTRY_THEMES = {
        'agritech': {
            'primary_colors': ['#2D5016', '#4A7C28', '#8BC34A', '#689F38'],
            'secondary_colors': ['#795548', '#8D6E63', '#A1887F'],
            'fonts': ['Georgia', 'Arial', 'Verdana'],
            'style': 'natural, earth-tones, organic'
        },
        'telecom': {
            'primary_colors': ['#0D47A1', '#1976D2', '#2196F3', '#64B5F6'],
            'secondary_colors': ['#263238', '#37474F', '#455A64'],
            'fonts': ['Helvetica', 'Arial', 'Roboto'],
            'style': 'professional, technical, corporate blue'
        },
        'saas': {
            'primary_colors': ['#6200EA', '#7C4DFF', '#9C27B0', '#BA68C8'],
            'secondary_colors': ['#424242', '#616161', '#757575'],
            'fonts': ['Inter', 'Roboto', 'Open Sans'],
            'style': 'modern, gradient, minimalist'
        },
        'finance': {
            'primary_colors': ['#1B5E20', '#388E3C', '#4CAF50', '#81C784'],
            'secondary_colors': ['#263238', '#455A64', '#546E7A'],
            'fonts': ['Times New Roman', 'Georgia', 'Arial'],
            'style': 'conservative, trustworthy, traditional'
        },
        'healthcare': {
            'primary_colors': ['#006064', '#00838F', '#0097A7', '#00ACC1'],
            'secondary_colors': ['#37474F', '#455A64', '#546E7A'],
            'fonts': ['Calibri', 'Arial', 'Segoe UI'],
            'style': 'clean, medical, professional'
        },
        'retail': {
            'primary_colors': ['#D32F2F', '#F44336', '#E91E63', '#EC407A'],
            'secondary_colors': ['#424242', '#616161', '#757575'],
            'fonts': ['Montserrat', 'Roboto', 'Lato'],
            'style': 'bold, consumer-focused, dynamic'
        }
    }

    # Template configurations
    TEMPLATES = {
        'modern_corporate': {
            'description': 'Clean, professional design for modern businesses',
            'layout': 'single-column, header, footer',
            'typography': 'serif headings, sans-serif body',
            'colors': 'neutral palette with accent color'
        },
        'startup_vibrant': {
            'description': 'Energetic design for startups and tech companies',
            'layout': 'asymmetric, bold elements',
            'typography': 'sans-serif, bold weights',
            'colors': 'vibrant gradients, bold contrasts'
        },
        'professional_classic': {
            'description': 'Traditional design for established companies',
            'layout': 'formal, structured grid',
            'typography': 'serif, traditional',
            'colors': 'conservative blues and grays'
        },
        'creative_minimal': {
            'description': 'Minimalist design for creative industries',
            'layout': 'white space focused, clean lines',
            'typography': 'light weights, generous spacing',
            'colors': 'monochromatic with single accent'
        }
    }

    # Quality thresholds
    QUALITY_THRESHOLDS = {
        'min_content_length': 500,  # characters
        'max_image_size_mb': 5,
        'max_page_count': 50,
        'min_font_size': 10,  # points
        'max_font_size': 72,
        'required_sections': ['introduction', 'conclusion']
    }

    @property
    def supported_formats(self) -> List[str]:
        """Return list of supported output formats"""
        return ['html', 'pdf', 'pptx', 'docx']

    def get_industry_theme(self, industry: str) -> Dict:
        """Get industry-specific theme configuration"""
        return self.INDUSTRY_THEMES.get(industry.lower(), self.INDUSTRY_THEMES['saas'])

    def get_document_type(self, keywords: List[str], content: str, has_tables: bool = False) -> str:
        """Determine document type based on keywords and content analysis"""
        scores = {}

        for doc_type, config in self.DOCUMENT_TYPES.items():
            score = 0
            content_lower = content.lower()

            # Check keyword matches
            for keyword in keywords:
                if keyword in content_lower:
                    score += config['keywords'].count(keyword) * 2

            # Check section matches
            for section in config.get('sections', []):
                if section in content_lower:
                    score += 1

            # Check for tables if relevant
            if has_tables and config.get('has_tables', False):
                score += 2

            # Check content length
            if 'max_length' in config:
                if len(content) <= config['max_length']:
                    score += 1

            scores[doc_type] = score

        # Return document type with highest score
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return 'business_plan'  # default fallback