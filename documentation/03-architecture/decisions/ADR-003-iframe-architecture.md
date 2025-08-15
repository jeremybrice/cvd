# ADR-003: Iframe-Based Frontend Architecture


## Metadata
- **ID**: 03_ARCHITECTURE_DECISIONS_ADR_003_IFRAME_ARCHITECTURE
- **Type**: Architecture
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #architecture #authentication #data-exchange #debugging #deployment #device-management #devops #dex-parser #driver-app #integration #logistics #machine-learning #metrics #mobile #optimization #performance #planogram #product-placement #pwa #quality-assurance #reporting #route-management #security #system-design #technical #testing #troubleshooting #vending-machine
- **Intent**: Architecture for ADR-003: Iframe-Based Frontend Architecture
- **Audience**: developers, system administrators, managers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/03-architecture/decisions/
- **Category**: Decisions
- **Search Keywords**: ###, (mpa), (spa), 2024-07-15, accepted, adr, advantages, analytics, api, application, approach, architecture, authentication, based, benefits

**Status**: Accepted  
**Date**: 2024-07-15  
**Deciders**: Development Team  
**Technical Story**: Frontend architecture pattern for modular page loading and navigation

## Context

The CVD system requires a frontend architecture that supports:

- **Modular Development**: Independent development of features by different team members
- **No Build Dependencies**: Immediate deployment without compilation steps
- **Progressive Loading**: Pages loaded on-demand to reduce initial bundle size
- **Shared Navigation**: Consistent navigation shell across all pages
- **Cross-Page Communication**: Data sharing and state synchronization between modules
- **Authentication Integration**: Unified session management across modules
- **Legacy Browser Support**: IE11+ compatibility for enterprise environments

Frontend architecture options considered:

1. **Iframe-based Architecture** - Each page loads in iframe with shared shell
2. **Single Page Application (SPA)** - React/Vue/Angular with client-side routing
3. **Multi-Page Application (MPA)** - Traditional server-rendered pages
4. **Module Federation** - Webpack 5 micro-frontend architecture

## Decision

We have chosen an **iframe-based architecture** with a central navigation shell (`index.html`) and modular pages loaded via iframe routing.

## Rationale

### Iframe Architecture Benefits

1. **Zero Build Dependencies**
   ```html
   <!-- Direct HTML/CSS/JS - no compilation required -->
   <script src="/api.js"></script>
   <link rel="stylesheet" href="/css/design-system.css">
   ```

2. **True Module Isolation**
   ```javascript
   // Each page runs in isolated context
   // No CSS bleeding or JavaScript conflicts
   // Independent error boundaries per module
   ```

3. **Progressive Loading**
   ```javascript
   const pageRoutes = {
       'home': 'pages/home-dashboard.html',
       'coolers': 'pages/PCP.html',
       'planogram': 'pages/NSPT.html'
   };
   
   // Pages loaded only when accessed
   function loadPage(pageKey) {
       const iframe = document.getElementById('pageFrame');
       iframe.src = pageRoutes[pageKey];
   }
   ```

4. **Parallel Development**
   - Teams can work independently on separate pages
   - No merge conflicts in shared components
   - Individual page testing and deployment

### Comparison with Alternatives

#### Single Page Application (SPA)
**Advantages**:
- Better user experience with client-side routing
- Shared state management
- Modern development patterns

**Disadvantages**:
- Requires build toolchain (Webpack, Vite, etc.)
- Complex bundle management and code splitting
- Framework lock-in (React/Vue/Angular)
- Longer initial development setup
- Team needs framework expertise

#### Multi-Page Application (MPA)
**Advantages**:
- Simple architecture
- SEO-friendly
- Independent pages

**Disadvantages**:
- Full page refreshes impact UX
- Shared state management difficult
- Authentication state lost between pages
- No progressive loading benefits

#### Module Federation
**Advantages**:
- True micro-frontend architecture
- Independent deployments
- Framework agnostic

**Disadvantages**:
- Complex Webpack 5 configuration
- Network overhead for module loading
- Browser compatibility concerns
- Immature ecosystem

## Implementation Details

### Navigation Shell (index.html)
```javascript
class NavigationShell {
    constructor() {
        this.currentPage = null;
        this.user = null;
        this.setupRouting();
        this.setupCrossFrameMessaging();
    }
    
    setupRouting() {
        // Hash-based routing for page navigation
        window.addEventListener('hashchange', () => {
            const page = window.location.hash.substring(1) || 'home';
            this.loadPage(page);
        });
    }
    
    loadPage(pageKey) {
        if (pageRoutes[pageKey]) {
            const iframe = document.getElementById('pageFrame');
            iframe.src = pageRoutes[pageKey];
            this.currentPage = pageKey;
            this.updateNavigation();
        }
    }
}
```

### Cross-Frame Communication
```javascript
// Parent to child communication
window.addEventListener('message', (event) => {
    if (event.origin !== window.location.origin) return;
    
    const { type, payload } = event.data;
    
    switch (type) {
        case 'NAVIGATE':
            window.location.hash = payload.page;
            break;
        case 'REFRESH_DATA':
            this.refreshUserData();
            break;
        case 'SHOW_TOAST':
            this.showToast(payload.message, payload.type);
            break;
    }
});

// Child to parent communication (from within iframe)
function navigateToPage(page) {
    window.parent.postMessage({
        type: 'NAVIGATE',
        payload: { page: page }
    }, window.location.origin);
}
```

### Shared API Client
```javascript
// api.js loaded in each iframe for consistent backend communication
class CVDApi {
    constructor() {
        this.baseUrl = '/api';
        this.setupAuthInterceptor();
    }
    
    setupAuthInterceptor() {
        // Global 401 handling across all pages
        const originalFetch = window.fetch;
        window.fetch = async function(...args) {
            const response = await originalFetch(...args);
            if (response.status === 401) {
                window.parent.postMessage({
                    type: 'AUTH_EXPIRED'
                }, window.location.origin);
            }
            return response;
        };
    }
}
```

