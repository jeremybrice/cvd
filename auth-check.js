// Shared authentication check for non-driver pages
// This script prevents drivers from accessing desktop pages

async function checkNonDriverAccess() {
    try {
        const response = await fetch('/api/auth/current-user', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            // Not authenticated, redirect to login
            window.location.href = '/pages/login.html?return=' + encodeURIComponent(window.location.pathname);
            return false;
        }
        
        const data = await response.json();
        
        // Check if user is a driver
        if (data.user.role === 'driver') {
            // Redirect drivers to driver app
            window.location.href = '/pages/driver-app/';
            return false;
        }
        
        // Non-driver user can proceed
        window.currentUser = data.user;
        return true;
        
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/pages/login.html';
        return false;
    }
}

// Auto-execute on load for pages that include this script
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkNonDriverAccess);
} else {
    checkNonDriverAccess();
}