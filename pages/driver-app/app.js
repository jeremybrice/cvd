// Initialize API client
const api = new CVDApi();

// App state
let currentUser = null;
let serviceOrders = [];
let routes = [];

// Register service worker
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js')
        .then(registration => {
            console.log('Service Worker registered:', registration.scope);
        })
        .catch(error => {
            console.error('Service Worker registration failed:', error);
        });
}

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    // Detect if running as standalone PWA
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || 
                        window.navigator.standalone || 
                        document.referrer.includes('android-app://');
    
    if (isStandalone) {
        console.log('App running in standalone mode');
    }
    // Initialize offline database
    try {
        await offlineDB.init();
        console.log('Offline database initialized');
    } catch (error) {
        console.error('Failed to initialize offline database:', error);
    }

    // Initialize sync manager
    try {
        await syncManager.init();
        console.log('Sync manager initialized');
    } catch (error) {
        console.error('Failed to initialize sync manager:', error);
    }

    // Initialize secure storage
    try {
        await secureStorage.init();
        console.log('Secure storage initialized');
    } catch (error) {
        console.error('Failed to initialize secure storage:', error);
    }

    // Check authentication
    if (!await checkAuth()) {
        window.location.href = '/pages/login.html?redirect=/pages/driver-app/';
        return;
    }

    // Initialize push notifications
    try {
        await pushManager.init();
        console.log('Push notifications initialized');
    } catch (error) {
        console.error('Failed to initialize push notifications:', error);
    }

    // Initialize location tracking
    try {
        await locationTracker.init();
        console.log('Location tracking initialized');
        
        // Start tracking when driver starts their route
        if (currentUser && currentUser.role === 'driver') {
            // Check if driver has active route
            const hasActiveRoute = await checkActiveRoute();
            if (hasActiveRoute) {
                locationTracker.startTracking();
            }
        }
    } catch (error) {
        console.error('Failed to initialize location tracking:', error);
    }

    // Initialize UI
    initializeNavigation();
    updateDateTime();
    loadDashboardData();
    
    // Handle initial hash navigation
    if (window.location.hash && window.switchView) {
        const hash = window.location.hash.substring(1);
        setTimeout(() => {
            window.switchView(hash);
        }, 100);
    }
    
    // Handle browser back/forward navigation
    window.addEventListener('hashchange', () => {
        if (window.location.hash && window.switchView) {
            const hash = window.location.hash.substring(1);
            window.switchView(hash);
        }
    });

    // Set up offline detection
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    updateOfflineIndicator();

    // Listen for service worker messages
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.addEventListener('message', handleServiceWorkerMessage);
    }

    // Listen for sync events
    window.addEventListener('sync:start', () => updateSyncStatus('syncing'));
    window.addEventListener('sync:success', () => updateSyncStatus('synced'));
    window.addEventListener('sync:error', () => updateSyncStatus('error'));

    // Listen for location events
    window.addEventListener('locationupdate', handleLocationUpdate);
    window.addEventListener('locationerror', handleLocationError);

    // Listen for push notification events
    window.addEventListener('pushstatus', handlePushStatus);

    // Update sync status
    updateSyncStatus();
});

// Authentication check
async function checkAuth() {
    try {
        const response = await api.makeRequest('GET', '/auth/current-user');
        if (response && response.user) {
            currentUser = response.user;
            
            // Check if user is a driver
            if (currentUser.role !== 'driver') {
                alert('This app is for drivers only');
                window.location.href = '/';
                return false;
            }
            
            updateUserInfo();
            return true;
        }
    } catch (error) {
        console.error('Auth check failed:', error);
    }
    return false;
}

// Update user information in UI
function updateUserInfo() {
    if (!currentUser) {
        console.error('No current user data available');
        return;
    }
    
    const driverNameEl = document.getElementById('driverName');
    const profileNameEl = document.getElementById('profileName');
    const profileEmailEl = document.getElementById('profileEmail');
    
    if (driverNameEl) {
        driverNameEl.textContent = currentUser.name || currentUser.username || 'Driver';
    }
    if (profileNameEl) {
        profileNameEl.textContent = currentUser.name || currentUser.username || 'Driver';
    }
    if (profileEmailEl) {
        profileEmailEl.textContent = currentUser.email || 'No email available';
    }
}

