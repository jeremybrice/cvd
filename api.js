/**
 * CVD API Module
 * Provides a clean interface for communicating with the backend API
 * Includes error handling, retry logic, and offline support
 */

const API_BASE_URL = '/api';

class CVDApi {
    constructor() {
        this.baseUrl = API_BASE_URL;
        this.retryDelay = 1000; // 1 second
        this.maxRetries = 3;
        this.offlineQueue = [];
        this.isOnline = navigator.onLine;
        
        // Monitor online/offline status
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
        
        // Setup authentication interceptor
        this.setupAuthInterceptor();
    }
    
    setupAuthInterceptor() {
        // Store original fetch
        const originalFetch = window.fetch;
        const api = this;
        
        // Override fetch to handle auth
        window.fetch = async function(...args) {
            const response = await originalFetch(...args);
            
            // Handle 401 responses globally
            if (response.status === 401 && !args[0].includes('/auth/login')) {
                // Clear user data
                localStorage.removeItem('user');
                
                // Redirect to login
                const currentPath = window.location.pathname + window.location.hash;
                window.location.href = `/pages/login.html?return=${encodeURIComponent(currentPath)}`;
            }
            
            return response;
        };
    }
    
    handleOnline() {
        this.isOnline = true;
        console.log('API: Back online, processing offline queue...');
        this.processOfflineQueue();
    }
    
    handleOffline() {
        this.isOnline = false;
        console.log('API: Gone offline, queueing requests...');
    }
    
    async processOfflineQueue() {
        while (this.offlineQueue.length > 0) {
            const request = this.offlineQueue.shift();
            try {
                await this.makeRequest(request.method, request.endpoint, request.data);
            } catch (error) {
                console.error('Failed to process offline request:', error);
                // Re-queue if still offline
                if (!this.isOnline) {
                    this.offlineQueue.unshift(request);
                    break;
                }
            }
        }
    }
    
