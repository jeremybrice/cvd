// Sync Manager for offline/online data synchronization
class SyncManager {
    constructor() {
        this.syncInProgress = false;
        this.syncInterval = null;
        this.lastSyncTime = null;
    }

    async init() {
        // Initialize sync on startup
        await this.loadSyncState();
        
        // Set up event listeners
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
        
        // Start periodic sync if online
        if (navigator.onLine) {
            this.startPeriodicSync();
        }
    }

    async loadSyncState() {
        const savedState = localStorage.getItem('cvd_sync_state');
        if (savedState) {
            const state = JSON.parse(savedState);
            this.lastSyncTime = new Date(state.lastSyncTime);
        }
    }

    saveSyncState() {
        localStorage.setItem('cvd_sync_state', JSON.stringify({
            lastSyncTime: this.lastSyncTime
        }));
    }

    handleOnline() {
        console.log('Network online - starting sync');
        this.performSync();
        this.startPeriodicSync();
    }

    handleOffline() {
        console.log('Network offline - stopping sync');
        this.stopPeriodicSync();
    }

    startPeriodicSync() {
        // Sync every 5 minutes
        this.syncInterval = setInterval(() => {
            this.performSync();
        }, 5 * 60 * 1000);
    }

    stopPeriodicSync() {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
            this.syncInterval = null;
        }
    }

    async performSync() {
        if (this.syncInProgress || !navigator.onLine) {
            return;
        }

        this.syncInProgress = true;
        this.notifySyncStart();
        
        const startTime = Date.now();
        const results = {
            queueProcessed: 0,
            ordersSync: 0,
            photosUploaded: 0
        };
        
        // Log sync attempt if monitoring available
        if (window.appMonitoring) {
            appMonitoring.logSyncAttempt('automatic');
        }

        try {
            // 1. Process offline action queue
            const actions = await offlineDB.getOfflineActions();
            results.queueProcessed = actions.length;
            await this.processOfflineQueue();
            
            // 2. Sync service orders
            const orders = await offlineDB.getAll('serviceOrders');
            const pendingOrders = orders.filter(o => o.syncStatus === 'pending');
            results.ordersSync = pendingOrders.length;
            await this.syncServiceOrders();
            
            // 3. Upload pending photos
            const photos = await offlineDB.getAll('photos');
            const pendingPhotos = photos.filter(p => !p.uploaded);
            results.photosUploaded = pendingPhotos.length;
            await this.uploadPendingPhotos();
            
            // 4. Download updates
            await this.downloadUpdates();
            
            this.lastSyncTime = new Date();
            this.saveSyncState();
            this.notifySyncSuccess();
            
            // Log sync success if monitoring available
            if (window.appMonitoring) {
                appMonitoring.logSyncSuccess({
                    startTime,
                    endTime: Date.now(),
                    itemsSynced: results.queueProcessed + results.ordersSync + results.photosUploaded,
                    type: 'automatic'
                });
            }
            
        } catch (error) {
            console.error('Sync failed:', error);
            this.notifySyncError(error);
            
            // Log sync failure if monitoring available
            if (window.appMonitoring) {
                appMonitoring.logSyncFailure(error, {
                    duration: Date.now() - startTime,
                    results
                });
            }
        } finally {
            this.syncInProgress = false;
        }
    }

    async processOfflineQueue() {
        const actions = await offlineDB.getOfflineActions();
        
        for (const action of actions) {
            try {
                await this.processOfflineAction(action);
                await offlineDB.removeOfflineAction(action.id);
            } catch (error) {
                console.error('Failed to process offline action:', error);
                
                // Increment retry count
                action.retryCount = (action.retryCount || 0) + 1;
                
                // Remove if too many retries
                if (action.retryCount > 3) {
                    await offlineDB.removeOfflineAction(action.id);
                    console.error('Removing action after 3 retries:', action);
                } else {
                    await offlineDB.update('offlineActions', action);
                }
            }
        }
    }

    async processOfflineAction(action) {
        const api = new CVDApi();
        
        switch (action.type) {
            case 'UPDATE_ORDER_STATUS':
                await api.makeRequest('PUT', `/service-orders/${action.orderId}`, {
                    status: action.status,
                    startTime: action.startTime
                });
                break;
                
            case 'COMPLETE_ORDER':
                await api.makeRequest('PUT', `/service-orders/${action.orderId}`, {
                    status: 'completed',
                    completedAt: action.completedAt
                });
                break;
                
            case 'EXECUTE_DELIVERY':
                await api.makeRequest('POST', '/service-orders/execute', action.data);
                break;
                
            case 'UPLOAD_PHOTO':
                // Photo uploads handled separately
                break;
                
            default:
                console.warn('Unknown offline action type:', action.type);
        }
    }

    async syncServiceOrders() {
        const api = new CVDApi();
        
        // Get all orders with pending changes
        const orders = await offlineDB.getAll('serviceOrders');
        const pendingOrders = orders.filter(o => o.syncStatus === 'pending');
        
        for (const order of pendingOrders) {
            try {
                // Send update to server
                const response = await api.makeRequest('PUT', `/service-orders/${order.id}/sync`, {
                    ...order,
                    lastModified: order.lastModified
                });
                
                // Handle conflicts
                if (response && response.conflict) {
                    await this.resolveConflict(order, response.serverVersion);
                } else {
                    // Mark as synced
                    order.syncStatus = 'synced';
                    await offlineDB.saveServiceOrder(order);
                }
            } catch (error) {
                console.error('Failed to sync order:', order.id, error);
            }
        }
    }

    async resolveConflict(localOrder, serverOrder) {
        // Simple conflict resolution: server wins for now
        // In a real app, you might want to merge changes or prompt the user
        console.warn('Conflict detected for order:', localOrder.id);
        
        // Update local with server version
        serverOrder.syncStatus = 'synced';
        await offlineDB.saveServiceOrder(serverOrder);
    }

    async uploadPendingPhotos() {
        const api = new CVDApi();
        const photos = await offlineDB.getAll('photos');
        const pendingPhotos = photos.filter(p => !p.uploaded);
        
        for (const photo of pendingPhotos) {
            try {
                const blob = this.dataURLtoBlob(photo.data);
                const formData = new FormData();
                formData.append('orderId', photo.orderId);
                formData.append('photo', blob, `photo_${photo.id}.jpg`);
                formData.append('timestamp', photo.timestamp);
                formData.append('type', photo.type);
                
                await api.makeRequest('POST', '/service-orders/photos', formData);
                
                // Mark as uploaded
                await offlineDB.markPhotoUploaded(photo.id);
                
                // Optionally delete old photos to save space
                const photoAge = Date.now() - new Date(photo.createdAt).getTime();
                if (photoAge > 7 * 24 * 60 * 60 * 1000) { // 7 days
                    await offlineDB.delete('photos', photo.id);
                }
            } catch (error) {
                console.error('Failed to upload photo:', photo.id, error);
            }
        }
    }

    async downloadUpdates() {
        const api = new CVDApi();
        
        // Get updates since last sync
        const params = new URLSearchParams();
        if (this.lastSyncTime) {
            params.append('since', this.lastSyncTime.toISOString());
        }
        
        try {
            // Download updated orders
            const ordersResponse = await api.makeRequest('GET', `/service-orders?${params}`);
            if (ordersResponse) {
                // Handle both array and {orders: [...]} format
                const orders = Array.isArray(ordersResponse) ? ordersResponse : ordersResponse.orders;
                if (orders) {
                        for (const order of orders) {
                        await offlineDB.saveServiceOrder(order);
                    }
                }
            }
            
            // Download updated routes
            const routesResponse = await api.makeRequest('GET', `/routes?${params}`);
            if (routesResponse && routesResponse.routes) {
                for (const route of routesResponse.routes) {
                    await offlineDB.update('routes', route);
                }
            }
        } catch (error) {
            console.error('Failed to download updates:', error);
        }
    }

    // Helper function to convert data URL to blob
    dataURLtoBlob(dataURL) {
        const parts = dataURL.split(',');
        const contentType = parts[0].match(/:(.*?);/)[1];
        const raw = atob(parts[1]);
        const rawLength = raw.length;
        const uInt8Array = new Uint8Array(rawLength);

        for (let i = 0; i < rawLength; ++i) {
            uInt8Array[i] = raw.charCodeAt(i);
        }

        return new Blob([uInt8Array], { type: contentType });
    }

    // Notification methods
    notifySyncStart() {
        // Update UI to show sync in progress
        const event = new CustomEvent('sync:start');
        window.dispatchEvent(event);
    }

    notifySyncSuccess() {
        const event = new CustomEvent('sync:success', {
            detail: { lastSyncTime: this.lastSyncTime }
        });
        window.dispatchEvent(event);
    }

    notifySyncError(error) {
        const event = new CustomEvent('sync:error', {
            detail: { error: error.message }
        });
        window.dispatchEvent(event);
    }
}

// Create singleton instance
const syncManager = new SyncManager();