// Navigation handling
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');
    
    console.log('Initializing navigation. Found nav items:', navItems.length, 'views:', views.length);

    // Function to switch views
    function switchView(targetId) {
        console.log('Switching to view:', targetId);
        
        // Update nav active states
        navItems.forEach(nav => {
            if (nav.getAttribute('href') === '#' + targetId) {
                nav.classList.add('active');
            } else {
                nav.classList.remove('active');
            }
        });
        
        // Update view visibility
        views.forEach(view => {
            if (view.id === targetId) {
                view.classList.add('active');
                view.style.display = 'block';
                // Force reflow on mobile
                view.offsetHeight;
            } else {
                view.classList.remove('active');
                view.style.display = 'none';
            }
        });
        
        // Update URL hash
        window.location.hash = targetId;
        
        // Load view-specific data
        switch(targetId) {
            case 'routes':
                loadRoutes();
                break;
            case 'orders':
                loadOrders();
                break;
            case 'profile':
                updateSettingsUI();
                break;
        }
    }

    // Add touch and click events with Android compatibility
    navItems.forEach(item => {
        // Function to handle navigation
        const handleNavigation = (e) => {
            e.preventDefault();
            e.stopPropagation();
            const target = item.getAttribute('href').substring(1);
            console.log('Navigation triggered for:', target);
            switchView(target);
        };
        
        // Detect if Android
        const isAndroid = /Android/i.test(navigator.userAgent);
        
        if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
            // For touch devices
            let touchStartY = 0;
            let touchStartX = 0;
            
            item.addEventListener('touchstart', (e) => {
                touchStartY = e.touches[0].clientY;
                touchStartX = e.touches[0].clientX;
            }, { passive: true });
            
            item.addEventListener('touchend', (e) => {
                e.preventDefault();
                
                // Check if it was a tap (not a swipe)
                if (e.changedTouches && e.changedTouches[0]) {
                    const touchEndY = e.changedTouches[0].clientY;
                    const touchEndX = e.changedTouches[0].clientX;
                    const deltaY = Math.abs(touchEndY - touchStartY);
                    const deltaX = Math.abs(touchEndX - touchStartX);
                    
                    if (deltaY < 10 && deltaX < 10) {
                        handleNavigation(e);
                    }
                } else {
                    handleNavigation(e);
                }
            }, { passive: false });
            
            // Add click as fallback for some Android browsers
            if (isAndroid) {
                item.addEventListener('click', handleNavigation);
            }
        } else {
            // For non-touch devices (desktop)
            item.addEventListener('click', handleNavigation);
        }
        
        // Add pointer events as additional fallback
        if ('onpointerdown' in window) {
            item.addEventListener('pointerup', (e) => {
                if (e.pointerType === 'touch' || e.pointerType === 'mouse') {
                    handleNavigation(e);
                }
            });
        }
    });
    
    // Store switchView function globally for hash handling
    window.switchView = switchView;
}

// Dashboard data loading
async function loadDashboardData() {
    try {
        // Get today's service orders
        const today = new Date().toISOString().split('T')[0];
        const response = await api.makeRequest('GET', `/service-orders?date=${today}`);
        
        // Handle both array response and {orders: [...]} format
        if (response) {
            if (Array.isArray(response)) {
                serviceOrders = response;
            } else if (response.orders) {
                serviceOrders = response.orders;
            }
            
            // Save to offline database
            for (const order of serviceOrders) {
                await offlineDB.saveServiceOrder(order);
            }
            
            updateDashboardStats();
            saveToLocalStorage();
        }
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        // Try to load from offline database
        await loadFromOfflineDB();
    }
}