    async makeRequest(method, endpoint, data = null, retries = 0) {
        const url = `${this.baseUrl}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            mode: 'cors',
            credentials: 'include'  // Include cookies for session
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(error.error || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            // Handle network errors
            if (error.message === 'Failed to fetch' || !navigator.onLine) {
                if (!this.isOnline && (method === 'POST' || method === 'PUT' || method === 'DELETE')) {
                    // Queue write operations for later
                    this.offlineQueue.push({ method, endpoint, data });
                    console.log('API: Request queued for offline processing');
                    return { offline: true, queued: true };
                }
                
                // Throw error to show message to user
            }
            
            // Retry logic for transient failures
            if (retries < this.maxRetries && this.isOnline) {
                console.log(`API: Retrying request (${retries + 1}/${this.maxRetries})...`);
                await new Promise(resolve => setTimeout(resolve, this.retryDelay));
                return this.makeRequest(method, endpoint, data, retries + 1);
            }
            
            throw error;
        }
    }
    
    
    // Device Management
    
    /**
     * Get all devices
     * @returns {Promise<Array>} Array of device objects
     */
    async getDevices() {
        const devices = await this.makeRequest('GET', '/devices');
        return devices;
    }
    
    /**
     * Check if an asset number already exists
     * @param {string} assetNumber - Asset number to check
     * @returns {Promise<boolean>} True if asset exists, false otherwise
     */
    async checkAssetExists(assetNumber) {
        try {
            const devices = await this.getDevices();
            return devices.some(device => device.asset === assetNumber);
        } catch (error) {
            console.error('Failed to check asset:', error);
            // In case of error, allow the form to continue (backend will validate)
            return false;
        }
    }
    
    /**
     * Create a new device
     * @param {Object} deviceData - Device data
     * @param {string} deviceData.asset - Asset number
     * @param {string} deviceData.cooler - Cooler/device name
     * @param {string} deviceData.location - Location
     * @param {string} deviceData.model - Model (parent cabinet)
     * @param {number} deviceData.device_type_id - Device type ID (1=PicoVision, 2=PicoVision Express)
     * @param {Array} deviceData.cabinetConfiguration - Cabinet configuration array
     * @returns {Promise<Object>} Created device object
     */
    async createDevice(deviceData) {
        // Ensure proper data structure
        const device = {
            asset: deviceData.asset,
            cooler: deviceData.cooler,
            location_id: deviceData.location_id, // Use location_id instead of location
            model: deviceData.model,
            device_type_id: deviceData.device_type_id, // Use numeric ID
            cabinetConfiguration: deviceData.cabinetConfiguration || []
        };
        
        const result = await this.makeRequest('POST', '/devices', device);
        
        return result;
    }
    
    async updateDevice(deviceId, deviceData) {
        const result = await this.makeRequest('PUT', `/devices/${deviceId}`, deviceData);
        return result;
    }
    
    async deleteDevice(deviceId) {
        const result = await this.makeRequest('DELETE', `/devices/${deviceId}`);
        return result;
    }
    
    async bulkDeleteDevices(deviceIds) {
        const result = await this.makeRequest('POST', '/devices/bulk-delete', { deviceIds });
        return result;
    }
    
    // Planogram Management
    
    async getPlanogram(planogramKey) {
        const endpoint = `/planograms/${planogramKey}`;
        const planogram = await this.makeRequest('GET', endpoint);
        return planogram;
    }
    
    async savePlanogram(planogramKey, planogramData) {
        const result = await this.makeRequest('POST', '/planograms', {
            planogramKey,
            planogramData
        });
        return result;
    }
    
    async exportPlanograms() {
        return await this.makeRequest('GET', '/planograms/export');
    }
    
    // AI Planogram Optimization
    
    async getAIRecommendations(deviceId, cabinetIndex = 0) {
        return await this.makeRequest('POST', '/planograms/ai-suggestions', {
            device_id: deviceId,
            cabinet_index: cabinetIndex,
            optimization_type: 'full'
        });
    }
    
    async checkAIAvailable() {
        return await this.makeRequest('GET', '/planograms/ai-available');
    }
    
    // Data Migration
    
    async migrateData(devices, planograms) {
        return await this.makeRequest('POST', '/migrate', {
            devices,
            planograms
        });
    }
    
    // Product Management
    
    async getProducts(options = {}) {
        const { category } = options;
        let endpoint = '/products';
        
        if (category && category !== 'all') {
            endpoint += `?category=${encodeURIComponent(category)}`;
        }
        
        const products = await this.makeRequest('GET', endpoint);
        return products;
    }
    
    async getProduct(productId) {
        const endpoint = `/products/${productId}`;
        const product = await this.makeRequest('GET', endpoint);
        return product;
    }
    
    async getProductCategories() {
        const endpoint = '/products/categories';
        const categories = await this.makeRequest('GET', endpoint);
        return categories;
    }
    
    // Device Type Management
    
    async getDeviceTypes() {
        const endpoint = '/device-types';
        const deviceTypes = await this.makeRequest('GET', endpoint);
        return deviceTypes;
    }
    
    async createDeviceType(deviceTypeData) {
        const result = await this.makeRequest('POST', '/device-types', deviceTypeData);
        return result;
    }
    
    // Cabinet Type Management
    
    async getCabinetTypes() {
        const endpoint = '/cabinet-types';
        const cabinetTypes = await this.makeRequest('GET', endpoint);
        return cabinetTypes;
    }
    
    async createCabinetType(cabinetTypeData) {
        const result = await this.makeRequest('POST', '/cabinet-types', cabinetTypeData);
        return result;
    }
    
    // Location Management
    
    async getLocations() {
        const endpoint = '/locations';
        const locations = await this.makeRequest('GET', endpoint);
        return locations;
    }
    
    async createLocation(locationData) {
        const result = await this.makeRequest('POST', '/locations', locationData);
        return result;
    }
    
    // Sales Management
    
    /**
     * Get sales data with optional filtering
     * @param {Object} options - Filter options
     * @param {number} options.deviceId - Filter by device ID
     * @param {number} options.productId - Filter by product ID
     * @param {string} options.startDate - Filter by start date (ISO format)
     * @param {string} options.endDate - Filter by end date (ISO format)
     * @returns {Promise<Array>} Array of sale objects
     */
    async getSales(options = {}) {
        let endpoint = '/sales';
        const params = new URLSearchParams();
        
        if (options.deviceId) params.append('device_id', options.deviceId);
        if (options.productId) params.append('product_id', options.productId);
        if (options.startDate) params.append('start_date', options.startDate);
        if (options.endDate) params.append('end_date', options.endDate);
        
        const queryString = params.toString();
        if (queryString) endpoint += `?${queryString}`;
        
        const sales = await this.makeRequest('GET', endpoint);
        return sales;
    }
    
    /**
     * Create a new sale record
     * @param {Object} saleData - Sale data
     * @param {number} saleData.deviceId - Device ID
     * @param {number} saleData.productId - Product ID
     * @param {number} saleData.saleUnits - Number of units sold
     * @param {number} saleData.saleCash - Cash value of sold units
     * @returns {Promise<Object>} Created sale object
     */
    async createSale(saleData) {
        const result = await this.makeRequest('POST', '/sales', saleData);
        return result;
    }
    
    /**
     * Get sales summary aggregated by device, product, or date
     * @param {Object} options - Summary options
     * @param {string} options.groupBy - Grouping option: 'device', 'product', or 'date'
     * @param {string} options.startDate - Filter by start date (ISO format)
     * @param {string} options.endDate - Filter by end date (ISO format)
     * @returns {Promise<Array>} Array of summary objects
     */
    async getSalesSummary(options = {}) {
        let endpoint = '/sales/summary';
        const params = new URLSearchParams();
        
        if (options.groupBy) params.append('groupBy', options.groupBy);
        if (options.startDate) params.append('start_date', options.startDate);
        if (options.endDate) params.append('end_date', options.endDate);
        
        const queryString = params.toString();
        if (queryString) endpoint += `?${queryString}`;
        
        const summary = await this.makeRequest('GET', endpoint);
        return summary;
    }
    
    /**
     * Get asset sales report data
     * @param {Object} options - Report options
     * @param {string} options.startDate - Start date (ISO format)
     * @param {string} options.endDate - End date (ISO format)
     * @returns {Promise<Object>} Report data with devices and summary
     */
    async getAssetSalesReport(options = {}) {
        let endpoint = '/sales/asset-report';
        const params = new URLSearchParams();
        
        if (options.startDate) params.append('start_date', options.startDate);
        if (options.endDate) params.append('end_date', options.endDate);
        
        const queryString = params.toString();
        if (queryString) endpoint += `?${queryString}`;
        
        const report = await this.makeRequest('GET', endpoint);
        return report;
    }
    
    /**
     * Generate demo sales data
     * @param {Object} options - Generation options
     * @param {number} options.days - Number of days of data to generate
     * @param {number} options.devicesPerDay - Percentage of devices with sales per day
     * @param {boolean} options.clearExisting - Clear existing sales data
     * @returns {Promise<Object>} Generation result
     */
    async generateDemoSalesData(options = {}) {
        const result = await this.makeRequest('POST', '/sales/generate-demo-data', options);
        return result;
    }
    
    // Route Management
    
    async getRoutes() {
        const endpoint = '/routes';
        const routes = await this.makeRequest('GET', endpoint);
        return routes;
    }
    
    async createRoute(routeData) {
        const result = await this.makeRequest('POST', '/routes', routeData);
        return result;
    }
    
    async updateRoute(routeId, routeData) {
        const endpoint = `/routes/${routeId}`;
        const result = await this.makeRequest('PUT', endpoint, routeData);
        return result;
    }
    
    async deleteRoute(routeId) {
        const endpoint = `/routes/${routeId}`;
        const result = await this.makeRequest('DELETE', endpoint);
        return result;
    }
    
    async getRouteDevices(routeId) {
        const endpoint = `/routes/${routeId}/devices`;
        const result = await this.makeRequest('GET', endpoint);
        return result;
    }
    
    async assignDeviceToRoute(routeId, deviceId) {
        const endpoint = `/routes/${routeId}/assign-device`;
        const result = await this.makeRequest('POST', endpoint, { deviceId });
        return result;
    }
    
    async removeDeviceFromRoute(routeId, deviceId) {
        const endpoint = `/routes/${routeId}/remove-device?deviceId=${deviceId}`;
        const result = await this.makeRequest('DELETE', endpoint);
        return result;
    }
    
    // Generic GET method for compatibility
    async get(endpoint) {
        return await this.makeRequest('GET', endpoint);
    }
    
    // Generic POST method for compatibility  
    async post(endpoint, data = null) {
        return await this.makeRequest('POST', endpoint, data);
    }
    
    // Health Check
    
    async checkHealth() {
        try {
            const result = await this.makeRequest('GET', '/health');
            return { ...result, available: true };
        } catch (error) {
            return { available: false, error: error.message };
        }
    }
    
    // Dashboard Metrics API
    
    async getWeeklyMetrics() {
        return await this.makeRequest('GET', '/metrics/weekly');
    }
    
    async getGrowthTimeline() {
        return await this.makeRequest('GET', '/metrics/timeline');
    }
    
    async getAchievements() {
        return await this.makeRequest('GET', '/metrics/achievements');
    }
    
    async getTopPerformers() {
        return await this.makeRequest('GET', '/metrics/top-performers');
    }
    
    // Admin/Query methods
    async executeQuery(sql) {
        return await this.makeRequest('POST', '/query', { sql });
    }
    
    // Metrics methods
    async calculateMetrics(metrics) {
        return await this.makeRequest('POST', '/metrics/calculate', { metrics });
    }
    
    // DEX Parser methods
    async parseDexFile(formData) {
        // FormData requires special handling - cannot use makeRequest
        const response = await fetch(`${this.baseUrl}/dex/parse`, {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        
        // Read the response body once
        const responseText = await response.text();
        
        // Try to parse as JSON
        let responseData;
        try {
            responseData = JSON.parse(responseText);
        } catch (e) {
            // If not valid JSON, wrap in error object
            responseData = {
                success: false,
                error: {
                    message: responseText || `API error: ${response.status} ${response.statusText}`,
                    line: 0,
                    field: 0
                }
            };
        }
        
        if (!response.ok) {
            // Handle error response
            const errorMessage = responseData.error?.message || responseData.message || `API error: ${response.status} ${response.statusText}`;
            throw new Error(errorMessage);
        }
        
        return responseData;
    }
    
    async getDexPARecords(readId) {
        return await this.makeRequest('GET', `/dex/pa-records/${readId}`);
    }
    
    // Authentication methods
    async login(username, password) {
        return await this.makeRequest('POST', '/auth/login', { username, password });
    }
    
    async logout() {
        const result = await this.makeRequest('POST', '/auth/logout');
        localStorage.removeItem('user');
        window.location.href = '/pages/login.html';
        return result;
    }
    
    async getCurrentUser() {
        return await this.makeRequest('GET', '/auth/current-user');
    }
    
    async changePassword(currentPassword, newPassword) {
        return await this.makeRequest('POST', '/auth/change-password', {
            currentPassword,
            newPassword
        });
    }
    
    // User management methods
    async getUsers(params = {}) {
        let endpoint = '/users';
        if (Object.keys(params).length > 0) {
            const queryString = new URLSearchParams(params).toString();
            endpoint += `?${queryString}`;
        }
        return await this.makeRequest('GET', endpoint);
    }
    
    async createUser(userData) {
        return await this.makeRequest('POST', '/users', userData);
    }
    
    async updateUser(userId, userData) {
        return await this.makeRequest('PUT', `/users/${userId}`, userData);
    }
    
    async deleteUser(userId) {
        return await this.makeRequest('DELETE', `/users/${userId}`);
    }
    
    async resetUserPassword(userId) {
        return await this.makeRequest('POST', `/users/${userId}/reset-password`);
    }

    // User lifecycle management methods
    async deactivateUser(userId) {
        return await this.makeRequest('PUT', `/users/${userId}/deactivate`);
    }

    async activateUser(userId) {
        return await this.makeRequest('PUT', `/users/${userId}/activate`);
    }

    async softDeleteUser(userId) {
        return await this.makeRequest('DELETE', `/users/${userId}/soft-delete`);
    }

    async getUserServiceOrders(userId) {
        // This would need to be implemented on backend or we can check for service orders constraint
        // For now, we'll rely on the error response from the deactivate/delete endpoints
        return await this.makeRequest('GET', `/users/${userId}/service-orders`);
    }

    async getUserAuditTrail(userId) {
        return await this.makeRequest('GET', `/users/${userId}/audit-trail`);
    }

    async batchDeactivateUsers(userIds) {
        return await this.makeRequest('POST', '/users/batch-deactivate', { user_ids: userIds });
    }

    async getUserLifecycleMetrics() {
        return await this.makeRequest('GET', '/metrics/user-lifecycle');
    }
    
    async getUserActivity(userId, params = {}) {
        let endpoint = `/users/${userId}/activity`;
        if (Object.keys(params).length > 0) {
            const queryString = new URLSearchParams(params).toString();
            endpoint += `?${queryString}`;
        }
        return await this.makeRequest('GET', endpoint);
    }
    
    async updateProfile(profileData) {
        return await this.makeRequest('PUT', '/auth/update-profile', profileData);
    }
    
    async getCurrentUserActivity() {
        return await this.makeRequest('GET', '/auth/activity');
    }
    
    // Knowledge Base methods
    async getKnowledgeBaseArticles() {
        return await this.makeRequest('GET', '/knowledge-base/articles');
    }
    
    async getKnowledgeBaseArticle(articleId) {
        return await this.makeRequest('GET', `/knowledge-base/articles/${articleId}`);
    }
    
    async searchKnowledgeBase(query, category = null, difficulty = null) {
        const params = new URLSearchParams({ q: query });
        if (category) params.append('category', category);
        if (difficulty) params.append('difficulty', difficulty);
        return await this.makeRequest('GET', `/knowledge-base/search?${params}`);
    }
    
    async getKnowledgeBaseCategories() {
        return await this.makeRequest('GET', '/knowledge-base/categories');
    }
    
    async getKnowledgeBaseStats() {
        return await this.makeRequest('GET', '/knowledge-base/stats');
    }
}

// Create singleton instance
const cvdApi = new CVDApi();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = cvdApi;
}