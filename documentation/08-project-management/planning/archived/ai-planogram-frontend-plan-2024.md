# AI Planogram Frontend Implementation Plan

## Executive Summary
This document provides a comprehensive frontend implementation plan for enhancing the NSPT.html planogram interface with real-time AI feedback, heat map visualizations, and advanced performance indicators based on the ai-planogram-strategy.md requirements.

## 1. UI/UX Design for Real-Time AI Feedback

### 1.1 Real-Time Placement Score Display
```javascript
// Component Structure
class RealtimePlacementFeedback {
    constructor() {
        this.scoreDisplay = null;
        this.feedbackPanel = null;
        this.debounceTimer = null;
        this.currentScore = 0;
        this.targetScore = 0;
    }
    
    // Visual feedback overlay that follows drag operation
    createScoreOverlay(x, y, score, feedback) {
        const overlay = document.createElement('div');
        overlay.className = 'ai-score-overlay';
        overlay.innerHTML = `
            <div class="score-badge ${this.getScoreClass(score)}">
                <span class="score-value">${score}</span>
                <span class="score-label">AI Score</span>
            </div>
            <div class="feedback-text">${feedback}</div>
        `;
        overlay.style.cssText = `
            position: fixed;
            left: ${x + 20}px;
            top: ${y - 60}px;
            z-index: 10000;
            pointer-events: none;
        `;
        return overlay;
    }
    
    getScoreClass(score) {
        if (score >= 80) return 'excellent';
        if (score >= 60) return 'good';
        if (score >= 40) return 'fair';
        return 'poor';
    }
}
```

### 1.2 Constraint Validation Indicators
```css
/* Real-time validation states */
.slot.ai-validating {
    position: relative;
    overflow: visible;
}

.slot.ai-validating::before {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 12px;
    padding: 2px;
    background: linear-gradient(45deg, #006dfe, #00c9ff);
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: xor;
    mask-composite: exclude;
    animation: ai-pulse 1.5s ease-in-out infinite;
}

@keyframes ai-pulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
}

.constraint-indicator {
    position: absolute;
    top: -8px;
    right: -8px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: bold;
    color: white;
    z-index: 100;
}

.constraint-indicator.valid {
    background: linear-gradient(135deg, #27ae60, #2ecc71);
    animation: checkmark-pop 0.3s ease-out;
}

.constraint-indicator.warning {
    background: linear-gradient(135deg, #f39c12, #f1c40f);
    animation: warning-shake 0.5s ease-out;
}

.constraint-indicator.invalid {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
    animation: error-bounce 0.5s ease-out;
}
```

### 1.3 Live Feedback Panel Design
```html
<!-- Enhanced AI Panel Structure -->
<div id="ai-realtime-panel" class="ai-realtime-panel">
    <div class="ai-panel-header">
        <div class="ai-status-indicator">
            <span class="status-dot"></span>
            <span class="status-text">AI Active</span>
        </div>
        <div class="ai-panel-controls">
            <button class="ai-mode-toggle" data-mode="realtime">
                <span class="mode-icon">⚡</span>
                Real-time
            </button>
            <button class="ai-mode-toggle" data-mode="batch">
                <span class="mode-icon">📊</span>
                Batch Analysis
            </button>
        </div>
    </div>
    
    <div class="ai-metrics-display">
        <div class="metric-card">
            <div class="metric-value" id="revenue-prediction">--</div>
            <div class="metric-label">Predicted Revenue</div>
            <div class="metric-change positive">+15%</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="optimization-score">--</div>
            <div class="metric-label">Optimization Score</div>
            <div class="metric-progress">
                <div class="progress-bar" style="width: 0%"></div>
            </div>
        </div>
    </div>
    
    <div class="ai-suggestions-feed">
        <!-- Dynamic suggestion cards -->
    </div>
</div>
```

## 2. JavaScript Implementation for NSPT.html

