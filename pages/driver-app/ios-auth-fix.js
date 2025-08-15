// iOS PWA Authentication Fix
// iOS handles cookies and sessions differently in PWA mode

(function() {
    // Check if iOS and standalone
    const isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent);
    const isStandalone = window.navigator.standalone === true;
    
    if (!isIOS || !isStandalone) {
        console.log('Not iOS standalone PWA, skipping iOS auth fixes');
        return;
    }
    
    console.log('iOS PWA detected - applying authentication fixes');
    
    // Override the loadOrders function to add debugging
    const originalLoadOrders = window.loadOrders;
    if (originalLoadOrders) {
        window.loadOrders = async function() {
            console.log('iOS: Starting loadOrders...');
            
            try {
                // Log the exact request being made
                const filter = document.getElementById('orderFilter')?.value || 'all';
                let endpoint = '/service-orders';
                if (filter !== 'all') {
                    endpoint += `?status=${filter}`;
                }
                
                console.log('iOS: Requesting endpoint:', endpoint);
                
                // Try to get orders
                const result = await originalLoadOrders.call(this);
                
                // Log what we got
                console.log('iOS: Orders loaded:', window.serviceOrders);
                
                return result;
            } catch (error) {
                console.error('iOS: Error loading orders:', error);
                
                // iOS specific error handling
                if (error.status === 401 || error.message.includes('401')) {
                    console.log('iOS: Auth error detected, attempting re-auth...');
                    
                    // Try to re-authenticate
                    const storedUser = localStorage.getItem('user');
                    if (storedUser) {
                        console.log('iOS: Found stored user, attempting to use stored session');
                        // Force a page reload to re-establish session
                        window.location.reload();
                    } else {
                        console.log('iOS: No stored user, redirecting to login');
                        window.location.href = '/pages/driver-app/ios-login.html';
                    }
                }
                
                throw error;
            }
        };
    }
    
    // iOS specific API handling
    if (window.CVDApi) {
        const originalMakeRequest = CVDApi.prototype.makeRequest;
        CVDApi.prototype.makeRequest = async function(method, endpoint, data) {
            console.log(`iOS API: ${method} ${endpoint}`);
            
            try {
                // Add iOS specific headers
                const options = {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-iOS-PWA': 'true'
                    },
                    credentials: 'include',
                    mode: 'cors'
                };
                
                if (data && method !== 'GET') {
                    options.body = JSON.stringify(data);
                }
                
                const response = await fetch(`${this.baseUrl}/api${endpoint}`, options);
                
                console.log(`iOS API Response: ${response.status}`);
                
                if (!response.ok) {
                    if (response.status === 401) {
                        console.log('iOS: 401 detected in API call');
                        // Try to get text response for debugging
                        const text = await response.text();
                        console.log('iOS: 401 response body:', text);
                    }
                    throw new Error(`HTTP ${response.status}`);
                }
                
                const result = await response.json();
                console.log('iOS API Result:', result);
                
                return result;
                
            } catch (error) {
                console.error('iOS API Error:', error);
                throw error;
            }
        };
    }
    
    // Force refresh auth on app launch
    window.addEventListener('load', async function() {
        console.log('iOS: App loaded, checking auth...');
        
        // Check if we have a stored session
        const authTime = localStorage.getItem('iosAuthTime');
        if (authTime) {
            const authAge = Date.now() - new Date(authTime).getTime();
            console.log('iOS: Last auth was', Math.round(authAge / 1000 / 60), 'minutes ago');
            
            // If auth is older than 30 minutes, force re-auth
            if (authAge > 30 * 60 * 1000) {
                console.log('iOS: Auth expired, clearing...');
                localStorage.removeItem('iosAuthTime');
                localStorage.removeItem('user');
            }
        }
    });
    
    // Store auth time when successful
    const originalCheckAuth = window.checkAuth;
    if (originalCheckAuth) {
        window.checkAuth = async function() {
            try {
                const result = await originalCheckAuth.call(this);
                if (result) {
                    console.log('iOS: Auth successful, storing time');
                    localStorage.setItem('iosAuthTime', new Date().toISOString());
                }
                return result;
            } catch (error) {
                console.error('iOS: checkAuth error:', error);
                throw error;
            }
        };
    }
    
})();