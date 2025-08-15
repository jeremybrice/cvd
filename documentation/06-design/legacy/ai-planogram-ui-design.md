# AI Planogram Enhancement - UI Design Specifications

## Executive Summary

This document provides comprehensive design specifications for AI-enhanced UI components in the CVD planogram management system (NSPT.html), focusing on Phase 1 MVP features. All designs strictly adhere to the CVD Style Guide v2.0, utilizing the established design tokens, SVG icon system, and responsive patterns.

**Target Container**: `container--dashboard` (1440px max-width) for optimal balance between workspace and information density.

---

## Design System Foundation

### Color Palette for AI Features

```css
/* AI-Specific Color Extensions */
:root {
  /* Heat Map Gradient */
  --ai-heat-cold: #e7f3ff;      /* Low revenue potential */
  --ai-heat-cool: #99ccff;      /* Below average */
  --ai-heat-neutral: #ffc107;   /* Average */
  --ai-heat-warm: #ff9800;      /* Above average */
  --ai-heat-hot: #dc3545;       /* High revenue potential */
  
  /* Score Indicators */
  --ai-score-excellent: #28a745;  /* 80-100 */
  --ai-score-good: #17a2b8;       /* 60-79 */
  --ai-score-fair: #ffc107;       /* 40-59 */
  --ai-score-poor: #dc3545;       /* 0-39 */
  
  /* AI Feedback States */
  --ai-processing: #006dfe;
  --ai-success: #28a745;
  --ai-warning: #ffc107;
  --ai-error: #dc3545;
  --ai-neutral: #6c757d;
}
```

### Spacing & Layout Constants

```css
:root {
  /* AI Panel Dimensions */
  --ai-panel-width-desktop: 360px;
  --ai-panel-width-tablet: 320px;
  --ai-panel-height-mobile: 280px;
  --ai-panel-collapsed-height: 48px;
  
  /* Component Spacing */
  --ai-card-padding: var(--space-md);
  --ai-section-gap: var(--space-lg);
  --ai-inline-gap: var(--space-sm);
}
```

---

## 1. Real-time AI Feedback Panel

### Visual Design Specifications

#### Desktop Layout (1024px+)
```css
.ai-feedback-panel {
  position: fixed;
  right: var(--space-lg);
  top: 80px; /* Below toolbar */
  width: var(--ai-panel-width-desktop);
  max-height: calc(100vh - 100px);
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-neutral-200);
  z-index: 100;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.ai-feedback-panel__header {
  padding: var(--space-md);
  background: var(--color-neutral-50);
  border-bottom: 1px solid var(--color-neutral-200);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.ai-feedback-panel__title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--color-neutral-900);
}

.ai-feedback-panel__body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-md);
}
```

#### Tablet Layout (768px-1023px)
```css
@media (min-width: 768px) and (max-width: 1023px) {
  .ai-feedback-panel {
    width: var(--ai-panel-width-tablet);
    right: var(--space-md);
  }
}
```

#### Mobile Layout (0-767px)
```css
@media (max-width: 767px) {
  .ai-feedback-panel {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    top: auto;
    width: 100%;
    max-height: var(--ai-panel-height-mobile);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    transform: translateY(calc(100% - var(--ai-panel-collapsed-height)));
    transition: transform var(--duration-base) var(--ease-out);
  }
  
  .ai-feedback-panel--expanded {
    transform: translateY(0);
  }
  
  .ai-feedback-panel__header {
    cursor: pointer;
    position: relative;
  }
  
  .ai-feedback-panel__header::before {
    content: '';
    position: absolute;
    top: var(--space-xs);
    left: 50%;
    transform: translateX(-50%);
    width: 40px;
    height: 4px;
    background: var(--color-neutral-300);
    border-radius: var(--radius-full);
  }
}
```

### Score Display Component