### Authentication Integration
```javascript
// auth-check.js - shared authentication verification
class AuthCheck {
    static async verify() {
        try {
            const response = await fetch('/api/auth/current-user');
            if (response.status === 401) {
                const currentPath = window.location.pathname + window.location.hash;
                window.location.href = `/pages/login.html?return=${encodeURIComponent(currentPath)}`;
                return null;
            }
            return await response.json();
        } catch (error) {
            console.error('Auth check failed:', error);
            return null;
        }
    }
}
```

### Page Structure Pattern
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Device Management - CVD</title>
    <link rel="stylesheet" href="/css/design-system.css">
</head>
<body>
    <div class="page-container">
        <header class="page-header">
            <h1>Device Management</h1>
        </header>
        <main class="page-content">
            <!-- Page-specific content -->
        </main>
    </div>
    
    <!-- Shared dependencies -->
    <script src="/api.js"></script>
    <script src="/auth-check.js"></script>
    
    <!-- Page-specific script -->
    <script>
        document.addEventListener('DOMContentLoaded', async () => {
            const user = await AuthCheck.verify();
            if (user) {
                initializePage();
            }
        });
    </script>
</body>
</html>
```

## Consequences

### Positive

1. **Development Velocity**
   - No build process delays
   - Independent feature development
   - Immediate code changes visible
   - Simple debugging with browser dev tools

2. **Deployment Simplicity**
   ```bash
   # Deploy new feature
   cp new-feature.html /var/www/cvd/pages/
   # Feature immediately available
   ```

3. **Module Isolation**
   - CSS conflicts impossible
   - JavaScript errors contained to single page
   - Memory leaks isolated per page
   - Independent performance optimization

4. **Browser Compatibility**
   - Works in all browsers supporting iframes (IE8+)
   - No modern JavaScript features required
   - Progressive enhancement possible

5. **Security Benefits**
   - Cross-site scripting (XSS) attacks contained to single page
   - Content Security Policy easily implemented
   - Script injection isolated

### Negative

1. **User Experience Limitations**
   ```javascript
   // Browser back button doesn't work within pages
   // URL doesn't reflect page state
   // No smooth transitions between pages
   ```

2. **Memory Usage**
   - Each iframe creates separate browsing context
   - Multiple JavaScript engines running
   - Higher memory footprint than SPA

3. **Mobile Performance**
   - iOS Safari iframe rendering issues
   - Android WebView memory constraints
   - Touch event handling complexity

4. **SEO Limitations**
   - Content not indexable by search engines
   - Social media sharing shows shell page
   - Analytics tracking requires custom implementation

### Mitigation Strategies

1. **Mobile PWA Support**
   ```javascript
   // Driver PWA bypasses iframe architecture for mobile-first experience
   // Standalone mobile app with dedicated navigation
   ```

2. **Performance Optimization**
   ```javascript
   // Preload critical pages
   const criticalPages = ['home', 'coolers', 'service-orders'];
   criticalPages.forEach(page => {
       const link = document.createElement('link');
       link.rel = 'prefetch';
       link.href = pageRoutes[page];
       document.head.appendChild(link);
   });
   ```

3. **Enhanced Navigation**
   ```javascript
   // Custom history management
   class HistoryManager {
       pushState(page, data) {
           history.pushState({ page, data }, '', `#${page}`);
       }
       
       onPopState(event) {
           if (event.state && event.state.page) {
               this.loadPage(event.state.page);
           }
       }
   }
   ```

4. **Analytics Integration**
   ```javascript
   // Cross-frame analytics tracking
   function trackPageView(page, user) {
       window.parent.postMessage({
           type: 'ANALYTICS_PAGE_VIEW',
           payload: { page, user, timestamp: Date.now() }
       }, window.location.origin);
   }
   ```

## Performance Characteristics

### Load Times (Development Environment)
```
Initial Shell Load: ~200ms
Page Load (Cached): ~50ms
Page Load (Uncached): ~300ms
Cross-Frame Message: <1ms
Memory Usage: ~15MB per active page
```

### Browser Compatibility
- **Chrome/Edge**: Excellent
- **Firefox**: Excellent  
- **Safari**: Good (with iOS-specific handling)
- **IE11**: Functional (legacy support)

## Future Evolution Path

### Potential Migration Strategies

1. **Hybrid Approach**
   ```javascript
   // Keep iframe architecture for admin pages
   // Use SPA for driver mobile experience
   // Best of both worlds
   ```

2. **Module Federation Migration**
   ```javascript
   // When team grows and needs independent deployments
   // Convert pages to federated modules
   // Maintain iframe fallback for compatibility
   ```

3. **Web Components Approach**
   ```html
   <!-- Future: Replace iframes with web components -->
   <cvd-page-devices route="coolers"></cvd-page-devices>
   <cvd-page-planogram route="planogram"></cvd-page-planogram>
   ```

## Success Metrics

### Development Metrics
- Time to implement new page: < 4 hours
- Build/deploy time: 0 (immediate)
- Developer onboarding time: < 1 day

### Performance Metrics
- Page load time: < 500ms
- Memory usage per page: < 20MB
- Cross-frame communication latency: < 10ms

### User Experience Metrics
- Navigation responsiveness: < 100ms
- Error isolation: 100% (errors don't cascade)
- Feature independence: 100% (features work independently)

This architecture provides the ideal balance of development simplicity, deployment flexibility, and operational reliability for the CVD system's current requirements while maintaining clear evolution paths for future needs.