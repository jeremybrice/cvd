// Fix for standalone PWA mode (installed apps)
(function() {
    // Check if running as installed PWA
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || 
                        window.navigator.standalone || 
                        document.referrer.includes('android-app://');
    
    if (isStandalone) {
        console.log('Running in standalone PWA mode - applying fixes');
        
        // Fix for iOS standalone mode where navigation might not work
        document.addEventListener('DOMContentLoaded', function() {
            // Wait for app initialization
            setTimeout(function() {
                const navItems = document.querySelectorAll('.nav-item');
                
                navItems.forEach(function(item) {
                    // Re-attach event listeners for standalone mode
                    item.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        const targetId = this.getAttribute('href').substring(1);
                        console.log('Standalone nav clicked:', targetId);
                        
                        // Force view switch
                        if (window.switchView) {
                            window.switchView(targetId);
                        } else {
                            // Fallback if switchView not available
                            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
                            this.classList.add('active');
                            
                            document.querySelectorAll('.view').forEach(view => {
                                view.style.display = 'none';
                                view.classList.remove('active');
                            });
                            
                            const targetView = document.getElementById(targetId);
                            if (targetView) {
                                targetView.style.display = 'block';
                                targetView.classList.add('active');
                            }
                        }
                        
                        return false;
                    }, true); // Use capture phase
                });
                
                // Fix for iOS status bar tap to scroll to top
                if (window.navigator.standalone) {
                    window.addEventListener('scroll', function() {
                        window.scrollTo(0, 0);
                    }, { passive: true });
                }
                
                // Handle external links in standalone mode
                document.addEventListener('click', function(e) {
                    const link = e.target.closest('a');
                    if (link && link.href && !link.href.startsWith('#') && 
                        !link.href.includes(window.location.hostname)) {
                        e.preventDefault();
                        window.open(link.href, '_blank');
                    }
                });
            }, 1000);
        });
        
        // Add visual indicator that we're in standalone mode
        document.addEventListener('DOMContentLoaded', function() {
            const indicator = document.createElement('div');
            indicator.style.cssText = `
                position: fixed;
                top: 5px;
                right: 5px;
                background: rgba(0, 109, 254, 0.1);
                color: #006dfe;
                padding: 2px 8px;
                font-size: 10px;
                border-radius: 10px;
                z-index: 9999;
                pointer-events: none;
            `;
            indicator.textContent = 'PWA';
            document.body.appendChild(indicator);
        });
    }
})();