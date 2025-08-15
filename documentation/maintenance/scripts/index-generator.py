#!/usr/bin/env python3
"""
CVD Documentation Index Generator
Automated search index rebuilding and optimization for the CVD documentation system.

Features:
- Automated search index rebuilding
- Index optimization and performance tuning
- Incremental index updates
- Search analytics integration
- Performance monitoring
- Index health validation
- Integration with existing search.py system
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
import hashlib

# Import the existing search engine
sys.path.append(str(Path(__file__).parent.parent.parent / "00-index" / "scripts"))
from search import DocumentationSearchEngine, SearchQuery

@dataclass
class IndexMetrics:
    """Metrics for index performance and health"""
    total_documents: int
    total_terms: int
    index_size_mb: float
    build_time_seconds: float
    search_performance_ms: float
    memory_usage_mb: float
    last_updated: str
    health_score: float  # 0-100

@dataclass
class IndexChangeDetection:
    """Track changes for incremental updates"""
    file_path: str
    last_modified: float
    content_hash: str
    needs_update: bool = False

class DocumentationIndexGenerator:
    """Enhanced index generator with optimization and monitoring"""
    
    def __init__(self, documentation_root: str = None):
        """Initialize the index generator"""
        if documentation_root is None:
            documentation_root = Path(__file__).parent.parent.parent
        
        self.documentation_root = Path(documentation_root)
        self.reports_dir = self.documentation_root / "maintenance" / "reports"
        self.cache_dir = self.documentation_root / "maintenance" / "cache"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize search engine
        self.search_engine = DocumentationSearchEngine(self.documentation_root)
        
        # Configuration
        self.incremental_enabled = True
        self.optimization_enabled = True
        self.analytics_enabled = True
        
        # Change tracking
        self.change_tracking_file = self.cache_dir / "file_changes.json"
        self.file_changes = {}
        self.load_change_tracking()
        
        # Performance tracking
        self.performance_log = []
        self.max_performance_entries = 1000
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.reports_dir / "index_generator.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_change_tracking(self):
        """Load file change tracking data"""
        try:
            if self.change_tracking_file.exists():
                with open(self.change_tracking_file, 'r') as f:
                    data = json.load(f)
                    self.file_changes = {
                        path: IndexChangeDetection(**change_data)
                        for path, change_data in data.items()
                    }
                self.logger.info(f"Loaded change tracking for {len(self.file_changes)} files")
        except Exception as e:
            self.logger.warning(f"Could not load change tracking: {e}")
            self.file_changes = {}
    
    def save_change_tracking(self):
        """Save file change tracking data"""
        try:
            data = {
                path: asdict(change_data)
                for path, change_data in self.file_changes.items()
            }
            with open(self.change_tracking_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save change tracking: {e}")
    
    def calculate_content_hash(self, file_path: Path) -> str:
        """Calculate hash of file content for change detection"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()
        except Exception:
            return ""
    
    def detect_changes(self) -> List[IndexChangeDetection]:
        """Detect changes in documentation files"""
        self.logger.info("Detecting file changes...")
        
        changed_files = []
        md_files = list(self.documentation_root.rglob("*.md"))
        
        for file_path in md_files:
            relative_path = str(file_path.relative_to(self.documentation_root))
            
            try:
                stat = file_path.stat()
                current_modified = stat.st_mtime
                current_hash = self.calculate_content_hash(file_path)
                
                if relative_path in self.file_changes:
                    previous = self.file_changes[relative_path]
                    if (current_modified != previous.last_modified or 
                        current_hash != previous.content_hash):
                        # File has changed
                        change = IndexChangeDetection(
                            file_path=relative_path,
                            last_modified=current_modified,
                            content_hash=current_hash,
                            needs_update=True
                        )
                        changed_files.append(change)
                        self.file_changes[relative_path] = change
                else:
                    # New file
                    change = IndexChangeDetection(
                        file_path=relative_path,
                        last_modified=current_modified,
                        content_hash=current_hash,
                        needs_update=True
                    )
                    changed_files.append(change)
                    self.file_changes[relative_path] = change
            
            except Exception as e:
                self.logger.warning(f"Error checking file {file_path}: {e}")
        
        # Check for deleted files
        existing_files = {str(f.relative_to(self.documentation_root)) for f in md_files}
        deleted_files = [path for path in self.file_changes.keys() if path not in existing_files]
        
        for deleted_path in deleted_files:
            del self.file_changes[deleted_path]
            self.logger.info(f"Detected deleted file: {deleted_path}")
        
        self.logger.info(f"Detected {len(changed_files)} changed files, {len(deleted_files)} deleted files")
        return changed_files
    
    def build_full_index(self) -> IndexMetrics:
        """Build complete search index from scratch"""
        self.logger.info("Building full search index...")
        start_time = time.time()
        
        # Build index using search engine
        processed_count = self.search_engine.build_index()
        
        # Save the index
        if not self.search_engine.save_index():
            raise Exception("Failed to save search index")
        
        build_time = time.time() - start_time
        
        # Calculate metrics
        metrics = self.calculate_index_metrics(build_time)
        
        # Update change tracking
        self.update_change_tracking_after_build()
        
        self.logger.info(f"Full index built: {processed_count} files in {build_time:.2f}s")
        return metrics
    
    def build_incremental_index(self, changed_files: List[IndexChangeDetection]) -> IndexMetrics:
        """Build incremental index updates"""
        self.logger.info(f"Building incremental index for {len(changed_files)} files...")
        start_time = time.time()
        
        # Process changed files
        processed_count = 0
        for change in changed_files:
            file_path = self.documentation_root / change.file_path
            if file_path.exists():
                if self.search_engine.process_file(file_path):
                    processed_count += 1
                    change.needs_update = False
            else:
                # File was deleted, remove from index
                if change.file_path in self.search_engine.search_index:
                    del self.search_engine.search_index[change.file_path]
                    self.logger.info(f"Removed deleted file from index: {change.file_path}")
        
        # Save updated index
        if not self.search_engine.save_index():
            raise Exception("Failed to save incremental index update")
        
        build_time = time.time() - start_time
        
        # Calculate metrics
        metrics = self.calculate_index_metrics(build_time)
        
        self.logger.info(f"Incremental index updated: {processed_count} files in {build_time:.2f}s")
        return metrics
    
    def update_change_tracking_after_build(self):
        """Update change tracking after successful index build"""
        md_files = list(self.documentation_root.rglob("*.md"))
        
        for file_path in md_files:
            relative_path = str(file_path.relative_to(self.documentation_root))
            try:
                stat = file_path.stat()
                current_modified = stat.st_mtime
                current_hash = self.calculate_content_hash(file_path)
                
                self.file_changes[relative_path] = IndexChangeDetection(
                    file_path=relative_path,
                    last_modified=current_modified,
                    content_hash=current_hash,
                    needs_update=False
                )
            except Exception as e:
                self.logger.warning(f"Error updating tracking for {file_path}: {e}")
        
        self.save_change_tracking()
    
    def calculate_index_metrics(self, build_time: float) -> IndexMetrics:
        """Calculate comprehensive index metrics"""
        stats = self.search_engine.get_statistics()
        
        # Test search performance
        search_time = self.measure_search_performance()
        
        # Calculate memory usage (approximate)
        memory_usage = self.estimate_memory_usage()
        
        # Calculate health score
        health_score = self.calculate_health_score(stats, search_time, memory_usage)
        
        return IndexMetrics(
            total_documents=stats['total_documents'],
            total_terms=stats['total_terms'],
            index_size_mb=stats['index_size_mb'],
            build_time_seconds=build_time,
            search_performance_ms=search_time,
            memory_usage_mb=memory_usage,
            last_updated=datetime.now().isoformat(),
            health_score=health_score
        )
    
    def measure_search_performance(self) -> float:
        """Measure search performance with test queries"""
        test_queries = [
            "authentication",
            "device management",
            "API endpoints",
            "planogram",
            "service orders"
        ]
        
        total_time = 0
        test_count = 0
        
        for query_text in test_queries:
            try:
                start_time = time.time()
                query = SearchQuery(query=query_text, max_results=10)
                results = self.search_engine.search(query)
                search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                total_time += search_time
                test_count += 1
                
                # Log performance entry
                self.performance_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'query': query_text,
                    'results_count': len(results),
                    'response_time_ms': search_time
                })
                
            except Exception as e:
                self.logger.warning(f"Error testing search performance for '{query_text}': {e}")
        
        # Trim performance log
        if len(self.performance_log) > self.max_performance_entries:
            self.performance_log = self.performance_log[-self.max_performance_entries:]
        
        return total_time / max(test_count, 1)
    
    def estimate_memory_usage(self) -> float:
        """Estimate memory usage of search index"""
        try:
            # Approximate memory usage based on index size and structure
            index_file_size = 0
            if self.search_engine.index_path.exists():
                index_file_size = self.search_engine.index_path.stat().st_size
            
            # Estimate in-memory usage (typically 2-3x file size)
            estimated_memory = (index_file_size * 2.5) / (1024 * 1024)  # Convert to MB
            return estimated_memory
        except Exception:
            return 0.0
    
    def calculate_health_score(self, stats: Dict, search_time: float, memory_usage: float) -> float:
        """Calculate overall index health score"""
        score = 100.0
        
        # Deduct for slow search performance
        if search_time > 100:  # >100ms average
            score -= min(20, (search_time - 100) / 10)
        
        # Deduct for large memory usage
        if memory_usage > 100:  # >100MB
            score -= min(15, (memory_usage - 100) / 20)
        
        # Deduct for missing documents
        expected_docs = len(list(self.documentation_root.rglob("*.md")))
        if stats['total_documents'] < expected_docs * 0.95:  # Less than 95% coverage
            score -= 20
        
        # Deduct for very few terms (indicates indexing issues)
        if stats['total_terms'] < 1000:
            score -= 15
        
        return max(0, score)
    
    def optimize_index(self) -> Dict:
        """Optimize search index for better performance"""
        self.logger.info("Optimizing search index...")
        
        optimization_results = {
            'cleaned_terms': 0,
            'compressed_size': 0,
            'performance_improvement': 0.0
        }
        
        # Remove very rare terms (appear in <0.1% of documents)
        min_doc_threshold = max(1, int(len(self.search_engine.search_index) * 0.001))
        rare_terms = []
        
        for term, docs in self.search_engine.inverted_index.items():
            if len(docs) < min_doc_threshold and len(term) > 3:
                rare_terms.append(term)
        
        # Remove rare terms
        for term in rare_terms:
            del self.search_engine.inverted_index[term]
        
        optimization_results['cleaned_terms'] = len(rare_terms)
        
        # Optimize synonym expansion
        self.optimize_synonyms()
        
        # Save optimized index
        self.search_engine.save_index()
        
        self.logger.info(f"Index optimization completed: removed {len(rare_terms)} rare terms")
        return optimization_results
    
    def optimize_synonyms(self):
        """Optimize synonym mapping for better search results"""
        # Add commonly searched but missing terms
        common_searches = [
            'vending machine', 'cooler', 'device',
            'product placement', 'slot assignment',
            'work order', 'maintenance task',
            'route planning', 'delivery schedule'
        ]
        
        for search_term in common_searches:
            # Find best matching existing terms
            matches = []
            for term in self.search_engine.inverted_index:
                if any(word in term for word in search_term.split()):
                    matches.append(term)
            
            if matches:
                # Add to synonym mapping
                if search_term not in self.search_engine.synonyms:
                    self.search_engine.synonyms[search_term] = matches[:3]  # Limit to top 3
    
    def validate_index_health(self) -> Dict:
        """Validate index health and detect issues"""
        self.logger.info("Validating index health...")
        
        issues = []
        warnings = []
        
        stats = self.search_engine.get_statistics()
        
        # Check document coverage
        expected_docs = len(list(self.documentation_root.rglob("*.md")))
        coverage = stats['total_documents'] / max(expected_docs, 1)
        
        if coverage < 0.9:
            issues.append(f"Low document coverage: {coverage:.1%} (expected >90%)")
        elif coverage < 0.95:
            warnings.append(f"Document coverage could be improved: {coverage:.1%}")
        
        # Check search performance
        avg_search_time = self.measure_search_performance()
        if avg_search_time > 200:
            issues.append(f"Slow search performance: {avg_search_time:.1f}ms (target <100ms)")
        elif avg_search_time > 100:
            warnings.append(f"Search performance suboptimal: {avg_search_time:.1f}ms")
        
        # Check index size
        if stats['index_size_mb'] > 50:
            warnings.append(f"Large index size: {stats['index_size_mb']:.1f}MB")
        
        # Check term count
        if stats['total_terms'] < 1000:
            issues.append(f"Very few indexed terms: {stats['total_terms']} (may indicate indexing problems)")
        
        health_report = {
            'status': 'healthy' if not issues else 'issues_detected',
            'issues': issues,
            'warnings': warnings,
            'metrics': stats,
            'recommendations': self.generate_health_recommendations(issues, warnings, stats)
        }
        
        return health_report
    
    def generate_health_recommendations(self, issues: List[str], warnings: List[str], stats: Dict) -> List[str]:
        """Generate recommendations for index health improvement"""
        recommendations = []
        
        if issues:
            recommendations.append("Address critical issues immediately to restore index health")
        
        if stats['index_size_mb'] > 30:
            recommendations.append("Consider index optimization to reduce size and improve performance")
        
        if len(warnings) > 3:
            recommendations.append("Multiple warnings detected - schedule comprehensive index rebuild")
        
        if stats['total_documents'] > 200:
            recommendations.append("Large documentation set - consider implementing index partitioning")
        
        return recommendations
    
    def generate_index_report(self, metrics: IndexMetrics, health_report: Dict) -> Dict:
        """Generate comprehensive index report"""
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator': 'CVD Documentation Index Generator',
                'version': '1.0.0',
                'documentation_root': str(self.documentation_root)
            },
            'metrics': asdict(metrics),
            'health': health_report,
            'performance_history': self.performance_log[-50:],  # Last 50 searches
            'file_changes': {
                'total_tracked': len(self.file_changes),
                'pending_updates': sum(1 for c in self.file_changes.values() if c.needs_update)
            },
            'recommendations': self.generate_overall_recommendations(metrics, health_report)
        }
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f"index_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save latest report
        latest_file = self.reports_dir / "index_report_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def generate_overall_recommendations(self, metrics: IndexMetrics, health_report: Dict) -> List[str]:
        """Generate overall recommendations for index management"""
        recommendations = []
        
        if metrics.health_score < 80:
            recommendations.append("Index health below 80% - schedule immediate optimization")
        
        if metrics.search_performance_ms > 100:
            recommendations.append("Search performance degraded - consider index optimization")
        
        if health_report['status'] == 'issues_detected':
            recommendations.append("Critical issues detected - address immediately")
        
        if metrics.total_documents > 150:
            recommendations.append("Large documentation set - implement automated index maintenance")
        
        return recommendations
    
    def schedule_index_maintenance(self, interval_hours: int = 4):
        """Schedule regular index maintenance"""
        self.logger.info(f"Scheduling index maintenance every {interval_hours} hours")
        
        while True:
            try:
                # Check for changes
                changed_files = self.detect_changes()
                
                if changed_files and self.incremental_enabled:
                    # Incremental update
                    metrics = self.build_incremental_index(changed_files)
                elif not changed_files and len(self.file_changes) > 0:
                    # No changes, just validate health
                    health_report = self.validate_index_health()
                    if health_report['status'] == 'issues_detected':
                        self.logger.warning("Health issues detected, rebuilding index")
                        metrics = self.build_full_index()
                    else:
                        self.logger.info("No changes detected, index is healthy")
                        time.sleep(interval_hours * 3600)
                        continue
                else:
                    # Full rebuild
                    metrics = self.build_full_index()
                
                # Generate report
                health_report = self.validate_index_health()
                self.generate_index_report(metrics, health_report)
                
                # Optimize if needed
                if self.optimization_enabled and metrics.health_score < 85:
                    self.optimize_index()
                
                time.sleep(interval_hours * 3600)
                
            except KeyboardInterrupt:
                self.logger.info("Index maintenance stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in scheduled maintenance: {e}")
                time.sleep(3600)  # Wait 1 hour before retry

