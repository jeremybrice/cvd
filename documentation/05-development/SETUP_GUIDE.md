# Development Environment Setup Guide


## Metadata
- **ID**: 05_DEVELOPMENT_SETUP_GUIDE
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #authentication #coding #data-exchange #data-layer #database #debugging #deployment #development #device-management #devops #dex-parser #integration #logistics #machine-learning #optimization #performance #planogram #product-placement #quality-assurance #route-management #security #testing #troubleshooting #vending-machine #workflows
- **Intent**: This guide provides comprehensive instructions for setting up a complete development environment for the CVD (Vision Device Configuration) application
- **Audience**: system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/
- **Category**: 05 Development
- **Search Keywords**: ####, (recommended), alternative, backend, bash, browser, check, code, configuration, console, database, deactivate, debugger, development, device

## Overview

This guide provides comprehensive instructions for setting up a complete development environment for the CVD (Vision Device Configuration) application. The CVD system is a Flask-based backend with a modular iframe-based frontend, designed for enterprise vending machine fleet management.

## Prerequisites

### System Requirements
- **Operating System**: Linux (recommended), macOS, or Windows with WSL2
- **Python**: 3.8+ (Python 3.12 recommended)
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space for development environment

### Required Tools
- `python3` and `pip`
- `git` (if using version control)
- Text editor or IDE (recommendations below)

## Quick Start

```bash
# 1. Clone/Navigate to project directory
cd /path/to/cvd-project

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize database (automatic on first run)
python app.py

# 6. Start frontend server (in new terminal)
python -m http.server 8000

# 7. Access application
# Backend API: http://localhost:5000
# Frontend UI: http://localhost:8000
```

## Detailed Setup Instructions

### 1. Python Virtual Environment Setup

#### Create Virtual Environment
```bash
# Navigate to project root
cd /home/jbrice/Projects/365

# Create virtual environment
python -m venv venv
```

#### Activate Virtual Environment
```bash
# Linux/macOS
source venv/bin/activate

# Windows Command Prompt
venv\Scripts\activate.bat

# Windows PowerShell
venv\Scripts\Activate.ps1

# Verify activation (should show project venv path)
which python
```

#### Deactivate When Done
```bash
deactivate
```

### 2. Dependencies Installation

#### Core Dependencies
The project uses a carefully curated set of dependencies defined in `requirements.txt`:

```bash
# Install all dependencies
pip install -r requirements.txt

# Core packages installed:
# - flask==2.3.3          # Web framework
# - flask-cors==4.0.0      # CORS support
# - flask-session==0.5.0   # Session management
# - werkzeug==2.3.7        # WSGI utilities
# - gunicorn==21.2.0       # Production WSGI server
# - anthropic==0.57.1      # AI integration (optional)
# - redis==5.0.1           # Caching (optional)
# - requests==2.31.0       # HTTP client
# - markdown==3.5.1        # Markdown processing
# - pyyaml==6.0.1          # YAML parsing
```

#### Optional AI Dependencies
For AI-powered features (planogram optimization, chat assistant):
```bash
# Install AI-specific requirements (optional)
pip install -r requirements-ai.txt
```

#### Development Dependencies
For development and testing:
```bash
# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

#### Verify Installation
```bash
# Check installed packages
pip list

# Test core imports
python -c "import flask, sqlite3; print('Core dependencies OK')"
```

### 3. Database Setup

The CVD application uses SQLite as its primary database with automatic initialization.

#### Automatic Initialization
The database is automatically created on first application startup:

```bash
# Start application (creates cvd.db if not exists)
python app.py
```

#### Manual Database Operations
```bash
# View database schema
sqlite3 cvd.db ".schema"

# Export database for backup
sqlite3 cvd.db ".dump" > backup.sql

# Import database from backup
sqlite3 cvd.db ".read backup.sql"
```

#### Sample Data Loading
The application includes default data for immediate development:
- Default admin user: `admin/admin`
- Sample products (12 system products)
- Default device types and configurations

### 4. Frontend Server Setup

The frontend uses a simple HTTP server to serve static files:

#### Start Frontend Server
```bash
# In project root directory
python -m http.server 8000

