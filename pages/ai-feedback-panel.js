/**
 * AI Feedback Panel Component
 * Real-time scoring and optimization feedback for planogram editing
 */

class AIFeedbackPanel {
    constructor(apiClient) {
        this.api = apiClient;
        this.panelElement = null;
        this.currentScore = 0;
        this.isVisible = false;
        this.updateThrottle = null;
        this.heatMapVisible = false;
        this.heatMapData = null;
        
        this.init();
    }
    
    init() {
        this.createPanel();
        this.attachEventListeners();
        this.checkAIAvailability();
    }
    
    createPanel() {
        // Create panel HTML
        const panelHTML = `
            <div id="aiFeedbackPanel" class="ai-feedback-panel">
                <div class="ai-panel-header">
                    <h3>AI Optimization Assistant</h3>
                    <button class="ai-panel-close" aria-label="Close">×</button>
                </div>
                
                <div class="ai-panel-body">
                    <!-- Real-time Score Display -->
                    <div class="ai-score-section">
                        <h4>Placement Score</h4>
                        <div class="score-display">
                            <div class="score-circle" data-score="0">
                                <svg viewBox="0 0 100 100">
                                    <circle cx="50" cy="50" r="45" class="score-bg"/>
                                    <circle cx="50" cy="50" r="45" class="score-fill"/>
                                </svg>
                                <span class="score-value">0</span>
                            </div>
                            <div class="score-label">-</div>
                        </div>
                        <div class="score-feedback"></div>
                    </div>
                    
                    <!-- Component Scores -->
                    <div class="component-scores">
                        <div class="score-component">
                            <span class="component-label">Zone</span>
                            <div class="component-bar">
                                <div class="component-fill" data-component="zone"></div>
                            </div>
                            <span class="component-value">-</span>
                        </div>
                        <div class="score-component">
                            <span class="component-label">Affinity</span>
                            <div class="component-bar">
                                <div class="component-fill" data-component="affinity"></div>
                            </div>
                            <span class="component-value">-</span>
                        </div>
                        <div class="score-component">
                            <span class="component-label">Category</span>
                            <div class="component-bar">
                                <div class="component-fill" data-component="category"></div>
                            </div>
                            <span class="component-value">-</span>
                        </div>
                    </div>
                    
                    <!-- Suggestions -->
                    <div class="ai-suggestions">
                        <h4>Suggestions</h4>
                        <ul class="suggestion-list"></ul>
                    </div>
                    
                    <!-- Revenue Prediction -->
                    <div class="revenue-prediction" style="display: none;">
                        <h4>Revenue Impact</h4>
                        <div class="prediction-display">
                            <div class="prediction-value">
                                <span class="label">Expected Change</span>
                                <span class="value">-</span>
                            </div>
                            <div class="prediction-confidence">
                                <span class="label">Confidence</span>
                                <span class="value">-</span>
                            </div>
                        </div>
                        <button class="btn-predict">Calculate Revenue Impact</button>
                    </div>
                    
                    <!-- Heat Map Toggle -->
                    <div class="heat-map-controls">
                        <button class="btn-heat-map">
                            <span class="icon">🔥</span>
                            <span class="label">Toggle Heat Map</span>
                        </button>
                        <button class="btn-optimize">
                            <span class="icon">✨</span>
                            <span class="label">Auto-Optimize</span>
                        </button>
                    </div>
                </div>
                
                <div class="ai-panel-footer">
                    <div class="ai-status">
                        <span class="status-indicator"></span>
                        <span class="status-text">AI Ready</span>
                    </div>
                </div>
            </div>
        `;
        
        // Add panel to page
        const container = document.createElement('div');
        container.innerHTML = panelHTML;
        this.panelElement = container.firstElementChild;
        document.body.appendChild(this.panelElement);
        
        // Add styles
        this.injectStyles();
    }
    
