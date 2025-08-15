# Activity Monitor Enhancement - Frontend Implementation Plan

## Executive Summary
This document provides a comprehensive technical specification for implementing the Activity Monitor Enhancement feature, focusing on desktop-only optimization with rich interactions, detailed analytics, and premium user experience.

---

## 1. COMPONENT SPECIFICATIONS

### 1.1 Trends Graph Component

#### Component Structure
```html
<div class="trends-graph-container">
    <div class="trends-header">
        <h3 class="trends-title">Activity Trends</h3>
        <div class="trends-controls">
            <div class="date-range-selector">
                <button class="date-preset active" data-range="7d">7 Days</button>
                <button class="date-preset" data-range="30d">30 Days</button>
                <button class="date-preset" data-range="90d">90 Days</button>
                <button class="date-preset" data-range="custom">Custom</button>
                <input type="date" class="date-input hidden" id="customStartDate">
                <input type="date" class="date-input hidden" id="customEndDate">
            </div>
            <div class="metric-toggles">
                <label class="metric-toggle">
                    <input type="checkbox" checked data-metric="active_users">
                    <span class="toggle-label">Active Users</span>
                </label>
                <label class="metric-toggle">
                    <input type="checkbox" checked data-metric="page_views">
                    <span class="toggle-label">Page Views</span>
                </label>
                <label class="metric-toggle">
                    <input type="checkbox" data-metric="avg_session">
                    <span class="toggle-label">Avg Session</span>
                </label>
                <label class="metric-toggle">
                    <input type="checkbox" data-metric="api_calls">
                    <span class="toggle-label">API Calls</span>
                </label>
            </div>
        </div>
    </div>
    <div class="trends-graph-wrapper">
        <canvas id="trendsChart" width="1200" height="400"></canvas>
        <div class="graph-loading-overlay hidden">
            <div class="spinner-large"></div>
            <span class="loading-text">Loading trends data...</span>
        </div>
    </div>
    <div class="trends-legend" id="customLegend"></div>
</div>
```

#### Component Requirements
- **Canvas Dimensions**: 1200x400px base (responsive scaling)
- **Interactive Tooltips**: Multi-metric display on hover
- **Zoom Controls**: Click-and-drag to zoom time ranges
- **Data Points**: Clickable for drill-down to specific time period
- **Animation**: Smooth line drawing on initial load (800ms duration)
- **Update Frequency**: Real-time updates every 30 seconds

### 1.2 User History Modal Component

#### Modal Structure
```html
<div class="modal-overlay" id="userHistoryModal">
    <div class="modal-container">
        <div class="modal-header">
            <div class="modal-title-section">
                <h2 class="modal-title">User Activity History</h2>
                <div class="user-info-badge">
                    <img src="/api/users/{id}/avatar" class="user-avatar">
                    <div class="user-details">
                        <span class="user-name">{display_name}</span>
                        <span class="user-role">{role}</span>
                    </div>
                </div>
            </div>
            <button class="modal-close" aria-label="Close">×</button>
        </div>
        <div class="modal-body">
            <div class="history-filters">
                <input type="date" class="date-filter" id="historyStartDate">
                <input type="date" class="date-filter" id="historyEndDate">
                <select class="action-filter" id="actionTypeFilter">
                    <option value="">All Actions</option>
                    <option value="page_view">Page Views</option>
                    <option value="api_call">API Calls</option>
                    <option value="data_change">Data Changes</option>
                </select>
                <button class="btn btn-secondary" onclick="applyHistoryFilters()">Apply Filters</button>
            </div>
            <div class="history-timeline-enhanced">
                <!-- Timeline items dynamically inserted here -->
            </div>
            <div class="history-pagination">
                <button class="pagination-btn" id="prevPage">Previous</button>
                <span class="pagination-info">Page <span id="currentPage">1</span> of <span id="totalPages">1</span></span>
                <button class="pagination-btn" id="nextPage">Next</button>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-primary export-btn" onclick="exportUserHistory()">
                Export Full History
            </button>
            <button class="btn btn-secondary" onclick="closeUserHistoryModal()">Close</button>
        </div>
    </div>
</div>
```

#### Modal Specifications
- **Width**: 900px (desktop)
- **Max Height**: 80vh with internal scrolling
- **Backdrop**: Semi-transparent (rgba(0, 0, 0, 0.6))
- **Animation**: Slide-up entrance (300ms cubic-bezier)
- **Pagination**: 50 items per page
- **Escape Key**: Closes modal

### 1.3 Control Components