// Load data from offline database
async function loadFromOfflineDB() {
    try {
        serviceOrders = await offlineDB.getAll('serviceOrders');
        routes = await offlineDB.getAll('routes');
        
        if (serviceOrders.length > 0) {
            updateDashboardStats();
        } else {
            // Fallback to localStorage if offline DB is empty
            loadFromLocalStorage();
        }
    } catch (error) {
        console.error('Failed to load from offline DB:', error);
        loadFromLocalStorage();
    }
}

// Update dashboard statistics
function updateDashboardStats() {
    const todayOrders = serviceOrders.length;
    const completedOrders = serviceOrders.filter(o => o.status === 'completed').length;
    const pendingOrders = serviceOrders.filter(o => o.status === 'pending').length;
    
    // Count unique stops
    const uniqueStops = new Set(serviceOrders.map(o => o.deviceId)).size;

    document.getElementById('todayOrders').textContent = todayOrders;
    document.getElementById('completedOrders').textContent = completedOrders;
    document.getElementById('pendingOrders').textContent = pendingOrders;
    document.getElementById('totalStops').textContent = uniqueStops;
}

// Load routes
async function loadRoutes() {
    const routeList = document.getElementById('routeList');
    routeList.innerHTML = '<div class="loading">Loading routes...</div>';

    try {
        const response = await api.makeRequest('GET', '/routes');
        if (response && response.routes) {
            routes = response.routes;
            
            // Save to offline database
            for (const route of routes) {
                await offlineDB.update('routes', route);
            }
            
            renderRoutes();
            saveToLocalStorage();
        }
    } catch (error) {
        console.error('Failed to load routes:', error);
        // Try to load from offline database
        const offlineRoutes = await offlineDB.getAll('routes');
        if (offlineRoutes.length > 0) {
            routes = offlineRoutes;
            renderRoutes();
        } else {
            routeList.innerHTML = '<div class="error">Failed to load routes</div>';
        }
    }
}

// Render routes
function renderRoutes() {
    const routeList = document.getElementById('routeList');
    
    if (routes.length === 0) {
        routeList.innerHTML = '<div class="empty-state">No routes assigned</div>';
        return;
    }

    routeList.innerHTML = routes.map(route => `
        <div class="route-item" onclick="viewRoute(${route.id})">
            <div class="route-header">
                <h3>${route.name}</h3>
                <span class="route-number">#${route.routeNumber}</span>
            </div>
            <div class="route-details">
                <span>${route.deviceCount || 0} devices</span>
                <span>•</span>
                <span>${route.orderCount || 0} orders</span>
            </div>
        </div>
    `).join('');
}

// Load orders
async function loadOrders() {
    const orderList = document.getElementById('orderList');
    orderList.innerHTML = '<div class="loading">Loading orders...</div>';

    try {
        const filter = document.getElementById('orderFilter').value;
        let endpoint = '/service-orders';
        if (filter !== 'all') {
            endpoint += `?status=${filter}`;
        }

        const response = await api.makeRequest('GET', endpoint);
        // Handle both array response and {orders: [...]} format
        if (response) {
            if (Array.isArray(response)) {
                serviceOrders = response;
            } else if (response.orders) {
                serviceOrders = response.orders;
            }
            renderOrders();
        }
    } catch (error) {
        console.error('Failed to load orders:', error);
        orderList.innerHTML = '<div class="error">Failed to load orders</div>';
    }
}

// Render orders
function renderOrders() {
    const orderList = document.getElementById('orderList');
    const filter = document.getElementById('orderFilter').value;
    
    let filteredOrders = serviceOrders;
    if (filter !== 'all') {
        filteredOrders = serviceOrders.filter(o => o.status === filter);
    }

    if (filteredOrders.length === 0) {
        orderList.innerHTML = '<div class="empty-state">No orders found</div>';
        return;
    }

    orderList.innerHTML = filteredOrders.map(order => `
        <div class="order-item" onclick="viewOrder(${order.id})">
            <div class="order-header">
                <span class="order-number">Order #${order.id}</span>
                <span class="order-status status-${order.status}">${order.status}</span>
            </div>
            <div class="order-details">
                <div>📍 ${order.location || 'Unknown Location'}</div>
                <div>🚛 ${order.deviceCount || 0} devices</div>
                <div>📦 ${order.itemCount || 0} items</div>
            </div>
        </div>
    `).join('');
}

