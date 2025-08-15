/**
 * CVD Recent Pages Tracker
 * P2 Medium Priority - User Features Component 2
 * 
 * Track and provide quick access to recently visited pages:
 * - IndexedDB storage for persistent history
 * - Keyboard shortcuts (Ctrl+1-9) for quick navigation
 * - Recent pages dropdown in navigation
 * - Page visit analytics and patterns
 */

class RecentPagesTracker {
    constructor() {
        this.db = null;
        this.dbName = 'cvd_recent_pages';
        this.dbVersion = 1;
        this.storeName = 'pages';
        this.maxPages = 5;
        
        this.currentPage = null;
        this.recentPages = [];
        this.subscribers = [];
        this.isEnabled = true;
        
        this.pageRoutes = {
            '#home': { title: 'Dashboard', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>', page: 'pages/home-dashboard.html' },
            '#coolers': { title: 'Device List', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><rect width="18" height="20" x="3" y="2" rx="2"/><circle cx="12" cy="8" r="2"/><path d="M12 14v6"/></svg>', page: 'pages/PCP.html' },
            '#new-device': { title: 'New Device', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="16"/><line x1="8" x2="16" y1="12" y2="12"/></svg>', page: 'pages/INVD.html' },
            '#planogram': { title: 'Planograms', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><polyline points="10,9 9,9 8,9"/></svg>', page: 'pages/NSPT.html' },
            '#service-orders': { title: 'Service Orders', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="m9 14 2 2 4-4"/></svg>', page: 'pages/service-orders.html' },
            '#route-schedule': { title: 'Route Schedule', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>', page: 'pages/route-schedule.html' },
            '#asset-sales': { title: 'Device Performance', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><line x1="12" x2="12" y1="1" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>', page: 'pages/asset-sales.html' },
            '#product-sales': { title: 'Product Performance', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>', page: 'pages/product-sales.html' },
            '#database': { title: 'Database Viewer', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="m3 5 0 14c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="m3 12c0 1.7 4 3 9 3s9-1.3 9-3"/></svg>', page: 'pages/database-viewer.html' },
            '#dex-parser': { title: 'DEX Parser', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/></svg>', page: 'pages/dex-parser.html' },
            '#company-settings': { title: 'Company Settings', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>', page: 'pages/company-settings.html' },
            '#user-management': { title: 'User Management', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>', page: 'pages/user-management.html' },
            '#profile': { title: 'My Profile', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>', page: 'pages/profile.html' }
        };
        
        this.init();
    }

    async init() {
        try {
            await this.initDatabase();
            await this.loadRecentPages();
            this.setupEventListeners();
            this.setupKeyboardShortcuts();
            this.createRecentPagesUI();
            
            // Track initial page after UI is created and pages are loaded
            this.trackInitialPage();
            
            console.log('RecentPagesTracker initialized');
        } catch (error) {
            console.error('Error initializing RecentPagesTracker:', error);
            // Fallback to localStorage
            this.initLocalStorageFallback();
        }
    }

    async initDatabase() {
        return new Promise((resolve, reject) => {
            if (!window.indexedDB) {
                reject(new Error('IndexedDB not supported'));
                return;
            }

            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = () => {
                reject(new Error('Failed to open IndexedDB'));
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create pages store
                const store = db.createObjectStore(this.storeName, { keyPath: 'hash' });
                store.createIndex('timestamp', 'timestamp', { unique: false });
                store.createIndex('visitCount', 'visitCount', { unique: false });
                store.createIndex('title', 'title', { unique: false });
            };
        });
    }

    initLocalStorageFallback() {
        console.warn('Using localStorage fallback for recent pages');
        this.db = null;
        
        try {
            const stored = localStorage.getItem('cvd_recent_pages');
            if (stored) {
                this.recentPages = JSON.parse(stored);
            }
        } catch (error) {
            console.error('Error loading from localStorage:', error);
            this.recentPages = [];
        }
        
        // Complete initialization for localStorage fallback
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        this.createRecentPagesUI();
        this.trackInitialPage();
    }

    async loadRecentPages() {
        if (!this.db) {
            return; // Already loaded in fallback
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const index = store.index('timestamp');
            const request = index.openCursor(null, 'prev'); // Reverse order (newest first)

            const pages = [];

            request.onsuccess = (event) => {
                const cursor = event.target.result;
                if (cursor && pages.length < this.maxPages) {
                    pages.push(cursor.value);
                    cursor.continue();
                } else {
                    this.recentPages = pages;
                    this.updateRecentPagesUI();
                    resolve();
                }
            };

            request.onerror = () => {
                reject(new Error('Failed to load recent pages'));
            };
        });
    }

    async saveToStorage() {
        if (this.db) {
            return this.saveToIndexedDB();
        } else {
            // Fallback to localStorage
            try {
                localStorage.setItem('cvd_recent_pages', JSON.stringify(this.recentPages));
            } catch (error) {
                console.error('Error saving to localStorage:', error);
            }
        }
    }

    async saveToIndexedDB() {
        if (!this.db) return;

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const index = store.index('timestamp');

            transaction.oncomplete = () => resolve();
            transaction.onerror = () => reject(new Error('Save transaction failed'));

            // First, get all existing entries to clean up old ones
            const getAllRequest = index.openCursor(null, 'prev');
            const existingEntries = [];
            
            getAllRequest.onsuccess = (event) => {
                const cursor = event.target.result;
                if (cursor) {
                    existingEntries.push(cursor.value);
                    cursor.continue();
                } else {
                    // Clear all existing entries
                    const clearRequest = store.clear();
                    clearRequest.onsuccess = () => {
                        // Save only the recent pages (limited to maxPages)
                        this.recentPages.forEach(page => {
                            store.put(page);
                        });
                    };
                }
            };
        });
    }

    setupEventListeners() {
        // Listen for hash changes to track page visits
        window.addEventListener('hashchange', () => {
            this.trackCurrentPage();
            // Update UI to reflect current page change
            this.updateRecentPagesUI();
        });

        // Listen for cross-frame navigation messages
        window.addEventListener('message', (event) => {
            if (event.origin !== window.location.origin) return;
            
            const { type, payload } = event.data;
            if (type === 'PAGE_VISITED') {
                this.handlePageVisit(payload);
            }
        });

        // Initial page tracking is now handled by trackInitialPage()
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+1-9 shortcuts for recent pages
            if (e.ctrlKey && !e.altKey && !e.metaKey && !e.shiftKey) {
                const keyNum = parseInt(e.key);
                if (keyNum >= 1 && keyNum <= 9) {
                    e.preventDefault();
                    this.navigateToRecentPage(keyNum - 1);
                }
            }
            
            // Ctrl+Shift+H for recent pages menu
            if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'h') {
                e.preventDefault();
                this.showRecentPagesMenu();
            }
        });
    }

    trackInitialPage() {
        // Track the current page immediately on initialization
        // This ensures the Recent menu is populated right away
        if (window.location.hash) {
            this.trackCurrentPage();
        } else {
            // Default to home if no hash
            window.location.hash = '#home';
            this.trackCurrentPage();
        }
    }

    trackCurrentPage() {
        if (!this.isEnabled) return;

        const hash = window.location.hash || '#home';
        const routeInfo = this.pageRoutes[hash];
        
        if (!routeInfo) return;

        const pageData = {
            hash,
            title: routeInfo.title,
            icon: routeInfo.icon,
            page: routeInfo.page,
            timestamp: Date.now(),
            visitCount: 1,
            timeSpent: 0,
            lastVisitDuration: 0
        };

        this.addOrUpdatePage(pageData);
    }

    handlePageVisit(payload) {
        if (payload.hash && this.pageRoutes[payload.hash]) {
            const pageData = {
                ...this.pageRoutes[payload.hash],
                hash: payload.hash,
                timestamp: Date.now(),
                visitCount: 1
            };
            
            this.addOrUpdatePage(pageData);
        }
    }

    async addOrUpdatePage(pageData) {
        // Find existing page
        const existingIndex = this.recentPages.findIndex(p => p.hash === pageData.hash);
        
        if (existingIndex !== -1) {
            // Update existing page
            const existing = this.recentPages[existingIndex];
            const timeSpent = Date.now() - (existing.lastVisitTime || existing.timestamp);
            
            const updated = {
                ...existing,
                timestamp: pageData.timestamp,
                visitCount: existing.visitCount + 1,
                timeSpent: existing.timeSpent + (timeSpent > 0 && timeSpent < 1800000 ? timeSpent : 0), // Max 30 min
                lastVisitTime: existing.timestamp,
                lastVisitDuration: timeSpent > 0 && timeSpent < 1800000 ? timeSpent : 0
            };
            
            // Move to front
            this.recentPages.splice(existingIndex, 1);
            this.recentPages.unshift(updated);
        } else {
            // Add new page at front
            this.recentPages.unshift({
                ...pageData,
                lastVisitTime: Date.now()
            });
            
            // Keep only maxPages
            if (this.recentPages.length > this.maxPages) {
                this.recentPages = this.recentPages.slice(0, this.maxPages);
            }
        }

        // Save to storage
        await this.saveToStorage();
        
        // Update UI
        this.updateRecentPagesUI();
        
        // Notify subscribers
        this.notifySubscribers('page_tracked', pageData);
        
        this.currentPage = pageData;
    }

    navigateToRecentPage(index) {
        // Filter out current page to match display
        const currentHash = window.location.hash || '#home';
        const displayPages = this.recentPages.filter(page => page.hash !== currentHash);
        
        if (index >= 0 && index < displayPages.length) {
            const page = displayPages[index];
            window.location.hash = page.hash;
            
            if (window.ToastManager) {
                window.ToastManager.show('info', `Navigating to ${page.title}`, 2000);
            }
        }
    }

    createRecentPagesUI() {
        // Check if already created
        if (document.querySelector('.recent-pages-dropdown')) {
            return; // Already exists, don't create duplicate
        }
        
        // Add recent pages dropdown to navigation
        const navMenu = document.querySelector('.nav-menu');
        if (!navMenu) {
            // If nav menu not found, retry after a short delay
            setTimeout(() => this.createRecentPagesUI(), 100);
            return;
        }

        // Create recent pages dropdown
        const recentPagesDropdown = document.createElement('div');
        recentPagesDropdown.className = 'nav-dropdown recent-pages-dropdown';
        recentPagesDropdown.innerHTML = `
            <button class="nav-button recent-pages-btn" data-menu="recent">
                <span class="nav-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg></span>Recent
            </button>
            <div class="dropdown-menu recent-pages-menu" id="recent-pages-menu">
                <div class="recent-pages-list"></div>
                <div class="dropdown-divider"></div>
                <div class="recent-pages-footer">
                    <div class="recent-pages-shortcuts">
                        <small>Use Ctrl+1-4 for quick access</small>
                    </div>
                </div>
            </div>
        `;

        // Insert before the help menu
        const helpDropdown = navMenu.querySelector('.nav-dropdown:last-child');
        if (helpDropdown) {
            navMenu.insertBefore(recentPagesDropdown, helpDropdown);
        } else {
            navMenu.appendChild(recentPagesDropdown);
        }

        // Add event listeners for the dropdown
        this.setupRecentPagesDropdown(recentPagesDropdown);
        
        // Initial UI update
        this.updateRecentPagesUI();
    }

    setupRecentPagesDropdown(dropdown) {
        const button = dropdown.querySelector('.recent-pages-btn');
        const menu = dropdown.querySelector('.recent-pages-menu');
        
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            
            // Check if this dropdown is currently open
            const isOpen = menu.style.display === 'block';
            
            // Use the global closeAllDropdowns function if available
            if (window.closeAllDropdowns) {
                window.closeAllDropdowns();
            } else {
                // Fallback: Close all dropdowns manually
                document.querySelectorAll('.dropdown-menu').forEach(m => {
                    m.style.display = 'none';
                });
                document.querySelectorAll('.nav-button').forEach(btn => {
                    btn.classList.remove('dropdown-open');
                    btn.blur();
                });
            }
            
            // If it wasn't open, open it
            if (!isOpen) {
                menu.style.display = 'block';
                button.classList.add('dropdown-open');
                this.updateRecentPagesUI(); // Refresh on open
            }
        });
    }

    updateRecentPagesUI() {
        const recentPagesList = document.querySelector('.recent-pages-list');
        if (!recentPagesList) return;

        // Filter out the current page from display
        const currentHash = window.location.hash || '#home';
        const displayPages = this.recentPages.filter(page => page.hash !== currentHash);

        if (displayPages.length === 0) {
            recentPagesList.innerHTML = `
                <div class="dropdown-item disabled">
                    <span class="nav-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/></svg></span>
                    <span>No recent pages</span>
                </div>
            `;
            return;
        }

        // Limit display to 5 pages (excluding current page)
        const pagesToShow = displayPages.slice(0, 5);

        const recentPagesHTML = pagesToShow.map((page, index) => {
            const shortcut = index < 9 ? `Ctrl+${index + 1}` : '';
            const visitInfo = page.visitCount > 1 ? ` (${page.visitCount} visits)` : '';
            
            return `
                <a href="${page.hash}" class="dropdown-item recent-page-item" 
                   data-hash="${page.hash}" data-index="${index}">
                    <span class="nav-icon">${page.icon}</span>
                    <div class="recent-page-info">
                        <div class="recent-page-title">${page.title}</div>
                        <div class="recent-page-meta">
                            ${this.formatTimestamp(page.timestamp)}${visitInfo}
                        </div>
                    </div>
                    ${shortcut ? `<span class="recent-page-shortcut">${shortcut}</span>` : ''}
                </a>
            `;
        }).join('');

        recentPagesList.innerHTML = recentPagesHTML;

        // Add click handlers
        recentPagesList.querySelectorAll('.recent-page-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const hash = item.dataset.hash;
                if (hash) {
                    window.location.hash = hash;
                }
            });
        });
    }

    formatTimestamp(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        
        if (diff < 60000) { // Less than 1 minute
            return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
            const minutes = Math.floor(diff / 60000);
            return `${minutes}m ago`;
        } else if (diff < 86400000) { // Less than 24 hours
            const hours = Math.floor(diff / 3600000);
            return `${hours}h ago`;
        } else if (diff < 604800000) { // Less than 7 days
            const days = Math.floor(diff / 86400000);
            return `${days}d ago`;
        } else {
            return new Date(timestamp).toLocaleDateString();
        }
    }

    showRecentPagesMenu() {
        const button = document.querySelector('.recent-pages-btn');
        if (button) {
            button.click();
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
                console.error('Error in recent pages subscriber:', error);
            }
        });
    }