#### Date Range Picker
```javascript
class DateRangePicker {
    constructor(container) {
        this.container = container;
        this.startDate = null;
        this.endDate = null;
        this.presets = {
            '7d': () => ({ start: moment().subtract(7, 'days'), end: moment() }),
            '30d': () => ({ start: moment().subtract(30, 'days'), end: moment() }),
            '90d': () => ({ start: moment().subtract(90, 'days'), end: moment() }),
            'custom': () => this.showCustomPicker()
        };
    }
    
    showCustomPicker() {
        // Calendar UI implementation
    }
}
```

#### Export Button Component
```javascript
class ExportManager {
    constructor() {
        this.formats = ['csv', 'json', 'pdf'];
        this.currentData = null;
    }
    
    async exportData(format, filters) {
        const data = await this.fetchExportData(filters);
        switch(format) {
            case 'csv': return this.exportCSV(data);
            case 'json': return this.exportJSON(data);
            case 'pdf': return this.exportPDF(data);
        }
    }
}
```

---

## 2. VISUAL DESIGN SPECIFICATIONS

### 2.1 Color System

```css
:root {
    /* Primary Palette - Activity Monitor Specific */
    --am-primary: #006dfe;
    --am-primary-dark: #0056cc;
    --am-primary-light: #4d9fff;
    --am-primary-pale: #e7f3ff;
    
    /* Metric Colors */
    --am-metric-users: #006dfe;      /* Blue - Active Users */
    --am-metric-views: #28a745;      /* Green - Page Views */
    --am-metric-session: #ffc107;    /* Amber - Session Duration */
    --am-metric-api: #17a2b8;        /* Cyan - API Calls */
    
    /* Status Colors */
    --am-status-active: #28a745;
    --am-status-idle: #ffc107;
    --am-status-inactive: #6c757d;
    
    /* Chart Gradients */
    --am-gradient-users-start: rgba(0, 109, 254, 0.4);
    --am-gradient-users-end: rgba(0, 109, 254, 0.05);
    --am-gradient-views-start: rgba(40, 167, 69, 0.4);
    --am-gradient-views-end: rgba(40, 167, 69, 0.05);
    
    /* Shadows */
    --am-shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.06);
    --am-shadow-md: 0 4px 8px rgba(0, 0, 0, 0.08);
    --am-shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.1);
    --am-shadow-modal: 0 20px 40px rgba(0, 0, 0, 0.15);
}
```

### 2.2 Typography

```css
/* Heading Hierarchy */
.trends-title {
    font-size: 24px;
    font-weight: 700;
    line-height: 1.2;
    letter-spacing: -0.02em;
    color: #1a1a1a;
}

.modal-title {
    font-size: 28px;
    font-weight: 700;
    line-height: 1.2;
    letter-spacing: -0.02em;
    color: #1a1a1a;
}

.section-subtitle {
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
}

/* Body Text */
.metric-value {
    font-size: 32px;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    line-height: 1;
}

.metric-label {
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
}

/* Chart Typography */
.chart-axis-label {
    font-size: 12px;
    font-weight: 500;
    color: #6c757d;
}

.chart-tooltip-text {
    font-size: 13px;
    font-weight: 600;
    color: white;
}
```

### 2.3 Spacing System

```css
/* Base unit: 8px */
.spacing {
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 16px;
    --space-lg: 24px;
    --space-xl: 32px;
    --space-2xl: 48px;
    --space-3xl: 64px;
}

/* Component Spacing */
.trends-graph-container {
    padding: var(--space-lg);
    margin-bottom: var(--space-xl);
}

.trends-controls {
    margin-bottom: var(--space-lg);
    gap: var(--space-lg);
}

.modal-container {
    padding: var(--space-xl);
}

.history-timeline-item {
    padding: var(--space-md);
    margin-bottom: var(--space-md);
}
```

### 2.4 Graph Styling

