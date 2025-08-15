// Monitoring and telemetry for driver app
class AppMonitoring {
    constructor() {
        this.metrics = {
            syncAttempts: 0,
            syncSuccesses: 0,
            syncFailures: 0,
            offlineActions: 0,
            apiErrors: [],
            performanceMarks: []
        };
        
        this.initPerformanceObserver();
        this.initErrorHandling();
    }

    // Initialize performance observer
    initPerformanceObserver() {
        if ('PerformanceObserver' in window) {
            // Observe long tasks
            try {
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.duration > 50) {
                            this.logPerformance('long-task', {
                                duration: entry.duration,
                                startTime: entry.startTime,
                                name: entry.name
                            });
                        }
                    }
                });
                observer.observe({ entryTypes: ['longtask'] });
            } catch (e) {
                console.log('Long task observer not supported');
            }
        }
    }

    // Initialize global error handling
    initErrorHandling() {
        window.addEventListener('error', (event) => {
            this.logError('javascript-error', {
                message: event.message,
                filename: event.filename,
                line: event.lineno,
                column: event.colno,
                stack: event.error?.stack
            });
        });

        window.addEventListener('unhandledrejection', (event) => {
            this.logError('unhandled-promise', {
                reason: event.reason,
                promise: event.promise
            });
        });
    }

    // Log sync attempt
    logSyncAttempt(type = 'manual') {
        this.metrics.syncAttempts++;
        this.logEvent('sync-attempt', { type });
    }

    // Log sync success
    logSyncSuccess(details = {}) {
        this.metrics.syncSuccesses++;
        const duration = details.endTime - details.startTime;
        this.logEvent('sync-success', {
            duration,
            itemsSynced: details.itemsSynced,
            type: details.type
        });
    }

    // Log sync failure
    logSyncFailure(error, details = {}) {
        this.metrics.syncFailures++;
        this.logError('sync-failure', {
            error: error.message || error,
            code: error.code,
            details,
            timestamp: new Date().toISOString()
        });
        
        // Store failure for later analysis
        this.storeFailure({
            type: 'sync',
            error: error.message || error,
            details,
            timestamp: new Date().toISOString()
        });
    }

    // Log offline action
    logOfflineAction(action, data = {}) {
        this.metrics.offlineActions++;
        this.logEvent('offline-action', {
            action,
            data,
            timestamp: new Date().toISOString()
        });
    }

    // Log API error
    logApiError(endpoint, error, details = {}) {
        const errorData = {
            endpoint,
            error: error.message || error,
            status: error.status,
            details,
            timestamp: new Date().toISOString()
        };
        
        this.metrics.apiErrors.push(errorData);
        this.logError('api-error', errorData);
        
        // Keep only last 100 errors
        if (this.metrics.apiErrors.length > 100) {
            this.metrics.apiErrors = this.metrics.apiErrors.slice(-100);
        }
    }

    // Log performance metric
    logPerformance(metric, value) {
        this.metrics.performanceMarks.push({
            metric,
            value,
            timestamp: new Date().toISOString()
        });
        
        // Send to console in development
        if (window.location.hostname === 'localhost') {
            console.log(`Performance: ${metric}`, value);
        }
    }

    // Generic event logging
    logEvent(eventName, data = {}) {
        const event = {
            name: eventName,
            data,
            timestamp: new Date().toISOString(),
            session: this.getSessionId(),
            user: window.currentUser?.id
        };
        
        // In production, send to analytics service
        if (window.location.hostname !== 'localhost') {
            this.sendToAnalytics(event);
        }
        
        // Log to console in development
        console.log(`Event: ${eventName}`, data);
    }

    // Generic error logging
    logError(errorType, errorData) {
        const error = {
            type: errorType,
            data: errorData,
            timestamp: new Date().toISOString(),
            session: this.getSessionId(),
            user: window.currentUser?.id,
            userAgent: navigator.userAgent,
            url: window.location.href
        };
        
        // Store locally for debugging
        this.storeError(error);
        
        // In production, send to error tracking service
        if (window.location.hostname !== 'localhost') {
            this.sendToErrorTracking(error);
        }
        
        // Log to console
        console.error(`Error: ${errorType}`, errorData);
    }

    // Get or create session ID
    getSessionId() {
        let sessionId = sessionStorage.getItem('monitoring-session-id');
        if (!sessionId) {
            sessionId = this.generateId();
            sessionStorage.setItem('monitoring-session-id', sessionId);
        }
        return sessionId;
    }

    // Generate unique ID
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    // Store error locally
    storeError(error) {
        try {
            const errors = JSON.parse(localStorage.getItem('app-errors') || '[]');
            errors.push(error);
            
            // Keep only last 50 errors
            const recentErrors = errors.slice(-50);
            localStorage.setItem('app-errors', JSON.stringify(recentErrors));
        } catch (e) {
            console.error('Failed to store error', e);
        }
    }

    // Store failure for retry
    storeFailure(failure) {
        try {
            const failures = JSON.parse(localStorage.getItem('sync-failures') || '[]');
            failures.push(failure);
            
            // Keep only last 20 failures
            const recentFailures = failures.slice(-20);
            localStorage.setItem('sync-failures', JSON.stringify(recentFailures));
        } catch (e) {
            console.error('Failed to store failure', e);
        }
    }

    // Send to analytics service (placeholder)
    async sendToAnalytics(event) {
        // In production, implement actual analytics endpoint
        try {
            await fetch('/api/analytics/event', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(event)
            });
        } catch (e) {
            // Silently fail - don't interrupt user experience
        }
    }

    // Send to error tracking service (placeholder)
    async sendToErrorTracking(error) {
        // In production, implement actual error tracking endpoint
        try {
            await fetch('/api/errors/track', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(error)
            });
        } catch (e) {
            // Silently fail - don't interrupt user experience
        }
    }

    // Get current metrics
    getMetrics() {
        return {
            ...this.metrics,
            syncSuccessRate: this.metrics.syncAttempts > 0 
                ? (this.metrics.syncSuccesses / this.metrics.syncAttempts * 100).toFixed(2) + '%'
                : 'N/A',
            recentApiErrors: this.metrics.apiErrors.slice(-10),
            sessionId: this.getSessionId()
        };
    }

    // Clear stored errors (for debugging)
    clearErrors() {
        localStorage.removeItem('app-errors');
        localStorage.removeItem('sync-failures');
        this.metrics.apiErrors = [];
    }

    // Export logs for debugging
    exportLogs() {
        const logs = {
            metrics: this.getMetrics(),
            errors: JSON.parse(localStorage.getItem('app-errors') || '[]'),
            failures: JSON.parse(localStorage.getItem('sync-failures') || '[]'),
            exported: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `driver-app-logs-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Create singleton instance
const appMonitoring = new AppMonitoring();

// Expose for debugging
window.appMonitoring = appMonitoring;