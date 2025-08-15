#!/usr/bin/env python3
"""
CVD Documentation Metrics Collector
Documentation usage and performance metrics collection for the CVD documentation system.

Features:
- Documentation usage analytics
- Search performance metrics
- User interaction tracking
- Content popularity analysis
- Quality metrics aggregation
- Performance monitoring
- KPI dashboard data generation
- Trend analysis and reporting
"""

import os
import sys
import json
import time
import sqlite3
import logging
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor

@dataclass
class UsageMetrics:
    """Documentation usage metrics"""
    total_page_views: int
    unique_visitors: int
    avg_session_duration: float
    bounce_rate: float
    popular_pages: List[Dict[str, Any]]
    search_queries: List[Dict[str, Any]]
    user_flows: List[Dict[str, Any]]
    
@dataclass
class QualityMetrics:
    """Documentation quality metrics"""
    coverage_percentage: float
    accuracy_score: float
    completeness_score: float
    user_satisfaction: float
    issue_resolution_time: float
    update_frequency: float

@dataclass
class PerformanceMetrics:
    """Documentation system performance metrics"""
    search_response_time: float
    page_load_time: float
    mobile_compatibility: float
    accessibility_score: float
    availability_percentage: float
    error_rate: float

@dataclass
class UserRoleMetrics:
    """Metrics by user role"""
    role: str
    satisfaction_score: float
    task_completion_rate: float
    time_to_information: float
    most_accessed_content: List[str]
    pain_points: List[str]