// Quick action handlers
async function startRoute() {
    // Start location tracking
    try {
        await locationTracker.requestPermission();
        locationTracker.startTracking();
    } catch (error) {
        console.log('Location permission not granted');
    }
    
    // Navigate to today's first pending order
    const pendingOrders = serviceOrders.filter(o => o.status === 'pending');
    if (pendingOrders.length > 0) {
        viewOrder(pendingOrders[0].id);
    } else {
        alert('No pending orders for today');
    }
}

function viewPendingOrders() {
    document.getElementById('orderFilter').value = 'pending';
    document.querySelector('.nav-item[href="#orders"]').click();
}

// View individual order
function viewOrder(orderId) {
    // Navigate to order detail view
    window.location.href = `/pages/driver-app/order-detail.html?id=${orderId}`;
}

// View route details
function viewRoute(routeId) {
    // TODO: Navigate to route detail view
    console.log('View route:', routeId);
}

// Logout function
async function logout() {
    if (confirm('Are you sure you want to logout?')) {
        try {
            await api.makeRequest('POST', '/auth/logout');
            // Add redirect parameter so login knows to send driver back here
            window.location.href = '/pages/login.html?redirect=/pages/driver-app/';
        } catch (error) {
            console.error('Logout failed:', error);
        }
    }
}

// Update date/time
function updateDateTime() {
    const dateElement = document.getElementById('currentDate');
    const now = new Date();
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    dateElement.textContent = now.toLocaleDateString('en-US', options);
}

// Offline/Online handlers
function handleOffline() {
    updateOfflineIndicator();
    updateSyncStatus();
}

function handleOnline() {
    updateOfflineIndicator();
    updateSyncStatus();
    // Trigger sync when back online
    syncData();
}

function updateOfflineIndicator() {
    const indicator = document.getElementById('offlineIndicator');
    if (navigator.onLine) {
        indicator.classList.remove('show');
    } else {
        indicator.classList.add('show');
    }
}

// Sync functionality
async function syncData() {
    const syncButton = document.getElementById('syncButton');
    const syncStatus = syncButton.querySelector('.sync-status');
    
    syncStatus.textContent = 'Syncing...';
    syncButton.disabled = true;
    
    try {
        // Trigger sync through sync manager
        await syncManager.performSync();
        syncStatus.textContent = 'Synced';
        updateSyncStatus();
    } catch (error) {
        console.error('Sync failed:', error);
        syncStatus.textContent = 'Sync Failed';
    } finally {
        syncButton.disabled = false;
    }
}

function updateSyncStatus(status) {
    const syncButton = document.getElementById('syncButton');
    const syncStatus = syncButton.querySelector('.sync-status');
    
    if (!navigator.onLine) {
        syncStatus.textContent = 'Offline';
    } else if (status === 'syncing') {
        syncStatus.textContent = 'Syncing...';
    } else if (status === 'error') {
        syncStatus.textContent = 'Sync Error';
    } else {
        syncStatus.textContent = 'Synced';
    }
}

// Local storage operations
function saveToLocalStorage() {
    localStorage.setItem('driver_orders', JSON.stringify(serviceOrders));
    localStorage.setItem('driver_routes', JSON.stringify(routes));
    localStorage.setItem('driver_user', JSON.stringify(currentUser));
}

function loadFromLocalStorage() {
    const savedOrders = localStorage.getItem('driver_orders');
    const savedRoutes = localStorage.getItem('driver_routes');
    
    if (savedOrders) {
        serviceOrders = JSON.parse(savedOrders);
        updateDashboardStats();
    }
    
    if (savedRoutes) {
        routes = JSON.parse(savedRoutes);
    }
}