```css
.ai-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-lg);
  background: var(--color-neutral-50);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-md);
}

.ai-score__value {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  line-height: 1;
  margin-bottom: var(--space-xs);
}

.ai-score__value--excellent { color: var(--ai-score-excellent); }
.ai-score__value--good { color: var(--ai-score-good); }
.ai-score__value--fair { color: var(--ai-score-fair); }
.ai-score__value--poor { color: var(--ai-score-poor); }

.ai-score__label {
  font-size: var(--text-sm);
  color: var(--color-neutral-600);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.ai-score__bar {
  width: 100%;
  height: 8px;
  background: var(--color-neutral-200);
  border-radius: var(--radius-full);
  margin-top: var(--space-md);
  overflow: hidden;
}

.ai-score__bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--duration-base) var(--ease-out);
  background: linear-gradient(90deg, 
    var(--ai-score-poor) 0%, 
    var(--ai-score-fair) 40%, 
    var(--ai-score-good) 60%, 
    var(--ai-score-excellent) 100%);
}
```

### Reasoning Display

```css
.ai-reasoning {
  padding: var(--space-md);
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-md);
}

.ai-reasoning__header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.ai-reasoning__icon {
  width: var(--icon-md);
  height: var(--icon-md);
  color: var(--color-primary-500);
}

.ai-reasoning__title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-neutral-700);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.ai-reasoning__content {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  color: var(--color-neutral-700);
}

.ai-reasoning__list {
  list-style: none;
  padding: 0;
  margin-top: var(--space-sm);
}

.ai-reasoning__item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
  padding-left: var(--space-md);
}

.ai-reasoning__item::before {
  content: '';
  width: 6px;
  height: 6px;
  background: var(--color-primary-500);
  border-radius: var(--radius-full);
  margin-top: 7px;
  flex-shrink: 0;
}
```

### Constraint Violation Indicators

```css
.ai-constraints {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  margin-top: var(--space-md);
}

.ai-constraint {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm);
  background: var(--color-neutral-50);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
}

.ai-constraint--passed {
  background: var(--color-success-bg);
  color: var(--color-success);
  border: 1px solid var(--color-success-border);
}

.ai-constraint--warning {
  background: var(--color-warning-bg);
  color: var(--color-warning);
  border: 1px solid var(--color-warning-border);
}

.ai-constraint--failed {
  background: var(--color-danger-bg);
  color: var(--color-danger);
  border: 1px solid var(--color-danger-border);
}

.ai-constraint__icon {
  width: var(--icon-sm);
  height: var(--icon-sm);
  flex-shrink: 0;
}

.ai-constraint__text {
  flex: 1;
  line-height: var(--leading-tight);
}
```

### Loading States

```css
.ai-feedback-panel__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
  min-height: 200px;
}

.ai-loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--color-neutral-200);
  border-top-color: var(--color-primary-500);
  border-radius: 50%;
  animation: ai-spin 0.8s linear infinite;
  margin-bottom: var(--space-md);
}

@keyframes ai-spin {
  to { transform: rotate(360deg); }
}

.ai-loading-text {
  font-size: var(--text-sm);
  color: var(--color-neutral-600);
  text-align: center;
  animation: ai-pulse 1.5s ease-in-out infinite;
}

@keyframes ai-pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
```

---

## 2. Revenue Heat Map Visualization

### Grid Overlay Design

```css
.heatmap-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.heatmap-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 10;
}

.heatmap-grid {
  display: grid;
  width: 100%;
  height: 100%;
  gap: 2px;
}

.heatmap-cell {
  position: relative;
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast) var(--ease-out);
  opacity: 0.6;
}

.heatmap-cell--cold {
  background: var(--ai-heat-cold);
}

.heatmap-cell--cool {
  background: var(--ai-heat-cool);
}

.heatmap-cell--neutral {
  background: var(--ai-heat-neutral);
}

.heatmap-cell--warm {
  background: var(--ai-heat-warm);
}

.heatmap-cell--hot {
  background: var(--ai-heat-hot);
}

.heatmap-cell:hover {
  opacity: 0.9;
  transform: scale(1.05);
  z-index: 1;
}
```

