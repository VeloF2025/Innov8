#!/usr/bin/env python3
"""
Embryo Template Synchronization Script

This script manages synchronization between embryo master templates and project-specific instances.
It handles version tracking, update notifications, and customized template management.

Usage:
    python sync_templates.py --check                    # Check for updates
    python sync_templates.py --update                   # Update outdated templates
    python sync_templates.py --validate                 # Validate template quality
    python sync_templates.py --stats                    # Show statistics
    python sync_templates.py --add-project <path>       # Add new project
"""

import os
import sys
import json
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

class TemplateSynchronizer:
    def __init__(self, embryo_path: str = None):
        """Initialize the template synchronizer."""
        self.embryo_path = Path(embryo_path) if embryo_path else Path(__file__).parent.parent
        self.registry_path = self.embryo_path / "TEMPLATE_REGISTRY.json"
        self.project_mapping_path = self.embryo_path / "PROJECT_MAPPING.json"

        # Load registry and mapping
        self.template_registry = self.load_registry()
        self.project_mapping = self.load_project_mapping()

    def load_registry(self) -> Dict:
        """Load the template registry."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"templates": {}, "last_updated": str(datetime.now())}

    def load_project_mapping(self) -> Dict:
        """Load the project mapping."""
        if self.project_mapping_path.exists():
            with open(self.project_mapping_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"projects": {}, "last_updated": str(datetime.now())}

    def save_registry(self):
        """Save the template registry."""
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.template_registry, f, indent=2, default=str)

    def save_project_mapping(self):
        """Save the project mapping."""
        with open(self.project_mapping_path, 'w', encoding='utf-8') as f:
            json.dump(self.project_mapping, f, indent=2, default=str)

    def scan_embryo_templates(self) -> Dict[str, Dict]:
        """Scan embryo directory for all templates."""
        templates = {}

        for template_file in self.embryo_path.rglob("*.md"):
            if template_file.is_file():
                relative_path = template_file.relative_to(self.embryo_path)
                template_id = str(relative_path).replace("\\", "/").replace(".md", "")

                # Extract metadata from template
                metadata = self.extract_metadata(template_file)

                templates[template_id] = {
                    "file_path": str(relative_path),
                    "full_path": str(template_file),
                    "metadata": metadata,
                    "last_scanned": str(datetime.now()),
                    "file_size": template_file.stat().st_size,
                    "last_modified": str(datetime.fromtimestamp(template_file.stat().st_mtime))
                }

        return templates

    def extract_metadata(self, template_path: Path) -> Dict:
        """Extract metadata from a template file."""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for YAML metadata block
            yaml_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                try:
                    metadata = yaml.safe_load(yaml_match.group(1))
                    return metadata if isinstance(metadata, dict) else {}
                except yaml.YAMLError:
                    return {}

            return {}
        except Exception as e:
            print(f"Error reading metadata from {template_path}: {e}")
            return {}

    def scan_projects(self) -> Dict:
        """Scan projects directory for template instances."""
        projects = {}
        projects_path = self.embryo_path.parent / "companies"

        if not projects_path.exists():
            return projects

        for company_path in projects_path.iterdir():
            if company_path.is_dir():
                for project_path in company_path.iterdir():
                    if project_path.is_dir():
                        workspace_path = project_path / "workspace"
                        if workspace_path.exists():
                            project_id = f"{company_path.name}/{project_path.name}"
                            projects[project_id] = self.scan_project_templates(workspace_path, project_id)

        return projects

    def scan_project_templates(self, workspace_path: Path, project_id: str) -> Dict:
        """Scan a specific project for templates."""
        templates = {}
        business_planning_path = workspace_path / "business-planning"

        if business_planning_path.exists():
            for template_file in business_planning_path.glob("*.md"):
                template_id = template_file.stem
                metadata = self.extract_metadata(template_file)

                templates[template_id] = {
                    "file_path": str(template_file.relative_to(workspace_path)),
                    "full_path": str(template_file),
                    "metadata": metadata,
                    "last_scanned": str(datetime.now()),
                    "file_size": template_file.stat().st_size
                }

        return templates

    def check_updates(self) -> List[Dict]:
        """Check for template updates."""
        updates_needed = []

        # Scan current embryo templates
        embryo_templates = self.scan_embryo_templates()

        # Check each project template
        for project_id, project_data in self.project_mapping.get("projects", {}).items():
            for template_name, template_info in project_data.get("templates", {}).items():
                source_template = template_info.get("source")
                current_version = template_info.get("version", "unknown")

                if source_template and source_template in embryo_templates:
                    source_info = embryo_templates[source_template]
                    source_version = source_info.get("metadata", {}).get("template_version", "unknown")

                    if source_version != current_version:
                        updates_needed.append({
                            "project_id": project_id,
                            "template_name": template_name,
                            "current_version": current_version,
                            "available_version": source_version,
                            "source_template": source_template,
                            "customizations": template_info.get("customizations", []),
                            "urgency": self.calculate_update_urgency(current_version, source_version)
                        })

        return updates_needed

    def calculate_update_urgency(self, current: str, available: str) -> str:
        """Calculate update urgency based on version difference."""
        try:
            current_parts = [int(x) for x in current.split('.')]
            available_parts = [int(x) for x in available.split('.')]

            # Pad shorter version with zeros
            max_len = max(len(current_parts), len(available_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            available_parts.extend([0] * (max_len - len(available_parts)))

            # Compare versions
            if available_parts[0] > current_parts[0]:
                return "HIGH"  # Major version update
            elif available_parts[1] > current_parts[1]:
                return "MEDIUM"  # Minor version update
            elif available_parts[2] > current_parts[2]:
                return "LOW"  # Patch update
            else:
                return "NONE"  # No update needed
        except:
            return "UNKNOWN"

    def update_template(self, project_id: str, template_name: str, dry_run: bool = False) -> bool:
        """Update a specific template in a project."""
        project_data = self.project_mapping.get("projects", {}).get(project_id)
        if not project_data:
            print(f"Project {project_id} not found in mapping")
            return False

        template_info = project_data.get("templates", {}).get(template_name)
        if not template_info:
            print(f"Template {template_name} not found in project {project_id}")
            return False

        source_template = template_info.get("source")
        if not source_template:
            print(f"No source template specified for {template_name}")
            return False

        # Get source template path
        source_path = self.embryo_path / f"{source_template}.md"
        if not source_path.exists():
            print(f"Source template {source_path} not found")
            return False

        # Get destination path
        dest_path = Path(template_info.get("full_path"))
        if not dest_path.exists():
            print(f"Destination template {dest_path} not found")
            return False

        # Read source and destination templates
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                source_content = f.read()

            with open(dest_path, 'r', encoding='utf-8') as f:
                dest_content = f.read()

            # Extract customizations from destination
            customizations = self.extract_customizations(dest_content)

            # Apply customizations to source
            updated_content = self.apply_customizations(source_content, customizations)

            if dry_run:
                print(f"DRY RUN: Would update {dest_path}")
                print(f"Customizations to preserve: {len(customizations)}")
                return True

            # Write updated content
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            # Update metadata
            metadata = self.extract_metadata(source_path)
            template_info["version"] = metadata.get("template_version", "unknown")
            template_info["last_updated"] = str(datetime.now())
            template_info["sync_status"] = "updated"

            # Save updated mapping
            self.save_project_mapping()

            print(f"Updated {dest_path} with version {template_info['version']}")
            return True

        except Exception as e:
            print(f"Error updating template: {e}")
            return False

    def extract_customizations(self, content: str) -> Dict:
        """Extract customizations from a template."""
        customizations = {}

        # Look for company-specific sections
        company_sections = re.findall(r'\n## 🎯 ([^-]+).*?\n(.*?)(?=\n## |\n---|\Z)', content, re.DOTALL)
        for title, section_content in company_sections:
            if "Specific" in title or "Custom" in title:
                customizations[title] = section_content

        return customizations

    def apply_customizations(self, content: str, customizations: Dict) -> str:
        """Apply customizations to template content."""
        # This is a simplified implementation
        # In practice, you'd want more sophisticated merge logic

        updated_content = content

        # Find company-specific sections and preserve them
        for title, custom_content in customizations.items():
            # Look for similar section in new template
            pattern = rf'(\n## 🎯 {re.escape(title)}.*?\n)(.*?)(?=\n## |\n---|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                # Replace the section content while preserving the header
                updated_content = updated_content.replace(
                    match.group(0),
                    match.group(1) + custom_content
                )

        return updated_content

    def validate_templates(self) -> List[Dict]:
        """Validate all templates for quality and completeness."""
        validation_results = []

        # Validate embryo templates
        embryo_templates = self.scan_embryo_templates()
        for template_id, template_info in embryo_templates.items():
            validation = self.validate_template(template_info["full_path"])
            validation["template_id"] = template_id
            validation["type"] = "embryo"
            validation_results.append(validation)

        # Validate project templates
        for project_id, project_data in self.project_mapping.get("projects", {}).items():
            for template_name, template_info in project_data.get("templates", {}).items():
                validation = self.validate_template(template_info["full_path"])
                validation["project_id"] = project_id
                validation["template_name"] = template_name
                validation["type"] = "project"
                validation_results.append(validation)

        return validation_results

    def validate_template(self, template_path: str) -> Dict:
        """Validate a single template."""
        result = {
            "path": template_path,
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {},
            "sections": []
        }

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for metadata
            metadata = self.extract_metadata(Path(template_path))
            result["metadata"] = metadata

            required_metadata_fields = ["template_version", "template_name", "category"]
            for field in required_metadata_fields:
                if field not in metadata:
                    result["errors"].append(f"Missing required metadata field: {field}")
                    result["valid"] = False

            # Check for required sections
            sections = re.findall(r'^## (.+)$', content, re.MULTILINE)
            result["sections"] = sections

            if len(sections) < 3:
                result["warnings"].append("Template has very few sections")

            # Check for completion checklist
            if "completion checklist" not in content.lower():
                result["warnings"].append("No completion checklist found")

            # Check for time estimates
            if "minutes" not in content.lower() and "hours" not in content.lower():
                result["warnings"].append("No time estimates found")

        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Error reading template: {e}")

        return result

    def generate_statistics(self) -> Dict:
        """Generate statistics about the template ecosystem."""
        stats = {
            "embryo_templates": 0,
            "project_templates": 0,
            "projects": 0,
            "updates_needed": 0,
            "validation_errors": 0,
            "categories": {},
            "last_updated": str(datetime.now())
        }

        # Count embryo templates
        embryo_templates = self.scan_embryo_templates()
        stats["embryo_templates"] = len(embryo_templates)

        # Count by category
        for template_id, template_info in embryo_templates.items():
            category = template_info.get("metadata", {}).get("category", "unknown")
            stats["categories"][category] = stats["categories"].get(category, 0) + 1

        # Count projects and templates
        projects = self.scan_projects()
        stats["projects"] = len(projects)
        for project_id, project_data in projects.items():
            stats["project_templates"] += len(project_data)

        # Count updates needed
        updates = self.check_updates()
        stats["updates_needed"] = len(updates)

        # Count validation errors
        validations = self.validate_templates()
        stats["validation_errors"] = len([v for v in validations if not v["valid"]])

        return stats

    def add_project(self, project_path: str) -> bool:
        """Add a new project to the mapping."""
        project_path = Path(project_path)
        if not project_path.exists():
            print(f"Project path {project_path} does not exist")
            return False

        # Extract project ID from path
        relative_path = project_path.relative_to(self.embryo_path.parent)
        project_id = str(relative_path).replace("\\", "/")

        # Scan project templates
        workspace_path = project_path / "workspace"
        if not workspace_path.exists():
            print(f"No workspace found in {project_path}")
            return False

        project_templates = self.scan_project_templates(workspace_path, project_id)

        # Add to mapping
        if "projects" not in self.project_mapping:
            self.project_mapping["projects"] = {}

        self.project_mapping["projects"][project_id] = {
            "path": str(relative_path),
            "templates": {},
            "last_scanned": str(datetime.now())
        }

        for template_name, template_info in project_templates.items():
            self.project_mapping["projects"][project_id]["templates"][template_name] = {
                "file_path": template_info["file_path"],
                "full_path": template_info["full_path"],
                "metadata": template_info["metadata"],
                "source": self.guess_source_template(template_info["metadata"]),
                "version": template_info["metadata"].get("template_version", "unknown"),
                "customizations": [],
                "last_updated": template_info["metadata"].get("last_updated", "unknown"),
                "sync_status": "new"
            }

        self.save_project_mapping()
        print(f"Added project {project_id} with {len(project_templates)} templates")
        return True

    def guess_source_template(self, metadata: Dict) -> Optional[str]:
        """Guess the source template based on metadata."""
        category = metadata.get("category", "")
        subcategory = metadata.get("subcategory", "")

        # Simple heuristic based on metadata
        if category == "business-stage":
            if subcategory == "seed-stage":
                return "embryo/business-stages/seed-stage-template-v2"
            elif subcategory == "pre-seed":
                return "embryo/business-stages/pre-seed-idea-template-v1"
        elif category == "business-type":
            if subcategory == "agritech":
                return "embryo/business-types/agritech-template"
            elif subcategory == "saas":
                return "embryo/business-types/saas-template"

        return None

def main():
    parser = argparse.ArgumentParser(description="Embryo Template Synchronization Script")
    parser.add_argument("--embryo-path", help="Path to embryo directory")
    parser.add_argument("--check", action="store_true", help="Check for template updates")
    parser.add_argument("--update", help="Update specific template (format: project_id/template_name)")
    parser.add_argument("--update-all", action="store_true", help="Update all outdated templates")
    parser.add_argument("--validate", action="store_true", help="Validate all templates")
    parser.add_argument("--stats", action="store_true", help="Show template statistics")
    parser.add_argument("--add-project", help="Add a new project to the mapping")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making changes")

    args = parser.parse_args()

    synchronizer = TemplateSynchronizer(args.embryo_path)

    if args.check:
        print("Checking for template updates...")
        updates = synchronizer.check_updates()

        if updates:
            print(f"\nFound {len(updates)} templates needing updates:")
            for update in updates:
                print(f"  - {update['project_id']}/{update['template_name']}")
                print(f"    Current: {update['current_version']} → Available: {update['available_version']}")
                print(f"    Urgency: {update['urgency']}")
                print()
        else:
            print("All templates are up to date!")

    elif args.update:
        if "/" in args.update:
            project_id, template_name = args.update.split("/", 1)
            print(f"Updating {project_id}/{template_name}...")
            success = synchronizer.update_template(project_id, template_name, args.dry_run)
            if success:
                print("Update completed successfully!")
            else:
                print("Update failed!")
        else:
            print("Please specify template in format: project_id/template_name")

    elif args.update_all:
        print("Updating all outdated templates...")
        updates = synchronizer.check_updates()

        for update in updates:
            print(f"Updating {update['project_id']}/{update['template_name']}...")
            success = synchronizer.update_template(update['project_id'], update['template_name'], args.dry_run)
            if success:
                print("  ✓ Updated successfully")
            else:
                print("  ✗ Update failed")

    elif args.validate:
        print("Validating all templates...")
        validations = synchronizer.validate_templates()

        errors = [v for v in validations if not v["valid"]]
        warnings = [v for v in validations if v["warnings"]]

        print(f"\nValidation Results:")
        print(f"  Total templates: {len(validations)}")
        print(f"  Templates with errors: {len(errors)}")
        print(f"  Templates with warnings: {len(warnings)}")

        if errors:
            print("\nTemplates with errors:")
            for error in errors:
                print(f"  - {error.get('template_id', error.get('project_id') + '/' + error.get('template_name', ''))}")
                for err in error["errors"]:
                    print(f"    ✗ {err}")

        if warnings:
            print("\nTemplates with warnings:")
            for warning in warnings:
                template_id = warning.get('template_id', warning.get('project_id') + '/' + warning.get('template_name', ''))
                print(f"  - {template_id}")
                for warn in warning["warnings"]:
                    print(f"    ⚠ {warn}")

    elif args.stats:
        print("Generating template statistics...")
        stats = synchronizer.generate_statistics()

        print(f"\nTemplate Ecosystem Statistics:")
        print(f"  Embryo Templates: {stats['embryo_templates']}")
        print(f"  Project Templates: {stats['project_templates']}")
        print(f"  Total Projects: {stats['projects']}")
        print(f"  Updates Needed: {stats['updates_needed']}")
        print(f"  Validation Errors: {stats['validation_errors']}")

        print(f"\nTemplates by Category:")
        for category, count in stats["categories"].items():
            print(f"  {category}: {count}")

    elif args.add_project:
        print(f"Adding project {args.add_project}...")
        success = synchronizer.add_project(args.add_project)
        if success:
            print("Project added successfully!")
        else:
            print("Failed to add project!")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()