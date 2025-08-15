# Developer Commands Cheat Sheet


## Metadata
- **ID**: 09_REFERENCE_CHEAT_SHEETS_DEVELOPER_COMMANDS
- **Type**: Reference
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #authentication #data-layer #database #debugging #device-management #documentation #integration #machine-learning #optimization #performance #quality-assurance #reference #security #testing #troubleshooting #vending-machine
- **Intent**: Reference for Developer Commands Cheat Sheet
- **Audience**: developers, system administrators, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/09-reference/cheat-sheets/
- **Category**: Cheat Sheets
- **Search Keywords**: "./venv/, ###, --include=", -not, -path, .html", .js", .py", analysis, api, cheat, code, commands, ctrl+, curl

## Quick Development Workflow

### Environment Setup (One-Time)
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (optional)
pip install pytest flask-testing
```

### Daily Development Workflow
```bash
# 1. Activate environment
source venv/bin/activate

# 2. Start backend (Terminal 1)
python app.py

# 3. Start frontend (Terminal 2)
python -m http.server 8000

# 4. Access application
# http://localhost:8000
# Login: admin/admin
```

### Code Quality & Testing
```bash
# Run all tests
python -m pytest

# Run specific test
python -m pytest test_endpoints.py -v

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Manual test files
python test_admin_user_hiding.py
python test_frontend_api_calls.py
```

### Database Operations
```bash
# View database schema
sqlite3 cvd.db ".schema"

# Interactive database session
sqlite3 cvd.db

# Quick data check
sqlite3 cvd.db "SELECT COUNT(*) FROM devices;"

# Backup database
cp cvd.db "cvd_backup_$(date +%Y%m%d_%H%M%S).db"

# Run migrations
python migration_add_activity_monitoring.py

# Database analysis
python analyze_db.py
```

### Debugging Commands
```bash
# Enable Flask debug mode
export FLASK_DEBUG=1
python app.py

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# View active processes
ps aux | grep python

# Check port usage
netstat -tulpn | grep :5000
netstat -tulpn | grep :8000

# View logs (if logging to file)
tail -f flask.log
```

### API Testing with curl
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  -c cookies.txt

# Get devices
curl -X GET http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -b cookies.txt

# Create device
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name":"Test Device","location":"Test Location"}'
```

### Git Workflow (if using Git)
```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# View commit history
git log --oneline

# Create feature branch
git checkout -b feature/new-feature

# Switch branches
git checkout main
git checkout feature/new-feature
```

### Environment Variables
```bash
# AI functionality
export ANTHROPIC_API_KEY="your-key-here"

# Session security
export SESSION_SECRET="your-secret-key"

# Flask environment
export FLASK_ENV=development
export FLASK_DEBUG=1

# View all environment variables
env | grep -E "(FLASK|ANTHROPIC|SESSION)"
```

### Performance Profiling
```bash
# Time application startup
time python app.py &

# Memory usage
ps -o pid,ppid,%mem,command -p $(pgrep -f "python app.py")

# Database performance
sqlite3 cvd.db "EXPLAIN QUERY PLAN SELECT * FROM devices;"

# Network requests (browser dev tools alternative)
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/api/devices
```

### File Operations
```bash
# Find Python files
find . -name "*.py" -not -path "./venv/*"

# Find HTML files
find . -name "*.html" -not -path "./venv/*"

# Search for specific code
grep -r "def get_devices" . --include="*.py"

# Count lines of code
find . -name "*.py" -not -path "./venv/*" | xargs wc -l

# Find large files
find . -type f -size +1M -not -path "./venv/*"
```

### Troubleshooting Commands
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check for missing dependencies
pip check

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# Reset database (CAUTION: Data loss!)
rm cvd.db
python app.py  # Will recreate with init_db()
```

### Code Analysis
```bash
# Find TODO/FIXME comments
grep -r "TODO\|FIXME" . --include="*.py" --include="*.js" --include="*.html"

# Check for potential security issues
grep -r "password" . --include="*.py" | grep -v "hash"

# Find unused imports (requires pyflakes)
pyflakes *.py

# Check code complexity (requires McCabe)
python -m mccabe --min 10 *.py
```

### Quick Fixes
```bash
# Fix import issues
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Fix file permissions
chmod +x app.py

# Fix line endings (if needed)
dos2unix *.py

# Clear browser cache (programmatically)
# Open DevTools > Application > Storage > Clear storage
```

### Keyboard Shortcuts (VS Code)
```
Ctrl+`          # Open terminal
Ctrl+Shift+P    # Command palette
Ctrl+Shift+F    # Search in files
F5              # Start debugging
Ctrl+F5         # Run without debugging
Ctrl+Shift+I    # Developer tools (browser)
```

### One-Liner Utilities
```bash
# Quick server status check
curl -s http://localhost:5000/api/auth/current-user && echo "Backend OK" || echo "Backend DOWN"

# Count database records
sqlite3 cvd.db "SELECT 
  'Users: ' || COUNT(*) FROM users UNION ALL
  SELECT 'Devices: ' || COUNT(*) FROM devices UNION ALL
  SELECT 'Products: ' || COUNT(*) FROM products;"

# Check for running processes
pgrep -f "python app.py" && echo "Backend running" || echo "Backend not running"
pgrep -f "http.server" && echo "Frontend running" || echo "Frontend not running"

# Quick backup with timestamp
cp cvd.db "backup/cvd_$(date +%Y%m%d_%H%M%S).db"

# View recent database changes
sqlite3 cvd.db "SELECT table_name, MAX(created_at) as latest 
FROM (SELECT 'users' as table_name, created_at FROM users UNION ALL
      SELECT 'devices', created_at FROM devices UNION ALL
      SELECT 'service_orders', created_at FROM service_orders)
GROUP BY table_name;"
```

---

*Keep this cheat sheet handy for quick reference during development.*