### 2.1 Core AI Integration Module
```javascript
// ai-planogram-assistant.js
class AIPlanogramAssistant {
    constructor(api, stateManager) {
        this.api = api;
        this.state = stateManager;
        this.realtimeMode = true;
        this.scoreCache = new Map();
        this.pendingRequests = new Map();
        this.heatmapLayer = null;
        this.initializeWebSocket();
    }
    
    async initializeWebSocket() {
        // WebSocket for real-time updates (optional enhancement)
        this.ws = new WebSocket(`ws://${window.location.host}/ai-stream`);
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleRealtimeUpdate(data);
        };
    }
    
    async analyzePlacement(productId, slotPosition, immediate = false) {
        const cacheKey = `${productId}-${slotPosition}`;
        
        // Check cache first
        if (!immediate && this.scoreCache.has(cacheKey)) {
            const cached = this.scoreCache.get(cacheKey);
            if (Date.now() - cached.timestamp < 5000) { // 5 second cache
                return cached.data;
            }
        }
        
        // Debounce multiple requests
        if (this.pendingRequests.has(cacheKey)) {
            return this.pendingRequests.get(cacheKey);
        }
        
        const request = this.performAnalysis(productId, slotPosition);
        this.pendingRequests.set(cacheKey, request);
        
        try {
            const result = await request;
            this.scoreCache.set(cacheKey, {
                data: result,
                timestamp: Date.now()
            });
            return result;
        } finally {
            this.pendingRequests.delete(cacheKey);
        }
    }
    
    async performAnalysis(productId, slotPosition) {
        const context = this.gatherContext(slotPosition);
        
        const response = await this.api.makeRequest('POST', '/api/planogram/analyze-placement', {
            productId,
            slotPosition,
            deviceId: this.state.currentAsset.id,
            cabinetIndex: this.state.currentCabinet.cabinetIndex,
            context: {
                adjacentProducts: context.adjacentProducts,
                zoneData: context.zoneData,
                salesHistory: context.salesHistory,
                currentPlanogram: this.state.currentPlanogram
            },
            mode: this.realtimeMode ? 'quick' : 'detailed'
        });
        
        return response;
    }
    
    gatherContext(slotPosition) {
        // Extract row and column from position (e.g., "B3" -> row B, col 3)
        const row = slotPosition.charCodeAt(0) - 65;
        const col = parseInt(slotPosition.slice(1)) - 1;
        
        // Get adjacent products
        const adjacentProducts = this.getAdjacentProducts(row, col);
        
        // Determine zone value
        const zoneData = this.calculateZoneValue(row, col);
        
        // Get recent sales for this position
        const salesHistory = this.state.salesData?.[slotPosition] || null;
        
        return { adjacentProducts, zoneData, salesHistory };
    }
    
    getAdjacentProducts(row, col) {
        const adjacent = [];
        const directions = [
            [-1, 0], [1, 0], [0, -1], [0, 1], // Cardinal
            [-1, -1], [-1, 1], [1, -1], [1, 1] // Diagonal
        ];
        
        directions.forEach(([dr, dc]) => {
            const newRow = row + dr;
            const newCol = col + dc;
            const position = `${String.fromCharCode(65 + newRow)}${newCol + 1}`;
            
            if (this.state.currentPlanogram[position]) {
                adjacent.push({
                    position,
                    productId: this.state.currentPlanogram[position],
                    distance: Math.sqrt(dr * dr + dc * dc)
                });
            }
        });
        
        return adjacent;
    }
    
    calculateZoneValue(row, col) {
        // Zone value matrix from strategy document
        const ZONE_VALUES = {
            0: { '0-2': 1.5, '3-5': 1.8, '6-9': 1.3 }, // Eye level (row A)
            1: { '0-2': 1.2, '3-5': 1.4, '6-9': 1.1 }, // Reach zone (row B)
            2: { '0-2': 0.9, '3-5': 1.0, '6-9': 0.8 }, // Bend zone (row C)
            3: { '0-2': 0.7, '3-5': 0.8, '6-9': 0.6 }  // Squat zone (row D)
        };
        
        const rowValues = ZONE_VALUES[Math.min(row, 3)];
        const colRange = col <= 2 ? '0-2' : col <= 5 ? '3-5' : '6-9';
        
        return {
            multiplier: rowValues[colRange],
            zone: this.getZoneName(row),
            visibility: this.getVisibilityScore(row, col)
        };
    }
    
    getZoneName(row) {
        const zones = ['Eye Level', 'Reach Zone', 'Bend Zone', 'Squat Zone'];
        return zones[Math.min(row, 3)];
    }
    
    getVisibilityScore(row, col) {
        // Center columns have higher visibility
        const centerDistance = Math.abs(col - 4.5);
        const rowPenalty = Math.abs(row - 1) * 0.15;
        return Math.max(0, 1 - (centerDistance * 0.1) - rowPenalty);
    }
}
```

### 2.2 Drag and Drop AI Integration
```javascript
// Enhanced drag-drop with AI feedback
class AIEnhancedDragDrop {
    constructor(assistant) {
        this.assistant = assistant;
        this.feedbackOverlay = null;
        this.validationTimer = null;
        this.setupDragListeners();
    }
    