### Interactive Tooltip

```css
.heatmap-tooltip {
  position: absolute;
  background: var(--color-neutral-900);
  color: var(--color-neutral-0);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  white-space: nowrap;
  pointer-events: none;
  z-index: 1000;
  opacity: 0;
  transform: translateY(-8px);
  transition: all var(--duration-fast) var(--ease-out);
}

.heatmap-tooltip--visible {
  opacity: 1;
  transform: translateY(0);
}

.heatmap-tooltip::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid var(--color-neutral-900);
}

.heatmap-tooltip__value {
  font-weight: var(--font-bold);
  font-size: var(--text-base);
  margin-bottom: var(--space-xs);
}

.heatmap-tooltip__label {
  opacity: 0.8;
  font-size: var(--text-xs);
}
```

### Legend Component

```css
.heatmap-legend {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  margin-top: var(--space-md);
}

.heatmap-legend__title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-neutral-700);
  margin-right: var(--space-sm);
}

.heatmap-legend__scale {
  flex: 1;
  height: 24px;
  background: linear-gradient(90deg, 
    var(--ai-heat-cold) 0%, 
    var(--ai-heat-cool) 25%, 
    var(--ai-heat-neutral) 50%, 
    var(--ai-heat-warm) 75%, 
    var(--ai-heat-hot) 100%);
  border-radius: var(--radius-sm);
  position: relative;
}

.heatmap-legend__labels {
  display: flex;
  justify-content: space-between;
  margin-top: var(--space-xs);
  font-size: var(--text-xs);
  color: var(--color-neutral-600);
}

.heatmap-legend__toggle {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-left: var(--space-md);
}

.heatmap-toggle {
  position: relative;
  width: 48px;
  height: 24px;
  background: var(--color-neutral-300);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}

.heatmap-toggle--active {
  background: var(--color-primary-500);
}

.heatmap-toggle__slider {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: var(--color-neutral-0);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-sm);
  transition: transform var(--duration-fast) var(--ease-out);
}

.heatmap-toggle--active .heatmap-toggle__slider {
  transform: translateX(24px);
}
```

---

## 3. AI Suggestions Sidebar

### Collapsible Panel Design

```css
.ai-suggestions {
  position: fixed;
  left: 0;
  top: 80px;
  bottom: 0;
  width: 320px;
  background: var(--color-neutral-0);
  border-right: 1px solid var(--color-neutral-200);
  box-shadow: var(--shadow-md);
  transform: translateX(-100%);
  transition: transform var(--duration-base) var(--ease-out);
  z-index: 90;
  display: flex;
  flex-direction: column;
}

.ai-suggestions--open {
  transform: translateX(0);
}

.ai-suggestions__toggle {
  position: absolute;
  right: -48px;
  top: 50%;
  transform: translateY(-50%);
  width: 48px;
  height: 80px;
  background: var(--color-primary-500);
  border: none;
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  color: var(--color-neutral-0);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast) var(--ease-out);
}

.ai-suggestions__toggle:hover {
  background: var(--color-primary-600);
  right: -52px;
}

.ai-suggestions__toggle-icon {
  width: var(--icon-lg);
  height: var(--icon-lg);
  transition: transform var(--duration-fast) var(--ease-out);
}

.ai-suggestions--open .ai-suggestions__toggle-icon {
  transform: rotate(180deg);
}
```

### Suggestion Cards