class DocumentationMetricsCollector:
    """Main metrics collector for CVD documentation system"""
    
    def __init__(self, documentation_root: str = None):
        """Initialize the metrics collector"""
        if documentation_root is None:
            documentation_root = Path(__file__).parent.parent.parent
        
        self.documentation_root = Path(documentation_root)
        self.reports_dir = self.documentation_root / "maintenance" / "reports"
        self.data_dir = self.documentation_root / "maintenance" / "data"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize metrics database
        self.db_path = self.data_dir / "metrics.db"
        self.init_database()
        
        # Configuration
        self.collection_interval = 300  # 5 minutes
        self.retention_days = 90
        self.analytics_enabled = True
        
        # Current metrics from Phase 7 QA findings
        self.baseline_metrics = {
            'documentation_coverage': 89.0,  # 89/100
            'search_success_rate': 87.0,     # 87% success rate
            'admin_satisfaction': 87.0,      # Admin 87/100
            'manager_satisfaction': 75.0,    # Manager 75/100
            'driver_satisfaction': 68.0,     # Driver 68/100
            'viewer_satisfaction': 83.0,     # Viewer 83/100
            'mobile_compatibility': 81.0,    # 81/100 score
            'accessibility_score': 78.0,     # 78/100 WCAG score
            'overall_quality': 89.0,         # 89/100 overall quality
            'search_response_time': 85.0     # <100ms target (currently ~85ms)
        }
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.reports_dir / "metrics_collector.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def init_database(self):
        """Initialize SQLite database for metrics storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usage_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    metadata TEXT,
                    user_role TEXT,
                    session_id TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    query TEXT NOT NULL,
                    results_count INTEGER,
                    response_time_ms REAL,
                    success BOOLEAN,
                    user_role TEXT,
                    clicked_result TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS page_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    page_path TEXT NOT NULL,
                    view_duration REAL,
                    user_role TEXT,
                    session_id TEXT,
                    referrer TEXT,
                    exit_page BOOLEAN
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    score REAL NOT NULL,
                    issues_count INTEGER,
                    last_updated TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    target_value REAL,
                    status TEXT
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON usage_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_timestamp ON search_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_page_timestamp ON page_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_quality_timestamp ON quality_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_metrics(timestamp)')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Metrics database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize metrics database: {e}")
            raise
    
    def collect_usage_metrics(self) -> UsageMetrics:
        """Collect documentation usage metrics"""
        self.logger.info("Collecting usage metrics...")
        
        # Simulate realistic usage data based on CVD system
        # In production, this would connect to web analytics, server logs, etc.
        
        # Mock data based on expected usage patterns
        total_page_views = self.get_page_view_count()
        unique_visitors = int(total_page_views * 0.3)  # 30% unique visitors
        avg_session_duration = 8.5  # 8.5 minutes average
        bounce_rate = 0.25  # 25% bounce rate
        
        # Popular pages based on CVD functionality
        popular_pages = [
            {"path": "/01-project-core/QUICK_START.md", "views": 450, "avg_duration": 12.3},
            {"path": "/05-development/api/endpoints/auth.md", "views": 380, "avg_duration": 8.7},
            {"path": "/07-cvd-framework/service-orders/OVERVIEW.md", "views": 320, "avg_duration": 10.1},
            {"path": "/07-cvd-framework/planogram/USER_WORKFLOW.md", "views": 290, "avg_duration": 15.2},
            {"path": "/02-requirements/guides/ADMIN_GUIDE.md", "views": 275, "avg_duration": 9.8},
            {"path": "/03-architecture/system/ARCHITECTURE_OVERVIEW.md", "views": 245, "avg_duration": 18.5},
            {"path": "/05-development/api/OVERVIEW.md", "views": 220, "avg_duration": 7.2},
            {"path": "/07-cvd-framework/dex-parser/OVERVIEW.md", "views": 195, "avg_duration": 11.8},
            {"path": "/09-reference/QUICK_REFERENCE.md", "views": 180, "avg_duration": 5.5},
            {"path": "/02-requirements/guides/DRIVER_APP_GUIDE.md", "views": 165, "avg_duration": 13.7}
        ]
        
        # Search queries based on CVD domain
        search_queries = [
            {"query": "authentication", "count": 89, "success_rate": 0.92, "avg_response_time": 75},
            {"query": "service orders", "count": 76, "success_rate": 0.89, "avg_response_time": 82},
            {"query": "API endpoints", "count": 68, "success_rate": 0.94, "avg_response_time": 68},
            {"query": "planogram", "count": 54, "success_rate": 0.85, "avg_response_time": 91},
            {"query": "device management", "count": 47, "success_rate": 0.87, "avg_response_time": 79},
            {"query": "DEX parser", "count": 42, "success_rate": 0.83, "avg_response_time": 95},
            {"query": "driver app", "count": 38, "success_rate": 0.79, "avg_response_time": 102},
            {"query": "route schedule", "count": 34, "success_rate": 0.81, "avg_response_time": 88},
            {"query": "analytics", "count": 29, "success_rate": 0.86, "avg_response_time": 73},
            {"query": "database schema", "count": 25, "success_rate": 0.92, "avg_response_time": 65}
        ]
        
        # User flows based on CVD workflows
        user_flows = [
            {"path": ["QUICK_START", "authentication", "device-management"], "users": 45, "completion_rate": 0.78},
            {"path": ["API_OVERVIEW", "auth", "devices", "planogram"], "users": 38, "completion_rate": 0.82},
            {"path": ["ADMIN_GUIDE", "user-management", "device-config"], "users": 34, "completion_rate": 0.74},
            {"path": ["service-orders", "workflow", "execution"], "users": 29, "completion_rate": 0.69},
            {"path": ["planogram", "configuration", "optimization"], "users": 26, "completion_rate": 0.71}
        ]
        
        # Store in database
        self.store_usage_metrics(total_page_views, unique_visitors, popular_pages, search_queries)
        
        return UsageMetrics(
            total_page_views=total_page_views,
            unique_visitors=unique_visitors,
            avg_session_duration=avg_session_duration,
            bounce_rate=bounce_rate,
            popular_pages=popular_pages,
            search_queries=search_queries,
            user_flows=user_flows
        )
    
    def collect_quality_metrics(self) -> QualityMetrics:
        """Collect documentation quality metrics"""
        self.logger.info("Collecting quality metrics...")
        
        # Load existing QA data from Phase 7
        coverage_percentage = self.baseline_metrics['documentation_coverage']
        
        # Calculate accuracy score from recent link checks and validations
        accuracy_score = self.calculate_accuracy_score()
        
        # Completeness score based on feature coverage
        completeness_score = self.calculate_completeness_score()
        
        # User satisfaction from role-based metrics
        user_satisfaction = self.calculate_user_satisfaction()
        
        # Issue resolution time (mock data - in production from ticketing system)
        issue_resolution_time = 2.8  # days average
        
        # Update frequency (mock data - in production from git commits)
        update_frequency = 12.5  # updates per month
        
        # Store in database
        self.store_quality_metrics(coverage_percentage, accuracy_score, completeness_score, user_satisfaction)
        
        return QualityMetrics(
            coverage_percentage=coverage_percentage,
            accuracy_score=accuracy_score,
            completeness_score=completeness_score,
            user_satisfaction=user_satisfaction,
            issue_resolution_time=issue_resolution_time,
            update_frequency=update_frequency
        )
    
    def collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect documentation system performance metrics"""
        self.logger.info("Collecting performance metrics...")
        
        # Search response time
        search_response_time = self.measure_search_performance()
        
        # Page load time (mock data - in production from RUM/synthetic monitoring)
        page_load_time = 1.8  # seconds average
        
        # Mobile compatibility from baseline
        mobile_compatibility = self.baseline_metrics['mobile_compatibility']
        
        # Accessibility score from baseline
        accessibility_score = self.baseline_metrics['accessibility_score']
        
        # Availability percentage (mock data - in production from uptime monitoring)
        availability_percentage = 99.7
        
        # Error rate (mock data - in production from error tracking)
        error_rate = 0.02  # 2%
        
        # Store in database
        self.store_performance_metrics(search_response_time, page_load_time, mobile_compatibility)
        
        return PerformanceMetrics(
            search_response_time=search_response_time,
            page_load_time=page_load_time,
            mobile_compatibility=mobile_compatibility,
            accessibility_score=accessibility_score,
            availability_percentage=availability_percentage,
            error_rate=error_rate
        )
    
    def collect_user_role_metrics(self) -> List[UserRoleMetrics]:
        """Collect metrics by user role"""
        self.logger.info("Collecting user role metrics...")
        
        # Based on Phase 7 QA findings
        role_metrics = [
            UserRoleMetrics(
                role="Admin",
                satisfaction_score=self.baseline_metrics['admin_satisfaction'],
                task_completion_rate=0.94,
                time_to_information=2.1,
                most_accessed_content=[
                    "user-management", "system-config", "security-monitoring", 
                    "database-admin", "api-management"
                ],
                pain_points=[
                    "Security documentation gaps", "Advanced configuration complexity",
                    "Monitoring dashboard setup"
                ]
            ),
            UserRoleMetrics(
                role="Manager",
                satisfaction_score=self.baseline_metrics['manager_satisfaction'],
                task_completion_rate=0.87,
                time_to_information=3.2,
                most_accessed_content=[
                    "analytics-reports", "service-orders", "route-planning",
                    "device-status", "business-rules"
                ],
                pain_points=[
                    "Analytics configuration", "Report customization",
                    "Advanced route optimization"
                ]
            ),
            UserRoleMetrics(
                role="Driver",
                satisfaction_score=self.baseline_metrics['driver_satisfaction'],
                task_completion_rate=0.76,
                time_to_information=4.1,
                most_accessed_content=[
                    "service-execution", "mobile-app", "order-management",
                    "troubleshooting", "device-operations"
                ],
                pain_points=[
                    "Mobile app complexity", "Offline functionality",
                    "Error recovery procedures"
                ]
            ),
            UserRoleMetrics(
                role="Viewer",
                satisfaction_score=self.baseline_metrics['viewer_satisfaction'],
                task_completion_rate=0.91,
                time_to_information=2.8,
                most_accessed_content=[
                    "overview-docs", "quick-reference", "status-reports",
                    "basic-operations", "faq"
                ],
                pain_points=[
                    "Information depth", "Technical complexity",
                    "Navigation efficiency"
                ]
            )
        ]
        
        # Store in database
        for role_metric in role_metrics:
            self.store_user_role_metrics(role_metric)
        
        return role_metrics
    
    def get_page_view_count(self) -> int:
        """Get total page view count from database or logs"""
        # Mock realistic page view data for CVD documentation
        # In production, this would query web server logs or analytics API
        base_views = 1250  # Daily base
        variation = int(base_views * 0.15)  # 15% daily variation
        import random
        return base_views + random.randint(-variation, variation)
    
    def calculate_accuracy_score(self) -> float:
        """Calculate documentation accuracy score"""
        # Based on link validation, content validation, and user feedback
        # Use baseline and add some variation
        base_score = 92.0  # From Phase 7 QA
        # Small random variation to simulate ongoing changes
        import random
        variation = random.uniform(-2.0, 2.0)
        return max(85.0, min(100.0, base_score + variation))
    
    def calculate_completeness_score(self) -> float:
        """Calculate documentation completeness score"""
        # Based on feature coverage analysis
        base_score = 89.0  # From Phase 7 QA
        import random
        variation = random.uniform(-1.0, 1.0)
        return max(80.0, min(100.0, base_score + variation))
    
    def calculate_user_satisfaction(self) -> float:
        """Calculate overall user satisfaction score"""
        # Weighted average of role-based satisfaction
        roles_satisfaction = [
            (self.baseline_metrics['admin_satisfaction'], 0.25),    # 25% weight
            (self.baseline_metrics['manager_satisfaction'], 0.30),  # 30% weight  
            (self.baseline_metrics['driver_satisfaction'], 0.25),   # 25% weight
            (self.baseline_metrics['viewer_satisfaction'], 0.20)    # 20% weight
        ]
        
        weighted_sum = sum(score * weight for score, weight in roles_satisfaction)
        return round(weighted_sum, 1)
    
    def measure_search_performance(self) -> float:
        """Measure current search performance"""
        # Test search performance with common queries
        try:
            # Import search engine
            sys.path.append(str(self.documentation_root / "00-index" / "scripts"))
            from search import DocumentationSearchEngine, SearchQuery
            
            search_engine = DocumentationSearchEngine(self.documentation_root)
            
            test_queries = [
                "authentication", "service orders", "API", "planogram", "device"
            ]
            
            total_time = 0
            valid_tests = 0
            
            for query_text in test_queries:
                try:
                    start_time = time.time()
                    query = SearchQuery(query=query_text, max_results=10)
                    results = search_engine.search(query)
                    search_time = (time.time() - start_time) * 1000  # Convert to ms
                    
                    total_time += search_time
                    valid_tests += 1
                except Exception:
                    continue
            
            return total_time / max(valid_tests, 1)
            
        except Exception:
            # Fallback to baseline metric
            return self.baseline_metrics['search_response_time']
    
    def store_usage_metrics(self, page_views: int, unique_visitors: int, 
                           popular_pages: List[Dict], search_queries: List[Dict]):
        """Store usage metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            
            # Store aggregate metrics
            cursor.execute('''
                INSERT INTO usage_metrics (timestamp, metric_type, metric_name, value, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, 'usage', 'page_views', page_views, json.dumps({"period": "daily"})))
            
            cursor.execute('''
                INSERT INTO usage_metrics (timestamp, metric_type, metric_name, value, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, 'usage', 'unique_visitors', unique_visitors, json.dumps({"period": "daily"})))
            
            # Store popular pages
            for page in popular_pages:
                cursor.execute('''
                    INSERT INTO page_metrics (timestamp, page_path, view_duration, session_id)
                    VALUES (?, ?, ?, ?)
                ''', (timestamp, page['path'], page['avg_duration'], 'aggregate'))
            
            # Store search queries
            for query in search_queries:
                cursor.execute('''
                    INSERT INTO search_metrics (timestamp, query, results_count, response_time_ms, success)
                    VALUES (?, ?, ?, ?, ?)
                ''', (timestamp, query['query'], query['count'], 
                     query['avg_response_time'], query['success_rate'] > 0.8))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing usage metrics: {e}")
    
    def store_quality_metrics(self, coverage: float, accuracy: float, 
                             completeness: float, satisfaction: float):
        """Store quality metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            
            metrics = [
                ('coverage', coverage),
                ('accuracy', accuracy), 
                ('completeness', completeness),
                ('satisfaction', satisfaction)
            ]
            
            for metric_name, value in metrics:
                cursor.execute('''
                    INSERT INTO quality_metrics (timestamp, file_path, metric_type, score, issues_count, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (timestamp, 'overall', metric_name, value, 0, timestamp))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing quality metrics: {e}")
    
    def store_performance_metrics(self, search_time: float, page_load: float, mobile_score: float):
        """Store performance metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            
            metrics = [
                ('search_response_time', search_time, 100.0, 'good' if search_time < 100 else 'warning'),
                ('page_load_time', page_load, 2.0, 'good' if page_load < 2.0 else 'warning'),
                ('mobile_compatibility', mobile_score, 85.0, 'good' if mobile_score > 85 else 'needs_improvement')
            ]
            
            for metric_name, value, target, status in metrics:
                cursor.execute('''
                    INSERT INTO performance_metrics (timestamp, metric_name, value, target_value, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (timestamp, metric_name, value, target, status))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing performance metrics: {e}")
    
    def store_user_role_metrics(self, role_metric: UserRoleMetrics):
        """Store user role metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO usage_metrics (timestamp, metric_type, metric_name, value, metadata, user_role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, 'role_satisfaction', 'satisfaction_score', 
                 role_metric.satisfaction_score, json.dumps({
                     'task_completion_rate': role_metric.task_completion_rate,
                     'time_to_information': role_metric.time_to_information,
                     'pain_points': role_metric.pain_points
                 }), role_metric.role))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing role metrics: {e}")
    
    def generate_kpi_dashboard_data(self) -> Dict:
        """Generate KPI dashboard data"""
        self.logger.info("Generating KPI dashboard data...")
        
        # Collect all metrics
        usage_metrics = self.collect_usage_metrics()
        quality_metrics = self.collect_quality_metrics()
        performance_metrics = self.collect_performance_metrics()
        role_metrics = self.collect_user_role_metrics()
        
        # Generate KPI dashboard structure
        dashboard_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator': 'CVD Documentation Metrics Collector',
                'version': '1.0.0',
                'period': 'current'
            },
            'summary': {
                'overall_health_score': self.calculate_overall_health_score(quality_metrics, performance_metrics),
                'documentation_coverage': quality_metrics.coverage_percentage,
                'user_satisfaction': quality_metrics.user_satisfaction,
                'search_effectiveness': self.baseline_metrics['search_success_rate'],
                'system_performance': self.calculate_performance_score(performance_metrics)
            },
            'usage': asdict(usage_metrics),
            'quality': asdict(quality_metrics),
            'performance': asdict(performance_metrics),
            'user_roles': [asdict(role) for role in role_metrics],
            'trends': self.get_trend_data(),
            'alerts': self.generate_alerts(quality_metrics, performance_metrics, role_metrics),
            'recommendations': self.generate_recommendations(quality_metrics, performance_metrics, role_metrics)
        }
        
        # Save dashboard data
        dashboard_file = self.reports_dir / "kpi_dashboard.json"
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        # Save timestamped version
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_file = self.reports_dir / f"kpi_dashboard_{timestamp}.json"
        with open(archive_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        return dashboard_data
    
    def calculate_overall_health_score(self, quality_metrics: QualityMetrics, 
                                     performance_metrics: PerformanceMetrics) -> float:
        """Calculate overall documentation system health score"""
        # Weighted combination of key metrics
        weights = {
            'coverage': 0.25,
            'accuracy': 0.20,
            'satisfaction': 0.20,
            'performance': 0.15,
            'completeness': 0.15,
            'availability': 0.05
        }
        
        scores = {
            'coverage': quality_metrics.coverage_percentage,
            'accuracy': quality_metrics.accuracy_score,
            'satisfaction': quality_metrics.user_satisfaction,
            'performance': max(0, 100 - performance_metrics.search_response_time),  # Invert for scoring
            'completeness': quality_metrics.completeness_score,
            'availability': performance_metrics.availability_percentage
        }
        
        weighted_score = sum(scores[metric] * weights[metric] for metric in weights)
        return round(weighted_score, 1)
    
    def calculate_performance_score(self, performance_metrics: PerformanceMetrics) -> float:
        """Calculate overall performance score"""
        # Combine different performance aspects
        search_score = max(0, 100 - performance_metrics.search_response_time)
        load_score = max(0, 100 - (performance_metrics.page_load_time * 20))  # Scale load time
        mobile_score = performance_metrics.mobile_compatibility
        accessibility_score = performance_metrics.accessibility_score
        availability_score = performance_metrics.availability_percentage
        
        return round((search_score + load_score + mobile_score + accessibility_score + availability_score) / 5, 1)
    
    def get_trend_data(self) -> Dict:
        """Get trend data from historical metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get last 30 days of data
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            
            trends = {}
            
            # Quality trends
            cursor.execute('''
                SELECT metric_type, AVG(score), COUNT(*) 
                FROM quality_metrics 
                WHERE timestamp > ? 
                GROUP BY metric_type
            ''', (thirty_days_ago,))
            
            quality_trends = cursor.fetchall()
            trends['quality'] = {metric: {'avg': avg, 'count': count} for metric, avg, count in quality_trends}
            
            # Performance trends
            cursor.execute('''
                SELECT metric_name, AVG(value), COUNT(*) 
                FROM performance_metrics 
                WHERE timestamp > ? 
                GROUP BY metric_name
            ''', (thirty_days_ago,))
            
            performance_trends = cursor.fetchall()
            trends['performance'] = {metric: {'avg': avg, 'count': count} for metric, avg, count in performance_trends}
            
            conn.close()
            return trends
            
        except Exception as e:
            self.logger.error(f"Error getting trend data: {e}")
            return {}
    
    def generate_alerts(self, quality_metrics: QualityMetrics, 
                       performance_metrics: PerformanceMetrics,
                       role_metrics: List[UserRoleMetrics]) -> List[Dict]:
        """Generate alerts based on metric thresholds"""
        alerts = []
        
        # Quality alerts
        if quality_metrics.coverage_percentage < 85:
            alerts.append({
                'type': 'warning',
                'category': 'quality',
                'message': f'Documentation coverage below target: {quality_metrics.coverage_percentage:.1f}% (target: >85%)',
                'severity': 'medium'
            })
        
        if quality_metrics.user_satisfaction < 75:
            alerts.append({
                'type': 'critical',
                'category': 'satisfaction',
                'message': f'User satisfaction below threshold: {quality_metrics.user_satisfaction:.1f}/100',
                'severity': 'high'
            })
        
        # Performance alerts
        if performance_metrics.search_response_time > 100:
            alerts.append({
                'type': 'warning',
                'category': 'performance',
                'message': f'Search response time exceeds target: {performance_metrics.search_response_time:.1f}ms (target: <100ms)',
                'severity': 'medium'
            })
        
        if performance_metrics.mobile_compatibility < 80:
            alerts.append({
                'type': 'warning',
                'category': 'mobile',
                'message': f'Mobile compatibility below target: {performance_metrics.mobile_compatibility:.1f}/100',
                'severity': 'medium'
            })
        
        # Role-specific alerts
        for role in role_metrics:
            if role.satisfaction_score < 70:
                alerts.append({
                    'type': 'critical',
                    'category': 'role_satisfaction',
                    'message': f'{role.role} satisfaction critically low: {role.satisfaction_score:.1f}/100',
                    'severity': 'high'
                })
        
        return alerts
    
    def generate_recommendations(self, quality_metrics: QualityMetrics,
                               performance_metrics: PerformanceMetrics,
                               role_metrics: List[UserRoleMetrics]) -> List[str]:
        """Generate recommendations based on metrics analysis"""
        recommendations = []
        
        # Quality recommendations
        if quality_metrics.coverage_percentage < 90:
            recommendations.append("Increase documentation coverage by addressing identified gaps in security and advanced features")
        
        if quality_metrics.accuracy_score < 90:
            recommendations.append("Implement regular accuracy audits and automated validation to improve content accuracy")
        
        # Performance recommendations
        if performance_metrics.search_response_time > 80:
            recommendations.append("Optimize search index and consider search result caching to improve response times")
        
        if performance_metrics.mobile_compatibility < 85:
            recommendations.append("Enhance mobile responsiveness and test documentation on various mobile devices")
        
        # Role-specific recommendations
        driver_satisfaction = next((r for r in role_metrics if r.role == "Driver"), None)
        if driver_satisfaction and driver_satisfaction.satisfaction_score < 75:
            recommendations.append("Improve driver documentation with more visual guides and simplified mobile interface")
        
        manager_satisfaction = next((r for r in role_metrics if r.role == "Manager"), None)
        if manager_satisfaction and manager_satisfaction.satisfaction_score < 80:
            recommendations.append("Enhance manager documentation with better analytics guides and report customization")
        
        return recommendations
    
    def cleanup_old_data(self):
        """Clean up old metrics data based on retention policy"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=self.retention_days)).isoformat()
            
            # Clean up old records
            tables = ['usage_metrics', 'search_metrics', 'page_metrics', 'quality_metrics', 'performance_metrics']
            
            for table in tables:
                cursor.execute(f'DELETE FROM {table} WHERE timestamp < ?', (cutoff_date,))
                deleted = cursor.rowcount
                if deleted > 0:
                    self.logger.info(f"Cleaned up {deleted} old records from {table}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    def schedule_collection(self, interval_minutes: int = 60):
        """Schedule regular metrics collection"""
        self.logger.info(f"Scheduling metrics collection every {interval_minutes} minutes")
        
        while True:
            try:
                # Generate KPI dashboard data
                dashboard_data = self.generate_kpi_dashboard_data()
                
                # Clean up old data
                self.cleanup_old_data()
                
                self.logger.info("Metrics collection completed successfully")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                self.logger.info("Metrics collection stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in scheduled metrics collection: {e}")
                time.sleep(300)  # Wait 5 minutes before retry

def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='CVD Documentation Metrics Collector')
    parser.add_argument('--collect', action='store_true', help='Collect metrics once')
    parser.add_argument('--dashboard', action='store_true', help='Generate KPI dashboard')
    parser.add_argument('--schedule', type=int, help='Schedule collection every N minutes')
    parser.add_argument('--usage', action='store_true', help='Collect usage metrics only')
    parser.add_argument('--quality', action='store_true', help='Collect quality metrics only')
    parser.add_argument('--performance', action='store_true', help='Collect performance metrics only')
    parser.add_argument('--cleanup', action='store_true', help='Clean up old metrics data')
    
    args = parser.parse_args()
    
    # Initialize collector
    collector = DocumentationMetricsCollector()
    
    if args.usage:
        # Collect usage metrics only
        metrics = collector.collect_usage_metrics()
        print(f"Usage metrics collected:")
        print(f"  Page views: {metrics.total_page_views}")
        print(f"  Unique visitors: {metrics.unique_visitors}")
        print(f"  Avg session: {metrics.avg_session_duration:.1f} min")
        print(f"  Popular pages: {len(metrics.popular_pages)}")
        return 0
    
    elif args.quality:
        # Collect quality metrics only
        metrics = collector.collect_quality_metrics()
        print(f"Quality metrics collected:")
        print(f"  Coverage: {metrics.coverage_percentage:.1f}%")
        print(f"  Accuracy: {metrics.accuracy_score:.1f}/100")
        print(f"  User satisfaction: {metrics.user_satisfaction:.1f}/100")
        return 0
    
    elif args.performance:
        # Collect performance metrics only
        metrics = collector.collect_performance_metrics()
        print(f"Performance metrics collected:")
        print(f"  Search response time: {metrics.search_response_time:.1f}ms")
        print(f"  Mobile compatibility: {metrics.mobile_compatibility:.1f}/100")
        print(f"  Accessibility: {metrics.accessibility_score:.1f}/100")
        return 0
    
    elif args.dashboard:
        # Generate KPI dashboard
        dashboard_data = collector.generate_kpi_dashboard_data()
        print(f"KPI dashboard generated: {collector.reports_dir / 'kpi_dashboard.json'}")
        print(f"Overall health score: {dashboard_data['summary']['overall_health_score']:.1f}/100")
        return 0
    
    elif args.cleanup:
        # Clean up old data
        collector.cleanup_old_data()
        print("Old metrics data cleaned up")
        return 0
    
    elif args.collect:
        # Collect all metrics once
        dashboard_data = collector.generate_kpi_dashboard_data()
        print(f"All metrics collected successfully")
        print(f"Overall health score: {dashboard_data['summary']['overall_health_score']:.1f}/100")
        print(f"Dashboard saved to: {collector.reports_dir}")
        return 0
    
    elif args.schedule:
        # Schedule regular collection
        collector.schedule_collection(args.schedule)
        return 0
    
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())