    injectStyles() {
        const styles = `
            .ai-feedback-panel {
                position: fixed;
                right: 20px;
                bottom: 20px;
                width: 360px;
                max-height: 80vh;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.15);
                z-index: 1000;
                display: none;
                flex-direction: column;
                animation: slideUp 0.3s ease-out;
            }
            
            .ai-feedback-panel.visible {
                display: flex;
            }
            
            @keyframes slideUp {
                from {
                    transform: translateY(100px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            .ai-panel-header {
                padding: 16px 20px;
                border-bottom: 1px solid #e5e5e5;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .ai-panel-header h3 {
                margin: 0;
                font-size: 16px;
                font-weight: 600;
                color: #333;
            }
            
            .ai-panel-close {
                background: none;
                border: none;
                font-size: 24px;
                color: #999;
                cursor: pointer;
                padding: 0;
                width: 28px;
                height: 28px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 4px;
                transition: all 0.2s;
            }
            
            .ai-panel-close:hover {
                background: #f5f5f5;
                color: #333;
            }
            
            .ai-panel-body {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
            }
            
            .ai-score-section {
                margin-bottom: 24px;
            }
            
            .ai-score-section h4 {
                margin: 0 0 16px 0;
                font-size: 14px;
                font-weight: 600;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .score-display {
                display: flex;
                align-items: center;
                gap: 20px;
            }
            
            .score-circle {
                position: relative;
                width: 100px;
                height: 100px;
            }
            
            .score-circle svg {
                transform: rotate(-90deg);
            }
            
            .score-circle circle {
                fill: none;
                stroke-width: 8;
            }
            
            .score-circle .score-bg {
                stroke: #f0f0f0;
            }
            
            .score-circle .score-fill {
                stroke: #4CAF50;
                stroke-dasharray: 283;
                stroke-dashoffset: 283;
                transition: stroke-dashoffset 0.5s ease, stroke 0.5s ease;
            }
            
            .score-circle[data-score="0"] .score-fill { stroke-dashoffset: 283; }
            
            .score-circle .score-value {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 32px;
                font-weight: bold;
                color: #333;
            }
            
            .score-label {
                font-size: 18px;
                font-weight: 500;
                color: #666;
            }
            
            .score-feedback {
                margin-top: 12px;
                padding: 12px;
                background: #f8f9fa;
                border-radius: 8px;
                font-size: 14px;
                color: #666;
                line-height: 1.5;
            }
            
            .component-scores {
                margin-bottom: 24px;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            
            .score-component {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .component-label {
                width: 60px;
                font-size: 13px;
                color: #666;
            }
            
            .component-bar {
                flex: 1;
                height: 8px;
                background: #f0f0f0;
                border-radius: 4px;
                overflow: hidden;
            }
            
            .component-fill {
                height: 100%;
                background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcf7f);
                width: 0%;
                transition: width 0.5s ease;
            }
            
            .component-value {
                width: 30px;
                text-align: right;
                font-size: 13px;
                font-weight: 500;
                color: #333;
            }
            
            .ai-suggestions {
                margin-bottom: 24px;
            }
            
            .ai-suggestions h4 {
                margin: 0 0 12px 0;
                font-size: 14px;
                font-weight: 600;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .suggestion-list {
                margin: 0;
                padding: 0;
                list-style: none;
            }
            
            .suggestion-list li {
                padding: 10px 12px;
                background: #f8f9fa;
                border-radius: 6px;
                margin-bottom: 8px;
                font-size: 14px;
                color: #555;
                display: flex;
                align-items: start;
                gap: 8px;
            }
            
            .suggestion-list li::before {
                content: "💡";
                flex-shrink: 0;
            }
            
            .revenue-prediction {
                margin-bottom: 24px;
                padding: 16px;
                background: #f0f8ff;
                border-radius: 8px;
            }
            
            .revenue-prediction h4 {
                margin: 0 0 16px 0;
                font-size: 14px;
                font-weight: 600;
                color: #666;
            }
            
            .prediction-display {
                display: flex;
                gap: 20px;
                margin-bottom: 16px;
            }
            
            .prediction-value {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            
            .prediction-value .label,
            .prediction-confidence .label {
                font-size: 12px;
                color: #666;
                margin-bottom: 4px;
            }
            
            .prediction-value .value,
            .prediction-confidence .value {
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }
            
            .heat-map-controls {
                display: flex;
                gap: 12px;
            }
            
            .btn-heat-map,
            .btn-optimize,
            .btn-predict {
                flex: 1;
                padding: 10px 16px;
                background: white;
                border: 2px solid #e5e5e5;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                color: #333;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }
            
            .btn-heat-map:hover,
            .btn-optimize:hover,
            .btn-predict:hover {
                background: #f5f5f5;
                border-color: #007bff;
                color: #007bff;
            }
            
            .btn-heat-map.active {
                background: #ff6b6b;
                border-color: #ff6b6b;
                color: white;
            }
            
            .ai-panel-footer {
                padding: 12px 20px;
                border-top: 1px solid #e5e5e5;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .status-indicator {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #4CAF50;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .status-text {
                font-size: 13px;
                color: #666;
            }
            
            /* Heat map overlay styles */
            .heat-map-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                pointer-events: none;
                z-index: 10;
            }
            
            .heat-zone {
                position: absolute;
                opacity: 0.4;
                transition: opacity 0.3s;
            }
            
            .heat-zone:hover {
                opacity: 0.6;
            }
            
            /* Mobile responsiveness */
            @media (max-width: 768px) {
                .ai-feedback-panel {
                    position: fixed;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    width: 100%;
                    max-height: 50vh;
                    border-radius: 12px 12px 0 0;
                }
            }
        `;
        
        if (!document.getElementById('ai-feedback-styles')) {
            const styleSheet = document.createElement('style');
            styleSheet.id = 'ai-feedback-styles';
            styleSheet.textContent = styles;
            document.head.appendChild(styleSheet);
        }
    }
    
