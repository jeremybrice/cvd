/**
 * CVD User Preferences Manager
 * P2 Medium Priority - Foundation Component 1
 * 
 * Centralized preference management system with categories:
 * - UI preferences (theme, layout, notifications)
 * - Notification preferences (types, frequency, delivery)
 * - Data preferences (cache, refresh intervals, display)
 */

class UserPreferencesManager {
    constructor() {
        this.preferences = {};
        this.subscribers = new Map();
        this.storageKey = 'cvd_user_preferences';
        this.defaultPreferences = this.getDefaultPreferences();
        
        this.init();
    }

    getDefaultPreferences() {
        return {
            ui: {
                theme: 'light',
                sidebarCollapsed: false,
                showBreadcrumbs: true,
                showTooltips: true,
                animationsEnabled: !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
                compactMode: false,
                gridDensity: 'comfortable', // comfortable, compact, spacious
                showIcons: true,
                fontSize: 'base' // xs, sm, base, lg, xl
            },
            notifications: {
                showToasts: true,
                toastDuration: 5000,
                soundEnabled: false,
                showDesktop: true,
                emailDigest: 'daily', // off, daily, weekly
                serviceOrderAlerts: true,
                deviceStatusAlerts: true,
                lowInventoryAlerts: true,
                systemMaintenanceAlerts: true,
                position: 'top-right' // top-left, top-right, bottom-left, bottom-right
            },
            data: {
                autoRefresh: true,
                refreshInterval: 300000, // 5 minutes
                cacheEnabled: true,
                cacheTimeout: 900000, // 15 minutes
                preloadData: true,
                maxHistoryItems: 50,
                dateFormat: 'MM/DD/YYYY',
                timeFormat: '12h', // 12h, 24h
                currency: 'USD',
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            },
            accessibility: {
                highContrast: false,
                reduceMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
                screenReaderAnnouncements: true,
                keyboardNavigation: true,
                focusIndicators: 'enhanced' // minimal, standard, enhanced
            },
            performance: {
                enablePerformanceMonitoring: true,
                trackPageLoadTimes: true,
                trackApiResponseTimes: true,
                memoryMonitoring: false, // Off by default for performance
                showPerformanceIndicators: true,
                performanceAlerts: false
            }
        };
    }

    async init() {
        await this.loadPreferences();
        this.setupEventListeners();
        this.applyPreferences();
        console.log('UserPreferencesManager initialized');
    }