```javascript
// Chart.js Configuration
const chartConfig = {
    type: 'line',
    options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        plugins: {
            legend: {
                display: false // Custom legend
            },
            tooltip: {
                backgroundColor: 'rgba(26, 26, 26, 0.95)',
                padding: 16,
                titleFont: {
                    size: 14,
                    weight: 600
                },
                bodyFont: {
                    size: 13
                },
                cornerRadius: 8,
                displayColors: true,
                callbacks: {
                    // Custom tooltip formatting
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: true,
                    color: 'rgba(0, 0, 0, 0.05)',
                    drawBorder: false
                },
                ticks: {
                    font: {
                        size: 12
                    },
                    color: '#6c757d'
                }
            },
            y: {
                grid: {
                    display: true,
                    color: 'rgba(0, 0, 0, 0.05)',
                    drawBorder: false
                },
                ticks: {
                    font: {
                        size: 12
                    },
                    color: '#6c757d'
                }
            }
        }
    },
    datasets: [
        {
            label: 'Active Users',
            borderColor: '#006dfe',
            backgroundColor: createGradient('#006dfe'),
            borderWidth: 3,
            tension: 0.4,
            pointRadius: 4,
            pointHoverRadius: 6,
            pointBackgroundColor: '#fff',
            pointBorderWidth: 2,
            pointHoverBorderWidth: 3
        }
    ]
};
```

---

## 3. INTERACTION SPECIFICATIONS

### 3.1 Graph Hover Behaviors

```javascript
// Hover interaction handler
class GraphInteractionManager {
    constructor(chart) {
        this.chart = chart;
        this.setupInteractions();
    }
    
    setupInteractions() {
        // Point hover
        this.chart.options.onHover = (event, activeElements) => {
            if (activeElements.length > 0) {
                this.showDetailedTooltip(activeElements[0]);
                this.highlightDataPoint(activeElements[0]);
            }
        };
        
        // Click for drill-down
        this.chart.options.onClick = (event, activeElements) => {
            if (activeElements.length > 0) {
                const dataPoint = activeElements[0];
                this.drillDown(dataPoint);
            }
        };
    }
    
    showDetailedTooltip(element) {
        // Enhanced tooltip with multiple metrics
        const tooltip = {
            title: formatDate(element.label),
            metrics: [
                { label: 'Active Users', value: element.dataset.data[element.index] },
                { label: 'Peak Hour', value: getPeakHour(element.index) },
                { label: 'Total Sessions', value: getTotalSessions(element.index) }
            ]
        };
        this.renderTooltip(tooltip);
    }
    
    drillDown(dataPoint) {
        // Open modal with hourly breakdown for selected day
        const date = dataPoint.label;
        openDrillDownModal(date);
    }
}
```

### 3.2 Modal Animations

```css
/* Modal entrance animation */
@keyframes modalSlideUp {
    from {
        opacity: 0;
        transform: translateY(100px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes modalBackdropFade {
    from { opacity: 0; }
    to { opacity: 1; }
}

.modal-overlay {
    animation: modalBackdropFade 200ms ease-out;
}

.modal-container {
    animation: modalSlideUp 300ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Modal exit animation */
.modal-overlay.closing {
    animation: modalBackdropFadeOut 200ms ease-out forwards;
}

.modal-container.closing {
    animation: modalSlideDown 200ms ease-in forwards;
}

@keyframes modalSlideDown {
    from {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
    to {
        opacity: 0;
        transform: translateY(50px) scale(0.98);
    }
}

@keyframes modalBackdropFadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
}
```

### 3.3 Data Export Flow

```javascript
class ExportWorkflow {
    constructor() {
        this.setupExportButton();
    }
    
    setupExportButton() {
        const exportBtn = document.querySelector('.export-btn');
        exportBtn.addEventListener('click', () => this.showExportOptions());
    }
    
    showExportOptions() {
        const dropdown = document.createElement('div');
        dropdown.className = 'export-dropdown';
        dropdown.innerHTML = `
            <div class="export-option" data-format="csv">
                <svg class="export-icon"><!-- CSV icon --></svg>
                <div class="export-details">
                    <span class="export-format">CSV Format</span>
                    <span class="export-desc">Spreadsheet compatible</span>
                </div>
            </div>
            <div class="export-option" data-format="json">
                <svg class="export-icon"><!-- JSON icon --></svg>
                <div class="export-details">
                    <span class="export-format">JSON Format</span>
                    <span class="export-desc">Developer friendly</span>
                </div>
            </div>
            <div class="export-option" data-format="pdf">
                <svg class="export-icon"><!-- PDF icon --></svg>
                <div class="export-details">
                    <span class="export-format">PDF Report</span>
                    <span class="export-desc">Formatted report with charts</span>
                </div>
            </div>
        `;
        
        dropdown.addEventListener('click', (e) => {
            const option = e.target.closest('.export-option');
            if (option) {
                this.executeExport(option.dataset.format);
            }
        });
    }
    
    async executeExport(format) {
        // Show progress indicator
        this.showExportProgress();
        
        try {
            const data = await this.gatherExportData();
            const file = await this.formatData(data, format);
            this.downloadFile(file, format);
        } catch (error) {
            this.showExportError(error);
        }
    }
}
```