    attachEventListeners() {
        // Close button
        const closeBtn = this.panelElement.querySelector('.ai-panel-close');
        closeBtn.addEventListener('click', () => this.hide());
        
        // Heat map toggle
        const heatMapBtn = this.panelElement.querySelector('.btn-heat-map');
        heatMapBtn.addEventListener('click', () => this.toggleHeatMap());
        
        // Auto-optimize button
        const optimizeBtn = this.panelElement.querySelector('.btn-optimize');
        optimizeBtn.addEventListener('click', () => this.autoOptimize());
        
        // Predict revenue button
        const predictBtn = this.panelElement.querySelector('.btn-predict');
        if (predictBtn) {
            predictBtn.addEventListener('click', () => this.predictRevenue());
        }
    }
    
    async checkAIAvailability() {
        try {
            const response = await fetch('/api/planograms/ai-available');
            const data = await response.json();
            
            const statusIndicator = this.panelElement.querySelector('.status-indicator');
            const statusText = this.panelElement.querySelector('.status-text');
            
            if (data.available) {
                statusIndicator.style.background = '#4CAF50';
                statusText.textContent = 'AI Ready';
            } else {
                statusIndicator.style.background = '#ff9800';
                statusText.textContent = 'AI Limited (Fallback Mode)';
            }
        } catch (error) {
            console.error('Failed to check AI availability:', error);
        }
    }
    
    show() {
        this.panelElement.classList.add('visible');
        this.isVisible = true;
    }
    
