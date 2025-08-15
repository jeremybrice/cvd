/**
 * CVD Performance Monitor
 * P2 Medium Priority - Foundation Component 2
 * 
 * Tracks and displays performance metrics:
 * - Page load times and navigation performance
 * - API response times and error rates
 * - Memory usage and resource consumption
 * - Visual indicators and performance alerts
 */

class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoads: [],
            apiCalls: [],
            memoryUsage: [],
            navigationTiming: [],
            resourceTiming: []
        };
        
        this.observers = {};
        this.isEnabled = false;
        this.settings = {
            trackPageLoadTimes: true,
            trackApiResponseTimes: true,
            memoryMonitoring: false,
            showIndicators: true,
            enableAlerts: false,
            maxHistorySize: 100,
            alertThresholds: {
                pageLoadTime: 3000,    // 3 seconds
                apiResponseTime: 2000, // 2 seconds
                memoryUsage: 500,      // 500MB
                errorRate: 0.05        // 5%
            }
        };
        
        this.indicators = new Map();
        this.alertCallbacks = [];
        this.startTime = performance.now();
        
        this.init();
    }

    init() {
        // Check if Performance API is available
        if (!window.performance) {
            console.warn('Performance API not available');
            return;
        }

        this.setupPerformanceObservers();
        this.setupAPIInterception();
        this.createIndicatorContainer();
        
        console.log('PerformanceMonitor initialized');
    }

    enable(customSettings = {}) {
        this.settings = { ...this.settings, ...customSettings };
        this.isEnabled = true;
        
        if (this.settings.showIndicators) {
            this.showIndicators();
        }
        
        if (this.settings.memoryMonitoring) {
            this.startMemoryMonitoring();
        }
        
        this.trackInitialPageLoad();
        console.log('Performance monitoring enabled');
    }

    disable() {
        this.isEnabled = false;
        this.hideIndicators();
        this.stopMemoryMonitoring();
        
        // Disconnect observers
        Object.values(this.observers).forEach(observer => {
            if (observer && observer.disconnect) {
                observer.disconnect();
            }
        });
        
        console.log('Performance monitoring disabled');
    }

    setupPerformanceObservers() {
        // Navigation timing observer
        if ('PerformanceObserver' in window) {
            try {
                this.observers.navigation = new PerformanceObserver((list) => {
                    if (this.isEnabled && this.settings.trackPageLoadTimes) {
                        list.getEntries().forEach(entry => {
                            this.handleNavigationEntry(entry);
                        });
                    }
                });
                this.observers.navigation.observe({ entryTypes: ['navigation'] });
            } catch (e) {
                console.log('Navigation observer not supported');
            }

            // Resource timing observer
            try {
                this.observers.resource = new PerformanceObserver((list) => {
                    if (this.isEnabled) {
                        list.getEntries().forEach(entry => {
                            this.handleResourceEntry(entry);
                        });
                    }
                });
                this.observers.resource.observe({ entryTypes: ['resource'] });
            } catch (e) {
                console.log('Resource observer not supported');
            }

            // Measure observer for custom metrics
            try {
                this.observers.measure = new PerformanceObserver((list) => {
                    if (this.isEnabled) {
                        list.getEntries().forEach(entry => {
                            this.handleMeasureEntry(entry);
                        });
                    }
                });
                this.observers.measure.observe({ entryTypes: ['measure'] });
            } catch (e) {
                console.log('Measure observer not supported');
            }
        }
    }

    setupAPIInterception() {
        // Intercept fetch calls to track API performance
        if (window.fetch && !window.fetch._cvdMonitored) {
            const originalFetch = window.fetch;
            
            window.fetch = async (...args) => {
                const startTime = performance.now();
                const url = args[0];
                
                try {
                    const response = await originalFetch(...args);
                    const endTime = performance.now();
                    const duration = endTime - startTime;
                    
                    if (this.isEnabled && this.settings.trackApiResponseTimes) {
                        this.trackAPICall(url, duration, response.status, true);
                    }
                    
                    return response;
                } catch (error) {
                    const endTime = performance.now();
                    const duration = endTime - startTime;
                    
                    if (this.isEnabled && this.settings.trackApiResponseTimes) {
                        this.trackAPICall(url, duration, 0, false, error.message);
                    }
                    
                    throw error;
                }
            };
            
            window.fetch._cvdMonitored = true;
        }

        // Intercept XMLHttpRequest
        if (window.XMLHttpRequest && !window.XMLHttpRequest._cvdMonitored) {
            const originalXHR = window.XMLHttpRequest;
            
            window.XMLHttpRequest = function() {
                const xhr = new originalXHR();
                const startTime = performance.now();
                let url = '';
                
                const originalOpen = xhr.open;
                xhr.open = function(method, requestUrl, ...args) {
                    url = requestUrl;
                    return originalOpen.call(this, method, requestUrl, ...args);
                };
                
                xhr.addEventListener('loadend', () => {
                    const endTime = performance.now();
                    const duration = endTime - startTime;
                    
                    if (window.PerformanceMonitor && window.PerformanceMonitor.isEnabled && 
                        window.PerformanceMonitor.settings.trackApiResponseTimes) {
                        const success = xhr.status >= 200 && xhr.status < 400;
                        window.PerformanceMonitor.trackAPICall(url, duration, xhr.status, success);
                    }
                });
                
                return xhr;
            };
            
            window.XMLHttpRequest._cvdMonitored = true;
        }
    }

    trackInitialPageLoad() {
        // Use navigation timing to get initial page load metrics
        const navigation = performance.getEntriesByType('navigation')[0];
        if (navigation) {
            this.handleNavigationEntry(navigation);
        }
    }

    handleNavigationEntry(entry) {
        const metrics = {
            timestamp: Date.now(),
            url: entry.name || window.location.href,
            type: entry.type || 'navigate',
            loadTime: entry.loadEventEnd - entry.loadEventStart,
            domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
            firstPaint: this.getFirstPaint(),
            firstContentfulPaint: this.getFirstContentfulPaint(),
            timeToInteractive: this.estimateTimeToInteractive(entry),
            transferSize: entry.transferSize || 0,
            encodedBodySize: entry.encodedBodySize || 0
        };

        this.addMetric('pageLoads', metrics);
        this.updateIndicators();
        
        if (this.settings.enableAlerts && metrics.loadTime > this.settings.alertThresholds.pageLoadTime) {
            this.triggerAlert('pageLoad', `Page load time exceeded threshold: ${metrics.loadTime.toFixed(2)}ms`, metrics);
        }
    }

    handleResourceEntry(entry) {
        // Track resource loading performance
        if (entry.name.includes('/api/')) {
            const metrics = {
                timestamp: Date.now(),
                url: entry.name,
                duration: entry.responseEnd - entry.requestStart,
                transferSize: entry.transferSize || 0,
                type: 'api'
            };
            
            this.addMetric('apiCalls', metrics);
        }
    }

    handleMeasureEntry(entry) {
        // Handle custom performance measures
        const metrics = {
            timestamp: Date.now(),
            name: entry.name,
            duration: entry.duration,
            detail: entry.detail || {}
        };
        
        this.addMetric('customMeasures', metrics);
    }

    trackAPICall(url, duration, status, success, errorMessage = null) {
        const metrics = {
            timestamp: Date.now(),
            url: typeof url === 'string' ? url : url.toString(),
            duration,
            status,
            success,
            errorMessage,
            type: 'api'
        };

        this.addMetric('apiCalls', metrics);
        this.updateIndicators();
        
        if (this.settings.enableAlerts && duration > this.settings.alertThresholds.apiResponseTime) {
            this.triggerAlert('apiResponse', `API response time exceeded threshold: ${duration.toFixed(2)}ms`, metrics);
        }
    }

    addMetric(category, metrics) {
        if (!this.metrics[category]) {
            this.metrics[category] = [];
        }
        
        this.metrics[category].push(metrics);
        
        // Maintain history size limit
        if (this.metrics[category].length > this.settings.maxHistorySize) {
            this.metrics[category] = this.metrics[category].slice(-this.settings.maxHistorySize);
        }
    }

    getFirstPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
        return firstPaint ? firstPaint.startTime : null;
    }

    getFirstContentfulPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const fcp = paintEntries.find(entry => entry.name === 'first-contentful-paint');
        return fcp ? fcp.startTime : null;
    }

    estimateTimeToInteractive(navigationEntry) {
        // Simplified TTI estimation based on navigation timing
        const interactive = Math.max(
            navigationEntry.domContentLoadedEventEnd,
            navigationEntry.loadEventEnd
        );
        return interactive;
    }

    startMemoryMonitoring() {
        if ('memory' in performance) {
            this.memoryInterval = setInterval(() => {
                const memory = performance.memory;
                const metrics = {
                    timestamp: Date.now(),
                    used: memory.usedJSHeapSize,
                    total: memory.totalJSHeapSize,
                    limit: memory.jsHeapSizeLimit
                };
                
                this.addMetric('memoryUsage', metrics);
                this.updateIndicators();
                
                // Convert to MB for alert threshold
                const usedMB = metrics.used / (1024 * 1024);
                if (this.settings.enableAlerts && usedMB > this.settings.alertThresholds.memoryUsage) {
                    this.triggerAlert('memory', `Memory usage exceeded threshold: ${usedMB.toFixed(2)}MB`, metrics);
                }
            }, 5000); // Check every 5 seconds
        }
    }

    stopMemoryMonitoring() {
        if (this.memoryInterval) {
            clearInterval(this.memoryInterval);
            this.memoryInterval = null;
        }
    }

    createIndicatorContainer() {
        if (document.getElementById('performance-indicators')) return;
        
        const container = document.createElement('div');
        container.id = 'performance-indicators';
        container.className = 'performance-indicators';
        container.innerHTML = `
            <div class="perf-indicator" id="perf-page-load" title="Average page load time">
                <span class="perf-icon">⏱️</span>
                <span class="perf-value">-</span>
            </div>
            <div class="perf-indicator" id="perf-api-response" title="Average API response time">
                <span class="perf-icon">🌐</span>
                <span class="perf-value">-</span>
            </div>
            <div class="perf-indicator" id="perf-memory" title="Memory usage">
                <span class="perf-icon">🧠</span>
                <span class="perf-value">-</span>
            </div>
            <div class="perf-indicator" id="perf-errors" title="Error rate">
                <span class="perf-icon">⚠️</span>
                <span class="perf-value">-</span>
            </div>
        `;
        
        // Add CSS if not already present
        this.addIndicatorStyles();
        
        document.body.appendChild(container);
        
        // Add click handler to toggle detailed view
        container.addEventListener('click', () => {
            this.showDetailedMetrics();
        });
    }

    addIndicatorStyles() {
        if (document.getElementById('performance-indicator-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'performance-indicator-styles';
        style.textContent = `
            .performance-indicators {
                position: fixed;
                bottom: 20px;
                left: 20px;
                display: flex;
                gap: 8px;
                z-index: var(--z-tooltip);
                opacity: 0.8;
                transition: opacity var(--duration-fast);
                pointer-events: all;
            }
            
            .performance-indicators:hover {
                opacity: 1;
            }
            
            .perf-indicator {
                background: var(--color-neutral-900);
                color: var(--color-neutral-0);
                padding: 4px 8px;
                border-radius: var(--radius-md);
                font-size: var(--text-xs);
                font-family: var(--font-mono);
                display: flex;
                align-items: center;
                gap: 4px;
                cursor: pointer;
                transition: background var(--duration-fast);
                min-width: 60px;
            }
            
            .perf-indicator:hover {
                background: var(--color-neutral-800);
            }
            
            .perf-indicator.good {
                background: var(--color-success);
            }
            
            .perf-indicator.warning {
                background: var(--color-warning);
            }
            
            .perf-indicator.danger {
                background: var(--color-danger);
            }
            
            .perf-icon {
                font-size: 12px;
            }
            
            .perf-value {
                font-weight: var(--font-medium);
                min-width: 40px;
                text-align: right;
            }
            
            @media (max-width: 768px) {
                .performance-indicators {
                    display: none;
                }
            }
        `;
        
        document.head.appendChild(style);
    }

    showIndicators() {
        const container = document.getElementById('performance-indicators');
        if (container) {
            container.style.display = 'flex';
        }
    }

    hideIndicators() {
        const container = document.getElementById('performance-indicators');
        if (container) {
            container.style.display = 'none';
        }
    }

    updateIndicators() {
        if (!this.settings.showIndicators) return;
        
        // Update page load indicator
        const avgPageLoad = this.getAverageMetric('pageLoads', 'loadTime');
        this.updateIndicator('perf-page-load', avgPageLoad, 'ms', 
            avgPageLoad < 1000 ? 'good' : avgPageLoad < 3000 ? 'warning' : 'danger');
        
        // Update API response indicator
        const avgAPIResponse = this.getAverageMetric('apiCalls', 'duration');
        this.updateIndicator('perf-api-response', avgAPIResponse, 'ms',
            avgAPIResponse < 500 ? 'good' : avgAPIResponse < 2000 ? 'warning' : 'danger');
        
        // Update memory indicator
        if (this.settings.memoryMonitoring && this.metrics.memoryUsage.length > 0) {
            const latestMemory = this.metrics.memoryUsage[this.metrics.memoryUsage.length - 1];
            const memoryMB = latestMemory.used / (1024 * 1024);
            this.updateIndicator('perf-memory', memoryMB, 'MB',
                memoryMB < 100 ? 'good' : memoryMB < 300 ? 'warning' : 'danger');
        }
        
        // Update error rate indicator
        const errorRate = this.getErrorRate();
        this.updateIndicator('perf-errors', (errorRate * 100), '%',
            errorRate < 0.01 ? 'good' : errorRate < 0.05 ? 'warning' : 'danger');
    }

    updateIndicator(id, value, unit, status) {
        const indicator = document.getElementById(id);
        if (!indicator) return;
        
        const valueEl = indicator.querySelector('.perf-value');
        if (valueEl) {
            const displayValue = value !== null && value !== undefined ? 
                Math.round(value * 10) / 10 : '-';
            valueEl.textContent = `${displayValue}${unit !== 'ms' && unit !== 'MB' && unit !== '%' ? '' : unit}`;
        }
        
        // Update status class
        indicator.className = `perf-indicator ${status}`;
    }

    getAverageMetric(category, property, timeWindow = 300000) { // 5 minutes
        const metrics = this.metrics[category];
        if (!metrics || metrics.length === 0) return null;
        
        const cutoff = Date.now() - timeWindow;
        const recentMetrics = metrics.filter(m => m.timestamp > cutoff);
        
        if (recentMetrics.length === 0) return null;
        
        const sum = recentMetrics.reduce((acc, metric) => {
            const value = typeof metric[property] === 'number' ? metric[property] : 0;
            return acc + value;
        }, 0);
        
        return sum / recentMetrics.length;
    }

    getErrorRate(timeWindow = 300000) { // 5 minutes
        const apiCalls = this.metrics.apiCalls;
        if (!apiCalls || apiCalls.length === 0) return 0;
        
        const cutoff = Date.now() - timeWindow;
        const recentCalls = apiCalls.filter(call => call.timestamp > cutoff);
        
        if (recentCalls.length === 0) return 0;
        
        const errors = recentCalls.filter(call => !call.success).length;
        return errors / recentCalls.length;
    }

    triggerAlert(type, message, metrics) {
        console.warn(`Performance Alert [${type}]:`, message, metrics);
        
        // Call registered alert callbacks
        this.alertCallbacks.forEach(callback => {
            try {
                callback(type, message, metrics);
            } catch (error) {
                console.error('Error in performance alert callback:', error);
            }
        });
        
        // Show toast notification if available
        if (window.ToastManager) {
            window.ToastManager.show('warning', `Performance: ${message}`, 8000);
        }
    }

    onAlert(callback) {
        this.alertCallbacks.push(callback);
        
        // Return unsubscribe function
        return () => {
            const index = this.alertCallbacks.indexOf(callback);
            if (index > -1) {
                this.alertCallbacks.splice(index, 1);
            }
        };
    }

    showDetailedMetrics() {
        const modal = this.createMetricsModal();
        document.body.appendChild(modal);
        
        // Show modal with animation
        requestAnimationFrame(() => {
            modal.classList.add('active');
        });
    }

    createMetricsModal() {
        const modal = document.createElement('div');
        modal.className = 'performance-modal';
        modal.innerHTML = `
            <div class="performance-modal-backdrop"></div>
            <div class="performance-modal-content">
                <div class="performance-modal-header">
                    <h3>Performance Metrics</h3>
                    <button class="performance-modal-close">×</button>
                </div>
                <div class="performance-modal-body">
                    ${this.generateMetricsHTML()}
                </div>
                <div class="performance-modal-footer">
                    <button class="btn btn-secondary" data-action="export">Export Data</button>
                    <button class="btn btn-secondary" data-action="clear">Clear History</button>
                    <button class="btn btn-primary" data-action="close">Close</button>
                </div>
            </div>
        `;
        
        this.addModalStyles();
        this.attachModalEventListeners(modal);
        
        return modal;
    }

    generateMetricsHTML() {
        const sections = [
            {
                title: 'Page Performance',
                data: this.metrics.pageLoads,
                format: (item) => `
                    <div class="metric-item">
                        <div class="metric-time">${new Date(item.timestamp).toLocaleTimeString()}</div>
                        <div class="metric-url">${this.truncateURL(item.url)}</div>
                        <div class="metric-value">${Math.round(item.loadTime)}ms</div>
                    </div>
                `
            },
            {
                title: 'API Performance',
                data: this.metrics.apiCalls,
                format: (item) => `
                    <div class="metric-item ${item.success ? '' : 'error'}">
                        <div class="metric-time">${new Date(item.timestamp).toLocaleTimeString()}</div>
                        <div class="metric-url">${this.truncateURL(item.url)}</div>
                        <div class="metric-value">${Math.round(item.duration)}ms</div>
                        <div class="metric-status">${item.status}</div>
                    </div>
                `
            }
        ];

        if (this.settings.memoryMonitoring && this.metrics.memoryUsage.length > 0) {
            sections.push({
                title: 'Memory Usage',
                data: this.metrics.memoryUsage.slice(-20), // Last 20 entries
                format: (item) => `
                    <div class="metric-item">
                        <div class="metric-time">${new Date(item.timestamp).toLocaleTimeString()}</div>
                        <div class="metric-value">${Math.round(item.used / 1024 / 1024)}MB</div>
                    </div>
                `
            });
        }

        return sections.map(section => `
            <div class="metrics-section">
                <h4>${section.title}</h4>
                <div class="metrics-list">
                    ${section.data.slice(-10).reverse().map(section.format).join('')}
                </div>
            </div>
        `).join('');
    }

    truncateURL(url, maxLength = 50) {
        if (url.length <= maxLength) return url;
        return url.substring(0, maxLength - 3) + '...';
    }

    addModalStyles() {
        if (document.getElementById('performance-modal-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'performance-modal-styles';
        style.textContent = `
            .performance-modal {
                position: fixed;
                inset: 0;
                z-index: var(--z-modal);
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                visibility: hidden;
                transition: opacity var(--duration-base), visibility var(--duration-base);
            }
            
            .performance-modal.active {
                opacity: 1;
                visibility: visible;
            }
            
            .performance-modal-backdrop {
                position: absolute;
                inset: 0;
                background: rgba(0, 0, 0, 0.5);
                cursor: pointer;
            }
            
            .performance-modal-content {
                background: var(--color-neutral-0);
                border-radius: var(--modal-radius);
                box-shadow: var(--modal-shadow);
                width: 90vw;
                max-width: 800px;
                max-height: 80vh;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                position: relative;
                z-index: 1;
            }
            
            .performance-modal-header {
                padding: var(--space-lg);
                border-bottom: 1px solid var(--color-neutral-200);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .performance-modal-header h3 {
                margin: 0;
                font-size: var(--text-lg);
                font-weight: var(--font-semibold);
            }
            
            .performance-modal-close {
                background: none;
                border: none;
                font-size: var(--text-xl);
                cursor: pointer;
                padding: 0;
                width: 32px;
                height: 32px;
                border-radius: var(--radius-md);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background var(--duration-fast);
            }
            
            .performance-modal-close:hover {
                background: var(--color-neutral-100);
            }
            
            .performance-modal-body {
                padding: var(--space-lg);
                overflow-y: auto;
                flex: 1;
            }
            
            .performance-modal-footer {
                padding: var(--space-lg);
                border-top: 1px solid var(--color-neutral-200);
                display: flex;
                gap: var(--space-sm);
                justify-content: flex-end;
            }
            
            .metrics-section {
                margin-bottom: var(--space-xl);
            }
            
            .metrics-section h4 {
                margin: 0 0 var(--space-md) 0;
                font-size: var(--text-base);
                font-weight: var(--font-semibold);
                color: var(--color-neutral-800);
            }
            
            .metrics-list {
                border: 1px solid var(--color-neutral-200);
                border-radius: var(--radius-md);
                overflow: hidden;
            }
            
            .metric-item {
                display: grid;
                grid-template-columns: 100px 1fr 80px auto;
                gap: var(--space-sm);
                padding: var(--space-sm) var(--space-md);
                border-bottom: 1px solid var(--color-neutral-100);
                font-size: var(--text-sm);
                align-items: center;
            }
            
            .metric-item:last-child {
                border-bottom: none;
            }
            
            .metric-item.error {
                background: var(--color-danger-bg);
            }
            
            .metric-time {
                font-family: var(--font-mono);
                color: var(--color-neutral-600);
            }
            
            .metric-url {
                color: var(--color-neutral-800);
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            
            .metric-value {
                font-family: var(--font-mono);
                font-weight: var(--font-semibold);
                text-align: right;
            }
            
            .metric-status {
                font-family: var(--font-mono);
                font-size: var(--text-xs);
                color: var(--color-neutral-600);
            }
            
            .btn {
                padding: var(--btn-padding-y) var(--btn-padding-x);
                border-radius: var(--btn-radius);
                border: 1px solid;
                cursor: pointer;
                font-weight: var(--btn-font-weight);
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                transition: all var(--duration-fast);
            }
            
            .btn-primary {
                background: var(--color-primary-500);
                border-color: var(--color-primary-500);
                color: var(--color-neutral-0);
            }
            
            .btn-primary:hover {
                background: var(--color-primary-600);
                border-color: var(--color-primary-600);
            }
            
            .btn-secondary {
                background: var(--color-neutral-0);
                border-color: var(--color-neutral-300);
                color: var(--color-neutral-700);
            }
            
            .btn-secondary:hover {
                background: var(--color-neutral-50);
                border-color: var(--color-neutral-400);
            }
        `;
        
        document.head.appendChild(style);
    }

    attachModalEventListeners(modal) {
        // Close modal handlers
        const closeModal = () => {
            modal.classList.remove('active');
            setTimeout(() => modal.remove(), 300);
        };
        
        modal.querySelector('.performance-modal-backdrop').addEventListener('click', closeModal);
        modal.querySelector('.performance-modal-close').addEventListener('click', closeModal);
        
        // Footer action handlers
        modal.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            if (!action) return;
            
            switch (action) {
                case 'export':
                    this.exportMetrics();
                    break;
                case 'clear':
                    if (confirm('Clear all performance history?')) {
                        this.clearMetrics();
                        closeModal();
                    }
                    break;
                case 'close':
                    closeModal();
                    break;
            }
        });
        
        // Keyboard support
        document.addEventListener('keydown', function escapeHandler(e) {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', escapeHandler);
            }
        });
    }

    exportMetrics() {
        const exportData = {
            timestamp: new Date().toISOString(),
            settings: this.settings,
            metrics: this.metrics,
            summary: {
                avgPageLoad: this.getAverageMetric('pageLoads', 'loadTime'),
                avgAPIResponse: this.getAverageMetric('apiCalls', 'duration'),
                errorRate: this.getErrorRate(),
                totalPageLoads: this.metrics.pageLoads.length,
                totalAPICalls: this.metrics.apiCalls.length
            }
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cvd-performance-metrics-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        if (window.ToastManager) {
            window.ToastManager.show('success', 'Performance data exported');
        }
    }

    clearMetrics() {
        this.metrics = {
            pageLoads: [],
            apiCalls: [],
            memoryUsage: [],
            navigationTiming: [],
            resourceTiming: []
        };
        
        this.updateIndicators();
        
        if (window.ToastManager) {
            window.ToastManager.show('info', 'Performance history cleared');
        }
    }

    // Custom performance marking methods
    mark(name) {
        if (this.isEnabled && performance.mark) {
            performance.mark(name);
        }
    }

    measure(name, startMark, endMark = null) {
        if (this.isEnabled && performance.measure) {
            try {
                if (endMark) {
                    performance.measure(name, startMark, endMark);
                } else {
                    performance.measure(name, startMark);
                }
            } catch (error) {
                console.warn('Performance measure failed:', error);
            }
        }
    }

    // Utility methods for iframe pages
    trackPageLoad(pageName) {
        this.mark(`${pageName}-start`);
        
        return () => {
            this.mark(`${pageName}-end`);
            this.measure(`${pageName}-load`, `${pageName}-start`, `${pageName}-end`);
        };
    }

    trackAction(actionName) {
        this.mark(`${actionName}-start`);
        
        return () => {
            this.mark(`${actionName}-end`);
            this.measure(`${actionName}-duration`, `${actionName}-start`, `${actionName}-end`);
        };
    }

    // Get current performance snapshot
    getSnapshot() {
        return {
            timestamp: Date.now(),
            metrics: {
                avgPageLoad: this.getAverageMetric('pageLoads', 'loadTime'),
                avgAPIResponse: this.getAverageMetric('apiCalls', 'duration'),
                errorRate: this.getErrorRate(),
                memoryUsage: this.settings.memoryMonitoring && this.metrics.memoryUsage.length > 0 ?
                    this.metrics.memoryUsage[this.metrics.memoryUsage.length - 1] : null
            },
            counts: {
                pageLoads: this.metrics.pageLoads.length,
                apiCalls: this.metrics.apiCalls.length,
                errors: this.metrics.apiCalls.filter(call => !call.success).length
            }
        };
    }
}

// Initialize global instance
window.PerformanceMonitor = new PerformanceMonitor();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceMonitor;
}