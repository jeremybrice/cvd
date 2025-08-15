/**
 * CVD Enhanced Search System
 * P2 Medium Priority - Navigation Enhancement Component 2
 * 
 * Global search functionality with:
 * - Multi-source search (devices, products, orders, users)
 * - Auto-complete with intelligent suggestions
 * - Search history tracking and persistence
 * - Advanced filters and sorting options
 * - Keyboard shortcuts and accessibility
 */

class EnhancedSearchSystem {
    constructor() {
        this.searchHistory = [];
        this.searchCache = new Map();
        this.searchProviders = new Map();
        this.filters = new Map();
        this.isSearching = false;
        this.currentQuery = '';
        
        this.searchContainer = null;
        this.searchInput = null;
        this.searchResults = null;
        this.searchOverlay = null;
        
        this.debounceTimer = null;
        this.cacheTimeout = 300000; // 5 minutes
        this.maxHistoryItems = 50;
        this.maxCacheItems = 100;
        
        this.init();
    }

    async init() {
        this.setupSearchProviders();
        this.createSearchInterface();
        this.setupEventListeners();
        this.loadSearchHistory();
        this.setupKeyboardShortcuts();
        
        console.log('EnhancedSearchSystem initialized');
    }

    setupSearchProviders() {
        // Register built-in search providers
        this.registerProvider('devices', {
            name: 'Devices',
            icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/></svg>',
            placeholder: 'Search devices by name, location, or type...',
            searchFunction: this.searchDevices.bind(this),
            priority: 10
        });
        
        this.registerProvider('products', {
            name: 'Products',
            icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="m2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57L22.38 9H5.12"/></svg>',
            placeholder: 'Search products by name or category...',
            searchFunction: this.searchProducts.bind(this),
            priority: 8
        });
        
        this.registerProvider('orders', {
            name: 'Service Orders',
            icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg>',
            placeholder: 'Search orders by ID, device, or status...',
            searchFunction: this.searchOrders.bind(this),
            priority: 9
        });
        
        this.registerProvider('users', {
            name: 'Users',
            icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="m22 21-3-3m0 0a5 5 0 1 0-7-7 5 5 0 0 0 7 7Z"/></svg>',
            placeholder: 'Search users by name, email, or role...',
            searchFunction: this.searchUsers.bind(this),
            priority: 5,
            adminOnly: true
        });
        
        this.registerProvider('pages', {
            name: 'Pages',
            icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14,2 14,8 20,8"/></svg>',
            placeholder: 'Search application pages...',
            searchFunction: this.searchPages.bind(this),
            priority: 6
        });
    }

    registerProvider(id, provider) {
        this.searchProviders.set(id, {
            id,
            enabled: true,
            ...provider
        });
    }

    createSearchInterface() {
        console.log('EnhancedSearchSystem: Creating search interface');
        
        // Create search container (modal only, no navbar trigger)
        this.searchContainer = document.createElement('div');
        this.searchContainer.className = 'enhanced-search-container';
        this.searchContainer.innerHTML = this.generateSearchHTML();
        
        // Add to body (modal overlay only)
        document.body.appendChild(this.searchContainer);
        
        // Cache elements
        this.searchInput = this.searchContainer.querySelector('.search-input');
        this.searchResults = this.searchContainer.querySelector('.search-results');
        this.searchOverlay = this.searchContainer.querySelector('.search-overlay');
        
        // Add styles
        this.addSearchStyles();
        
        console.log('EnhancedSearchSystem: Search interface created successfully (modal only)');
    }