    setupDragListeners() {
        // Override existing drag events
        document.addEventListener('dragstart', this.handleDragStart.bind(this));
        document.addEventListener('dragover', this.handleDragOver.bind(this));
        document.addEventListener('drop', this.handleDrop.bind(this));
        document.addEventListener('dragend', this.handleDragEnd.bind(this));
    }
    
    async handleDragOver(e) {
        e.preventDefault();
        const slot = e.target.closest('.slot');
        
        if (!slot) return;
        
        // Clear previous validation timer
        clearTimeout(this.validationTimer);
        
        // Add validating state
        slot.classList.add('ai-validating');
        
        // Get slot position
        const position = slot.dataset.position;
        const productId = this.draggedProductId;
        
        // Debounce validation requests
        this.validationTimer = setTimeout(async () => {
            const analysis = await this.assistant.analyzePlacement(
                productId, 
                position, 
                true // immediate mode
            );
            
            this.showRealtimeFeedback(slot, analysis);
        }, 200); // 200ms debounce
    }
    
    showRealtimeFeedback(slot, analysis) {
        // Remove previous feedback
        this.clearFeedback();
        
        // Create feedback overlay
        const rect = slot.getBoundingClientRect();
        this.feedbackOverlay = document.createElement('div');
        this.feedbackOverlay.className = 'ai-feedback-overlay';
        this.feedbackOverlay.innerHTML = `
            <div class="ai-score-badge score-${this.getScoreLevel(analysis.score)}">
                <div class="score-ring">
                    <svg viewBox="0 0 36 36">
                        <circle cx="18" cy="18" r="16" fill="none" stroke="#eee" stroke-width="2"/>
                        <circle cx="18" cy="18" r="16" fill="none" 
                                stroke="currentColor" stroke-width="2"
                                stroke-dasharray="${analysis.score} 100"
                                stroke-dashoffset="25"
                                transform="rotate(-90 18 18)"/>
                    </svg>
                    <span class="score-text">${analysis.score}</span>
                </div>
            </div>
            <div class="ai-feedback-tooltip">
                <div class="feedback-message">${analysis.feedback}</div>
                ${analysis.constraints.map(c => `
                    <div class="constraint-item ${c.valid ? 'valid' : 'invalid'}">
                        <span class="constraint-icon">${c.valid ? '✓' : '✗'}</span>
                        <span class="constraint-text">${c.message}</span>
                    </div>
                `).join('')}
            </div>
        `;
        
        // Position overlay
        this.feedbackOverlay.style.cssText = `
            position: fixed;
            left: ${rect.right + 10}px;
            top: ${rect.top}px;
            z-index: 10000;
        `;
        
        document.body.appendChild(this.feedbackOverlay);
        
        // Update slot visual state
        slot.classList.remove('drag-over-valid', 'drag-over-invalid');
        slot.classList.add(analysis.score >= 60 ? 'drag-over-valid' : 'drag-over-invalid');
    }
    
    clearFeedback() {
        if (this.feedbackOverlay) {
            this.feedbackOverlay.remove();
            this.feedbackOverlay = null;
        }
        
        document.querySelectorAll('.slot').forEach(slot => {
            slot.classList.remove('ai-validating', 'drag-over-valid', 'drag-over-invalid');
        });
    }
    
