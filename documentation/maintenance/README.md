# CVD Documentation Maintenance System

## Overview

This directory contains the comprehensive automation and monitoring infrastructure for the CVD documentation system. It provides automated tools, metrics collection, health monitoring, and maintenance capabilities to ensure sustainable documentation quality.

## Directory Structure

```
maintenance/
├── README.md                    # This file - system overview
├── METRICS.md                   # Comprehensive metrics framework
├── HEALTH.md                    # Health monitoring specifications
├── scripts/                     # Automation scripts
│   ├── link-checker.py         # Automated link validation
│   ├── format-validator.py     # Documentation standards compliance
│   ├── index-generator.py      # Search index rebuilding
│   ├── metrics-collector.py    # Usage and performance metrics
│   └── backup-creator.sh       # Automated backup and versioning
├── config/                      # Configuration files (auto-created)
├── data/                        # Metrics database and cache (auto-created)
├── reports/                     # Generated reports and logs (auto-created)
└── backups/                     # Documentation backups (auto-created)
```

## Quick Start

### 1. Setup and Installation

```bash
# Navigate to maintenance directory
cd /home/jbrice/Projects/365/documentation/maintenance

# Make scripts executable
chmod +x scripts/*.py scripts/*.sh

# Install Python dependencies (if needed)
pip install requests sqlite3 yaml frontmatter difflib

# Initialize the system
scripts/backup-creator.sh help  # Creates config directories
python scripts/metrics-collector.py --collect  # Initializes database
```

### 2. Basic Operations

#### Run Link Check
```bash
# Check all links once
python scripts/link-checker.py --check

# Check specific file
python scripts/link-checker.py --file path/to/document.md

# Schedule daily checks
python scripts/link-checker.py --schedule 24
```

#### Validate Documentation Format
```bash
# Validate all files
python scripts/format-validator.py --validate

# Validate specific file
python scripts/format-validator.py --file path/to/document.md

# Show only errors
python scripts/format-validator.py --validate --severity error
```

#### Rebuild Search Index
```bash
# Full index rebuild
python scripts/index-generator.py --build

# Incremental update
python scripts/index-generator.py --incremental

# Optimize existing index
python scripts/index-generator.py --optimize
```

#### Collect Metrics
```bash
# Collect all metrics and generate dashboard
python scripts/metrics-collector.py --dashboard

# Collect specific metric types
python scripts/metrics-collector.py --usage
python scripts/metrics-collector.py --quality
python scripts/metrics-collector.py --performance
```

#### Create Backup
```bash
# Smart backup (auto-selects full or incremental)
scripts/backup-creator.sh auto

# Force full backup
scripts/backup-creator.sh full

# List existing backups
scripts/backup-creator.sh list
```

## Automation Setup

### 1. Scheduled Automation (Recommended)

Add to system crontab for automated maintenance:

```bash
# Edit crontab
crontab -e

# Add these entries:
# Daily link check at 6 AM
0 6 * * * cd /home/jbrice/Projects/365/documentation/maintenance && python scripts/link-checker.py --check

# Daily format validation at 7 AM
0 7 * * * cd /home/jbrice/Projects/365/documentation/maintenance && python scripts/format-validator.py --validate

# Hourly index updates during business hours
0 9-17 * * 1-5 cd /home/jbrice/Projects/365/documentation/maintenance && python scripts/index-generator.py --incremental

# Daily metrics collection at 8 AM
0 8 * * * cd /home/jbrice/Projects/365/documentation/maintenance && python scripts/metrics-collector.py --collect

# Weekly backup on Sunday at 2 AM
0 2 * * 0 cd /home/jbrice/Projects/365/documentation/maintenance && scripts/backup-creator.sh auto
```

### 2. Continuous Monitoring

#### Start Monitoring Services
```bash
# Link monitoring (checks every 4 hours)
nohup python scripts/link-checker.py --schedule 4 > logs/link-monitor.log 2>&1 &

# Index maintenance (checks every 2 hours)
nohup python scripts/index-generator.py --schedule 2 > logs/index-monitor.log 2>&1 &

# Metrics collection (every hour)
nohup python scripts/metrics-collector.py --schedule 60 > logs/metrics-monitor.log 2>&1 &
```

### 3. Integration with Development Workflow

#### Pre-commit Hook Example
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run format validation on changed documentation
git diff --cached --name-only --diff-filter=AM | grep '\.md$' | while read file; do
    python documentation/maintenance/scripts/format-validator.py --file "$file"
    if [ $? -ne 0 ]; then
        echo "Documentation format validation failed for $file"
        exit 1
    fi
done

# Update search index for documentation changes
if git diff --cached --name-only --diff-filter=AM | grep -q 'documentation/.*\.md$'; then
    python documentation/maintenance/scripts/index-generator.py --incremental
