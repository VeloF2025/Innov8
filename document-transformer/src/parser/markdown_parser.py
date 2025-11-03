"""
Intelligent Markdown Parser for Business Documents
Handles content analysis, structure detection, and metadata extraction
"""

import re
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class DocumentMetadata:
    """Metadata extracted from business documents"""
    title: str = ""
    company: str = ""
    project: str = ""
    document_type: str = ""
    industry: str = ""
    created_date: Optional[str] = None
    last_modified: Optional[str] = None
    author: str = ""
    status: str = "draft"
    priority: str = "medium"
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class ContentSection:
    """Represents a section of the document"""
    title: str
    content: str
    level: int = 1
    subsections: List['ContentSection'] = None

    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []

@dataclass
class FinancialData:
    """Financial data extracted from tables"""
    table_data: List[List[str]]
    headers: List[str]
    title: str = ""
    currency: str = "USD"
    period: str = "annual"

@dataclass
class TeamMember:
    """Team member information"""
    name: str = ""
    title: str = ""
    bio: str = ""
    experience: str = ""
    education: str = ""

@dataclass
class ParsedDocument:
    """Complete parsed document structure"""
    metadata: DocumentMetadata
    sections: List[ContentSection]
    financial_data: List[FinancialData] = None
    team_members: List[TeamMember] = None
    tables: List[List[List[str]]] = None
    images: List[str] = None
    links: List[str] = None

    def __post_init__(self):
        if self.financial_data is None:
            self.financial_data = []
        if self.team_members is None:
            self.team_members = []
        if self.tables is None:
            self.tables = []
        if self.images is None:
            self.images = []
        if self.links is None:
            self.links = []