    getScoreLevel(score) {
        if (score >= 80) return 'excellent';
        if (score >= 60) return 'good';
        if (score >= 40) return 'fair';
        return 'poor';
    }
}
```

## 3. Heat Map Visualization Components

### 3.1 Revenue Heat Map Layer
```javascript
class RevenueHeatMap {
    constructor(containerElement) {
        this.container = containerElement;
        this.canvas = null;
        this.ctx = null;
        this.data = null;
        this.colorScale = this.createColorScale();
    }
    
    createColorScale() {
        // Create gradient from cool to hot
        return {
            0: '#3498db',    // Cool blue (low revenue)
            25: '#9b59b6',   // Purple
            50: '#f39c12',   // Orange
            75: '#e74c3c',   // Red
            100: '#c0392b'   // Dark red (high revenue)
        };
    }
    
    render(planogramData, revenueData) {
        this.clearCanvas();
        
        const slots = document.querySelectorAll('.slot');
        const maxRevenue = Math.max(...Object.values(revenueData));
        const minRevenue = Math.min(...Object.values(revenueData));
        
        slots.forEach(slot => {
            const position = slot.dataset.position;
            const revenue = revenueData[position] || 0;
            const normalizedValue = (revenue - minRevenue) / (maxRevenue - minRevenue);
            
            this.applyHeatToSlot(slot, normalizedValue);
        });
        
        this.renderLegend(minRevenue, maxRevenue);
    }
    
    applyHeatToSlot(slot, value) {
        const color = this.getColorForValue(value);
        const opacity = 0.3 + (value * 0.4); // 30-70% opacity
        
        // Create heat overlay
        const overlay = slot.querySelector('.heat-overlay') || 
                       document.createElement('div');
        overlay.className = 'heat-overlay';
        overlay.style.cssText = `
            position: absolute;
            inset: 0;
            background: ${color};
            opacity: ${opacity};
            pointer-events: none;
            border-radius: 7px;
            mix-blend-mode: multiply;
        `;
        
        if (!slot.querySelector('.heat-overlay')) {
            slot.appendChild(overlay);
        }
        
        // Add value indicator
        const indicator = slot.querySelector('.heat-value') || 
                         document.createElement('div');
        indicator.className = 'heat-value';
        indicator.textContent = `$${(value * 100).toFixed(0)}`;
        indicator.style.cssText = `
            position: absolute;
            bottom: 2px;
            left: 2px;
            font-size: 9px;
            font-weight: bold;
            color: white;
            background: rgba(0,0,0,0.5);
            padding: 1px 3px;
            border-radius: 3px;
        `;
        
        if (!slot.querySelector('.heat-value')) {
            slot.appendChild(indicator);
        }
    }
    
    getColorForValue(value) {
        const percentage = value * 100;
        
        // Find the two closest color stops
        const stops = Object.keys(this.colorScale).map(Number).sort((a, b) => a - b);
        let lowerStop = 0, upperStop = 100;
        
        for (let i = 0; i < stops.length - 1; i++) {
            if (percentage >= stops[i] && percentage <= stops[i + 1]) {
                lowerStop = stops[i];
                upperStop = stops[i + 1];
                break;
            }
        }
        
        // Interpolate between colors
        const ratio = (percentage - lowerStop) / (upperStop - lowerStop);
        return this.interpolateColor(
            this.colorScale[lowerStop],
            this.colorScale[upperStop],
            ratio
        );
    }
    
    interpolateColor(color1, color2, ratio) {
        // Simple hex color interpolation
        const hex2rgb = (hex) => {
            const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            } : null;
        };
        
        const c1 = hex2rgb(color1);
        const c2 = hex2rgb(color2);
        
        const r = Math.round(c1.r + (c2.r - c1.r) * ratio);
        const g = Math.round(c1.g + (c2.g - c1.g) * ratio);
        const b = Math.round(c1.b + (c2.b - c1.b) * ratio);
        
