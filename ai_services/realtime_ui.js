/**
 * Real-time Planogram AI Assistant UI Integration
 * Provides immediate feedback and suggestions while users work
 */

class RealtimeAssistant {
    constructor(apiClient) {
        this.api = apiClient;
        this.isActive = true;
        this.debounceTimer = null;
        this.currentAnalysis = null;
        this.feedbackPanel = null;
        this.initializeUI();
    }
    
    initializeUI() {
        // Create floating feedback panel
        this.createFeedbackPanel();
        
        // Create placement indicator overlay
        this.createPlacementIndicator();
        
        // Setup event listeners for drag events
        this.setupDragListeners();
        
        // Initialize WebSocket for streaming
        this.initializeStreaming();
    }
    
    createFeedbackPanel() {
        const panel = document.createElement('div');
        panel.id = 'realtime-feedback';
        panel.className = 'realtime-feedback-panel';
        panel.innerHTML = `
            <div class="feedback-header">
                <span class="feedback-title">🤖 AI Assistant</span>
                <button class="feedback-toggle" onclick="realtimeAssistant.togglePanel()">−</button>
            </div>
            <div class="feedback-content">
                <div class="placement-score">
                    <div class="score-circle">
                        <span class="score-value">--</span>
                        <span class="score-label">Score</span>
                    </div>
                    <div class="score-details">
                        <p class="score-reasoning">Hover over a slot to see analysis</p>
                    </div>
                </div>
                <div class="quick-suggestions">
                    <!-- Suggestions will be inserted here -->
                </div>
                <div class="constraint-warnings">
                    <!-- Warnings will be inserted here -->
                </div>
            </div>
        `;
        document.body.appendChild(panel);
        this.feedbackPanel = panel;
    }
    
    createPlacementIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'placement-indicator';
        indicator.className = 'placement-indicator';
        indicator.style.display = 'none';
        document.body.appendChild(indicator);
        this.indicator = indicator;
    }
    
    setupDragListeners() {
        // Listen for drag events on product catalog
        document.addEventListener('dragstart', (e) => {
            if (e.target.classList.contains('product-item')) {
                this.handleDragStart(e);
            }
        });
        
        // Listen for dragover on planogram slots
        document.addEventListener('dragover', (e) => {
            if (e.target.classList.contains('planogram-slot')) {
                e.preventDefault();
                this.handleDragOver(e);
            }
        });
        
        // Listen for drop events
        document.addEventListener('drop', (e) => {
            if (e.target.classList.contains('planogram-slot')) {
                this.handleDrop(e);
            }
        });
    }
    
    handleDragStart(event) {
        const productData = {
            id: parseInt(event.target.dataset.productId),
            name: event.target.dataset.productName,
            category: event.target.dataset.category,
            price: parseFloat(event.target.dataset.price),
            velocity: parseFloat(event.target.dataset.velocity || 0)
        };
        
        this.currentProduct = productData;
        
        // Show placement hints
        this.highlightOptimalSlots(productData);
    }
    
    handleDragOver(event) {
        const slot = event.target;
        const slotPosition = slot.dataset.position;
        
        // Debounce API calls
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.analyzeProposedPlacement(slotPosition);
        }, 200);
        
        // Update visual indicator
        this.updatePlacementIndicator(slot);
    }
    
    async analyzeProposedPlacement(slotPosition) {
        if (!this.currentProduct) return;
        
        try {
            const response = await fetch('/api/planograms/realtime-analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    device_id: window.currentDeviceId,
                    cabinet_index: window.currentCabinetIndex,
                    action: 'drag_over',
                    product: this.currentProduct,
                    slot: slotPosition
                })
            });
            
            const analysis = await response.json();
            
            if (analysis.success) {
                this.displayAnalysis(analysis.analysis);
                this.updateSlotHighlight(slotPosition, analysis.analysis.score);
            }
        } catch (error) {
            console.error('Analysis failed:', error);
        }
    }
    
    displayAnalysis(analysis) {
        // Update score circle
        const scoreElement = this.feedbackPanel.querySelector('.score-value');
        const reasoningElement = this.feedbackPanel.querySelector('.score-reasoning');
        const scoreCircle = this.feedbackPanel.querySelector('.score-circle');
        
        scoreElement.textContent = analysis.score;
        reasoningElement.textContent = analysis.reasoning;
        
        // Update score color
        scoreCircle.className = 'score-circle';
        if (analysis.score >= 80) {
            scoreCircle.classList.add('score-excellent');
        } else if (analysis.score >= 60) {
            scoreCircle.classList.add('score-good');
        } else {
            scoreCircle.classList.add('score-poor');
        }
        
        // Show improvement suggestion if score is low
        if (analysis.score < 70 && analysis.improvement) {
            this.showImprovementSuggestion(analysis.improvement);
        }
        
        // Animate score update
        this.animateScoreUpdate(scoreElement, analysis.score);
    }
    
    updateSlotHighlight(slotPosition, score) {
        const slot = document.querySelector(`[data-position="${slotPosition}"]`);
        if (!slot) return;
        
        // Remove previous highlights
        document.querySelectorAll('.slot-highlight').forEach(el => {
            el.classList.remove('slot-highlight', 'highlight-good', 'highlight-poor');
        });
        
        // Add new highlight based on score
        slot.classList.add('slot-highlight');
        if (score >= 70) {
            slot.classList.add('highlight-good');
        } else {
            slot.classList.add('highlight-poor');
        }
    }
    
    highlightOptimalSlots(product) {
        // Request optimal slots from AI
        fetch('/api/planograms/optimal-slots', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                device_id: window.currentDeviceId,
                cabinet_index: window.currentCabinetIndex,
                product: product
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.optimal_slots) {
                data.optimal_slots.forEach(slot => {
                    const element = document.querySelector(`[data-position="${slot.position}"]`);
                    if (element && element.classList.contains('empty-slot')) {
                        element.classList.add('optimal-slot');
                        element.title = `Recommended: ${slot.reason}`;
                    }
                });
            }
        });
    }
    
    showImprovementSuggestion(suggestion) {
        const suggestionsDiv = this.feedbackPanel.querySelector('.quick-suggestions');
        suggestionsDiv.innerHTML = `
            <div class="suggestion-card">
                <span class="suggestion-icon">💡</span>
                <p>${suggestion}</p>
            </div>
        `;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            suggestionsDiv.innerHTML = '';
        }, 5000);
    }
    
    animateScoreUpdate(element, targetScore) {
        const startScore = parseInt(element.textContent) || 0;
        const duration = 500;
        const steps = 20;
        const increment = (targetScore - startScore) / steps;
        let currentStep = 0;
        
        const interval = setInterval(() => {
            currentStep++;
            const newScore = Math.round(startScore + (increment * currentStep));
            element.textContent = newScore;
            
            if (currentStep >= steps) {
                clearInterval(interval);
                element.textContent = targetScore;
            }
        }, duration / steps);
    }
    
    initializeStreaming() {
        // Setup EventSource for streaming analysis
        this.eventSource = null;
        
        // Method to start streaming
        this.startStreaming = () => {
            if (this.eventSource) {
                this.eventSource.close();
            }
            
            this.eventSource = new EventSource('/api/planograms/stream-analysis');
            
            this.eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleStreamUpdate(data);
            };
            
            this.eventSource.onerror = (error) => {
                console.error('Streaming error:', error);
                this.eventSource.close();
            };
        };
    }
    
    handleStreamUpdate(data) {
        // Update UI with streaming data
        if (data.stage === 'analyzing_layout') {
            this.showProgress('Analyzing current layout...', data.progress);
        } else if (data.stage === 'generating_suggestions') {
            this.showProgress('Generating suggestions...', data.progress);
        }
        
        if (data.suggestions) {
            this.displaySuggestions(data.suggestions);
        }
    }
    
    showProgress(message, progress) {
        const progressDiv = document.createElement('div');
        progressDiv.className = 'analysis-progress';
        progressDiv.innerHTML = `
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${progress}%"></div>
            </div>
            <p class="progress-message">${message}</p>
        `;
        
        const content = this.feedbackPanel.querySelector('.feedback-content');
        const existing = content.querySelector('.analysis-progress');
        if (existing) {
            existing.replaceWith(progressDiv);
        } else {
            content.appendChild(progressDiv);
        }
        
        if (progress === 100) {
            setTimeout(() => progressDiv.remove(), 1000);
        }
    }
    
    togglePanel() {
        this.feedbackPanel.classList.toggle('minimized');
    }
    
    // Constraint validation on drop
    async validateConstraints(product, slot) {
        const response = await fetch('/api/planograms/validate-constraints', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                device_id: window.currentDeviceId,
                cabinet_index: window.currentCabinetIndex,
                changes: [{
                    slot: slot,
                    product: product,
                    action: 'add'
                }]
            })
        });
        
        const result = await response.json();
        
        if (!result.overall_valid) {
            this.showConstraintWarnings(result.validations);
            return false;
        }
        
        return true;
    }
    
    showConstraintWarnings(validations) {
        const warningsDiv = this.feedbackPanel.querySelector('.constraint-warnings');
        warningsDiv.innerHTML = '<h4>⚠️ Constraint Violations:</h4>';
        
        validations.forEach(validation => {
            if (!validation.valid) {
                validation.validations.forEach(v => {
                    warningsDiv.innerHTML += `
                        <div class="warning-item">
                            <span class="warning-icon">⚠️</span>
                            <span>${v.message}</span>
                        </div>
                    `;
                });
            }
        });
        
        // Auto-clear after 5 seconds
        setTimeout(() => {
            warningsDiv.innerHTML = '';
        }, 5000);
    }
}

