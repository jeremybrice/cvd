/**
 * Activity Monitor Enhancement - Frontend Implementation
 * Desktop-optimized with rich interactions and real-time updates
 */

// ===== CONFIGURATION =====
const CONFIG = {
    API_BASE: '/api/admin/activity',
    REFRESH_INTERVAL: 30000, // 30 seconds
    ITEMS_PER_PAGE: 50,
    CHART_UPDATE_ANIMATION: 800,
    DEBOUNCE_DELAY: 300
};

// ===== STATE MANAGEMENT =====
class ActivityMonitorState {
    constructor() {
        this.state = {
            dateRange: '7d',
            customDateStart: null,
            customDateEnd: null,
            activeMetrics: ['active_users', 'page_views'],
            selectedUser: null,
            historyFilters: {
                startDate: null,
                endDate: null,
                actionType: null
            },
            chartData: null,
            activeUsers: [],
            userHistory: [],
            currentPage: 1,
            totalPages: 1,
            isLoading: false,
            error: null
        };
        
        this.subscribers = [];
        this.loadSavedState();
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
    
    notify() {
        this.subscribers.forEach(callback => callback(this.state));
    }
    
    setState(updates) {
        this.state = { ...this.state, ...updates };
        this.saveState();
        this.notify();
    }
    
    saveState() {
        const preferences = {
            dateRange: this.state.dateRange,
            activeMetrics: this.state.activeMetrics
        };
        localStorage.setItem('activityMonitorPrefs', JSON.stringify(preferences));
    }
    
    loadSavedState() {
        const saved = localStorage.getItem('activityMonitorPrefs');
        if (saved) {
            try {
                const preferences = JSON.parse(saved);
                this.state = { ...this.state, ...preferences };
            } catch (error) {
                console.error('Failed to load saved preferences:', error);
            }
        }
    }
}

// Global state instance
const activityState = new ActivityMonitorState();

// ===== CHART MANAGEMENT =====
class ActivityTrendsChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas element ${canvasId} not found`);
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.chart = null;
        this.initChart();
    }
    
    initChart() {
        // Create gradient fills
        const gradients = this.createGradients();
        
        this.chart = new Chart(this.ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: CONFIG.CHART_UPDATE_ANIMATION,
                    easing: 'easeInOutQuart'
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        display: false // We'll create custom legend
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(26, 26, 26, 0.95)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        padding: 16,
                        displayColors: true,
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        titleFont: {
                            size: 14,
                            weight: '600'
                        },
                        bodyFont: {
                            size: 13
                        },
                        callbacks: {
                            title: (tooltipItems) => {
                                const date = new Date(tooltipItems[0].label);
                                return date.toLocaleDateString('en-US', {
                                    weekday: 'short',
                                    month: 'short',
                                    day: 'numeric',
                                    year: 'numeric'
                                });
                            },
                            label: (context) => {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y;
                                return `${label}: ${this.formatValue(value, context.dataset.metric)}`;
                            }
                        }
                    },
                    zoom: {
                        zoom: {
                            wheel: {
                                enabled: true,
                            },
                            pinch: {
                                enabled: true
                            },
                            mode: 'x',
                        },
                        pan: {
                            enabled: true,
                            mode: 'x',
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day',
                            displayFormats: {
                                day: 'MMM DD'
                            }
                        },
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            font: {
                                size: 12
                            },
                            color: '#6c757d',
                            maxRotation: 0
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            font: {
                                size: 12
                            },
                            color: '#6c757d',
                            callback: (value) => {
                                if (value >= 1000) {
                                    return (value / 1000).toFixed(1) + 'k';
                                }
                                return value;
                            }
                        }
                    }
                },
                onClick: (event, activeElements) => {
                    if (activeElements.length > 0) {
                        this.handleDataPointClick(activeElements[0]);
                    }
                }
            }
        });
    }
    
    createGradients() {
        const gradients = {};
        
        // Active Users gradient
        gradients.activeUsers = this.ctx.createLinearGradient(0, 0, 0, 400);
        gradients.activeUsers.addColorStop(0, 'rgba(0, 109, 254, 0.4)');
        gradients.activeUsers.addColorStop(1, 'rgba(0, 109, 254, 0.05)');
        
        // Page Views gradient
        gradients.pageViews = this.ctx.createLinearGradient(0, 0, 0, 400);
        gradients.pageViews.addColorStop(0, 'rgba(40, 167, 69, 0.4)');
        gradients.pageViews.addColorStop(1, 'rgba(40, 167, 69, 0.05)');
        
        // Session Duration gradient
        gradients.sessionDuration = this.ctx.createLinearGradient(0, 0, 0, 400);
        gradients.sessionDuration.addColorStop(0, 'rgba(255, 193, 7, 0.4)');
        gradients.sessionDuration.addColorStop(1, 'rgba(255, 193, 7, 0.05)');
        
        // API Calls gradient
        gradients.apiCalls = this.ctx.createLinearGradient(0, 0, 0, 400);
        gradients.apiCalls.addColorStop(0, 'rgba(23, 162, 184, 0.4)');
        gradients.apiCalls.addColorStop(1, 'rgba(23, 162, 184, 0.05)');
        
        return gradients;
    }
    
    async loadData() {
        this.showLoading(true);
        
        try {
            const params = {
                range: activityState.state.dateRange,
                metrics: activityState.state.activeMetrics.join(',')
            };
            
            if (activityState.state.dateRange === 'custom') {
                params.start_date = activityState.state.customDateStart;
                params.end_date = activityState.state.customDateEnd;
            }
            
            const response = await fetch(`${CONFIG.API_BASE}/trends?${new URLSearchParams(params)}`, {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error('Failed to load trends data');
            
            const data = await response.json();
            this.updateChart(data.data);
            
        } catch (error) {
            console.error('Error loading trends:', error);
            errorHandler.showError('Failed to load trends data');
        } finally {
            this.showLoading(false);
        }
    }
    
    updateChart(data) {
        const datasets = [];
        const gradients = this.createGradients();
        
        const metricConfigs = {
            active_users: {
                label: 'Active Users',
                borderColor: '#006dfe',
                backgroundColor: gradients.activeUsers,
                metric: 'active_users'
            },
            page_views: {
                label: 'Page Views',
                borderColor: '#28a745',
                backgroundColor: gradients.pageViews,
                metric: 'page_views'
            },
            avg_session: {
                label: 'Avg Session (min)',
                borderColor: '#ffc107',
                backgroundColor: gradients.sessionDuration,
                metric: 'avg_session'
            },
            api_calls: {
                label: 'API Calls',
                borderColor: '#17a2b8',
                backgroundColor: gradients.apiCalls,
                metric: 'api_calls'
            }
        };
        
        activityState.state.activeMetrics.forEach(metric => {
            if (data[metric] && metricConfigs[metric]) {
                const config = metricConfigs[metric];
                datasets.push({
                    label: config.label,
                    data: data[metric],
                    borderColor: config.borderColor,
                    backgroundColor: config.backgroundColor,
                    borderWidth: 3,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#fff',
                    pointBorderWidth: 2,
                    metric: config.metric
                });
            }
        });
        
        this.chart.data = {
            labels: data.labels || [],
            datasets: datasets
        };
        
        this.chart.update('active');
        this.updateCustomLegend();
    }
    
    updateCustomLegend() {
        const legendContainer = document.getElementById('customLegend');
        if (!legendContainer) return;
        
        legendContainer.innerHTML = this.chart.data.datasets.map(dataset => `
            <div class="legend-item">
                <div class="legend-color" style="background: ${dataset.borderColor}"></div>
                <span>${dataset.label}</span>
            </div>
        `).join('');
    }
    
    formatValue(value, metric) {
        switch (metric) {
            case 'active_users':
                return `${value} users`;
            case 'page_views':
                return `${value} views`;
            case 'avg_session':
                return `${value} min`;
            case 'api_calls':
                return `${value} calls`;
            default:
                return value;
        }
    }
    
    handleDataPointClick(element) {
        const date = this.chart.data.labels[element.index];
        const metric = element.dataset.metric;
        
        // Could open a drill-down view here
        console.log('Data point clicked:', { date, metric, value: element.parsed.y });
    }
    
    showLoading(show) {
        const overlay = document.getElementById('graphLoadingOverlay');
        if (overlay) {
            overlay.classList.toggle('hidden', !show);
        }
    }
}

// ===== API INTEGRATION =====
class ActivityMonitorAPI {
    constructor() {
        this.baseURL = CONFIG.API_BASE;
    }
    
    async fetchTrends(params) {
        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(`${this.baseURL}/trends?${queryString}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async fetchActiveUsers(filters = {}) {
        const params = {
            include_idle: 'true',
            sort: 'last_activity',
            order: 'desc',
            ...filters
        };
        
        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(`/api/admin/activity/current?${queryString}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async fetchUserHistory(userId, filters = {}) {
        const params = {
            limit: filters.limit || CONFIG.ITEMS_PER_PAGE,
            offset: filters.offset || 0,
            start_date: filters.startDate,
            end_date: filters.endDate,
            action_type: filters.actionType
        };
        
        // Remove undefined values
        Object.keys(params).forEach(key => {
            if (params[key] === undefined || params[key] === null || params[key] === '') {
                delete params[key];
            }
        });
        
        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(`${this.baseURL}/history/${userId}?${queryString}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async exportData(format, filters) {
        const params = {
            format: format,
            date_range: filters.dateRange,
            metrics: filters.metrics ? filters.metrics.join(',') : ''
        };
        
        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(`${this.baseURL}/export?${queryString}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`Export failed: ${response.status}`);
        }
        
        // Handle file download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `activity-report-${Date.now()}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
}

// ===== ERROR HANDLER =====
class ActivityMonitorErrorHandler {
    constructor() {
        this.errorContainer = null;
        this.createErrorContainer();
    }
    
    createErrorContainer() {
        this.errorContainer = document.createElement('div');
        this.errorContainer.className = 'error-notification-container';
        this.errorContainer.setAttribute('role', 'alert');
        this.errorContainer.setAttribute('aria-live', 'polite');
        document.body.appendChild(this.errorContainer);
    }
    
    showError(message, type = 'error', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `error-notification error-notification--${type}`;
        
        const icons = {
            error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>',
            warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
            success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
            info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
        };
        
        const titles = {
            error: 'Error',
            warning: 'Warning',
            success: 'Success',
            info: 'Information'
        };
        
        notification.innerHTML = `
            <div class="error-notification__icon">
                ${icons[type] || icons.info}
            </div>
            <div class="error-notification__content">
                <div class="error-notification__title">${titles[type]}</div>
                <div class="error-notification__message">${message}</div>
            </div>
            <button class="error-notification__close" aria-label="Close notification">
                <svg width="16" height="16" viewBox="0 0 24 24">
                    <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2"/>
                </svg>
            </button>
        `;
        
        // Add close functionality
        notification.querySelector('.error-notification__close').addEventListener('click', () => {
            this.removeNotification(notification);
        });
        
        // Add to container
        this.errorContainer.appendChild(notification);
        
        // Animate in
        requestAnimationFrame(() => {
            notification.classList.add('error-notification--visible');
        });
        
        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.removeNotification(notification);
            }, duration);
        }
        
        return notification;
    }
    
    removeNotification(notification) {
        notification.classList.remove('error-notification--visible');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }
}

// ===== EVENT HANDLERS =====
class ActivityMonitorEventHandlers {
    constructor() {
        this.chart = null;
        this.api = new ActivityMonitorAPI();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Date range selection
        document.querySelectorAll('.date-preset').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleDateRangeChange(e));
        });
        
        // Metric toggles
        document.querySelectorAll('.metric-toggle input').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => this.handleMetricToggle(e));
        });
        
        // User search
        const userSearch = document.getElementById('userSearch');
        if (userSearch) {
            userSearch.addEventListener('input', debounce(() => {
                this.loadActiveUsers();
            }, CONFIG.DEBOUNCE_DELAY));
        }
        
        // Role filter
        const roleFilter = document.getElementById('roleFilter');
        if (roleFilter) {
            roleFilter.addEventListener('change', () => {
                this.loadActiveUsers();
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeActiveModal();
            }
            
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '1': 
                        e.preventDefault();
                        this.selectDateRange('7d'); 
                        break;
                    case '2': 
                        e.preventDefault();
                        this.selectDateRange('30d'); 
                        break;
                    case '3': 
                        e.preventDefault();
                        this.selectDateRange('90d'); 
                        break;
                    case 'e': 
                        e.preventDefault();
                        this.triggerExport(); 
                        break;
                    case 'r': 
                        e.preventDefault();
                        this.refreshData(); 
                        break;
                }
            }
        });
    }
    
    handleDateRangeChange(e) {
        const btn = e.currentTarget;
        const range = btn.dataset.range;
        
        // Update active state
        document.querySelectorAll('.date-preset').forEach(b => {
            b.classList.remove('active');
        });
        btn.classList.add('active');
        
        if (range === 'custom') {
            this.showCustomDatePicker();
        } else {
            activityState.setState({ dateRange: range });
            this.chart.loadData();
        }
    }
    
    showCustomDatePicker() {
        const startInput = document.getElementById('customStartDate');
        const endInput = document.getElementById('customEndDate');
        
        startInput.classList.remove('hidden');
        endInput.classList.remove('hidden');
        
        // Set default values
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - 30);
        
        startInput.value = startDate.toISOString().split('T')[0];
        endInput.value = endDate.toISOString().split('T')[0];
        
        // Add change listeners
        const updateCustomRange = () => {
            activityState.setState({
                dateRange: 'custom',
                customDateStart: startInput.value,
                customDateEnd: endInput.value
            });
            this.chart.loadData();
        };
        
        startInput.addEventListener('change', updateCustomRange);
        endInput.addEventListener('change', updateCustomRange);
    }
    
    handleMetricToggle(e) {
        const checkbox = e.currentTarget;
        const metric = checkbox.dataset.metric;
        
        let activeMetrics = [...activityState.state.activeMetrics];
        
        if (checkbox.checked) {
            if (!activeMetrics.includes(metric)) {
                activeMetrics.push(metric);
            }
        } else {
            const index = activeMetrics.indexOf(metric);
            if (index > -1) {
                activeMetrics.splice(index, 1);
            }
        }
        
        activityState.setState({ activeMetrics });
        this.chart.loadData();
    }
    
    async loadActiveUsers() {
        try {
            const roleFilter = document.getElementById('roleFilter').value;
            const searchTerm = document.getElementById('userSearch').value.toLowerCase();
            
            const filters = {};
            if (roleFilter) {
                filters.role_filter = roleFilter;
            }
            
            const data = await this.api.fetchActiveUsers(filters);
            let users = data.data.sessions || [];
            
            // Filter by search term
            if (searchTerm) {
                users = users.filter(user => 
                    (user.username && user.username.toLowerCase().includes(searchTerm)) ||
                    (user.display_name && user.display_name.toLowerCase().includes(searchTerm))
                );
            }
            
            activityState.setState({ activeUsers: users });
            this.renderActiveUsers(users);
            
        } catch (error) {
            console.error('Error loading active users:', error);
            errorHandler.showError('Failed to load active users');
        }
    }
    
    renderActiveUsers(users) {
        const tbody = document.getElementById('activeUsersBody');
        if (!tbody) return;
        
        if (users.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7">
                        <div class="empty-state">
                            <div class="empty-state-message">No active users found</div>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = users.map(user => {
            const activityScore = this.calculateActivityScore(user);
            
            return `
                <tr>
                    <td>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #006dfe, #0056cc);"></div>
                            <div>
                                <div style="font-weight: 600;">${user.display_name || user.username}</div>
                                <div style="font-size: 12px; color: #64748b;">@${user.username}</div>
                            </div>
                        </div>
                    </td>
                    <td>
                        <span style="display: inline-block; padding: 4px 8px; background: ${this.getRoleColor(user.role)}; color: white; border-radius: 4px; font-size: 12px; font-weight: 600; text-transform: uppercase;">
                            ${user.role}
                        </span>
                    </td>
                    <td>
                        <div class="activity-score">
                            <div class="activity-score-bar">
                                <div class="activity-score-fill" style="width: ${activityScore}%"></div>
                            </div>
                            <span class="activity-score-value">${activityScore}%</span>
                        </div>
                    </td>
                    <td>${user.page_title || user.current_page || 'Unknown'}</td>
                    <td>${this.formatTimeAgo(user.last_activity)}</td>
                    <td>${this.formatDuration(user.session_duration_minutes)}</td>
                    <td>
                        <button class="view-history-btn" onclick="openUserHistory(${user.user_id}, '${user.username}', '${user.role}')">
                            View History
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }
    
    calculateActivityScore(user) {
        // Simple activity score calculation
        let score = 0;
        
        // Recent activity (max 40 points)
        const minutesSinceActivity = (Date.now() - new Date(user.last_activity)) / 1000 / 60;
        if (minutesSinceActivity < 5) score += 40;
        else if (minutesSinceActivity < 15) score += 30;
        else if (minutesSinceActivity < 30) score += 20;
        else if (minutesSinceActivity < 60) score += 10;
        
        // Session duration (max 30 points)
        const sessionMinutes = user.session_duration_minutes || 0;
        if (sessionMinutes > 60) score += 30;
        else if (sessionMinutes > 30) score += 20;
        else if (sessionMinutes > 15) score += 10;
        else if (sessionMinutes > 5) score += 5;
        
        // Page views (max 30 points) - simplified since we don't have this data
        score += Math.min(30, Math.floor(sessionMinutes / 2));
        
        return Math.min(100, score);
    }
    
    getRoleColor(role) {
        const colors = {
            admin: '#dc3545',
            manager: '#006dfe',
            driver: '#28a745',
            viewer: '#6c757d'
        };
        return colors[role] || '#6c757d';
    }
    
    formatTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const seconds = Math.floor((now - time) / 1000);
        
        if (seconds < 60) return 'just now';
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes}m ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        const days = Math.floor(hours / 24);
        return `${days}d ago`;
    }
    
    formatDuration(minutes) {
        if (!minutes) return '0m';
        if (minutes < 60) return `${Math.floor(minutes)}m`;
        const hours = Math.floor(minutes / 60);
        const mins = Math.floor(minutes % 60);
        return `${hours}h ${mins}m`;
    }
    
    selectDateRange(range) {
        const btn = document.querySelector(`.date-preset[data-range="${range}"]`);
        if (btn) {
            btn.click();
        }
    }
    
    triggerExport() {
        exportTrends();
    }
    
    async refreshData() {
        await Promise.all([
            this.chart.loadData(),
            this.loadActiveUsers()
        ]);
        
        // Update last refresh time
        const lastRefreshEl = document.getElementById('lastRefresh');
        if (lastRefreshEl) {
            lastRefreshEl.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        }
        
        errorHandler.showError('Data refreshed successfully', 'success', 2000);
    }
    
    closeActiveModal() {
        const modal = document.getElementById('userHistoryModal');
        if (modal && !modal.classList.contains('hidden')) {
            closeUserHistoryModal();
        }
    }
    
    startRealTimeUpdates() {
        setInterval(() => {
            this.refreshData();
        }, CONFIG.REFRESH_INTERVAL);
    }
}

// ===== MODAL MANAGEMENT =====
let currentUserId = null;
let currentUserPage = 1;

async function openUserHistory(userId, username, role) {
    const modal = document.getElementById('userHistoryModal');
    const modalUserName = document.getElementById('modalUserName');
    const modalUserRole = document.getElementById('modalUserRole');
    
    currentUserId = userId;
    currentUserPage = 1;
    
    // Update modal header
    modalUserName.textContent = username;
    modalUserRole.textContent = role;
    
    // Show modal
    modal.classList.remove('hidden');
    
    // Load history
    await loadUserHistoryData();
}

async function loadUserHistoryData() {
    const timeline = document.getElementById('historyTimeline');
    timeline.innerHTML = '<div class="spinner-large"></div>';
    
    try {
        const api = new ActivityMonitorAPI();
        const filters = {
            startDate: document.getElementById('historyStartDate').value,
            endDate: document.getElementById('historyEndDate').value,
            actionType: document.getElementById('actionTypeFilter').value,
            offset: (currentUserPage - 1) * CONFIG.ITEMS_PER_PAGE
        };
        
        const data = await api.fetchUserHistory(currentUserId, filters);
        const activities = data.data.activities || [];
        
        // Update pagination
        const totalItems = data.data.total || activities.length;
        const totalPages = Math.ceil(totalItems / CONFIG.ITEMS_PER_PAGE);
        document.getElementById('currentPage').textContent = currentUserPage;
        document.getElementById('totalPages').textContent = totalPages;
        document.getElementById('prevPage').disabled = currentUserPage === 1;
        document.getElementById('nextPage').disabled = currentUserPage >= totalPages;
        
        // Render timeline
        if (activities.length === 0) {
            timeline.innerHTML = '<div class="empty-state"><div class="empty-state-message">No activity history found</div></div>';
        } else {
            timeline.innerHTML = activities.map(activity => {
                let actionText = activity.action_type || 'Unknown Action';
                let detailsText = '';
                
                switch (activity.action_type) {
                    case 'page_view':
                        actionText = 'Page View';
                        detailsText = activity.page_title || activity.page_url || 'Unknown Page';
                        break;
                    case 'api_call':
                        actionText = 'API Call';
                        detailsText = activity.page_url || 'Unknown Endpoint';
                        break;
                    case 'login':
                        actionText = 'Login';
                        detailsText = `from ${activity.ip_address || 'Unknown IP'}`;
                        break;
                    case 'logout':
                        actionText = 'Logout';
                        detailsText = 'Session ended';
                        break;
                    default:
                        detailsText = activity.page_url || activity.page_title || '';
                }
                
                if (activity.duration_ms) {
                    detailsText += ` (${activity.duration_ms}ms)`;
                }
                
                return `
                    <div class="timeline-item-enhanced">
                        <div class="timeline-time">${formatDateTime(activity.timestamp)}</div>
                        <div class="timeline-content">
                            <div class="timeline-action">${actionText}</div>
                            <div class="timeline-details">${detailsText}</div>
                        </div>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Error loading user history:', error);
        timeline.innerHTML = '<div class="empty-state"><div class="empty-state-message">Failed to load activity history</div></div>';
    }
}

function closeUserHistoryModal() {
    const modal = document.getElementById('userHistoryModal');
    modal.classList.add('hidden');
    currentUserId = null;
    currentUserPage = 1;
}

function applyHistoryFilters() {
    currentUserPage = 1;
    loadUserHistoryData();
}

function previousPage() {
    if (currentUserPage > 1) {
        currentUserPage--;
        loadUserHistoryData();
    }
}

function nextPage() {
    currentUserPage++;
    loadUserHistoryData();
}

async function exportUserHistory() {
    try {
        const api = new ActivityMonitorAPI();
        await api.exportData('csv', {
            userId: currentUserId,
            dateRange: 'all'
        });
        errorHandler.showError('Export started', 'success');
    } catch (error) {
        console.error('Export failed:', error);
        errorHandler.showError('Export failed', 'error');
    }
}

async function exportTrends() {
    try {
        const api = new ActivityMonitorAPI();
        await api.exportData('csv', {
            dateRange: activityState.state.dateRange,
            metrics: activityState.state.activeMetrics
        });
        errorHandler.showError('Export started', 'success');
    } catch (error) {
        console.error('Export failed:', error);
        errorHandler.showError('Export failed', 'error');
    }
}

// ===== UTILITY FUNCTIONS =====
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatDateTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ===== INITIALIZATION =====
let trendsChart = null;
let eventHandlers = null;
let errorHandler = null;

async function checkAdminAccess() {
    try {
        const response = await fetch('/api/auth/current-user', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            window.location.href = '/pages/login.html?return=' + encodeURIComponent(window.location.pathname);
            return false;
        }
        
        const data = await response.json();
        
        if (data.user.role !== 'admin') {
            alert('Access Denied: Admin privileges required');
            window.location.href = '/';
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/pages/login.html';
        return false;
    }
}

async function initActivityMonitor() {
    // Check admin access
    const hasAccess = await checkAdminAccess();
    if (!hasAccess) return;
    
    // Initialize components
    errorHandler = new ActivityMonitorErrorHandler();
    trendsChart = new ActivityTrendsChart('trendsChart');
    eventHandlers = new ActivityMonitorEventHandlers();
    
    // Set chart reference
    eventHandlers.chart = trendsChart;
    
    // Subscribe to state changes
    activityState.subscribe((state) => {
        console.log('State updated:', state);
    });
    
    // Load initial data
    try {
        await Promise.all([
            trendsChart.loadData(),
            eventHandlers.loadActiveUsers()
        ]);
        
        // Start real-time updates
        eventHandlers.startRealTimeUpdates();
        
        // Show success indicator
        errorHandler.showError('Activity Monitor Enhanced loaded successfully', 'success', 3000);
        
        // Update last refresh time
        const lastRefreshEl = document.getElementById('lastRefresh');
        if (lastRefreshEl) {
            lastRefreshEl.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        }
        
    } catch (error) {
        errorHandler.showError('Failed to initialize Activity Monitor', 'error');
        console.error('Initialization error:', error);
    }
}

// Start the application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initActivityMonitor);
} else {
    initActivityMonitor();
}