// Add event listener for sync button
document.getElementById('syncButton').addEventListener('click', syncData);

// Handle service worker messages
function handleServiceWorkerMessage(event) {
    const { data } = event;
    
    switch (data.type) {
        case 'SYNC_REQUIRED':
            console.log('Service worker requested sync');
            syncData();
            break;
        default:
            console.log('Unknown message from service worker:', data);
    }
}

// Check if driver has active route
async function checkActiveRoute() {
    // Check if there are any in-progress orders
    const inProgressOrders = serviceOrders.filter(o => o.status === 'in_progress');
    return inProgressOrders.length > 0;
}

// Handle location updates
function handleLocationUpdate(event) {
    const location = event.detail;
    console.log('Location updated:', location);
    
    // Update UI with current location if needed
    // For example, show distance to next stop
}

// Handle location errors
function handleLocationError(event) {
    const error = event.detail.error;
    console.error('Location error:', error);
    
    // Show user-friendly message based on error
    if (error.code === 1) {
        // Permission denied
        console.log('Location permission denied');
    }
}

// Handle push notification status
function handlePushStatus(event) {
    const { status } = event.detail;
    console.log('Push notification status:', status);
    
    // Update UI based on notification status
    updateNotificationUI(status);
}

// Toggle push notifications
async function toggleNotifications() {
    const button = document.getElementById('notificationToggle');
    
    if (button.classList.contains('enabled')) {
        // Disable notifications
        await pushManager.unsubscribe();
        button.classList.remove('enabled');
        button.textContent = 'Enable';
    } else {
        // Enable notifications
        await pushManager.setupPushNotifications();
    }
}

// Toggle location tracking
async function toggleLocation() {
    const button = document.getElementById('locationToggle');
    
    if (button.classList.contains('enabled')) {
        // Stop tracking
        locationTracker.stopTracking();
        button.classList.remove('enabled');
        button.textContent = 'Enable';
        updateLocationStatus('Disabled');
    } else {
        // Start tracking
        try {
            await locationTracker.requestPermission();
            locationTracker.startTracking();
            button.classList.add('enabled');
            button.textContent = 'Disable';
            updateLocationStatus('Active');
        } catch (error) {
            updateLocationStatus('Permission Denied');
        }
    }
}

// Send test notification
function sendTestNotification() {
    pushManager.sendTestNotification();
}

// Update notification UI
function updateNotificationUI(status) {
    const button = document.getElementById('notificationToggle');
    
    if (status === 'enabled') {
        button.classList.add('enabled');
        button.textContent = 'Disable';
    } else {
        button.classList.remove('enabled');
        button.textContent = 'Enable';
    }
}

// Update location status
function updateLocationStatus(status) {
    const locationStatusEl = document.getElementById('locationStatus');
    if (locationStatusEl) {
        locationStatusEl.textContent = `Status: ${status}`;
    }
}

// Check and update settings UI on profile view
function updateSettingsUI() {
    try {
        // Check notification permission
        if ('Notification' in window && Notification.permission === 'granted') {
            updateNotificationUI('enabled');
        }
        
        // Check location status
        if (locationTracker && typeof locationTracker.checkLocationServices === 'function') {
            locationTracker.checkLocationServices().then(state => {
                if (state === 'granted' && locationTracker.tracking) {
                    const button = document.getElementById('locationToggle');
                    if (button) {
                        button.classList.add('enabled');
                        button.textContent = 'Disable';
                    }
                    updateLocationStatus('Active');
                } else {
                    updateLocationStatus(state === 'granted' ? 'Disabled' : 'Permission Required');
                }
            }).catch(error => {
                console.error('Error checking location services:', error);
                updateLocationStatus('Unknown');
            });
        } else {
            console.warn('Location tracker not available');
            updateLocationStatus('Not Available');
        }
    } catch (error) {
        console.error('Error updating settings UI:', error);
    }
}