# Access points:
# Main UI: http://localhost:8000
# Direct pages: http://localhost:8000/pages/[page].html
```

#### Alternative Servers
```bash
# Using Node.js (if available)
npx http-server -p 8000 -c-1

# Using PHP (if available)
php -S localhost:8000

# Using Python 2 (legacy)
python -m SimpleHTTPServer 8000
```

### 5. Environment Variables Configuration

#### Required Variables
```bash
# Create .env file (optional but recommended)
# No variables are strictly required for basic operation

# Optional AI Features
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# Optional Redis Caching
export REDIS_URL="redis://localhost:6379"

# Production Settings
export FLASK_ENV="development"  # or "production"
export SESSION_SECRET="your-secret-key-here"
```

#### Environment File Setup
```bash
# Create .env file
cat > .env << EOF
# CVD Development Environment Variables

# AI Services (Optional)
ANTHROPIC_API_KEY=your-key-here

# Session Configuration
SESSION_SECRET=your-secret-key-here

# Development Settings
FLASK_ENV=development
DEBUG=true

# Database Settings (uses SQLite by default)
DATABASE_URL=sqlite:///cvd.db

# Server Settings
FLASK_PORT=5000
FRONTEND_PORT=8000
EOF

# Load environment variables
source .env
```

### 6. IDE and Editor Configuration

#### Recommended IDEs

**VS Code (Recommended)**
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "files.associations": {
        "*.html": "html"
    },
    "emmet.includeLanguages": {
        "html": "html"
    }
}
```

**PyCharm Configuration**
- Set Python interpreter to `./venv/bin/python`
- Configure code style to PEP 8
- Enable Flask project template
- Set project root correctly

#### Recommended Extensions

**VS Code Extensions**
- Python (Microsoft)
- Pylance
- Flask Snippets
- HTML CSS Support
- Live Server (for frontend development)
- SQLite Viewer
- GitLens (if using Git)

#### Editor Settings
```bash
# Create .editorconfig
cat > .editorconfig << EOF
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[*.{js,html,css,json}]
indent_size = 2

[*.py]
indent_size = 4
max_line_length = 88

[*.md]
trim_trailing_whitespace = false
EOF
```

## Development Workflow

### 1. Daily Development Process

```bash
# Start development session
cd /path/to/cvd-project
source venv/bin/activate

# Update dependencies (if needed)
pip install -r requirements.txt

# Start backend (Terminal 1)
python app.py

# Start frontend (Terminal 2)
python -m http.server 8000

# Access application
# Frontend: http://localhost:8000
# Backend API: http://localhost:5000/api
```

### 2. Making Changes

#### Backend Changes
1. Edit Python files in project root
2. Flask auto-reloads in development mode
3. Test API endpoints via browser or curl
4. Check logs in terminal

#### Frontend Changes
1. Edit HTML/CSS/JS files in `/pages/` directory
2. Refresh browser to see changes
3. Use browser dev tools for debugging
4. Check console for JavaScript errors

### 3. Testing Your Changes

```bash
# Run basic tests
python -m pytest tests/ -v

# Test specific functionality
python tests/test_auth_flow.py
python tests/test_knowledge_base_api.py

# Test API endpoints
curl http://localhost:5000/api/devices
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

### 4. Database Development

```bash
# View current schema
sqlite3 cvd.db ".schema" | head -50

# Check table contents
sqlite3 cvd.db "SELECT * FROM users LIMIT 5;"

# Apply migrations (if any)
python migrations/apply_migration.py

# Backup before major changes
cp cvd.db cvd.db.backup.$(date +%Y%m%d_%H%M%S)
```

## Common Development Tasks

### 1. Adding a New Page

```bash
# 1. Create HTML page
touch pages/new-feature.html

# 2. Add route to index.html navigation
# Edit index.html pageRoutes object

# 3. Include API client
# Add: <script src="/api.js"></script>

