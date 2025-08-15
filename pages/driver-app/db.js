// IndexedDB wrapper for offline data storage
class OfflineDB {
    constructor() {
        this.dbName = 'CVDDriverDB';
        this.version = 1;
        this.db = null;
    }

    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Service Orders store
                if (!db.objectStoreNames.contains('serviceOrders')) {
                    const orderStore = db.createObjectStore('serviceOrders', { keyPath: 'id' });
                    orderStore.createIndex('status', 'status', { unique: false });
                    orderStore.createIndex('date', 'createdAt', { unique: false });
                    orderStore.createIndex('syncStatus', 'syncStatus', { unique: false });
                }

                // Routes store
                if (!db.objectStoreNames.contains('routes')) {
                    const routeStore = db.createObjectStore('routes', { keyPath: 'id' });
                    routeStore.createIndex('routeNumber', 'routeNumber', { unique: false });
                }

                // Devices store
                if (!db.objectStoreNames.contains('devices')) {
                    const deviceStore = db.createObjectStore('devices', { keyPath: 'id' });
                    deviceStore.createIndex('asset', 'asset', { unique: true });
                }

                // Offline Actions queue
                if (!db.objectStoreNames.contains('offlineActions')) {
                    const actionStore = db.createObjectStore('offlineActions', { keyPath: 'id', autoIncrement: true });
                    actionStore.createIndex('timestamp', 'timestamp', { unique: false });
                    actionStore.createIndex('type', 'type', { unique: false });
                }

                // Photos store
                if (!db.objectStoreNames.contains('photos')) {
                    const photoStore = db.createObjectStore('photos', { keyPath: 'id' });
                    photoStore.createIndex('orderId', 'orderId', { unique: false });
                    photoStore.createIndex('uploaded', 'uploaded', { unique: false });
                }
            };
        });
    }

    // Generic CRUD operations
    async add(storeName, data) {
        const transaction = this.db.transaction([storeName], 'readwrite');
        const store = transaction.objectStore(storeName);
        return store.add(data);
    }

    async get(storeName, key) {
        const transaction = this.db.transaction([storeName], 'readonly');
        const store = transaction.objectStore(storeName);
        return new Promise((resolve, reject) => {
            const request = store.get(key);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getAll(storeName) {
        const transaction = this.db.transaction([storeName], 'readonly');
        const store = transaction.objectStore(storeName);
        return new Promise((resolve, reject) => {
            const request = store.getAll();
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async update(storeName, data) {
        const transaction = this.db.transaction([storeName], 'readwrite');
        const store = transaction.objectStore(storeName);
        return store.put(data);
    }

    async delete(storeName, key) {
        const transaction = this.db.transaction([storeName], 'readwrite');
        const store = transaction.objectStore(storeName);
        return store.delete(key);
    }

    // Service Order specific operations
    async saveServiceOrder(order) {
        order.syncStatus = order.syncStatus || 'synced';
        order.lastModified = new Date().toISOString();
        return this.update('serviceOrders', order);
    }

    async getServiceOrdersByStatus(status) {
        const transaction = this.db.transaction(['serviceOrders'], 'readonly');
        const store = transaction.objectStore('serviceOrders');
        const index = store.index('status');
        
        return new Promise((resolve, reject) => {
            const request = index.getAll(status);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // Offline action queue
    async queueOfflineAction(action) {
        const actionData = {
            ...action,
            timestamp: new Date().toISOString(),
            retryCount: 0
        };
        return this.add('offlineActions', actionData);
    }

    async getOfflineActions() {
        const actions = await this.getAll('offlineActions');
        return actions.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    }

    async removeOfflineAction(id) {
        return this.delete('offlineActions', id);
    }

    // Photo storage
    async savePhoto(photoData) {
        const photo = {
            id: `photo_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            ...photoData,
            uploaded: false,
            createdAt: new Date().toISOString()
        };
        return this.add('photos', photo);
    }

    async getPhotosByOrder(orderId) {
        const transaction = this.db.transaction(['photos'], 'readonly');
        const store = transaction.objectStore('photos');
        const index = store.index('orderId');
        
        return new Promise((resolve, reject) => {
            const request = index.getAll(orderId);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async markPhotoUploaded(photoId) {
        const photo = await this.get('photos', photoId);
        if (photo) {
            photo.uploaded = true;
            photo.uploadedAt = new Date().toISOString();
            return this.update('photos', photo);
        }
    }
}

// Export singleton instance
const offlineDB = new OfflineDB();