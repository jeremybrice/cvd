# System Architecture

## Purpose
System-wide architecture documentation including overall design, component relationships, and system views.

## Contents

### Architecture Overviews
- **[ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)** - Complete system architecture with Flask backend, nginx proxy, and frontend components
- **[OVERVIEW.md](OVERVIEW.md)** - High-level system overview and design principles

### Database and Schema
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Complete database schema documentation with relationships and constraints

### File Organization and Structure
- **[FILE_STRUCTURE_GUIDE.md](FILE_STRUCTURE_GUIDE.md)** - Comprehensive guide to file locations and project organization

### Driver App Architecture
- **[DRIVER_APP_DATA_FLOW.md](DRIVER_APP_DATA_FLOW.md)** - Complete analysis of PWA data flows and offline sync patterns
- **[DRIVER_APP_DATA_POINTS.md](DRIVER_APP_DATA_POINTS.md)** - Detailed documentation of all data structures and API endpoints used by the driver app

### Infrastructure Configuration
- **[NGINX_CONFIGURATION.md](NGINX_CONFIGURATION.md)** - Complete nginx configuration with SSL, proxy settings, and deployment instructions

### Technical Specifications
- **[METRICS_CALCULATION_SYSTEM.md](METRICS_CALCULATION_SYSTEM.md)** - Technical specification for inventory metrics calculation system including database schema and algorithms

## Expected Content Types
- System context diagrams
- Component architecture
- Deployment architecture
- Data flow diagrams
- Sequence diagrams
- Network architecture
- Database schemas
- Configuration files
- Technical specifications

## Navigation Hints
- Start with **ARCHITECTURE_OVERVIEW.md** for system boundaries and overall design
- Review **FILE_STRUCTURE_GUIDE.md** to understand project organization
- Check **DATABASE_SCHEMA.md** for data model and relationships
- Use **DRIVER_APP_DATA_FLOW.md** for PWA implementation details
- Reference **NGINX_CONFIGURATION.md** for deployment infrastructure
- See **METRICS_CALCULATION_SYSTEM.md** for complex algorithmic implementations

## Cross-References
- [Architecture Patterns](/documentation/03-architecture/patterns/) - Implementation patterns used throughout the system
- [API Documentation](/documentation/05-development/api/) - API endpoint documentation
- [Security Architecture](/documentation/03-architecture/SECURITY.md) - Security implementation details