        return `rgb(${r}, ${g}, ${b})`;
    }
    
    renderLegend(min, max) {
        const legend = document.createElement('div');
        legend.className = 'heatmap-legend';
        legend.innerHTML = `
            <div class="legend-title">Revenue Heat Map</div>
            <div class="legend-gradient">
                <div class="gradient-bar"></div>
                <div class="gradient-labels">
                    <span>$${min.toFixed(0)}</span>
                    <span>$${((min + max) / 2).toFixed(0)}</span>
                    <span>$${max.toFixed(0)}</span>
                </div>
            </div>
        `;
        
        this.container.appendChild(legend);
    }
    
    clearCanvas() {
        document.querySelectorAll('.heat-overlay, .heat-value, .heatmap-legend')
            .forEach(el => el.remove());
    }
    
    toggle() {
        const overlays = document.querySelectorAll('.heat-overlay');
        overlays.forEach(overlay => {
            overlay.style.display = overlay.style.display === 'none' ? 'block' : 'none';
        });
    }
}
```

### 3.2 Zone Visibility Overlay
```javascript
class ZoneVisibilityOverlay {
    constructor() {
        this.zones = {
            'A': { name: 'Eye Level', color: '#27ae60', value: 1.5 },
            'B': { name: 'Reach Zone', color: '#3498db', value: 1.2 },
            'C': { name: 'Bend Zone', color: '#f39c12', value: 0.9 },
            'D': { name: 'Squat Zone', color: '#e74c3c', value: 0.7 }
        };
    }
    
    apply() {
        const rows = document.querySelectorAll('.row');
        
        rows.forEach((row, index) => {
            const zone = String.fromCharCode(65 + index);
            const zoneData = this.zones[zone] || this.zones['D'];
            
            // Add zone indicator
            const indicator = document.createElement('div');
            indicator.className = 'zone-indicator';
            indicator.innerHTML = `
                <div class="zone-label" style="background: ${zoneData.color}">
                    ${zoneData.name}
                </div>
                <div class="zone-value">×${zoneData.value}</div>
            `;
            
            row.insertBefore(indicator, row.firstChild);
            
            // Apply subtle background to row
            row.style.background = `linear-gradient(90deg, 
                ${zoneData.color}15 0%, 
                transparent 100px)`;
        });
    }
    
    remove() {
        document.querySelectorAll('.zone-indicator').forEach(el => el.remove());
        document.querySelectorAll('.row').forEach(row => {
            row.style.background = '';
        });
    }
}
```

## 4. Performance Indicators and Loading States

### 4.1 Performance Metrics Dashboard
```javascript
class PerformanceMetrics {
    constructor(container) {
        this.container = container;
        this.metrics = {};
        this.charts = {};
        this.init();
    }
    