```css
.suggestion-card {
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  margin-bottom: var(--space-md);
  transition: all var(--duration-fast) var(--ease-out);
}

.suggestion-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-200);
}

.suggestion-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-sm);
}

.suggestion-card__confidence {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  background: var(--color-primary-50);
  color: var(--color-primary-700);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}

.suggestion-card__confidence-icon {
  width: var(--icon-xs);
  height: var(--icon-xs);
}

.suggestion-card__title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--color-neutral-900);
  margin-bottom: var(--space-xs);
}

.suggestion-card__description {
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  color: var(--color-neutral-600);
  margin-bottom: var(--space-md);
}

.suggestion-card__preview {
  display: flex;
  gap: var(--space-sm);
  padding: var(--space-sm);
  background: var(--color-neutral-50);
  border-radius: var(--radius-sm);
  margin-bottom: var(--space-md);
}

.suggestion-card__product {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.suggestion-card__product-image {
  width: 40px;
  height: 40px;
  object-fit: contain;
  border-radius: var(--radius-sm);
  background: var(--color-neutral-0);
  padding: var(--space-xs);
}

.suggestion-card__product-name {
  font-size: var(--text-sm);
  color: var(--color-neutral-700);
}

.suggestion-card__arrow {
  display: flex;
  align-items: center;
  color: var(--color-neutral-400);
}

.suggestion-card__actions {
  display: flex;
  gap: var(--space-sm);
}

.suggestion-card__action {
  flex: 1;
  padding: var(--space-sm);
  border-radius: var(--radius-md);
  border: 1px solid;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
}

.suggestion-card__action--accept {
  background: var(--color-success);
  color: var(--color-neutral-0);
  border-color: var(--color-success);
}

.suggestion-card__action--accept:hover {
  background: #218838;
  border-color: #218838;
}

.suggestion-card__action--reject {
  background: var(--color-neutral-0);
  color: var(--color-neutral-700);
  border-color: var(--color-neutral-300);
}

.suggestion-card__action--reject:hover {
  background: var(--color-neutral-50);
  border-color: var(--color-neutral-400);
}
```

### Confidence Score Indicators

```css
.confidence-bar {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.confidence-bar__label {
  font-size: var(--text-xs);
  color: var(--color-neutral-600);
  min-width: 80px;
}

.confidence-bar__track {
  flex: 1;
  height: 6px;
  background: var(--color-neutral-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.confidence-bar__fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--duration-base) var(--ease-out);
}

.confidence-bar__fill--high {
  background: var(--color-success);
}

.confidence-bar__fill--medium {
  background: var(--color-warning);
}

.confidence-bar__fill--low {
  background: var(--color-danger);
}

.confidence-bar__value {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-neutral-700);
  min-width: 35px;
  text-align: right;
}
```

---

## 4. Performance Metrics Dashboard

### KPI Cards

```css
.metrics-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-lg);
  margin-bottom: var(--space-xl);
}

.kpi-card {
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  position: relative;
  overflow: hidden;
  transition: all var(--duration-fast) var(--ease-out);
}

.kpi-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.kpi-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-md);
}

.kpi-card__title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-neutral-600);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.kpi-card__icon {
  width: var(--icon-lg);
  height: var(--icon-lg);
  color: var(--color-primary-500);
  opacity: 0.6;
}

.kpi-card__value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--color-neutral-900);
  line-height: 1;
  margin-bottom: var(--space-sm);
}

.kpi-card__change {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  background: var(--color-success-bg);
  color: var(--color-success);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}

.kpi-card__change--negative {
  background: var(--color-danger-bg);
  color: var(--color-danger);
}

.kpi-card__change-icon {
  width: var(--icon-xs);
  height: var(--icon-xs);
}

.kpi-card__baseline {
  font-size: var(--text-sm);
  color: var(--color-neutral-500);
  margin-top: var(--space-sm);
}
```

### Trend Charts

```css
.trend-chart {
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
}

.trend-chart__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
}

.trend-chart__title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-neutral-900);
}

.trend-chart__controls {
  display: flex;
  gap: var(--space-xs);
}

.trend-chart__period {
  padding: var(--space-xs) var(--space-sm);
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-300);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  color: var(--color-neutral-700);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.trend-chart__period:hover {
  background: var(--color-neutral-50);
}

.trend-chart__period--active {
  background: var(--color-primary-500);
  color: var(--color-neutral-0);
  border-color: var(--color-primary-500);
}

.trend-chart__canvas {
  width: 100%;
  height: 250px;
  margin-bottom: var(--space-md);
}

.trend-chart__legend {
  display: flex;
  gap: var(--space-lg);
  justify-content: center;
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-neutral-200);
}

.trend-chart__legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--text-sm);
  color: var(--color-neutral-600);
}

.trend-chart__legend-color {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-sm);
}
```

