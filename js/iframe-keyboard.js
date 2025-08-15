/**
 * iframe-keyboard.js
 * Keyboard navigation helper for iframe pages
 * Enables keyboard shortcuts to work from within iframe content
 */

(function() {
    'use strict';
    
    // Only initialize if we're in an iframe
    if (window.self === window.top) {
        return;
    }
    
    /**
     * Send keyboard event to parent frame
     */
    function forwardKeyboardEvent(event) {
        // Check for keyboard shortcuts
        const isModifier = event.ctrlKey || event.metaKey || event.altKey;
        
        if (!isModifier) {
            return; // Only forward modified key combinations
        }
        
        // Forward to parent
        window.parent.postMessage({
            type: 'KEYBOARD_EVENT',
            payload: {
                key: event.key,
                code: event.code,
                ctrlKey: event.ctrlKey,
                metaKey: event.metaKey,
                altKey: event.altKey,
                shiftKey: event.shiftKey
            }
        }, window.location.origin);
        
        // Check if this is a navigation shortcut (Alt+1-9 or Cmd/Ctrl+K)
        if (event.altKey && event.key >= '1' && event.key <= '9') {
            event.preventDefault();
            event.stopPropagation();
        } else if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
            event.preventDefault();
            event.stopPropagation();
        }
    }
    
    /**
     * Initialize keyboard forwarding
     */
    function init() {
        // Listen for keydown events
        document.addEventListener('keydown', forwardKeyboardEvent, true);
        
        // Also listen for command palette trigger from parent
        window.addEventListener('message', function(event) {
            if (event.origin !== window.location.origin) {
                return;
            }
            
            if (event.data.type === 'FOCUS_SEARCH') {
                // Focus the first search input if available
                const searchInput = document.querySelector('input[type="search"], input[type="text"][placeholder*="search" i], input[placeholder*="filter" i]');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }
        });
        
        console.log('Iframe keyboard navigation helper initialized');
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();