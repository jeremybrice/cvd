// iOS PWA Navigation Fix
// This addresses the specific issue where navigation doesn't work in installed PWA on iOS

(function() {
    // Only run on iOS devices in standalone mode
    const isIOSStandalone = ('standalone' in window.navigator) && window.navigator.standalone;
    
    if (!isIOSStandalone) return;
    
    console.log('iOS PWA standalone mode detected - applying navigation fixes');
    
    // Override the switchView function for iOS PWA
    window.addEventListener('load', function() {
        // Store original switchView if it exists
        const originalSwitchView = window.switchView;
        
        // Create iOS-optimized switchView
        window.switchView = function(targetId) {
            console.log('iOS PWA switchView called for:', targetId);
            
            // Get all views and nav items
            const views = document.querySelectorAll('.view');
            const navItems = document.querySelectorAll('.nav-item');
            
            // Update navigation
            navItems.forEach(nav => {
                const navTarget = nav.getAttribute('href');
                if (navTarget === '#' + targetId) {
                    nav.classList.add('active');
                } else {
                    nav.classList.remove('active');
                }
            });
            
            // Hide all views using multiple methods for iOS compatibility
            views.forEach(view => {
                view.style.display = 'none';
                view.style.visibility = 'hidden';
                view.style.position = 'absolute';
                view.style.left = '-9999px';
                view.classList.remove('active');
            });
            
            // Show target view
            const targetView = document.getElementById(targetId);
            if (targetView) {
                // Use multiple methods to ensure visibility
                targetView.style.display = 'block';
                targetView.style.visibility = 'visible';
                targetView.style.position = 'relative';
                targetView.style.left = '0';
                targetView.classList.add('active');
                
                // Force iOS to repaint
                targetView.style.opacity = '0.99';
                setTimeout(() => {
                    targetView.style.opacity = '1';
                }, 10);
                
                // Scroll to top
                window.scrollTo(0, 0);
                
                // Call original function if needed
                if (originalSwitchView && typeof originalSwitchView === 'function') {
                    try {
                        // Load view-specific data
                        switch(targetId) {
                            case 'routes':
                                if (window.loadRoutes) window.loadRoutes();
                                break;
                            case 'orders':
                                if (window.loadOrders) window.loadOrders();
                                break;
                            case 'profile':
                                if (window.updateSettingsUI) window.updateSettingsUI();
                                break;
                        }
                    } catch (e) {
                        console.error('Error calling view functions:', e);
                    }
                }
            }
            
            // Update URL hash
            if (window.location.hash !== '#' + targetId) {
                window.location.hash = targetId;
            }
        };
        
        // Re-attach all navigation listeners
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            // Remove existing listeners by cloning
            const newItem = item.cloneNode(true);
            item.parentNode.replaceChild(newItem, item);
            
            // Add new listener
            newItem.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const target = this.getAttribute('href').substring(1);
                window.switchView(target);
                
                return false;
            });
        });
        
        // Handle initial view if hash is present
        if (window.location.hash) {
            const initialTarget = window.location.hash.substring(1);
            setTimeout(() => {
                window.switchView(initialTarget);
            }, 100);
        }
    });
})();