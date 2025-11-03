# 🎨 Document Transformer

Transform your business markdown documents into beautiful, professionally branded documents in multiple formats.

## ✨ Features

### 🎯 Core Capabilities
- **Intelligent Document Parsing**: Automatically detects document types (investor teasers, pitch decks, business plans, etc.)
- **Industry-Specific Branding**: Pre-configured themes for different industries (AgriTech, Telecom, SaaS, Finance, etc.)
- **Multi-Format Export**: HTML, PDF, PowerPoint, and Word document generation
- **Batch Processing**: Process multiple documents and companies simultaneously
- **Template System**: Dynamic templates with professional styling

### 🏢 Industry Themes
- **AgriTech**: Natural, earth-toned designs
- **Telecom**: Professional, corporate blue themes
- **SaaS**: Modern, gradient-based designs
- **Finance**: Conservative, traditional styling
- **Healthcare**: Clean, medical-focused design
- **Retail**: Bold, consumer-oriented themes

### 📄 Output Formats
- **HTML**: Responsive web documents with interactive elements
- **PDF**: Print-optimized professional documents
- **PowerPoint**: Slide decks for presentations
- **Word**: Editable documents for further customization

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the document transformer directory
cd document-transformer

# Install dependencies
pip install -r requirements.txt

# Initialize the system
python main.py init
```

### 2. Create a Brand Profile

```bash
# Create a brand profile for your company
python main.py brand

# Or create for a specific company
python main.py brand --company "YourCompanyName"
```

The interactive questionnaire will guide you through:
- Company information and industry
- Design style preferences
- Color scheme selection
- Typography choices
- Logo and branding assets

### 3. Transform a Single Document

```bash
# Basic transformation
python main.py transform path/to/document.md

# Specify formats and company
python main.py transform document.md --company "YourCompany" --formats html pdf

# Custom output directory
python main.py transform document.md --output-dir ./outputs
```

### 4. Batch Process Documents

```bash
# Process all documents in a directory
python main.py batch ./documents --company "YourCompany"

# Multiple formats with parallel processing
python main.py batch ./documents --formats html pdf pptx --workers 4

# Recursive processing of subdirectories
python main.py batch ./companies --recursive
```

## 📋 Commands Reference

### `transform` - Single Document Processing
```bash
python main.py transform INPUT_FILE [OPTIONS]

Options:
  -c, --company TEXT     Company name for branding
  -f, --formats TEXT     Output formats (html, pdf, pptx, docx)
  -o, --output-dir PATH  Output directory
  -t, --template TEXT    Template to use
  --create-brand         Create new brand profile
```

### `batch` - Bulk Processing
```bash
python main.py batch DIRECTORY [OPTIONS]

Options:
  -c, --company TEXT     Company name for branding
  -f, --formats TEXT     Output formats
  -o, --output-dir PATH  Output directory
  -w, --workers INTEGER  Number of parallel workers
  -r, --recursive        Process subdirectories
  --create-brand         Create new brand profile
```

### `brand` - Brand Management
```bash
python main.py brand [OPTIONS]

Options:
  -c, --company TEXT     Company name (creates profile for specific company)
```

### `analyze` - Document Analysis
```bash
python main.py analyze INPUT_FILE

Analyzes a document without generating output:
- Document type detection
- Section analysis
- Content summary
- Metadata extraction
```

### `list-brands` - View Available Brands
```bash
python main.py list-brands