def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='CVD Documentation Index Generator')
    parser.add_argument('--build', action='store_true', help='Build full index')
    parser.add_argument('--incremental', action='store_true', help='Build incremental index update')
    parser.add_argument('--optimize', action='store_true', help='Optimize existing index')
    parser.add_argument('--validate', action='store_true', help='Validate index health')
    parser.add_argument('--schedule', type=int, help='Schedule maintenance every N hours')
    parser.add_argument('--report', action='store_true', help='Generate index report')
    parser.add_argument('--performance', action='store_true', help='Run performance tests')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = DocumentationIndexGenerator()
    
    if args.build:
        # Build full index
        metrics = generator.build_full_index()
        print(f"Index built successfully")
        print(f"Documents: {metrics.total_documents}, Terms: {metrics.total_terms}")
        print(f"Build time: {metrics.build_time_seconds:.2f}s")
        print(f"Health score: {metrics.health_score:.1f}/100")
        return 0
    
    elif args.incremental:
        # Build incremental update
        changed_files = generator.detect_changes()
        if changed_files:
            metrics = generator.build_incremental_index(changed_files)
            print(f"Incremental update completed: {len(changed_files)} files processed")
            print(f"Health score: {metrics.health_score:.1f}/100")
        else:
            print("No changes detected")
        return 0
    
    elif args.optimize:
        # Optimize index
        results = generator.optimize_index()
        print(f"Index optimized: {results['cleaned_terms']} terms removed")
        return 0
    
    elif args.validate:
        # Validate index health
        health_report = generator.validate_index_health()
        print(f"Index status: {health_report['status']}")
        
        if health_report['issues']:
            print(f"Issues ({len(health_report['issues'])}):")
            for issue in health_report['issues']:
                print(f"  - {issue}")
        
        if health_report['warnings']:
            print(f"Warnings ({len(health_report['warnings'])}):")
            for warning in health_report['warnings']:
                print(f"  - {warning}")
        
        return 1 if health_report['issues'] else 0
    
    elif args.performance:
        # Run performance tests
        search_time = generator.measure_search_performance()
        print(f"Average search performance: {search_time:.1f}ms")
        return 0
    
    elif args.report:
        # Generate comprehensive report
        metrics = generator.calculate_index_metrics(0)
        health_report = generator.validate_index_health()
        report = generator.generate_index_report(metrics, health_report)
        
        print(f"Index report generated: {generator.reports_dir}")
        print(f"Health score: {metrics.health_score:.1f}/100")
        print(f"Search performance: {metrics.search_performance_ms:.1f}ms")
        return 0
    
    elif args.schedule:
        # Schedule maintenance
        generator.schedule_index_maintenance(args.schedule)
        return 0
    
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())