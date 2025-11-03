"""
Document Transformer - Main CLI Interface
Transform business markdown documents into beautiful, professionally branded documents
"""

import click
import sys
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import Config
from src.parser import MarkdownParser
from src.branding import BrandQuestionnaire, BrandProfileManager
from src.batch import BatchProcessor, BatchConfiguration

# Initialize base directory
BASE_DIR = Path(__file__).parent
config = Config()

@click.group()
@click.version_option(version="1.0.0", prog_name="Document Transformer")
@click.pass_context
def cli(ctx):
    """🎨 Document Transformer - Convert markdown business documents to beautiful branded documents"""
    ctx.ensure_object(dict)
    ctx.obj['base_dir'] = BASE_DIR
    ctx.obj['config'] = config

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--company', '-c', help='Company name for branding')
@click.option('--formats', '-f', multiple=True, default=['html', 'pdf'],
              type=click.Choice(['html', 'pdf', 'pptx', 'docx']),
              help='Output formats to generate')
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory')
@click.option('--template', '-t', help='Template to use')
@click.option('--create-brand', is_flag=True, help='Create new brand profile')
@click.pass_context
def transform(ctx, input_file, company, formats, output_dir, template, create_brand):
    """Transform a single markdown document"""

    base_dir = ctx.obj['base_dir']

    # Setup components
    parser = MarkdownParser(config)

    # Parse document
    click.echo(f"📄 Parsing {input_file}...")
    document = parser.parse_file(Path(input_file))
    click.echo(f"✅ Parsed: {document.metadata.title} ({document.metadata.document_type})")

    # Handle branding
    brand_manager = BrandProfileManager(base_dir / "brand-profiles")

    if create_brand or not company:
        # Run questionnaire
        click.echo("🎨 Creating brand profile...")
        questionnaire = BrandQuestionnaire(config)
        brand_profile = questionnaire.run_interactive()
        brand_manager.save_profile(brand_profile)
        click.echo(f"✅ Saved brand profile for {brand_profile.company_name}")
    else:
        # Load existing profile
        brand_profile = brand_manager.load_profile(company)
        if not brand_profile:
            click.echo(f"❌ No brand profile found for '{company}'. Use --create-brand to create one.")
            return

    # Import generators
    from src.templates import TemplateEngine
    from src.generators.html_generator import HTMLGenerator
    from src.generators.pdf_generator import PDFGenerator
    from src.generators.pptx_generator import PowerPointGenerator
    from src.generators.docx_generator import WordGenerator

    # Setup template engine and generators
    templates_dir = base_dir / "src" / "templates"
    template_engine = TemplateEngine(templates_dir)

    # Set output directory
    output_dir = Path(output_dir) if output_dir else base_dir / "outputs"

    # Generate documents
    for format_type in formats:
        click.echo(f"🔄 Generating {format_type.upper()}...")

        try:
            if format_type == 'html':
                generator = HTMLGenerator(template_engine, output_dir / "html")
                output_path = generator.generate_html(document, brand_profile)
            elif format_type == 'pdf':
                generator = PDFGenerator(template_engine, output_dir / "pdf")
                output_path = generator.generate_pdf(document, brand_profile)
            elif format_type == 'pptx':
                generator = PowerPointGenerator(template_engine, output_dir / "presentations")
                output_path = generator.generate_presentation(document, brand_profile)
            elif format_type == 'docx':
                generator = WordGenerator(template_engine, output_dir / "documents")
                output_path = generator.generate_document(document, brand_profile)

            click.echo(f"✅ {format_type.upper()}: {output_path}")

        except Exception as e:
            click.echo(f"❌ Error generating {format_type}: {e}")

    click.echo("🎉 Transformation complete!")

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--company', '-c', help='Company name for branding')
@click.option('--formats', '-f', multiple=True, default=['html', 'pdf'],
              type=click.Choice(['html', 'pdf', 'pptx', 'docx']),
              help='Output formats to generate')
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory')
@click.option('--workers', '-w', default=4, help='Number of parallel workers')
@click.option('--recursive', '-r', is_flag=True, help='Process subdirectories recursively')
@click.option('--create-brand', is_flag=True, help='Create new brand profile')
@click.pass_context
def batch(ctx, directory, company, formats, output_dir, workers, recursive, create_brand):
    """Process multiple documents in batch"""

    base_dir = ctx.obj['base_dir']

    # Handle branding
    brand_manager = BrandProfileManager(base_dir / "brand-profiles")
    brand_profile = None

    if create_brand or not company:
        click.echo("🎨 Creating brand profile...")
        questionnaire = BrandQuestionnaire(config)
        brand_profile = questionnaire.run_interactive()
        brand_manager.save_profile(brand_profile)
        company = brand_profile.company_name
    else:
        brand_profile = brand_manager.load_profile(company)
        if not brand_profile:
            click.echo(f"❌ No brand profile found for '{company}'. Use --create-brand to create one.")
            return

    # Setup batch processor
    batch_config = BatchConfiguration(
        max_workers=workers,
        output_directory=Path(output_dir) if output_dir else base_dir / "outputs",
        create_index_pages=True,
        create_summary_document=True
    )

    batch_processor = BatchProcessor(base_dir, batch_config)

    # Add jobs
    click.echo(f"📂 Adding jobs from {directory}...")
    jobs = batch_processor.add_batch_from_directory(
        Path(directory),
        formats=list(formats),
        brand_profile=brand_profile,
        recursive=recursive
    )

    click.echo(f"✅ Added {len(jobs)} jobs")

    # Process jobs
    click.echo("🚀 Starting batch processing...")

    def progress_callback(job, status):
        if status == "completed":
            click.echo(f"✅ Completed: {job.input_path.name}")
        elif status == "failed":
            click.echo(f"❌ Failed: {job.input_path.name} - {job.error_message}")

    batch_processor.config.progress_callback = progress_callback

    # Process all jobs
    results = batch_processor.process_all_jobs()

    # Display summary
    click.echo("\n" + "="*50)
    click.echo("📊 PROCESSING SUMMARY")
    click.echo("="*50)
    click.echo(f"Total jobs: {results['total_jobs']}")
    click.echo(f"Completed: {results['completed_jobs']}")
    click.echo(f"Failed: {results['failed_jobs']}")
    click.echo(f"Success rate: {results['success_rate']:.1f}%")
    click.echo(f"Total time: {results['total_processing_time']:.2f} seconds")

    if results['formats_generated']:
        click.echo("\n📄 Formats generated:")
        for format_type, count in results['formats_generated'].items():
            click.echo(f"  {format_type.upper()}: {count}")

    if results['failed_job_details']:
        click.echo("\n❌ Failed jobs:")
        for job_detail in results['failed_job_details'][:5]:  # Show first 5
            click.echo(f"  {Path(job_detail['input_file']).name}: {job_detail['error']}")

        if len(results['failed_job_details']) > 5:
            click.echo(f"  ... and {len(results['failed_job_details']) - 5} more")

    click.echo(f"\n📁 Output directory: {results['output_directories']['base']}")

