/**
 * CVD Notification Badge System
 * P2 Medium Priority - Communication Component
 * 
 * Real-time badge indicators for:
 * - Service orders (pending, overdue, completed)
 * - System alerts (errors, warnings, maintenance)
 * - Messages and communications
 * - Device status changes
 * - Performance alerts
 */

class NotificationBadgeSystem {
    constructor() {
        this.badges = new Map();
        this.notifications = new Map();
        this.subscribers = [];
        this.updateInterval = null;
        this.isEnabled = true;
        
        this.badgeConfig = {
            'service-orders': {
                label: 'Service Orders',
                icon: '📋',
                color: 'primary',
                priority: 10,
                endpoint: '/api/service-orders/pending-count',
                refreshInterval: 30000 // 30 seconds
            },
            'device-alerts': {
                label: 'Device Alerts',
                icon: '⚠️',
                color: 'warning',
                priority: 9,
                endpoint: '/api/devices/alert-count',
                refreshInterval: 60000 // 1 minute
            },
            'system-notifications': {
                label: 'System Notifications',
                icon: '🔔',
                color: 'info',
                priority: 8,
                endpoint: '/api/notifications/unread-count',
                refreshInterval: 45000 // 45 seconds
            },
            'low-inventory': {
                label: 'Low Inventory',
                icon: '📦',
                color: 'danger',
                priority: 7,
                endpoint: '/api/inventory/low-stock-count',
                refreshInterval: 300000 // 5 minutes
            },
            'maintenance-due': {
                label: 'Maintenance Due',
                icon: '🔧',
                color: 'warning',
                priority: 6,
                endpoint: '/api/maintenance/due-count',
                refreshInterval: 3600000 // 1 hour
            }
        };
        
        this.init();
    }

    async init() {
        this.setupBadgeContainers();
        this.setupEventListeners();
        this.startPeriodicUpdates();
        
        // Initial badge update
        await this.updateAllBadges();
        
        console.log('NotificationBadgeSystem initialized');
    }

    setupBadgeContainers() {
        // Add badges to navigation items
        this.addNavigationBadges();
        
        // Add global notification indicator
        this.addGlobalNotificationIndicator();
        
        // Add styles
        this.addBadgeStyles();
    }

    addNavigationBadges() {
        // Service Orders badge
        const serviceOrderLink = document.querySelector('a[href="#service-orders"]');
        if (serviceOrderLink) {
            this.addBadgeToElement(serviceOrderLink, 'service-orders');
        }
        
        // Add badges to dropdown menus as well
        const dropdownServiceOrderLink = document.querySelector('.dropdown-item[data-page="service-orders.html"]');
        if (dropdownServiceOrderLink) {
            this.addBadgeToElement(dropdownServiceOrderLink, 'service-orders');
        }
        
        // Device list badge for device alerts
        const deviceListLink = document.querySelector('a[href="#coolers"]');
        if (deviceListLink) {
            this.addBadgeToElement(deviceListLink, 'device-alerts');
        }
    }

    addBadgeToElement(element, badgeId) {
        const badge = document.createElement('span');
        badge.className = `notification-badge notification-badge-${badgeId}`;
        badge.setAttribute('data-badge-id', badgeId);
        badge.style.display = 'none';
        
        // Position relative to the element
        element.style.position = 'relative';
        element.appendChild(badge);
        
        this.badges.set(badgeId, {
            element: badge,
            parentElement: element,
            count: 0,
            lastUpdate: 0
        });
    }