### 3.4 Keyboard Navigation

```javascript
class KeyboardNavigation {
    constructor() {
        this.setupKeyboardShortcuts();
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Modal controls
            if (e.key === 'Escape') {
                this.closeActiveModal();
            }
            
            // Date range shortcuts
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '1': this.selectDateRange('7d'); break;
                    case '2': this.selectDateRange('30d'); break;
                    case '3': this.selectDateRange('90d'); break;
                    case 'e': this.triggerExport(); break;
                    case 'r': this.refreshData(); break;
                }
            }
            
            // Tab navigation in modal
            if (this.isModalOpen()) {
                this.handleModalTabbing(e);
            }
        });
    }
    
    handleModalTabbing(e) {
        if (e.key === 'Tab') {
            const focusableElements = this.getFocusableElements();
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            if (e.shiftKey && document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    }
}
```

---

## 4. HTML/CSS STRUCTURE

### 4.1 Semantic HTML Structure

```html
<!-- Main Activity Monitor Enhancement Section -->
<section class="activity-monitor-enhanced" role="region" aria-label="Activity Analytics">
    <!-- Trends Section -->
    <article class="trends-section" role="article" aria-label="Activity Trends">
        <header class="trends-header">
            <h2 id="trends-title">Activity Trends</h2>
            <nav class="trends-navigation" role="navigation" aria-label="Trend controls">
                <!-- Date range controls -->
                <fieldset class="date-range-controls" role="group" aria-label="Date range selection">
                    <legend class="sr-only">Select date range</legend>
                    <!-- Date buttons -->
                </fieldset>
                <!-- Metric toggles -->
                <fieldset class="metric-controls" role="group" aria-label="Metric selection">
                    <legend class="sr-only">Toggle metrics</legend>
                    <!-- Metric checkboxes -->
                </fieldset>
            </nav>
        </header>
        
        <div class="trends-visualization" role="img" aria-label="Activity trends chart">
            <canvas id="trendsChart" role="img" aria-describedby="chart-description"></canvas>
            <p id="chart-description" class="sr-only">
                Interactive line chart showing activity trends over time
            </p>
        </div>
        
        <aside class="trends-insights" role="complementary" aria-label="Trend insights">
            <!-- Key insights and statistics -->
        </aside>
    </article>
    
    <!-- Enhanced Active Users Table -->
    <article class="users-section" role="article" aria-label="Active Users">
        <table class="users-table-enhanced" role="table" aria-label="Active users with history">
            <caption class="sr-only">List of currently active users with session details</caption>
            <thead>
                <tr role="row">
                    <th role="columnheader" aria-sort="none">User</th>
                    <th role="columnheader" aria-sort="none">Activity Score</th>
                    <th role="columnheader" aria-sort="none">Last Action</th>
                    <th role="columnheader">Actions</th>
                </tr>
            </thead>
            <tbody role="rowgroup">
                <!-- Dynamic user rows -->
            </tbody>
        </table>
    </article>
</section>
```

### 4.2 CSS Architecture

```css
/* BEM Methodology with Utility Classes */

/* Block: Trends Graph */
.trends-graph {
    position: relative;
    background: white;
    border-radius: 12px;
    box-shadow: var(--am-shadow-md);
    overflow: hidden;
}

/* Element: Graph Header */
.trends-graph__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-lg);
    border-bottom: 1px solid #e2e8f0;
    background: linear-gradient(180deg, #fafbfc, #ffffff);
}

/* Element: Graph Canvas */
.trends-graph__canvas {
    position: relative;
    padding: var(--space-lg);
    min-height: 400px;
}

/* Modifier: Loading State */
.trends-graph--loading .trends-graph__canvas {
    opacity: 0.5;
    pointer-events: none;
}

/* Component: Date Range Selector */
.date-range {
    display: inline-flex;
    background: #f8f9fa;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
}

.date-range__button {
    padding: 8px 16px;
    border: none;
    background: transparent;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s ease;
}

.date-range__button--active {
    background: white;
    color: var(--am-primary);
    box-shadow: var(--am-shadow-sm);
}

.date-range__button:hover:not(.date-range__button--active) {
    color: #374151;
    background: rgba(0, 0, 0, 0.03);
}

/* Utility Classes */
.u-flex { display: flex; }
.u-flex-center { align-items: center; justify-content: center; }
.u-flex-between { justify-content: space-between; }
.u-gap-sm { gap: var(--space-sm); }
.u-gap-md { gap: var(--space-md); }
.u-gap-lg { gap: var(--space-lg); }
.u-mt-lg { margin-top: var(--space-lg); }
.u-mb-lg { margin-bottom: var(--space-lg); }
.u-text-center { text-align: center; }
.u-text-muted { color: #64748b; }
.u-font-bold { font-weight: 700; }
.u-hidden { display: none !important; }
.u-sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
```

