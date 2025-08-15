#!/bin/bash
# Smoke test script for deployment verification

set -e

# Configuration
BASE_URL="${1:-http://localhost:5000}"
TIMEOUT=10
MAX_RETRIES=5

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to log messages
log() {
    echo -e "${2:-$NC}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Function to perform HTTP test
http_test() {
    local endpoint="$1"
    local expected_status="$2"
    local description="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    log "Testing: $description" "$YELLOW"
    
    for i in $(seq 1 $MAX_RETRIES); do
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            --connect-timeout $TIMEOUT \
            --max-time $TIMEOUT \
            "${BASE_URL}${endpoint}" || echo "000")
        
        if [ "$response" = "$expected_status" ]; then
            log "✓ PASSED: $description (HTTP $response)" "$GREEN"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            return 0
        fi
        
        if [ $i -lt $MAX_RETRIES ]; then
            log "  Retry $i/$MAX_RETRIES..." "$YELLOW"
            sleep 2
        fi
    done
    
    log "✗ FAILED: $description (Expected: $expected_status, Got: $response)" "$RED"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    return 1
}

# Function to test API endpoint with data
api_test() {
    local endpoint="$1"
    local method="$2"
    local expected_status="$3"
    local description="$4"
    local data="$5"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    log "Testing API: $description" "$YELLOW"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            --connect-timeout $TIMEOUT \
            --max-time $TIMEOUT \
            -H "Content-Type: application/json" \
            "${BASE_URL}${endpoint}" || echo "000")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            --connect-timeout $TIMEOUT \
            --max-time $TIMEOUT \
            -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "${BASE_URL}${endpoint}" || echo "000")
    fi
    
    if [ "$response" = "$expected_status" ]; then
        log "✓ PASSED: $description (HTTP $response)" "$GREEN"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        log "✗ FAILED: $description (Expected: $expected_status, Got: $response)" "$RED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to test WebSocket connection
ws_test() {
    local endpoint="$1"
    local description="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    log "Testing WebSocket: $description" "$YELLOW"
    
    # Check if WebSocket endpoint responds
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        --connect-timeout $TIMEOUT \
        --max-time $TIMEOUT \
        -H "Upgrade: websocket" \
        -H "Connection: Upgrade" \
        "${BASE_URL}${endpoint}" || echo "000")
    
    if [ "$response" = "101" ] || [ "$response" = "426" ]; then
        log "✓ PASSED: $description" "$GREEN"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        log "✗ FAILED: $description (Got: $response)" "$RED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Main smoke tests
log "Starting smoke tests for: $BASE_URL" "$YELLOW"
log "========================================" "$YELLOW"

# Health check
http_test "/health" "200" "Health check endpoint"

# Static content
http_test "/" "200" "Homepage"
http_test "/manifest.json" "200" "PWA manifest"
http_test "/service-worker.js" "200" "Service worker"

# Authentication endpoints
api_test "/api/auth/current-user" "GET" "401" "Auth check (unauthenticated)"

# Core API endpoints
api_test "/api/devices" "GET" "401" "Devices API (requires auth)"
api_test "/api/planograms" "GET" "401" "Planograms API (requires auth)"
api_test "/api/products" "GET" "401" "Products API (requires auth)"

# AI endpoints
api_test "/api/ai/health" "GET" "200" "AI service health"

# WebSocket endpoints (if applicable)
# ws_test "/ws/" "WebSocket connection"

# Database connectivity test
log "Testing database connectivity..." "$YELLOW"
db_response=$(curl -s "${BASE_URL}/api/health" | grep -o '"database":[^,}]*' || echo "")
if [[ "$db_response" == *"healthy"* ]]; then
    log "✓ PASSED: Database connectivity" "$GREEN"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    log "✗ FAILED: Database connectivity" "$RED"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Redis connectivity test
log "Testing Redis connectivity..." "$YELLOW"
redis_response=$(curl -s "${BASE_URL}/api/health" | grep -o '"redis":[^,}]*' || echo "")
if [[ "$redis_response" == *"healthy"* ]]; then
    log "✓ PASSED: Redis connectivity" "$GREEN"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    log "✗ FAILED: Redis connectivity" "$RED"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Summary
log "========================================" "$YELLOW"
log "Smoke Test Results:" "$YELLOW"
log "Total Tests: $TOTAL_TESTS"
log "Passed: $PASSED_TESTS" "$GREEN"
log "Failed: $FAILED_TESTS" "$RED"

if [ $FAILED_TESTS -eq 0 ]; then
    log "✓ All smoke tests passed!" "$GREEN"
    exit 0
else
    log "✗ Some tests failed. Please check the logs." "$RED"
    exit 1
fi