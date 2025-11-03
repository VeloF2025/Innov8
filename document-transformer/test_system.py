"""
Test script for the Document Transformer system
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import Config
from src.parser import MarkdownParser
from src.branding import BrandProfile, ColorPalette, Typography, DesignStyle, BrandProfileManager
from src.templates import TemplateEngine
from src.generators.html_generator import HTMLGenerator
from src.batch import BatchProcessor, BatchConfiguration

def test_single_document():
    """Test processing a single document"""
    print("🧪 Testing Single Document Processing")
    print("="*50)

    # Initialize components
    config = Config()
    parser = MarkdownParser(config)

    # Test with VeloCity investor teaser
    test_file = Path("../companies/VeloCity/projects/VeloCity/workspace/funding-docs/INVESTOR_TEASER.md")
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return

    print(f"📄 Parsing: {test_file.name}")
    document = parser.parse_file(test_file)

    print(f"✅ Parsed Document:")
    print(f"  Title: {document.metadata.title}")
    print(f"  Company: {document.metadata.company_name}")
    print(f"  Type: {document.metadata.document_type}")
    print(f"  Industry: {document.metadata.industry}")
    print(f"  Sections: {len(document.sections)}")
    print(f"  Financial Data: {len(document.financial_data)}")
    print(f"  Team Members: {len(document.team_members)}")
    print(f"  Tables: {len(document.tables)}")

    # Create a default brand profile
    brand_profile = BrandProfile(
        company_name=document.metadata.company_name or "VeloCity",
        industry=document.metadata.industry or "telecom",
        design_style=DesignStyle.MODERN_CORPORATE,
        color_palette=ColorPalette(
            primary=["#1976D2", "#2196F3"],
            secondary=["#424242", "#757575"]
        ),
        typography=Typography(
            heading_font="Inter",
            body_font="Inter"
        )
    )

    # Test HTML generation
    print("\n🔄 Testing HTML Generation...")
    try:
        template_engine = TemplateEngine(Path(__file__).parent / "src" / "templates")
        html_generator = HTMLGenerator(template_engine, Path(__file__).parent / "outputs" / "test_html")

        output_path = html_generator.generate_html(document, brand_profile)
        print(f"✅ HTML generated: {output_path}")
    except Exception as e:
        print(f"❌ HTML generation failed: {e}")
        import traceback
        traceback.print_exc()

def test_brand_profiles():
    """Test brand profile creation and management"""
    print("\n🧪 Testing Brand Profiles")
    print("="*50)

    brand_manager = BrandProfileManager(Path(__file__).parent / "brand-profiles")

    # Create test brand profile
    test_brand = BrandProfile(
        company_name="TestCompany",
        industry="saas",
        tagline="Innovating the Future",
        design_style=DesignStyle.STARTUP_VIBRANT,
        color_palette=ColorPalette(
            primary=["#6200EA", "#7C4DFF"],
            secondary=["#FF6B6B", "#424242"]
        )
    )

    # Save and load
    try:
        profile_path = brand_manager.save_profile(test_brand)
        print(f"✅ Brand profile saved: {profile_path}")

        loaded_profile = brand_manager.load_profile("TestCompany")
        if loaded_profile:
            print(f"✅ Brand profile loaded: {loaded_profile.company_name}")
        else:
            print("❌ Failed to load brand profile")
    except Exception as e:
        print(f"❌ Brand profile test failed: {e}")

def test_template_engine():
    """Test template engine functionality"""
    print("\n🧪 Testing Template Engine")
    print("="*50)

    try:
        template_engine = TemplateEngine(Path(__file__).parent / "src" / "templates")

        available_templates = template_engine.list_templates()
        print(f"✅ Available templates: {available_templates}")

        for template_name in available_templates[:3]:  # Test first 3 templates
            template_info = template_engine.get_template_info(template_name)
            print(f"  • {template_name}: {template_info.description}")

    except Exception as e:
        print(f"❌ Template engine test failed: {e}")

def test_batch_processor():
    """Test batch processor initialization"""
    print("\n🧪 Testing Batch Processor")
    print("="*50)

    try:
        base_dir = Path(__file__).parent
        batch_config = BatchConfiguration(max_workers=2)
        batch_processor = BatchProcessor(base_dir, batch_config)

        print("✅ Batch processor initialized successfully")
        print(f"  Output directories: {list(batch_processor.output_dirs.keys())}")

    except Exception as e:
        print(f"❌ Batch processor test failed: {e}")

def run_all_tests():
    """Run all tests"""
    print("🚀 Running Document Transformer Tests")
    print("="*60)

    test_single_document()
    test_brand_profiles()
    test_template_engine()
    test_batch_processor()

    print("\n" + "="*60)
    print("🎉 Testing Complete!")

if __name__ == "__main__":
    run_all_tests()