    init() {
        this.container.innerHTML = `
            <div class="metrics-dashboard">
                <div class="metric-tile" id="revenue-metric">
                    <div class="metric-icon">💰</div>
                    <div class="metric-content">
                        <div class="metric-value">
                            <span class="value">$0</span>
                            <span class="change">--</span>
                        </div>
                        <div class="metric-label">Predicted Daily Revenue</div>
                        <div class="metric-chart">
                            <canvas id="revenue-trend"></canvas>
                        </div>
                    </div>
                </div>
                
                <div class="metric-tile" id="optimization-metric">
                    <div class="metric-icon">📊</div>
                    <div class="metric-content">
                        <div class="metric-value">
                            <span class="value">0%</span>
                            <span class="change">--</span>
                        </div>
                        <div class="metric-label">Optimization Score</div>
                        <div class="metric-progress">
                            <div class="progress-segments">
                                <div class="segment poor"></div>
                                <div class="segment fair"></div>
                                <div class="segment good"></div>
                                <div class="segment excellent"></div>
                            </div>
                            <div class="progress-indicator" style="left: 0%"></div>
                        </div>
                    </div>
                </div>
                
                <div class="metric-tile" id="stockout-metric">
                    <div class="metric-icon">📦</div>
                    <div class="metric-content">
                        <div class="metric-value">
                            <span class="value">0</span>
                            <span class="change">--</span>
                        </div>
                        <div class="metric-label">Predicted Stockouts</div>
                        <div class="metric-list">
                            <!-- Dynamic stockout predictions -->
                        </div>
                    </div>
                </div>
                
                <div class="metric-tile" id="affinity-metric">
                    <div class="metric-icon">🔗</div>
                    <div class="metric-content">
                        <div class="metric-value">
                            <span class="value">0</span>
                            <span class="change">--</span>
                        </div>
                        <div class="metric-label">Cross-Sell Score</div>
                        <div class="affinity-matrix">
                            <!-- Dynamic affinity visualization -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.initializeCharts();
    }
    
    update(data) {
        // Animate metric updates
        this.animateValue('revenue-metric', data.revenue, data.revenueChange);
        this.animateValue('optimization-metric', data.optimizationScore, data.optimizationChange);
        this.animateValue('stockout-metric', data.stockoutRisk, data.stockoutChange);
        this.animateValue('affinity-metric', data.affinityScore, data.affinityChange);
        
        // Update charts
        this.updateCharts(data);
        
        // Update progress indicators
        this.updateProgress(data.optimizationScore);
    }
    
    animateValue(metricId, newValue, change) {
        const metric = document.querySelector(`#${metricId}`);
        const valueEl = metric.querySelector('.value');
        const changeEl = metric.querySelector('.change');
        
        // Animate number change
        const startValue = parseFloat(valueEl.textContent.replace(/[^0-9.-]/g, ''));
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = startValue + (newValue - startValue) * easeOutQuart;
            
            // Format based on metric type
            if (metricId === 'revenue-metric') {
                valueEl.textContent = `$${currentValue.toFixed(0)}`;
            } else if (metricId === 'optimization-metric') {
                valueEl.textContent = `${currentValue.toFixed(0)}%`;
            } else {
                valueEl.textContent = currentValue.toFixed(0);
            }
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
        
        // Update change indicator
        if (change !== null && change !== undefined) {
            changeEl.textContent = change > 0 ? `+${change}%` : `${change}%`;
            changeEl.className = `change ${change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'}`;
        }
    }
}
```

### 4.2 Advanced Loading States
```javascript
class AILoadingStates {
    constructor() {
        this.states = {
            analyzing: {
                icon: '🔍',
                message: 'Analyzing current planogram...',
                animation: 'pulse'
            },
            optimizing: {
                icon: '⚡',
                message: 'Optimizing product placement...',
                animation: 'spin'
            },
            calculating: {
                icon: '📊',
                message: 'Calculating revenue impact...',
                animation: 'wave'
            },
            validating: {
                icon: '✓',
                message: 'Validating constraints...',
                animation: 'bounce'
            }
        };
    }
    
    show(state, target) {
        const config = this.states[state];
        
        const loader = document.createElement('div');
        loader.className = `ai-loader ai-loader-${config.animation}`;
        loader.innerHTML = `
            <div class="loader-content">
                <div class="loader-icon">${config.icon}</div>
                <div class="loader-message">${config.message}</div>
                <div class="loader-progress">
                    <div class="progress-track">
                        <div class="progress-fill"></div>
                    </div>
                </div>
            </div>
        `;
        
        target.appendChild(loader);
        
        // Simulate progress
        this.animateProgress(loader.querySelector('.progress-fill'));
        
        return loader;
    }
    