### 4.3 Grid/Flexbox Layout

```css
/* Main Layout Grid */
.activity-monitor-enhanced {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--space-xl);
    max-width: 1600px;
    margin: 0 auto;
    padding: var(--space-xl);
}

/* Trends Section Layout */
.trends-section {
    display: grid;
    grid-template-rows: auto 1fr auto;
    gap: var(--space-lg);
}

.trends-header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: var(--space-lg);
}

.trends-navigation {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-lg);
    align-items: center;
}

/* Controls Layout */
.date-range-controls,
.metric-controls {
    display: flex;
    gap: var(--space-sm);
    align-items: center;
}

/* Table Layout Enhancement */
.users-table-enhanced {
    display: table;
    width: 100%;
    table-layout: fixed;
}

.users-table-enhanced thead {
    position: sticky;
    top: 0;
    z-index: 10;
    background: linear-gradient(180deg, #f8fafc, #f1f5f9);
}

/* Modal Layout */
.modal-container {
    display: grid;
    grid-template-rows: auto 1fr auto;
    max-height: 80vh;
    width: 900px;
}

.modal-body {
    overflow-y: auto;
    padding: var(--space-xl);
}

.history-filters {
    display: flex;
    gap: var(--space-md);
    margin-bottom: var(--space-lg);
    flex-wrap: wrap;
}

.history-timeline-enhanced {
    display: flex;
    flex-direction: column;
    gap: var(--space-md);
}
```

### 4.4 Z-Index Layering

```css
/* Z-Index Scale */
:root {
    --z-base: 0;
    --z-dropdown: 100;
    --z-sticky: 200;
    --z-fixed: 300;
    --z-modal-backdrop: 400;
    --z-modal: 500;
    --z-tooltip: 600;
    --z-notification: 700;
}

/* Applied Z-Index */
.trends-graph__canvas { z-index: var(--z-base); }
.date-range-dropdown { z-index: var(--z-dropdown); }
.users-table-enhanced thead { z-index: var(--z-sticky); }
.export-dropdown { z-index: var(--z-dropdown); }
.modal-overlay { z-index: var(--z-modal-backdrop); }
.modal-container { z-index: var(--z-modal); }
.chart-tooltip { z-index: var(--z-tooltip); }
.notification-toast { z-index: var(--z-notification); }
```

---

## 5. JAVASCRIPT IMPLEMENTATION GUIDE

### 5.1 Chart.js Setup and Configuration

```javascript
// ActivityTrendsChart.js
class ActivityTrendsChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.chart = null;
        this.currentData = null;
        this.activeMetrics = ['active_users', 'page_views'];
        this.dateRange = '7d';
        
        this.initChart();
        this.setupEventListeners();
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
                    duration: 800,
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
                                return moment(tooltipItems[0].label).format('MMM DD, YYYY');
                            },
                            label: (context) => {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y;
                                return `${label}: ${this.formatValue(value, context.dataset.metric)}`;
                            },
                            afterBody: (tooltipItems) => {
                                // Add additional context
                                const index = tooltipItems[0].dataIndex;
                                return this.getAdditionalContext(index);
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
        
        return gradients;
    }
    
    async loadData() {
        this.showLoading(true);
        
        try {
            const params = {
                range: this.dateRange,
                metrics: this.activeMetrics.join(',')
            };
            
            const response = await fetch(`/api/admin/activity/trends?${new URLSearchParams(params)}`, {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error('Failed to load trends data');
            
            const data = await response.json();
            this.updateChart(data.data);
            
        } catch (error) {
            console.error('Error loading trends:', error);
            this.showError('Failed to load trends data');
        } finally {
            this.showLoading(false);
        }
    }
    
    updateChart(data) {
        const datasets = [];
        const gradients = this.createGradients();
        
        if (this.activeMetrics.includes('active_users')) {
            datasets.push({
                label: 'Active Users',
                data: data.active_users,
                borderColor: '#006dfe',
                backgroundColor: gradients.activeUsers,
                borderWidth: 3,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#fff',
                pointBorderWidth: 2,
                metric: 'active_users'
            });
        }
        
        if (this.activeMetrics.includes('page_views')) {
            datasets.push({
                label: 'Page Views',
                data: data.page_views,
                borderColor: '#28a745',
                backgroundColor: gradients.pageViews,
                borderWidth: 3,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#fff',
                pointBorderWidth: 2,
                metric: 'page_views'
            });
        }
        
        this.chart.data = {
            labels: data.labels,
            datasets: datasets
        };
        
        this.chart.update('active');
        this.updateCustomLegend();
    }
    
    handleDataPointClick(element) {
        const date = this.chart.data.labels[element.index];
        const metric = element.dataset.metric;
        
        // Open drill-down modal
        this.openDrillDownModal(date, metric);
    }
    
    openDrillDownModal(date, metric) {
        const modal = new DrillDownModal(date, metric);
        modal.show();
    }
}
```

