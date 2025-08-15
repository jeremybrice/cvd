/**
 * loading-helper.js
 * Loading state helper for iframe pages
 * Provides skeleton loaders and progress indicators
 */

(function() {
    'use strict';
    
    // Global loading object for iframe pages
    window.Loading = {
        /**
         * Show skeleton loader for an element
         * @param {HTMLElement|string} element - Element or selector
         * @param {Object} options - Loader options
         */
        skeleton: function(element, options = {}) {
            const el = typeof element === 'string' ? document.querySelector(element) : element;
            if (!el) return;
            
            // Store original content
            const originalContent = el.innerHTML;
            el.dataset.originalContent = originalContent;
            
            // Create skeleton based on element type
            const skeletonHTML = createSkeleton(el, options);
            el.innerHTML = skeletonHTML;
            el.classList.add('skeleton-active');
            
            return {
                remove: function() {
                    el.innerHTML = el.dataset.originalContent || originalContent;
                    el.classList.remove('skeleton-active');
                    delete el.dataset.originalContent;
                }
            };
        },
        
        /**
         * Show progress bar
         * @param {string} title - Progress title
         * @param {number} percent - Initial percentage
         */
        progress: function(title, percent = 0) {
            sendLoadingMessage({
                type: 'SHOW_PROGRESS',
                payload: {
                    title: title,
                    percent: percent
                }
            });
            
            return {
                update: function(newPercent, newTitle) {
                    sendLoadingMessage({
                        type: 'UPDATE_PROGRESS',
                        payload: {
                            percent: newPercent,
                            title: newTitle || title
                        }
                    });
                },
                complete: function() {
                    sendLoadingMessage({
                        type: 'HIDE_PROGRESS',
                        payload: {}
                    });
                }
            };
        },
        
        /**
         * Show loading overlay
         * @param {string} message - Loading message
         */
        show: function(message) {
            sendLoadingMessage({
                type: 'SHOW_LOADING',
                payload: {
                    message: message || 'Loading...'
                }
            });
        },
        
        /**
         * Hide loading overlay
         */
        hide: function() {
            sendLoadingMessage({
                type: 'HIDE_LOADING',
                payload: {}
            });
        },
        
        /**
         * Create table skeleton
         * @param {number} rows - Number of rows
         * @param {number} cols - Number of columns
         */
        table: function(container, rows = 5, cols = 4) {
            const el = typeof container === 'string' ? document.querySelector(container) : container;
            if (!el) return;
            
            let html = '<table class="skeleton-table" style="width: 100%;">';
            html += '<thead><tr>';
            for (let i = 0; i < cols; i++) {
                html += '<th><div class="skeleton-line" style="height: 20px; margin: 4px;"></div></th>';
            }
            html += '</tr></thead><tbody>';
            
            for (let r = 0; r < rows; r++) {
                html += '<tr>';
                for (let c = 0; c < cols; c++) {
                    html += '<td><div class="skeleton-line" style="height: 16px; margin: 4px;"></div></td>';
                }
                html += '</tr>';
            }
            html += '</tbody></table>';
            
            const originalContent = el.innerHTML;
            el.innerHTML = html;
            el.classList.add('skeleton-active');
            
            return {
                remove: function() {
                    el.innerHTML = originalContent;
                    el.classList.remove('skeleton-active');
                }
            };
        },
        
        /**
         * Create card skeleton
         * @param {HTMLElement|string} container - Container element
         * @param {number} count - Number of cards
         */
        cards: function(container, count = 3) {
            const el = typeof container === 'string' ? document.querySelector(container) : container;
            if (!el) return;
            
            let html = '<div class="skeleton-cards" style="display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));">';
            
            for (let i = 0; i < count; i++) {
                html += `
                    <div class="skeleton-card" style="border: 1px solid #e1e5e8; border-radius: 8px; padding: 16px;">
                        <div class="skeleton-line" style="height: 24px; width: 60%; margin-bottom: 12px;"></div>
                        <div class="skeleton-line" style="height: 16px; width: 100%; margin-bottom: 8px;"></div>
                        <div class="skeleton-line" style="height: 16px; width: 80%; margin-bottom: 8px;"></div>
                        <div class="skeleton-line" style="height: 16px; width: 90%; margin-bottom: 16px;"></div>
                        <div style="display: flex; gap: 8px;">
                            <div class="skeleton-line" style="height: 32px; width: 80px;"></div>
                            <div class="skeleton-line" style="height: 32px; width: 80px;"></div>
                        </div>
                    </div>
                `;
            }
            
            html += '</div>';
            
            const originalContent = el.innerHTML;
            el.innerHTML = html;
            el.classList.add('skeleton-active');
            
            return {
                remove: function() {
                    el.innerHTML = originalContent;
                    el.classList.remove('skeleton-active');
                }
            };
        }
    };
    
    /**
     * Create skeleton HTML based on element type
     */
    function createSkeleton(element, options) {
        const lines = options.lines || 3;
        const height = options.height || 16;
        
        let html = '<div class="skeleton-container">';
        for (let i = 0; i < lines; i++) {
            const width = options.width || (90 - (i * 10)) + '%';
            html += `<div class="skeleton-line" style="height: ${height}px; width: ${width}; margin: 4px 0;"></div>`;
        }
        html += '</div>';
        
        return html;
    }
    
    /**
     * Send loading message to parent frame
     */
    function sendLoadingMessage(data) {
        const inIframe = window.self !== window.top;
        
        if (inIframe) {
            window.parent.postMessage(data, window.location.origin);
        } else {
            // Handle locally if not in iframe
            if (window.LoadingManager) {
                window.LoadingManager.handle(data);
            }
        }
    }
    
    /**
     * Add skeleton CSS if not already present
     */
    function addSkeletonStyles() {
        if (document.getElementById('skeleton-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'skeleton-styles';
        style.textContent = `
            .skeleton-line {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: skeleton-loading 1.5s ease-in-out infinite;
                border-radius: 4px;
            }
            
            .skeleton-active {
                pointer-events: none;
                user-select: none;
            }
            
            .skeleton-table th,
            .skeleton-table td {
                padding: 8px;
            }
            
            @keyframes skeleton-loading {
                0% {
                    background-position: 200% 0;
                }
                100% {
                    background-position: -200% 0;
                }
            }
            
            .skeleton-container {
                padding: 8px;
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Auto-detect loading states for fetch requests
     */
    function autoDetectLoading() {
        const originalFetch = window.fetch;
        let activeRequests = 0;
        
        window.fetch = function(...args) {
            activeRequests++;
            
            // Show loading for long requests
            const loadingTimeout = setTimeout(() => {
                if (activeRequests > 0) {
                    Loading.show('Loading data...');
                }
            }, 500);
            
            return originalFetch.apply(this, args).finally(() => {
                activeRequests--;
                clearTimeout(loadingTimeout);
                
                if (activeRequests === 0) {
                    Loading.hide();
                }
            });
        };
    }
    
    // Initialize
    function init() {
        addSkeletonStyles();
        
        // Only auto-detect if enabled
        if (!window.disableAutoLoading) {
            autoDetectLoading();
        }
        
        console.log('Loading helper initialized');
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();