    addGlobalNotificationIndicator() {
        const navRight = document.querySelector('.nav-right');
        if (!navRight) return;
        
        const globalIndicator = document.createElement('div');
        globalIndicator.className = 'global-notification-indicator';
        globalIndicator.innerHTML = `
            <button class="notification-bell" aria-label="View notifications">
                <span class="bell-icon">🔔</span>
                <span class="notification-badge global-badge" data-badge-id="global" style="display: none;"></span>
            </button>
            <div class="notification-dropdown" style="display: none;">
                <div class="notification-dropdown-header">
                    <h3>Notifications</h3>
                    <button class="mark-all-read">Mark all read</button>
                </div>
                <div class="notification-dropdown-content">
                    <div class="notification-list"></div>
                </div>
                <div class="notification-dropdown-footer">
                    <a href="#" class="view-all-notifications">View all notifications</a>
                </div>
            </div>
        `;
        
        // Insert before search or user dropdown
        const searchContainer = navRight.querySelector('.enhanced-search-container');
        const userDropdown = navRight.querySelector('.user-dropdown');
        const insertBefore = searchContainer || userDropdown || navRight.firstChild;
        
        if (insertBefore) {
            navRight.insertBefore(globalIndicator, insertBefore);
        } else {
            navRight.appendChild(globalIndicator);
        }
        
        // Add event listeners
        this.setupGlobalIndicatorEvents(globalIndicator);
        
        // Register global badge
        const globalBadge = globalIndicator.querySelector('.global-badge');
        this.badges.set('global', {
            element: globalBadge,
            parentElement: globalIndicator.querySelector('.notification-bell'),
            count: 0,
            lastUpdate: 0
        });
    }

