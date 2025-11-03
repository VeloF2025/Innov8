"""
Batch Processing System for Document Transformation
Handles bulk processing of multiple documents and companies
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from ..parser import MarkdownParser, ParsedDocument
from ..branding import BrandProfile, BrandProfileManager, BrandQuestionnaire
from ..templates import TemplateEngine
from ..generators.html_generator import HTMLGenerator
from ..generators.pdf_generator import PDFGenerator, PDFOptions
from ..generators.pptx_generator import PowerPointGenerator
from ..generators.docx_generator import WordGenerator, DocumentOptions

@dataclass
class ProcessingJob:
    """Represents a single document processing job"""
    input_path: Path
    output_formats: List[str]
    brand_profile: Optional[BrandProfile] = None
    template_config: Optional[str] = None
    custom_options: Optional[Dict] = None
    priority: int = 0  # Higher number = higher priority
    status: str = "pending"  # pending, processing, completed, failed
    error_message: Optional[str] = None
    output_paths: Dict[str, str] = None
    processing_time: Optional[float] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.output_paths is None:
            self.output_paths = {}
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class BatchConfiguration:
    """Configuration for batch processing"""
    max_workers: int = 4
    output_directory: Optional[Path] = None
    create_index_pages: bool = True
    create_summary_document: bool = True
    log_level: str = "INFO"
    retry_failed_jobs: bool = True
    max_retries: int = 3
    timeout_seconds: int = 300
    progress_callback: Optional[callable] = None

class BatchProcessor:
    """Handles batch processing of multiple documents"""

    def __init__(self, base_dir: Path, config: Optional[BatchConfiguration] = None):
        self.base_dir = base_dir
        self.config = config or BatchConfiguration()

        # Setup output directories
        self.setup_output_directories()

        # Initialize components
        self.parser = MarkdownParser()
        self.template_engine = TemplateEngine(self.base_dir / "src" / "templates")
        self.brand_manager = BrandProfileManager(self.base_dir / "brand-profiles")

        # Initialize generators
        self.html_generator = HTMLGenerator(
            self.template_engine,
            self.output_dirs["html"]
        )
        self.pdf_generator = PDFGenerator(
            self.template_engine,
            self.output_dirs["pdf"],
            self.html_generator
        )
        self.pptx_generator = PowerPointGenerator(
            self.template_engine,
            self.output_dirs["presentations"]
        )
        self.docx_generator = WordGenerator(
            self.template_engine,
            self.output_dirs["documents"]
        )

        # Job tracking
        self.jobs: List[ProcessingJob] = []
        self.processing_stats = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "total_time": 0.0,
            "formats_generated": {}
        }

        # Setup logging
        self.setup_logging()

    def setup_output_directories(self):
        """Setup output directories for different formats"""

        base_output = self.config.output_directory or self.base_dir / "outputs"
        base_output.mkdir(exist_ok=True)

        self.output_dirs = {
            "base": base_output,
            "html": base_output / "html",
            "pdf": base_output / "pdf",
            "presentations": base_output / "presentations",
            "documents": base_output / "documents",
            "logs": base_output / "logs",
            "reports": base_output / "reports"
        }

        # Create directories
        for directory in self.output_dirs.values():
            directory.mkdir(exist_ok=True)

    def setup_logging(self):
        """Setup logging configuration"""

        log_file = self.output_dirs["logs"] / f"batch_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)

    def add_company_processing_job(self, company_path: Path, formats: List[str] = None,
                                 brand_profile: Optional[BrandProfile] = None) -> List[ProcessingJob]:
        """Add processing jobs for all documents in a company"""

        if formats is None:
            formats = ["html", "pdf"]

        jobs = []
        company_name = company_path.name

        # Find all markdown files in the company
        for md_file in self._find_markdown_files(company_path):
            job = ProcessingJob(
                input_path=md_file,
                output_formats=formats,
                brand_profile=brand_profile,
                priority=1
            )
            jobs.append(job)

        self.jobs.extend(jobs)
        self.logger.info(f"Added {len(jobs)} jobs for company: {company_name}")

        return jobs

    def add_document_processing_job(self, document_path: Path, formats: List[str] = None,
                                  brand_profile: Optional[BrandProfile] = None) -> ProcessingJob:
        """Add a single document processing job"""

        if formats is None:
            formats = ["html", "pdf"]

        job = ProcessingJob(
            input_path=document_path,
            output_formats=formats,
            brand_profile=brand_profile,
            priority=2
        )

        self.jobs.append(job)
        self.logger.info(f"Added job for document: {document_path.name}")

        return job

    def add_batch_from_directory(self, directory: Path, formats: List[str] = None,
                               brand_profile: Optional[BrandProfile] = None,
                               recursive: bool = True) -> List[ProcessingJob]:
        """Add processing jobs for all markdown files in a directory"""

        if formats is None:
            formats = ["html", "pdf"]

        jobs = []
        markdown_files = self._find_markdown_files(directory, recursive)

        for md_file in markdown_files:
            job = ProcessingJob(
                input_path=md_file,
                output_formats=formats,
                brand_profile=brand_profile,
                priority=1
            )
            jobs.append(job)

        self.jobs.extend(jobs)
        self.logger.info(f"Added {len(jobs)} jobs from directory: {directory}")

        return jobs

    def process_all_jobs(self) -> Dict[str, Any]:
        """Process all queued jobs"""

        start_time = time.time()
        self.logger.info(f"Starting batch processing of {len(self.jobs)} jobs")

        # Sort jobs by priority
        sorted_jobs = sorted(self.jobs, key=lambda x: x.priority, reverse=True)

        # Process jobs in parallel
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_job = {
                executor.submit(self._process_single_job, job): job
                for job in sorted_jobs
            }

            for future in as_completed(future_to_job):
                job = future_to_job[future]
                try:
                    result = future.result()
                    self._update_job_status(job, "completed", result)
                    if self.config.progress_callback:
                        self.config.progress_callback(job, "completed")
                except Exception as e:
                    self._update_job_status(job, "failed", {"error": str(e)})
                    self.logger.error(f"Job failed: {job.input_path.name} - {e}")
                    if self.config.progress_callback:
                        self.config.progress_callback(job, "failed")

        total_time = time.time() - start_time
        self.processing_stats["total_time"] = total_time

        # Generate reports
        if self.config.create_summary_document:
            self._create_processing_report()

        self.logger.info(f"Batch processing completed in {total_time:.2f} seconds")
        return self.get_processing_summary()

    def process_single_job(self, job: ProcessingJob) -> Dict[str, Any]:
        """Process a single job (can be called directly)"""
        return self._process_single_job(job)

    def _process_single_job(self, job: ProcessingJob) -> Dict[str, Any]:
        """Internal method to process a single job"""

        job.status = "processing"
        start_time = time.time()

        try:
            # Parse document
            document = self.parser.parse_file(job.input_path)

            # Get or create brand profile
            brand_profile = job.brand_profile
            if not brand_profile:
                brand_profile = self._get_or_create_brand_profile(document)

            # Generate output files
            output_paths = {}

            for format_type in job.output_formats:
                try:
                    if format_type == "html":
                        output_path = self.html_generator.generate_html(document, brand_profile)
                    elif format_type == "pdf":
                        output_path = self.pdf_generator.generate_pdf(document, brand_profile)
                    elif format_type == "pptx":
                        output_path = self.pptx_generator.generate_presentation(document, brand_profile)
                    elif format_type == "docx":
                        output_path = self.docx_generator.generate_document(document, brand_profile)
                    else:
                        self.logger.warning(f"Unsupported format: {format_type}")
                        continue

                    output_paths[format_type] = output_path
                    self.processing_stats["formats_generated"][format_type] = \
                        self.processing_stats["formats_generated"].get(format_type, 0) + 1

                except Exception as e:
                    self.logger.error(f"Error generating {format_type} for {job.input_path.name}: {e}")
                    continue

            processing_time = time.time() - start_time

            return {
                "output_paths": output_paths,
                "processing_time": processing_time,
                "document_info": {
                    "title": document.metadata.title,
                    "type": document.metadata.document_type,
                    "company": document.metadata.company_name
                }
            }

        except Exception as e:
            raise Exception(f"Failed to process {job.input_path.name}: {e}")

    def _get_or_create_brand_profile(self, document: ParsedDocument) -> BrandProfile:
        """Get existing brand profile or create a default one"""

        company_name = document.metadata.company_name
        if company_name:
            existing_profile = self.brand_manager.load_profile(company_name)
            if existing_profile:
                return existing_profile

        # Create default brand profile based on industry
        return self._create_default_brand_profile(document)

    def _create_default_brand_profile(self, document: ParsedDocument) -> BrandProfile:
        """Create a default brand profile for a document"""

        from ..branding import ColorPalette, Typography, Layout, BrandAssets, DesignStyle

        # Industry-based defaults
        industry = document.metadata.industry.lower() if document.metadata.industry else "saas"
        design_style = DesignStyle.MODERN_CORPORATE

        industry_colors = {
            "agritech": ["#4CAF50", "#2E7D32"],
            "telecom": ["#1976D2", "#0D47A1"],
            "saas": ["#6200EA", "#7C4DFF"],
            "finance": ["#388E3C", "#1B5E20"],
            "healthcare": ["#00838F", "#006064"],
            "retail": ["#F44336", "#C62828"]
        }

        primary_colors = industry_colors.get(industry, industry_colors["saas"])

        return BrandProfile(
            company_name=document.metadata.company_name or "Untitled Company",
            industry=document.metadata.industry or "Technology",
            design_style=design_style,
            color_palette=ColorPalette(
                primary=primary_colors,
                secondary=["#424242", "#757575"],
                accent=primary_colors[0]
            ),
            typography=Typography(
                heading_font="Inter",
                body_font="Inter"
            ),
            layout=Layout(),
            brand_assets=BrandAssets()
        )

    def _update_job_status(self, job: ProcessingJob, status: str, result: Optional[Dict] = None):
        """Update job status and processing stats"""

        job.status = status
        if status == "completed":
            self.processing_stats["completed_jobs"] += 1
            if result and "output_paths" in result:
                job.output_paths = result["output_paths"]
            if result and "processing_time" in result:
                job.processing_time = result["processing_time"]
        elif status == "failed":
            self.processing_stats["failed_jobs"] += 1
            if result and "error" in result:
                job.error_message = result["error"]

    def _find_markdown_files(self, directory: Path, recursive: bool = True) -> List[Path]:
        """Find all markdown files in a directory"""

        pattern = "**/*.md" if recursive else "*.md"
        return list(directory.glob(pattern))

    def _create_processing_report(self) -> str:
        """Create a detailed processing report"""

        report_data = {
            "processing_summary": self.processing_stats,
            "job_details": [],
            "generated_at": datetime.now().isoformat(),
            "configuration": asdict(self.config)
        }

        # Add job details
        for job in self.jobs:
            job_data = {
                "input_file": str(job.input_path),
                "status": job.status,
                "formats_requested": job.output_formats,
                "output_paths": job.output_paths,
                "processing_time": job.processing_time,
                "error_message": job.error_message
            }
            report_data["job_details"].append(job_data)

        # Save report
        report_path = self.output_dirs["reports"] / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)

        self.logger.info(f"Processing report saved: {report_path}")
        return str(report_path)

    def create_index_pages(self, brand_profile: Optional[BrandProfile] = None) -> Dict[str, str]:
        """Create index pages for all output formats"""

        index_pages = {}

        # HTML index
        html_files = list(self.output_dirs["html"].glob("*.html"))
        if html_files:
            index_path = self.html_generator.create_index_page(
                [str(f) for f in html_files],
                brand_profile or self._create_default_brand_profile(None)
            )
            index_pages["html"] = index_path

        return index_pages

    def get_processing_summary(self) -> Dict[str, Any]:
        """Get a summary of processing results"""

        completed_jobs = [j for j in self.jobs if j.status == "completed"]
        failed_jobs = [j for j in self.jobs if j.status == "failed"]

        return {
            "total_jobs": len(self.jobs),
            "completed_jobs": len(completed_jobs),
            "failed_jobs": len(failed_jobs),
            "success_rate": (len(completed_jobs) / len(self.jobs)) * 100 if self.jobs else 0,
            "total_processing_time": self.processing_stats["total_time"],
            "formats_generated": self.processing_stats["formats_generated"],
            "output_directories": {k: str(v) for k, v in self.output_dirs.items()},
            "failed_job_details": [
                {
                    "input_file": str(job.input_path),
                    "error": job.error_message
                }
                for job in failed_jobs
            ]
        }

    def retry_failed_jobs(self) -> Dict[str, Any]:
        """Retry all failed jobs"""

        failed_jobs = [j for j in self.jobs if j.status == "failed"]
        if not failed_jobs:
            self.logger.info("No failed jobs to retry")
            return {"retried_jobs": 0, "results": {}}

        self.logger.info(f"Retrying {len(failed_jobs)} failed jobs")

        # Reset failed jobs
        for job in failed_jobs:
            job.status = "pending"
            job.error_message = None

        # Process retried jobs
        retried_results = {}
        for job in failed_jobs:
            try:
                result = self._process_single_job(job)
                self._update_job_status(job, "completed", result)
                retried_results[str(job.input_path)] = "success"
            except Exception as e:
                self._update_job_status(job, "failed", {"error": str(e)})
                retried_results[str(job.input_path)] = f"failed: {e}"

        return {
            "retried_jobs": len(failed_jobs),
            "results": retried_results
        }

    def clear_completed_jobs(self):
        """Remove completed jobs from the queue"""

        self.jobs = [j for j in self.jobs if j.status != "completed"]
        self.logger.info(f"Cleared completed jobs. Remaining: {len(self.jobs)}")

    def export_job_queue(self, file_path: Path):
        """Export job queue to a JSON file"""

        queue_data = {
            "jobs": [asdict(job) for job in self.jobs],
            "exported_at": datetime.now().isoformat(),
            "total_jobs": len(self.jobs)
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(queue_data, f, indent=2, default=str)

        self.logger.info(f"Job queue exported to: {file_path}")

    def import_job_queue(self, file_path: Path):
        """Import job queue from a JSON file"""

        with open(file_path, 'r', encoding='utf-8') as f:
            queue_data = json.load(f)

        imported_jobs = []
        for job_data in queue_data["jobs"]:
            # Convert paths back to Path objects
            job_data["input_path"] = Path(job_data["input_path"])
            if job_data.get("output_paths"):
                for format_type, path in job_data["output_paths"].items():
                    job_data["output_paths"][format_type] = Path(path) if path else None

            # Convert created_at back to datetime if present
            if job_data.get("created_at"):
                job_data["created_at"] = datetime.fromisoformat(job_data["created_at"])

            job = ProcessingJob(**job_data)
            imported_jobs.append(job)

        self.jobs.extend(imported_jobs)
        self.logger.info(f"Imported {len(imported_jobs)} jobs from: {file_path}")