class MarkdownParser:
    """Intelligent parser for business markdown documents"""

    def __init__(self, config=None):
        self.config = config
        self.financial_keywords = [
            'revenue', 'expenses', 'profit', 'loss', 'income', 'cost',
            'budget', 'forecast', 'projection', 'investment', 'funding',
            'cash flow', 'burn rate', 'runway', 'valuation', 'cap table'
        ]

        self.team_keywords = [
            'team', 'founders', 'leadership', 'management', 'advisors',
            'board', 'executives', 'key personnel', 'staff'
        ]

        self.section_patterns = {
            'executive_summary': r'(executive summary|overview|introduction)',
            'problem': r'(problem|challenge|opportunity|pain point)',
            'solution': r'(solution|product|service|offering)',
            'market': r'(market|industry|sector|landscape)',
            'competition': r'(competition|competitors|alternatives)',
            'business_model': r'(business model|revenue model|monetization)',
            'team': r'(team|founders|leadership|management)',
            'financials': r'(financial|projections|forecasts|budget)',
            'traction': r'(traction|milestones|progress|achievements)',
            'ask': r'(ask|investment|funding|raise)'
        }

    def parse_file(self, file_path: Path) -> ParsedDocument:
        """Parse a markdown file and extract all relevant information"""

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return self.parse_content(content, file_path)

    def parse_content(self, content: str, source_path: Optional[Path] = None) -> ParsedDocument:
        """Parse markdown content and return structured document"""

        # Extract metadata
        metadata = self._extract_metadata(content, source_path)

        # Extract sections
        sections = self._extract_sections(content)

        # Extract financial data
        financial_data = self._extract_financial_data(content)

        # Extract team information
        team_members = self._extract_team_info(content)

        # Extract tables
        tables = self._extract_tables(content)

        # Extract images
        images = self._extract_images(content)

        # Extract links
        links = self._extract_links(content)

        return ParsedDocument(
            metadata=metadata,
            sections=sections,
            financial_data=financial_data,
            team_members=team_members,
            tables=tables,
            images=images,
            links=links
        )

    def _extract_metadata(self, content: str, source_path: Optional[Path] = None) -> DocumentMetadata:
        """Extract metadata from document content and file path"""

        metadata = DocumentMetadata()

        # Extract YAML frontmatter if present
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if yaml_match:
            try:
                yaml_data = yaml.safe_load(yaml_match.group(1))
                for key, value in yaml_data.items():
                    if hasattr(metadata, key):
                        setattr(metadata, key, value)
            except yaml.YAMLError:
                pass

        # Extract from file path
        if source_path:
            path_parts = source_path.parts
            if len(path_parts) >= 2:
                metadata.company = self._extract_company_name(source_path)
                metadata.project = self._extract_project_name(source_path)

        # Extract title from first H1 if not in metadata
        if not metadata.title:
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            if title_match:
                metadata.title = title_match.group(1).strip()

        # Detect document type
        metadata.document_type = self._detect_document_type(content)

        # Detect industry
        metadata.industry = self._detect_industry(content)

        # Extract dates
        if source_path and source_path.exists():
            metadata.last_modified = datetime.fromtimestamp(
                source_path.stat().st_mtime
            ).isoformat()

        # Extract author if present
        author_match = re.search(r'(?:author|by):\s*(.+)', content, re.IGNORECASE)
        if author_match:
            metadata.author = author_match.group(1).strip()

        # Extract status
        status_match = re.search(r'status:\s*(.+)', content, re.IGNORECASE)
        if status_match:
            metadata.status = status_match.group(1).strip().lower()

        return metadata

    def _extract_sections(self, content: str) -> List[ContentSection]:
        """Extract document sections based on headers"""

        lines = content.split('\n')
        sections = []
        current_section = None
        current_content = []

        for line in lines:
            # Check for headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                # Save previous section
                if current_section:
                    current_section.content = '\n'.join(current_content).strip()
                    sections.append(current_section)

                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = ContentSection(title=title, level=level, content="")
                current_content = []
            else:
                # Skip YAML frontmatter
                if not line.startswith('---'):
                    current_content.append(line)

        # Save last section
        if current_section:
            current_section.content = '\n'.join(current_content).strip()
            sections.append(current_section)

        return sections

    def _extract_financial_data(self, content: str) -> List[FinancialData]:
        """Extract financial data from tables and content"""

        financial_data = []

        # Find financial tables
        tables = self._extract_tables(content)
        for i, table in enumerate(tables):
            if self._is_financial_table(table):
                title = f"Financial Data {i+1}"

                # Try to extract title from preceding text
                table_start = content.find('\n'.join(['|'.join(row) for row in table]))
                if table_start > 0:
                    preceding_text = content[:table_start].split('\n')[-3:]
                    for line in reversed(preceding_text):
                        if line.strip() and any(keyword in line.lower() for keyword in self.financial_keywords):
                            title = line.strip('# ').strip()
                            break

                financial_data.append(FinancialData(
                    table_data=table,
                    headers=table[0] if table else [],
                    title=title
                ))

        return financial_data

    def _extract_team_info(self, content: str) -> List[TeamMember]:
        """Extract team member information"""

        team_members = []

        # Look for team sections
        team_section_match = re.search(
            r'(?:team|founders|leadership|management)[\s\S]*?(?=\n#{1,3} |\Z)',
            content,
            re.IGNORECASE
        )

        if team_section_match:
            team_content = team_section_match.group(0)

            # Pattern for team member information
            member_pattern = r'(?:^|\n)[\*\-]\s*([^,\n]+?)\s*(?:,\s*([^,\n]+))?'
            matches = re.findall(member_pattern, team_content)

            for match in matches:
                name = match[0].strip()
                title = match[1].strip() if len(match) > 1 and match[1] else ""

                if name and len(name.split()) >= 2:  # Likely a real name
                    team_member = TeamMember(
                        name=name,
                        title=title
                    )
                    team_members.append(team_member)

        return team_members

    def _extract_tables(self, content: str) -> List[List[List[str]]]:
        """Extract markdown tables"""

        tables = []
        table_lines = []
        in_table = False

        lines = content.split('\n')
        for line in lines:
            if '|' in line and ('|' in line.split('|')[1] if len(line.split('|')) > 2 else False):
                # This looks like a table row
                if not in_table:
                    in_table = True
                table_lines.append(line)
            elif in_table:
                # Table ended
                if table_lines:
                    table = self._parse_table(table_lines)
                    if table:
                        tables.append(table)
                table_lines = []
                in_table = False

        # Handle table at end of file
        if table_lines:
            table = self._parse_table(table_lines)
            if table:
                tables.append(table)

        return tables

    def _parse_table(self, table_lines: List[str]) -> List[List[str]]:
        """Parse table lines into 2D array"""

        table = []
        for line in table_lines:
            if line.strip() and '|' in line:
                # Skip separator lines (e.g., |---|---|)
                if not re.match(r'^[\s\|\-\:]*$', line):
                    cells = [cell.strip() for cell in line.split('|')]
                    # Remove empty cells at start and end
                    if cells and not cells[0]:
                        cells = cells[1:]
                    if cells and not cells[-1]:
                        cells = cells[:-1]
                    if cells:
                        table.append(cells)

        return table

    def _extract_images(self, content: str) -> List[str]:
        """Extract image references"""

        # Markdown images: ![alt](src)
        img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(img_pattern, content)
        return [match[1] for match in matches]

    def _extract_links(self, content: str) -> List[str]:
        """Extract web links"""

        # Markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)

        # Filter out images and internal links
        links = []
        for match in matches:
            url = match[1]
            if not url.startswith(('http://', 'https://')):
                continue
            if url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                continue
            links.append(url)

        return links

    def _is_financial_table(self, table: List[List[str]]) -> bool:
        """Determine if a table contains financial data"""

        if not table:
            return False

        # Check headers and content for financial keywords
        all_text = ' '.join([' '.join(row) for row in table]).lower()
        financial_count = sum(1 for keyword in self.financial_keywords if keyword in all_text)

        return financial_count >= 2

    def _detect_document_type(self, content: str) -> str:
        """Detect document type based on content analysis"""

        content_lower = content.lower()

        if self.config:
            return self.config.get_document_type([], content_lower, len(self._extract_tables(content)) > 0)

        # Fallback detection
        if 'teaser' in content_lower or 'one pager' in content_lower:
            return 'investor_teaser'
        elif 'pitch deck' in content_lower or 'presentation' in content_lower:
            return 'pitch_deck'
        elif any(keyword in content_lower for keyword in ['financial', 'projections', 'revenue']):
            return 'financial_projections'
        elif 'business plan' in content_lower:
            return 'business_plan'
        elif 'market research' in content_lower or 'market analysis' in content_lower:
            return 'market_research'
        else:
            return 'business_plan'

    def _detect_industry(self, content: str) -> str:
        """Detect industry based on content keywords"""

        content_lower = content.lower()

        industry_keywords = {
            'agritech': ['agriculture', 'farming', 'crop', 'soil', 'harvest', 'agricultural'],
            'telecom': ['telecom', 'communication', 'network', 'fiber', 'broadband', 'connectivity'],
            'saas': ['software', 'saas', 'platform', 'subscription', 'cloud', 'digital'],
            'finance': ['finance', 'fintech', 'banking', 'payments', 'financial services'],
            'healthcare': ['health', 'medical', 'healthcare', 'hospital', 'pharmaceutical'],
            'retail': ['retail', 'ecommerce', 'shopping', 'consumer', 'store'],
            'manufacturing': ['manufacturing', 'production', 'factory', 'industrial']
        }

        industry_scores = {}
        for industry, keywords in industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            industry_scores[industry] = score

        if industry_scores:
            return max(industry_scores.items(), key=lambda x: x[1])[0]

        return 'saas'  # default

    def _extract_company_name(self, file_path: Path) -> str:
        """Extract company name from file path"""

        # Look for company in path structure
        parts = file_path.parts
        for i, part in enumerate(parts):
            if part == 'companies' and i + 1 < len(parts):
                return parts[i + 1]

        return ""

    def _extract_project_name(self, file_path: Path) -> str:
        """Extract project name from file path"""

        # Look for project in path structure
        parts = file_path.parts
        for i, part in enumerate(parts):
            if part == 'projects' and i + 1 < len(parts):
                return parts[i + 1]

        return ""

    def get_document_summary(self, doc: ParsedDocument) -> Dict:
        """Get a summary of the parsed document"""

        return {
            'title': doc.metadata.title,
            'type': doc.metadata.document_type,
            'industry': doc.metadata.industry,
            'sections_count': len(doc.sections),
            'has_financial_data': len(doc.financial_data) > 0,
            'has_team_info': len(doc.team_members) > 0,
            'tables_count': len(doc.tables),
            'images_count': len(doc.images),
            'word_count': len(' '.join([section.content for section in doc.sections]).split()),
            'status': doc.metadata.status
        }