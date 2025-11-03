"""
Simple test script for the Document Transformer system
Tests core functionality without external dependencies
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_parser():
    """Test the markdown parser"""
    print("🧪 Testing Markdown Parser")
    print("="*50)

    try:
        from src.config.settings import Config
        from src.parser import MarkdownParser

        config = Config()
        parser = MarkdownParser(config)

        # Test with VeloCity investor teaser
        test_file = Path("../companies/VeloCity/projects/VeloCity/workspace/funding-docs/INVESTOR_TEASER.md")
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return False

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

        # Show first few sections
        if document.sections:
            print(f"\n📑 First 3 sections:")
            for i, section in enumerate(document.sections[:3], 1):
                print(f"  {i}. {section.title} (Level {section.level})")
                print(f"     Content preview: {section.content[:100]}...")

        return True

    except Exception as e:
        print(f"❌ Parser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_brand_system():
    """Test the branding system"""
    print("\n🧪 Testing Brand System")
    print("="*50)

    try:
        from src.branding import BrandProfile, ColorPalette, Typography, DesignStyle

        # Create test brand profile
        test_brand = BrandProfile(
            company_name="TestCompany",
            industry="saas",
            tagline="Innovating the Future",
            design_style=DesignStyle.STARTUP_VIBRANT,
            color_palette=ColorPalette(
                primary=["#6200EA", "#7C4DFF"],
                secondary=["#FF6B6B", "#424242"]
            ),
            typography=Typography(
                heading_font="Inter",
                body_font="Inter"
            )
        )

        print(f"✅ Created brand profile:")
        print(f"  Company: {test_brand.company_name}")
        print(f"  Industry: {test_brand.industry}")
        print(f"  Style: {test_brand.design_style.value}")
        print(f"  Primary Colors: {test_brand.color_palette.primary}")

        return True

    except Exception as e:
        print(f"❌ Brand system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_system():
    """Test the template system"""
    print("\n🧪 Testing Template System")
    print("="*50)

    try:
        from src.templates import TemplateEngine
        from src.branding import BrandProfile, ColorPalette, Typography, DesignStyle
        from src.config.settings import Config

        config = Config()
        template_engine = TemplateEngine(Path(__file__).parent / "src" / "templates")

        available_templates = template_engine.list_templates()
        print(f"✅ Available templates: {available_templates}")

        # Create a test brand profile
        test_brand = BrandProfile(
            company_name="VeloCity",
            industry="telecom",
            design_style=DesignStyle.MODERN_CORPORATE,
            color_palette=ColorPalette(primary=["#1976D2", "#2196F3"]),
            typography=Typography(heading_font="Inter", body_font="Inter")
        )

        return True

    except Exception as e:
        print(f"❌ Template system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_html_generator():
    """Test HTML generator without external dependencies"""
    print("\n🧪 Testing HTML Generator")
    print("="*50)

    try:
        from src.config.settings import Config
        from src.parser import MarkdownParser
        from src.templates import TemplateEngine
        from src.branding import BrandProfile, ColorPalette, Typography, DesignStyle

        config = Config()
        parser = MarkdownParser(config)
        template_engine = TemplateEngine(Path(__file__).parent / "src" / "templates")

        # Parse a simple test document
        test_file = Path("../companies/VeloCity/projects/VeloCity/workspace/funding-docs/INVESTOR_TEASER.md")
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return False

        document = parser.parse_file(test_file)

        # Create brand profile
        brand_profile = BrandProfile(
            company_name="VeloCity",
            industry="telecom",
            design_style=DesignStyle.MODERN_CORPORATE,
            color_palette=ColorPalette(primary=["#1976D2", "#2196F3"]),
            typography=Typography(heading_font="Inter", body_font="Inter")
        )

        # Get template for document
        template_config = template_engine.get_template_for_document(document, brand_profile)
        print(f"✅ Selected template: {template_config.name}")

        # Test rendering (without saving file)
        rendered_content = template_engine.render_document(document, brand_profile, template_config)
        print(f"✅ Rendered {len(rendered_content)} characters of HTML")

        return True

    except Exception as e:
        print(f"❌ HTML generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_simple_tests():
    """Run simple tests"""
    print("🚀 Running Simple Document Transformer Tests")
    print("="*60)

    results = []
    results.append(test_parser())
    results.append(test_brand_system())
    results.append(test_template_system())
    results.append(test_html_generator())

    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️ {total - passed} test(s) failed")

    return passed == total

if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)