// CSS for the real-time assistant
const assistantStyles = `
<style>
.realtime-feedback-panel {
    position: fixed;
    right: 20px;
    top: 100px;
    width: 320px;
    background: white;
    border: 1px solid #e1e5e8;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    z-index: 1000;
    transition: all 0.3s ease;
}

.realtime-feedback-panel.minimized {
    height: 40px;
    overflow: hidden;
}

.feedback-header {
    padding: 12px 16px;
    border-bottom: 1px solid #e1e5e8;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f8f9fa;
    border-radius: 8px 8px 0 0;
}

.feedback-title {
    font-weight: 600;
    color: #2c3e50;
}

.feedback-content {
    padding: 16px;
}

.placement-score {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
}

.score-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #f0f0f0;
    transition: all 0.3s ease;
}

.score-circle.score-excellent {
    background: linear-gradient(135deg, #27ae60, #2ecc71);
    color: white;
}

.score-circle.score-good {
    background: linear-gradient(135deg, #f39c12, #f1c40f);
    color: white;
}

.score-circle.score-poor {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
    color: white;
}

.score-value {
    font-size: 24px;
    font-weight: bold;
}

.score-label {
    font-size: 12px;
    opacity: 0.8;
}

.score-details {
    flex: 1;
}

.score-reasoning {
    font-size: 14px;
    color: #7f8c8d;
    margin: 0;
}

.suggestion-card {
    background: #e8f4fd;
    border-left: 3px solid #006dfe;
    padding: 12px;
    border-radius: 4px;
    display: flex;
    gap: 8px;
    align-items: start;
    margin-top: 12px;
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.warning-item {
    background: #fff3cd;
    border-left: 3px solid #ffc107;
    padding: 8px 12px;
    margin-top: 8px;
    border-radius: 4px;
    font-size: 14px;
}

.slot-highlight.highlight-good {
    box-shadow: 0 0 0 3px rgba(39, 174, 96, 0.5);
    animation: pulse-good 1s infinite;
}

.slot-highlight.highlight-poor {
    box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.5);
    animation: pulse-poor 1s infinite;
}

@keyframes pulse-good {
    0% { box-shadow: 0 0 0 3px rgba(39, 174, 96, 0.5); }
    50% { box-shadow: 0 0 0 6px rgba(39, 174, 96, 0.2); }
    100% { box-shadow: 0 0 0 3px rgba(39, 174, 96, 0.5); }
}

@keyframes pulse-poor {
    0% { box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.5); }
    50% { box-shadow: 0 0 0 6px rgba(231, 76, 60, 0.2); }
    100% { box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.5); }
}

.optimal-slot {
    background: rgba(39, 174, 96, 0.1) !important;
    border: 2px dashed #27ae60 !important;
}

.progress-bar {
    height: 4px;
    background: #e1e5e8;
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 8px;
}

.progress-fill {
    height: 100%;
    background: #006dfe;
    transition: width 0.3s ease;
}

.progress-message {
    font-size: 12px;
    color: #7f8c8d;
    margin: 0;
}
</style>
`;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Add styles
    document.head.insertAdjacentHTML('beforeend', assistantStyles);
    
    // Initialize assistant if API client exists
    if (window.cvdApi) {
        window.realtimeAssistant = new RealtimeAssistant(window.cvdApi);
    }
});