### 5.2 Event Handlers

```javascript
// EventHandlers.js
class ActivityMonitorEventHandlers {
    constructor() {
        this.chart = null;
        this.exportManager = new ExportManager();
        this.modalManager = new ModalManager();
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
        
        // User row clicks for history
        document.addEventListener('click', (e) => {
            if (e.target.closest('.view-history-btn')) {
                const userId = e.target.closest('.view-history-btn').dataset.userId;
                this.openUserHistory(userId);
            }
        });
        
        // Export button
        document.querySelector('.export-trends-btn').addEventListener('click', () => {
            this.handleExport();
        });
        
        // Real-time updates
        this.startRealTimeUpdates();
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
            this.chart.dateRange = range;
            this.chart.loadData();
        }
    }
    
    handleMetricToggle(e) {
        const checkbox = e.currentTarget;
        const metric = checkbox.dataset.metric;
        
        if (checkbox.checked) {
            this.chart.activeMetrics.push(metric);
        } else {
            const index = this.chart.activeMetrics.indexOf(metric);
            if (index > -1) {
                this.chart.activeMetrics.splice(index, 1);
            }
        }
        
        this.chart.loadData();
    }
    
    async openUserHistory(userId) {
        // Show loading state
        this.modalManager.showLoading();
        
        try {
            const response = await fetch(`/api/admin/activity/history/${userId}?limit=500`, {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error('Failed to load user history');
            
            const data = await response.json();
            this.modalManager.showUserHistory(data.data);
            
        } catch (error) {
            console.error('Error loading user history:', error);
            this.modalManager.showError('Failed to load user history');
        }
    }
    
    handleExport() {
        const exportOptions = {
            dateRange: this.chart.dateRange,
            metrics: this.chart.activeMetrics,
            format: 'csv' // Can be made selectable
        };
        
        this.exportManager.exportTrends(exportOptions);
    }
    
    startRealTimeUpdates() {
        // Update every 30 seconds
        setInterval(() => {
            this.refreshData();
        }, 30000);
    }
    
    async refreshData() {
        // Don't show loading indicator for background refresh
        await this.chart.loadData();
        
        // Update last refresh timestamp
        document.getElementById('lastRefresh').textContent = 
            `Last updated: ${moment().format('HH:mm:ss')}`;
    }
}
```

### 5.3 State Management

```javascript
// StateManager.js
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
        // Save user preferences to localStorage
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
```

### 5.4 API Integration

```javascript
// ActivityMonitorAPI.js
class ActivityMonitorAPI {
    constructor() {
        this.baseURL = '/api/admin/activity';
        this.headers = {
            'Content-Type': 'application/json'
        };
    }
    
    async fetchTrends(params) {
        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(`${this.baseURL}/trends?${queryString}`, {
            credentials: 'include',
            headers: this.headers
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async fetchUserHistory(userId, filters = {}) {
        const params = {
            limit: filters.limit || 100,
            offset: filters.offset || 0,
            start_date: filters.startDate,
            end_date: filters.endDate,
            action_type: filters.actionType
        };
        
        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(`${this.baseURL}/history/${userId}?${queryString}`, {
            credentials: 'include',
            headers: this.headers
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
            metrics: filters.metrics.join(',')
        };
        
        const response = await fetch(`${this.baseURL}/export`, {
            method: 'POST',
            credentials: 'include',
            headers: this.headers,
            body: JSON.stringify(params)
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
```

### 5.5 Error Handling