    setupGlobalIndicatorEvents(indicator) {
        const bellButton = indicator.querySelector('.notification-bell');
        const dropdown = indicator.querySelector('.notification-dropdown');
        const markAllRead = indicator.querySelector('.mark-all-read');
        
        bellButton.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleNotificationDropdown();
        });
        
        markAllRead.addEventListener('click', () => {
            this.markAllNotificationsRead();
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!indicator.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    }

    addBadgeStyles() {
        if (document.getElementById('notification-badge-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'notification-badge-styles';
        style.textContent = `
            .notification-badge {
                position: absolute;
                top: -8px;
                right: -8px;
                min-width: 18px;
                height: 18px;
                border-radius: 9px;
                font-size: 11px;
                font-weight: 600;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10;
                animation: badgeAppear 0.3s ease-out;
                font-family: var(--font-sans);
                line-height: 1;
                padding: 0 4px;
                box-sizing: border-box;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
            }
            
            @keyframes badgeAppear {
                from {
                    opacity: 0;
                    transform: scale(0.5);
                }
                to {
                    opacity: 1;
                    transform: scale(1);
                }
            }
            
            .notification-badge.pulse {
                animation: badgePulse 2s infinite;
            }
            
            @keyframes badgePulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            
            /* Badge color variants */
            .notification-badge.primary {
                background: var(--color-primary-500);
            }
            
            .notification-badge.danger {
                background: var(--color-danger);
            }
            
            .notification-badge.warning {
                background: var(--color-warning);
                color: var(--color-warning-text);
            }
            
            .notification-badge.info {
                background: var(--color-info);
            }
            
            .notification-badge.success {
                background: var(--color-success);
            }
            
            /* Global notification indicator */
            .global-notification-indicator {
                position: relative;
                margin-right: var(--space-md);
            }
            
            .notification-bell {
                background: none;
                border: 1px solid rgba(255,255,255,0.3);
                color: white;
                padding: var(--space-sm);
                border-radius: var(--radius-md);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all var(--duration-fast);
                position: relative;
            }
            
            .notification-bell:hover {
                background: rgba(255,255,255,0.1);
                border-color: rgba(255,255,255,0.5);
            }
            
            .bell-icon {
                font-size: 16px;
            }
            
            .notification-dropdown {
                position: absolute;
                top: calc(100% + 8px);
                right: 0;
                background: var(--color-neutral-0);
                border-radius: var(--radius-md);
                box-shadow: var(--shadow-xl);
                min-width: 350px;
                max-width: 400px;
                max-height: 500px;
                z-index: var(--z-tooltip);
                overflow: hidden;
            }
            
            .notification-dropdown-header {
                padding: var(--space-md);
                border-bottom: 1px solid var(--color-neutral-200);
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: var(--color-neutral-50);
            }
            
            .notification-dropdown-header h3 {
                margin: 0;
                font-size: var(--text-base);
                font-weight: var(--font-semibold);
                color: var(--color-neutral-800);
            }
            
            .mark-all-read {
                background: none;
                border: none;
                color: var(--color-primary-500);
                font-size: var(--text-sm);
                cursor: pointer;
                padding: var(--space-xs) var(--space-sm);
                border-radius: var(--radius-sm);
                transition: background var(--duration-fast);
            }
            
            .mark-all-read:hover {
                background: var(--color-primary-50);
            }
            
            .notification-dropdown-content {
                max-height: 300px;
                overflow-y: auto;
            }
            
            .notification-list {
                padding: 0;
            }
            
            .notification-item {
                display: flex;
                align-items: flex-start;
                gap: var(--space-sm);
                padding: var(--space-md);
                border-bottom: 1px solid var(--color-neutral-100);
                transition: background var(--duration-fast);
                cursor: pointer;
            }
            
            .notification-item:hover {
                background: var(--color-neutral-50);
            }
            
            .notification-item.unread {
                background: var(--color-primary-50);
                border-left: 3px solid var(--color-primary-500);
            }
            
            .notification-icon {
                font-size: 20px;
                flex-shrink: 0;
                width: 24px;
                text-align: center;
            }
            
            .notification-content {
                flex: 1;
                min-width: 0;
            }
            
            .notification-title {
                font-size: var(--text-sm);
                font-weight: var(--font-medium);
                color: var(--color-neutral-800);
                margin-bottom: 2px;
                line-height: 1.4;
            }
            
            .notification-message {
                font-size: var(--text-xs);
                color: var(--color-neutral-600);
                margin-bottom: 4px;
                line-height: 1.3;
            }
            
            .notification-time {
                font-size: var(--text-xs);
                color: var(--color-neutral-500);
                font-family: var(--font-mono);
            }
            
            .notification-dropdown-footer {
                padding: var(--space-sm) var(--space-md);
                border-top: 1px solid var(--color-neutral-200);
                background: var(--color-neutral-50);
                text-align: center;
            }
            
            .view-all-notifications {
                color: var(--color-primary-500);
                text-decoration: none;
                font-size: var(--text-sm);
                font-weight: var(--font-medium);
            }
            
            .view-all-notifications:hover {
                text-decoration: underline;
            }
            
            .notification-empty {
                padding: var(--space-xl);
                text-align: center;
                color: var(--color-neutral-500);
            }
            
            .notification-empty-icon {
                font-size: 48px;
                opacity: 0.3;
                margin-bottom: var(--space-md);
            }
            
            /* Sidebar badge adjustments */
            .sidebar-item .notification-badge {
                top: 50%;
                right: var(--space-sm);
                transform: translateY(-50%);
            }
            
            /* Mobile responsive */
            @media (max-width: 768px) {
                .notification-dropdown {
                    min-width: 300px;
                    right: -50px;
                }
                
                .global-notification-indicator {
                    margin-right: var(--space-sm);
                }
            }
            
            /* High contrast support */
            @media (prefers-contrast: high) {
                .notification-badge {
                    border: 2px solid white;
                }
            }
            
            /* Reduced motion support */
            @media (prefers-reduced-motion: reduce) {
                .notification-badge {
                    animation: none !important;
                }
                
                .notification-badge.pulse {
                    animation: none !important;
                }
            }
        `;
        
        document.head.appendChild(style);
    }

    setupEventListeners() {
        // Listen for cross-frame messages about badge updates
        window.addEventListener('message', (event) => {
            if (event.origin !== window.location.origin) return;
            
            const { type, payload } = event.data;
            switch (type) {
                case 'BADGE_UPDATE':
                    this.updateBadge(payload.badgeId, payload.count, payload.notifications);
                    break;
                case 'NOTIFICATION_ADDED':
                    this.addNotification(payload);
                    break;
                case 'NOTIFICATION_CLEARED':
                    this.removeNotification(payload.id);
                    break;
            }
        });

        // Listen for user preferences changes
        if (window.UserPreferences) {
            window.UserPreferences.subscribe('preference_changed', (data) => {
                if (data.category === 'notifications') {
                    this.handlePreferenceChange(data);
                }
            });
        }
    }

    startPeriodicUpdates() {
        // Update badges every minute
        this.updateInterval = setInterval(() => {
            this.updateAllBadges();
        }, 60000);
        
        // More frequent updates for high-priority badges
        setInterval(() => {
            this.updateHighPriorityBadges();
        }, 15000);
    }

    stopPeriodicUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    async updateAllBadges() {
        if (!this.isEnabled) return;
        
        const updatePromises = Object.keys(this.badgeConfig).map(badgeId => 
            this.updateBadgeData(badgeId)
        );
        
        await Promise.allSettled(updatePromises);
        this.updateGlobalBadge();
    }

    async updateHighPriorityBadges() {
        if (!this.isEnabled) return;
        
        const highPriorityBadges = Object.entries(this.badgeConfig)
            .filter(([_, config]) => config.priority >= 9)
            .map(([badgeId]) => badgeId);
        
        const updatePromises = highPriorityBadges.map(badgeId => 
            this.updateBadgeData(badgeId)
        );
        
        await Promise.allSettled(updatePromises);
        this.updateGlobalBadge();
    }

    async updateBadgeData(badgeId) {
        const config = this.badgeConfig[badgeId];
        if (!config) return;
        
        const badge = this.badges.get(badgeId);
        if (!badge) return;
        
        // Check if update is needed based on refresh interval
        const now = Date.now();
        if (now - badge.lastUpdate < config.refreshInterval) {
            return;
        }
        
        try {
            const data = await this.fetchBadgeData(badgeId, config);
            this.updateBadge(badgeId, data.count, data.notifications);
            badge.lastUpdate = now;
        } catch (error) {
            console.error(`Error updating badge ${badgeId}:`, error);
        }
    }

    async fetchBadgeData(badgeId, config) {
        // Simulate API calls - replace with actual endpoints
        switch (badgeId) {
            case 'service-orders':
                return this.fetchServiceOrderBadgeData();
            case 'device-alerts':
                return this.fetchDeviceAlertBadgeData();
            case 'system-notifications':
                return this.fetchSystemNotificationBadgeData();
            case 'low-inventory':
                return this.fetchLowInventoryBadgeData();
            case 'maintenance-due':
                return this.fetchMaintenanceBadgeData();
            default:
                return { count: 0, notifications: [] };
        }
    }

    async fetchServiceOrderBadgeData() {
        try {
            if (!window.CVDApi) return { count: 0, notifications: [] };
            
            const api = new CVDApi();
            const orders = await api.makeRequest('GET', '/service-orders');
            const pendingOrders = orders.filter(order => 
                order.status === 'pending' || order.status === 'in_progress'
            );
            
            const notifications = pendingOrders.slice(0, 5).map(order => ({
                id: `service-order-${order.id}`,
                type: 'service-order',
                title: `Service Order #${order.id}`,
                message: `${order.device_name} - ${order.status}`,
                timestamp: Date.now(),
                data: order,
                read: false
            }));
            
            return {
                count: pendingOrders.length,
                notifications
            };
        } catch (error) {
            console.error('Error fetching service order badge data:', error);
            return { count: 0, notifications: [] };
        }
    }

    async fetchDeviceAlertBadgeData() {
        try {
            if (!window.CVDApi) return { count: 0, notifications: [] };
            
            const api = new CVDApi();
            const devices = await api.getDevices();
            
            // Simulate device alerts based on last communication
            const alertDevices = devices.filter(device => {
                if (!device.last_communication) return true;
                const lastComm = new Date(device.last_communication);
                const hoursSinceLastComm = (Date.now() - lastComm.getTime()) / (1000 * 60 * 60);
                return hoursSinceLastComm > 24; // Alert if no communication for 24+ hours
            });
            
            const notifications = alertDevices.slice(0, 5).map(device => ({
                id: `device-alert-${device.id}`,
                type: 'device-alert',
                title: `Device Alert: ${device.asset_tag}`,
                message: `No communication for 24+ hours`,
                timestamp: Date.now(),
                data: device,
                read: false
            }));
            
            return {
                count: alertDevices.length,
                notifications
            };
        } catch (error) {
            console.error('Error fetching device alert badge data:', error);
            return { count: 0, notifications: [] };
        }
    }

    async fetchSystemNotificationBadgeData() {
        // Simulate system notifications
        const systemNotifications = [
            {
                id: 'system-maintenance',
                type: 'system',
                title: 'System Maintenance Scheduled',
                message: 'Scheduled maintenance on Sunday 2:00 AM',
                timestamp: Date.now() - 300000, // 5 minutes ago
                read: false
            }
        ];
        
        return {
            count: systemNotifications.filter(n => !n.read).length,
            notifications: systemNotifications
        };
    }

    async fetchLowInventoryBadgeData() {
        try {
            if (!window.CVDApi) return { count: 0, notifications: [] };
            
            // This would need actual inventory tracking
            // For now, simulate based on planogram data
            return { count: 0, notifications: [] };
        } catch (error) {
            console.error('Error fetching low inventory badge data:', error);
            return { count: 0, notifications: [] };
        }
    }

    async fetchMaintenanceBadgeData() {
        try {
            if (!window.CVDApi) return { count: 0, notifications: [] };
            
            // This would need actual maintenance tracking
            // For now, return empty
            return { count: 0, notifications: [] };
        } catch (error) {
            console.error('Error fetching maintenance badge data:', error);
            return { count: 0, notifications: [] };
        }
    }

    updateBadge(badgeId, count, notifications = []) {
        const badge = this.badges.get(badgeId);
        if (!badge) return;
        
        const oldCount = badge.count;
        badge.count = count;
        
        if (count > 0) {
            badge.element.textContent = count > 99 ? '99+' : count.toString();
            badge.element.style.display = 'flex';
            
            // Add color class
            const config = this.badgeConfig[badgeId];
            if (config) {
                badge.element.className = `notification-badge notification-badge-${badgeId} ${config.color}`;
            }
            
            // Add pulse animation for new notifications
            if (count > oldCount && oldCount > 0) {
                badge.element.classList.add('pulse');
                setTimeout(() => {
                    badge.element.classList.remove('pulse');
                }, 2000);
            }
        } else {
            badge.element.style.display = 'none';
            badge.element.classList.remove('pulse');
        }
        
        // Update notifications
        if (notifications && notifications.length > 0) {
            notifications.forEach(notification => {
                this.notifications.set(notification.id, notification);
            });
        }
        
        // Notify subscribers
        this.notifySubscribers('badge_updated', {
            badgeId,
            count,
            oldCount,
            notifications
        });
    }

    updateGlobalBadge() {
        const totalCount = Array.from(this.badges.values())
            .filter(badge => badge.count > 0)
            .reduce((sum, badge) => sum + badge.count, 0);
        
        const globalBadge = this.badges.get('global');
        if (globalBadge) {
            this.updateBadge('global', totalCount);
        }
    }

    toggleNotificationDropdown() {
        const dropdown = document.querySelector('.notification-dropdown');
        if (!dropdown) return;
        
        const isVisible = dropdown.style.display !== 'none';
        
        if (isVisible) {
            dropdown.style.display = 'none';
        } else {
            this.updateNotificationDropdown();
            dropdown.style.display = 'block';
        }
    }

    updateNotificationDropdown() {
        const notificationList = document.querySelector('.notification-list');
        if (!notificationList) return;
        
        const allNotifications = Array.from(this.notifications.values())
            .sort((a, b) => b.timestamp - a.timestamp)
            .slice(0, 10); // Show latest 10
        
        if (allNotifications.length === 0) {
            notificationList.innerHTML = `
                <div class="notification-empty">
                    <div class="notification-empty-icon">🔔</div>
                    <div>No notifications</div>
                </div>
            `;
            return;
        }
        
        notificationList.innerHTML = allNotifications.map(notification => `
            <div class="notification-item ${!notification.read ? 'unread' : ''}" 
                 data-notification-id="${notification.id}">
                <span class="notification-icon">${this.getNotificationIcon(notification.type)}</span>
                <div class="notification-content">
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-message">${notification.message}</div>
                    <div class="notification-time">${this.formatNotificationTime(notification.timestamp)}</div>
                </div>
            </div>
        `).join('');
        
        // Add click handlers
        notificationList.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', () => {
                const notificationId = item.dataset.notificationId;
                this.handleNotificationClick(notificationId);
            });
        });
    }

    getNotificationIcon(type) {
        const icons = {
            'service-order': '📋',
            'device-alert': '⚠️',
            'system': '🔔',
            'inventory': '📦',
            'maintenance': '🔧'
        };
        return icons[type] || '🔔';
    }

    formatNotificationTime(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        
        if (diff < 60000) return 'now';
        if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
        if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';
        return Math.floor(diff / 86400000) + 'd ago';
    }

    handleNotificationClick(notificationId) {
        const notification = this.notifications.get(notificationId);
        if (!notification) return;
        
        // Mark as read
        notification.read = true;
        
        // Navigate based on notification type
        switch (notification.type) {
            case 'service-order':
                window.location.hash = '#service-orders';
                break;
            case 'device-alert':
                window.location.hash = '#coolers';
                break;
            default:
                // Close dropdown
                break;
        }
        
        // Close dropdown
        const dropdown = document.querySelector('.notification-dropdown');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
        
        // Update badges
        this.updateAllBadges();
    }

    markAllNotificationsRead() {
        this.notifications.forEach(notification => {
            notification.read = true;
        });
        
        // Update dropdown
        this.updateNotificationDropdown();
        
        // Clear all badges
        this.badges.forEach((badge, badgeId) => {
            if (badgeId !== 'global') {
                this.updateBadge(badgeId, 0);
            }
        });
        
        this.updateGlobalBadge();
        
        if (window.ToastManager) {
            window.ToastManager.show('success', 'All notifications marked as read');
        }
    }

    addNotification(notification) {
        this.notifications.set(notification.id, {
            ...notification,
            timestamp: notification.timestamp || Date.now(),
            read: false
        });
        
        // Update relevant badge
        const badgeType = this.getNotificationBadgeType(notification.type);
        if (badgeType) {
            this.updateBadgeData(badgeType);
        }
    }

    removeNotification(notificationId) {
        this.notifications.delete(notificationId);
        this.updateAllBadges();
    }

    getNotificationBadgeType(notificationType) {
        const mapping = {
            'service-order': 'service-orders',
            'device-alert': 'device-alerts',
            'system': 'system-notifications',
            'inventory': 'low-inventory',
            'maintenance': 'maintenance-due'
        };
        return mapping[notificationType];
    }

    handlePreferenceChange(data) {
        const { key, value } = data;
        
        switch (key) {
            case 'showDesktop':
                // Enable/disable desktop notifications
                if (value && 'Notification' in window && Notification.permission === 'default') {
                    Notification.requestPermission();
                }
                break;
            case 'serviceOrderAlerts':
                // Enable/disable service order notifications
                this.badgeConfig['service-orders'].enabled = value;
                break;
            case 'deviceStatusAlerts':
                // Enable/disable device status notifications
                this.badgeConfig['device-alerts'].enabled = value;
                break;
        }
    }

    subscribe(callback) {
        this.subscribers.push(callback);
        
        return () => {
            const index = this.subscribers.indexOf(callback);
            if (index > -1) {
                this.subscribers.splice(index, 1);
            }
        };
    }

    notifySubscribers(event, data) {
        this.subscribers.forEach(callback => {
            try {
                callback(event, data);
            } catch (error) {
                console.error('Error in notification badge subscriber:', error);
            }
        });
    }

    // Manual badge operations
    setBadgeCount(badgeId, count) {
        this.updateBadge(badgeId, count);
    }

    incrementBadge(badgeId, increment = 1) {
        const badge = this.badges.get(badgeId);
        if (badge) {
            this.updateBadge(badgeId, badge.count + increment);
        }
    }

    decrementBadge(badgeId, decrement = 1) {
        const badge = this.badges.get(badgeId);
        if (badge) {
            this.updateBadge(badgeId, Math.max(0, badge.count - decrement));
        }
    }

    clearBadge(badgeId) {
        this.updateBadge(badgeId, 0);
    }

    clearAllBadges() {
        this.badges.forEach((_, badgeId) => {
            this.clearBadge(badgeId);
        });
    }

    // Enable/disable system
    enable() {
        this.isEnabled = true;
        this.startPeriodicUpdates();
        this.updateAllBadges();
    }

    disable() {
        this.isEnabled = false;
        this.stopPeriodicUpdates();
        this.clearAllBadges();
    }

    // Integration with other systems
    integrateWithToastSystem() {
        if (window.ToastManager && typeof window.ToastManager.subscribe === 'function') {
            window.ToastManager.subscribe('toast_shown', (data) => {
                // Convert certain toasts to persistent notifications
                if (data.type === 'error' || data.type === 'warning') {
                    const notification = {
                        id: `toast-${Date.now()}`,
                        type: 'system',
                        title: data.type === 'error' ? 'System Error' : 'Warning',
                        message: data.message,
                        timestamp: Date.now()
                    };
                    this.addNotification(notification);
                }
            });
        }
    }

    integrateWithCommandPalette() {
        if (window.commandPaletteCommands) {
            window.commandPaletteCommands.push(
                { group: 'Notifications', icon: '🔔', text: 'View Notifications', action: () => this.toggleNotificationDropdown() },
                { group: 'Notifications', icon: '✅', text: 'Mark All Read', action: () => this.markAllNotificationsRead() },
                { group: 'Notifications', icon: '🔕', text: 'Clear All Badges', action: () => this.clearAllBadges() }
            );
        }
    }

    // Utility methods
    getBadgeCount(badgeId) {
        const badge = this.badges.get(badgeId);
        return badge ? badge.count : 0;
    }

    getTotalBadgeCount() {
        return Array.from(this.badges.values())
            .reduce((sum, badge) => sum + badge.count, 0);
    }

    getStats() {
        return {
            badgeCount: this.badges.size,
            notificationCount: this.notifications.size,
            totalBadges: this.getTotalBadgeCount(),
            unreadNotifications: Array.from(this.notifications.values()).filter(n => !n.read).length,
            isEnabled: this.isEnabled
        };
    }

    // Cleanup
    destroy() {
        this.stopPeriodicUpdates();
        
        // Remove all badge elements
        this.badges.forEach(badge => {
            if (badge.element && badge.element.parentNode) {
                badge.element.parentNode.removeChild(badge.element);
            }
        });
        
        // Remove global indicator
        const globalIndicator = document.querySelector('.global-notification-indicator');
        if (globalIndicator && globalIndicator.parentNode) {
            globalIndicator.parentNode.removeChild(globalIndicator);
        }
        
        // Remove styles
        const styles = document.getElementById('notification-badge-styles');
        if (styles) {
            styles.remove();
        }
        
        this.badges.clear();
        this.notifications.clear();
        this.subscribers = [];
    }
}

// Initialize global instance
window.NotificationBadgeSystem = new NotificationBadgeSystem();

// Auto-integrate when loaded
document.addEventListener('DOMContentLoaded', () => {
    if (window.NotificationBadgeSystem) {
        window.NotificationBadgeSystem.integrateWithToastSystem();
        window.NotificationBadgeSystem.integrateWithCommandPalette();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationBadgeSystem;
}