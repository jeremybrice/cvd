# API Client Component


## Metadata
- **ID**: 04_IMPLEMENTATION_COMPONENTS_API_CLIENT
- **Type**: API Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #code #data-exchange #debugging #device-management #dex-parser #features #implementation #integration #logistics #machine-learning #metrics #operations #optimization #performance #planogram #product-placement #reporting #route-management #security #service-orders #troubleshooting #vending-machine
- **Intent**: The API client (`api
- **Audience**: developers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/04-implementation/components/
- **Category**: Components
- **Search Keywords**: ###, ####, (401), (403), (4xx), (5xx), 401, access, api, api.js, authentication, authorization, backoff, base, batching

## Overview

The API client (`api.js`) provides a comprehensive JavaScript interface for communicating with the CVD backend API. It implements error handling, retry logic, offline support, and authentication management for all frontend-backend interactions.

## Core Architecture

### CVDApi Class Structure

The `CVDApi` class is implemented as a singleton pattern providing a consistent interface across all frontend pages.

```javascript
class CVDApi {
    constructor() {
        this.baseUrl = '/api';
        this.retryDelay = 1000; // 1 second
        this.maxRetries = 3;
        this.offlineQueue = [];
        this.isOnline = navigator.onLine;
        
        // Initialize monitoring and interceptors
        this.setupOnlineMonitoring();
        this.setupAuthInterceptor();
    }
}

// Singleton instance
const cvdApi = new CVDApi();
```

### Request Architecture

#### Core Request Method
The `makeRequest` method serves as the foundation for all API communication:

```javascript
async makeRequest(method, endpoint, data = null, retries = 0) {
    const url = `${this.baseUrl}${endpoint}`;
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
        mode: 'cors',
        credentials: 'include'  // Include cookies for session
    };
    
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }
    
    // Request processing with error handling and retries
}
```

#### Request Configuration
- **Base URL**: Relative path `/api` for backend communication
- **Content Type**: JSON for structured data exchange
- **CORS Mode**: Cross-origin resource sharing enabled
- **Credentials**: Include cookies for session-based authentication
- **Method Support**: GET, POST, PUT, DELETE operations

## Error Handling System

### Multi-Layer Error Handling

#### 1. HTTP Status Code Handling
```javascript
if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error || `HTTP ${response.status}`);
}
```

#### 2. Network Error Detection
```javascript
// Handle network errors
if (error.message === 'Failed to fetch' || !navigator.onLine) {
    if (!this.isOnline && (method === 'POST' || method === 'PUT' || method === 'DELETE')) {
        // Queue write operations for later
        this.offlineQueue.push({ method, endpoint, data });
        console.log('API: Request queued for offline processing');
        return { offline: true, queued: true };
    }
}
```

#### 3. Retry Logic
```javascript
// Retry logic for transient failures
if (retries < this.maxRetries && this.isOnline) {
    console.log(`API: Retrying request (${retries + 1}/${this.maxRetries})...`);
    await new Promise(resolve => setTimeout(resolve, this.retryDelay));
    return this.makeRequest(method, endpoint, data, retries + 1);
}
```

### Error Categories

1. **Authentication Errors (401)**: Session expired or invalid credentials
2. **Authorization Errors (403)**: Insufficient permissions
3. **Network Errors**: Connection failures, timeouts
4. **Server Errors (5xx)**: Backend processing failures
5. **Client Errors (4xx)**: Invalid requests, missing data

## Authentication Integration

### Global Authentication Interceptor
The API client includes a global fetch interceptor that handles authentication automatically:

```javascript
setupAuthInterceptor() {
    const originalFetch = window.fetch;
    const api = this;
    
    // Override fetch to handle auth
    window.fetch = async function(...args) {
        const response = await originalFetch(...args);
        
        // Handle 401 responses globally
        if (response.status === 401 && !args[0].includes('/auth/login')) {
            // Clear user data
            localStorage.removeItem('user');
            
            // Redirect to login
            const currentPath = window.location.pathname + window.location.hash;
            window.location.href = `/pages/login.html?return=${encodeURIComponent(currentPath)}`;
        }
        
        return response;
    };
}
```

#### Authentication Flow Integration
- **Session Persistence**: Cookies automatically included in requests
- **401 Handling**: Automatic redirect to login page
- **Return URL**: Preserves current page for post-login redirect
- **User Context**: Clears local storage on session expiry

## Offline Support

### Online/Offline Monitoring
```javascript
// Monitor online/offline status
window.addEventListener('online', () => this.handleOnline());
window.addEventListener('offline', () => this.handleOffline());
```

### Offline Queue Management

#### Request Queueing
- **Write Operations**: POST, PUT, DELETE requests queued when offline
- **Read Operations**: Fail immediately with appropriate error messages
- **Queue Storage**: In-memory array for request details

#### Queue Processing
```javascript
async processOfflineQueue() {
    while (this.offlineQueue.length > 0) {
        const request = this.offlineQueue.shift();
        try {
            await this.makeRequest(request.method, request.endpoint, request.data);
        } catch (error) {
            console.error('Failed to process offline request:', error);
            // Re-queue if still offline
            if (!this.isOnline) {
                this.offlineQueue.unshift(request);
                break;
            }
        }
    }
}
```

## API Method Categories

### 1. Authentication Methods
```javascript
async login(username, password) {
    return await this.makeRequest('POST', '/auth/login', { username, password });
}