### Comparison Views

```css
.comparison-view {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: var(--space-lg);
  padding: var(--space-lg);
  background: var(--color-neutral-50);
  border-radius: var(--radius-lg);
}

.comparison-view__side {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.comparison-view__label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-neutral-700);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-align: center;
  padding: var(--space-sm);
  background: var(--color-neutral-0);
  border-radius: var(--radius-md);
}

.comparison-view__label--before {
  border: 2px solid var(--color-neutral-400);
}

.comparison-view__label--after {
  border: 2px solid var(--color-primary-500);
}

.comparison-view__divider {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
}

.comparison-view__arrow {
  width: var(--icon-xl);
  height: var(--icon-xl);
  color: var(--color-primary-500);
}

.comparison-view__metrics {
  background: var(--color-neutral-0);
  border-radius: var(--radius-md);
  padding: var(--space-md);
}

.comparison-view__metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-sm) 0;
  border-bottom: 1px solid var(--color-neutral-100);
}

.comparison-view__metric:last-child {
  border-bottom: none;
}

.comparison-view__metric-label {
  font-size: var(--text-sm);
  color: var(--color-neutral-600);
}

.comparison-view__metric-value {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--color-neutral-900);
}
```

---

## 5. Mobile-First Responsive Layouts

### Bottom Sheet Pattern (Mobile)

```css
@media (max-width: 767px) {
  .mobile-ai-sheet {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--color-neutral-0);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    box-shadow: var(--shadow-xl);
    z-index: 200;
    transform: translateY(100%);
    transition: transform var(--duration-base) var(--ease-out);
    max-height: 85vh;
    display: flex;
    flex-direction: column;
  }
  
  .mobile-ai-sheet--visible {
    transform: translateY(0);
  }
  
  .mobile-ai-sheet__handle {
    padding: var(--space-md);
    cursor: grab;
    touch-action: pan-y;
  }
  
  .mobile-ai-sheet__handle::before {
    content: '';
    display: block;
    width: 40px;
    height: 4px;
    background: var(--color-neutral-300);
    border-radius: var(--radius-full);
    margin: 0 auto;
  }
  
  .mobile-ai-sheet__content {
    flex: 1;
    overflow-y: auto;
    padding: 0 var(--space-md) var(--space-md);
    -webkit-overflow-scrolling: touch;
  }
}
```

### Touch-Optimized Controls

```css
@media (max-width: 767px) {
  .touch-control {
    min-height: 44px;
    min-width: 44px;
    padding: var(--space-md);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .touch-slider {
    height: 44px;
    padding: var(--space-sm) 0;
  }
  
  .touch-slider__track {
    height: 8px;
    background: var(--color-neutral-200);
    border-radius: var(--radius-full);
    position: relative;
  }
  
  .touch-slider__thumb {
    width: 28px;
    height: 28px;
    background: var(--color-primary-500);
    border: 3px solid var(--color-neutral-0);
    border-radius: var(--radius-full);
    box-shadow: var(--shadow-md);
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    cursor: grab;
    touch-action: pan-x;
  }
  
  .touch-slider__thumb:active {
    cursor: grabbing;
    transform: translateY(-50%) scale(1.1);
  }
}
```

### Swipe Gestures

```css
.swipeable-list {
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.swipeable-list::-webkit-scrollbar {
  display: none;
}

.swipeable-item {
  scroll-snap-align: center;
  flex: 0 0 85%;
  margin: 0 var(--space-sm);
}

.swipe-indicator {
  display: flex;
  justify-content: center;
  gap: var(--space-xs);
  padding: var(--space-md);
}

.swipe-indicator__dot {
  width: 8px;
  height: 8px;
  background: var(--color-neutral-300);
  border-radius: var(--radius-full);
  transition: all var(--duration-fast) var(--ease-out);
}

.swipe-indicator__dot--active {
  width: 24px;
  background: var(--color-primary-500);
}
```

