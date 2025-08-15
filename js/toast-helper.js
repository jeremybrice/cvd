/**
 * toast-helper.js
 * Toast notification helper for iframe pages
 * Allows iframe content to trigger toast notifications in the parent frame
 */

(function() {
    'use strict';
    
    // Global toast object for iframe pages
    window.Toast = {
        /**
         * Show a success toast
         * @param {string} message - The message to display
         * @param {number} duration - Duration in milliseconds (optional)
         */
        success: function(message, duration) {
            sendToast('success', message, duration);
        },
        
        /**
         * Show an error toast
         * @param {string} message - The message to display
         * @param {number} duration - Duration in milliseconds (optional)
         */
        error: function(message, duration) {
            sendToast('error', message, duration);
        },
        
        /**
         * Show a warning toast
         * @param {string} message - The message to display
         * @param {number} duration - Duration in milliseconds (optional)
         */
        warning: function(message, duration) {
            sendToast('warning', message, duration);
        },
        
        /**
         * Show an info toast
         * @param {string} message - The message to display
         * @param {number} duration - Duration in milliseconds (optional)
         */
        info: function(message, duration) {
            sendToast('info', message, duration);
        },
        
        /**
         * Show a custom toast with progress
         * @param {Object} options - Toast options
         */
        custom: function(options) {
            sendToast('custom', options.message, options.duration, options);
        }
    };
    
    /**
     * Send toast message to parent frame
     */
    function sendToast(type, message, duration, options) {
        // Check if we're in an iframe
        const inIframe = window.self !== window.top;
        
        const toastData = {
            type: 'SHOW_TOAST',
            payload: {
                toastType: type,
                message: message,
                duration: duration,
                options: options || {}
            }
        };
        
        if (inIframe) {
            // Send to parent frame
            window.parent.postMessage(toastData, window.location.origin);
        } else {
            // If not in iframe, trigger local toast if available
            if (window.ToastManager) {
                window.ToastManager.show(type, message, duration, options);
            } else {
                // Fallback to console
                console.log(`[Toast ${type}]:`, message);
            }
        }
    }
    
    // Auto-detect common operations and show toasts
    function autoDetectToasts() {
        // Override fetch to detect successful operations
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            return originalFetch.apply(this, args).then(response => {
                // Auto-detect successful POST/PUT/DELETE operations
                const method = (args[1] && args[1].method) || 'GET';
                const url = args[0];
                
                if (response.ok && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(method.toUpperCase())) {
                    // Parse URL for context
                    if (url.includes('/api/devices') && method === 'POST') {
                        Toast.success('Device created successfully');
                    } else if (url.includes('/api/devices') && method === 'PUT') {
                        Toast.success('Device updated successfully');
                    } else if (url.includes('/api/devices') && method === 'DELETE') {
                        Toast.success('Device deleted successfully');
                    } else if (url.includes('/api/planograms') && method === 'POST') {
                        Toast.success('Planogram saved successfully');
                    } else if (url.includes('/api/service-orders') && method === 'POST') {
                        Toast.success('Service order created successfully');
                    } else if (url.includes('/api/users') && method === 'POST') {
                        Toast.success('User created successfully');
                    } else if (url.includes('/api/users') && method === 'PUT') {
                        Toast.success('User updated successfully');
                    }
                } else if (!response.ok && response.status >= 400) {
                    // Auto-detect errors
                    response.text().then(text => {
                        try {
                            const data = JSON.parse(text);
                            if (data.error || data.message) {
                                Toast.error(data.error || data.message);
                            }
                        } catch (e) {
                            if (response.status === 401) {
                                Toast.error('Authentication required');
                            } else if (response.status === 403) {
                                Toast.error('Permission denied');
                            } else if (response.status === 404) {
                                Toast.warning('Resource not found');
                            } else if (response.status >= 500) {
                                Toast.error('Server error occurred');
                            }
                        }
                    });
                }
                
                return response;
            });
        };
    }
    
    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', autoDetectToasts);
    } else {
        autoDetectToasts();
    }
    
    console.log('Toast helper initialized');
})();