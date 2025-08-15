# CVD System Quick Start Guide


## Metadata
- **ID**: 01_PROJECT_CORE_QUICK_START
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #authentication #core-concepts #data-layer #database #debugging #deployment #device-management #devops #driver-app #getting-started #integration #logistics #machine-learning #mobile #optimization #performance #planogram #product-placement #project-overview #pwa #quality-assurance #quick-start #route-management #security #testing #troubleshooting #vending-machine
- **Intent**: Documentation for CVD System Quick Start Guide
- **Audience**: system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/01-project-core/
- **Category**: 01 Project Core
- **Search Keywords**: ###, **expected, **password**:, --version, 2gb, 3.8+, 500mb, ```, `admin`, access, active!, api, available, backend, browser

## 5-Minute Setup Guide

This guide will get you up and running with the CVD (Vision Device Configuration) system in 5 minutes or less.

## Prerequisites Checklist

Before starting, ensure you have the following installed on your system:

- [ ] **Python 3.8+** - Check with `python --version` or `python3 --version`
- [ ] **pip** - Python package manager (usually comes with Python)
- [ ] **Git** - For version control (optional but recommended)
- [ ] **Web browser** - Chrome, Firefox, Safari, or Edge (modern versions)
- [ ] **Terminal/Command Prompt** - For running commands

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: Minimum 2GB available
- **Storage**: 500MB free space
- **Network**: Internet connection for AI features (optional)

## Environment Setup

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone [repository-url]
cd cvd-system

# Or download and extract the ZIP file to your desired directory
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

**Verification**: Your terminal prompt should now show `(venv)` indicating the virtual environment is active.

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

**Expected output**: You should see packages being installed, including Flask, SQLAlchemy, and other dependencies.

### Step 4: Configuration (Optional)

For AI-powered features, set up the Anthropic API key:

```bash
# On Windows:
set ANTHROPIC_API_KEY=your-key-here

# On macOS/Linux:
export ANTHROPIC_API_KEY="your-key-here"
```

**Note**: The system works without an API key, but AI features (planogram optimization, chat assistant) will use fallback logic.

## First Run Instructions

### Terminal 1: Start the Backend Server

```bash
# Make sure virtual environment is activated
# You should see (venv) in your terminal prompt

python app.py
```

**Expected output**:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
* Restarting with stat
* Debugger is active!
```

**Keep this terminal open** - the backend server needs to stay running.

### Terminal 2: Start the Frontend Server

Open a new terminal window/tab and run:

```bash
# Navigate to your project directory if needed
cd /path/to/cvd-system

# Start the frontend server
python -m http.server 8000
```

**Expected output**:
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

**Keep this terminal open** as well - the frontend server also needs to stay running.

## Access and Verification Steps

### Step 1: Open the Application

1. Open your web browser
2. Navigate to: `http://localhost:8000/`
3. You should see the CVD login page

### Step 2: Initial Login

Use the default administrator credentials:
- **Username**: `admin`
- **Password**: `admin`

### Step 3: Verify Core Functions

After logging in, verify these key areas work:

1. **Dashboard Access**: 
   - Click "Dashboard" - should show the home dashboard
   - Verify the map loads (may show default location)

2. **Device Management**:
   - Click "Coolers" - should show device listing page
   - Should see "No devices found" or existing devices

3. **Navigation Test**:
   - Try clicking different menu items
   - Each should load a different page in the main content area

4. **User Profile**:
   - Click your username in the top-right
   - Select "Profile" to verify user management works

### Step 4: System Status Verification

Check that both servers are responding:

1. **Backend API**: Visit `http://localhost:5000/api/auth/current-user`
   - Should return user information in JSON format

2. **Frontend**: Main interface at `http://localhost:8000/`
   - Should display the CVD interface without errors

## Quick Configuration

### Change Default Password (Recommended)

1. After logging in, click your username → "Profile"
2. Change the default admin password
3. Update other user accounts as needed

### Basic System Setup

1. **Company Settings**: Navigate to Settings → Company to configure your organization details
2. **User Management**: Add users with appropriate roles (Admin, Manager, Driver, Viewer)
3. **Device Setup**: Add your first vending machine device for testing

## Troubleshooting Common Issues

### Backend Server Won't Start
```bash
# Check if port 5000 is in use
netstat -an | grep 5000

# Try a different port
python app.py --port 5001
```

### Frontend Server Won't Start
```bash
# Check if port 8000 is in use
netstat -an | grep 8000

# Use a different port
python -m http.server 8001
```

### Database Issues
```bash
# Check if database file exists
ls -la cvd.db

# If missing, the app will create it automatically on first run
```

### Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall requirements
pip install -r requirements.txt
```

## Next Steps

Once you have the system running:

1. **Explore Documentation**: Check `/documentation/` for detailed guides
2. **Sample Data**: Load test data to explore features fully
3. **Mobile PWA**: Test the driver app at `/pages/driver-app/`
4. **AI Features**: Set up API keys for intelligent features
5. **Production Setup**: Review deployment documentation for live environments

## Quick Reference Commands

```bash
# Start both servers (in separate terminals)
# Terminal 1:
source venv/bin/activate && python app.py

# Terminal 2:
python -m http.server 8000

# Access URLs:
# Main Application: http://localhost:8000/
# Backend API: http://localhost:5000/
# Driver PWA: http://localhost:8000/pages/driver-app/
```

## Getting Help

- **Documentation**: Browse `/documentation/` for comprehensive guides
- **API Reference**: Check backend endpoints at `/api/` routes
- **Sample Files**: Look in `/docs/examples/` for reference data
- **Test Cases**: Review `/tests/` for usage examples

The CVD system is now ready for use! Proceed to explore the various features and refer to the detailed documentation for advanced configuration and usage patterns.