---

## 6. Loading & Error States

### Skeleton Loaders

```css
.ai-skeleton {
  animation: ai-skeleton-shimmer 1.5s ease-in-out infinite;
  background: linear-gradient(
    90deg,
    var(--color-neutral-100) 0%,
    var(--color-neutral-50) 50%,
    var(--color-neutral-100) 100%
  );
  background-size: 200% 100%;
  border-radius: var(--radius-md);
}

@keyframes ai-skeleton-shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.ai-skeleton--text {
  height: var(--text-base);
  margin-bottom: var(--space-sm);
}

.ai-skeleton--title {
  height: var(--text-xl);
  width: 60%;
  margin-bottom: var(--space-md);
}

.ai-skeleton--card {
  height: 120px;
  margin-bottom: var(--space-md);
}

.ai-skeleton--chart {
  height: 250px;
  margin-bottom: var(--space-lg);
}
```

### Error States

```css
.ai-error {
  padding: var(--space-lg);
  text-align: center;
  background: var(--color-danger-bg);
  border: 1px solid var(--color-danger-border);
  border-radius: var(--radius-md);
  color: var(--color-danger);
}

.ai-error__icon {
  width: var(--icon-2xl);
  height: var(--icon-2xl);
  margin: 0 auto var(--space-md);
  opacity: 0.6;
}

.ai-error__title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-sm);
}

.ai-error__message {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--space-lg);
}

.ai-error__action {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--color-danger);
  color: var(--color-neutral-0);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.ai-error__action:hover {
  background: #c82333;
}
```

### Empty States

```css
.ai-empty {
  padding: var(--space-xl);
  text-align: center;
  color: var(--color-neutral-600);
}

.ai-empty__illustration {
  width: 120px;
  height: 120px;
  margin: 0 auto var(--space-lg);
  opacity: 0.3;
}

.ai-empty__title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-neutral-700);
  margin-bottom: var(--space-sm);
}

.ai-empty__description {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--space-lg);
}

.ai-empty__action {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--color-primary-500);
  color: var(--color-neutral-0);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.ai-empty__action:hover {
  background: var(--color-primary-600);
}
```

---

## 7. SVG Icon Specifications

### AI-Specific Icons

```html
<!-- AI Assistant Icon -->
<symbol id="icon-ai-assistant" viewBox="0 0 24 24">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
        d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
</symbol>

<!-- Heat Map Icon -->
<symbol id="icon-heatmap" viewBox="0 0 24 24">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
        d="M4 5h3v3H4V5zM10 5h3v3h-3V5zM16 5h3v3h-3V5zM4 10h3v3H4v-3zM10 10h3v3h-3v-3zM16 10h3v3h-3v-3zM4 15h3v3H4v-3zM10 15h3v3h-3v-3zM16 15h3v3h-3v-3z"/>
</symbol>

<!-- Optimization Icon -->
<symbol id="icon-optimize" viewBox="0 0 24 24">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
        d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/>
</symbol>

<!-- Confidence Icon -->
<symbol id="icon-confidence" viewBox="0 0 24 24">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
        d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
</symbol>

<!-- Revenue Icon -->
<symbol id="icon-revenue" viewBox="0 0 24 24">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
        d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
</symbol>
```

### Icon Usage in Components

```css
.ai-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  fill: none;
  stroke: currentColor;
}

.ai-icon--filled {
  fill: currentColor;
  stroke: none;
}

/* Contextual icon colors */
.ai-icon--processing {
  color: var(--ai-processing);
  animation: ai-icon-pulse 1.5s ease-in-out infinite;
}

@keyframes ai-icon-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.ai-icon--success {
  color: var(--ai-success);
}

.ai-icon--warning {
  color: var(--ai-warning);
}

.ai-icon--error {
  color: var(--ai-error);
}
```