    generateSearchHTML() {
        return `
            <div class="search-overlay">
                <div class="search-modal">
                    <div class="search-header">
                        <div class="search-input-container">
                            <span class="search-input-icon">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                                </svg>
                            </span>
                            <input type="text" 
                                   class="search-input" 
                                   placeholder="Search across all data..."
                                   autocomplete="off"
                                   spellcheck="false">
                            <button class="search-close" aria-label="Close search">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                    <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
                                </svg>
                            </button>
                        </div>
                        
                        <div class="search-filters">
                            <div class="search-filter-tabs">
                                <button class="filter-tab active" data-provider="all">
                                    <span class="tab-icon">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                                        </svg>
                                    </span>
                                    <span class="tab-label">All</span>
                                </button>
                                ${this.generateFilterTabs()}
                            </div>
                        </div>
                    </div>
                    
                    <div class="search-content">
                        <div class="search-results">
                            ${this.generateEmptyState()}
                        </div>
                    </div>
                    
                    <div class="search-footer">
                        <div class="search-shortcuts">
                            <span class="shortcut-item"><kbd>↑</kbd><kbd>↓</kbd> Navigate</span>
                            <span class="shortcut-item"><kbd>Enter</kbd> Select</span>
                            <span class="shortcut-item"><kbd>Esc</kbd> Close</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    generateFilterTabs() {
        const providers = Array.from(this.searchProviders.values())
            .filter(provider => !provider.adminOnly || (window.currentUser && window.currentUser.role === 'admin'))
            .sort((a, b) => b.priority - a.priority);
        
        return providers.map(provider => `
            <button class="filter-tab" data-provider="${provider.id}">
                <span class="tab-icon">${provider.icon}</span>
                <span class="tab-label">${provider.name}</span>
            </button>
        `).join('');
    }

    generateEmptyState() {
        return `
            <div class="search-empty-state">
                <div class="empty-icon">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                    </svg>
                </div>
                <div class="empty-title">Search Everything</div>
                <div class="empty-description">
                    Find devices, products, orders, users, and more across your entire system.
                </div>
                ${this.generateRecentSearches()}
            </div>
        `;
    }

    generateRecentSearches() {
        if (this.searchHistory.length === 0) {
            return '';
        }

        return `
            <div class="recent-searches">
                <div class="recent-searches-header">Recent searches</div>
                <div class="recent-searches-list">
                    ${this.searchHistory.slice(0, 5).map(search => `
                        <button class="recent-search-item" data-query="${search.query}" data-provider="${search.provider}">
                            <span class="recent-icon">${search.provider === 'all' ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>' : this.searchProviders.get(search.provider)?.icon || '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>'}</span>
                            <span class="recent-query">${search.query}</span>
                            <span class="recent-time">${this.formatRelativeTime(search.timestamp)}</span>
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
    }

    addSearchStyles() {
        if (document.getElementById('enhanced-search-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'enhanced-search-styles';
        style.textContent = `
            .enhanced-search-container {
                position: relative;
            }
            
            .search-overlay {
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.5);
                z-index: var(--z-modal);
                display: none;
                opacity: 0;
                visibility: hidden;
                transition: opacity var(--duration-base), visibility var(--duration-base);
                align-items: flex-start;
                justify-content: center;
                padding-top: 10vh;
            }
            
            .search-overlay.active {
                display: flex;
                opacity: 1;
                visibility: visible;
            }
            
            .search-modal {
                background: var(--color-neutral-0);
                border-radius: var(--radius-xl);
                box-shadow: var(--shadow-2xl);
                width: 90vw;
                max-width: 700px;
                max-height: 80vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                transform: scale(0.95) translateY(-20px);
                transition: transform var(--duration-base);
            }
            
            .search-overlay.active .search-modal {
                transform: scale(1) translateY(0);
            }
            
            .search-header {
                border-bottom: 1px solid var(--color-neutral-200);
                padding: var(--space-lg);
                padding-bottom: 0;
            }
            
            .search-input-container {
                position: relative;
                display: flex;
                align-items: center;
                gap: var(--space-sm);
                margin-bottom: var(--space-md);
            }
            
            .search-input-icon {
                position: absolute;
                left: var(--space-md);
                color: var(--color-neutral-400);
                pointer-events: none;
                z-index: 1;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .search-input-icon svg {
                width: 16px;
                height: 16px;
            }
            
            .search-input {
                flex: 1;
                padding: var(--space-md) var(--space-lg);
                padding-left: 48px;
                font-size: var(--text-lg);
                border: 2px solid var(--color-neutral-200);
                border-radius: var(--radius-lg);
                outline: none;
                transition: border-color var(--duration-fast);
                background: var(--color-neutral-0);
            }
            
            .search-input:focus {
                border-color: var(--color-primary-500);
            }
            
            .search-close {
                position: absolute;
                right: var(--space-md);
                background: none;
                border: none;
                color: var(--color-neutral-400);
                cursor: pointer;
                padding: var(--space-xs);
                border-radius: var(--radius-md);
                transition: all var(--duration-fast);
                z-index: 1;
            }
            
            .search-close:hover {
                background: var(--color-neutral-100);
                color: var(--color-neutral-600);
            }
            
            .search-filters {
                margin-bottom: var(--space-lg);
            }
            
            .search-filter-tabs {
                display: flex;
                gap: var(--space-xs);
                overflow-x: auto;
                padding-bottom: var(--space-xs);
            }
            
            .filter-tab {
                display: flex;
                align-items: center;
                gap: var(--space-xs);
                padding: var(--space-sm) var(--space-md);
                background: var(--color-neutral-100);
                border: 1px solid var(--color-neutral-200);
                border-radius: var(--radius-md);
                cursor: pointer;
                transition: all var(--duration-fast);
                font-size: var(--text-sm);
                white-space: nowrap;
                flex-shrink: 0;
            }
            
            .filter-tab:hover {
                background: var(--color-neutral-50);
                border-color: var(--color-neutral-300);
            }
            
            .filter-tab.active {
                background: var(--color-primary-100);
                border-color: var(--color-primary-300);
                color: var(--color-primary-700);
            }
            
            .tab-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
            }
            
            .tab-icon svg {
                width: 16px;
                height: 16px;
            }
            
            .search-content {
                flex: 1;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }
            
            .search-results {
                flex: 1;
                overflow-y: auto;
                padding: var(--space-lg);
            }
            
            .search-empty-state {
                text-align: center;
                padding: var(--space-xxl) var(--space-lg);
            }
            
            .empty-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 64px;
                opacity: 0.3;
                margin-bottom: var(--space-lg);
            }
            
            .empty-icon svg {
                width: 64px;
                height: 64px;
                color: var(--color-neutral-400);
            }
            
            .empty-title {
                font-size: var(--text-xl);
                font-weight: var(--font-semibold);
                color: var(--color-neutral-800);
                margin-bottom: var(--space-sm);
            }
            
            .empty-description {
                font-size: var(--text-base);
                color: var(--color-neutral-600);
                max-width: 400px;
                margin: 0 auto var(--space-lg);
            }
            
            .recent-searches {
                text-align: left;
                max-width: 400px;
                margin: 0 auto;
            }
            
            .recent-searches-header {
                font-size: var(--text-sm);
                font-weight: var(--font-semibold);
                color: var(--color-neutral-700);
                margin-bottom: var(--space-sm);
                padding-left: var(--space-sm);
            }
            
            .recent-search-item {
                width: 100%;
                display: flex;
                align-items: center;
                gap: var(--space-sm);
                padding: var(--space-sm);
                background: none;
                border: none;
                border-radius: var(--radius-md);
                cursor: pointer;
                transition: background var(--duration-fast);
                text-align: left;
            }
            
            .recent-search-item:hover {
                background: var(--color-neutral-50);
            }
            
            .recent-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                width: 20px;
                opacity: 0.7;
            }
            