@cli.command()
@click.option('--company', '-c', help='Company name (creates profile for specific company)')
@click.pass_context
def brand(ctx, company):
    """Create or manage brand profiles"""

    base_dir = ctx.obj['base_dir']
    brand_manager = BrandProfileManager(base_dir / "brand-profiles")

    if company:
        # Load existing profile
        existing_profile = brand_manager.load_profile(company)
        if existing_profile:
            click.echo(f"📋 Brand profile found for {company}:")
            click.echo(f"  Industry: {existing_profile.industry}")
            click.echo(f"  Design Style: {existing_profile.design_style.value}")
            click.echo(f"  Colors: {existing_profile.color_palette.primary}")

            if click.confirm("Do you want to recreate this profile?"):
                pass  # Continue with questionnaire
            else:
                return
        else:
            click.echo(f"📝 Creating new brand profile for {company}...")

    # Run questionnaire
    click.echo("🎨 Let's create your brand profile!")
    questionnaire = BrandQuestionnaire(config)
    brand_profile = questionnaire.run_interactive()

    # Save profile
    profile_path = brand_manager.save_profile(brand_profile)
    click.echo(f"✅ Brand profile saved: {profile_path}")

@cli.command()
def list_brands():
    """List all available brand profiles"""

    base_dir = Path(__file__).parent
    brand_manager = BrandProfileManager(base_dir / "brand-profiles")

    profiles = brand_manager.list_profiles()

    if profiles:
        click.echo("🎨 Available brand profiles:")
        for profile in profiles:
            click.echo(f"  • {profile}")
    else:
        click.echo("❌ No brand profiles found. Use 'brand' command to create one.")

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.pass_context
def analyze(ctx, input_file):
    """Analyze a markdown document without generating output"""

    base_dir = ctx.obj['base_dir']
    parser = MarkdownParser(config)

    click.echo(f"🔍 Analyzing {input_file}...")

    # Parse document
    document = parser.parse_file(Path(input_file))

    # Display analysis
    click.echo("\n" + "="*50)
    click.echo("📋 DOCUMENT ANALYSIS")
    click.echo("="*50)

    click.echo(f"Title: {document.metadata.title or 'Untitled'}")
    click.echo(f"Company: {document.metadata.company_name}")
    click.echo(f"Project: {document.metadata.project}")
    click.echo(f"Type: {document.metadata.document_type}")
    click.echo(f"Industry: {document.metadata.industry}")
    click.echo(f"Author: {document.metadata.author}")
    click.echo(f"Status: {document.metadata.status}")

    click.echo(f"\n📊 Content:")
    click.echo(f"  Sections: {len(document.sections)}")
    click.echo(f"  Financial tables: {len(document.financial_data)}")
    click.echo(f"  Team members: {len(document.team_members)}")
    click.echo(f"  Total tables: {len(document.tables)}")
    click.echo(f"  Images: {len(document.images)}")

    if document.sections:
        click.echo(f"\n📑 Sections:")
        for i, section in enumerate(document.sections[:10], 1):
            click.echo(f"  {i}. {section.title} (Level {section.level})")

        if len(document.sections) > 10:
            click.echo(f"  ... and {len(document.sections) - 10} more sections")

    if document.team_members:
        click.echo(f"\n👥 Team ({len(document.team_members)} members):")
        for member in document.team_members[:5]:
            click.echo(f"  • {member.name} - {member.title}")

@cli.command()
def init():
    """Initialize the document transformer (install dependencies)"""

    click.echo("🚀 Initializing Document Transformer...")

    try:
        # Install dependencies
        import subprocess
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r",
            str(Path(__file__).parent / "requirements.txt")
        ])

        click.echo("✅ Dependencies installed successfully!")
        click.echo("\n🎉 Document Transformer is ready to use!")
        click.echo("\nTry these commands:")
        click.echo("  python main.py brand                    # Create a brand profile")
        click.echo("  python main.py transform file.md       # Transform a document")
        click.echo("  python main.py batch ./documents/      # Process multiple documents")
        click.echo("  python main.py analyze file.md         # Analyze a document")

    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Error installing dependencies: {e}")
        click.echo("Please install manually: pip install -r requirements.txt")

if __name__ == '__main__':
    cli()