---

## 8. Animation Specifications

### Transition Timings

```css
:root {
  /* AI-specific animations */
  --ai-transition-instant: 100ms;
  --ai-transition-fast: 200ms;
  --ai-transition-base: 300ms;
  --ai-transition-slow: 500ms;
  
  /* Easing functions */
  --ai-ease-sharp: cubic-bezier(0.4, 0, 0.6, 1);
  --ai-ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
  --ai-ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

### Loading Animations

```css
@keyframes ai-fade-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes ai-slide-in-right {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

@keyframes ai-scale-in {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.ai-animate-in {
  animation: ai-fade-in var(--ai-transition-base) var(--ai-ease-smooth) both;
}

.ai-animate-slide {
  animation: ai-slide-in-right var(--ai-transition-base) var(--ai-ease-smooth) both;
}

.ai-animate-scale {
  animation: ai-scale-in var(--ai-transition-fast) var(--ai-ease-sharp) both;
}
```

---

## 9. Accessibility Compliance

### ARIA Labels & Roles

```html
<!-- AI Feedback Panel -->
<aside 
  class="ai-feedback-panel" 
  role="complementary"
  aria-label="AI Assistant Feedback"
  aria-live="polite"
  aria-atomic="true">
  
  <div class="ai-score" role="status" aria-label="Placement score">
    <span class="ai-score__value" aria-label="Score: 85 out of 100">85</span>
  </div>
</aside>

<!-- Heat Map -->
<div 
  class="heatmap-container"
  role="img"
  aria-label="Revenue potential heat map">
  
  <div class="heatmap-cell" 
       role="gridcell"
       tabindex="0"
       aria-label="Zone B4: High revenue potential, $45 daily average">
  </div>
</div>

<!-- Suggestion Cards -->
<article 
  class="suggestion-card"
  role="article"
  aria-labelledby="suggestion-title-1">
  
  <h3 id="suggestion-title-1" class="suggestion-card__title">
    Move high-velocity item to eye level
  </h3>
  
  <div class="suggestion-card__actions" role="group" aria-label="Suggestion actions">
    <button 
      class="suggestion-card__action--accept"
      aria-label="Accept suggestion">
      Accept
    </button>
  </div>
</article>
```

### Keyboard Navigation

```css
/* Focus indicators */
.ai-focusable:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}

/* Skip links for screen readers */
.ai-skip-link {
  position: absolute;
  left: -9999px;
  z-index: 999;
}

.ai-skip-link:focus {
  left: 50%;
  transform: translateX(-50%);
  top: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  background: var(--color-primary-500);
  color: var(--color-neutral-0);
  border-radius: var(--radius-md);
}
```

### Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  .ai-feedback-panel,
  .ai-suggestions,
  .heatmap-cell,
  .suggestion-card {
    transition: none !important;
    animation: none !important;
  }
  
  .ai-loading-spinner {
    animation: none;
    border-top-color: var(--color-neutral-600);
  }
}
```

---

## 10. Implementation Guidelines

### Component Integration

```javascript
// Initialize AI components on page load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize feedback panel
    const feedbackPanel = new AIFeedbackPanel({
        container: '.ai-feedback-panel',
        api: new CVDApi(),
        updateInterval: 500 // Real-time update throttle
    });
    
    // Initialize heat map
    const heatMap = new RevenueHeatMap({
        container: '.heatmap-container',
        colorScheme: 'revenue', // 'revenue' | 'velocity' | 'affinity'
        interactive: true
    });
    
    // Initialize suggestions sidebar
    const suggestions = new AISuggestionsSidebar({
        container: '.ai-suggestions',
        maxSuggestions: 5,
        autoRefresh: true
    });
    
    // Initialize metrics dashboard
    const metrics = new PerformanceMetrics({
        container: '.metrics-dashboard',
        refreshInterval: 30000 // Update every 30 seconds
    });
});
```

### Performance Optimization

```css
/* Use CSS containment for performance */
.ai-feedback-panel,
.ai-suggestions,
.metrics-dashboard {
  contain: layout style;
}

/* Hardware acceleration for animations */
.ai-animate-in,
.heatmap-cell,
.suggestion-card {
  will-change: transform, opacity;
}

/* Remove will-change after animation */
.ai-animate-complete {
  will-change: auto;
}
```

### Browser Support

```css
/* Progressive enhancement for older browsers */
@supports not (display: grid) {
  .metrics-dashboard {
    display: flex;
    flex-wrap: wrap;
  }
  
  .metrics-dashboard > * {
    flex: 1 1 240px;
  }
}

/* Fallback for CSS variables */
.ai-feedback-panel {
  background: #ffffff;
  background: var(--color-neutral-0);
}
```

---

## Component States Reference

### Real-time Feedback States
- **Idle**: Waiting for user interaction
- **Processing**: Analyzing placement (show spinner)
- **Success**: Valid placement with score
- **Warning**: Constraint violations
- **Error**: API failure or timeout

### Heat Map States
- **Loading**: Initial data fetch
- **Active**: Interactive with hover tooltips
- **Disabled**: View-only mode
- **Updating**: Refreshing data

### Suggestion States
- **Pending**: New suggestion available
- **Reviewing**: User viewing details
- **Accepted**: Applied to planogram
- **Rejected**: Dismissed by user
- **Expired**: No longer valid

### Metric States
- **Current**: Real-time data
- **Calculating**: Processing prediction
- **Comparison**: Before/after view
- **Historical**: Trend analysis

---

## Quality Assurance Checklist

### Design System Compliance
- [x] All colors from CVD palette with verified contrast ratios
- [x] Typography follows established hierarchy and scale
- [x] Spacing uses 4px grid system consistently
- [x] Components use documented border radius values
- [x] Shadows match defined elevation system
- [x] Animation timings use standard durations

### Accessibility
- [x] WCAG AA contrast ratios (4.5:1 normal, 3:1 large text)
- [x] All interactive elements have 44×44px minimum touch targets
- [x] Proper ARIA labels and roles throughout
- [x] Keyboard navigation fully supported
- [x] Screen reader optimized with semantic HTML
- [x] Reduced motion alternatives provided

### Responsive Design
- [x] Mobile-first approach with progressive enhancement
- [x] Touch-optimized controls on mobile devices
- [x] Appropriate container widths per breakpoint
- [x] Flexible grid systems for all screen sizes
- [x] Swipe gestures for mobile navigation
- [x] Bottom sheet pattern for mobile panels

### Performance
- [x] CSS containment for layout optimization
- [x] Hardware acceleration for animations
- [x] Lazy loading for non-critical components
- [x] Throttled real-time updates (500ms)
- [x] Efficient selector specificity
- [x] Progressive enhancement fallbacks

### SVG Icons
- [x] All icons from approved CVD sprite sheet
- [x] No emoji usage throughout specifications
- [x] Consistent icon sizing using CSS variables
- [x] Proper color inheritance with currentColor
- [x] Accessible with aria-hidden where decorative

---

## Conclusion

These comprehensive design specifications provide a complete blueprint for implementing AI-enhanced features in the CVD planogram management system. All components strictly adhere to the CVD Style Guide v2.0, ensuring consistency, accessibility, and professional presentation.

The designs prioritize:
- **User efficiency** through real-time feedback and intelligent suggestions
- **Data clarity** with intuitive visualizations and clear metrics
- **Accessibility** with WCAG AA compliance throughout
- **Performance** with optimized animations and responsive layouts
- **Consistency** using established CVD design tokens and patterns

Implementation should proceed in phases as outlined in the AI implementation plan, with Phase 1 MVP focusing on core components: Real-time AI Feedback Panel, Revenue Heat Map, and basic Performance Metrics.

---

*Document Version: 1.0*  
*Created: 2025*  
*Design System: CVD Style Guide v2.0*  
*Container Strategy: container--dashboard (1440px)*