    hide() {
        this.panelElement.classList.remove('visible');
        this.isVisible = false;
    }
    
    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }
    
    async updateScore(planogramData, productId, slotPosition) {
        // Throttle updates to max 2 per second
        if (this.updateThrottle) {
            clearTimeout(this.updateThrottle);
        }
        
        this.updateThrottle = setTimeout(async () => {
            try {
                // Validate inputs
                if (!planogramData || !planogramData.slots) {
                    console.warn('AI Panel: Invalid planogram data for scoring');
                    return;
                }
                
                const deviceId = this.getCurrentDeviceId();
                if (!deviceId) {
                    console.warn('AI Panel: No device ID available for scoring');
                    return;
                }
                
                const response = await fetch('/api/planograms/realtime/score', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: JSON.stringify({
                        device_id: deviceId,
                        planogram: planogramData,
                        product_id: productId,
                        position: slotPosition
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                    throw new Error(errorData.error || `Server error: ${response.status}`);
                }
                
                const scoreData = await response.json();
                this.displayScore(scoreData);
                
            } catch (error) {
                console.error('Score update error:', error);
                // Don't show error message for score updates as they happen frequently
                // Just log it for debugging
            }
        }, 500); // 500ms throttle
    }
    
    displayScore(scoreData) {
        // Update main score
        const score = Math.round(scoreData.score);
        const scoreCircle = this.panelElement.querySelector('.score-circle');
        const scoreValue = this.panelElement.querySelector('.score-value');
        const scoreLabel = this.panelElement.querySelector('.score-label');
        const scoreFill = this.panelElement.querySelector('.score-fill');
        
        scoreValue.textContent = score;
        scoreCircle.setAttribute('data-score', score);
        
        // Update score circle color and fill
        const offset = 283 - (283 * score / 100);
        scoreFill.style.strokeDashoffset = offset;
        
        if (score >= 80) {
            scoreFill.style.stroke = '#4CAF50';
            scoreLabel.textContent = 'Excellent';
        } else if (score >= 60) {
            scoreFill.style.stroke = '#FFC107';
            scoreLabel.textContent = 'Good';
        } else if (score >= 40) {
            scoreFill.style.stroke = '#FF9800';
            scoreLabel.textContent = 'Fair';
        } else {
            scoreFill.style.stroke = '#F44336';
            scoreLabel.textContent = 'Poor';
        }
        
        // Update feedback
        const feedbackEl = this.panelElement.querySelector('.score-feedback');
        feedbackEl.textContent = scoreData.feedback || '';
        
        // Update component scores
        if (scoreData.components) {
            this.updateComponentScores(scoreData.components);
        }
        
        // Update suggestions
        if (scoreData.suggestions) {
            this.updateSuggestions(scoreData.suggestions);
        }
    }
    
    updateComponentScores(components) {
        const componentTypes = ['zone', 'affinity', 'category'];
        
        componentTypes.forEach((type, index) => {
            const score = components[`${type}_score`] || 0;
            const fillEl = this.panelElement.querySelector(`[data-component="${type}"]`);
            const valueEl = this.panelElement.querySelectorAll('.component-value')[index];
            
            if (fillEl) {
                fillEl.style.width = `${score}%`;
            }
            
            if (valueEl) {
                valueEl.textContent = Math.round(score);
            }
        });
    }
    
    updateSuggestions(suggestions) {
        const listEl = this.panelElement.querySelector('.suggestion-list');
        listEl.innerHTML = '';
        
        if (suggestions.length === 0) {
            listEl.innerHTML = '<li>No suggestions at this time</li>';
            return;
        }
        
        suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.textContent = suggestion;
            listEl.appendChild(li);
        });
    }
    
    async toggleHeatMap() {
        const btn = this.panelElement.querySelector('.btn-heat-map');
        
        if (this.heatMapVisible) {
            this.hideHeatMap();
            btn.classList.remove('active');
            this.heatMapVisible = false;
        } else {
            await this.showHeatMap();
            btn.classList.add('active');
            this.heatMapVisible = true;
        }
    }
    
    async showHeatMap() {
        try {
            // Get current device ID
            const deviceId = this.getCurrentDeviceId();
            if (!deviceId) {
                this.displayError('Please select a device first to view heat map');
                return;
            }
            
            // Check if we have cabinet selected too
            if (window.state && !window.state.currentCabinet) {
                this.displayError('Please select a cabinet first to view heat map');
                return;
            }
            
            this.displayMessage('Loading heat map...');
            
            const response = await fetch(`/api/planograms/optimize/heat-zones?device_id=${deviceId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }
            
            this.heatMapData = await response.json();
            this.renderHeatMap();
            this.displayMessage('Heat map loaded successfully');
            
        } catch (error) {
            console.error('Heat map error:', error);
            this.displayError(`Unable to load heat map: ${error.message}`);
            
            // Reset button state
            const btn = this.panelElement.querySelector('.btn-heat-map');
            btn.classList.remove('active');
            this.heatMapVisible = false;
        }
    }
    
    renderHeatMap() {
        if (!this.heatMapData || !this.heatMapData.heat_matrix) {
            return;
        }
        
        // Find planogram grid container
        const gridContainer = document.querySelector('.planogram-grid');
        if (!gridContainer) {
            return;
        }
        
        // Remove existing overlay
        const existingOverlay = gridContainer.querySelector('.heat-map-overlay');
        if (existingOverlay) {
            existingOverlay.remove();
        }
        
        // Create heat map overlay
        const overlay = document.createElement('div');
        overlay.className = 'heat-map-overlay';
        
        const matrix = this.heatMapData.heat_matrix;
        const rows = matrix.length;
        const cols = matrix[0] ? matrix[0].length : 0;
        
        // Create heat zones
        matrix.forEach((row, rowIndex) => {
            row.forEach((value, colIndex) => {
                const zone = document.createElement('div');
                zone.className = 'heat-zone';
                zone.style.gridRow = rowIndex + 1;
                zone.style.gridColumn = colIndex + 1;
                
                // Set color based on value
                const hue = (value / 100) * 120; // 0 = red, 120 = green
                zone.style.background = `hsl(${hue}, 70%, 50%)`;
                
                // Add tooltip
                zone.title = `Zone Performance: ${value.toFixed(1)}%`;
                
                overlay.appendChild(zone);
            });
        });
        
        gridContainer.appendChild(overlay);
    }
    
    hideHeatMap() {
        const overlay = document.querySelector('.heat-map-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
    
    async autoOptimize() {
        try {
            // Check prerequisites
            const deviceId = this.getCurrentDeviceId();
            if (!deviceId) {
                this.displayError('Please select a device first to optimize');
                return;
            }
            
            if (window.state && !window.state.currentCabinet) {
                this.displayError('Please select a cabinet first to optimize');
                return;
            }
            
            const planogramData = this.getCurrentPlanogramData();
            if (!planogramData.slots || planogramData.slots.length === 0) {
                this.displayError('No planogram data found to optimize');
                return;
            }
            
            this.displayMessage('Optimizing planogram...');
            
            // Ensure we have heat map data
            if (!this.heatMapData) {
                await this.showHeatMap();
                if (!this.heatMapData) {
                    this.displayError('Could not load heat map data for optimization');
                    return;
                }
            }
            
            const response = await fetch('/api/planograms/optimize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    device_id: deviceId,
                    planogram: planogramData,
                    heat_map: this.heatMapData,
                    constraints: {} // Add any constraints here
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }
            
            const result = await response.json();
            this.applyOptimization(result);
            
        } catch (error) {
            console.error('Optimization error:', error);
            this.displayError(`Unable to optimize planogram: ${error.message}`);
        }
    }
    
    applyOptimization(result) {
        if (!result.recommendations || result.recommendations.length === 0) {
            this.displayMessage('Planogram is already optimized!');
            return;
        }
        
        // Show optimization summary
        const message = `Found ${result.recommendations.length} optimization opportunities. Expected revenue increase: ${result.expected_improvement.revenue_increase}%`;
        this.displayMessage(message);
        
        // Trigger planogram update event
        window.dispatchEvent(new CustomEvent('planogram-optimized', {
            detail: result
        }));
    }
    
    async predictRevenue() {
        try {
            const planogramData = this.getCurrentPlanogramData();
            
            const response = await fetch('/api/planograms/predict/revenue', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    planogram: planogramData,
                    days: 30,
                    include_seasonality: true
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to predict revenue');
            }
            
            const prediction = await response.json();
            this.displayRevenuePrediction(prediction);
            
        } catch (error) {
            console.error('Prediction error:', error);
            this.displayError('Unable to predict revenue');
        }
    }
    
    displayRevenuePrediction(prediction) {
        const predictionSection = this.panelElement.querySelector('.revenue-prediction');
        predictionSection.style.display = 'block';
        
        const changeValue = predictionSection.querySelector('.prediction-value .value');
        const confidenceValue = predictionSection.querySelector('.prediction-confidence .value');
        
        const changePercent = prediction.change_percentage;
        const changeAmount = prediction.expected_change;
        
        changeValue.textContent = `${changePercent > 0 ? '+' : ''}${changePercent.toFixed(1)}%`;
        changeValue.style.color = changePercent > 0 ? '#4CAF50' : '#F44336';
        
        const confidence = prediction.factors?.ai_confidence || 0.5;
        confidenceValue.textContent = confidence > 0.7 ? 'High' : confidence > 0.4 ? 'Medium' : 'Low';
    }
    
    displayError(message) {
        const feedbackEl = this.panelElement.querySelector('.score-feedback');
        feedbackEl.innerHTML = `<span style="color: #F44336;">⚠️ ${message}</span>`;
    }
    
    displayMessage(message) {
        const feedbackEl = this.panelElement.querySelector('.score-feedback');
        feedbackEl.innerHTML = `<span style="color: #4CAF50;">✓ ${message}</span>`;
    }
    
    // Method to refresh planogram data when the page state changes
    refreshPlanogramData() {
        if (typeof window.getCurrentPlanogramData === 'function') {
            window.currentPlanogram = window.getCurrentPlanogramData();
        }
    }
    
    // Helper methods to get current context
    getCurrentDeviceId() {
        // Try to get from URL parameters first
        const urlParams = new URLSearchParams(window.location.search);
        const deviceId = urlParams.get('device_id');
        
        if (deviceId) {
            return parseInt(deviceId);
        }
        
        // Try to get from global window state
        if (window.currentDeviceId) {
            return window.currentDeviceId;
        }
        
        // Try to get from NSPT page state
        if (window.state && window.state.currentAsset && window.state.currentAsset.id) {
            return window.state.currentAsset.id;
        }
        
        // Fallback: try to find device select dropdown
        const selectedDevice = document.querySelector('.device-select')?.value;
        if (selectedDevice) {
            return parseInt(selectedDevice);
        }
        
        console.warn('AI Panel: No device ID found. Please select a device first.');
        return null;
    }
    
    getCurrentPlanogramData() {
        // Try to get from window.currentPlanogram first
        if (window.currentPlanogram) {
            return window.currentPlanogram;
        }
        
        // Try to get from NSPT page state
        if (window.state && window.state.currentAsset && window.state.currentCabinet) {
            // Try to get the planogram key and fetch data
            const planogramKey = window.state.currentCabinet.planogramKey;
            if (planogramKey && window.state.planograms && window.state.planograms[planogramKey]) {
                return window.state.planograms[planogramKey];
            }
        }
        
        // Build from DOM as fallback
        const slots = [];
        const slotElements = document.querySelectorAll('.planogram-slot');
        
        if (slotElements.length === 0) {
            console.warn('AI Panel: No planogram slots found in DOM');
            return { slots: [] };
        }
        
        slotElements.forEach(slot => {
            const row = parseInt(slot.dataset.row);
            const col = parseInt(slot.dataset.column);
            const productId = slot.dataset.productId ? parseInt(slot.dataset.productId) : null;
            
            if (!isNaN(row) && !isNaN(col)) {
                slots.push({
                    row: row,
                    column: col,
                    product_id: productId
                });
            }
        });
        
        console.log('AI Panel: Built planogram data from DOM:', { slots: slots.length });
        return { slots: slots };
    }
}

// Export for use in other modules
window.AIFeedbackPanel = AIFeedbackPanel;