async logout() {
    const result = await this.makeRequest('POST', '/auth/logout');
    localStorage.removeItem('user');
    window.location.href = '/pages/login.html';
    return result;
}

async getCurrentUser() {
    return await this.makeRequest('GET', '/auth/current-user');
}

async changePassword(currentPassword, newPassword) {
    return await this.makeRequest('POST', '/auth/change-password', {
        currentPassword, newPassword
    });
}
```

### 2. Device Management
```javascript
async getDevices() {
    const devices = await this.makeRequest('GET', '/devices');
    return devices;
}

async createDevice(deviceData) {
    const device = {
        asset: deviceData.asset,
        cooler: deviceData.cooler,
        location_id: deviceData.location_id,
        model: deviceData.model,
        device_type_id: deviceData.device_type_id,
        cabinetConfiguration: deviceData.cabinetConfiguration || []
    };
    
    return await this.makeRequest('POST', '/devices', device);
}

async checkAssetExists(assetNumber) {
    try {
        const devices = await this.getDevices();
        return devices.some(device => device.asset === assetNumber);
    } catch (error) {
        console.error('Failed to check asset:', error);
        return false; // Allow form to continue (backend will validate)
    }
}
```

### 3. Planogram Management
```javascript
async getPlanogram(planogramKey) {
    return await this.makeRequest('GET', `/planograms/${planogramKey}`);
}

async savePlanogram(planogramKey, planogramData) {
    return await this.makeRequest('POST', '/planograms', {
        planogramKey, planogramData
    });
}

async getAIRecommendations(deviceId, cabinetIndex = 0) {
    return await this.makeRequest('POST', '/planograms/ai-suggestions', {
        device_id: deviceId,
        cabinet_index: cabinetIndex,
        optimization_type: 'full'
    });
}
```

### 4. Service Orders
```javascript
async getServiceOrders() {
    return await this.makeRequest('GET', '/service-orders');
}

async createServiceOrder(orderData) {
    return await this.makeRequest('POST', '/service-orders', orderData);
}

async executeServiceOrder(orderId, executionData) {
    return await this.makeRequest('POST', '/service-orders/execute', {
        orderId, ...executionData
    });
}
```

### 5. Analytics and Reports
```javascript
async getSales(options = {}) {
    let endpoint = '/sales';
    const params = new URLSearchParams();
    
    if (options.deviceId) params.append('device_id', options.deviceId);
    if (options.productId) params.append('product_id', options.productId);
    if (options.startDate) params.append('start_date', options.startDate);
    if (options.endDate) params.append('end_date', options.endDate);
    
    const queryString = params.toString();
    if (queryString) endpoint += `?${queryString}`;
    
    return await this.makeRequest('GET', endpoint);
}

async getAssetSalesReport(options = {}) {
    let endpoint = '/sales/asset-report';
    const params = new URLSearchParams();
    
    if (options.startDate) params.append('start_date', options.startDate);
    if (options.endDate) params.append('end_date', options.endDate);
    
    const queryString = params.toString();
    if (queryString) endpoint += `?${queryString}`;
    
    return await this.makeRequest('GET', endpoint);
}
```

### 6. User Management
```javascript
async getUsers(params = {}) {
    let endpoint = '/users';
    if (Object.keys(params).length > 0) {
        const queryString = new URLSearchParams(params).toString();
        endpoint += `?${queryString}`;
    }
    return await this.makeRequest('GET', endpoint);
}

async createUser(userData) {
    return await this.makeRequest('POST', '/users', userData);
}

async updateUser(userId, userData) {
    return await this.makeRequest('PUT', `/users/${userId}`, userData);
}

// User lifecycle management
async deactivateUser(userId) {
    return await this.makeRequest('PUT', `/users/${userId}/deactivate`);
}

async softDeleteUser(userId) {
    return await this.makeRequest('DELETE', `/users/${userId}/soft-delete`);
}
```

## Special Handling Cases

### File Upload Processing
```javascript
async parseDexFile(formData) {
    // FormData requires special handling - cannot use makeRequest
    const response = await fetch(`${this.baseUrl}/dex/parse`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
    });
    
    // Read the response body once
    const responseText = await response.text();
    
    // Try to parse as JSON
    let responseData;
    try {
        responseData = JSON.parse(responseText);
    } catch (e) {
        // If not valid JSON, wrap in error object
        responseData = {
            success: false,
            error: {
                message: responseText || `API error: ${response.status} ${response.statusText}`,
                line: 0, field: 0
            }
        };
    }
    
    if (!response.ok) {
        const errorMessage = responseData.error?.message || responseData.message || 
                           `API error: ${response.status} ${response.statusText}`;
        throw new Error(errorMessage);
    }
    
    return responseData;
}
```

### Health Check Implementation
```javascript
async checkHealth() {
    try {
        const result = await this.makeRequest('GET', '/health');
        return { ...result, available: true };
    } catch (error) {
        return { available: false, error: error.message };
    }
}
```

## Frontend Integration Patterns

### Page-Level Integration
Each frontend page imports and uses the API client:

```html
<!-- Absolute import path required -->
<script src="/api.js"></script>

