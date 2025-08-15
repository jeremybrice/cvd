#!/usr/bin/env python3
"""
CVD Documentation Link Checker
Automated link validation for internal and external links across the documentation system.

Features:
- Internal link validation with path resolution
- External link validation with HTTP status checking
- Broken link detection and reporting
- Link inventory and statistics
- Scheduled execution and error reporting
- Integration with health monitoring system
- Performance tracking and analytics
"""

import os
import re
import sys
import json
import time
import requests
import logging
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import concurrent.futures
import threading
from collections import defaultdict

@dataclass
class LinkResult:
    """Represents the result of checking a single link"""
    url: str
    status: str  # 'valid', 'broken', 'redirect', 'timeout', 'error'
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    redirect_url: Optional[str] = None
    last_checked: str = None

    def __post_init__(self):
        if self.last_checked is None:
            self.last_checked = datetime.now().isoformat()

@dataclass
class FileReport:
    """Represents link check results for a single file"""
    file_path: str
    total_links: int
    valid_links: int
    broken_links: int
    external_links: int
    internal_links: int
    link_results: List[LinkResult]
    last_checked: str = None

    def __post_init__(self):
        if self.last_checked is None:
            self.last_checked = datetime.now().isoformat()

class DocumentationLinkChecker:
    """Main link checker for CVD documentation system"""
    
    def __init__(self, documentation_root: str = None):
        """Initialize the link checker"""
        if documentation_root is None:
            documentation_root = Path(__file__).parent.parent.parent
        
        self.documentation_root = Path(documentation_root)
        self.reports_dir = self.documentation_root / "maintenance" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.timeout = 30
        self.max_workers = 10
        self.retry_count = 2
        self.cache_duration = 3600  # 1 hour cache for external links
        self.user_agent = "CVD-Documentation-Link-Checker/1.0"
        
        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        
        # Link cache for performance
        self.link_cache = {}
        self.cache_file = self.reports_dir / "link_cache.json"
        self.load_cache()
        
        # Statistics tracking
        self.stats = {
            'total_files': 0,
            'total_links': 0,
            'internal_links': 0,
            'external_links': 0,
            'valid_links': 0,
            'broken_links': 0,
            'redirected_links': 0,
            'timeout_links': 0,
            'error_links': 0,
            'check_duration': 0,
            'files_with_issues': 0
        }
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.reports_dir / "link_checker.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_cache(self):
        """Load link cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    # Filter out expired cache entries
                    current_time = time.time()
                    self.link_cache = {
                        url: data for url, data in cache_data.items()
                        if current_time - data.get('timestamp', 0) < self.cache_duration
                    }
                self.logger.info(f"Loaded {len(self.link_cache)} cached link results")
        except Exception as e:
            self.logger.warning(f"Could not load link cache: {e}")
            self.link_cache = {}
    
    def save_cache(self):
        """Save link cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.link_cache, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save link cache: {e}")
    
    def extract_links_from_file(self, file_path: Path) -> List[Tuple[str, str]]:
        """Extract all links from a markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            links = []
            
            # Regular markdown links [text](url)
            markdown_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
            for match in re.finditer(markdown_pattern, content):
                text, url = match.groups()
                links.append((url.strip(), 'markdown'))
            
            # Reference links [text][ref] and [ref]: url
            ref_links = {}
            ref_pattern = r'^\s*\[([^\]]+)\]:\s*(.+)$'
            for match in re.finditer(ref_pattern, content, re.MULTILINE):
                ref, url = match.groups()
                ref_links[ref.strip()] = url.strip()
            
            ref_usage_pattern = r'\[([^\]]*)\]\[([^\]]+)\]'
            for match in re.finditer(ref_usage_pattern, content):
                text, ref = match.groups()
                if ref in ref_links:
                    links.append((ref_links[ref], 'reference'))
            
            # HTML links <a href="url">
            html_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>'
            for match in re.finditer(html_pattern, content, re.IGNORECASE):
                url = match.group(1)
                links.append((url.strip(), 'html'))
            
            # Image links ![alt](url)
            image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
            for match in re.finditer(image_pattern, content):
                alt, url = match.groups()
                links.append((url.strip(), 'image'))
            
            return links
            
        except Exception as e:
            self.logger.error(f"Error extracting links from {file_path}: {e}")
            return []
    
    def is_internal_link(self, url: str) -> bool:
        """Check if a link is internal to the documentation"""
        # Skip anchors, mailto, javascript, etc.
        if url.startswith(('#', 'mailto:', 'javascript:', 'tel:', 'ftp:')):
            return False
        
        # Check if it's a relative path or absolute path within docs
        if not url.startswith(('http://', 'https://')):
            return True
        
        # Check if it's an absolute URL to the same domain (if configured)
        return False
    
    def resolve_internal_link(self, url: str, source_file: Path) -> Path:
        """Resolve internal link to absolute file path"""
        if url.startswith('/'):
            # Absolute path from documentation root
            return self.documentation_root / url.lstrip('/')
        else:
            # Relative path from source file directory
            return source_file.parent / url
    
    def check_internal_link(self, url: str, source_file: Path) -> LinkResult:
        """Check if an internal link is valid"""
        try:
            # Remove fragment identifier
            clean_url = url.split('#')[0] if '#' in url else url
            if not clean_url:  # Just a fragment
                return LinkResult(url, 'valid')
            
            # Resolve the path
            target_path = self.resolve_internal_link(clean_url, source_file)
            
            # Handle directory links (should point to index or README)
            if target_path.is_dir():
                possible_files = ['index.md', 'README.md', 'index.html']
                found = False
                for possible_file in possible_files:
                    if (target_path / possible_file).exists():
                        found = True
                        break
                if not found:
                    return LinkResult(url, 'broken', error_message=f"Directory {target_path} has no index file")
            elif not target_path.exists():
                return LinkResult(url, 'broken', error_message=f"File not found: {target_path}")
            
            return LinkResult(url, 'valid')
            
        except Exception as e:
            return LinkResult(url, 'error', error_message=str(e))
    
    def check_external_link(self, url: str) -> LinkResult:
        """Check if an external link is valid"""
        # Check cache first
        cache_key = url
        if cache_key in self.link_cache:
            cached = self.link_cache[cache_key]
            if time.time() - cached['timestamp'] < self.cache_duration:
                result = LinkResult(**cached['result'])
                result.last_checked = cached['timestamp']
                return result
        
        start_time = time.time()
        
        for attempt in range(self.retry_count + 1):
            try:
                response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = LinkResult(url, 'valid', response.status_code, response_time)
                elif 300 <= response.status_code < 400:
                    result = LinkResult(url, 'redirect', response.status_code, response_time, redirect_url=response.url)
                else:
                    # Try GET request if HEAD fails
                    try:
                        get_response = self.session.get(url, timeout=self.timeout, stream=True)
                        if get_response.status_code == 200:
                            result = LinkResult(url, 'valid', get_response.status_code, response_time)
                        else:
                            result = LinkResult(url, 'broken', get_response.status_code, response_time)
                    except:
                        result = LinkResult(url, 'broken', response.status_code, response_time)
                
                # Cache the result
                self.link_cache[cache_key] = {
                    'result': asdict(result),
                    'timestamp': time.time()
                }
                
                return result
                
            except requests.exceptions.Timeout:
                if attempt == self.retry_count:
                    result = LinkResult(url, 'timeout', error_message="Request timeout")
                    return result
                time.sleep(1)  # Wait before retry
                
            except requests.exceptions.RequestException as e:
                if attempt == self.retry_count:
                    result = LinkResult(url, 'error', error_message=str(e))
                    return result
                time.sleep(1)  # Wait before retry
            
            except Exception as e:
                result = LinkResult(url, 'error', error_message=str(e))
                return result
        
        return LinkResult(url, 'error', error_message="Max retries exceeded")
    
    def check_file_links(self, file_path: Path) -> FileReport:
        """Check all links in a single file"""
        self.logger.info(f"Checking links in: {file_path.relative_to(self.documentation_root)}")
        
        links = self.extract_links_from_file(file_path)
        link_results = []
        
        internal_count = 0
        external_count = 0
        valid_count = 0
        broken_count = 0
        
        # Check each link
        for url, link_type in links:
            if self.is_internal_link(url):
                internal_count += 1
                result = self.check_internal_link(url, file_path)
            else:
                external_count += 1
                result = self.check_external_link(url)
            
            link_results.append(result)
            
            # Update counters
            if result.status == 'valid':
                valid_count += 1
            elif result.status in ['broken', 'timeout', 'error']:
                broken_count += 1
            
            # Small delay to be respectful
            time.sleep(0.1)
        
        return FileReport(
            file_path=str(file_path.relative_to(self.documentation_root)),
            total_links=len(links),
            valid_links=valid_count,
            broken_links=broken_count,
            external_links=external_count,
            internal_links=internal_count,
            link_results=link_results
        )
    
    def check_all_links(self) -> Dict:
        """Check all links in the documentation"""
        start_time = time.time()
        self.logger.info("Starting comprehensive link check...")
        
        # Find all markdown files
        md_files = list(self.documentation_root.rglob("*.md"))
        self.stats['total_files'] = len(md_files)
        
        file_reports = []
        
        # Process files
        for file_path in md_files:
            try:
                report = self.check_file_links(file_path)
                file_reports.append(report)
                
                # Update statistics
                self.stats['total_links'] += report.total_links
                self.stats['internal_links'] += report.internal_links
                self.stats['external_links'] += report.external_links
                self.stats['valid_links'] += report.valid_links
                self.stats['broken_links'] += report.broken_links
                
                if report.broken_links > 0:
                    self.stats['files_with_issues'] += 1
                
                # Count specific result types
                for result in report.link_results:
                    if result.status == 'redirect':
                        self.stats['redirected_links'] += 1
                    elif result.status == 'timeout':
                        self.stats['timeout_links'] += 1
                    elif result.status == 'error':
                        self.stats['error_links'] += 1
                
            except Exception as e:
                self.logger.error(f"Error checking file {file_path}: {e}")
        
        self.stats['check_duration'] = time.time() - start_time
        
        # Save cache
        self.save_cache()
        
        # Generate report
        report = self.generate_report(file_reports)
        
        self.logger.info(f"Link check completed in {self.stats['check_duration']:.2f} seconds")
        self.logger.info(f"Total links: {self.stats['total_links']}, Valid: {self.stats['valid_links']}, Broken: {self.stats['broken_links']}")
        
        return report
    
    def generate_report(self, file_reports: List[FileReport]) -> Dict:
        """Generate comprehensive link check report"""
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator': 'CVD Documentation Link Checker',
                'version': '1.0.0',
                'documentation_root': str(self.documentation_root)
            },
            'summary': dict(self.stats),
            'file_reports': [asdict(report) for report in file_reports],
            'broken_links_summary': self.get_broken_links_summary(file_reports),
            'external_domains': self.get_external_domains_summary(file_reports),
            'recommendations': self.generate_recommendations(file_reports)
        }
        
        # Save detailed report
        report_file = self.reports_dir / f"link_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save latest report
        latest_file = self.reports_dir / "link_check_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate human-readable summary
        self.generate_summary_report(report)
        
        return report
    
    def get_broken_links_summary(self, file_reports: List[FileReport]) -> List[Dict]:
        """Get summary of all broken links"""
        broken_links = []
        
        for report in file_reports:
            for result in report.link_results:
                if result.status in ['broken', 'timeout', 'error']:
                    broken_links.append({
                        'file': report.file_path,
                        'url': result.url,
                        'status': result.status,
                        'error': result.error_message,
                        'status_code': result.status_code
                    })
        
        return broken_links
    
    def get_external_domains_summary(self, file_reports: List[FileReport]) -> Dict:
        """Get summary of external domains and their status"""
        domains = defaultdict(lambda: {'total': 0, 'valid': 0, 'broken': 0})
        
        for report in file_reports:
            for result in report.link_results:
                if not self.is_internal_link(result.url):
                    try:
                        domain = urlparse(result.url).netloc
                        domains[domain]['total'] += 1
                        if result.status == 'valid':
                            domains[domain]['valid'] += 1
                        elif result.status in ['broken', 'timeout', 'error']:
                            domains[domain]['broken'] += 1
                    except:
                        pass
        
        return dict(domains)
    
    def generate_recommendations(self, file_reports: List[FileReport]) -> List[str]:
        """Generate recommendations based on link check results"""
        recommendations = []
        
        broken_ratio = self.stats['broken_links'] / max(self.stats['total_links'], 1)
        if broken_ratio > 0.05:  # More than 5% broken links
            recommendations.append(f"High broken link ratio ({broken_ratio:.1%}). Prioritize fixing broken links.")
        
        if self.stats['timeout_links'] > 10:
            recommendations.append(f"{self.stats['timeout_links']} links timed out. Consider reviewing external link timeouts.")
        
        if self.stats['redirected_links'] > 20:
            recommendations.append(f"{self.stats['redirected_links']} links are redirected. Update to final URLs for better performance.")
        
        files_with_issues_ratio = self.stats['files_with_issues'] / max(self.stats['total_files'], 1)
        if files_with_issues_ratio > 0.2:
            recommendations.append(f"{files_with_issues_ratio:.1%} of files have link issues. Implement regular link checking.")
        
        return recommendations
    
    def generate_summary_report(self, report: Dict):
        """Generate human-readable summary report"""
        summary_file = self.reports_dir / "link_check_summary.md"
        
        with open(summary_file, 'w') as f:
            f.write("# CVD Documentation Link Check Summary\n\n")
            f.write(f"**Generated**: {report['metadata']['generated_at']}\n\n")
            
            # Overall statistics
            f.write("## Overall Statistics\n\n")
            stats = report['summary']
            f.write(f"- **Total Files**: {stats['total_files']}\n")
            f.write(f"- **Total Links**: {stats['total_links']}\n")
            f.write(f"- **Valid Links**: {stats['valid_links']} ({stats['valid_links']/max(stats['total_links'],1):.1%})\n")
            f.write(f"- **Broken Links**: {stats['broken_links']} ({stats['broken_links']/max(stats['total_links'],1):.1%})\n")
            f.write(f"- **Internal Links**: {stats['internal_links']}\n")
            f.write(f"- **External Links**: {stats['external_links']}\n")
            f.write(f"- **Check Duration**: {stats['check_duration']:.2f} seconds\n\n")
            
            # Broken links
            if report['broken_links_summary']:
                f.write("## Broken Links\n\n")
                for broken in report['broken_links_summary'][:20]:  # Limit to first 20
                    f.write(f"- **{broken['file']}**: {broken['url']} ({broken['status']})\n")
                    if broken['error']:
                        f.write(f"  - Error: {broken['error']}\n")
                if len(report['broken_links_summary']) > 20:
                    f.write(f"\n*... and {len(report['broken_links_summary']) - 20} more broken links*\n")
                f.write("\n")
            
            # Recommendations
            if report['recommendations']:
                f.write("## Recommendations\n\n")
                for rec in report['recommendations']:
                    f.write(f"- {rec}\n")
                f.write("\n")
            
            # External domains
            f.write("## External Domains Summary\n\n")
            domains = report['external_domains']
            for domain, stats in sorted(domains.items(), key=lambda x: x[1]['total'], reverse=True)[:10]:
                success_rate = stats['valid'] / max(stats['total'], 1)
                f.write(f"- **{domain}**: {stats['total']} links ({success_rate:.1%} success rate)\n")
    
    def schedule_check(self, interval_hours: int = 24):
        """Schedule regular link checking"""
        self.logger.info(f"Scheduling link checks every {interval_hours} hours")
        
        while True:
            try:
                self.check_all_links()
                time.sleep(interval_hours * 3600)
            except KeyboardInterrupt:
                self.logger.info("Link checker stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in scheduled link check: {e}")
                time.sleep(3600)  # Wait 1 hour before retry

def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='CVD Documentation Link Checker')
    parser.add_argument('--check', action='store_true', help='Run link check once')
    parser.add_argument('--schedule', type=int, help='Schedule checks every N hours')
    parser.add_argument('--file', type=str, help='Check links in specific file')
    parser.add_argument('--external-only', action='store_true', help='Check only external links')
    parser.add_argument('--internal-only', action='store_true', help='Check only internal links')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    parser.add_argument('--workers', type=int, default=10, help='Number of worker threads')
    
    args = parser.parse_args()
    
    # Initialize link checker
    checker = DocumentationLinkChecker()
    checker.timeout = args.timeout
    checker.max_workers = args.workers
    
    if args.file:
        # Check single file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File {file_path} not found")
            return 1
        
        report = checker.check_file_links(file_path)
        print(f"File: {report.file_path}")
        print(f"Total links: {report.total_links}")
        print(f"Valid: {report.valid_links}, Broken: {report.broken_links}")
        
        if report.broken_links > 0:
            print("\nBroken links:")
            for result in report.link_results:
                if result.status in ['broken', 'timeout', 'error']:
                    print(f"  - {result.url} ({result.status})")
                    if result.error_message:
                        print(f"    Error: {result.error_message}")
    
    elif args.schedule:
        # Schedule regular checks
        checker.schedule_check(args.schedule)
    
    elif args.check:
        # Run single comprehensive check
        report = checker.check_all_links()
        print(f"Link check completed. Report saved to: {checker.reports_dir}")
        
        # Print summary
        stats = report['summary']
        print(f"Total links: {stats['total_links']}")
        print(f"Valid: {stats['valid_links']} ({stats['valid_links']/max(stats['total_links'],1):.1%})")
        print(f"Broken: {stats['broken_links']} ({stats['broken_links']/max(stats['total_links'],1):.1%})")
        
        return 1 if stats['broken_links'] > 0 else 0
    
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())