    // Analytics and insights
    getMostVisitedPages() {
        return [...this.recentPages]
            .sort((a, b) => b.visitCount - a.visitCount)
            .slice(0, 5);
    }

    getPageStats() {
        const totalVisits = this.recentPages.reduce((sum, page) => sum + page.visitCount, 0);
        const totalTimeSpent = this.recentPages.reduce((sum, page) => sum + (page.timeSpent || 0), 0);
        const avgTimePerPage = totalVisits > 0 ? totalTimeSpent / totalVisits : 0;

        return {
            totalPages: this.recentPages.length,
            totalVisits,
            totalTimeSpent,
            avgTimePerPage,
            mostVisited: this.getMostVisitedPages()
        };
    }

    createStatsModal() {
        const stats = this.getPageStats();
        
        const modal = document.createElement('div');
        modal.className = 'recent-pages-stats-modal';
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Page Visit Statistics</h3>
                    <button class="modal-close">×</button>
                </div>
                <div class="modal-body">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value">${stats.totalPages}</div>
                            <div class="stat-label">Unique Pages</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${stats.totalVisits}</div>
                            <div class="stat-label">Total Visits</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${this.formatDuration(stats.totalTimeSpent)}</div>
                            <div class="stat-label">Time Spent</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${this.formatDuration(stats.avgTimePerPage)}</div>
                            <div class="stat-label">Avg Per Visit</div>
                        </div>
                    </div>
                    
                    <div class="most-visited-section">
                        <h4>Most Visited Pages</h4>
                        <div class="most-visited-list">
                            ${stats.mostVisited.map(page => `
                                <div class="most-visited-item">
                                    <span class="page-icon">${page.icon}</span>
                                    <div class="page-details">
                                        <div class="page-name">${page.title}</div>
                                        <div class="page-visits">${page.visitCount} visits</div>
                                    </div>
                                    <div class="page-time">${this.formatDuration(page.timeSpent || 0)}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" data-action="export">Export Data</button>
                    <button class="btn btn-warning" data-action="clear">Clear History</button>
                    <button class="btn btn-primary" data-action="close">Close</button>
                </div>
            </div>
        `;

        this.addStatsModalStyles();
        this.attachStatsModalEvents(modal);
        
        return modal;
    }

    formatDuration(ms) {
        if (ms < 1000) return '0s';
        if (ms < 60000) return Math.round(ms / 1000) + 's';
        if (ms < 3600000) return Math.round(ms / 60000) + 'm';
        return Math.round(ms / 3600000) + 'h';
    }

    addStatsModalStyles() {
        if (document.getElementById('recent-pages-stats-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'recent-pages-stats-styles';
        style.textContent = `
            .recent-pages-stats-modal {
                position: fixed;
                inset: 0;
                z-index: var(--z-modal);
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                visibility: hidden;
                transition: opacity var(--duration-base), visibility var(--duration-base);
            }
            
            .recent-pages-stats-modal.active {
                opacity: 1;
                visibility: visible;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: var(--space-md);
                margin-bottom: var(--space-lg);
            }
            
            .stat-card {
                background: var(--color-neutral-50);
                padding: var(--space-md);
                border-radius: var(--radius-md);
                text-align: center;
            }
            
            .stat-value {
                font-size: var(--text-2xl);
                font-weight: var(--font-bold);
                color: var(--color-primary-500);
                margin-bottom: var(--space-xs);
            }
            
            .stat-label {
                font-size: var(--text-sm);
                color: var(--color-neutral-600);
            }
            
            .most-visited-section h4 {
                margin: 0 0 var(--space-md) 0;
                font-size: var(--text-base);
                font-weight: var(--font-semibold);
            }
            
            .most-visited-item {
                display: flex;
                align-items: center;
                gap: var(--space-sm);
                padding: var(--space-sm);
                border-radius: var(--radius-md);
                margin-bottom: var(--space-xs);
                transition: background var(--duration-fast);
            }
            
            .most-visited-item:hover {
                background: var(--color-neutral-50);
            }
            
            .page-icon {
                font-size: var(--text-lg);
            }
            
            .page-icon .nav-icon-svg {
                width: 20px;
                height: 20px;
            }
            
            .page-details {
                flex: 1;
            }
            
            .page-name {
                font-weight: var(--font-medium);
                color: var(--color-neutral-800);
            }
            
            .page-visits {
                font-size: var(--text-sm);
                color: var(--color-neutral-600);
            }
            
            .page-time {
                font-size: var(--text-sm);
                color: var(--color-neutral-600);
                font-family: var(--font-mono);
            }
        `;
        
        document.head.appendChild(style);
    }

    attachStatsModalEvents(modal) {
        const closeModal = () => {
            modal.classList.remove('active');
            setTimeout(() => modal.remove(), 300);
        };
        
        modal.querySelector('.modal-backdrop').addEventListener('click', closeModal);
        modal.querySelector('.modal-close').addEventListener('click', closeModal);
        
        modal.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            if (!action) return;
            
            switch (action) {
                case 'export':
                    this.exportData();
                    break;
                case 'clear':
                    if (confirm('Clear all page visit history?')) {
                        this.clearHistory();
                        closeModal();
                    }
                    break;
                case 'close':
                    closeModal();
                    break;
            }
        });
        
        document.addEventListener('keydown', function escapeHandler(e) {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', escapeHandler);
            }
        });
    }

    showStatsModal() {
        const modal = this.createStatsModal();
        document.body.appendChild(modal);
        
        requestAnimationFrame(() => {
            modal.classList.add('active');
        });
    }

    async clearHistory() {
        this.recentPages = [];
        
        if (this.db) {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            await store.clear();
        } else {
            localStorage.removeItem('cvd_recent_pages');
        }
        
        this.updateRecentPagesUI();
        this.notifySubscribers('history_cleared', {});
        
        if (window.ToastManager) {
            window.ToastManager.show('info', 'Page history cleared');
        }
    }

    exportData() {
        const exportData = {
            timestamp: new Date().toISOString(),
            stats: this.getPageStats(),
            pages: this.recentPages,
            version: '1.0'
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cvd-page-history-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        if (window.ToastManager) {
            window.ToastManager.show('success', 'Page history exported');
        }
    }

    // Admin/debug methods
    enable() {
        this.isEnabled = true;
        if (window.ToastManager) {
            window.ToastManager.show('info', 'Recent pages tracking enabled');
        }
    }

    disable() {
        this.isEnabled = false;
        if (window.ToastManager) {
            window.ToastManager.show('info', 'Recent pages tracking disabled');
        }
    }

    // Add CSS for recent pages styling
    addRecentPagesStyles() {
        if (document.getElementById('recent-pages-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'recent-pages-styles';
        style.textContent = `
            .recent-pages-list {
                max-height: 400px;
                overflow-y: auto;
            }
            
            .recent-page-item {
                display: flex !important;
                align-items: center;
                gap: var(--space-sm);
                padding: var(--space-sm) var(--space-md) !important;
                transition: background var(--duration-fast);
                position: relative;
            }
            
            .recent-page-item.current {
                background: var(--color-primary-50);
                color: var(--color-primary-700);
            }
            
            .recent-page-info {
                flex: 1;
                min-width: 0;
            }
            
            .recent-page-title {
                font-weight: var(--font-medium);
                color: var(--color-neutral-800);
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            .recent-page-meta {
                font-size: var(--text-xs);
                color: var(--color-neutral-500);
                margin-top: 2px;
            }
            
            .recent-page-shortcut {
                font-size: var(--text-xs);
                color: var(--color-neutral-400);
                font-family: var(--font-mono);
                background: var(--color-neutral-100);
                padding: 2px 6px;
                border-radius: var(--radius-sm);
            }
            
            .recent-pages-footer {
                padding: var(--space-sm) var(--space-md);
                text-align: center;
            }
            
            .recent-pages-shortcuts small {
                color: var(--color-neutral-500);
                font-size: var(--text-xs);
            }
            
            .dropdown-item.disabled {
                opacity: 0.6;
                cursor: not-allowed;
                pointer-events: none;
            }
            
            /* SVG icon styles for Recent Pages */
            .recent-page-item .nav-icon-svg,
            .recent-pages-dropdown .nav-icon-svg,
            .dropdown-item .nav-icon-svg {
                width: 16px;
                height: 16px;
                flex-shrink: 0;
            }
            
            .recent-pages-btn .nav-icon-svg {
                width: 18px;
                height: 18px;
            }
        `;
        
        document.head.appendChild(style);
    }

    // Integration method to add to existing systems
    integrate() {
        this.addRecentPagesStyles();
        
        // Add to command palette if available
        if (window.commandPaletteCommands) {
            window.commandPaletteCommands.push(
                { group: 'Navigation', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><line x1="18" x2="18" y1="20" y2="10"/><line x1="12" x2="12" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="14"/></svg>', text: 'View Page Statistics', action: () => this.showStatsModal() },
                { group: 'Navigation', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon-svg" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg>', text: 'Show Recent Pages', shortcut: 'Ctrl+Shift+H', action: () => this.showRecentPagesMenu() }
            );
        }
    }
}

// Initialize global instance
window.RecentPagesTracker = new RecentPagesTracker();

// Auto-integrate when loaded
document.addEventListener('DOMContentLoaded', () => {
    if (window.RecentPagesTracker) {
        window.RecentPagesTracker.integrate();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RecentPagesTracker;
}