    animateProgress(element) {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            progress = Math.min(progress, 95);
            element.style.width = `${progress}%`;
            
            if (progress >= 95) {
                clearInterval(interval);
            }
        }, 200);
        
        return () => {
            clearInterval(interval);
            element.style.width = '100%';
        };
    }
}
```

## 5. Responsive Design Considerations

### 5.1 Breakpoint Strategy
```css
/* Mobile-first responsive design */
@media (max-width: 768px) {
    /* Tablet adjustments */
    .ai-realtime-panel {
        width: 100%;
        right: 0;
        left: 0;
        bottom: 0;
        top: auto;
        max-height: 50vh;
        border-radius: 20px 20px 0 0;
    }
    
    .planogram-grid {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    .slot {
        width: 80px;
        height: 80px;
        font-size: 0.9em;
    }
    
    .metrics-dashboard {
        grid-template-columns: 1fr;
        gap: 12px;
    }
}

@media (max-width: 480px) {
    /* Mobile adjustments */
    .toolbar {
        flex-direction: column;
        height: auto;
        padding: 12px;
    }
    
    .toolbar-group {
        width: 100%;
        justify-content: center;
        margin: 4px 0;
    }
    
    .ai-feedback-overlay {
        position: fixed;
        bottom: 20px;
        left: 20px;
        right: 20px;
        top: auto;
    }
    
    .heat-overlay {
        opacity: 0.5 !important;
    }
}

/* High DPI displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
    .slot-image {
        image-rendering: -webkit-optimize-contrast;
        image-rendering: crisp-edges;
    }
    
    .ai-score-badge svg {
        transform: scale(1.5);
        transform-origin: center;
    }
}

/* Landscape orientation for tablets */
@media (min-width: 768px) and (max-width: 1024px) and (orientation: landscape) {
    .app-container {
        grid-template-columns: 1fr 2fr 1fr;
    }
    
    .ai-realtime-panel {
        position: relative;
        width: 100%;
        height: 100%;
    }
}
```

### 5.2 Touch Interaction Enhancements
```javascript
class TouchOptimizedDragDrop {
    constructor() {
        this.touchStartPos = null;
        this.draggedElement = null;
        this.ghostElement = null;
        this.setupTouchHandlers();
    }
    
    setupTouchHandlers() {
        // Enable touch drag-drop
        document.addEventListener('touchstart', this.handleTouchStart.bind(this), {passive: false});
        document.addEventListener('touchmove', this.handleTouchMove.bind(this), {passive: false});
        document.addEventListener('touchend', this.handleTouchEnd.bind(this));
    }
    
    handleTouchStart(e) {
        const touch = e.touches[0];
        const target = document.elementFromPoint(touch.clientX, touch.clientY);
        
        if (target?.classList.contains('product-item') || 
            target?.closest('.slot')?.querySelector('.slot-image')) {
            e.preventDefault();
            
            this.touchStartPos = { x: touch.clientX, y: touch.clientY };
            this.draggedElement = target.closest('.product-item, .slot');
            
            // Create ghost element for visual feedback
            this.createGhostElement(touch);
            
            // Add haptic feedback if available
            if (navigator.vibrate) {
                navigator.vibrate(10);
            }
        }
    }
    
    handleTouchMove(e) {
        if (!this.draggedElement) return;
        
        e.preventDefault();
        const touch = e.touches[0];
        
        // Update ghost position
        if (this.ghostElement) {
            this.ghostElement.style.left = `${touch.clientX - 40}px`;
            this.ghostElement.style.top = `${touch.clientY - 40}px`;
        }
        
        // Find drop target
        const dropTarget = this.findDropTarget(touch.clientX, touch.clientY);
        if (dropTarget) {
            this.highlightDropTarget(dropTarget);
        }
    }
    
    createGhostElement(touch) {
        this.ghostElement = this.draggedElement.cloneNode(true);
        this.ghostElement.className = 'drag-ghost';
        this.ghostElement.style.cssText = `
            position: fixed;
            left: ${touch.clientX - 40}px;
            top: ${touch.clientY - 40}px;
            width: 80px;
            height: 80px;
            opacity: 0.8;
            pointer-events: none;
            z-index: 10000;
            transform: scale(1.1);
            transition: transform 0.2s;
        `;
        document.body.appendChild(this.ghostElement);
    }
}
```

## 6. Integration Checklist

### 6.1 File Structure
```
/pages/
  ├── NSPT.html (enhanced)
  ├── ai-planogram-assistant.js (new)
  ├── ai-components.css (new)
  └── ai-visualizations.js (new)

/api/
  └── planogram-ai-endpoints.js (new)

/styles/
  └── ai-enhancements.css (new)
```

### 6.2 Implementation Phases

#### Phase 1: Core AI Integration (Week 1)
- [ ] Implement AIPlanogramAssistant class
- [ ] Add real-time placement analysis endpoint
- [ ] Create basic score display UI
- [ ] Integrate with existing drag-drop

#### Phase 2: Visualization Layer (Week 2)
- [ ] Implement RevenueHeatMap component
- [ ] Add ZoneVisibilityOverlay
- [ ] Create performance metrics dashboard
- [ ] Add loading states and animations

#### Phase 3: Advanced Features (Week 3)
- [ ] Implement predictive analytics
- [ ] Add affinity clustering visualization
- [ ] Create batch optimization mode
- [ ] Add A/B testing framework

#### Phase 4: Polish & Optimization (Week 4)
- [ ] Performance optimization
- [ ] Responsive design refinements
- [ ] Touch interaction improvements
- [ ] Accessibility enhancements

### 6.3 Performance Targets
- Real-time feedback: <200ms response time
- Heat map rendering: <100ms
- Drag operation: 60fps smooth animation
- Initial load: <2s with AI features
- Memory usage: <50MB additional

### 6.4 Browser Compatibility
- Chrome 90+ (primary)
- Safari 14+ (iOS support)
- Firefox 88+
- Edge 90+
- Mobile Safari (iOS 14+)
- Chrome Mobile (Android 10+)

## 7. Code Examples for Immediate Implementation

### 7.1 Quick Start Integration
```javascript
// Add to NSPT.html after existing initialization
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize AI Assistant
    window.aiAssistant = new AIPlanogramAssistant(cvdApi, state);
    
    // Add heat map toggle button
    const heatmapBtn = document.createElement('button');
    heatmapBtn.className = 'btn btn-secondary';
    heatmapBtn.innerHTML = '🔥 Heat Map';
    heatmapBtn.onclick = () => {
        if (!window.heatMap) {
            window.heatMap = new RevenueHeatMap(document.querySelector('.planogram-container'));
        }
        window.heatMap.toggle();
    };
    document.querySelector('.toolbar-right').appendChild(heatmapBtn);
    
    // Initialize performance metrics
    const metricsContainer = document.createElement('div');
    metricsContainer.id = 'performance-metrics';
    document.querySelector('.right-panel').appendChild(metricsContainer);
    window.performanceMetrics = new PerformanceMetrics(metricsContainer);
    
    // Enhance drag-drop with AI
    window.aiDragDrop = new AIEnhancedDragDrop(window.aiAssistant);
});
```

### 7.2 CSS Enhancements to Add
```css
/* Add to NSPT.html <style> section */