    async loadPreferences() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                const parsed = JSON.parse(stored);
                // Merge with defaults to ensure all new preferences are available
                this.preferences = this.mergePreferences(this.defaultPreferences, parsed);
            } else {
                this.preferences = { ...this.defaultPreferences };
            }
        } catch (error) {
            console.error('Error loading preferences:', error);
            this.preferences = { ...this.defaultPreferences };
        }
    }

    mergePreferences(defaults, stored) {
        const merged = {};
        
        for (const [category, categoryDefaults] of Object.entries(defaults)) {
            merged[category] = {
                ...categoryDefaults,
                ...(stored[category] || {})
            };
        }
        
        return merged;
    }

    async savePreferences() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.preferences));
            
            // Also sync to server for cross-device preferences
            if (window.currentUser) {
                await this.syncToServer();
            }
            
            this.notifySubscribers('preferences_saved', this.preferences);
        } catch (error) {
            console.error('Error saving preferences:', error);
        }
    }

    async syncToServer() {
        try {
            // Only sync if we have an API instance
            if (typeof CVDApi !== 'undefined') {
                const api = new CVDApi();
                await api.makeRequest('PUT', '/user/preferences', {
                    preferences: this.preferences
                });
            }
        } catch (error) {
            console.log('Server sync failed, continuing with local storage:', error);
        }
    }

    get(category, key = null) {
        if (!this.preferences[category]) {
            return null;
        }
        
        return key ? this.preferences[category][key] : this.preferences[category];
    }

    set(category, key, value) {
        if (!this.preferences[category]) {
            this.preferences[category] = {};
        }
        
        const oldValue = this.preferences[category][key];
        this.preferences[category][key] = value;
        
        // Apply the change immediately
        this.applySpecificPreference(category, key, value);
        
        // Save preferences
        this.savePreferences();
        
        // Notify subscribers
        this.notifySubscribers('preference_changed', {
            category,
            key,
            value,
            oldValue
        });
    }

    setCategory(category, values) {
        this.preferences[category] = {
            ...this.preferences[category],
            ...values
        };
        
        this.applyPreferencesForCategory(category);
        this.savePreferences();
        
        this.notifySubscribers('category_changed', {
            category,
            values
        });
    }

    reset(category = null) {
        if (category) {
            this.preferences[category] = { ...this.defaultPreferences[category] };
            this.applyPreferencesForCategory(category);
        } else {
            this.preferences = { ...this.defaultPreferences };
            this.applyPreferences();
        }
        
        this.savePreferences();
        this.notifySubscribers('preferences_reset', { category });
    }

    subscribe(event, callback) {
        if (!this.subscribers.has(event)) {
            this.subscribers.set(event, []);
        }
        this.subscribers.get(event).push(callback);
        
        // Return unsubscribe function
        return () => {
            const callbacks = this.subscribers.get(event);
            if (callbacks) {
                const index = callbacks.indexOf(callback);
                if (index > -1) {
                    callbacks.splice(index, 1);
                }
            }
        };
    }

    notifySubscribers(event, data) {
        const callbacks = this.subscribers.get(event);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in preference subscriber:', error);
                }
            });
        }
    }

    applyPreferences() {
        // Apply all preference categories
        Object.keys(this.preferences).forEach(category => {
            this.applyPreferencesForCategory(category);
        });
    }

    applyPreferencesForCategory(category) {
        switch (category) {
            case 'ui':
                this.applyUIPreferences();
                break;
            case 'notifications':
                this.applyNotificationPreferences();
                break;
            case 'accessibility':
                this.applyAccessibilityPreferences();
                break;
            case 'performance':
                this.applyPerformancePreferences();
                break;
        }
    }

    applySpecificPreference(category, key, value) {
        const method = `apply${category.charAt(0).toUpperCase() + category.slice(1)}${key.charAt(0).toUpperCase() + key.slice(1)}`;
        
        if (typeof this[method] === 'function') {
            this[method](value);
        } else {
            // Fallback to category-wide application
            this.applyPreferencesForCategory(category);
        }
    }

    applyUIPreferences() {
        const ui = this.preferences.ui;
        
        // Font size
        document.documentElement.classList.remove('font-xs', 'font-sm', 'font-base', 'font-lg', 'font-xl');
        document.documentElement.classList.add(`font-${ui.fontSize}`);
        
        // Compact mode
        document.documentElement.classList.toggle('compact-mode', ui.compactMode);
        
        // Grid density
        document.documentElement.setAttribute('data-grid-density', ui.gridDensity);
        
        // Icons visibility
        document.documentElement.classList.toggle('hide-icons', !ui.showIcons);
        
        // Animations
        if (!ui.animationsEnabled) {
            document.documentElement.style.setProperty('--duration-fast', '0ms');
            document.documentElement.style.setProperty('--duration-base', '0ms');
            document.documentElement.style.setProperty('--duration-slow', '0ms');
        } else {
            document.documentElement.style.removeProperty('--duration-fast');
            document.documentElement.style.removeProperty('--duration-base');
            document.documentElement.style.removeProperty('--duration-slow');
        }
    }

    applyNotificationPreferences() {
        const notifications = this.preferences.notifications;
        
        // Configure toast system if available
        if (window.ToastManager) {
            window.ToastManager.defaultDuration = notifications.toastDuration;
            window.ToastManager.soundEnabled = notifications.soundEnabled;
            window.ToastManager.position = notifications.position;
        }
    }

    applyAccessibilityPreferences() {
        const accessibility = this.preferences.accessibility;
        
        // High contrast
        document.documentElement.classList.toggle('high-contrast', accessibility.highContrast);
        
        // Reduced motion
        if (accessibility.reduceMotion) {
            document.documentElement.style.setProperty('--duration-instant', '0ms');
            document.documentElement.style.setProperty('--duration-fast', '0ms');
            document.documentElement.style.setProperty('--duration-base', '0ms');
        }
        
        // Focus indicators
        document.documentElement.setAttribute('data-focus-style', accessibility.focusIndicators);
    }

    applyPerformancePreferences() {
        const performance = this.preferences.performance;
        
        // Enable/disable performance monitoring
        if (window.PerformanceMonitor && performance.enablePerformanceMonitoring) {
            window.PerformanceMonitor.enable({
                trackPageLoadTimes: performance.trackPageLoadTimes,
                trackApiResponseTimes: performance.trackApiResponseTimes,
                memoryMonitoring: performance.memoryMonitoring,
                showIndicators: performance.showPerformanceIndicators,
                enableAlerts: performance.performanceAlerts
            });
        }
    }

    setupEventListeners() {
        // Listen for system theme changes
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
            mediaQuery.addEventListener('change', (e) => {
                if (this.get('accessibility', 'reduceMotion') === 'system') {
                    this.set('accessibility', 'reduceMotion', e.matches);
                }
            });
        }
    }

    // Export/Import functionality
    export() {
        return {
            version: '1.0',
            timestamp: new Date().toISOString(),
            preferences: this.preferences
        };
    }

    import(exportedData) {
        try {
            if (exportedData.version && exportedData.preferences) {
                this.preferences = this.mergePreferences(
                    this.defaultPreferences, 
                    exportedData.preferences
                );
                this.applyPreferences();
                this.savePreferences();
                
                this.notifySubscribers('preferences_imported', exportedData);
                return true;
            }
        } catch (error) {
            console.error('Error importing preferences:', error);
        }
        return false;
    }

    // Utility methods for common preference checks
    isAnimationsEnabled() {
        return this.get('ui', 'animationsEnabled');
    }

    getToastDuration() {
        return this.get('notifications', 'toastDuration');
    }

    shouldShowToasts() {
        return this.get('notifications', 'showToasts');
    }

    getRefreshInterval() {
        return this.get('data', 'refreshInterval');
    }

    isAutoRefreshEnabled() {
        return this.get('data', 'autoRefresh');
    }

    getDateFormat() {
        return this.get('data', 'dateFormat');
    }

    getTimeFormat() {
        return this.get('data', 'timeFormat');
    }

    // Preference validation
    validatePreference(category, key, value) {
        const validators = {
            ui: {
                theme: (v) => ['light', 'dark', 'auto'].includes(v),
                fontSize: (v) => ['xs', 'sm', 'base', 'lg', 'xl'].includes(v),
                gridDensity: (v) => ['comfortable', 'compact', 'spacious'].includes(v)
            },
            notifications: {
                toastDuration: (v) => typeof v === 'number' && v >= 1000 && v <= 30000,
                emailDigest: (v) => ['off', 'daily', 'weekly'].includes(v),
                position: (v) => ['top-left', 'top-right', 'bottom-left', 'bottom-right'].includes(v)
            },
            data: {
                refreshInterval: (v) => typeof v === 'number' && v >= 30000, // Min 30 seconds
                cacheTimeout: (v) => typeof v === 'number' && v >= 60000, // Min 1 minute
                timeFormat: (v) => ['12h', '24h'].includes(v)
            }
        };

        const categoryValidators = validators[category];
        if (categoryValidators && categoryValidators[key]) {
            return categoryValidators[key](value);
        }
        
        return true; // Allow unknown preferences
    }

    // UI Builder for preferences
    createPreferencesUI() {
        const container = document.createElement('div');
        container.className = 'preferences-ui';
        container.innerHTML = `
            <div class="preferences-header">
                <h2>User Preferences</h2>
                <div class="preferences-actions">
                    <button class="btn btn-secondary" data-action="export">Export</button>
                    <button class="btn btn-secondary" data-action="import">Import</button>
                    <button class="btn btn-warning" data-action="reset">Reset All</button>
                </div>
            </div>
            <div class="preferences-content">
                ${this.createCategoryTabs()}
                ${this.createCategoryPanels()}
            </div>
        `;

        this.attachUIEventListeners(container);
        return container;
    }

    createCategoryTabs() {
        const categories = Object.keys(this.defaultPreferences);
        const tabsHTML = categories.map((category, index) => {
            const displayName = category.charAt(0).toUpperCase() + category.slice(1);
            const isActive = index === 0 ? 'active' : '';
            return `<button class="tab-button ${isActive}" data-category="${category}">${displayName}</button>`;
        }).join('');

        return `<div class="preferences-tabs">${tabsHTML}</div>`;
    }

    createCategoryPanels() {
        const categories = Object.keys(this.defaultPreferences);
        return categories.map((category, index) => {
            const isActive = index === 0 ? 'active' : '';
            return `
                <div class="tab-panel ${isActive}" data-category="${category}">
                    ${this.createCategoryForm(category)}
                </div>
            `;
        }).join('');
    }

    createCategoryForm(category) {
        const preferences = this.preferences[category];
        const fields = Object.entries(preferences).map(([key, value]) => {
            return this.createFormField(category, key, value);
        }).join('');

        return `<form class="preferences-form" data-category="${category}">${fields}</form>`;
    }

    createFormField(category, key, value) {
        const fieldType = this.getFieldType(category, key, value);
        const label = this.formatLabel(key);
        const fieldId = `${category}_${key}`;

        switch (fieldType) {
            case 'boolean':
                return `
                    <div class="form-field">
                        <label class="checkbox-label">
                            <input type="checkbox" id="${fieldId}" ${value ? 'checked' : ''} 
                                   data-category="${category}" data-key="${key}">
                            ${label}
                        </label>
                    </div>
                `;
            case 'select':
                const options = this.getSelectOptions(category, key);
                const optionsHTML = options.map(option => 
                    `<option value="${option}" ${value === option ? 'selected' : ''}>${option}</option>`
                ).join('');
                return `
                    <div class="form-field">
                        <label for="${fieldId}">${label}</label>
                        <select id="${fieldId}" data-category="${category}" data-key="${key}">
                            ${optionsHTML}
                        </select>
                    </div>
                `;
            case 'number':
                return `
                    <div class="form-field">
                        <label for="${fieldId}">${label}</label>
                        <input type="number" id="${fieldId}" value="${value}" 
                               data-category="${category}" data-key="${key}"
                               min="${this.getNumberMin(category, key)}"
                               max="${this.getNumberMax(category, key)}">
                    </div>
                `;
            default:
                return `
                    <div class="form-field">
                        <label for="${fieldId}">${label}</label>
                        <input type="text" id="${fieldId}" value="${value}" 
                               data-category="${category}" data-key="${key}">
                    </div>
                `;
        }
    }

    getFieldType(category, key, value) {
        if (typeof value === 'boolean') return 'boolean';
        if (typeof value === 'number') return 'number';
        
        // Specific field types based on key names
        const selectFields = {
            theme: ['light', 'dark', 'auto'],
            fontSize: ['xs', 'sm', 'base', 'lg', 'xl'],
            gridDensity: ['comfortable', 'compact', 'spacious'],
            emailDigest: ['off', 'daily', 'weekly'],
            position: ['top-left', 'top-right', 'bottom-left', 'bottom-right'],
            timeFormat: ['12h', '24h'],
            focusIndicators: ['minimal', 'standard', 'enhanced']
        };

        if (selectFields[key]) return 'select';
        return 'text';
    }

    getSelectOptions(category, key) {
        const selectFields = {
            theme: ['light', 'dark', 'auto'],
            fontSize: ['xs', 'sm', 'base', 'lg', 'xl'],
            gridDensity: ['comfortable', 'compact', 'spacious'],
            emailDigest: ['off', 'daily', 'weekly'],
            position: ['top-left', 'top-right', 'bottom-left', 'bottom-right'],
            timeFormat: ['12h', '24h'],
            focusIndicators: ['minimal', 'standard', 'enhanced']
        };

        return selectFields[key] || [];
    }

    getNumberMin(category, key) {
        const mins = {
            toastDuration: 1000,
            refreshInterval: 30000,
            cacheTimeout: 60000,
            maxHistoryItems: 10
        };
        return mins[key] || 0;
    }

    getNumberMax(category, key) {
        const maxs = {
            toastDuration: 30000,
            refreshInterval: 3600000, // 1 hour
            cacheTimeout: 86400000, // 24 hours
            maxHistoryItems: 200
        };
        return maxs[key] || 999999;
    }

    formatLabel(key) {
        return key
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, str => str.toUpperCase())
            .trim();
    }

    attachUIEventListeners(container) {
        // Tab switching
        container.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const category = e.target.dataset.category;
                this.switchToTab(container, category);
            });
        });

        // Form field changes
        container.addEventListener('change', (e) => {
            const target = e.target;
            if (target.dataset.category && target.dataset.key) {
                const category = target.dataset.category;
                const key = target.dataset.key;
                const value = target.type === 'checkbox' ? target.checked : 
                             target.type === 'number' ? Number(target.value) : target.value;
                
                if (this.validatePreference(category, key, value)) {
                    this.set(category, key, value);
                } else {
                    // Revert to previous value
                    target.value = this.get(category, key);
                    if (window.ToastManager) {
                        window.ToastManager.show('error', 'Invalid preference value');
                    }
                }
            }
        });

        // Action buttons
        container.addEventListener('click', (e) => {
            if (e.target.dataset.action) {
                switch (e.target.dataset.action) {
                    case 'export':
                        this.handleExport();
                        break;
                    case 'import':
                        this.handleImport();
                        break;
                    case 'reset':
                        if (confirm('Reset all preferences to defaults?')) {
                            this.reset();
                            // Rebuild UI
                            const newUI = this.createPreferencesUI();
                            container.replaceWith(newUI);
                        }
                        break;
                }
            }
        });
    }

    switchToTab(container, category) {
        // Update tab buttons
        container.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.category === category);
        });

        // Update panels
        container.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.toggle('active', panel.dataset.category === category);
        });
    }

    handleExport() {
        const exportData = this.export();
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cvd-preferences-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        if (window.ToastManager) {
            window.ToastManager.show('success', 'Preferences exported successfully');
        }
    }

    handleImport() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const importData = JSON.parse(e.target.result);
                        if (this.import(importData)) {
                            if (window.ToastManager) {
                                window.ToastManager.show('success', 'Preferences imported successfully');
                            }
                            // Reload page to apply all changes
                            window.location.reload();
                        } else {
                            if (window.ToastManager) {
                                window.ToastManager.show('error', 'Invalid preferences file');
                            }
                        }
                    } catch (error) {
                        console.error('Import error:', error);
                        if (window.ToastManager) {
                            window.ToastManager.show('error', 'Failed to parse preferences file');
                        }
                    }
                };
                reader.readAsText(file);
            }
        });
        input.click();
    }
}

// Initialize global instance
window.UserPreferences = new UserPreferencesManager();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserPreferencesManager;
}