# CVD Security Audit Runbook


## Metadata
- **ID**: 05_DEVELOPMENT_DEPLOYMENT_RUNBOOKS_SECURITY_AUDIT
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #authentication #coding #data-layer #database #debugging #deployment #development #device-management #devops #integration #logistics #machine-learning #optimization #quality-assurance #route-management #security #testing #troubleshooting #vending-machine #workflows
- **Intent**: This runbook provides comprehensive security assessment and hardening procedures for the CVD (Vision Device Configuration) system
- **Audience**: system administrators, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/deployment/runbooks/
- **Category**: Runbooks
- **Search Keywords**: "200", "query., "secret., "session., --include=", .db, 1.0, 2024-01-01, 2024-04-01, <host>, \([^, \(x-[a-za-z-], \+., access., alignment

## Overview

This runbook provides comprehensive security assessment and hardening procedures for the CVD (Vision Device Configuration) system. It covers security auditing, vulnerability assessment, compliance verification, and hardening implementation for the Flask/SQLite architecture.

### Scope
- Application security assessment
- Infrastructure security audit
- Database security review
- Network security verification
- Compliance and regulatory checks
- Security hardening implementation

### Security Standards
- **OWASP Top 10** compliance
- **CIS Controls** implementation
- **NIST Cybersecurity Framework** alignment
- **SOC 2 Type II** readiness
- Industry best practices for web applications

## Table of Contents

1. [Security Assessment](#security-assessment)
2. [Application Security Audit](#application-security-audit)
3. [Infrastructure Security](#infrastructure-security)
4. [Database Security](#database-security)
5. [Network Security](#network-security)
6. [Compliance Verification](#compliance-verification)
7. [Security Hardening](#security-hardening)
8. [Vulnerability Management](#vulnerability-management)

## Security Assessment

### Comprehensive Security Scan

```bash
#!/bin/bash
echo "=== CVD COMPREHENSIVE SECURITY ASSESSMENT ==="

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SECURITY_REPORT_DIR="/opt/cvd/logs/security_audits"
REPORT_FILE="${SECURITY_REPORT_DIR}/security_audit_${TIMESTAMP}.log"

mkdir -p "$SECURITY_REPORT_DIR"

log_security() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$REPORT_FILE"
}

log_security "Starting comprehensive security assessment..."

# 1. System Information Gathering
log_security "=== System Information ==="

# OS and kernel information
OS_INFO=$(uname -a)
DISTRO=$(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
log_security "Operating System: $DISTRO"
log_security "Kernel: $OS_INFO"

# Installed packages with security relevance
log_security "Security-relevant packages:"
dpkg -l | grep -E "(ssl|crypto|security|firewall)" | head -n 10 | while read line; do
    log_security "  $line"
done 2>/dev/null || rpm -qa | grep -E "(ssl|crypto|security|firewall)" | head -n 10 | while read line; do
    log_security "  $line"
done

# 2. Network Security Assessment
log_security "=== Network Security Assessment ==="

# Open ports
log_security "Open network ports:"
netstat -tulpn | grep LISTEN | while read line; do
    log_security "  $line"
done

# Firewall status
if command -v ufw >/dev/null 2>&1; then
    UFW_STATUS=$(ufw status | head -n 1)
    log_security "UFW Firewall: $UFW_STATUS"
    
    if [[ "$UFW_STATUS" == *"active"* ]]; then
        ufw status | grep -v "Status:" | while read line; do
            log_security "  $line"
        done
    fi
fi

# Check for fail2ban
if systemctl is-active fail2ban >/dev/null 2>&1; then
    log_security "Fail2ban: Active"
    fail2ban-client status | while read line; do
        log_security "  $line"
    done
else
    log_security "⚠️  Fail2ban: Not installed or inactive"
fi

# 3. SSL/TLS Assessment
log_security "=== SSL/TLS Security Assessment ==="

# Check SSL certificate
if [ -f "/etc/letsencrypt/live/your-domain.com/cert.pem" ]; then
    CERT_EXPIRY=$(openssl x509 -in "/etc/letsencrypt/live/your-domain.com/cert.pem" -noout -enddate)
    log_security "SSL Certificate: $CERT_EXPIRY"
    
    # Check certificate strength
    CERT_BITS=$(openssl x509 -in "/etc/letsencrypt/live/your-domain.com/cert.pem" -noout -text | grep "Public-Key:" | grep -o "[0-9]*")
    log_security "Certificate key size: $CERT_BITS bits"
else
    log_security "⚠️  SSL Certificate: Not found or not configured"
fi

# Test SSL configuration
SSL_TEST_RESULT=$(curl -I -s --connect-timeout 5 https://your-domain.com/health 2>&1 | head -n 1)
if [[ "$SSL_TEST_RESULT" == *"200"* ]]; then
    log_security "✅ SSL connectivity test: PASSED"
else
    log_security "❌ SSL connectivity test: FAILED - $SSL_TEST_RESULT"
fi

# 4. Application Security Assessment
log_security "=== Application Security Assessment ==="

# Check for exposed debug information
if curl -s http://localhost:5000/ | grep -qi "debug\|error\|traceback\|exception"; then
    log_security "⚠️  Potential debug information exposure detected"
else
    log_security "✅ No obvious debug information exposure"
fi

# Check security headers
log_security "HTTP Security Headers:"
SECURITY_HEADERS=(
    "X-Frame-Options"
    "X-Content-Type-Options" 
    "X-XSS-Protection"
    "Strict-Transport-Security"
    "Content-Security-Policy"
    "Referrer-Policy"
)

for header in "${SECURITY_HEADERS[@]}"; do
    HEADER_VALUE=$(curl -I -s http://localhost:5000/health | grep -i "$header" || echo "Missing")
    log_security "  $header: $HEADER_VALUE"
done

# Check for default credentials
log_security "Default credentials check:"
if sqlite3 /opt/cvd/data/cvd.db "SELECT username FROM users WHERE username='admin' AND password_hash LIKE '%default%';" 2>/dev/null | grep -q admin; then
    log_security "⚠️  Default admin credentials may be in use"
else
    log_security "✅ No obvious default credentials found"
fi

# 5. File System Security
log_security "=== File System Security ==="

# Check permissions on sensitive files
SENSITIVE_FILES=(
    "/opt/cvd/config/.env"
    "/opt/cvd/data/cvd.db"
    "/etc/ssl/private"
    "/etc/systemd/system/cvd.service"
)

for file in "${SENSITIVE_FILES[@]}"; do
    if [ -f "$file" ] || [ -d "$file" ]; then
        PERMS=$(ls -ld "$file" 2>/dev/null)
        log_security "Permissions: $PERMS"
    fi
done

# Check for world-readable files in application directory
WORLD_READABLE=$(find /opt/cvd -type f -perm /004 2>/dev/null | head -n 10)
if [ -n "$WORLD_READABLE" ]; then
    log_security "⚠️  World-readable files found:"
    echo "$WORLD_READABLE" | while read file; do
        log_security "  $file"
    done
else
    log_security "✅ No world-readable files found in application directory"
fi

# 6. Process Security
log_security "=== Process Security ==="

# Check if CVD is running as non-root
CVD_USER=$(ps aux | grep -E "(gunicorn|python.*app)" | grep -v grep | head -n 1 | awk '{print $1}')
if [ "$CVD_USER" = "root" ]; then
    log_security "❌ Application running as root - SECURITY RISK"
else
    log_security "✅ Application running as user: $CVD_USER"
fi

# Check for SUID/SGID files
SUID_FILES=$(find /opt/cvd -type f \( -perm -4000 -o -perm -2000 \) 2>/dev/null)
if [ -n "$SUID_FILES" ]; then
    log_security "⚠️  SUID/SGID files found:"
    echo "$SUID_FILES" | while read file; do
        log_security "  $file"
    done
else
    log_security "✅ No SUID/SGID files found"
fi

log_security "Comprehensive security assessment completed"
log_security "Report saved to: $REPORT_FILE"
echo "Security assessment report: $REPORT_FILE"
```

### Automated Vulnerability Scanner

```bash
#!/bin/bash
echo "=== CVD VULNERABILITY SCANNER ==="

LOG_FILE="/opt/cvd/logs/vulnerability_scan_$(date +%Y%m%d_%H%M%S).log"

log_vuln() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_vuln "Starting vulnerability scan..."

# Install security scanning tools if not available
install_security_tools() {
    log_vuln "Installing security scanning tools..."
    
    # Install Lynis for system security audit
    if ! command -v lynis >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y lynis
    fi
    
    # Install chkrootkit for rootkit detection
    if ! command -v chkrootkit >/dev/null 2>&1; then
        sudo apt-get install -y chkrootkit
    fi
    
    # Install rkhunter for rootkit detection
    if ! command -v rkhunter >/dev/null 2>&1; then
        sudo apt-get install -y rkhunter
    fi
}

# Run system security audit with Lynis
run_lynis_scan() {
    log_vuln "Running Lynis system security audit..."
    
    if command -v lynis >/dev/null 2>&1; then
        LYNIS_REPORT="/tmp/lynis_cvd_$(date +%Y%m%d_%H%M%S)"
        
        sudo lynis audit system --quick --report-file "$LYNIS_REPORT" 2>/dev/null | while read line; do
            log_vuln "LYNIS: $line"
        done
        
        # Extract key findings
        if [ -f "${LYNIS_REPORT}.log" ]; then
            log_vuln "Lynis key findings:"
            grep -E "(WARNING|SUGGESTION)" "${LYNIS_REPORT}.log" | head -n 20 | while read line; do
                log_vuln "  $line"
            done
        fi
    else
        log_vuln "Lynis not available - skipping system audit"
    fi
}

# Check for rootkits
check_rootkits() {
    log_vuln "Scanning for rootkits and malware..."
    
    # chkrootkit scan
    if command -v chkrootkit >/dev/null 2>&1; then
        log_vuln "Running chkrootkit scan..."
        CHKROOTKIT_RESULT=$(sudo chkrootkit -q 2>/dev/null | grep -v "nothing found")
        
        if [ -z "$CHKROOTKIT_RESULT" ]; then
            log_vuln "✅ chkrootkit: No issues found"
        else
            log_vuln "⚠️  chkrootkit findings:"
            echo "$CHKROOTKIT_RESULT" | while read line; do
                log_vuln "  $line"
            done
        fi
    fi
    
    # rkhunter scan
    if command -v rkhunter >/dev/null 2>&1; then
        log_vuln "Running rkhunter scan..."
        sudo rkhunter --update >/dev/null 2>&1
        RKHUNTER_RESULT=$(sudo rkhunter --check --skip-keypress --report-warnings-only 2>/dev/null)
        
        if [ -z "$RKHUNTER_RESULT" ]; then
            log_vuln "✅ rkhunter: No warnings found"
        else
            log_vuln "⚠️  rkhunter warnings:"
            echo "$RKHUNTER_RESULT" | while read line; do
                log_vuln "  $line"
            done
        fi
    fi
}

# Check for outdated packages with security vulnerabilities
check_package_vulnerabilities() {
    log_vuln "Checking for package vulnerabilities..."
    
    # Check for available security updates
    if command -v apt >/dev/null 2>&1; then
        SECURITY_UPDATES=$(apt list --upgradable 2>/dev/null | grep -i security | wc -l)
        log_vuln "Available security updates: $SECURITY_UPDATES"
        
        if [ "$SECURITY_UPDATES" -gt 0 ]; then
            apt list --upgradable 2>/dev/null | grep -i security | head -n 10 | while read line; do
                log_vuln "  $line"
            done
        fi
    fi
}

# Python dependency vulnerability check
check_python_vulnerabilities() {
    log_vuln "Checking Python dependencies for vulnerabilities..."
    
    # Install safety if not available
    if ! /opt/cvd/app/venv/bin/pip show safety >/dev/null 2>&1; then
        /opt/cvd/app/venv/bin/pip install safety >/dev/null 2>&1
    fi
    
    # Check for vulnerable Python packages
    cd /opt/cvd/app
    SAFETY_RESULT=$(/opt/cvd/app/venv/bin/safety check --json 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        VULN_COUNT=$(echo "$SAFETY_RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null)
        
        if [ "$VULN_COUNT" = "0" ]; then
            log_vuln "✅ Python dependencies: No known vulnerabilities"
        else
            log_vuln "⚠️  Python vulnerabilities found: $VULN_COUNT"
            echo "$SAFETY_RESULT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for vuln in data[:5]:  # Show first 5 vulnerabilities
        print(f'  {vuln[0]}: {vuln[1]} (ID: {vuln[2]})')
except:
    pass
" | while read line; do
                log_vuln "$line"
            done
        fi
    else
        log_vuln "Unable to check Python dependencies"
    fi
}

# Web application vulnerability scan
check_web_vulnerabilities() {
    log_vuln "Scanning web application for common vulnerabilities..."
    
    # Basic OWASP Top 10 checks
    BASE_URL="http://localhost:5000"
    
    # Check for SQL injection (basic test)
    log_vuln "Testing for SQL injection vulnerabilities..."
    SQL_INJECTION_PAYLOADS=("'" "1' OR '1'='1" "'; DROP TABLE users; --")
    
    for payload in "${SQL_INJECTION_PAYLOADS[@]}"; do
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/auth/login" \
            -H "Content-Type: application/json" \
            -d "{\"username\":\"$payload\",\"password\":\"test\"}" 2>/dev/null)
        
        if [ "$RESPONSE" = "500" ]; then
            log_vuln "⚠️  Potential SQL injection vulnerability detected with payload: $payload"
        fi
    done
    
    # Check for XSS vulnerabilities (basic test)
    log_vuln "Testing for XSS vulnerabilities..."
    XSS_PAYLOADS=("<script>alert(1)</script>" "<img src=x onerror=alert(1)>")
    
    for payload in "${XSS_PAYLOADS[@]}"; do
        RESPONSE=$(curl -s "${BASE_URL}/?test=$payload" 2>/dev/null)
        if echo "$RESPONSE" | grep -q "$payload"; then
            log_vuln "⚠️  Potential XSS vulnerability detected"
        fi
    done
    
    # Check for directory traversal
    log_vuln "Testing for directory traversal..."
    TRAVERSAL_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/../../../etc/passwd" 2>/dev/null)
    if [ "$TRAVERSAL_RESPONSE" = "200" ]; then
        log_vuln "⚠️  Potential directory traversal vulnerability"
    else
        log_vuln "✅ Directory traversal test: PASSED"
    fi
    
    # Check for information disclosure
    log_vuln "Checking for information disclosure..."
    INFO_ENDPOINTS=("/.env" "/config" "/admin" "/.git" "/debug")
    
    for endpoint in "${INFO_ENDPOINTS[@]}"; do
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}${endpoint}" 2>/dev/null)
        if [ "$RESPONSE" = "200" ]; then
            log_vuln "⚠️  Potentially sensitive endpoint accessible: $endpoint"
        fi
    done
}

# Execute all vulnerability checks
install_security_tools
run_lynis_scan
check_rootkits
check_package_vulnerabilities
check_python_vulnerabilities
check_web_vulnerabilities

log_vuln "Vulnerability scan completed"
echo "Vulnerability scan report: $LOG_FILE"
```

## Application Security Audit

### Code Security Review

```bash
#!/bin/bash
echo "=== CVD APPLICATION SECURITY AUDIT ==="

APP_DIR="/opt/cvd/app"
AUDIT_LOG="/opt/cvd/logs/app_security_audit_$(date +%Y%m%d_%H%M%S).log"

log_audit() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$AUDIT_LOG"
}

log_audit "Starting application security audit..."

# 1. Static Code Analysis
perform_static_analysis() {
    log_audit "=== Static Code Analysis ==="
    
    cd "$APP_DIR"
    
    # Install bandit for Python security analysis
    if ! /opt/cvd/app/venv/bin/pip show bandit >/dev/null 2>&1; then
        /opt/cvd/app/venv/bin/pip install bandit >/dev/null 2>&1
    fi
    
    # Run bandit security scan
    log_audit "Running Bandit security scan..."
    BANDIT_RESULT=$(/opt/cvd/app/venv/bin/bandit -r . -f json 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        # Parse bandit results
        HIGH_SEVERITY=$(echo "$BANDIT_RESULT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    high_issues = [issue for issue in data.get('results', []) if issue.get('issue_severity') == 'HIGH']
    print(len(high_issues))
except:
    print(0)
")
        
        MEDIUM_SEVERITY=$(echo "$BANDIT_RESULT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    medium_issues = [issue for issue in data.get('results', []) if issue.get('issue_severity') == 'MEDIUM']
    print(len(medium_issues))
except:
    print(0)
")
        
        log_audit "Bandit scan results: $HIGH_SEVERITY high severity, $MEDIUM_SEVERITY medium severity issues"
        
        # Show high severity issues
        if [ "$HIGH_SEVERITY" -gt 0 ]; then
            log_audit "High severity security issues:"
            echo "$BANDIT_RESULT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for issue in data.get('results', []):
        if issue.get('issue_severity') == 'HIGH':
            print(f'  {issue[\"filename\"]}:{issue[\"line_number\"]} - {issue[\"issue_text\"]}')
except:
    pass
" | head -n 10 | while read line; do
                log_audit "$line"
            done
        fi
    else
        log_audit "Bandit scan failed or not available"
    fi
    
    # Manual security pattern checks
    log_audit "Checking for security anti-patterns..."
    
    # Check for hardcoded secrets
    SECRET_PATTERNS=("password.*=" "api_key.*=" "secret.*=" "token.*=")
    
    for pattern in "${SECRET_PATTERNS[@]}"; do
        MATCHES=$(grep -r -i "$pattern" --include="*.py" . | grep -v "example\|test\|demo" || true)
        if [ -n "$MATCHES" ]; then
            log_audit "⚠️  Potential hardcoded secrets found:"
            echo "$MATCHES" | head -n 5 | while read line; do
                log_audit "  $line"
            done
        fi
    done
    
    # Check for SQL injection vulnerabilities
    log_audit "Checking for SQL injection patterns..."
    SQL_PATTERNS=("execute.*format\|%" "query.*format\|%" "\"\s*\+.*\+\s*\"")
    
    for pattern in "${SQL_PATTERNS[@]}"; do
        MATCHES=$(grep -r -E "$pattern" --include="*.py" . || true)
        if [ -n "$MATCHES" ]; then
            log_audit "⚠️  Potential SQL injection patterns:"
            echo "$MATCHES" | head -n 3 | while read line; do
                log_audit "  $line"
            done
        fi
    done
    
    # Check for command injection vulnerabilities
    log_audit "Checking for command injection patterns..."
    CMD_PATTERNS=("os\.system\|subprocess\|eval\|exec")
    
    for pattern in "${CMD_PATTERNS[@]}"; do
        MATCHES=$(grep -r -E "$pattern" --include="*.py" . || true)
        if [ -n "$MATCHES" ]; then
            log_audit "⚠️  Potential command injection patterns:"
            echo "$MATCHES" | head -n 3 | while read line; do
                log_audit "  $line"
            done
        fi
    done
}

# 2. Configuration Security Review
review_configuration() {
    log_audit "=== Configuration Security Review ==="
    
    # Check environment configuration
    ENV_FILE="/opt/cvd/config/.env"
    if [ -f "$ENV_FILE" ]; then
        log_audit "Environment configuration security:"
        
        # Check file permissions
        ENV_PERMS=$(stat -c "%a" "$ENV_FILE")
        if [ "$ENV_PERMS" -le 600 ]; then
            log_audit "✅ Environment file permissions: $ENV_PERMS"
        else
            log_audit "⚠️  Environment file permissions too permissive: $ENV_PERMS"
        fi
        
        # Check for secure settings
        SECURE_CONFIGS=(
            "FLASK_ENV=production"
            "SESSION_COOKIE_SECURE=True"
            "SESSION_COOKIE_HTTPONLY=True"
            "FORCE_HTTPS=true"
        )
        
        for config in "${SECURE_CONFIGS[@]}"; do
            if grep -q "$config" "$ENV_FILE"; then
                log_audit "✅ $config"
            else
                log_audit "⚠️  Missing secure configuration: $config"
            fi
        done
        
        # Check for weak secrets
        if grep -E "SECRET.*=.{1,16}$" "$ENV_FILE" >/dev/null; then
            log_audit "⚠️  Potentially weak secret keys detected (too short)"
        else
            log_audit "✅ Secret keys appear to be adequately long"
        fi
    else
        log_audit "❌ Environment configuration file not found"
    fi
    
    # Check Flask application configuration
    log_audit "Flask application security configuration:"
    
    FLASK_SECURITY_CHECKS=(
        "app.config.*DEBUG.*False"
        "app.config.*TESTING.*False"
        "session.*permanent"
    )
    
    for check in "${FLASK_SECURITY_CHECKS[@]}"; do
        if grep -r -E "$check" --include="*.py" "$APP_DIR" >/dev/null; then
            log_audit "✅ Found security configuration: $check"
        else
            log_audit "⚠️  Security configuration not found or not set properly: $check"
        fi
    done
}

# 3. Authentication and Authorization Audit
audit_auth() {
    log_audit "=== Authentication and Authorization Audit ==="
    
    # Check password hashing implementation
    log_audit "Password security implementation:"
    
    if grep -r "bcrypt\|scrypt\|argon2" --include="*.py" "$APP_DIR" >/dev/null; then
        log_audit "✅ Strong password hashing algorithm detected"
    elif grep -r "hashlib.*sha" --include="*.py" "$APP_DIR" >/dev/null; then
        log_audit "⚠️  SHA hashing detected - consider using bcrypt/scrypt/argon2"
    elif grep -r "md5\|sha1" --include="*.py" "$APP_DIR" >/dev/null; then
        log_audit "❌ Weak hashing algorithm detected (MD5/SHA1)"
    else
        log_audit "❓ Password hashing implementation unclear"
    fi
    
    # Check session management
    log_audit "Session management security:"
    
    SESSION_CHECKS=(
        "session.*permanent"
        "session.*timeout"
        "session.*expire"
    )
    
    for check in "${SESSION_CHECKS[@]}"; do
        if grep -r -E "$check" --include="*.py" "$APP_DIR" >/dev/null; then
            log_audit "✅ Session security feature: $check"
        fi
    done
    
    # Check for session fixation protection
    if grep -r "session.*regenerate\|session.*new" --include="*.py" "$APP_DIR" >/dev/null; then
        log_audit "✅ Session regeneration detected"
    else
        log_audit "⚠️  No session regeneration detected - potential session fixation risk"
    fi
    
    # Check authorization implementation
    log_audit "Authorization implementation:"
    
    if grep -r "@.*require.*auth\|@.*login_required" --include="*.py" "$APP_DIR" >/dev/null; then
        log_audit "✅ Authentication decorators found"
    else
        log_audit "⚠️  No authentication decorators detected"
    fi
    
    if grep -r "role.*check\|permission.*check" --include="*.py" "$APP_DIR" >/dev/null; then
        log_audit "✅ Role/permission checking detected"
    else
        log_audit "⚠️  No role/permission checking detected"
    fi
}

# 4. Input Validation and Sanitization Audit
audit_input_validation() {
    log_audit "=== Input Validation and Sanitization Audit ==="
    
    # Check for input validation
    log_audit "Input validation implementation:"
    
    VALIDATION_PATTERNS=("validate\|sanitize\|escape\|clean")
    
    for pattern in "${VALIDATION_PATTERNS[@]}"; do
        MATCHES=$(grep -r -E "$pattern" --include="*.py" "$APP_DIR" | wc -l)
        if [ "$MATCHES" -gt 0 ]; then
            log_audit "✅ Input validation patterns found: $MATCHES instances"
        fi
    done
    
    # Check for dangerous functions without validation
    DANGEROUS_FUNCTIONS=("eval\|exec\|compile")
    
    for func in "${DANGEROUS_FUNCTIONS[@]}"; do
        MATCHES=$(grep -r -E "$func" --include="*.py" "$APP_DIR" || true)
        if [ -n "$MATCHES" ]; then
            log_audit "⚠️  Dangerous function usage detected:"
            echo "$MATCHES" | head -n 3 | while read line; do
                log_audit "  $line"
            done
        fi
    done
    
    # Check for XSS prevention
    if grep -r "escape\|safe\|Markup" --include="*.py" "$APP_DIR" >/dev/null; then
        log_audit "✅ XSS prevention measures detected"
    else
        log_audit "⚠️  No obvious XSS prevention detected"
    fi
    
    # Check CSRF protection
    if grep -r "csrf\|CSRFProtect" --include="*.py" "$APP_DIR" >/dev/null; then
        log_audit "✅ CSRF protection detected"
    else
        log_audit "⚠️  No CSRF protection detected"
    fi
}

# 5. Database Security Audit
audit_database() {
    log_audit "=== Database Security Audit ==="
    
    DATABASE_PATH="/opt/cvd/data/cvd.db"
    
    if [ -f "$DATABASE_PATH" ]; then
        # Check database file permissions
        DB_PERMS=$(stat -c "%a" "$DATABASE_PATH")
        if [ "$DB_PERMS" -le 644 ]; then
            log_audit "✅ Database file permissions: $DB_PERMS"
        else
            log_audit "⚠️  Database file permissions too permissive: $DB_PERMS"
        fi
        
        # Check for SQL injection protection
        if grep -r "parameterized\|prepared\|placeholder\|?" --include="*.py" "$APP_DIR" >/dev/null; then
            log_audit "✅ Parameterized queries detected"
        else
            log_audit "⚠️  No parameterized queries detected - SQL injection risk"
        fi
        
        # Check database connection security
        if grep -r "sqlite3.*timeout\|sqlite3.*isolation" --include="*.py" "$APP_DIR" >/dev/null; then
            log_audit "✅ Database connection security measures detected"
        fi
        
        # Analyze database schema for security issues
        log_audit "Database schema security analysis:"
        
        # Check for password storage
        PASSWORD_TABLES=$(sqlite3 "$DATABASE_PATH" ".schema" | grep -i password)
        if [ -n "$PASSWORD_TABLES" ]; then
            log_audit "Password storage tables found - verifying hashing:"
            sqlite3 "$DATABASE_PATH" "SELECT username, length(password_hash) as hash_length FROM users LIMIT 3;" | while read line; do
                log_audit "  $line"
            done
        fi
        
        # Check for sensitive data in logs
        if sqlite3 "$DATABASE_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%log%';" | grep -q log; then
            log_audit "Log tables detected - checking for sensitive data storage"
        fi
    else
        log_audit "❌ Database file not found: $DATABASE_PATH"
    fi
}

# Execute all audit functions
perform_static_analysis
review_configuration  
audit_auth
audit_input_validation
audit_database

log_audit "Application security audit completed"
echo "Application security audit report: $AUDIT_LOG"
```

## Infrastructure Security

### System Hardening

```bash
#!/bin/bash
echo "=== CVD INFRASTRUCTURE SECURITY HARDENING ==="

HARDENING_LOG="/opt/cvd/logs/security_hardening_$(date +%Y%m%d_%H%M%S).log"

log_harden() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$HARDENING_LOG"
}

log_harden "Starting infrastructure security hardening..."

# 1. SSH Hardening
harden_ssh() {
    log_harden "=== SSH Security Hardening ==="
    
    SSH_CONFIG="/etc/ssh/sshd_config"
    SSH_BACKUP="/etc/ssh/sshd_config.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Backup SSH configuration
    sudo cp "$SSH_CONFIG" "$SSH_BACKUP"
    log_harden "SSH configuration backed up to: $SSH_BACKUP"
    
    # SSH hardening settings
    SSH_HARDENING_SETTINGS=(
        "Protocol 2"
        "PermitRootLogin no"
        "PasswordAuthentication no"
        "PubkeyAuthentication yes"
        "PermitEmptyPasswords no"
        "MaxAuthTries 3"
        "ClientAliveInterval 300"
        "ClientAliveCountMax 2"
        "X11Forwarding no"
        "AllowUsers cvdapp"
        "Banner /etc/issue.net"
    )
    
    for setting in "${SSH_HARDENING_SETTINGS[@]}"; do
        KEY=$(echo "$setting" | cut -d' ' -f1)
        
        if grep -q "^$KEY" "$SSH_CONFIG"; then
            sudo sed -i "s/^$KEY.*/$setting/" "$SSH_CONFIG"
        else
            echo "$setting" | sudo tee -a "$SSH_CONFIG" >/dev/null
        fi
        
        log_harden "SSH hardening applied: $setting"
    done
    
    # Create SSH banner
    sudo tee /etc/issue.net << 'EOF'
***************************************************************************
                    UNAUTHORIZED ACCESS PROHIBITED
                        
This system is for authorized users only. All activities are monitored
and logged. Unauthorized access is prohibited and may result in criminal
prosecution.
***************************************************************************
EOF
    
    # Restart SSH service
    sudo systemctl reload sshd
    log_harden "SSH service reloaded with hardened configuration"
}

# 2. Firewall Configuration
configure_firewall() {
    log_harden "=== Firewall Configuration ==="
    
    # Install and configure UFW
    if ! command -v ufw >/dev/null 2>&1; then
        sudo apt-get update && sudo apt-get install -y ufw
        log_harden "UFW firewall installed"
    fi
    
    # Reset UFW rules
    sudo ufw --force reset
    
    # Default policies
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    
    # Essential services
    sudo ufw allow ssh
    sudo ufw allow 'Nginx Full'
    
    # CVD application (if needed for direct access)
    # sudo ufw allow 5000/tcp
    
    # Rate limiting for SSH
    sudo ufw limit ssh
    
    # Enable firewall
    sudo ufw --force enable
    
    log_harden "UFW firewall configured and enabled"
    
    # Install and configure fail2ban
    if ! command -v fail2ban-client >/dev/null 2>&1; then
        sudo apt-get install -y fail2ban
        log_harden "Fail2ban installed"
    fi
    
    # Create fail2ban configuration for CVD
    sudo tee /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
filter = nginx-badbots
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-noproxy]
enabled = true
port = http,https
filter = nginx-noproxy
logpath = /var/log/nginx/access.log
maxretry = 2

[cvd-auth]
enabled = true
port = http,https
filter = cvd-auth
logpath = /opt/cvd/logs/error.log
maxretry = 5
bantime = 600
EOF
    
    # Create custom filter for CVD authentication failures
    sudo tee /etc/fail2ban/filter.d/cvd-auth.conf << 'EOF'
[Definition]
failregex = .*authentication.*failed.*from.*<HOST>
            .*login.*failed.*from.*<HOST>
            .*unauthorized.*access.*from.*<HOST>
ignoreregex =
EOF
    
    sudo systemctl enable fail2ban
    sudo systemctl restart fail2ban
    log_harden "Fail2ban configured and started"
}

# 3. System Security Settings
apply_system_hardening() {
    log_harden "=== System Security Hardening ==="
    
    # Kernel security parameters
    sudo tee /etc/sysctl.d/99-security.conf << 'EOF'
# Network security
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.tcp_syncookies = 1
net.ipv4.ip_forward = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0
net.ipv6.conf.default.accept_source_route = 0

# Memory protection
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
kernel.yama.ptrace_scope = 1

# Process security
fs.suid_dumpable = 0
kernel.core_uses_pid = 1
EOF
    
    sudo sysctl -p /etc/sysctl.d/99-security.conf
    log_harden "Kernel security parameters applied"
    
    # File system security
    log_harden "Configuring file system security..."
    
    # Secure /tmp with noexec
    if ! mount | grep -q "/tmp.*noexec"; then
        sudo mount -o remount,noexec,nosuid,nodev /tmp 2>/dev/null || true
        log_harden "Temporary filesystem secured"
    fi
    
    # Set proper file permissions
    sudo chmod 700 /root
    sudo chmod 755 /etc/crontab
    sudo chmod -R 600 /etc/cron.hourly /etc/cron.daily /etc/cron.weekly /etc/cron.monthly 2>/dev/null || true
    
    log_harden "File system permissions hardened"
    
    # Remove unnecessary packages
    log_harden "Removing unnecessary packages..."
    UNNECESSARY_PACKAGES=("telnet" "rsh-client" "rsh-redone-client" "talk" "finger")
    
    for package in "${UNNECESSARY_PACKAGES[@]}"; do
        if dpkg -l | grep -q "^ii.*$package"; then
            sudo apt-get remove -y "$package" >/dev/null 2>&1
            log_harden "Removed package: $package"
        fi
    done
    
    # Disable unnecessary services
    UNNECESSARY_SERVICES=("avahi-daemon" "cups" "bluetooth")
    
    for service in "${UNNECESSARY_SERVICES[@]}"; do
        if systemctl is-enabled "$service" >/dev/null 2>&1; then
            sudo systemctl disable "$service" >/dev/null 2>&1
            sudo systemctl stop "$service" >/dev/null 2>&1
            log_harden "Disabled service: $service"
        fi
    done
}

# 4. Log Security Configuration
configure_log_security() {
    log_harden "=== Log Security Configuration ==="
    
    # Configure rsyslog for security logging
    sudo tee /etc/rsyslog.d/50-security.conf << 'EOF'
# Security logging
auth,authpriv.*                 /var/log/auth.log
*.*;auth,authpriv.none         -/var/log/syslog
daemon.*                       -/var/log/daemon.log
kern.*                         -/var/log/kern.log
mail.*                         -/var/log/mail.log
user.*                         -/var/log/user.log

# CVD application logs
local0.*                       /var/log/cvd-security.log
EOF
    
    sudo systemctl restart rsyslog
    
    # Configure log rotation for security logs
    sudo tee /etc/logrotate.d/security << 'EOF'
/var/log/auth.log
/var/log/cvd-security.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    copytruncate
    create 640 syslog adm
    postrotate
        systemctl reload rsyslog > /dev/null 2>&1 || true
    endscript
}
EOF
    
    log_harden "Security logging configured"
    
    # Set proper log file permissions
    sudo chmod 640 /var/log/auth.log 2>/dev/null || true
    sudo chmod 640 /opt/cvd/logs/*.log 2>/dev/null || true
    
    log_harden "Log file permissions secured"
}

# 5. Application-specific hardening
harden_application() {
    log_harden "=== Application-specific Security Hardening ==="
    
    # Secure application file permissions
    sudo find /opt/cvd/app -type f -name "*.py" -exec chmod 644 {} \;
    sudo find /opt/cvd/app -type d -exec chmod 755 {} \;
    sudo chmod 600 /opt/cvd/config/.env
    sudo chmod 644 /opt/cvd/data/cvd.db
    sudo chmod 755 /opt/cvd/logs
    sudo chmod 640 /opt/cvd/logs/*.log 2>/dev/null || true
    
    log_harden "Application file permissions secured"
    
    # Create security monitoring script
    sudo tee /opt/cvd/scripts/security_monitor.sh << 'EOF'
#!/bin/bash
# CVD Security Monitoring Script

SECURITY_LOG="/var/log/cvd-security.log"
ALERT_EMAIL="security@company.com"

# Monitor for security events
monitor_security_events() {
    # Check for failed login attempts
    FAILED_LOGINS=$(grep "authentication failed" /opt/cvd/logs/error.log | grep "$(date +%Y-%m-%d)" | wc -l)
    
    if [ "$FAILED_LOGINS" -gt 10 ]; then
        echo "$(date): WARNING - High number of failed login attempts: $FAILED_LOGINS" >> "$SECURITY_LOG"
        echo "High number of failed CVD login attempts: $FAILED_LOGINS" | \
            mail -s "CVD Security Alert" "$ALERT_EMAIL" 2>/dev/null || true
    fi
    
    # Check for suspicious file changes
    if find /opt/cvd/app -name "*.py" -mmin -60 | grep -q .; then
        echo "$(date): WARNING - Application files modified in last hour" >> "$SECURITY_LOG"
    fi
    
    # Check for database access anomalies
    DB_CONNECTIONS=$(lsof /opt/cvd/data/cvd.db 2>/dev/null | wc -l)
    if [ "$DB_CONNECTIONS" -gt 10 ]; then
        echo "$(date): WARNING - High number of database connections: $DB_CONNECTIONS" >> "$SECURITY_LOG"
    fi
}

monitor_security_events
EOF
    
    sudo chmod +x /opt/cvd/scripts/security_monitor.sh
    
    # Add to cron for regular monitoring
    (sudo crontab -l 2>/dev/null; echo "*/15 * * * * /opt/cvd/scripts/security_monitor.sh") | sudo crontab -
    
    log_harden "Security monitoring script configured"
}

# Execute hardening procedures
harden_ssh
configure_firewall
apply_system_hardening
configure_log_security
harden_application

log_harden "Infrastructure security hardening completed"
echo "Security hardening report: $HARDENING_LOG"
```

## Database Security

### SQLite Security Audit

```bash
#!/bin/bash
echo "=== CVD DATABASE SECURITY AUDIT ==="

DB_AUDIT_LOG="/opt/cvd/logs/database_security_audit_$(date +%Y%m%d_%H%M%S).log"
DATABASE_PATH="/opt/cvd/data/cvd.db"

log_db_audit() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$DB_AUDIT_LOG"
}

log_db_audit "Starting database security audit..."

# 1. Database File Security
audit_database_file() {
    log_db_audit "=== Database File Security ==="
    
    if [ ! -f "$DATABASE_PATH" ]; then
        log_db_audit "❌ Database file not found: $DATABASE_PATH"
        return 1
    fi
    
    # Check file permissions
    DB_PERMS=$(stat -c "%a" "$DATABASE_PATH")
    DB_OWNER=$(stat -c "%U:%G" "$DATABASE_PATH")
    DB_SIZE=$(stat -c "%s" "$DATABASE_PATH" | awk '{print int($1/1024/1024)"MB"}')
    
    log_db_audit "Database file: $DATABASE_PATH"
    log_db_audit "Permissions: $DB_PERMS"
    log_db_audit "Owner: $DB_OWNER"
    log_db_audit "Size: $DB_SIZE"
    
    # Security assessment
    if [ "$DB_PERMS" -le 644 ]; then
        log_db_audit "✅ File permissions are secure"
    else
        log_db_audit "⚠️  File permissions may be too permissive"
    fi
    
    if [ "$DB_OWNER" = "cvdapp:www-data" ] || [ "$DB_OWNER" = "cvdapp:cvdapp" ]; then
        log_db_audit "✅ File ownership is correct"
    else
        log_db_audit "⚠️  File ownership should be cvdapp:www-data"
    fi
    
    # Check for backup files
    BACKUP_FILES=$(find "$(dirname "$DATABASE_PATH")" -name "*.db*" -not -name "$(basename "$DATABASE_PATH")" 2>/dev/null)
    if [ -n "$BACKUP_FILES" ]; then
        log_db_audit "Database backup files found:"
        echo "$BACKUP_FILES" | while read file; do
            FILE_PERMS=$(stat -c "%a" "$file" 2>/dev/null || echo "unknown")
            log_db_audit "  $file (permissions: $FILE_PERMS)"
        done
    fi
}

# 2. Database Schema Security Analysis
analyze_schema() {
    log_db_audit "=== Database Schema Security Analysis ==="
    
    # Get database schema
    SCHEMA=$(sqlite3 "$DATABASE_PATH" ".schema")
    
    # Analyze tables for security concerns
    log_db_audit "Database tables:"
    echo "$SCHEMA" | grep "CREATE TABLE" | while read line; do
        TABLE_NAME=$(echo "$line" | sed -n 's/.*CREATE TABLE \([^ (]*\).*/\1/p')
        log_db_audit "  Table: $TABLE_NAME"
    done
    
    # Check for sensitive data storage
    log_db_audit "Sensitive data analysis:"
    
    # Check password storage
    if echo "$SCHEMA" | grep -qi "password"; then
        PASSWORD_COLUMNS=$(echo "$SCHEMA" | grep -i password)
        log_db_audit "Password storage detected:"
        echo "$PASSWORD_COLUMNS" | while read line; do
            log_db_audit "  $line"
        done
        
        # Check password hashing
        SAMPLE_PASSWORDS=$(sqlite3 "$DATABASE_PATH" "SELECT password_hash FROM users LIMIT 3;" 2>/dev/null | head -n 3)
        if [ -n "$SAMPLE_PASSWORDS" ]; then
            log_db_audit "Password hash samples (for length analysis):"
            echo "$SAMPLE_PASSWORDS" | while read hash; do
                HASH_LENGTH=$(echo "$hash" | wc -c)
                log_db_audit "  Hash length: $HASH_LENGTH characters"
            done
        fi
    fi
    
    # Check for API keys or secrets storage
    if echo "$SCHEMA" | grep -qi -E "api_key|secret|token"; then
        log_db_audit "⚠️  Potential API keys/secrets storage detected"
        echo "$SCHEMA" | grep -i -E "api_key|secret|token" | while read line; do
            log_db_audit "  $line"
        done
    fi
    
    # Check for PII storage
    PII_PATTERNS=("email|phone|ssn|address|credit_card")
    for pattern in "${PII_PATTERNS[@]}"; do
        if echo "$SCHEMA" | grep -qi "$pattern"; then
            log_db_audit "PII data detected: $pattern"
        fi
    done
    
    # Check for audit logging
    if echo "$SCHEMA" | grep -qi "audit\|log"; then
        log_db_audit "✅ Audit logging tables detected"
    else
        log_db_audit "⚠️  No obvious audit logging detected"
    fi
}

# 3. Access Control Analysis
analyze_access_control() {
    log_db_audit "=== Database Access Control Analysis ==="
    
    # Check current database connections
    DB_CONNECTIONS=$(lsof "$DATABASE_PATH" 2>/dev/null | wc -l)
    log_db_audit "Current database connections: $DB_CONNECTIONS"
    
    if [ "$DB_CONNECTIONS" -gt 0 ]; then
        lsof "$DATABASE_PATH" 2>/dev/null | while read line; do
            log_db_audit "  $line"
        done
    fi
    
    # Check SQLite security pragmas
    log_db_audit "SQLite security configuration:"
    
    SECURITY_PRAGMAS=(
        "foreign_keys"
        "secure_delete" 
        "recursive_triggers"
        "trusted_schema"
    )
    
    for pragma in "${SECURITY_PRAGMAS[@]}"; do
        VALUE=$(sqlite3 "$DATABASE_PATH" "PRAGMA $pragma;" 2>/dev/null || echo "unknown")
        log_db_audit "  PRAGMA $pragma: $VALUE"
    done
    
    # Check for database encryption (if supported)
    if sqlite3 "$DATABASE_PATH" "PRAGMA cipher_version;" 2>/dev/null | grep -q .; then
        log_db_audit "✅ Database encryption detected"
    else
        log_db_audit "⚠️  Database is not encrypted"
    fi
}

# 4. Data Integrity and Backup Analysis
analyze_integrity_backup() {
    log_db_audit "=== Data Integrity and Backup Analysis ==="
    
    # Database integrity check
    log_db_audit "Performing database integrity check..."
    INTEGRITY_RESULT=$(sqlite3 "$DATABASE_PATH" "PRAGMA integrity_check;" 2>/dev/null)
    
    if [ "$INTEGRITY_RESULT" = "ok" ]; then
        log_db_audit "✅ Database integrity check: PASSED"
    else
        log_db_audit "❌ Database integrity check: FAILED"
        log_db_audit "Integrity issues: $INTEGRITY_RESULT"
    fi
    
    # Foreign key check
    FK_VIOLATIONS=$(sqlite3 "$DATABASE_PATH" "PRAGMA foreign_key_check;" 2>/dev/null)
    if [ -z "$FK_VIOLATIONS" ]; then
        log_db_audit "✅ Foreign key integrity: PASSED"
    else
        log_db_audit "⚠️  Foreign key violations detected:"
        echo "$FK_VIOLATIONS" | head -n 10 | while read line; do
            log_db_audit "  $line"
        done
    fi
    
    # Check backup configuration
    BACKUP_DIR="/opt/cvd/backups"
    if [ -d "$BACKUP_DIR" ]; then
        BACKUP_COUNT=$(find "$BACKUP_DIR" -name "*.db*" | wc -l)
        RECENT_BACKUP=$(find "$BACKUP_DIR" -name "*.db*" -mtime -1 | head -n 1)
        
        log_db_audit "Database backups: $BACKUP_COUNT total"
        
        if [ -n "$RECENT_BACKUP" ]; then
            log_db_audit "✅ Recent backup found: $(basename "$RECENT_BACKUP")"
            
            # Test backup integrity
            BACKUP_INTEGRITY=$(sqlite3 "$RECENT_BACKUP" "PRAGMA integrity_check;" 2>/dev/null)
            if [ "$BACKUP_INTEGRITY" = "ok" ]; then
                log_db_audit "✅ Backup integrity: PASSED"
            else
                log_db_audit "❌ Backup integrity: FAILED"
            fi
        else
            log_db_audit "⚠️  No recent backup found (within 24 hours)"
        fi
    else
        log_db_audit "❌ Backup directory not found: $BACKUP_DIR"
    fi
}

# 5. Query Security Analysis
analyze_query_security() {
    log_db_audit "=== Query Security Analysis ==="
    
    # Check application code for SQL injection vulnerabilities
    APP_DIR="/opt/cvd/app"
    
    if [ -d "$APP_DIR" ]; then
        # Check for parameterized queries
        PARAM_QUERIES=$(find "$APP_DIR" -name "*.py" -exec grep -l "?" {} \; 2>/dev/null | wc -l)
        TOTAL_DB_FILES=$(find "$APP_DIR" -name "*.py" -exec grep -l "sqlite3\|cursor\|execute" {} \; 2>/dev/null | wc -l)
        
        if [ "$TOTAL_DB_FILES" -gt 0 ]; then
            log_db_audit "Database query files found: $TOTAL_DB_FILES"
            log_db_audit "Files with parameterized queries: $PARAM_QUERIES"
            
            if [ "$PARAM_QUERIES" -gt 0 ]; then
                PARAM_RATIO=$(echo "scale=2; ($PARAM_QUERIES * 100) / $TOTAL_DB_FILES" | bc)
                log_db_audit "Parameterized query usage: ${PARAM_RATIO}%"
                
                if (( $(echo "$PARAM_RATIO > 80" | bc -l) )); then
                    log_db_audit "✅ Good parameterized query usage"
                else
                    log_db_audit "⚠️  Low parameterized query usage - SQL injection risk"
                fi
            fi
        fi
        
        # Check for dangerous query patterns
        DANGEROUS_PATTERNS=("execute.*format\|%" "query.*format\|%" "f\".*SELECT\|INSERT\|UPDATE\|DELETE")
        
        for pattern in "${DANGEROUS_PATTERNS[@]}"; do
            MATCHES=$(find "$APP_DIR" -name "*.py" -exec grep -H -E "$pattern" {} \; 2>/dev/null)
            if [ -n "$MATCHES" ]; then
                log_db_audit "⚠️  Potentially dangerous query pattern found:"
                echo "$MATCHES" | head -n 5 | while read line; do
                    log_db_audit "  $line"
                done
            fi
        done
    fi
}

# 6. Generate Security Recommendations
generate_recommendations() {
    log_db_audit "=== Database Security Recommendations ==="
    
    # File system recommendations
    if [ "$(stat -c "%a" "$DATABASE_PATH")" -gt 644 ]; then
        log_db_audit "RECOMMENDATION: Restrict database file permissions to 640 or 644"
    fi
    
    # Backup recommendations
    if [ ! -d "/opt/cvd/backups" ] || [ $(find "/opt/cvd/backups" -name "*.db*" -mtime -1 | wc -l) -eq 0 ]; then
        log_db_audit "RECOMMENDATION: Implement automated daily database backups"
    fi
    
    # Encryption recommendations
    if ! sqlite3 "$DATABASE_PATH" "PRAGMA cipher_version;" 2>/dev/null | grep -q .; then
        log_db_audit "RECOMMENDATION: Consider implementing database encryption for sensitive data"
    fi
    
    # Access control recommendations
    if [ "$(lsof "$DATABASE_PATH" 2>/dev/null | wc -l)" -gt 5 ]; then
        log_db_audit "RECOMMENDATION: Monitor and limit database connection pools"
    fi
    
    # Query security recommendations
    log_db_audit "RECOMMENDATION: Ensure all database queries use parameterized statements"
    log_db_audit "RECOMMENDATION: Implement query logging for security monitoring"
    log_db_audit "RECOMMENDATION: Regular security audits of database schema and data"
}

# Execute all audit functions
audit_database_file
analyze_schema
analyze_access_control
analyze_integrity_backup
analyze_query_security
generate_recommendations

log_db_audit "Database security audit completed"
echo "Database security audit report: $DB_AUDIT_LOG"
```

## Network Security

### SSL/TLS and Network Security Audit

```bash
#!/bin/bash
echo "=== CVD NETWORK SECURITY AUDIT ==="

NETWORK_AUDIT_LOG="/opt/cvd/logs/network_security_audit_$(date +%Y%m%d_%H%M%S).log"

log_net_audit() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$NETWORK_AUDIT_LOG"
}

log_net_audit "Starting network security audit..."

# 1. SSL/TLS Configuration Audit
audit_ssl_tls() {
    log_net_audit "=== SSL/TLS Configuration Audit ==="
    
    DOMAIN="your-domain.com"  # Update with actual domain
    
    # Check SSL certificate
    if [ -f "/etc/letsencrypt/live/$DOMAIN/cert.pem" ]; then
        CERT_PATH="/etc/letsencrypt/live/$DOMAIN/cert.pem"
        
        # Certificate validity
        CERT_EXPIRY=$(openssl x509 -in "$CERT_PATH" -noout -enddate | cut -d= -f2)
        CERT_DAYS_REMAINING=$(( ($(date -d "$CERT_EXPIRY" +%s) - $(date +%s)) / 86400 ))
        
        log_net_audit "SSL Certificate expires: $CERT_EXPIRY"
        log_net_audit "Days remaining: $CERT_DAYS_REMAINING"
        
        if [ "$CERT_DAYS_REMAINING" -gt 30 ]; then
            log_net_audit "✅ Certificate expiry: OK"
        elif [ "$CERT_DAYS_REMAINING" -gt 7 ]; then
            log_net_audit "⚠️  Certificate expires soon"
        else
            log_net_audit "❌ Certificate expires very soon - URGENT renewal needed"
        fi
        
        # Certificate details
        CERT_SUBJECT=$(openssl x509 -in "$CERT_PATH" -noout -subject | sed 's/subject=//')
        CERT_ISSUER=$(openssl x509 -in "$CERT_PATH" -noout -issuer | sed 's/issuer=//')
        CERT_SERIAL=$(openssl x509 -in "$CERT_PATH" -noout -serial | sed 's/serial=//')
        
        log_net_audit "Certificate subject: $CERT_SUBJECT"
        log_net_audit "Certificate issuer: $CERT_ISSUER"
        log_net_audit "Certificate serial: $CERT_SERIAL"
        
        # Check key strength
        if [ -f "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ]; then
            KEY_BITS=$(openssl rsa -in "/etc/letsencrypt/live/$DOMAIN/privkey.pem" -text -noout 2>/dev/null | grep "Private-Key:" | grep -o "[0-9]*")
            log_net_audit "Private key strength: $KEY_BITS bits"
            
            if [ "$KEY_BITS" -ge 2048 ]; then
                log_net_audit "✅ Key strength: Adequate"
            else
                log_net_audit "⚠️  Key strength: Weak (should be at least 2048 bits)"
            fi
        fi
    else
        log_net_audit "❌ SSL certificate not found"
    fi
    
    # Test SSL configuration
    if command -v openssl >/dev/null 2>&1; then
        log_net_audit "Testing SSL connection..."
        
        # Test SSL handshake
        SSL_HANDSHAKE=$(echo "" | timeout 10 openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            log_net_audit "✅ SSL handshake: Successful"
            
            # Extract protocol and cipher information
            SSL_PROTOCOL=$(echo "$SSL_HANDSHAKE" | grep "Protocol" | head -n1)
            SSL_CIPHER=$(echo "$SSL_HANDSHAKE" | grep "Cipher" | head -n1)
            
            log_net_audit "SSL Protocol: $SSL_PROTOCOL"
            log_net_audit "SSL Cipher: $SSL_CIPHER"
            
            # Check for weak protocols
            if echo "$SSL_HANDSHAKE" | grep -q "TLSv1.3\|TLSv1.2"; then
                log_net_audit "✅ Strong TLS protocol in use"
            else
                log_net_audit "⚠️  Weak or outdated TLS protocol"
            fi
        else
            log_net_audit "❌ SSL handshake: Failed"
        fi
    fi
}

# 2. Network Configuration Audit
audit_network_config() {
    log_net_audit "=== Network Configuration Audit ==="
    
    # Check listening ports
    log_net_audit "Open ports analysis:"
    netstat -tulpn | grep LISTEN | while read line; do
        PORT=$(echo "$line" | awk '{print $4}' | cut -d: -f2)
        PROCESS=$(echo "$line" | awk '{print $7}')
        log_net_audit "  Port $PORT: $PROCESS"
    done
    
    # Check for unnecessary open ports
    DANGEROUS_PORTS=("21" "23" "25" "53" "135" "139" "445" "1433" "3389")
    
    for port in "${DANGEROUS_PORTS[@]}"; do
        if netstat -tulpn | grep ":$port "; then
            log_net_audit "⚠️  Potentially dangerous port open: $port"
        fi
    done
    
    # Check firewall status
    if command -v ufw >/dev/null 2>&1; then
        UFW_STATUS=$(ufw status)
        log_net_audit "UFW Firewall status:"
        echo "$UFW_STATUS" | while read line; do
            log_net_audit "  $line"
        done
        
        if echo "$UFW_STATUS" | grep -q "Status: active"; then
            log_net_audit "✅ Firewall: Active"
        else
            log_net_audit "❌ Firewall: Inactive"
        fi
    fi
    
    # Check for fail2ban
    if systemctl is-active fail2ban >/dev/null 2>&1; then
        log_net_audit "✅ Fail2ban: Active"
        
        # Check fail2ban status
        FAIL2BAN_STATUS=$(fail2ban-client status)
        log_net_audit "Fail2ban jails:"
        echo "$FAIL2BAN_STATUS" | while read line; do
            log_net_audit "  $line"
        done
        
        # Check current bans
        BANNED_IPS=$(fail2ban-client status sshd 2>/dev/null | grep "Banned IP list" | cut -d: -f2 | xargs)
        if [ -n "$BANNED_IPS" ]; then
            log_net_audit "Currently banned IPs: $BANNED_IPS"
        fi
    else
        log_net_audit "⚠️  Fail2ban: Not active"
    fi
}

# 3. NGINX Security Configuration
audit_nginx_security() {
    log_net_audit "=== NGINX Security Configuration Audit ==="
    
    NGINX_CONFIG="/etc/nginx/sites-available/cvd"
    
    if [ -f "$NGINX_CONFIG" ]; then
        log_net_audit "Analyzing NGINX configuration..."
        
        # Security headers check
        SECURITY_HEADERS=(
            "add_header.*X-Frame-Options"
            "add_header.*X-Content-Type-Options"
            "add_header.*X-XSS-Protection"
            "add_header.*Strict-Transport-Security"
            "add_header.*Content-Security-Policy"
            "add_header.*Referrer-Policy"
        )
        
        for header in "${SECURITY_HEADERS[@]}"; do
            if grep -q "$header" "$NGINX_CONFIG"; then
                HEADER_NAME=$(echo "$header" | sed 's/.*add_header.*\(X-[A-Za-z-]*\|Strict-Transport-Security\|Content-Security-Policy\|Referrer-Policy\).*/\1/')
                log_net_audit "✅ Security header configured: $HEADER_NAME"
            else
                HEADER_NAME=$(echo "$header" | sed 's/.*\(X-[A-Za-z-]*\|Strict-Transport-Security\|Content-Security-Policy\|Referrer-Policy\).*/\1/')
                log_net_audit "⚠️  Missing security header: $HEADER_NAME"
            fi
        done
        
        # SSL configuration check
        if grep -q "ssl_protocols.*TLSv1.3\|ssl_protocols.*TLSv1.2" "$NGINX_CONFIG"; then
            log_net_audit "✅ Modern SSL protocols configured"
        else
            log_net_audit "⚠️  SSL protocol configuration needs review"
        fi
        
        # Check for SSL ciphers
        if grep -q "ssl_ciphers" "$NGINX_CONFIG"; then
            log_net_audit "✅ SSL ciphers configured"
        else
            log_net_audit "⚠️  SSL ciphers not explicitly configured"
        fi
        
        # Server tokens check
        if grep -q "server_tokens off" "$NGINX_CONFIG"; then
            log_net_audit "✅ Server version hiding enabled"
        else
            log_net_audit "⚠️  Server version may be exposed"
        fi
        
        # Rate limiting check
        if grep -q "limit_req\|limit_conn" "$NGINX_CONFIG"; then
            log_net_audit "✅ Rate limiting configured"
        else
            log_net_audit "⚠️  No rate limiting detected"
        fi
    else
        log_net_audit "❌ NGINX configuration file not found: $NGINX_CONFIG"
    fi
}

# 4. Network Security Testing
test_network_security() {
    log_net_audit "=== Network Security Testing ==="
    
    DOMAIN="your-domain.com"
    
    # Test HTTP to HTTPS redirect
    log_net_audit "Testing HTTP to HTTPS redirect..."
    HTTP_RESPONSE=$(curl -s -I -L "http://$DOMAIN/health" | head -n 1)
    
    if echo "$HTTP_RESPONSE" | grep -q "200"; then
        REDIRECT_COUNT=$(curl -s -I -L "http://$DOMAIN/health" | grep -c "HTTP/")
        if [ "$REDIRECT_COUNT" -gt 1 ]; then
            log_net_audit "✅ HTTP to HTTPS redirect: Working"
        else
            log_net_audit "⚠️  HTTP to HTTPS redirect: May not be working"
        fi
    else
        log_net_audit "❌ Unable to test HTTP redirect"
    fi
    
    # Test security headers
    log_net_audit "Testing security headers..."
    SECURITY_HEADERS_TEST=$(curl -s -I "https://$DOMAIN/health")
    
    EXPECTED_HEADERS=("X-Frame-Options" "X-Content-Type-Options" "X-XSS-Protection" "Strict-Transport-Security")
    
    for header in "${EXPECTED_HEADERS[@]}"; do
        if echo "$SECURITY_HEADERS_TEST" | grep -q "$header"; then
            log_net_audit "✅ $header: Present"
        else
            log_net_audit "⚠️  $header: Missing"
        fi
    done
    
    # Test for information disclosure
    log_net_audit "Testing for information disclosure..."
    
    INFO_ENDPOINTS=("/.env" "/admin" "/.git" "/config" "/debug")
    
    for endpoint in "${INFO_ENDPOINTS[@]}"; do
        RESPONSE_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN$endpoint" 2>/dev/null)
        if [ "$RESPONSE_CODE" = "200" ]; then
            log_net_audit "⚠️  Sensitive endpoint accessible: $endpoint (HTTP $RESPONSE_CODE)"
        elif [ "$RESPONSE_CODE" = "404" ] || [ "$RESPONSE_CODE" = "403" ]; then
            log_net_audit "✅ Endpoint properly protected: $endpoint (HTTP $RESPONSE_CODE)"
        fi
    done
}

# 5. Network Monitoring and Intrusion Detection
check_intrusion_detection() {
    log_net_audit "=== Intrusion Detection and Monitoring ==="
    
    # Check for suspicious network activity
    log_net_audit "Analyzing network connections..."
    
    # Check for unusual connection counts
    CONNECTION_COUNT=$(netstat -an | grep :5000 | wc -l)
    log_net_audit "Current connections to application port: $CONNECTION_COUNT"
    
    if [ "$CONNECTION_COUNT" -gt 100 ]; then
        log_net_audit "⚠️  High number of connections - potential DDoS or high load"
    fi
    
    # Check for connections from suspicious IPs
    FOREIGN_CONNECTIONS=$(netstat -an | grep :5000 | grep -v "127.0.0.1\|localhost" | wc -l)
    log_net_audit "External connections: $FOREIGN_CONNECTIONS"
    
    # Check recent failed connection attempts in auth.log
    if [ -f "/var/log/auth.log" ]; then
        FAILED_SSH=$(grep "Failed password" /var/log/auth.log | grep "$(date +%Y-%m-%d)" | wc -l)
        log_net_audit "Failed SSH attempts today: $FAILED_SSH"
        
        if [ "$FAILED_SSH" -gt 20 ]; then
            log_net_audit "⚠️  High number of failed SSH attempts"
            
            # Show top attacking IPs
            TOP_ATTACKERS=$(grep "Failed password" /var/log/auth.log | grep "$(date +%Y-%m-%d)" | \
                awk '{print $(NF-3)}' | sort | uniq -c | sort -nr | head -5)
            log_net_audit "Top attacking IPs:"
            echo "$TOP_ATTACKERS" | while read line; do
                log_net_audit "  $line"
            done
        fi
    fi
    
    # Check for port scanning attempts
    if [ -f "/var/log/kern.log" ]; then
        PORT_SCANS=$(grep "martian source" /var/log/kern.log | grep "$(date +%Y-%m-%d)" | wc -l)
        if [ "$PORT_SCANS" -gt 0 ]; then
            log_net_audit "⚠️  Potential port scanning attempts: $PORT_SCANS"
        fi
    fi
}

# 6. Generate Network Security Recommendations
generate_network_recommendations() {
    log_net_audit "=== Network Security Recommendations ==="
    
    # SSL/TLS recommendations
    if [ ! -f "/etc/letsencrypt/live/your-domain.com/cert.pem" ]; then
        log_net_audit "RECOMMENDATION: Implement SSL/TLS certificate"
    fi
    
    # Firewall recommendations
    if ! ufw status | grep -q "Status: active"; then
        log_net_audit "RECOMMENDATION: Enable and configure UFW firewall"
    fi
    
    # Fail2ban recommendations
    if ! systemctl is-active fail2ban >/dev/null 2>&1; then
        log_net_audit "RECOMMENDATION: Install and configure fail2ban"
    fi
    
    # NGINX security recommendations
    log_net_audit "RECOMMENDATION: Ensure all security headers are configured in NGINX"
    log_net_audit "RECOMMENDATION: Implement rate limiting to prevent abuse"
    log_net_audit "RECOMMENDATION: Configure proper SSL/TLS settings"
    
    # Monitoring recommendations
    log_net_audit "RECOMMENDATION: Implement network monitoring and alerting"
    log_net_audit "RECOMMENDATION: Regular security scans and penetration testing"
    log_net_audit "RECOMMENDATION: Monitor and analyze access logs regularly"
}

# Execute all network audit functions
audit_ssl_tls
audit_network_config
audit_nginx_security
test_network_security
check_intrusion_detection
generate_network_recommendations

log_net_audit "Network security audit completed"
echo "Network security audit report: $NETWORK_AUDIT_LOG"
```

## Compliance Verification

### SOC 2 and Security Compliance Check

```bash
#!/bin/bash
echo "=== CVD COMPLIANCE VERIFICATION ==="

COMPLIANCE_LOG="/opt/cvd/logs/compliance_audit_$(date +%Y%m%d_%H%M%S).log"

log_compliance() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$COMPLIANCE_LOG"
}

log_compliance "Starting compliance verification audit..."

# 1. SOC 2 Type II Compliance Check
check_soc2_compliance() {
    log_compliance "=== SOC 2 Type II Compliance Check ==="
    
    # Security Principle
    log_compliance "Security Principle Assessment:"
    
    # Access controls
    if grep -q "authentication\|authorization" /opt/cvd/app/*.py; then
        log_compliance "✅ CC6.1 - Access controls implemented"
    else
        log_compliance "❌ CC6.1 - Access controls need review"
    fi
    
    # Logical access security
    SSH_CONFIG="/etc/ssh/sshd_config"
    if [ -f "$SSH_CONFIG" ] && grep -q "PasswordAuthentication no" "$SSH_CONFIG"; then
        log_compliance "✅ CC6.2 - SSH key-based authentication enforced"
    else
        log_compliance "❌ CC6.2 - Password authentication should be disabled"
    fi
    
    # Confidentiality controls
    if [ -f "/opt/cvd/config/.env" ] && [ "$(stat -c "%a" "/opt/cvd/config/.env")" -le 600 ]; then
        log_compliance "✅ CC6.7 - Confidential data protection"
    else
        log_compliance "❌ CC6.7 - Confidential data protection needs improvement"
    fi
    
    # Availability Principle  
    log_compliance "Availability Principle Assessment:"
    
    # System monitoring
    if systemctl is-active cvd >/dev/null 2>&1; then
        log_compliance "✅ A1.1 - System availability monitoring"
    else
        log_compliance "❌ A1.1 - System not running"
    fi
    
    # Backup and recovery
    if [ -d "/opt/cvd/backups" ] && [ $(find /opt/cvd/backups -name "*.db*" -mtime -1 | wc -l) -gt 0 ]; then
        log_compliance "✅ A1.2 - Backup and recovery procedures"
    else
        log_compliance "❌ A1.2 - Backup procedures need verification"
    fi
    
    # Processing Integrity
    log_compliance "Processing Integrity Assessment:"
    
    # Data validation
    if grep -r "validate\|sanitize" /opt/cvd/app/*.py >/dev/null 2>&1; then
        log_compliance "✅ PI1.1 - Data validation controls"
    else
        log_compliance "❌ PI1.1 - Data validation needs review"
    fi
    
    # Error handling
    if grep -r "try:\|except:\|error" /opt/cvd/app/*.py >/dev/null 2>&1; then
        log_compliance "✅ PI1.2 - Error handling implemented"
    else
        log_compliance "❌ PI1.2 - Error handling needs review"
    fi
}

# 2. GDPR Compliance Check
check_gdpr_compliance() {
    log_compliance "=== GDPR Compliance Check ==="
    
    # Right to be forgotten (data deletion)
    if grep -r "delete\|remove\|soft_delete" /opt/cvd/app/*.py >/dev/null 2>&1; then
        log_compliance "✅ GDPR Article 17 - Right to erasure implementation detected"
    else
        log_compliance "⚠️  GDPR Article 17 - Data deletion capabilities need review"
    fi
    
    # Data portability
    if grep -r "export\|download" /opt/cvd/app/*.py >/dev/null 2>&1; then
        log_compliance "✅ GDPR Article 20 - Data portability features detected"
    else
        log_compliance "⚠️  GDPR Article 20 - Data export capabilities need review"
    fi
    
    # Consent management
    if grep -r "consent\|agree\|accept" /opt/cvd/app/*.py >/dev/null 2>&1; then
        log_compliance "✅ GDPR Article 7 - Consent management detected"
    else
        log_compliance "⚠️  GDPR Article 7 - Consent management needs review"
    fi
    
    # Data breach notification (logging)
    if [ -f "/opt/cvd/logs/audit.log" ] || grep -r "audit\|log" /opt/cvd/app/*.py >/dev/null 2>&1; then
        log_compliance "✅ GDPR Article 33 - Audit logging for breach detection"
    else
        log_compliance "❌ GDPR Article 33 - Audit logging needs implementation"
    fi
    
    # Privacy by design
    if grep -r "encrypt\|hash\|secure" /opt/cvd/app/*.py >/dev/null 2>&1; then
        log_compliance "✅ GDPR Article 25 - Privacy by design principles"
    else
        log_compliance "⚠️  GDPR Article 25 - Privacy by design needs review"
    fi
}

# 3. PCI DSS Compliance (if handling payment data)
check_pci_dss_compliance() {
    log_compliance "=== PCI DSS Compliance Check ==="
    
    # Check if payment data is handled
    PAYMENT_KEYWORDS=("credit_card\|card_number\|cvv\|payment\|billing")
    
    PAYMENT_REFERENCES=$(find /opt/cvd -name "*.py" -exec grep -l -E "$PAYMENT_KEYWORDS" {} \; 2>/dev/null)
    
    if [ -n "$PAYMENT_REFERENCES" ]; then
        log_compliance "Payment data processing detected - PCI DSS applies"
        
        # PCI DSS Requirement 1: Firewall configuration
        if ufw status | grep -q "Status: active"; then
            log_compliance "✅ PCI DSS 1.1 - Firewall configuration"
        else
            log_compliance "❌ PCI DSS 1.1 - Firewall not properly configured"
        fi
        
        # PCI DSS Requirement 2: Default passwords
        if ! sqlite3 /opt/cvd/data/cvd.db "SELECT username FROM users WHERE password_hash='default' OR password_hash='admin';" 2>/dev/null | grep -q .; then
            log_compliance "✅ PCI DSS 2.1 - No default passwords"
        else
            log_compliance "❌ PCI DSS 2.1 - Default passwords detected"
        fi
        
        # PCI DSS Requirement 3: Cardholder data protection
        log_compliance "⚠️  PCI DSS 3.1 - Cardholder data encryption needs verification"
        
        # PCI DSS Requirement 4: Encrypted transmission
        if [ -f "/etc/letsencrypt/live/your-domain.com/cert.pem" ]; then
            log_compliance "✅ PCI DSS 4.1 - Encrypted transmission (SSL/TLS)"
        else
            log_compliance "❌ PCI DSS 4.1 - SSL/TLS encryption not configured"
        fi
        
        # PCI DSS Requirement 8: User authentication
        if grep -r "login\|authenticate" /opt/cvd/app/*.py >/dev/null 2>&1; then
            log_compliance "✅ PCI DSS 8.1 - User authentication system"
        else
            log_compliance "❌ PCI DSS 8.1 - Authentication system needs review"
        fi
        
        # PCI DSS Requirement 10: Logging and monitoring
        if [ -d "/opt/cvd/logs" ] && [ $(ls /opt/cvd/logs/*.log 2>/dev/null | wc -l) -gt 0 ]; then
            log_compliance "✅ PCI DSS 10.1 - Audit logging implemented"
        else
            log_compliance "❌ PCI DSS 10.1 - Audit logging needs implementation"
        fi
    else
        log_compliance "No payment data processing detected - PCI DSS may not apply"
    fi
}

# 4. HIPAA Compliance (if handling health data)
check_hipaa_compliance() {
    log_compliance "=== HIPAA Compliance Check ==="
    
    # Check if health information is handled
    HEALTH_KEYWORDS=("medical\|health\|patient\|diagnosis\|treatment")
    
    HEALTH_REFERENCES=$(find /opt/cvd -name "*.py" -exec grep -l -E "$HEALTH_KEYWORDS" {} \; 2>/dev/null)
    
    if [ -n "$HEALTH_REFERENCES" ]; then
        log_compliance "Health information processing detected - HIPAA may apply"
        
        # Administrative safeguards
        log_compliance "Administrative Safeguards:"
        if [ -f "/opt/cvd/policies/security_policy.md" ]; then
            log_compliance "✅ Security policies documented"
        else
            log_compliance "❌ Security policies need documentation"
        fi
        
        # Physical safeguards
        log_compliance "Physical Safeguards:"
        log_compliance "⚠️  Physical access controls need verification"
        
        # Technical safeguards
        log_compliance "Technical Safeguards:"
        
        # Access control
        if grep -r "role\|permission" /opt/cvd/app/*.py >/dev/null 2>&1; then
            log_compliance "✅ Role-based access control"
        else
            log_compliance "❌ Access control needs enhancement"
        fi
        
        # Audit controls
        if [ -f "/opt/cvd/logs/audit.log" ]; then
            log_compliance "✅ Audit logging implemented"
        else
            log_compliance "❌ Audit logging needs implementation"
        fi
        
        # Integrity controls
        if grep -r "hash\|checksum\|integrity" /opt/cvd/app/*.py >/dev/null 2>&1; then
            log_compliance "✅ Data integrity controls"
        else
            log_compliance "❌ Data integrity controls need implementation"
        fi
        
        # Transmission security
        if [ -f "/etc/letsencrypt/live/your-domain.com/cert.pem" ]; then
            log_compliance "✅ Transmission encryption (SSL/TLS)"
        else
            log_compliance "❌ Transmission encryption needs implementation"
        fi
    else
        log_compliance "No health information processing detected - HIPAA may not apply"
    fi
}

# 5. ISO 27001 Compliance Check
check_iso27001_compliance() {
    log_compliance "=== ISO 27001 Compliance Check ==="
    
    # A.9 Access Control
    log_compliance "A.9 Access Control:"
    
    if grep -r "authentication\|login" /opt/cvd/app/*.py >/dev/null 2>&1; then
        log_compliance "✅ A.9.1.1 - Access control policy implementation"
    else
        log_compliance "❌ A.9.1.1 - Access control needs review"
    fi
    
    if grep -r "session\|timeout" /opt/cvd/app/*.py >/dev/null 2>&1; then
        log_compliance "✅ A.9.1.2 - Access management procedures"
    else
        log_compliance "❌ A.9.1.2 - Session management needs review"
    fi
    
    # A.10 Cryptography
    log_compliance "A.10 Cryptography:"
    
    if grep -r "encrypt\|hash\|bcrypt" /opt/cvd/app/*.py >/dev/null 2>&1; then
        log_compliance "✅ A.10.1.1 - Cryptographic controls"
    else
        log_compliance "❌ A.10.1.1 - Cryptographic controls need implementation"
    fi
    
    # A.12 Operations Security
    log_compliance "A.12 Operations Security:"
    
    if [ -d "/opt/cvd/logs" ]; then
        log_compliance "✅ A.12.4.1 - Event logging implemented"
    else
        log_compliance "❌ A.12.4.1 - Event logging needs implementation"
    fi
    
    if [ -d "/opt/cvd/backups" ]; then
        log_compliance "✅ A.12.3.1 - Information backup procedures"
    else
        log_compliance "❌ A.12.3.1 - Backup procedures need implementation"
    fi
    
    # A.13 Communications Security
    log_compliance "A.13 Communications Security:"
    
    if [ -f "/etc/letsencrypt/live/your-domain.com/cert.pem" ]; then
        log_compliance "✅ A.13.1.1 - Network communications protection"
    else
        log_compliance "❌ A.13.1.1 - Network encryption needs implementation"
    fi
    
    # A.14 System Acquisition, Development and Maintenance
    log_compliance "A.14 System Development:"
    
    if grep -r "validate\|sanitize" /opt/cvd/app/*.py >/dev/null 2>&1; then
        log_compliance "✅ A.14.2.1 - Secure development procedures"
    else
        log_compliance "❌ A.14.2.1 - Input validation needs enhancement"
    fi
}

# 6. Generate Compliance Report
generate_compliance_report() {
    log_compliance "=== Compliance Assessment Summary ==="
    
    # Count compliance status
    TOTAL_CHECKS=$(grep -c "✅\|❌\|⚠️" "$COMPLIANCE_LOG")
    PASSED_CHECKS=$(grep -c "✅" "$COMPLIANCE_LOG")
    FAILED_CHECKS=$(grep -c "❌" "$COMPLIANCE_LOG")
    WARNING_CHECKS=$(grep -c "⚠️" "$COMPLIANCE_LOG")
    
    COMPLIANCE_PERCENTAGE=$(echo "scale=1; ($PASSED_CHECKS * 100) / $TOTAL_CHECKS" | bc)
    
    log_compliance "Compliance Assessment Results:"
    log_compliance "  Total checks: $TOTAL_CHECKS"
    log_compliance "  Passed: $PASSED_CHECKS (${COMPLIANCE_PERCENTAGE}%)"
    log_compliance "  Failed: $FAILED_CHECKS"
    log_compliance "  Warnings: $WARNING_CHECKS"
    
    # Risk assessment
    if (( $(echo "$COMPLIANCE_PERCENTAGE > 80" | bc -l) )); then
        log_compliance "Overall compliance status: GOOD"
    elif (( $(echo "$COMPLIANCE_PERCENTAGE > 60" | bc -l) )); then
        log_compliance "Overall compliance status: MODERATE - Improvements needed"
    else
        log_compliance "Overall compliance status: POOR - Significant improvements required"
    fi
    
    # Priority recommendations
    log_compliance "Priority Recommendations:"
    
    if [ "$FAILED_CHECKS" -gt 0 ]; then
        log_compliance "1. Address all failed compliance checks immediately"
    fi
    
    if [ "$WARNING_CHECKS" -gt 0 ]; then
        log_compliance "2. Review and resolve warning items"
    fi
    
    log_compliance "3. Implement continuous compliance monitoring"
    log_compliance "4. Schedule regular compliance audits"
    log_compliance "5. Document all security policies and procedures"
}

# Execute compliance checks
check_soc2_compliance
check_gdpr_compliance
check_pci_dss_compliance
check_hipaa_compliance
check_iso27001_compliance
generate_compliance_report

log_compliance "Compliance verification completed"
echo "Compliance audit report: $COMPLIANCE_LOG"
```

---

**Runbook Version**: 1.0  
**Last Updated**: 2024-01-01  
**Next Review Date**: 2024-04-01  
**Owner**: Security Team  
**Approver**: Chief Security Officer

**Security Standards:**
- OWASP Top 10 compliance
- CIS Controls implementation  
- NIST Cybersecurity Framework alignment
- SOC 2 Type II readiness
- Industry security best practices

**Audit Schedule:**
- Security assessment: Monthly
- Vulnerability scanning: Weekly
- Compliance verification: Quarterly
- Penetration testing: Annually