<script>
// API client automatically available as cvdApi
const devices = await cvdApi.getDevices();
</script>
```

### Error Display Integration
```javascript
try {
    const result = await cvdApi.createDevice(deviceData);
    showSuccessMessage('Device created successfully');
} catch (error) {
    showErrorMessage(`Failed to create device: ${error.message}`);
}
```

### Loading State Management
```javascript
function showLoading() {
    document.getElementById('loadingSpinner').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

async function loadData() {
    try {
        showLoading();
        const data = await cvdApi.getDevices();
        displayData(data);
    } catch (error) {
        handleError(error);
    } finally {
        hideLoading();
    }
}
```

## Request/Response Processing

### Request Transformation
```javascript
// Automatic data serialization
if (data && (method === 'POST' || method === 'PUT')) {
    options.body = JSON.stringify(data);
}
```

### Response Processing
```javascript
// Automatic JSON parsing
return await response.json();

// Error response handling
const error = await response.json().catch(() => ({ error: 'Unknown error' }));
```

### Query Parameter Handling
```javascript
// Dynamic query string building
const params = new URLSearchParams();
if (options.deviceId) params.append('device_id', options.deviceId);
if (options.startDate) params.append('start_date', options.startDate);

const queryString = params.toString();
if (queryString) endpoint += `?${queryString}`;
```

## Performance Optimizations

### Connection Reuse
- **Keep-Alive**: Browser handles connection pooling automatically
- **Session Persistence**: Cookies eliminate per-request authentication overhead
- **Request Batching**: Multiple operations can be combined where appropriate

### Caching Strategy
- **Browser Caching**: Leverages browser's native caching for static endpoints
- **Local Storage**: User information cached for offline reference
- **Memory Caching**: In-memory storage for frequently accessed data

### Retry Strategy
- **Exponential Backoff**: Could be enhanced with exponential delay increase
- **Circuit Breaker**: Potential enhancement for repeated failures
- **Request Deduplication**: Prevents duplicate concurrent requests

## Error Recovery Patterns

### Automatic Recovery
1. **Network Reconnection**: Automatic queue processing when online
2. **Session Refresh**: Transparent handling of session expiry
3. **Request Retry**: Automatic retry for transient failures

### Manual Recovery
1. **User-Initiated Retry**: Explicit retry buttons in UI
2. **Data Refresh**: Manual refresh options for stale data
3. **Offline Sync**: Manual sync trigger for offline queued requests

## Integration with Authentication System

### Session Management
- **Cookie-Based Sessions**: Automatic inclusion in requests
- **Session Validation**: Handled by backend on each request
- **Expiry Handling**: Automatic redirect on session expiry

### Role-Based Feature Access
```javascript
// The API client doesn't enforce roles - this is handled by:
// 1. Backend authorization on each endpoint
// 2. Frontend UI hiding/showing based on user role
// 3. Router-level access control in index.html
```

## Module Export Support

### CommonJS Compatibility
```javascript
// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = cvdApi;
}
```

### Browser Global Access
```javascript
// Available globally as cvdApi in browser context
window.cvdApi = cvdApi;
```

## Debugging and Monitoring

### Console Logging
- **Request Tracking**: Logs retry attempts and offline queue operations
- **Error Reporting**: Detailed error messages for debugging
- **State Changes**: Online/offline state changes logged

### Development Tools
- **Network Tab**: All requests visible in browser dev tools
- **Console Output**: Detailed logging for troubleshooting
- **LocalStorage**: User session data available for inspection

## Common Usage Patterns

### Data Loading Pattern
```javascript
async function loadPageData() {
    try {
        const [devices, routes, products] = await Promise.all([
            cvdApi.getDevices(),
            cvdApi.getRoutes(),
            cvdApi.getProducts()
        ]);
        
        displayData({ devices, routes, products });
    } catch (error) {
        showErrorMessage(error.message);
    }
}
```

### Form Submission Pattern
```javascript
async function submitForm(formData) {
    try {
        const result = await cvdApi.createDevice(formData);
        showSuccessMessage('Device created successfully');
        redirectToDeviceList();
    } catch (error) {
        showErrorMessage(error.message);
        // Keep form open for corrections
    }
}
```

### Real-time Data Pattern
```javascript
// Periodic refresh for dashboard data
setInterval(async () => {
    try {
        const metrics = await cvdApi.getWeeklyMetrics();
        updateDashboard(metrics);
    } catch (error) {
        console.error('Failed to refresh metrics:', error);
    }
}, 30000); // 30 seconds
```