Lists all saved brand profiles
```

## 🏗️ Architecture

### Core Components

#### 📖 Parser (`src/parser/`)
- **MarkdownParser**: Intelligent parsing with content type detection
- **Content Extraction**: Sections, financial data, team information, tables
- **Metadata Analysis**: Automatic document classification

#### 🎨 Branding (`src/branding/`)
- **BrandProfile**: Complete brand configuration
- **BrandQuestionnaire**: Interactive brand creation
- **Industry Themes**: Pre-configured styling by industry

#### 📄 Templates (`src/templates/`)
- **TemplateEngine**: Dynamic template selection and rendering
- **Built-in Templates**: Modern Corporate, Startup Vibrant, Professional Classic, etc.
- **Jinja2-based**: Flexible template system with custom filters

#### 🔧 Generators (`src/generators/`)
- **HTMLGenerator**: Responsive web documents with CSS
- **PDFGenerator**: Print-optimized PDF generation
- **PowerPointGenerator**: Professional slide decks
- **WordGenerator**: Editable Word documents

#### ⚡ Batch Processing (`src/batch/`)
- **BatchProcessor**: Parallel document processing
- **Job Queue**: Priority-based job management
- **Progress Tracking**: Real-time processing status

## 🎯 Document Types Supported

### 📊 Business Documents
- **Investor Teasers**: One-page investment summaries
- **Pitch Decks**: Full presentation materials
- **Business Plans**: Comprehensive planning documents
- **Financial Projections**: Financial data and forecasts
- **Market Research**: Industry analysis and competitive insights
- **Company Overviews**: Corporate profiles and information

### 🔍 Automatic Detection
The system automatically identifies document types based on:
- Content keywords and patterns
- Document structure
- Section organization
- Financial data presence

## 🎨 Customization Options

### Brand Profiles
Each company can have a unique brand profile including:
- **Colors**: Primary, secondary, accent colors
- **Typography**: Heading and body fonts
- **Layout**: Margins, spacing, sizing
- **Assets**: Logos, brand images

### Templates
Multiple built-in templates:
- **Modern Corporate**: Clean, professional design
- **Startup Vibrant**: Energetic, tech-focused
- **Professional Classic**: Traditional, established
- **Creative Minimal**: Minimalist, artistic
- **Financial Report**: Optimized for data tables

### Output Customization
- **PDF Options**: Page size, margins, print optimization
- **HTML**: Responsive design, interactive elements
- **PowerPoint**: Slide layouts, visual elements
- **Word**: Document formatting, styles

## 📊 Use Cases

### 🏢 For Companies
- **Investor Materials**: Professional pitch documents
- **Client Presentations**: Branded marketing materials
- **Internal Reports**: Consistent corporate documentation
- **Regulatory Documents**: Professional compliance materials

### 💼 For Consultants
- **Client Deliverables**: Professional branded reports
- **Proposals**: Consistent proposal formatting
- **Case Studies**: Professional presentation of work
- **Documentation**: Standardized document creation

### 🎓 For Educational Institutions
- **Course Materials**: Professional educational content
- **Research Papers**: Academic document formatting
- **Student Projects**: Professional presentation
- **Administrative Documents**: Consistent formatting

## 🔧 Technical Details

### Dependencies
```bash
# Core dependencies
markdown>=3.5.1          # Markdown parsing
jinja2>=3.1.2           # Template engine
click>=8.1.7             # CLI interface

# HTML/CSS generation
weasyprint>=60.0         # PDF generation (optional)

# PowerPoint generation
python-pptx>=0.6.22      # PowerPoint files

# Word document generation
python-docx>=0.8.11     # Word documents

# Data visualization
matplotlib>=3.7.0       # Charts and graphs
plotly>=5.17.0          # Interactive charts

# Configuration and utilities
pyyaml>=6.0.1           # YAML configuration
rich>=13.6.0            # Terminal output
colorama>=0.4.6         # Cross-platform colors
```

### File Structure
```
document-transformer/
├── src/
│   ├── config/          # Configuration settings
│   ├── parser/          # Markdown parsing
│   ├── branding/        # Brand management
│   ├── templates/       # Template engine
│   ├── generators/      # Output generators
│   └── batch/          # Batch processing
├── outputs/             # Generated documents
├── brand-profiles/      # Saved brand profiles
├── requirements.txt     # Dependencies
└── main.py             # CLI interface
```

## 🐛 Troubleshooting

### Common Issues

#### Installation Problems
```bash
# If WeasyPrint fails to install
pip install --upgrade pip
pip install --upgrade setuptools
pip install -r requirements.txt
```

#### Encoding Issues
- **Windows**: Use Python 3.8+ and ensure UTF-8 encoding
- **File Names**: Avoid special characters in document names
- **Content**: Remove problematic emoji characters from markdown

#### Memory Issues
- **Large Documents**: Process in smaller batches
- **Parallel Processing**: Reduce worker count (`--workers 2`)
- **Complex Templates**: Use simpler templates for large documents

### Performance Optimization

#### For Large Numbers of Documents
```bash
# Optimize batch processing
python main.py batch ./documents \
  --workers 2 \
  --formats html pdf \
  --output-dir ./outputs
```

#### For Large Documents
- Use simpler templates
- Limit the number of formats generated
- Process documents individually first to test

## 📄 License

This project is part of the Innov8 workspace and is intended for internal business use.

## 🤝 Support

For support and questions:
1. Check this README for common issues
2. Run `python main.py analyze document.md` to diagnose document issues
3. Use `python main.py list-brands` to verify brand profiles
4. Check the logs in `outputs/logs/` for detailed error information

---

**Created by**: AI Document Transformer Team
**Version**: 1.0.0
**Last Updated**: 2025-11-02