/* AI Score Badges */
.ai-score-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 20px;
    font-weight: 600;
    animation: score-appear 0.3s ease-out;
}

.ai-score-badge.excellent {
    background: linear-gradient(135deg, #27ae60, #2ecc71);
    color: white;
}

.ai-score-badge.good {
    background: linear-gradient(135deg, #3498db, #5dade2);
    color: white;
}

.ai-score-badge.fair {
    background: linear-gradient(135deg, #f39c12, #f4d03f);
    color: #2c3e50;
}

.ai-score-badge.poor {
    background: linear-gradient(135deg, #e74c3c, #ec7063);
    color: white;
}

/* Animated loading states */
@keyframes ai-pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.8; }
}

@keyframes ai-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes ai-wave {
    0%, 100% { transform: translateY(0); }
    25% { transform: translateY(-10px); }
    75% { transform: translateY(10px); }
}

/* Heat map overlays */
.heat-overlay {
    transition: opacity 0.3s ease;
}

.heat-value {
    transition: all 0.3s ease;
}

.heatmap-legend {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: white;
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.gradient-bar {
    width: 200px;
    height: 20px;
    background: linear-gradient(90deg, #3498db, #9b59b6, #f39c12, #e74c3c, #c0392b);
    border-radius: 4px;
    margin: 8px 0;
}
```

## Conclusion

This comprehensive frontend implementation plan provides a complete roadmap for enhancing the NSPT.html planogram interface with advanced AI capabilities. The modular architecture ensures clean integration with existing code while adding powerful new features including real-time feedback, heat map visualizations, and sophisticated performance metrics.

Key deliverables include:
- Real-time AI scoring with <200ms response time
- Interactive heat map visualizations
- Touch-optimized drag-and-drop
- Responsive design for all devices
- Performance metrics dashboard
- Progressive enhancement approach

The implementation follows best practices for maintainability, performance, and user experience, ensuring the AI enhancements seamlessly integrate with the existing CVD application architecture.