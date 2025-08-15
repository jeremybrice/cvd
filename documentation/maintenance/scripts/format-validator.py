#!/usr/bin/env python3
"""
CVD Documentation Format Validator
Documentation standards compliance checking for the CVD documentation system.

Features:
- Metadata validation and standardization
- File naming convention compliance
- Document structure validation
- Template usage verification
- Cross-reference format checking
- Content formatting standards
- Automated fix suggestions
- Integration with quality monitoring
"""

import os
import re
import sys
import json
import yaml
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import frontmatter

@dataclass
class ValidationIssue:
    """Represents a single validation issue"""
    file_path: str
    issue_type: str  # 'metadata', 'naming', 'structure', 'template', 'formatting'
    severity: str    # 'error', 'warning', 'info'
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    auto_fixable: bool = False

@dataclass
class FileValidationResult:
    """Represents validation results for a single file"""
    file_path: str
    is_valid: bool
    score: float  # 0-100 compliance score
    issues: List[ValidationIssue]
    metadata_compliance: float
    structure_compliance: float
    formatting_compliance: float
    last_validated: str = None

    def __post_init__(self):
        if self.last_validated is None:
            self.last_validated = datetime.now().isoformat()

class DocumentationFormatValidator:
    """Main format validator for CVD documentation system"""
    
    def __init__(self, documentation_root: str = None):
        """Initialize the format validator"""
        if documentation_root is None:
            documentation_root = Path(__file__).parent.parent.parent
        
        self.documentation_root = Path(documentation_root)
        self.reports_dir = self.documentation_root / "maintenance" / "reports"
        self.templates_dir = self.documentation_root / "00-index" / "templates"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Load standards and templates
        self.load_standards()
        self.load_templates()
        
        # Setup logging
        self.setup_logging()
        
        # Statistics tracking
        self.stats = {
            'total_files': 0,
            'valid_files': 0,
            'files_with_errors': 0,
            'files_with_warnings': 0,
            'total_issues': 0,
            'auto_fixable_issues': 0,
            'average_score': 0.0,
            'metadata_compliance': 0.0,
            'structure_compliance': 0.0,
            'formatting_compliance': 0.0
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.reports_dir / "format_validator.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_standards(self):
        """Load documentation standards"""
        # File naming standards
        self.naming_standards = {
            'patterns': {
                'general': r'^[a-z0-9-]+\.md$',
                'adr': r'^ADR-\d{3}-[a-z0-9-]+\.md$',
                'date_stamped': r'^\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md$',
                'numbered': r'^\d{2,3}-[a-z0-9-]+\.md$'
            },
            'forbidden_chars': r'[A-Z\s_]',
            'max_length': 60
        }
        
        # Required metadata schema
        self.metadata_schema = {
            'required_fields': ['title', 'type', 'version', 'date'],
            'optional_fields': ['id', 'tags', 'author', 'status', 'category'],
            'field_formats': {
                'version': r'^\d+\.\d+\.\d+$',
                'date': r'^\d{4}-\d{2}-\d{2}$',
                'status': ['draft', 'review', 'approved', 'archived'],
                'type': ['guide', 'reference', 'specification', 'tutorial', 'overview', 'api', 'template']
            }
        }
        
        # Document structure requirements
        self.structure_requirements = {
            'required_sections': {
                'guide': ['Overview', 'Prerequisites', 'Steps', 'Examples'],
                'reference': ['Overview', 'Syntax', 'Parameters', 'Examples'],
                'specification': ['Overview', 'Requirements', 'Implementation'],
                'tutorial': ['Overview', 'Prerequisites', 'Steps', 'Next Steps'],
                'api': ['Overview', 'Endpoints', 'Request Format', 'Response Format']
            },
            'heading_structure': {
                'max_depth': 6,
                'sequential_required': True,
                'toc_threshold': 1000  # characters
            }
        }
        
        # Content formatting standards
        self.formatting_standards = {
            'line_length': 120,
            'code_block_language': True,
            'link_formats': {
                'internal': r'^\.\./|^[^/]',
                'external': r'^https?://'
            },
            'image_alt_text': True,
            'table_headers': True
        }
    
    def load_templates(self):
        """Load document templates for validation"""
        self.templates = {}
        
        if self.templates_dir.exists():
            for template_file in self.templates_dir.glob("*.md"):
                template_name = template_file.stem.replace('-template', '')
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                    self.templates[template_name] = template_content
                    self.logger.info(f"Loaded template: {template_name}")
                except Exception as e:
                    self.logger.warning(f"Could not load template {template_file}: {e}")
    
    def validate_file_naming(self, file_path: Path) -> List[ValidationIssue]:
        """Validate file naming conventions"""
        issues = []
        filename = file_path.name
        
        # Check for forbidden characters
        if re.search(self.naming_standards['forbidden_chars'], filename):
            issues.append(ValidationIssue(
                file_path=str(file_path),
                issue_type='naming',
                severity='error',
                message='Filename contains uppercase letters, spaces, or underscores',
                suggestion=f'Rename to: {filename.lower().replace(" ", "-").replace("_", "-")}',
                auto_fixable=True
            ))
        
        # Check length
        if len(filename) > self.naming_standards['max_length']:
            issues.append(ValidationIssue(
                file_path=str(file_path),
                issue_type='naming',
                severity='warning',
                message=f'Filename too long ({len(filename)} > {self.naming_standards["max_length"]} chars)',
                suggestion='Consider shortening filename while maintaining clarity'
            ))
        
        # Check specific patterns for special types
        relative_path = str(file_path.relative_to(self.documentation_root))
        
        if '/decisions/' in relative_path and not re.match(self.naming_standards['patterns']['adr'], filename):
            issues.append(ValidationIssue(
                file_path=str(file_path),
                issue_type='naming',
                severity='error',
                message='ADR files must follow ADR-NNN-title format',
                suggestion='Rename to ADR-001-descriptive-title.md format'
            ))
        
        return issues
    
    def validate_metadata(self, file_path: Path, content: str) -> Tuple[List[ValidationIssue], Dict]:
        """Validate document metadata"""
        issues = []
        metadata = {}
        
        # Check for frontmatter
        try:
            post = frontmatter.loads(content)
            metadata = post.metadata
        except Exception as e:
            # Try manual YAML extraction
            yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                try:
                    metadata = yaml.safe_load(yaml_match.group(1))
                except Exception as yaml_e:
                    issues.append(ValidationIssue(
                        file_path=str(file_path),
                        issue_type='metadata',
                        severity='error',
                        message=f'Invalid YAML frontmatter: {yaml_e}',
                        suggestion='Fix YAML syntax in frontmatter'
                    ))
                    return issues, {}
            else:
                issues.append(ValidationIssue(
                    file_path=str(file_path),
                    issue_type='metadata',
                    severity='warning',
                    message='No metadata frontmatter found',
                    suggestion='Add YAML frontmatter with required fields',
                    auto_fixable=True
                ))
                return issues, {}
        
        # Validate required fields
        for field in self.metadata_schema['required_fields']:
            if field not in metadata:
                issues.append(ValidationIssue(
                    file_path=str(file_path),
                    issue_type='metadata',
                    severity='error',
                    message=f'Missing required metadata field: {field}',
                    suggestion=f'Add {field} to frontmatter',
                    auto_fixable=True
                ))
        
        # Validate field formats
        for field, format_rule in self.metadata_schema['field_formats'].items():
            if field in metadata:
                value = metadata[field]
                if isinstance(format_rule, str):  # Regex pattern
                    if not re.match(format_rule, str(value)):
                        issues.append(ValidationIssue(
                            file_path=str(file_path),
                            issue_type='metadata',
                            severity='error',
                            message=f'Invalid format for {field}: {value}',
                            suggestion=f'{field} should match pattern: {format_rule}'
                        ))
                elif isinstance(format_rule, list):  # Allowed values
                    if value not in format_rule:
                        issues.append(ValidationIssue(
                            file_path=str(file_path),
                            issue_type='metadata',
                            severity='error',
                            message=f'Invalid value for {field}: {value}',
                            suggestion=f'{field} must be one of: {", ".join(format_rule)}'
                        ))
        
        return issues, metadata
    
    def validate_document_structure(self, file_path: Path, content: str, metadata: Dict) -> List[ValidationIssue]:
        """Validate document structure and organization"""
        issues = []
        
        # Extract headings
        headings = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                headings.append((level, title, i + 1))
        
        if not headings:
            issues.append(ValidationIssue(
                file_path=str(file_path),
                issue_type='structure',
                severity='warning',
                message='No headings found in document',
                suggestion='Add clear section headings to improve document structure'
            ))
            return issues
        
        # Check heading hierarchy
        prev_level = 0
        for level, title, line_num in headings:
            if level > prev_level + 1 and prev_level > 0:
                issues.append(ValidationIssue(
                    file_path=str(file_path),
                    issue_type='structure',
                    severity='warning',
                    message=f'Heading level skip from H{prev_level} to H{level}',
                    line_number=line_num,
                    suggestion='Use sequential heading levels (H1→H2→H3)'
                ))
            prev_level = level
        
        # Check for required sections based on document type
        doc_type = metadata.get('type', '').lower()
        if doc_type in self.structure_requirements['required_sections']:
            required_sections = self.structure_requirements['required_sections'][doc_type]
            found_sections = [title.lower() for _, title, _ in headings]
            
            for required_section in required_sections:
                if required_section.lower() not in found_sections:
                    issues.append(ValidationIssue(
                        file_path=str(file_path),
                        issue_type='structure',
                        severity='warning',
                        message=f'Missing recommended section for {doc_type}: {required_section}',
                        suggestion=f'Consider adding {required_section} section'
                    ))
        
        # Check for table of contents in long documents
        content_length = len(content)
        if content_length > self.structure_requirements['heading_structure']['toc_threshold']:
            toc_pattern = r'#\s*table\s+of\s+contents|#\s*contents|##\s*toc'
            if not re.search(toc_pattern, content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    file_path=str(file_path),
                    issue_type='structure',
                    severity='info',
                    message='Long document without table of contents',
                    suggestion='Consider adding a table of contents for better navigation'
                ))
        
        return issues
    
    def validate_content_formatting(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate content formatting standards"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > self.formatting_standards['line_length']:
                issues.append(ValidationIssue(
                    file_path=str(file_path),
                    issue_type='formatting',
                    severity='info',
                    message=f'Line {i} exceeds recommended length ({len(line)} > {self.formatting_standards["line_length"]})',
                    line_number=i,
                    suggestion='Consider breaking long lines for better readability'
                ))
        
        # Check code blocks have language specification
        code_blocks = re.findall(r'```(\w*)\n', content)
        for i, lang in enumerate(code_blocks):
            if not lang:
                issues.append(ValidationIssue(
                    file_path=str(file_path),
                    issue_type='formatting',
                    severity='warning',
                    message=f'Code block {i+1} missing language specification',
                    suggestion='Add language identifier to code blocks (e.g., ```python)',
                    auto_fixable=True
                ))
        
        # Check image alt text
        images = re.findall(r'!\[([^\]]*)\]\([^)]+\)', content)
        for i, alt_text in enumerate(images):
            if not alt_text.strip():
                issues.append(ValidationIssue(
                    file_path=str(file_path),
                    issue_type='formatting',
                    severity='warning',
                    message=f'Image {i+1} missing alt text',
                    suggestion='Add descriptive alt text for accessibility',
                    auto_fixable=True
                ))
        
        # Check table formatting
        table_lines = [line for line in lines if '|' in line and line.strip().startswith('|')]
        if table_lines:
            # Check for header row
            header_separator = [line for line in table_lines if re.match(r'^\|\s*[-:]+\s*\|', line)]
            if not header_separator:
                issues.append(ValidationIssue(
                    file_path=str(file_path),
                    issue_type='formatting',
                    severity='warning',
                    message='Table found without proper header separator',
                    suggestion='Add header separator row with |---|---|'
                ))
        
        # Check link formats
        links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
        for link_text, url in links:
            if url.startswith('http://'):
                issues.append(ValidationIssue(
                    file_path=str(file_path),
                    issue_type='formatting',
                    severity='warning',
                    message=f'Non-secure HTTP link: {url}',
                    suggestion='Use HTTPS links when possible',
                    auto_fixable=True
                ))
        
        return issues
    
    def validate_template_compliance(self, file_path: Path, content: str, metadata: Dict) -> List[ValidationIssue]:
        """Validate compliance with document templates"""
        issues = []
        doc_type = metadata.get('type', '').lower()
        
        if doc_type in self.templates:
            template_content = self.templates[doc_type]
            
            # Extract template sections
            template_headings = re.findall(r'^#{1,6}\s+(.+)$', template_content, re.MULTILINE)
            doc_headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
            
            # Check for missing template sections
            for template_heading in template_headings:
                if template_heading not in doc_headings:
                    issues.append(ValidationIssue(
                        file_path=str(file_path),
                        issue_type='template',
                        severity='info',
                        message=f'Missing template section: {template_heading}',
                        suggestion=f'Consider adding {template_heading} section as per template'
                    ))
        
        return issues
    
    def calculate_compliance_score(self, issues: List[ValidationIssue]) -> Tuple[float, float, float, float]:
        """Calculate compliance scores for different aspects"""
        total_score = 100.0
        metadata_score = 100.0
        structure_score = 100.0
        formatting_score = 100.0
        
        # Deduct points based on issue severity and type
        deductions = {
            'error': 10,
            'warning': 5,
            'info': 2
        }
        
        for issue in issues:
            deduction = deductions.get(issue.severity, 2)
            total_score -= deduction
            
            if issue.issue_type == 'metadata':
                metadata_score -= deduction * 1.5  # Metadata is more critical
            elif issue.issue_type == 'structure':
                structure_score -= deduction
            elif issue.issue_type == 'formatting':
                formatting_score -= deduction * 0.5  # Formatting is less critical
        
        # Ensure scores don't go below 0
        total_score = max(0, total_score)
        metadata_score = max(0, metadata_score)
        structure_score = max(0, structure_score)
        formatting_score = max(0, formatting_score)
        
        return total_score, metadata_score, structure_score, formatting_score
    
    def validate_file(self, file_path: Path) -> FileValidationResult:
        """Validate a single file against all standards"""
        self.logger.info(f"Validating: {file_path.relative_to(self.documentation_root)}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return FileValidationResult(
                file_path=str(file_path.relative_to(self.documentation_root)),
                is_valid=False,
                score=0.0,
                issues=[ValidationIssue(
                    file_path=str(file_path),
                    issue_type='file',
                    severity='error',
                    message=f'Could not read file: {e}'
                )],
                metadata_compliance=0.0,
                structure_compliance=0.0,
                formatting_compliance=0.0
            )
        
        all_issues = []
        
        # Run all validations
        all_issues.extend(self.validate_file_naming(file_path))
        
        metadata_issues, metadata = self.validate_metadata(file_path, content)
        all_issues.extend(metadata_issues)
        
        all_issues.extend(self.validate_document_structure(file_path, content, metadata))
        all_issues.extend(self.validate_content_formatting(file_path, content))
        all_issues.extend(self.validate_template_compliance(file_path, content, metadata))
        
        # Calculate scores
        total_score, metadata_score, structure_score, formatting_score = self.calculate_compliance_score(all_issues)
        
        # Determine if valid (no errors)
        has_errors = any(issue.severity == 'error' for issue in all_issues)
        is_valid = not has_errors
        
        return FileValidationResult(
            file_path=str(file_path.relative_to(self.documentation_root)),
            is_valid=is_valid,
            score=total_score,
            issues=all_issues,
            metadata_compliance=metadata_score,
            structure_compliance=structure_score,
            formatting_compliance=formatting_score
        )
    
    def validate_all_files(self) -> Dict:
        """Validate all documentation files"""
        start_time = datetime.now()
        self.logger.info("Starting comprehensive format validation...")
        
        # Find all markdown files
        md_files = list(self.documentation_root.rglob("*.md"))
        self.stats['total_files'] = len(md_files)
        
        file_results = []
        total_score = 0
        total_metadata_score = 0
        total_structure_score = 0
        total_formatting_score = 0
        
        for file_path in md_files:
            try:
                result = self.validate_file(file_path)
                file_results.append(result)
                
                # Update statistics
                total_score += result.score
                total_metadata_score += result.metadata_compliance
                total_structure_score += result.structure_compliance
                total_formatting_score += result.formatting_compliance
                
                if result.is_valid:
                    self.stats['valid_files'] += 1
                
                has_errors = any(issue.severity == 'error' for issue in result.issues)
                has_warnings = any(issue.severity == 'warning' for issue in result.issues)
                
                if has_errors:
                    self.stats['files_with_errors'] += 1
                if has_warnings:
                    self.stats['files_with_warnings'] += 1
                
                self.stats['total_issues'] += len(result.issues)
                self.stats['auto_fixable_issues'] += sum(1 for issue in result.issues if issue.auto_fixable)
                
            except Exception as e:
                self.logger.error(f"Error validating file {file_path}: {e}")
        
        # Calculate averages
        if self.stats['total_files'] > 0:
            self.stats['average_score'] = total_score / self.stats['total_files']
            self.stats['metadata_compliance'] = total_metadata_score / self.stats['total_files']
            self.stats['structure_compliance'] = total_structure_score / self.stats['total_files']
            self.stats['formatting_compliance'] = total_formatting_score / self.stats['total_files']
        
        # Generate report
        duration = datetime.now() - start_time
        report = self.generate_report(file_results, duration)
        
        self.logger.info(f"Validation completed in {duration.total_seconds():.2f} seconds")
        self.logger.info(f"Overall compliance: {self.stats['average_score']:.1f}/100")
        
        return report
    
    def generate_report(self, file_results: List[FileValidationResult], duration) -> Dict:
        """Generate comprehensive validation report"""
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator': 'CVD Documentation Format Validator',
                'version': '1.0.0',
                'validation_duration': duration.total_seconds(),
                'documentation_root': str(self.documentation_root)
            },
            'summary': dict(self.stats),
            'file_results': [asdict(result) for result in file_results],
            'issue_summary': self.get_issue_summary(file_results),
            'recommendations': self.generate_recommendations(file_results),
            'auto_fix_plan': self.generate_auto_fix_plan(file_results)
        }
        
        # Save detailed report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f"format_validation_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save latest report
        latest_file = self.reports_dir / "format_validation_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate human-readable summary
        self.generate_summary_report(report)
        
        return report
    
    def get_issue_summary(self, file_results: List[FileValidationResult]) -> Dict:
        """Generate summary of all issues by type and severity"""
        summary = defaultdict(lambda: defaultdict(int))
        
        for result in file_results:
            for issue in result.issues:
                summary[issue.issue_type][issue.severity] += 1
        
        return dict(summary)
    
    def generate_recommendations(self, file_results: List[FileValidationResult]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if self.stats['average_score'] < 80:
            recommendations.append("Overall documentation quality below 80%. Prioritize fixing critical issues.")
        
        if self.stats['metadata_compliance'] < 70:
            recommendations.append("Low metadata compliance. Implement metadata standardization process.")
        
        if self.stats['files_with_errors'] > self.stats['total_files'] * 0.1:
            recommendations.append("More than 10% of files have errors. Implement pre-commit validation.")
        
        if self.stats['auto_fixable_issues'] > 50:
            recommendations.append(f"{self.stats['auto_fixable_issues']} issues can be auto-fixed. Run auto-fix script.")
        
        return recommendations
    
    def generate_auto_fix_plan(self, file_results: List[FileValidationResult]) -> List[Dict]:
        """Generate plan for auto-fixable issues"""
        auto_fixes = []
        
        for result in file_results:
            for issue in result.issues:
                if issue.auto_fixable:
                    auto_fixes.append({
                        'file': result.file_path,
                        'issue_type': issue.issue_type,
                        'message': issue.message,
                        'suggestion': issue.suggestion,
                        'line_number': issue.line_number
                    })
        
        return auto_fixes
    
    def generate_summary_report(self, report: Dict):
        """Generate human-readable summary report"""
        summary_file = self.reports_dir / "format_validation_summary.md"
        
        with open(summary_file, 'w') as f:
            f.write("# CVD Documentation Format Validation Summary\n\n")
            f.write(f"**Generated**: {report['metadata']['generated_at']}\n")
            f.write(f"**Duration**: {report['metadata']['validation_duration']:.2f} seconds\n\n")
            
            # Overall statistics
            f.write("## Overall Compliance\n\n")
            stats = report['summary']
            f.write(f"- **Overall Score**: {stats['average_score']:.1f}/100\n")
            f.write(f"- **Metadata Compliance**: {stats['metadata_compliance']:.1f}/100\n")
            f.write(f"- **Structure Compliance**: {stats['structure_compliance']:.1f}/100\n")
            f.write(f"- **Formatting Compliance**: {stats['formatting_compliance']:.1f}/100\n\n")
            
            f.write(f"- **Total Files**: {stats['total_files']}\n")
            f.write(f"- **Valid Files**: {stats['valid_files']} ({stats['valid_files']/max(stats['total_files'],1):.1%})\n")
            f.write(f"- **Files with Errors**: {stats['files_with_errors']}\n")
            f.write(f"- **Files with Warnings**: {stats['files_with_warnings']}\n")
            f.write(f"- **Total Issues**: {stats['total_issues']}\n")
            f.write(f"- **Auto-fixable Issues**: {stats['auto_fixable_issues']}\n\n")
            
            # Issue breakdown
            f.write("## Issue Summary\n\n")
            issue_summary = report['issue_summary']
            for issue_type, severities in issue_summary.items():
                f.write(f"### {issue_type.title()} Issues\n")
                for severity, count in severities.items():
                    f.write(f"- **{severity.title()}**: {count}\n")
                f.write("\n")
            
            # Recommendations
            if report['recommendations']:
                f.write("## Recommendations\n\n")
                for rec in report['recommendations']:
                    f.write(f"- {rec}\n")
                f.write("\n")
            
            # Auto-fix plan summary
            if report['auto_fix_plan']:
                f.write("## Auto-Fix Opportunities\n\n")
                f.write(f"**{len(report['auto_fix_plan'])} issues can be automatically fixed:**\n\n")
                
                # Group by file
                files_with_fixes = {}
                for fix in report['auto_fix_plan']:
                    file_path = fix['file']
                    if file_path not in files_with_fixes:
                        files_with_fixes[file_path] = []
                    files_with_fixes[file_path].append(fix)
                
                for file_path, fixes in list(files_with_fixes.items())[:10]:  # Show first 10 files
                    f.write(f"**{file_path}**:\n")
                    for fix in fixes[:5]:  # Show first 5 fixes per file
                        f.write(f"- {fix['message']}\n")
                    if len(fixes) > 5:
                        f.write(f"- ... and {len(fixes) - 5} more\n")
                    f.write("\n")
                
                if len(files_with_fixes) > 10:
                    f.write(f"*... and {len(files_with_fixes) - 10} more files with auto-fixable issues*\n")

def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='CVD Documentation Format Validator')
    parser.add_argument('--validate', action='store_true', help='Run comprehensive validation')
    parser.add_argument('--file', type=str, help='Validate specific file')
    parser.add_argument('--auto-fix', action='store_true', help='Apply auto-fixes')
    parser.add_argument('--type', type=str, choices=['metadata', 'naming', 'structure', 'formatting', 'template'],
                       help='Validate only specific aspect')
    parser.add_argument('--severity', type=str, choices=['error', 'warning', 'info'],
                       help='Show only issues of specific severity')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = DocumentationFormatValidator()
    
    if args.file:
        # Validate single file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File {file_path} not found")
            return 1
        
        result = validator.validate_file(file_path)
        print(f"File: {result.file_path}")
        print(f"Score: {result.score:.1f}/100")
        print(f"Valid: {result.is_valid}")
        
        if result.issues:
            print(f"\nIssues ({len(result.issues)}):")
            for issue in result.issues:
                if not args.severity or issue.severity == args.severity:
                    if not args.type or issue.issue_type == args.type:
                        line_info = f" (line {issue.line_number})" if issue.line_number else ""
                        print(f"  {issue.severity.upper()}: {issue.message}{line_info}")
                        if issue.suggestion:
                            print(f"    Suggestion: {issue.suggestion}")
        
        return 1 if not result.is_valid else 0
    
    elif args.validate:
        # Run comprehensive validation
        report = validator.validate_all_files()
        stats = report['summary']
        
        print(f"Format validation completed. Report saved to: {validator.reports_dir}")
        print(f"Overall score: {stats['average_score']:.1f}/100")
        print(f"Valid files: {stats['valid_files']}/{stats['total_files']}")
        print(f"Total issues: {stats['total_issues']} ({stats['auto_fixable_issues']} auto-fixable)")
        
        return 1 if stats['files_with_errors'] > 0 else 0
    
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())