fi
```

## Configuration

### 1. Link Checker Configuration

Edit `config/link-checker.conf` (auto-created):
```yaml
timeout: 30
max_workers: 10
retry_count: 2
cache_duration: 3600
user_agent: "CVD-Documentation-Link-Checker/1.0"
```

### 2. Backup Configuration

Edit `config/backup.conf` (auto-created):
```bash
RETENTION_DAYS=90
MAX_BACKUPS=50
COMPRESS_BACKUPS=true
VERIFY_BACKUPS=true
INCLUDE_METRICS=true
NOTIFICATION_EMAIL="docs-team@company.com"
```

### 3. Metrics Configuration

Metrics are configured in the Python scripts with baseline values from Phase 7 QA findings:
- Documentation Coverage: 89/100
- Search Success Rate: 87%
- User Satisfaction Scores by Role
- Mobile Compatibility: 81/100
- Accessibility Score: 78/100

## Key Features

### 1. Automated Link Validation
- **Internal & External Links**: Comprehensive validation with retry logic
- **Performance Tracking**: Response time monitoring and caching
- **Intelligent Reporting**: Broken link categorization and repair suggestions
- **Integration Ready**: Works with existing search.py system

### 2. Documentation Standards Compliance
- **Metadata Validation**: YAML frontmatter and schema compliance
- **Format Checking**: Style guide adherence and template compliance
- **Auto-fix Capability**: Automated correction for common issues
- **Quality Scoring**: Multi-dimensional compliance assessment

### 3. Search Index Optimization
- **Incremental Updates**: Smart change detection and partial rebuilds
- **Performance Monitoring**: Search response time tracking
- **Health Validation**: Index integrity and coverage verification
- **Automated Optimization**: Synonym expansion and performance tuning

### 4. Comprehensive Metrics Collection
- **Usage Analytics**: Page views, search patterns, user behavior
- **Quality Metrics**: Coverage, accuracy, freshness, consistency
- **Performance Monitoring**: Response times, availability, mobile compatibility
- **Role-based Analysis**: User satisfaction by role with actionable insights

### 5. Backup and Versioning
- **Smart Backup Strategy**: Automatic full/incremental selection
- **Compression & Encryption**: Optional security and space optimization
- **Verification System**: Backup integrity validation
- **Retention Management**: Automated cleanup based on policy

## Monitoring and Alerting

### 1. Health Thresholds

| Metric | Good | Warning | Critical | Action |
|--------|------|---------|----------|--------|
| **Link Validity** | >95% | 90-95% | <90% | Immediate fix |
| **Search Response** | <100ms | 100-200ms | >200ms | Performance tuning |
| **Documentation Coverage** | >90% | 85-90% | <85% | Content planning |
| **User Satisfaction** | >85/100 | 75-85/100 | <75/100 | UX improvement |

### 2. Automated Alerts

Alerts are generated for:
- **Critical**: >10 broken links, system availability <99%, user satisfaction <70
- **Warning**: Response time >100ms, coverage <85%, stale content >20%
- **Info**: Weekly quality summaries, monthly strategic reports

### 3. Report Generation

Automated reports include:
- **Daily**: System health, broken links, performance metrics
- **Weekly**: Quality trends, user feedback, improvement recommendations
- **Monthly**: Strategic KPI dashboard, ROI analysis, roadmap updates

## Troubleshooting

### Common Issues

#### 1. Link Checker Not Finding Links
```bash
# Check if the documentation path is correct
python scripts/link-checker.py --file documentation/README.md

# Verify the search patterns in link-checker.py
# Check for markdown, HTML, and image link patterns
```

#### 2. Search Index Build Failures
```bash
# Check search engine integration
python scripts/index-generator.py --validate

# Rebuild from scratch if corrupted
rm -f documentation/00-index/SEARCH_INDEX.json
python scripts/index-generator.py --build
```

#### 3. Metrics Database Issues
```bash
# Reset metrics database
rm -f data/metrics.db
python scripts/metrics-collector.py --collect
```

#### 4. Backup Failures
```bash
# Check backup configuration
scripts/backup-creator.sh help

# Verify disk space and permissions
df -h
ls -la backups/
```

### Performance Optimization

#### 1. Large Documentation Sets
- Enable index partitioning for >200 documents
- Use incremental processing where possible
- Configure appropriate worker threads and timeouts

#### 2. Network-Heavy Operations
- Adjust retry counts and timeouts for external links
- Enable caching for frequently checked URLs
- Schedule heavy operations during off-peak hours

#### 3. Storage Management
- Configure backup retention policies
- Enable compression for large documentation sets
- Monitor disk usage and set up cleanup automation

## Integration Points

### 1. Existing CVD Systems
- **Search Engine**: Integrates with `/documentation/00-index/scripts/search.py`
- **Quality Assurance**: Builds on Phase 7 QA findings and metrics
- **Validation Tools**: Enhances existing validation in `/documentation/00-index/scripts/`

### 2. Development Workflow
- **Pre-commit Hooks**: Format validation and link checking
- **CI/CD Integration**: Quality gates and automated index updates
- **Release Process**: Documentation readiness validation

### 3. Monitoring Infrastructure
- **Metrics Export**: Compatible with Prometheus, Grafana, and similar tools
- **Log Integration**: Structured logging for centralized log management
- **Alert Integration**: Webhook support for Slack, email, and ticketing systems

## Future Enhancements

### Phase 2 (Months 2-3)
- Machine learning for content gap detection
- Predictive quality degradation alerts
- Advanced user behavior analytics
- Cross-platform integration

### Phase 3 (Months 4-6)
- Self-healing content management
- AI-powered content suggestions
- Advanced personalization
- Industry benchmarking

---

**Contact**: Documentation Infrastructure Team
**Last Updated**: 2025-08-13
**Version**: 1.0.0