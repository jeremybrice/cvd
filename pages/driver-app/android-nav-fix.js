// Android-specific navigation fix
(function() {
    // Only run on Android
    if (!/Android/i.test(navigator.userAgent)) return;
    
    console.log('Applying Android navigation fixes...');
    
    // Wait for DOM
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            // Get all nav items
            const navItems = document.querySelectorAll('.nav-item');
            
            navItems.forEach(function(item, index) {
                // Remove all existing listeners
                const newItem = item.cloneNode(true);
                item.parentNode.replaceChild(newItem, item);
                
                // Add a simple onclick handler
                newItem.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const targetId = this.getAttribute('href').substring(1);
                    console.log('Android nav clicked:', targetId);
                    
                    // Update active states
                    document.querySelectorAll('.nav-item').forEach(function(nav) {
                        nav.classList.remove('active');
                    });
                    this.classList.add('active');
                    
                    // Hide all views
                    document.querySelectorAll('.view').forEach(function(view) {
                        view.style.display = 'none';
                        view.classList.remove('active');
                    });
                    
                    // Show target view
                    const targetView = document.getElementById(targetId);
                    if (targetView) {
                        targetView.style.display = 'block';
                        targetView.classList.add('active');
                        
                        // Update hash
                        window.location.hash = targetId;
                        
                        // Trigger view-specific updates
                        if (window.switchView) {
                            window.switchView(targetId);
                        }
                    }
                    
                    return false;
                };
            });
            
            console.log('Android navigation fixes applied');
        }, 500); // Delay to ensure main app.js has loaded
    });
})();