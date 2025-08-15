# Frontend Architecture Patterns


## Metadata
- **ID**: 03_ARCHITECTURE_PATTERNS_FRONTEND_PATTERNS
- **Type**: Architecture
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #architecture #authentication #data-exchange #data-layer #database #debugging #deployment #device-management #devops #dex-parser #driver-app #integration #logistics #machine-learning #mobile #operations #optimization #performance #planogram #product-placement #pwa #quality-assurance #route-management #security #service-orders #system-design #technical #testing #troubleshooting #vending-machine
- **Intent**: Architecture for Frontend Architecture Patterns
- **Audience**: managers, end users, architects
- **Related**: API_PATTERNS.md, SECURITY_PATTERNS.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/03-architecture/patterns/
- **Category**: Patterns
- **Search Keywords**: ###, 1.0, 2025-08-12, :root, ```css, accessibility, api, architecture, benefits:, boundaries, challenges, communication, component, cooler, cvd:

**Document Version:** 1.0  
**Last Updated:** 2025-08-12  
**Status:** Complete

## Introduction

This document outlines the frontend architectural patterns, component design strategies, and client-side best practices implemented in the CVD system. These patterns enable scalable, maintainable, and performant user interfaces across desktop and mobile platforms.

## Table of Contents

1. [Iframe-Based Micro-Frontend Architecture](#iframe-based-micro-frontend-architecture)
2. [Cross-Frame Communication Patterns](#cross-frame-communication-patterns)
3. [Component Architecture Patterns](#component-architecture-patterns)
4. [State Management Patterns](#state-management-patterns)
5. [API Client Patterns](#api-client-patterns)
6. [Progressive Web App Patterns](#progressive-web-app-patterns)
7. [Design System Integration](#design-system-integration)
8. [Error Handling and User Feedback](#error-handling-and-user-feedback)
9. [Performance Optimization Patterns](#performance-optimization-patterns)
10. [Accessibility Patterns](#accessibility-patterns)

## Iframe-Based Micro-Frontend Architecture

### Core Architecture Pattern

**Implementation in CVD:**
```html
<!-- Main shell (index.html) -->
<div class="app-layout">
    <nav class="navbar">
        <!-- Navigation shell -->
    </nav>
    <main class="content-area">
        <iframe id="content-frame" 
                src="pages/home-dashboard.html"
                sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                loading="eager">
        </iframe>
    </main>
</div>
```

```javascript
// Navigation system
const pageRoutes = {
    'home': 'pages/home-dashboard.html',
    'coolers': 'pages/PCP.html',
    'new-device': 'pages/INVD.html',
    'planogram': 'pages/NSPT.html',
    'service-orders': 'pages/service-orders.html',
    'route-schedule': 'pages/route-schedule.html',
    'asset-sales': 'pages/asset-sales.html',
    'product-sales': 'pages/product-sales.html',
    'database': 'pages/database-viewer.html',
    'dex-parser': 'pages/dex-parser.html',
    'company-settings': 'pages/company-settings.html',
    'user-management': 'pages/user-management.html',
    'profile': 'pages/profile.html'
};

function navigateTo(page) {
    const iframe = document.getElementById('content-frame');
    const route = pageRoutes[page];
    
    if (route) {
        // Show loading state
        showPageLoading();
        
        // Update iframe source
        iframe.src = route;
        
        // Update navigation state
        updateNavigation(page);
        
        // Update URL hash
        window.location.hash = page;
        
        // Track navigation
        trackPageView(page);
    }
}

// Handle browser back/forward
window.addEventListener('hashchange', () => {
    const page = window.location.hash.slice(1) || 'home';
    if (pageRoutes[page] && getCurrentPage() !== page) {
        navigateTo(page);
    }
});
```

### Benefits and Trade-offs

**Benefits:**
- **Independent Development**: Teams can develop pages independently
- **Technology Flexibility**: Different pages can use different technologies
- **Deployment Independence**: Pages can be deployed separately
- **Isolation**: Failures in one page don't affect others
- **Legacy Integration**: Easy to integrate existing applications

**Trade-offs:**
- **Communication Overhead**: Cross-frame messaging complexity
- **Performance**: Additional frame overhead
- **Shared State Challenges**: Limited shared state management
- **SEO Limitations**: Search engine indexing challenges

## Cross-Frame Communication Patterns

### Message-Based Communication

**Implementation in CVD:**
```javascript
// Parent frame message handler (index.html)
window.addEventListener('message', (event) => {
    // Validate origin for security
    if (event.origin !== window.location.origin) {
        console.warn('Ignored message from unauthorized origin:', event.origin);
        return;
    }
    
    const { type, payload } = event.data;
    
    switch (type) {
        case 'NAVIGATE':
            navigateTo(payload.page);
            break;
            
        case 'SHOW_TOAST':
            ToastManager.show(
                payload.toastType, 
                payload.message, 
                payload.duration, 
                payload.options
            );
            break;
            
        case 'UPDATE_USER_AVATAR':
            updateUserAvatar(payload.avatarData);
            break;
            
        case 'REFRESH_NAVIGATION_DATA':
            refreshNavigationBadges();
            break;
            
        case 'SET_PAGE_TITLE':
            updatePageTitle(payload.title);
            break;
            
        case 'KEYBOARD_SHORTCUT':
            handleGlobalKeyboardShortcut(payload);
            break;
            
        case 'LOADING_STATE':
            handlePageLoadingState(payload);
            break;
            
        case 'PAGE_READY':
            handlePageReady(payload);
            break;
            
        default:
            console.warn('Unknown message type:', type);
    }
});

// Child frame communication helper
function sendToParent(type, payload) {
    const message = { type, payload };
    window.parent.postMessage(message, window.location.origin);
}
```

### Toast Notification Pattern

**Implementation in CVD (toast-helper.js):**
```javascript
// Toast helper for iframe pages
window.Toast = {
    success: function(message, duration) {
        sendToast('success', message, duration);
    },
    
    error: function(message, duration) {
        sendToast('error', message, duration);
    },
    
    warning: function(message, duration) {
        sendToast('warning', message, duration);
    },
    
    info: function(message, duration) {
        sendToast('info', message, duration);
    }
};

function sendToast(type, message, duration, options) {
    const inIframe = window.self !== window.top;
    
    const toastData = {
        type: 'SHOW_TOAST',
        payload: {
            toastType: type,
            message: message,
            duration: duration || 4000,
            options: options || {}
        }
    };
    
    if (inIframe) {
        window.parent.postMessage(toastData, window.location.origin);
    } else {
        // Fallback for standalone usage
        if (window.ToastManager) {
            window.ToastManager.show(type, message, duration, options);
        }
    }
}

// Auto-detect API operations and show appropriate toasts
function autoDetectToasts() {
    const originalFetch = window.fetch;
    
    window.fetch = function(...args) {
        return originalFetch.apply(this, args).then(response => {
            const method = (args[1] && args[1].method) || 'GET';
            const url = args[0];
            
            if (response.ok && ['POST', 'PUT', 'DELETE'].includes(method.toUpperCase())) {
                // Auto-generate success messages based on URL patterns
                if (url.includes('/api/devices') && method === 'POST') {
                    Toast.success('Device created successfully');
                } else if (url.includes('/api/planograms') && method === 'POST') {
                    Toast.success('Planogram saved successfully');
                } else if (url.includes('/api/service-orders') && method === 'POST') {
                    Toast.success('Service order created successfully');
                }
            } else if (!response.ok && response.status >= 400) {
                // Auto-handle error responses
                response.clone().json().then(data => {
                    if (data.error || data.message) {
                        Toast.error(data.error || data.message);
                    }
                }).catch(() => {
                    // Handle non-JSON error responses
                    if (response.status === 401) {
                        Toast.error('Authentication required');
                    } else if (response.status === 403) {
                        Toast.error('Permission denied');
                    } else if (response.status >= 500) {
                        Toast.error('Server error occurred');
                    }
                });
            }
            
            return response;
        });
    };
}
```

### Navigation Communication Pattern

```javascript
// Navigation helper for iframe pages
window.Navigation = {
    // Navigate to another page
    goTo: function(page) {
        sendToParent('NAVIGATE', { page: page });
    },
    
    // Set page title in parent navigation
    setTitle: function(title) {
        sendToParent('SET_PAGE_TITLE', { title: title });
    },
    
    // Update notification badges
    updateBadge: function(badgeType, count) {
        sendToParent('UPDATE_BADGE', { type: badgeType, count: count });
    },
    
    // Refresh navigation data
    refresh: function() {
        sendToParent('REFRESH_NAVIGATION_DATA', {});
    }
};
```

## Component Architecture Patterns

### Page Component Structure

**Standard Page Template:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title</title>
    <link rel="stylesheet" href="/css/design-system.css">
    <style>
        /* Page-specific styles */
    </style>
</head>
<body>
    <div class="page-container">
        <header class="page-header">
            <h1 class="page-title">Page Title</h1>
            <div class="page-actions">
                <!-- Page-specific actions -->
            </div>
        </header>
        
        <main class="page-content">
            <!-- Main content area -->
        </main>
        
        <aside class="page-sidebar" style="display: none;">
            <!-- Optional sidebar -->
        </aside>
    </div>
    
    <!-- Scripts -->
    <script src="/api.js"></script>
    <script src="/auth-check.js"></script>
    <script src="/js/toast-helper.js"></script>
    <script>
        // Page-specific JavaScript
    </script>
</body>
</html>
```

### Reusable Component Patterns

**Modal Component Pattern:**
```javascript
class ModalComponent {
    constructor(options = {}) {
        this.options = {
            title: options.title || 'Modal',
            size: options.size || 'medium',
            closeOnOverlay: options.closeOnOverlay !== false,
            closeOnEscape: options.closeOnEscape !== false,
            ...options
        };
        
        this.isOpen = false;
        this.createElement();
        this.bindEvents();
    }
    
    createElement() {
        this.modal = document.createElement('div');
        this.modal.className = `modal modal-${this.options.size}`;
        this.modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-container">
                <div class="modal-header">
                    <h3 class="modal-title">${this.options.title}</h3>
                    <button class="modal-close" type="button">&times;</button>
                </div>
                <div class="modal-body">
                    ${this.options.content || ''}
                </div>
                <div class="modal-footer">
                    ${this.options.footer || ''}
                </div>
            </div>
        `;
        
        document.body.appendChild(this.modal);
    }
    
    bindEvents() {
        // Close button
        this.modal.querySelector('.modal-close').addEventListener('click', () => {
            this.close();
        });
        
        // Overlay click
        if (this.options.closeOnOverlay) {
            this.modal.querySelector('.modal-backdrop').addEventListener('click', () => {
                this.close();
            });
        }
        
        // Escape key
        if (this.options.closeOnEscape) {
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });
        }
    }
    
    open() {
        this.modal.classList.add('active');
        this.isOpen = true;
        
        // Focus management
        const firstFocusable = this.modal.querySelector('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) {
            firstFocusable.focus();
        }
        
        // Emit event
        this.emit('open');
    }
    
    close() {
        this.modal.classList.remove('active');
        this.isOpen = false;
        
        // Emit event
        this.emit('close');
    }
    
    setContent(content) {
        this.modal.querySelector('.modal-body').innerHTML = content;
    }
    
    destroy() {
        this.modal.remove();
    }
    
    emit(eventName, data = {}) {
        const event = new CustomEvent(`modal:${eventName}`, { detail: data });
        this.modal.dispatchEvent(event);
    }
}
```

**Data Table Component Pattern:**
```javascript
class DataTable {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            columns: options.columns || [],
            data: options.data || [],
            sortable: options.sortable !== false,
            paginated: options.paginated !== false,
            pageSize: options.pageSize || 50,
            searchable: options.searchable !== false,
            actions: options.actions || [],
            ...options
        };
        
        this.currentPage = 1;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.searchTerm = '';
        
        this.render();
        this.bindEvents();
    }
    
    render() {
        this.container.innerHTML = `
            <div class="data-table-wrapper">
                ${this.options.searchable ? this.renderSearchBar() : ''}
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            ${this.renderHeader()}
                        </thead>
                        <tbody>
                            ${this.renderBody()}
                        </tbody>
                    </table>
                </div>
                ${this.options.paginated ? this.renderPagination() : ''}
            </div>
        `;
    }
    
    renderHeader() {
        return `
            <tr>
                ${this.options.columns.map(col => `
                    <th class="table-header ${this.options.sortable ? 'sortable' : ''}" 
                        data-column="${col.key}">
                        ${col.label}
                        ${this.options.sortable ? '<span class="sort-indicator"></span>' : ''}
                    </th>
                `).join('')}
                ${this.options.actions.length > 0 ? '<th class="actions-header">Actions</th>' : ''}
            </tr>
        `;
    }
    
    renderBody() {
        const data = this.getFilteredAndSortedData();
        const startIndex = (this.currentPage - 1) * this.options.pageSize;
        const endIndex = startIndex + this.options.pageSize;
        const pageData = data.slice(startIndex, endIndex);
        
        return pageData.map(row => `
            <tr data-id="${row.id || ''}">
                ${this.options.columns.map(col => `
                    <td data-column="${col.key}">
                        ${this.formatCellValue(row[col.key], col)}
                    </td>
                `).join('')}
                ${this.options.actions.length > 0 ? `
                    <td class="actions-cell">
                        ${this.renderActions(row)}
                    </td>
                ` : ''}
            </tr>
        `).join('');
    }
    
    formatCellValue(value, column) {
        if (column.formatter && typeof column.formatter === 'function') {
            return column.formatter(value);
        }
        
        if (value === null || value === undefined) {
            return '-';
        }
        
        return value;
    }
    
    getFilteredAndSortedData() {
        let data = [...this.options.data];
        
        // Apply search filter
        if (this.searchTerm) {
            data = data.filter(row => {
                return this.options.columns.some(col => {
                    const value = row[col.key];
                    return value && value.toString().toLowerCase().includes(this.searchTerm.toLowerCase());
                });
            });
        }
        
        // Apply sorting
        if (this.sortColumn) {
            data.sort((a, b) => {
                const aVal = a[this.sortColumn];
                const bVal = b[this.sortColumn];
                
                if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
                if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
                return 0;
            });
        }
        
        return data;
    }
}
```

## State Management Patterns

### Local Storage Pattern

```javascript
class LocalStateManager {
    constructor(namespace) {
        this.namespace = namespace;
        this.listeners = new Map();
    }
    
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(`${this.namespace}:${key}`);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.warn('Failed to parse localStorage item:', key, e);
            return defaultValue;
        }
    }
    
    set(key, value) {
        try {
            localStorage.setItem(`${this.namespace}:${key}`, JSON.stringify(value));
            this.notifyListeners(key, value);
        } catch (e) {
            console.error('Failed to set localStorage item:', key, e);
        }
    }
    
    remove(key) {
        localStorage.removeItem(`${this.namespace}:${key}`);
        this.notifyListeners(key, null);
    }
    
    clear() {
        const keys = Object.keys(localStorage).filter(key => 
            key.startsWith(`${this.namespace}:`)
        );
        
        keys.forEach(key => localStorage.removeItem(key));
        
        // Notify all listeners
        this.listeners.forEach((callbacks, key) => {
            callbacks.forEach(callback => callback(null, key));
        });
    }
    
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, []);
        }
        
        this.listeners.get(key).push(callback);
        
        // Return unsubscribe function
        return () => {
            const callbacks = this.listeners.get(key);
            if (callbacks) {
                const index = callbacks.indexOf(callback);
                if (index > -1) {
                    callbacks.splice(index, 1);
                }
            }
        };
    }
    
    notifyListeners(key, value) {
        const callbacks = this.listeners.get(key);
        if (callbacks) {
            callbacks.forEach(callback => callback(value, key));
        }
    }
}

// Usage
const appState = new LocalStateManager('cvd-app');

// User preferences
const userPrefs = {
    theme: appState.get('theme', 'light'),
    pageSize: appState.get('pageSize', 50),
    lastPage: appState.get('lastPage', 'home')
};

// Listen for changes
appState.subscribe('theme', (newTheme) => {
    document.body.className = `theme-${newTheme}`;
});
```

### Session State Pattern

```javascript
class SessionStateManager {
    constructor() {
        this.state = new Map();
        this.listeners = new Map();
    }
    
    setState(key, value) {
        const oldValue = this.state.get(key);
        this.state.set(key, value);
        
        // Notify listeners
        const callbacks = this.listeners.get(key);
        if (callbacks) {
            callbacks.forEach(callback => callback(value, oldValue));
        }
    }
    
    getState(key, defaultValue = null) {
        return this.state.get(key) ?? defaultValue;
    }
    
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, []);
        }
        
        this.listeners.get(key).push(callback);
        
        return () => {
            const callbacks = this.listeners.get(key);
            if (callbacks) {
                const index = callbacks.indexOf(callback);
                if (index > -1) {
                    callbacks.splice(index, 1);
                }
            }
        };
    }
    
    clearState() {
        this.state.clear();
        // Notify all listeners with null values
        this.listeners.forEach((callbacks, key) => {
            callbacks.forEach(callback => callback(null, this.state.get(key)));
        });
    }
}

// Global session state
window.SessionState = new SessionStateManager();
```

## API Client Patterns

### Centralized API Client

**Implementation in CVD (api.js):**
```javascript
class CVDApi {
    constructor() {
        this.baseUrl = '/api';
        this.retryDelay = 1000;
        this.maxRetries = 3;
        this.offlineQueue = [];
        this.isOnline = navigator.onLine;
        
        this.setupAuthInterceptor();
        this.setupOfflineHandling();
    }
    
    setupAuthInterceptor() {
        const originalFetch = window.fetch;
        
        window.fetch = async function(...args) {
            const response = await originalFetch(...args);
            
            // Handle 401 responses globally
            if (response.status === 401 && !args[0].includes('/auth/login')) {
                localStorage.removeItem('user');
                const currentPath = window.location.pathname + window.location.hash;
                window.location.href = `/pages/login.html?return=${encodeURIComponent(currentPath)}`;
            }
            
            return response;
        };
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const config = {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        // Handle request body
        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }
        
        let attempt = 0;
        
        while (attempt <= this.maxRetries) {
            try {
                const response = await fetch(url, config);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                return data;
                
            } catch (error) {
                attempt++;
                
                if (attempt > this.maxRetries) {
                    throw error;
                }
                
                // Wait before retry
                await new Promise(resolve => 
                    setTimeout(resolve, this.retryDelay * attempt)
                );
            }
        }
    }
    
    // Resource-specific methods
    async getDevices(filters = {}) {
        const queryParams = new URLSearchParams(filters);
        return this.request(`/devices?${queryParams}`);
    }
    
    async createDevice(deviceData) {
        return this.request('/devices', {
            method: 'POST',
            body: deviceData
        });
    }
    
    async updateDevice(deviceId, deviceData) {
        return this.request(`/devices/${deviceId}`, {
            method: 'PUT',
            body: deviceData
        });
    }
    
    async deleteDevice(deviceId) {
        return this.request(`/devices/${deviceId}`, {
            method: 'DELETE'
        });
    }
}

// Global API instance
window.api = new CVDApi();
```

## Progressive Web App Patterns

### Service Worker Integration

**Implementation in CVD:**
```javascript
// service-worker.js
const CACHE_NAME = 'cvd-cache-v1';
const STATIC_ASSETS = [
    '/',
    '/css/design-system.css',
    '/api.js',
    '/manifest.json',
    '/images/icons/icon-192x192.png',
    '/images/icons/icon-512x512.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(STATIC_ASSETS))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
});

// Push notification handling
self.addEventListener('push', event => {
    const options = {
        body: event.data.text(),
        icon: '/images/icons/icon-192x192.png',
        badge: '/images/icons/icon-72x72.png'
    };
    
    event.waitUntil(
        self.registration.showNotification('CVD Notification', options)
    );
});
```

## Design System Integration

### CSS Custom Properties Pattern

**Implementation in CVD (design-system.css):**
```css
:root {
  /* Color System */
  --color-primary-500: #006dfe;
  --color-neutral-0: #ffffff;
  --color-neutral-900: #212529;
  --color-success: #28a745;
  --color-danger: #dc3545;
  
  /* Typography */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --text-base: 1rem;
  --font-medium: 500;
  
  /* Spacing */
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  
  /* Layout */
  --nav-height: 64px;
  --sidebar-width: 280px;
  --container-max: 1200px;
  
  /* Animation */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
}

/* Component classes using design tokens */
.btn {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast);
}

.btn-primary {
  background: var(--color-primary-500);
  color: var(--color-neutral-0);
}
```

## Error Handling and User Feedback

### Global Error Handling Pattern

```javascript
class ErrorHandler {
    constructor() {
        this.setupGlobalHandlers();
    }
    
    setupGlobalHandlers() {
        // JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleError({
                type: 'javascript',
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error
            });
        });
        
        // Promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError({
                type: 'promise',
                message: event.reason.message || 'Unhandled promise rejection',
                error: event.reason
            });
        });
        
        // Network errors
        this.setupNetworkErrorHandling();
    }
    
    setupNetworkErrorHandling() {
        const originalFetch = window.fetch;
        
        window.fetch = async function(...args) {
            try {
                const response = await originalFetch(...args);
                
                if (!response.ok) {
                    ErrorHandler.instance.handleNetworkError(response, args[0]);
                }
                
                return response;
            } catch (error) {
                ErrorHandler.instance.handleNetworkError(error, args[0]);
                throw error;
            }
        };
    }
    
    handleError(errorInfo) {
        console.error('Global error:', errorInfo);
        
        // Show user-friendly message
        if (window.Toast) {
            Toast.error('An unexpected error occurred. Please try again.');
        }
        
        // Log to monitoring service (if available)
        this.logError(errorInfo);
    }
    
    handleNetworkError(error, url) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            // Network connectivity error
            if (window.Toast) {
                Toast.error('Network connection error. Please check your connection.');
            }
        } else if (error.status >= 500) {
            // Server error
            if (window.Toast) {
                Toast.error('Server error. Please try again later.');
            }
        }
    }
    
    logError(errorInfo) {
        // Send to logging service
        if (navigator.sendBeacon && window.location.origin) {
            const logData = JSON.stringify({
                ...errorInfo,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href
            });
            
            navigator.sendBeacon('/api/logs/error', logData);
        }
    }
}

// Initialize global error handler
ErrorHandler.instance = new ErrorHandler();
```

## Implementation Guidelines

### Frontend Architecture Checklist

- [ ] **Iframe Communication**: Proper postMessage implementation
- [ ] **Error Handling**: Global error boundaries and user feedback
- [ ] **State Management**: Appropriate state management strategy
- [ ] **API Integration**: Centralized API client with retry logic
- [ ] **Design System**: Consistent design token usage
- [ ] **Accessibility**: WCAG compliance and keyboard navigation
- [ ] **Performance**: Lazy loading and optimization
- [ ] **PWA Features**: Service worker and offline support
- [ ] **Security**: CSP headers and input sanitization

### Best Practices

1. **Component Reusability**: Create reusable, composable components
2. **State Management**: Keep state as local as possible
3. **Error Boundaries**: Implement proper error handling at component level
4. **Performance**: Optimize bundle size and loading times
5. **Accessibility**: Ensure keyboard navigation and screen reader support
6. **Testing**: Write unit and integration tests for components
7. **Documentation**: Document component APIs and usage patterns

## Related Documentation

- [API Patterns](./API_PATTERNS.md) - Backend API integration patterns
- [Security Patterns](./SECURITY_PATTERNS.md) - Frontend security patterns
- [Design System](../../06-design/components/) - Component design guidelines
- [PWA Guide](../../../07-cvd-framework/driver-app/) - Progressive Web App implementation

## References

- Micro-Frontend Architecture Patterns
- Cross-Frame Communication Security
- Progressive Web App Best Practices
- Frontend Performance Optimization
- Accessible Web Components