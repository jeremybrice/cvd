# Database Reference

## Purpose
Quick reference documentation for the CVD database including schemas, relationships, query examples, and analysis reports.

## Contents

### Schema Documentation
- **[DATABASE_SCHEMA.md](/documentation/03-architecture/system/DATABASE_SCHEMA.md)** - Complete database schema with relationships
- **cvd-database-schema.sql** - SQL schema definition for the CVD database
- **cvd-database-schema.json** - JSON representation of database schema
- **cvd-database-explained.txt** - Human-readable database explanation

### Data Analysis Reports
- **device_products.csv** - Device and product relationship data export
- **ai-chatbot-data-usage.md** - Analysis of AI chatbot data consumption patterns
- **ai-planogram-no-suggestions-analysis.md** - Analysis of planogram optimization edge cases

### Development and Debug Reports
- **console-logs.md** - Console log analysis and debugging information
- **chatbot-code-analysis.md** - Code analysis for chatbot implementation

## Expected Content Types
- Entity Relationship Diagrams (ERDs)
- Table schemas and definitions
- Index strategies
- Common queries
- Data dictionary
- Migration scripts
- Analysis reports
- Data exports
- Debug information

## File Locations
Files migrated from `/docs/reports/` to this directory:
- `ai-chatbot-data-usage.md`
- `ai-planogram-no-suggestions-analysis.md`
- `chatbot-code-analysis.md`
- `console-logs.md`
- `cvd-database-explained.txt`
- `cvd-database-schema.json`
- `cvd-database-schema.sql`
- `device_products.csv`

## Navigation Hints
- Start with **[DATABASE_SCHEMA.md](/documentation/03-architecture/system/DATABASE_SCHEMA.md)** for comprehensive schema documentation
- Check **cvd-database-schema.sql** for current table structures
- Reference **device_products.csv** for data relationship examples
- Review analysis reports for system insights and optimization opportunities

## Cross-References
- [Database Schema](/documentation/03-architecture/system/DATABASE_SCHEMA.md) - Comprehensive schema documentation
- [Database Patterns](/documentation/03-architecture/patterns/DATABASE_PATTERNS.md) - Database design patterns
- [Cheat Sheets](/documentation/09-reference/cheat-sheets/DATABASE_QUERIES.md) - Common database queries