```javascript
// ErrorHandler.js
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
        
        notification.innerHTML = `
            <div class="error-notification__icon">
                ${this.getIcon(type)}
            </div>
            <div class="error-notification__content">
                <div class="error-notification__title">${this.getTitle(type)}</div>
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
    
    getIcon(type) {
        const icons = {
            error: '<svg><!-- Error icon --></svg>',
            warning: '<svg><!-- Warning icon --></svg>',
            success: '<svg><!-- Success icon --></svg>',
            info: '<svg><!-- Info icon --></svg>'
        };
        return icons[type] || icons.info;
    }
    
    getTitle(type) {
        const titles = {
            error: 'Error',
            warning: 'Warning',
            success: 'Success',
            info: 'Information'
        };
        return titles[type] || 'Notification';
    }
    
    handleAPIError(error) {
        console.error('API Error:', error);
        
        let message = 'An unexpected error occurred';
        
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    message = 'Your session has expired. Please log in again.';
                    // Redirect to login after delay
                    setTimeout(() => {
                        window.location.href = '/pages/login.html';
                    }, 2000);
                    break;
                case 403:
                    message = 'You do not have permission to perform this action.';
                    break;
                case 404:
                    message = 'The requested resource was not found.';
                    break;
                case 429:
                    message = 'Too many requests. Please try again later.';
                    break;
                case 500:
                    message = 'Server error. Please try again later.';
                    break;
                default:
                    message = error.message || message;
            }
        }
        
        this.showError(message, 'error');
    }
}

// Global error handler instance
const errorHandler = new ActivityMonitorErrorHandler();
```

---

## 6. STEP-BY-STEP IMPLEMENTATION ORDER

### Phase 1: Foundation (Days 1-2)

1. **Create HTML Structure**
   - Add trends section to existing activity-monitor.html
   - Implement semantic HTML with ARIA labels
   - Add container elements for chart and controls

2. **Implement CSS Framework**
   - Add new CSS variables for Activity Monitor enhancements
   - Create BEM-structured component styles
   - Implement responsive grid layout
   - Add animation keyframes

3. **Setup Chart.js**
   - Install Chart.js via CDN or npm
   - Create ActivityTrendsChart class
   - Implement basic line chart with dummy data
   - Test rendering and responsiveness

### Phase 2: Core Functionality (Days 3-4)

4. **Implement Date Range Controls**
   - Create DateRangePicker class
   - Wire up preset buttons (7d, 30d, 90d)
   - Implement custom date picker UI
   - Connect to chart data loading

5. **Implement Metric Toggles**
   - Create metric checkbox controls
   - Wire up toggle event handlers
   - Update chart datasets dynamically
   - Implement smooth transitions

6. **API Integration**
   - Create ActivityMonitorAPI class
   - Implement trends endpoint integration
   - Add error handling and retry logic
   - Test with real backend data

### Phase 3: Interactive Features (Days 5-6)

7. **Chart Interactions**
   - Implement hover tooltips with detailed metrics
   - Add click handlers for data points
   - Create zoom and pan functionality
   - Add loading and error states

8. **User History Modal**
   - Create modal HTML structure
   - Implement ModalManager class
   - Add open/close animations
   - Implement keyboard navigation

9. **History Timeline**
   - Create enhanced timeline component
   - Implement pagination
   - Add filtering controls
   - Connect to API for user history data

### Phase 4: Advanced Features (Days 7-8)

10. **Export Functionality**
    - Create ExportManager class
    - Implement CSV export
    - Add JSON export option
    - Create download UI feedback

11. **Real-time Updates**
    - Implement WebSocket connection (if available)
    - Add polling fallback (30-second intervals)
    - Update chart without full refresh
    - Add update indicators

12. **State Management**
    - Implement StateManager for preferences
    - Save user selections to localStorage
    - Restore preferences on page load
    - Sync state across components

### Phase 5: Polish & Optimization (Days 9-10)

13. **Performance Optimization**
    - Implement data caching strategy
    - Add request debouncing
    - Optimize chart rendering
    - Minimize reflows and repaints

14. **Accessibility Testing**
    - Test keyboard navigation
    - Verify screen reader compatibility
    - Check color contrast ratios
    - Add focus indicators

15. **Cross-browser Testing**
    - Test in Chrome, Firefox, Safari, Edge
    - Fix any browser-specific issues
    - Verify chart rendering consistency
    - Test animations and transitions

### Phase 6: Integration & Testing (Days 11-12)

16. **Integration with Existing Page**
    - Merge with current activity-monitor.html
    - Ensure no style conflicts
    - Test all existing functionality
    - Update navigation if needed

17. **Error Scenarios**
    - Test network failures
    - Handle empty data states
    - Test permission errors
    - Implement graceful degradation

18. **Documentation**
    - Create inline code documentation
    - Write user guide for new features
    - Document API endpoints used
    - Create troubleshooting guide

---

## Testing Checklist

### Functional Testing
- [ ] Date range selection works correctly
- [ ] Metric toggles update chart properly
- [ ] Chart displays accurate data
- [ ] Tooltips show correct information
- [ ] Modal opens and closes smoothly
- [ ] History pagination works
- [ ] Export generates valid files
- [ ] Real-time updates function properly

### Visual Testing
- [ ] Chart renders correctly at different sizes
- [ ] Animations are smooth (60fps)
- [ ] Colors match design specifications
- [ ] Typography is consistent
- [ ] Spacing follows design system
- [ ] Loading states display properly
- [ ] Error states are clear

### Performance Testing
- [ ] Page loads in under 2 seconds
- [ ] Chart updates without lag
- [ ] Scrolling remains smooth
- [ ] Memory usage is reasonable
- [ ] No memory leaks detected

### Accessibility Testing
- [ ] All interactive elements are keyboard accessible
- [ ] Focus indicators are visible
- [ ] Screen reader announces changes
- [ ] Color contrast meets WCAG AA
- [ ] Error messages are announced
- [ ] Modal can be closed with Escape key

### Browser Compatibility
- [ ] Chrome 90+
- [ ] Firefox 88+
- [ ] Safari 14+
- [ ] Edge 90+

---

## Code Examples

### Complete Initialization Script

```javascript
// main.js - Activity Monitor Enhancement Initialization
document.addEventListener('DOMContentLoaded', async function() {
    // Check authentication
    const authCheck = await checkAdminAccess();
    if (!authCheck) return;
    
    // Initialize components
    const trendsChart = new ActivityTrendsChart('trendsChart');
    const eventHandlers = new ActivityMonitorEventHandlers();
    const errorHandler = new ActivityMonitorErrorHandler();
    const api = new ActivityMonitorAPI();
    
    // Set chart reference
    eventHandlers.chart = trendsChart;
    
    // Subscribe to state changes
    activityState.subscribe((state) => {
        console.log('State updated:', state);
    });
    
    // Load initial data
    try {
        await trendsChart.loadData();
        
        // Start real-time updates
        eventHandlers.startRealTimeUpdates();
        
        // Show success indicator
        errorHandler.showError('Activity Monitor Enhanced loaded successfully', 'success', 3000);
        
    } catch (error) {
        errorHandler.handleAPIError(error);
    }
    
    // Setup performance monitoring
    if (window.performance && performance.mark) {
        performance.mark('activity-monitor-ready');
        performance.measure('activity-monitor-load', 'navigationStart', 'activity-monitor-ready');
        const measure = performance.getEntriesByName('activity-monitor-load')[0];
        console.log(`Activity Monitor loaded in ${measure.duration.toFixed(2)}ms`);
    }
});
```

### CSS Animation Library

```css
/* animations.css - Reusable Animation Classes */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes shimmer {
    0% {
        background-position: -1000px 0;
    }
    100% {
        background-position: 1000px 0;
    }
}