# 4. Test page access
# http://localhost:8000/#new-feature
```

### 2. Adding a New API Endpoint

```python
# In app.py, add new route
@app.route('/api/new-feature', methods=['GET', 'POST'])
@auth_manager.require_auth(['admin', 'manager'])
def new_feature_api():
    if request.method == 'POST':
        # Handle POST logic
        return jsonify({'success': True})
    else:
        # Handle GET logic
        return jsonify({'data': []})
```

### 3. Database Schema Changes

```python
# Create migration file
# migrations/YYYYMMDD_description.sql

# Apply migration
python -c "
import sqlite3
conn = sqlite3.connect('cvd.db')
with open('migrations/YYYYMMDD_description.sql') as f:
    conn.executescript(f.read())
conn.close()
"
```

### 4. Adding JavaScript Functionality

```javascript
// In page HTML or separate .js file
class NewFeature {
    constructor() {
        this.api = new CVDApi();
    }
    
    async loadData() {
        try {
            const data = await this.api.get('/new-feature');
            this.renderData(data);
        } catch (error) {
            console.error('Failed to load data:', error);
        }
    }
}
```

## Development Best Practices

### 1. Code Organization
- Keep Python files in project root
- Place HTML pages in `/pages/` directory
- Put shared JavaScript in project root
- Store CSS in `/css/` directory
- Use `/tools/` for utility scripts

### 2. Database Management
- Always backup database before schema changes
- Use migrations for schema modifications
- Keep sample data in separate SQL files
- Test database operations in isolation

### 3. API Development
- Follow RESTful conventions
- Include proper error handling
- Use appropriate HTTP status codes
- Validate input parameters
- Log important operations

### 4. Frontend Development
- Use semantic HTML structure
- Follow responsive design principles
- Include proper error handling
- Use browser development tools
- Test across different browsers

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Kill process using port 5000 (backend)
sudo lsof -t -i:5000 | xargs kill -9

# Kill process using port 8000 (frontend)
sudo lsof -t -i:8000 | xargs kill -9

# Or use different ports
python app.py --port 5001
python -m http.server 8001
```

#### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Database Lock Errors
```bash
# Check for database locks
sqlite3 cvd.db ".timeout 5000"

# Restart application to release locks
# Kill Python processes and restart
```

#### Import Errors
```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Check virtual environment
which python

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

#### Permission Errors
```bash
# Fix file permissions
chmod +x *.py
chmod -R 755 pages/
chmod -R 755 css/

# Fix virtual environment permissions
chmod -R 755 venv/
```

### Getting Help

1. **Check Logs**: Review terminal output for error messages
2. **Browser Console**: Check for JavaScript errors in dev tools
3. **Database Integrity**: Verify database schema and data
4. **Network Requests**: Monitor API calls in browser dev tools
5. **Python Debugger**: Use `pdb` for stepping through code

### Performance Tips

1. **Database Optimization**
   - Use database indexes for frequently queried fields
   - Limit result sets with pagination
   - Use prepared statements for repeated queries

2. **Frontend Optimization**
   - Minimize HTTP requests
   - Use browser caching
   - Optimize images and assets
   - Minimize JavaScript and CSS

3. **Backend Optimization**
   - Use connection pooling for database
   - Implement caching for expensive operations
   - Monitor memory usage and optimize queries

## Advanced Configuration

### Production Considerations

When preparing for production deployment:

1. **Environment Variables**
   ```bash
   export FLASK_ENV=production
   export SESSION_SECRET="secure-secret-key"
   export DATABASE_URL="postgresql://..."
   ```

2. **Security Settings**
   - Use HTTPS in production
   - Set secure session cookies
   - Implement proper authentication
   - Use environment-specific configurations

3. **Performance Settings**
   - Use Gunicorn for production WSGI server
   - Implement Redis for session storage
   - Configure database connection pooling
   - Set up monitoring and logging

### Docker Development (Optional)

```dockerfile
# Use provided Dockerfile.dev for containerized development
docker build -f Dockerfile.dev -t cvd-dev .
docker run -p 5000:5000 -p 8000:8000 -v $(pwd):/app cvd-dev
```

This setup guide provides everything needed to establish a productive development environment for the CVD application. Follow the workflow and best practices to ensure efficient development and reliable code quality.