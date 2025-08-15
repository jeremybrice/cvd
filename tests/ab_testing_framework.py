#!/usr/bin/env python3
"""
A/B Testing Framework for AI Planogram Features
Provides experiment setup, metric tracking, and statistical analysis
"""

import os
import sys
import json
import sqlite3
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ExperimentStatus(Enum):
    """Experiment status states"""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"


@dataclass
class ExperimentConfig:
    """Configuration for an A/B test experiment"""
    name: str
    feature: str
    hypothesis: str
    primary_metric: str
    secondary_metrics: List[str]
    sample_size: int
    duration_days: int
    confidence_level: float = 0.95
    minimum_detectable_effect: float = 0.05
    allocation_ratio: float = 0.5  # Percentage in treatment


class ABTestingFramework:
    """Framework for running and analyzing A/B tests on AI features"""
    
    def __init__(self, db_path: str = 'cvd.db'):
        self.db_path = db_path
        self.experiments = {}
        self._init_database()
    
    def _init_database(self):
        """Initialize A/B testing tables in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create experiments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ab_experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                feature TEXT NOT NULL,
                hypothesis TEXT,
                config TEXT NOT NULL,
                status TEXT NOT NULL,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create experiment assignments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ab_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER NOT NULL,
                device_id INTEGER NOT NULL,
                group_name TEXT NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES ab_experiments(id),
                UNIQUE(experiment_id, device_id)
            )
        """)
        
        # Create metrics tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ab_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER NOT NULL,
                device_id INTEGER NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES ab_experiments(id)
            )
        """)
        
        # Create results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ab_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER NOT NULL,
                metric_name TEXT NOT NULL,
                control_mean REAL,
                treatment_mean REAL,
                effect_size REAL,
                p_value REAL,
                confidence_lower REAL,
                confidence_upper REAL,
                is_significant BOOLEAN,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES ab_experiments(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_experiment(self, config: ExperimentConfig) -> Dict:
        """Create a new A/B test experiment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert experiment
            cursor.execute("""
                INSERT INTO ab_experiments (name, feature, hypothesis, config, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                config.name,
                config.feature,
                config.hypothesis,
                json.dumps(config.__dict__),
                ExperimentStatus.DRAFT.value
            ))
            
            experiment_id = cursor.lastrowid
            
            # Get available devices
            cursor.execute("SELECT id FROM devices WHERE is_deleted = 0")
            all_devices = [row[0] for row in cursor.fetchall()]
            
            # Randomly assign devices to groups
            random.shuffle(all_devices)
            
            # Determine split point
            treatment_size = int(len(all_devices) * config.allocation_ratio)
            treatment_devices = all_devices[:treatment_size]
            control_devices = all_devices[treatment_size:]
            
            # Insert assignments
            assignments = []
            for device_id in treatment_devices:
                assignments.append((experiment_id, device_id, 'treatment'))
            for device_id in control_devices:
                assignments.append((experiment_id, device_id, 'control'))
            
            cursor.executemany("""
                INSERT INTO ab_assignments (experiment_id, device_id, group_name)
                VALUES (?, ?, ?)
            """, assignments)
            
            conn.commit()
            
            # Return experiment details
            experiment = {
                'id': experiment_id,
                'name': config.name,
                'feature': config.feature,
                'hypothesis': config.hypothesis,
                'status': ExperimentStatus.DRAFT.value,
                'control_size': len(control_devices),
                'treatment_size': len(treatment_devices),
                'total_devices': len(all_devices)
            }
            
            self.experiments[config.name] = experiment
            return experiment
            
        except sqlite3.IntegrityError as e:
            conn.rollback()
            raise ValueError(f"Experiment '{config.name}' already exists")
        finally:
            conn.close()
    
    def start_experiment(self, experiment_name: str) -> bool:
        """Start running an experiment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update status and start date
            cursor.execute("""
                UPDATE ab_experiments
                SET status = ?, start_date = CURRENT_TIMESTAMP
                WHERE name = ? AND status = ?
            """, (ExperimentStatus.RUNNING.value, experiment_name, ExperimentStatus.DRAFT.value))
            
            if cursor.rowcount == 0:
                return False
            
            conn.commit()
            
            if experiment_name in self.experiments:
                self.experiments[experiment_name]['status'] = ExperimentStatus.RUNNING.value
            
            return True
            
        finally:
            conn.close()
    
    def get_device_assignment(self, experiment_name: str, device_id: int) -> Optional[str]:
        """Get the group assignment for a device in an experiment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.group_name
            FROM ab_assignments a
            JOIN ab_experiments e ON a.experiment_id = e.id
            WHERE e.name = ? AND a.device_id = ?
        """, (experiment_name, device_id))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def track_metric(self, experiment_name: str, device_id: int, 
                    metric_name: str, value: float) -> bool:
        """Track a metric value for an experiment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get experiment ID
            cursor.execute("""
                SELECT id FROM ab_experiments 
                WHERE name = ? AND status = ?
            """, (experiment_name, ExperimentStatus.RUNNING.value))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            experiment_id = result[0]
            
            # Insert metric
            cursor.execute("""
                INSERT INTO ab_metrics (experiment_id, device_id, metric_name, metric_value)
                VALUES (?, ?, ?, ?)
            """, (experiment_id, device_id, metric_name, value))
            
            conn.commit()
            return True
            
        finally:
            conn.close()
    
    def analyze_results(self, experiment_name: str, 
                       confidence_level: Optional[float] = None) -> Dict:
        """Analyze A/B test results with statistical significance"""
        from scipy import stats
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get experiment details
        cursor.execute("""
            SELECT id, config FROM ab_experiments WHERE name = ?
        """, (experiment_name,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            raise ValueError(f"Experiment '{experiment_name}' not found")
        
        experiment_id, config_json = result
        config = json.loads(config_json)
        
        if confidence_level is None:
            confidence_level = config.get('confidence_level', 0.95)
        
        # Get all metrics for this experiment
        cursor.execute("""
            SELECT 
                m.metric_name,
                a.group_name,
                m.metric_value
            FROM ab_metrics m
            JOIN ab_assignments a ON m.device_id = a.device_id 
                AND m.experiment_id = a.experiment_id
            WHERE m.experiment_id = ?
        """, (experiment_id,))
        
        # Organize metrics by name and group
        metrics_data = {}
        for metric_name, group_name, value in cursor.fetchall():
            if metric_name not in metrics_data:
                metrics_data[metric_name] = {'control': [], 'treatment': []}
            metrics_data[metric_name][group_name].append(value)
        
        # Analyze each metric
        results = {}
        for metric_name, groups in metrics_data.items():
            control = np.array(groups['control'])
            treatment = np.array(groups['treatment'])
            
            if len(control) == 0 or len(treatment) == 0:
                continue
            
            # Calculate statistics
            control_mean = np.mean(control)
            treatment_mean = np.mean(treatment)
            
            # Effect size (percentage lift)
            if control_mean != 0:
                effect_size = (treatment_mean - control_mean) / control_mean
            else:
                effect_size = 0
            
            # Perform t-test
            t_stat, p_value = stats.ttest_ind(treatment, control)
            
            # Calculate confidence interval for the difference
            pooled_std = np.sqrt((np.var(control) + np.var(treatment)) / 2)
            se_diff = pooled_std * np.sqrt(1/len(control) + 1/len(treatment))
            
            t_critical = stats.t.ppf((1 + confidence_level) / 2, 
                                     len(control) + len(treatment) - 2)
            
            diff = treatment_mean - control_mean
            ci_lower = diff - t_critical * se_diff
            ci_upper = diff + t_critical * se_diff
            
            # Determine statistical significance
            is_significant = p_value < (1 - confidence_level)
            
            # Store results
            results[metric_name] = {
                'control_mean': float(control_mean),
                'treatment_mean': float(treatment_mean),
                'control_std': float(np.std(control)),
                'treatment_std': float(np.std(treatment)),
                'control_n': len(control),
                'treatment_n': len(treatment),
                'effect_size': float(effect_size),
                'effect_size_percentage': float(effect_size * 100),
                'absolute_difference': float(diff),
                'p_value': float(p_value),
                'confidence_interval': (float(ci_lower), float(ci_upper)),
                'confidence_level': confidence_level,
                'is_significant': bool(is_significant),
                't_statistic': float(t_stat)
            }
            
            # Save results to database
            cursor.execute("""
                INSERT INTO ab_results 
                (experiment_id, metric_name, control_mean, treatment_mean, 
                 effect_size, p_value, confidence_lower, confidence_upper, is_significant)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                experiment_id, metric_name, control_mean, treatment_mean,
                effect_size, p_value, ci_lower, ci_upper, is_significant
            ))
        
        conn.commit()
        conn.close()
        
        return results
    
    def calculate_sample_size(self, baseline_rate: float, 
                             minimum_detectable_effect: float,
                             power: float = 0.8,
                             alpha: float = 0.05) -> int:
        """Calculate required sample size for desired statistical power"""
        from scipy.stats import norm
        
        # Convert percentages to proportions if needed
        if baseline_rate > 1:
            baseline_rate = baseline_rate / 100
        if minimum_detectable_effect > 1:
            minimum_detectable_effect = minimum_detectable_effect / 100
        
        # Expected rate with effect
        expected_rate = baseline_rate * (1 + minimum_detectable_effect)
        
        # Calculate pooled standard deviation
        pooled_p = (baseline_rate + expected_rate) / 2
        pooled_std = np.sqrt(2 * pooled_p * (1 - pooled_p))
        
        # Calculate z-scores
        z_alpha = norm.ppf(1 - alpha / 2)
        z_beta = norm.ppf(power)
        
        # Calculate sample size per group
        effect_size = abs(expected_rate - baseline_rate)
        n = ((z_alpha + z_beta) * pooled_std / effect_size) ** 2
        
        return int(np.ceil(n))
    
    def get_experiment_status(self, experiment_name: str) -> Dict:
        """Get current status and progress of an experiment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get experiment details
        cursor.execute("""
            SELECT 
                id, 
                status, 
                start_date,
                config,
                julianday('now') - julianday(start_date) as days_running
            FROM ab_experiments 
            WHERE name = ?
        """, (experiment_name,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return None
        
        exp_id, status, start_date, config_json, days_running = result
        config = json.loads(config_json)
        
        # Get metric counts
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT device_id) as devices_with_data,
                COUNT(*) as total_observations,
                MIN(recorded_at) as first_observation,
                MAX(recorded_at) as last_observation
            FROM ab_metrics
            WHERE experiment_id = ?
        """, (exp_id,))
        
        metrics_info = cursor.fetchone()
        
        # Get group sizes
        cursor.execute("""
            SELECT group_name, COUNT(*) as size
            FROM ab_assignments
            WHERE experiment_id = ?
            GROUP BY group_name
        """, (exp_id,))
        
        groups = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        # Calculate progress
        target_duration = config.get('duration_days', 30)
        progress = (days_running / target_duration * 100) if days_running and target_duration else 0
        
        return {
            'name': experiment_name,
            'status': status,
            'start_date': start_date,
            'days_running': days_running or 0,
            'target_duration': target_duration,
            'progress_percentage': min(100, progress),
            'control_size': groups.get('control', 0),
            'treatment_size': groups.get('treatment', 0),
            'devices_with_data': metrics_info[0] or 0,
            'total_observations': metrics_info[1] or 0,
            'first_observation': metrics_info[2],
            'last_observation': metrics_info[3]
        }
    
    def stop_experiment(self, experiment_name: str, reason: str = None) -> bool:
        """Stop a running experiment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE ab_experiments
            SET status = ?, end_date = CURRENT_TIMESTAMP
            WHERE name = ? AND status = ?
        """, (ExperimentStatus.STOPPED.value, experiment_name, ExperimentStatus.RUNNING.value))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_power_analysis(self, experiment_name: str) -> Dict:
        """Perform power analysis on current experiment data"""
        results = self.analyze_results(experiment_name)
        
        power_analysis = {}
        
        for metric_name, metric_results in results.items():
            # Calculate observed power
            effect_size = metric_results['effect_size']
            sample_size = metric_results['control_n']
            
            # Simplified power calculation
            if effect_size != 0 and sample_size > 0:
                # This is a simplified calculation
                # In practice, you'd use more sophisticated methods
                z_score = abs(metric_results['t_statistic'])
                from scipy.stats import norm
                observed_power = 1 - norm.cdf(-z_score + 1.96)
            else:
                observed_power = 0
            
            power_analysis[metric_name] = {
                'observed_power': float(observed_power),
                'is_adequately_powered': observed_power >= 0.8,
                'sample_size': sample_size,
                'effect_size': effect_size
            }
        
        return power_analysis