            .recent-icon svg {
                width: 14px;
                height: 14px;
            }
            
            .recent-query {
                flex: 1;
                color: var(--color-neutral-700);
                font-size: var(--text-sm);
            }
            
            .recent-time {
                font-size: var(--text-xs);
                color: var(--color-neutral-500);
                font-family: var(--font-mono);
            }
            
            .search-loading {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: var(--space-xl);
                color: var(--color-neutral-500);
                font-size: var(--text-sm);
            }
            
            .search-no-results {
                text-align: center;
                padding: var(--space-xl);
                color: var(--color-neutral-500);
            }
            
            .search-results-list {
                display: flex;
                flex-direction: column;
                gap: var(--space-sm);
            }
            
            .search-result-group {
                margin-bottom: var(--space-lg);
            }
            
            .search-result-group-header {
                display: flex;
                align-items: center;
                gap: var(--space-sm);
                margin-bottom: var(--space-sm);
                padding-bottom: var(--space-xs);
                border-bottom: 1px solid var(--color-neutral-200);
            }
            
            .group-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: var(--text-base);
            }
            
            .group-icon svg {
                width: 16px;
                height: 16px;
            }
            
            .group-title {
                font-size: var(--text-sm);
                font-weight: var(--font-semibold);
                color: var(--color-neutral-700);
            }
            
            .group-count {
                font-size: var(--text-xs);
                color: var(--color-neutral-500);
                background: var(--color-neutral-100);
                padding: 2px 6px;
                border-radius: var(--radius-sm);
            }
            
            .search-result-item {
                display: flex;
                align-items: center;
                gap: var(--space-md);
                padding: var(--space-md);
                border-radius: var(--radius-md);
                cursor: pointer;
                transition: background var(--duration-fast);
                border: 1px solid transparent;
            }
            
            .search-result-item:hover,
            .search-result-item.selected {
                background: var(--color-neutral-50);
                border-color: var(--color-neutral-200);
            }
            
            .search-result-item.selected {
                background: var(--color-primary-50);
                border-color: var(--color-primary-200);
            }
            
            .result-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: var(--text-lg);
                width: 24px;
                flex-shrink: 0;
            }
            
            .result-icon svg {
                width: 18px;
                height: 18px;
            }
            
            .result-content {
                flex: 1;
                min-width: 0;
            }
            
            .result-title {
                font-size: var(--text-base);
                font-weight: var(--font-medium);
                color: var(--color-neutral-800);
                margin-bottom: 2px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            .result-description {
                font-size: var(--text-sm);
                color: var(--color-neutral-600);
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            .result-meta {
                display: flex;
                flex-direction: column;
                align-items: flex-end;
                gap: 2px;
                flex-shrink: 0;
            }
            
            .result-type {
                font-size: var(--text-xs);
                color: var(--color-neutral-500);
                background: var(--color-neutral-100);
                padding: 2px 6px;
                border-radius: var(--radius-sm);
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .result-action {
                font-size: var(--text-xs);
                color: var(--color-primary-600);
                opacity: 0;
                transition: opacity var(--duration-fast);
            }
            
            .search-result-item:hover .result-action,
            .search-result-item.selected .result-action {
                opacity: 1;
            }
            
            .search-footer {
                border-top: 1px solid var(--color-neutral-200);
                padding: var(--space-md) var(--space-lg);
                background: var(--color-neutral-50);
            }
            
            .search-shortcuts {
                display: flex;
                gap: var(--space-lg);
                justify-content: center;
            }
            
            .shortcut-item {
                display: flex;
                align-items: center;
                gap: var(--space-xs);
                font-size: var(--text-xs);
                color: var(--color-neutral-600);
            }
            
            .shortcut-item kbd {
                background: var(--color-neutral-200);
                border: 1px solid var(--color-neutral-300);
                border-radius: var(--radius-sm);
                padding: 2px 6px;
                font-size: var(--text-xs);
                font-family: inherit;
            }
            
            /* Highlight matched text */
            .search-highlight {
                background: var(--color-warning);
                color: var(--color-warning-text);
                padding: 1px 2px;
                border-radius: 2px;
                font-weight: var(--font-medium);
            }
            
            /* Mobile responsive */
            @media (max-width: 768px) {
                .search-modal {
                    width: 95vw;
                    margin-top: 5vh;
                }
                
                .search-filter-tabs {
                    flex-wrap: wrap;
                }
            }
        `;
        
        document.head.appendChild(style);
    }

    setupEventListeners() {
        // Search input
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearchInput(e.target.value);
        });

        // Close button
        const closeBtn = this.searchContainer.querySelector('.search-close');
        closeBtn.addEventListener('click', () => this.closeSearch());

        // Overlay click to close
        this.searchOverlay.addEventListener('click', (e) => {
            if (e.target === this.searchOverlay) {
                this.closeSearch();
            }
        });

        // Filter tabs
        const filterTabs = this.searchContainer.querySelectorAll('.filter-tab');
        filterTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const provider = e.currentTarget.dataset.provider;
                this.setActiveProvider(provider);
            });
        });

        // Keyboard navigation in search results
        this.searchInput.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });

        // Recent searches
        this.searchResults.addEventListener('click', (e) => {
            const recentItem = e.target.closest('.recent-search-item');
            if (recentItem) {
                const query = recentItem.dataset.query;
                const provider = recentItem.dataset.provider;
                this.performSearch(query, provider);
            }
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+/ or Cmd+/ to open search
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                e.preventDefault();
                this.openSearch();
            }
            
            // Escape to close search
            if (e.key === 'Escape' && this.isSearchOpen()) {
                this.closeSearch();
            }
        });
    }

    openSearch() {
        this.searchOverlay.classList.add('active');
        // Body overflow is now permanently hidden via CSS
        
        // Focus input after animation
        setTimeout(() => {
            this.searchInput.focus();
        }, 100);
        
        // Update recent searches
        this.updateEmptyState();
    }

    closeSearch() {
        this.searchOverlay.classList.remove('active');
        // Body overflow is now permanently hidden via CSS
        
        // Clear input and results
        this.searchInput.value = '';
        this.currentQuery = '';
        this.clearSearch();
    }

    isSearchOpen() {
        return this.searchOverlay.classList.contains('active');
    }

    handleSearchInput(query) {
        this.currentQuery = query.trim();
        
        // Clear previous timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        if (this.currentQuery === '') {
            this.clearSearch();
            this.updateEmptyState();
            return;
        }
        
        // Debounce search
        this.debounceTimer = setTimeout(() => {
            this.performSearch(this.currentQuery);
        }, 300);
    }

    async performSearch(query, specificProvider = null) {
        if (!query.trim()) return;
        
        this.isSearching = true;
        this.showLoadingState();
        
        const activeProvider = specificProvider || this.getActiveProvider();
        
        try {
            // Add to search history
            this.addToHistory(query, activeProvider);
            
            let results = [];
            
            if (activeProvider === 'all') {
                // Search all providers
                results = await this.searchAllProviders(query);
            } else {
                // Search specific provider
                results = await this.searchSingleProvider(query, activeProvider);
            }
            
            this.displayResults(results, query);
            
        } catch (error) {
            console.error('Search error:', error);
            this.showErrorState(error.message);
        } finally {
            this.isSearching = false;
        }
    }

    async searchAllProviders(query) {
        const providers = Array.from(this.searchProviders.values())
            .filter(provider => provider.enabled && this.canAccessProvider(provider));
        
        const searchPromises = providers.map(async (provider) => {
            try {
                const results = await this.searchSingleProvider(query, provider.id);
                return {
                    provider: provider.id,
                    providerName: provider.name,
                    providerIcon: provider.icon,
                    results: results.slice(0, 5) // Limit results per provider
                };
            } catch (error) {
                console.warn(`Search failed for provider ${provider.id}:`, error);
                return {
                    provider: provider.id,
                    providerName: provider.name,
                    providerIcon: provider.icon,
                    results: []
                };
            }
        });
        
        return Promise.all(searchPromises);
    }

    async searchSingleProvider(query, providerId) {
        const provider = this.searchProviders.get(providerId);
        if (!provider || !provider.searchFunction) {
            return [];
        }
        
        // Check cache first
        const cacheKey = `${providerId}:${query.toLowerCase()}`;
        const cached = this.searchCache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.results;
        }
        
        // Perform search
        const results = await provider.searchFunction(query);
        
        // Cache results
        this.searchCache.set(cacheKey, {
            results,
            timestamp: Date.now()
        });
        
        // Limit cache size
        if (this.searchCache.size > this.maxCacheItems) {
            const oldestKey = this.searchCache.keys().next().value;
            this.searchCache.delete(oldestKey);
        }
        
        return results;
    }

    // Search provider implementations
    async searchDevices(query) {
        try {
            if (!window.CVDApi) return [];
            
            const api = new CVDApi();
            const devices = await api.getDevices();
            
            const queryLower = query.toLowerCase();
            return devices
                .filter(device => 
                    device.asset_tag?.toLowerCase().includes(queryLower) ||
                    device.location_name?.toLowerCase().includes(queryLower) ||
                    device.device_type?.toLowerCase().includes(queryLower)
                )
                .map(device => ({
                    id: device.id,
                    title: device.asset_tag,
                    description: `${device.location_name} • ${device.device_type}`,
                    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/></svg>',
                    type: 'device',
                    action: 'View Device',
                    url: `#coolers`,
                    data: device
                }))
                .slice(0, 10);
        } catch (error) {
            console.error('Device search error:', error);
            return [];
        }
    }

    async searchProducts(query) {
        try {
            if (!window.CVDApi) return [];
            
            const api = new CVDApi();
            const products = await api.getProducts();
            
            const queryLower = query.toLowerCase();
            return products
                .filter(product => 
                    product.name?.toLowerCase().includes(queryLower) ||
                    product.category?.toLowerCase().includes(queryLower)
                )
                .map(product => ({
                    id: product.id,
                    title: product.name,
                    description: `Category: ${product.category || 'Unknown'}`,
                    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="m2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57L22.38 9H5.12"/></svg>',
                    type: 'product',
                    action: 'View Product',
                    url: `#planogram`,
                    data: product
                }))
                .slice(0, 10);
        } catch (error) {
            console.error('Product search error:', error);
            return [];
        }
    }

    async searchOrders(query) {
        try {
            if (!window.CVDApi) return [];
            
            const api = new CVDApi();
            const orders = await api.makeRequest('GET', '/service-orders');
            
            const queryLower = query.toLowerCase();
            return orders
                .filter(order => 
                    order.id?.toString().includes(queryLower) ||
                    order.device_name?.toLowerCase().includes(queryLower) ||
                    order.status?.toLowerCase().includes(queryLower)
                )
                .map(order => ({
                    id: order.id,
                    title: `Service Order #${order.id}`,
                    description: `${order.device_name} • Status: ${order.status}`,
                    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg>',
                    type: 'order',
                    action: 'View Order',
                    url: `#service-orders`,
                    data: order
                }))
                .slice(0, 10);
        } catch (error) {
            console.error('Order search error:', error);
            return [];
        }
    }

    async searchUsers(query) {
        if (!window.currentUser || window.currentUser.role !== 'admin') {
            return [];
        }

        try {
            if (!window.CVDApi) return [];
            
            const api = new CVDApi();
            const users = await api.makeRequest('GET', '/users');
            
            const queryLower = query.toLowerCase();
            return users
                .filter(user => 
                    user.username?.toLowerCase().includes(queryLower) ||
                    user.email?.toLowerCase().includes(queryLower) ||
                    user.role?.toLowerCase().includes(queryLower)
                )
                .map(user => ({
                    id: user.id,
                    title: user.username,
                    description: `${user.email || 'No email'} • Role: ${user.role}`,
                    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
                    type: 'user',
                    action: 'View User',
                    url: `#user-management`,
                    data: user
                }))
                .slice(0, 10);
        } catch (error) {
            console.error('User search error:', error);
            return [];
        }
    }

    async searchPages(query) {
        const pages = [
            { hash: '#home', title: 'Dashboard', description: 'Main dashboard with business overview' },
            { hash: '#coolers', title: 'Device List', description: 'Manage and view all vending devices' },
            { hash: '#planogram', title: 'Planograms', description: 'Product placement and optimization' },
            { hash: '#service-orders', title: 'Service Orders', description: 'Manage service tasks and maintenance' },
            { hash: '#route-schedule', title: 'Route Schedule', description: 'Plan and optimize delivery routes' },
            { hash: '#asset-sales', title: 'Device Performance', description: 'Sales analytics by device' },
            { hash: '#product-sales', title: 'Product Performance', description: 'Product sales analytics' },
            { hash: '#database', title: 'Database Viewer', description: 'View raw database information' },
            { hash: '#dex-parser', title: 'DEX Parser', description: 'Process DEX files and data' },
            { hash: '#company-settings', title: 'Company Settings', description: 'Manage company configuration' },
            { hash: '#user-management', title: 'User Management', description: 'Manage users and permissions' },
            { hash: '#profile', title: 'My Profile', description: 'Personal account settings' }
        ];

        const queryLower = query.toLowerCase();
        return pages
            .filter(page => 
                page.title.toLowerCase().includes(queryLower) ||
                page.description.toLowerCase().includes(queryLower)
            )
            .map(page => ({
                id: page.hash,
                title: page.title,
                description: page.description,
                icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14,2 14,8 20,8"/></svg>',
                type: 'page',
                action: 'Navigate',
                url: page.hash,
                data: page
            }));
    }

    displayResults(results, query) {
        if (Array.isArray(results[0]?.results)) {
            // Multiple providers (search all)
            this.displayGroupedResults(results, query);
        } else {
            // Single provider
            this.displaySimpleResults(results, query);
        }
    }

    displayGroupedResults(providerResults, query) {
        const totalResults = providerResults.reduce((sum, group) => sum + group.results.length, 0);
        
        if (totalResults === 0) {
            this.showNoResultsState(query);
            return;
        }

        let html = '<div class="search-results-list">';
        
        providerResults.forEach(group => {
            if (group.results.length > 0) {
                html += `
                    <div class="search-result-group">
                        <div class="search-result-group-header">
                            <span class="group-icon">${group.providerIcon}</span>
                            <span class="group-title">${group.providerName}</span>
                            <span class="group-count">${group.results.length}</span>
                        </div>
                        ${group.results.map((result, index) => this.renderResultItem(result, query, index)).join('')}
                    </div>
                `;
            }
        });
        
        html += '</div>';
        this.searchResults.innerHTML = html;
        this.attachResultHandlers();
    }

    displaySimpleResults(results, query) {
        if (results.length === 0) {
            this.showNoResultsState(query);
            return;
        }

        const html = `
            <div class="search-results-list">
                ${results.map((result, index) => this.renderResultItem(result, query, index)).join('')}
            </div>
        `;
        
        this.searchResults.innerHTML = html;
        this.attachResultHandlers();
    }

    renderResultItem(result, query, index) {
        const highlightedTitle = this.highlightText(result.title, query);
        const highlightedDescription = this.highlightText(result.description, query);
        
        return `
            <div class="search-result-item" data-index="${index}" data-url="${result.url}" data-type="${result.type}">
                <span class="result-icon">${result.icon}</span>
                <div class="result-content">
                    <div class="result-title">${highlightedTitle}</div>
                    <div class="result-description">${highlightedDescription}</div>
                </div>
                <div class="result-meta">
                    <span class="result-type">${result.type}</span>
                    <span class="result-action">${result.action}</span>
                </div>
            </div>
        `;
    }

    highlightText(text, query) {
        if (!query || !text) return text;
        
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return text.replace(regex, '<span class="search-highlight">$1</span>');
    }

    attachResultHandlers() {
        const resultItems = this.searchResults.querySelectorAll('.search-result-item');
        resultItems.forEach((item, index) => {
            item.addEventListener('click', () => {
                this.selectResult(index);
            });
        });
    }

    selectResult(index) {
        const items = this.searchResults.querySelectorAll('.search-result-item');
        const item = items[index];
        
        if (item) {
            const url = item.dataset.url;
            const type = item.dataset.type;
            
            if (url && url !== '#') {
                window.location.hash = url;
                this.closeSearch();
                
                if (window.ToastManager) {
                    window.ToastManager.show('info', `Navigating to ${type}`, 2000);
                }
            }
        }
    }

    handleKeyboardNavigation(e) {
        const items = this.searchResults.querySelectorAll('.search-result-item');
        if (items.length === 0) return;
        
        let selectedIndex = -1;
        items.forEach((item, index) => {
            if (item.classList.contains('selected')) {
                selectedIndex = index;
            }
        });
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = selectedIndex < items.length - 1 ? selectedIndex + 1 : 0;
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = selectedIndex > 0 ? selectedIndex - 1 : items.length - 1;
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (selectedIndex >= 0) {
                this.selectResult(selectedIndex);
            }
            return;
        } else {
            return; // Don't update selection for other keys
        }
        
        // Update selection
        items.forEach((item, index) => {
            item.classList.toggle('selected', index === selectedIndex);
        });
        
        // Scroll into view
        if (selectedIndex >= 0) {
            items[selectedIndex].scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }
    }

    setActiveProvider(provider) {
        // Update active tab
        const tabs = this.searchContainer.querySelectorAll('.filter-tab');
        tabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.provider === provider);
        });
        
        // Update input placeholder
        if (provider === 'all') {
            this.searchInput.placeholder = 'Search across all data...';
        } else {
            const providerData = this.searchProviders.get(provider);
            if (providerData) {
                this.searchInput.placeholder = providerData.placeholder;
            }
        }
        
        // Re-search with new provider
        if (this.currentQuery) {
            this.performSearch(this.currentQuery, provider);
        }
    }

    getActiveProvider() {
        const activeTab = this.searchContainer.querySelector('.filter-tab.active');
        return activeTab ? activeTab.dataset.provider : 'all';
    }

    canAccessProvider(provider) {
        if (provider.adminOnly) {
            return window.currentUser && window.currentUser.role === 'admin';
        }
        return true;
    }

    showLoadingState() {
        this.searchResults.innerHTML = `
            <div class="search-loading">
                <div class="loading-spinner"></div>
                <span>Searching...</span>
            </div>
        `;
    }

    showNoResultsState(query) {
        this.searchResults.innerHTML = `
            <div class="search-no-results">
                <div class="empty-icon">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                    </svg>
                </div>
                <div class="empty-title">No results found</div>
                <div class="empty-description">
                    No results found for "${query}". Try a different search term or check a different category.
                </div>
            </div>
        `;
    }

    showErrorState(error) {
        this.searchResults.innerHTML = `
            <div class="search-no-results">
                <div class="empty-icon">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="m12 17 .01 0"/>
                    </svg>
                </div>
                <div class="empty-title">Search Error</div>
                <div class="empty-description">
                    ${error || 'An error occurred while searching. Please try again.'}
                </div>
            </div>
        `;
    }

    clearSearch() {
        this.searchResults.innerHTML = this.generateEmptyState();
    }

    updateEmptyState() {
        if (!this.currentQuery) {
            this.searchResults.innerHTML = this.generateEmptyState();
        }
    }

    addToHistory(query, provider) {
        const historyItem = {
            query,
            provider,
            timestamp: Date.now()
        };
        
        // Remove duplicate
        this.searchHistory = this.searchHistory.filter(item => 
            !(item.query === query && item.provider === provider)
        );
        
        // Add to front
        this.searchHistory.unshift(historyItem);
        
        // Limit size
        if (this.searchHistory.length > this.maxHistoryItems) {
            this.searchHistory = this.searchHistory.slice(0, this.maxHistoryItems);
        }
        
        this.saveSearchHistory();
    }

    loadSearchHistory() {
        try {
            const stored = localStorage.getItem('cvd_search_history');
            if (stored) {
                this.searchHistory = JSON.parse(stored);
            }
        } catch (error) {
            console.error('Error loading search history:', error);
            this.searchHistory = [];
        }
    }

    saveSearchHistory() {
        try {
            localStorage.setItem('cvd_search_history', JSON.stringify(this.searchHistory));
        } catch (error) {
            console.error('Error saving search history:', error);
        }
    }

    formatRelativeTime(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        
        if (diff < 60000) return 'now';
        if (diff < 3600000) return Math.floor(diff / 60000) + 'm';
        if (diff < 86400000) return Math.floor(diff / 3600000) + 'h';
        if (diff < 604800000) return Math.floor(diff / 86400000) + 'd';
        return Math.floor(diff / 604800000) + 'w';
    }

    // Admin/debug methods
    clearHistory() {
        this.searchHistory = [];
        this.saveSearchHistory();
        this.updateEmptyState();
    }

    clearCache() {
        this.searchCache.clear();
    }

    getStats() {
        return {
            historySize: this.searchHistory.length,
            cacheSize: this.searchCache.size,
            providers: this.searchProviders.size,
            isSearching: this.isSearching
        };
    }

    // Integration with command palette
    addToCommandPalette() {
        if (window.commandPaletteCommands) {
            window.commandPaletteCommands.push(
                { group: 'Search', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>', text: 'Open Search', shortcut: 'Ctrl+/', action: () => this.openSearch() },
                { group: 'Search', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>', text: 'Clear Search History', action: () => this.clearHistory() }
            );
        }
    }
}

// Initialize global instance
window.EnhancedSearchSystem = new EnhancedSearchSystem();

// Auto-integrate when loaded
document.addEventListener('DOMContentLoaded', () => {
    if (window.EnhancedSearchSystem) {
        window.EnhancedSearchSystem.addToCommandPalette();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedSearchSystem;
}