.animate-fadeIn { animation: fadeIn 0.3s ease; }
.animate-slideInUp { animation: slideInUp 0.4s ease; }
.animate-scaleIn { animation: scaleIn 0.3s ease; }
.animate-shimmer {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
}
```

---

## Notes for Frontend Engineers

1. **Performance Considerations**
   - Use `requestAnimationFrame` for smooth animations
   - Debounce user inputs (search, filters) by 300ms
   - Lazy load historical data (pagination)
   - Cache API responses for 5 minutes

2. **Desktop Optimization**
   - Optimize for 1920x1080 and 2560x1440 resolutions
   - Use hover states extensively for rich interactions
   - Implement keyboard shortcuts for power users
   - Take advantage of screen space with detailed tooltips

3. **Chart.js Plugins**
   - Consider adding zoom plugin for time range selection
   - Use annotation plugin for highlighting anomalies
   - Implement custom legend for better control

4. **Error Recovery**
   - Implement exponential backoff for failed requests
   - Show inline errors rather than alerts where possible
   - Provide retry buttons for failed operations
   - Cache last known good state

5. **Development Tools**
   - Use Chrome DevTools Performance tab to profile
   - Monitor memory usage with Heap Snapshots
   - Test with Network throttling (Slow 3G)
   - Use Lighthouse for performance audits

This implementation plan provides a complete blueprint for building the Activity Monitor Enhancement feature with premium desktop experience and rich interactions.