class ExperimentSimulator:
    """Simulate experiment data for testing"""
    
    @staticmethod
    def simulate_revenue_experiment(framework: ABTestingFramework,
                                   experiment_name: str,
                                   days: int = 30,
                                   base_revenue: float = 100,
                                   treatment_lift: float = 0.10):
        """Simulate revenue data for an experiment"""
        
        # Get all device assignments
        conn = sqlite3.connect(framework.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.device_id, a.group_name
            FROM ab_assignments a
            JOIN ab_experiments e ON a.experiment_id = e.id
            WHERE e.name = ?
        """, (experiment_name,))
        
        assignments = cursor.fetchall()
        conn.close()
        
        # Simulate daily revenue for each device
        for day in range(days):
            for device_id, group in assignments:
                # Base revenue with random variation
                daily_revenue = base_revenue + np.random.normal(0, 10)
                
                # Apply treatment effect
                if group == 'treatment':
                    daily_revenue *= (1 + treatment_lift)
                
                # Add some noise
                daily_revenue += np.random.normal(0, 5)
                
                # Track metric
                framework.track_metric(
                    experiment_name,
                    device_id,
                    'daily_revenue',
                    max(0, daily_revenue)
                )
                
                # Also track secondary metrics
                if np.random.random() < 0.3:  # 30% chance of stockout
                    stockout = 1 if group == 'control' else 0.7
                    framework.track_metric(
                        experiment_name,
                        device_id,
                        'stockout_rate',
                        stockout
                    )


if __name__ == '__main__':
    # Example usage and testing
    framework = ABTestingFramework('test_ab.db')
    
    # Create an experiment
    config = ExperimentConfig(
        name="realtime_assistant_v1",
        feature="realtime_placement_scoring",
        hypothesis="Real-time AI feedback increases revenue by 10%",
        primary_metric="daily_revenue",
        secondary_metrics=["stockout_rate", "placement_changes"],
        sample_size=50,
        duration_days=30,
        minimum_detectable_effect=0.10
    )
    
    experiment = framework.create_experiment(config)
    print(f"Created experiment: {experiment}")
    
    # Calculate required sample size
    sample_size = framework.calculate_sample_size(
        baseline_rate=100,  # $100 baseline revenue
        minimum_detectable_effect=0.10,  # 10% lift
        power=0.8
    )
    print(f"Required sample size per group: {sample_size}")
    
    # Start the experiment
    framework.start_experiment("realtime_assistant_v1")
    
    # Simulate some data
    simulator = ExperimentSimulator()
    simulator.simulate_revenue_experiment(
        framework,
        "realtime_assistant_v1",
        days=30,
        treatment_lift=0.12  # 12% actual lift
    )
    
    # Analyze results
    results = framework.analyze_results("realtime_assistant_v1")
    
    print("\n=== Experiment Results ===")
    for metric, stats in results.items():
        print(f"\n{metric}:")
        print(f"  Control: {stats['control_mean']:.2f} (n={stats['control_n']})")
        print(f"  Treatment: {stats['treatment_mean']:.2f} (n={stats['treatment_n']})")
        print(f"  Lift: {stats['effect_size_percentage']:.1f}%")
        print(f"  P-value: {stats['p_value']:.4f}")
        print(f"  Significant: {stats['is_significant']}")
    
    # Get experiment status
    status = framework.get_experiment_status("realtime_assistant_v1")
    print(f"\nExperiment Status: {status}")
    
    # Power analysis
    power = framework.get_power_analysis("realtime_assistant_v1")
    print(f"\nPower Analysis: {power}")
    
    # Clean up test database
    if os.path.exists('test_ab.db'):
        os.remove('test_ab.db')