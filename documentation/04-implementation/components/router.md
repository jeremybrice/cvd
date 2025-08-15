# Frontend Router Component


## Metadata
- **ID**: 04_IMPLEMENTATION_COMPONENTS_ROUTER
- **Type**: Implementation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #authentication #code #data-exchange #data-layer #database #debugging #device-management #dex-parser #driver-app #features #implementation #integration #logistics #machine-learning #mobile #operations #optimization #performance #planogram #product-placement #pwa #quality-assurance #route-management #security #service-orders #testing #troubleshooting #vending-machine
- **Intent**: The frontend router (`index
- **Audience**: developers, system administrators, managers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/04-implementation/components/
- **Category**: Components
- **Search Keywords**: ###, ####, attributes, component, content, cooler, data, device, dex, driver, error, focus, frontend, handling, implementation

## Overview

The frontend router (`index.html`) implements a hash-based navigation system using iframes for page content, providing a single-page application experience while maintaining complete separation between the navigation shell and individual pages. The router handles cross-frame communication, authentication integration, and dynamic route management.

## Architecture Overview

### Core Components

#### Navigation Shell Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Meta, styles, and PWA configuration -->
</head>
<body>
    <!-- Skip navigation link for accessibility -->
    <a href="#contentFrame" class="skip-link">Skip to main content</a>
    
    <!-- Top navigation bar -->
    <nav class="navbar" role="navigation" aria-label="Main navigation">
        <div class="nav-content">
            <div class="nav-left">
                <img src="/images/365-logo.png" alt="365 Logo" class="nav-logo">
                <div class="nav-menu">
                    <!-- Dynamic navigation buttons -->
                </div>
            </div>
            <div class="nav-right">
                <!-- User info and controls -->
            </div>
        </div>
    </nav>
    
    <!-- Breadcrumb navigation -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
        <!-- Dynamic breadcrumb trail -->
    </nav>
    
    <!-- Main content area -->
    <main class="content-container">
        <iframe id="contentFrame" src="pages/home-dashboard.html" 
                title="Main application content" 
                aria-label="Application content"></iframe>
        <div class="loading-overlay" id="loadingOverlay">
            <div class="loading-spinner"></div>
        </div>
    </main>
</body>
</html>
```

## Hash-Based Navigation System

### Route Configuration
```javascript
const pageRoutes = {
    '#home': 'pages/home-dashboard.html',
    '#coolers': 'pages/PCP.html',
    '#new-device': 'pages/INVD.html',
    '#planogram': 'pages/NSPT.html',
    '#service-orders': 'pages/service-orders.html',
    '#route-schedule': 'pages/route-schedule.html',
    '#asset-sales': 'pages/asset-sales.html',
    '#product-sales': 'pages/product-sales.html',
    '#database': 'pages/database-viewer.html',
    '#dex-parser': 'pages/dex-parser.html',
    '#company-settings': 'pages/company-settings.html',
    '#user-management': 'pages/user-management.html',
    '#activity-monitor': 'pages/admin/activity-monitor.html',
    '#profile': 'pages/profile.html',
    '#knowledge-base': 'pages/knowledge-base.html',
    '#driver-app': 'pages/driver-app/index.html'
};
```

### Breadcrumb Configuration
```javascript
const breadcrumbRoutes = {
    '#home': ['Home'],
    '#coolers': ['Home', 'Devices', 'Device List'],
    '#new-device': ['Home', 'Devices', 'Add Device'],
    '#planogram': ['Home', 'Devices', 'Planograms'],
    '#service-orders': ['Home', 'Operations', 'Service Orders'],
    '#route-schedule': ['Home', 'Operations', 'Route Schedule'],
    '#asset-sales': ['Home', 'Reports', 'Asset Sales'],
    '#product-sales': ['Home', 'Reports', 'Product Sales'],
    '#database': ['Home', 'Admin', 'Database Viewer'],
    '#dex-parser': ['Home', 'Help', 'DEX Parser'],
    '#company-settings': ['Home', 'Settings', 'Company Settings'],
    '#user-management': ['Home', 'Admin', 'User Management'],
    '#activity-monitor': ['Home', 'Admin', 'Activity Monitor'],
    '#profile': ['Home', 'Account', 'Profile'],
    '#knowledge-base': ['Home', 'Help', 'Knowledge Base'],
    '#driver-app': ['Home', 'Driver App']
};
```

### Navigation Flow

#### Hash Change Detection
```javascript
// Initialize navigation on page load
document.addEventListener('DOMContentLoaded', async function() {
    // Check authentication first
    await checkAuth();
    
    // Set up navigation
    setupNavigation();
    
    // Handle initial route
    const initialHash = window.location.hash || '#home';
    navigateToHash(initialHash);
});

// Handle hash changes
window.addEventListener('hashchange', function() {
    const newHash = window.location.hash || '#home';
    navigateToHash(newHash);
    updateActiveNav();
});
```

#### Page Loading Process
```javascript
function navigateToHash(hash) {
    const page = pageRoutes[hash];
    if (page && page !== currentPage) {
        navigateToPage(page);
        updateBreadcrumbs(hash);
    } else if (hash === '#home' || !hash) {
        updateBreadcrumbs('#home');
    }
}

function navigateToPage(pageUrl) {
    if (isNavigating || pageUrl === currentPage) return;
    
    isNavigating = true;
    showLoading();
    
    const iframe = document.getElementById('contentFrame');
    
    // Set up load handler
    const handleLoad = () => {
        hideLoading();
        currentPage = pageUrl;
        isNavigating = false;
        iframe.removeEventListener('load', handleLoad);
        
        // Post navigation message to iframe
        setTimeout(() => {
            sendMessageToFrame({
                type: 'NAVIGATION_COMPLETE',
                payload: { page: pageUrl }
            });
        }, 100);
    };
    
    iframe.addEventListener('load', handleLoad);
    iframe.src = pageUrl;
    
    // Update active navigation state
    updateActiveNav();
}
```

## Role-Based Route Management

### Dynamic Route Filtering
```javascript
function updatePageRoutesForRole(role) {
    // Remove restricted pages from routes based on role
    if (role !== 'admin') {
        delete pageRoutes['#database'];
        delete pageRoutes['#user-management'];
        delete pageRoutes['#activity-monitor'];
        
        // Hide admin menu items
        const usersMenuItem = document.getElementById('usersMenuItem');
        if (usersMenuItem) usersMenuItem.style.display = 'none';
        
        const activityMonitorMenuItem = document.getElementById('activityMonitorMenuItem');
        if (activityMonitorMenuItem) activityMonitorMenuItem.style.display = 'none';
    } else {
        // Show admin menu items
        const usersMenuItem = document.getElementById('usersMenuItem');
        if (usersMenuItem) usersMenuItem.style.display = '';
        
        const activityMonitorMenuItem = document.getElementById('activityMonitorMenuItem');
        if (activityMonitorMenuItem) activityMonitorMenuItem.style.display = '';
    }
    
    if (!['admin', 'manager'].includes(role)) {
        delete pageRoutes['#dex-parser'];
        delete pageRoutes['#company-settings'];
    }
    
    if (!['admin', 'manager', 'driver'].includes(role)) {
        delete pageRoutes['#service-orders'];
    }
}
```

### Navigation State Management
```javascript
function updateActiveNav() {
    const hash = window.location.hash;
    
    document.querySelectorAll('.nav-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Set active state based on current hash
    const activeButton = document.querySelector(`[data-hash="${hash}"]`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
}
```

## Iframe Management

### Content Frame Setup
```javascript
// Main content iframe configuration
<iframe id="contentFrame" 
        src="pages/home-dashboard.html" 
        title="Main application content" 
        aria-label="Application content"
        sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals">
</iframe>
```

### Iframe Security
- **Sandbox Attributes**: Controlled permissions for iframe content
- **Same-Origin Policy**: Ensures secure cross-frame communication
- **Content Security Policy**: Prevents unauthorized script execution

### Loading State Management
```javascript
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('active');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
    
    // Clear any existing timeout
    if (window.loadingTimeout) {
        clearTimeout(window.loadingTimeout);
    }
}
```

## Cross-Frame Communication

### Message Passing Architecture
```javascript
// Listen for messages from iframes
window.addEventListener('message', function(event) {
    // Verify origin for security
    const allowedOrigin = window.location.origin;
    if (event.origin !== allowedOrigin) {
        console.warn('Rejected message from unauthorized origin:', event.origin);
        return;
    }
    
    const { type, payload } = event.data;
    
    switch (type) {
        case 'NAVIGATE':
            handleNavigate(payload);
            break;
        case 'REFRESH_DATA':
            handleRefreshData(payload);
            break;
        case 'UPDATE_BREADCRUMBS':
            handleUpdateBreadcrumbs(payload);
            break;
        case 'SHOW_LOADING':
            showLoading();
            break;
        case 'HIDE_LOADING':
            hideLoading();
            break;
        case 'UPDATE_USER_INFO':
            handleUpdateUserInfo(payload);
            break;
        case 'LOGOUT':
            logout();
            break;
        default:
            console.log('Unhandled message type:', type);
    }
});
```

### Message Sending to Frames
```javascript
function sendMessageToFrame(message) {
    const iframe = document.getElementById('contentFrame');
    const allowedOrigin = window.location.origin;
    
    if (iframe && iframe.contentWindow) {
        iframe.contentWindow.postMessage(message, allowedOrigin);
    }
}

// Example: Notify iframe of navigation completion
sendMessageToFrame({
    type: 'NAVIGATION_COMPLETE',
    payload: { 
        page: currentPage,
        hash: window.location.hash,
        user: window.currentUser
    }
});
```

### Common Message Types

#### Navigation Messages
```javascript
// Navigate to different page
sendMessageToFrame({
    type: 'NAVIGATE',
    payload: { page: 'device-list' }
});

// Update breadcrumbs dynamically
sendMessageToFrame({
    type: 'UPDATE_BREADCRUMBS',
    payload: { 
        trail: ['Home', 'Devices', 'Edit Device', 'PV-001'] 
    }
});
```

#### Data Refresh Messages
```javascript
// Refresh specific data sections
sendMessageToFrame({
    type: 'REFRESH_DATA',
    payload: { 
        sections: ['devices', 'routes'],
        reason: 'user_action'
    }
});
```

#### UI State Messages
```javascript
// Show/hide loading states
sendMessageToFrame({
    type: 'SHOW_LOADING',
    payload: { message: 'Saving device...' }
});

sendMessageToFrame({
    type: 'HIDE_LOADING'
});
```

## Breadcrumb Navigation

### Dynamic Breadcrumb Updates
```javascript
function updateBreadcrumbs(hash) {
    const breadcrumbList = document.getElementById('breadcrumbList');
    const trail = breadcrumbRoutes[hash] || ['Home'];
    
    // Clear existing breadcrumbs
    breadcrumbList.innerHTML = '';
    
    // Build breadcrumb trail
    trail.forEach((item, index) => {
        const li = document.createElement('li');
        li.className = 'breadcrumb-item';
        
        if (index === trail.length - 1) {
            // Current page (no link)
            li.textContent = item;
        } else {
            // Previous pages (with links)
            const link = document.createElement('a');
            link.href = getBreadcrumbLink(item, index);
            link.className = 'breadcrumb-link';
            link.textContent = item;
            li.appendChild(link);
        }
        
        breadcrumbList.appendChild(li);
    });
}
```

### Contextual Breadcrumb Enhancement
```javascript
// Handle dynamic breadcrumb updates from iframes
function handleUpdateBreadcrumbs(payload) {
    const { trail, context } = payload;
    
    if (trail && Array.isArray(trail)) {
        const breadcrumbList = document.getElementById('breadcrumbList');
        breadcrumbList.innerHTML = '';
        
        trail.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = 'breadcrumb-item';
            
            if (index === trail.length - 1) {
                li.textContent = item;
            } else {
                const link = document.createElement('a');
                link.href = '#';
                link.className = 'breadcrumb-link';
                link.textContent = item;
                
                // Handle breadcrumb navigation
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    handleBreadcrumbNavigation(item, index, context);
                });
                
                li.appendChild(link);
            }
            
            breadcrumbList.appendChild(li);
        });
    }
}
```

## Page Loading and Error Handling

### Loading States
```javascript
// Global loading management
let loadingTimeout;

function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loadingOverlay');
    const spinner = overlay.querySelector('.loading-spinner');
    
    overlay.classList.add('active');
    
    // Add timeout to prevent infinite loading
    loadingTimeout = setTimeout(() => {
        hideLoading();
        showError('Page took too long to load. Please try refreshing.');
    }, 30000); // 30 second timeout
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.remove('active');
    
    if (loadingTimeout) {
        clearTimeout(loadingTimeout);
        loadingTimeout = null;
    }
}
```

### Error Handling
```javascript
// Handle iframe loading errors
iframe.addEventListener('error', (e) => {
    console.error('Failed to load page:', pageUrl);
    hideLoading();
    showError(`Failed to load page: ${pageUrl}`);
    
    // Fallback to home page
    setTimeout(() => {
        window.location.hash = '#home';
    }, 2000);
});

// Network connectivity handling
window.addEventListener('offline', () => {
    showNotification('You are offline. Some features may not be available.', 'warning');
});

window.addEventListener('online', () => {
    showNotification('Connection restored.', 'success');
    
    // Refresh current page
    const currentHash = window.location.hash || '#home';
    navigateToHash(currentHash);
});
```

## Authentication Integration

### Auth Check Integration
```javascript
async function checkAuth() {
    try {
        // Import auth check module
        if (typeof AuthCheck === 'undefined') {
            await import('./auth-check.js');
        }
        
        // Verify authentication
        const isAuthenticated = await AuthCheck.verify();
        
        if (!isAuthenticated) {
            // Redirect to login with return URL
            const returnUrl = encodeURIComponent(window.location.pathname + window.location.hash);
            window.location.href = `/pages/login.html?return=${returnUrl}`;
            return false;
        }
        
        // Set up user context
        await setupUserContext();
        return true;
        
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/pages/login.html';
        return false;
    }
}
```

### User Context Management
```javascript
async function setupUserContext() {
    try {
        const user = await cvdApi.getCurrentUser();
        window.currentUser = user;
        
        // Update UI with user info
        updateUserDisplay(user);
        
        // Configure routes based on user role
        updatePageRoutesForRole(user.role);
        
        // Initialize role-specific features
        initializeRoleFeatures(user.role);
        
    } catch (error) {
        console.error('Failed to setup user context:', error);
        logout();
    }
}

function updateUserDisplay(user) {
    const usernameElement = document.querySelector('.username');
    const roleElement = document.querySelector('.role');
    
    if (usernameElement) usernameElement.textContent = user.username;
    if (roleElement) roleElement.textContent = user.role;
    
    // Update user avatar if system is available
    if (window.UserAvatarSystem) {
        window.UserAvatarSystem.updateNavigationAvatar();
    }
}
```

### Logout Implementation
```javascript
async function logout() {
    if (confirm('Are you sure you want to logout?')) {
        try {
            await cvdApi.logout();
            // cvdApi.logout() handles the redirect
        } catch (error) {
            console.error('Logout error:', error);
            // Force redirect even if API call fails
            window.location.href = '/pages/login.html';
        }
    }
}
```

## Keyboard Navigation and Accessibility

### Keyboard Shortcuts
```javascript
// Global keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Command palette
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        toggleCommandPalette();
        return;
    }
    
    // Alt + number shortcuts for navigation
    if (e.altKey && !e.ctrlKey && !e.metaKey) {
        switch(e.key) {
            case '1':
                e.preventDefault();
                toggleDropdown('routes');
                break;
            case '2':
                e.preventDefault();
                toggleDropdown('operations');
                break;
            case 'h':
                e.preventDefault();
                window.location.hash = '#home';
                break;
            case 'd':
                e.preventDefault();
                window.location.hash = '#coolers';
                break;
            case 'p':
                e.preventDefault();
                window.location.hash = '#planogram';
                break;
        }
    }
    
    // Help shortcut
    if (e.key === '?') {
        e.preventDefault();
        showKeyboardShortcuts();
    }
});
```

### Focus Management
```javascript
// Manage focus for iframe navigation
function handleIframeFocus() {
    const iframe = document.getElementById('contentFrame');
    
    // Set focus to iframe content when navigation completes
    iframe.addEventListener('load', () => {
        // Small delay to ensure content is ready
        setTimeout(() => {
            iframe.contentWindow.focus();
        }, 100);
    });
}

// Skip link implementation
document.querySelector('.skip-link').addEventListener('click', (e) => {
    e.preventDefault();
    const iframe = document.getElementById('contentFrame');
    iframe.focus();
});
```

## Progressive Web App Integration

### Service Worker Communication
```javascript
// Register service worker for PWA functionality
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js')
        .then(registration => {
            console.log('SW registered: ', registration);
            
            // Handle service worker messages
            navigator.serviceWorker.addEventListener('message', handleServiceWorkerMessage);
        })
        .catch(registrationError => {
            console.log('SW registration failed: ', registrationError);
        });
}

function handleServiceWorkerMessage(event) {
    const { type, payload } = event.data;
    
    switch (type) {
        case 'OFFLINE_READY':
            showNotification('App is ready for offline use', 'info');
            break;
        case 'UPDATE_AVAILABLE':
            showUpdatePrompt();
            break;
        case 'SYNC_COMPLETE':
            showNotification('Data synchronized', 'success');
            break;
    }
}
```

## Performance Optimizations

### Iframe Preloading
```javascript
// Preload commonly accessed pages
function preloadPages() {
    const commonPages = ['pages/PCP.html', 'pages/NSPT.html'];
    
    commonPages.forEach(page => {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = page;
        document.head.appendChild(link);
    });
}
```

### Navigation Optimization
```javascript
// Debounce rapid navigation attempts
let navigationDebounce;

function navigateToPage(pageUrl) {
    if (navigationDebounce) {
        clearTimeout(navigationDebounce);
    }
    
    navigationDebounce = setTimeout(() => {
        performNavigation(pageUrl);
    }, 50); // 50ms debounce
}
```

## Testing and Debugging

### Debug Mode
```javascript
// Enable debug mode with URL parameter
const debugMode = new URLSearchParams(window.location.search).has('debug');

if (debugMode) {
    // Log all navigation events
    window.addEventListener('hashchange', (e) => {
        console.log('Navigation:', e.oldURL, '→', e.newURL);
    });
    
    // Log cross-frame messages
    window.addEventListener('message', (event) => {
        console.log('Frame message:', event.data);
    });
}
```

### Navigation Testing
```javascript
// Automated navigation testing
function testNavigation() {
    const routes = Object.keys(pageRoutes);
    let currentIndex = 0;
    
    function testNextRoute() {
        if (currentIndex < routes.length) {
            const route = routes[currentIndex];
            console.log(`Testing route: ${route}`);
            
            window.location.hash = route;
            
            setTimeout(() => {
                currentIndex++;
                testNextRoute();
            }, 1000);
        } else {
            console.log('Navigation testing complete');
        }
    }
    
    testNextRoute();
}
```