---
title: Service Order Execution Flow
description: Complete mobile-first workflow for field service execution by drivers using the CVD PWA
feature: service-orders
last-updated: 2025-08-12
version: 2.1.0
related-files:
  - USER_FLOWS_OVERVIEW.md
  - ../components/UI_COMPONENTS_OVERVIEW.md
  - MOBILE_APP_WORKFLOWS.md
dependencies:
  - service-order-system
  - mobile-pwa-framework
  - offline-sync-capabilities
status: active
---

# Service Order Execution Flow


## Metadata
- **ID**: 06_DESIGN_USER_FLOWS_SERVICE_ORDER_EXECUTION
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #debugging #device-management #driver-app #integration #interface #logistics #machine-learning #metrics #mobile #operations #optimization #performance #planogram #product-placement #pwa #reporting #route-management #security #service-orders #troubleshooting #ui-design #user-experience #vending-machine
- **Intent**: The service order execution flow is the critical mobile workflow that enables drivers to efficiently complete field service tasks
- **Audience**: managers, end users, architects
- **Related**: USER_FLOWS_OVERVIEW.md, LOGIN_FLOW.md, MOBILE_APP_WORKFLOWS.md, UI_COMPONENTS_OVERVIEW.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/06-design/user-flows/
- **Category**: User Flows
- **Search Keywords**: 2025-08-12, accessibility, alternative, annotation, arrival, automatic, average, cabinet, camera, capability:, check, check-in, completion, complexity, conflict

## Overview

The service order execution flow is the critical mobile workflow that enables drivers to efficiently complete field service tasks. This flow is optimized for single-handed operation, offline capability, and rapid task completion while maintaining accurate inventory tracking and service documentation.

## Flow Metadata

- **Flow Name**: Service Order Execution (Mobile)
- **User Roles**: Driver (primary), Manager (monitoring)
- **Frequency**: Multiple times daily per driver
- **Complexity**: Medium-High (offline synchronization, photo capture)
- **Devices**: Mobile PWA (primary), Tablet (secondary)
- **Dependencies**: Service orders, inventory data, camera access, GPS

## Flow Triggers

### Primary Entry Points

1. **Push Notification**: New order assigned to driver
2. **Route Start**: Beginning daily service route
3. **Manual Check**: Driver checking for available orders
4. **Order Continuation**: Resuming partially completed order
5. **Emergency Service**: Urgent repair or restock request

### Context-Aware Scenarios

- **Offline Continuation**: Resuming work without internet connection
- **Location Arrival**: GPS-triggered order presentation
- **Schedule Deviation**: Handling route changes or delays
- **Multi-Cabinet Service**: Managing complex multi-unit locations

## User Journey Breakdown

### Phase 1: Order Discovery & Selection (30 seconds - 2 minutes)

#### Entry State: Driver Dashboard

**Mobile Dashboard Layout**:
```html
<div class="driver-dashboard">
  <header class="mobile-header">
    <div class="header-content">
      <div class="driver-info">
        <div class="driver-greeting">Good morning, <strong>John</strong></div>
        <div class="route-info">
          Route 1 - Downtown • <span class="orders-remaining">6 orders remaining</span>
        </div>
      </div>
      
      <div class="header-actions">
        <button class="sync-button" id="syncStatus" aria-label="Sync status">
          <svg class="icon icon--sm sync-icon" aria-hidden="true">
            <use href="#icon-refresh"></use>
          </svg>
          <span class="sync-text">Synced</span>
        </button>
      </div>
    </div>
  </header>
  
  <div class="dashboard-content">
    <div class="route-progress">
      <div class="progress-header">
        <h2 class="progress-title">Today's Route</h2>
        <div class="progress-stats">
          <span class="completed">2 completed</span> • 
          <span class="remaining">4 active</span> • 
          <span class="total">6 total</span>
        </div>
      </div>
      
      <div class="progress-bar">
        <div class="progress-fill" style="width: 33%"></div>
      </div>
    </div>
    
    <div class="order-queue">
      <div class="queue-header">
        <h3 class="queue-title">Next Orders</h3>
        <button class="btn btn--ghost btn--sm" onclick="optimizeRoute()">
          <svg class="icon icon--xs" aria-hidden="true">
            <use href="#icon-navigation"></use>
          </svg>
          Optimize Route
        </button>
      </div>
      
      <div class="order-list">
        <!-- High Priority Order -->
        <div class="order-card order-card--priority" onclick="selectOrder('SO-001')">
          <div class="order-header">
            <div class="order-priority">
              <svg class="icon icon--sm icon--danger" aria-hidden="true">
                <use href="#icon-alert-triangle"></use>
              </svg>
              <span class="priority-label">High Priority</span>
            </div>
            <div class="order-distance">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-navigation"></use>
              </svg>
              2.3 mi • 8 min
            </div>
          </div>
          
          <div class="order-location">
            <h4 class="location-name">Office Building A - 2nd Floor</h4>
            <div class="location-address">123 Business Park Dr</div>
          </div>
          
          <div class="order-summary">
            <div class="device-info">
              <svg class="icon icon--sm" aria-hidden="true">
                <use href="#icon-server"></use>
              </svg>
              <span class="device-name">Snack Machine Alpha</span>
            </div>
            
            <div class="task-summary">
              <div class="task-item">
                <svg class="icon icon--xs icon--warning" aria-hidden="true">
                  <use href="#icon-package"></use>
                </svg>
                <span class="task-text">8 items to restock</span>
              </div>
              
              <div class="task-item">
                <svg class="icon icon--xs icon--info" aria-hidden="true">
                  <use href="#icon-wrench"></use>
                </svg>
                <span class="task-text">Check coin mechanism</span>
              </div>
            </div>
          </div>
          
          <div class="order-actions">
            <button class="btn btn--primary btn--sm" onclick="startOrder('SO-001')">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-play"></use>
              </svg>
              Start Service
            </button>
          </div>
        </div>
        
        <!-- Standard Priority Order -->
        <div class="order-card" onclick="selectOrder('SO-002')">
          <div class="order-header">
            <div class="order-id">SO-002</div>
            <div class="order-distance">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-navigation"></use>
              </svg>
              1.8 mi • 6 min
            </div>
          </div>
          
          <div class="order-location">
            <h4 class="location-name">Warehouse B - Employee Break Room</h4>
          </div>
          
          <div class="order-summary">
            <div class="device-info">
              <svg class="icon icon--sm" aria-hidden="true">
                <use href="#icon-server"></use>
              </svg>
              <span class="device-name">Beverage Machine Beta</span>
            </div>
            
            <div class="task-summary">
              <div class="task-item">
                <svg class="icon icon--xs" aria-hidden="true">
                  <use href="#icon-package"></use>
                </svg>
                <span class="task-text">Regular restock</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- More orders... -->
      </div>
    </div>
  </div>
  
  <!-- Bottom Navigation -->
  <nav class="bottom-nav">
    <a href="#dashboard" class="nav-item nav-item--active">
      <svg class="icon nav-icon" aria-hidden="true">
        <use href="#icon-home"></use>
      </svg>
      <span class="nav-label">Dashboard</span>
    </a>
    
    <a href="#orders" class="nav-item">
      <svg class="icon nav-icon" aria-hidden="true">
        <use href="#icon-clipboard-list"></use>
      </svg>
      <span class="nav-label">Orders</span>
      <span class="nav-badge">6</span>
    </a>
    
    <a href="#inventory" class="nav-item">
      <svg class="icon nav-icon" aria-hidden="true">
        <use href="#icon-package"></use>
      </svg>
      <span class="nav-label">Inventory</span>
    </a>
    
    <a href="#profile" class="nav-item">
      <svg class="icon nav-icon" aria-hidden="true">
        <use href="#icon-user"></use>
      </svg>
      <span class="nav-label">Profile</span>
    </a>
  </nav>
</div>
```

#### Order Selection & Navigation

**Order Detail View**:
```html
<div class="order-detail">
  <header class="mobile-header">
    <div class="header-content">
      <button class="header-back" onclick="goBack()" aria-label="Go back">
        <svg class="icon icon--md" aria-hidden="true">
          <use href="#icon-arrow-left"></use>
        </svg>
      </button>
      
      <div class="header-title">
        <h1 class="order-title">Service Order SO-001</h1>
        <div class="order-status">
          <span class="status-badge status-badge--warning">
            <svg class="icon icon--xs" aria-hidden="true">
              <use href="#icon-clock"></use>
            </svg>
            In Progress
          </span>
        </div>
      </div>
      
      <div class="header-actions">
        <button class="header-action" onclick="getDirections()" aria-label="Get directions">
          <svg class="icon icon--md" aria-hidden="true">
            <use href="#icon-navigation"></use>
          </svg>
        </button>
      </div>
    </div>
  </header>
  
  <div class="order-content">
    <div class="location-section">
      <div class="location-card">
        <div class="location-header">
          <h2 class="location-name">Office Building A - 2nd Floor</h2>
          <button class="btn btn--primary btn--sm" onclick="getDirections()">
            <svg class="icon icon--xs" aria-hidden="true">
              <use href="#icon-navigation"></use>
            </svg>
            Directions
          </button>
        </div>
        
        <div class="location-details">
          <div class="location-address">
            123 Business Park Drive<br>
            Springfield, IL 62701
          </div>
          
          <div class="location-distance">
            <svg class="icon icon--xs" aria-hidden="true">
              <use href="#icon-map-pin"></use>
            </svg>
            2.3 miles away • Est. 8 minutes
          </div>
        </div>
        
        <div class="location-notes" id="locationNotes">
          <div class="notes-header">
            <svg class="icon icon--sm" aria-hidden="true">
              <use href="#icon-info-circle"></use>
            </svg>
            <span class="notes-title">Access Notes</span>
          </div>
          <div class="notes-content">
            Use main elevator to 2nd floor. Machine is in break room next to kitchen.
            Building requires visitor badge at reception.
          </div>
        </div>
      </div>
    </div>
    
    <div class="device-section">
      <div class="device-card">
        <div class="device-header">
          <div class="device-info">
            <svg class="icon icon--lg" aria-hidden="true">
              <use href="#icon-server"></use>
            </svg>
            <div class="device-details">
              <h3 class="device-name">Snack Machine Alpha</h3>
              <div class="device-id">DEV-001 • Serial: SM2025001</div>
              <div class="device-status">
                <span class="status-badge status-badge--success">
                  <svg class="icon icon--xs" aria-hidden="true">
                    <use href="#icon-wifi"></use>
                  </svg>
                  Online
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="service-tasks">
          <h4 class="tasks-title">Service Tasks</h4>
          
          <div class="task-list">
            <div class="task-item task-item--primary">
              <div class="task-icon">
                <svg class="icon icon--sm icon--warning" aria-hidden="true">
                  <use href="#icon-package"></use>
                </svg>
              </div>
              <div class="task-content">
                <div class="task-title">Restock Low Inventory</div>
                <div class="task-description">8 product slots need restocking</div>
                <div class="task-progress">
                  <div class="progress-bar progress-bar--sm">
                    <div class="progress-fill" style="width: 0%"></div>
                  </div>
                  <span class="progress-text">0 of 8 complete</span>
                </div>
              </div>
            </div>
            
            <div class="task-item">
              <div class="task-icon">
                <svg class="icon icon--sm icon--info" aria-hidden="true">
                  <use href="#icon-wrench"></use>
                </svg>
              </div>
              <div class="task-content">
                <div class="task-title">Maintenance Check</div>
                <div class="task-description">Inspect coin mechanism operation</div>
              </div>
            </div>
            
            <div class="task-item">
              <div class="task-icon">
                <svg class="icon icon--sm" aria-hidden="true">
                  <use href="#icon-clipboard-list"></use>
                </svg>
              </div>
              <div class="task-content">
                <div class="task-title">Service Documentation</div>
                <div class="task-description">Take photos and update service log</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <div class="order-actions">
    <button class="btn btn--primary btn--large btn--block" onclick="beginService()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-play"></use>
      </svg>
      Begin Service at Location
    </button>
  </div>
</div>
```

### Phase 2: Location Arrival & Check-in (1-3 minutes)

#### GPS Arrival Detection

**Automatic Check-in Prompt**:
```html
<div class="arrival-prompt" id="arrivalPrompt">
  <div class="prompt-content">
    <div class="prompt-icon">
      <svg class="icon icon--xl icon--success" aria-hidden="true">
        <use href="#icon-map-pin"></use>
      </svg>
    </div>
    
    <h3 class="prompt-title">You've arrived!</h3>
    <p class="prompt-message">
      GPS detected you're at <strong>Office Building A</strong>.
      Ready to start service?
    </p>
    
    <div class="prompt-actions">
      <button class="btn btn--primary btn--large" onclick="confirmArrival()">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-check"></use>
        </svg>
        Yes, I'm Here
      </button>
      
      <button class="btn btn--secondary" onclick="manualLocation()">
        Not Quite Right
      </button>
    </div>
  </div>
</div>
```

**Manual Check-in Alternative**:
```html
<div class="manual-checkin">
  <div class="checkin-header">
    <h2 class="checkin-title">Confirm Your Location</h2>
    <p class="checkin-description">
      Let us know when you arrive at the service location
    </p>
  </div>
  
  <div class="location-verification">
    <div class="location-display">
      <div class="location-icon">
        <svg class="icon icon--lg" aria-hidden="true">
          <use href="#icon-building"></use>
        </svg>
      </div>
      <div class="location-info">
        <div class="location-name">Office Building A - 2nd Floor</div>
        <div class="location-address">123 Business Park Drive</div>
      </div>
    </div>
    
    <div class="checkin-options">
      <button class="checkin-option" onclick="confirmLocation()">
        <svg class="icon icon--md" aria-hidden="true">
          <use href="#icon-check-circle"></use>
        </svg>
        <div class="option-content">
          <div class="option-title">I'm at this location</div>
          <div class="option-description">Ready to start service</div>
        </div>
      </button>
      
      <button class="checkin-option" onclick="reportIssue()">
        <svg class="icon icon--md" aria-hidden="true">
          <use href="#icon-alert-triangle"></use>
        </svg>
        <div class="option-content">
          <div class="option-title">I can't access this location</div>
          <div class="option-description">Report access issue</div>
        </div>
      </button>
      
      <button class="checkin-option" onclick="postponeService()">
        <svg class="icon icon--md" aria-hidden="true">
          <use href="#icon-clock"></use>
        </svg>
        <div class="option-content">
          <div class="option-title">Need to come back later</div>
          <div class="option-description">Reschedule this service</div>
        </div>
      </button>
    </div>
  </div>
</div>
```

### Phase 3: Service Task Execution (10-45 minutes)

#### Service Workspace Interface

**Task-Focused Service View**:
```html
<div class="service-workspace">
  <header class="service-header">
    <div class="service-progress">
      <button class="progress-back" onclick="pauseService()" aria-label="Pause service">
        <svg class="icon icon--md" aria-hidden="true">
          <use href="#icon-pause"></use>
        </svg>
      </button>
      
      <div class="progress-info">
        <div class="progress-title">Restocking Items</div>
        <div class="progress-detail">
          <span class="current-task">3</span> of <span class="total-tasks">8</span> complete
        </div>
      </div>
      
      <div class="progress-indicator">
        <div class="progress-ring">
          <svg class="progress-circle" viewBox="0 0 36 36">
            <path class="progress-track" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
            <path class="progress-fill" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" 
                  stroke-dasharray="37.5, 100"/>
          </svg>
        </div>
        <div class="progress-percent">38%</div>
      </div>
    </div>
  </header>
  
  <div class="service-content">
    <div class="current-task-card">
      <div class="task-header">
        <div class="task-info">
          <h2 class="task-title">Slot A3 - Lay's Classic Chips</h2>
          <div class="task-location">Row A, Position 3</div>
        </div>
        
        <div class="task-status">
          <span class="status-badge status-badge--warning">
            <svg class="icon icon--xs" aria-hidden="true">
              <use href="#icon-package"></use>
            </svg>
            Low Stock
          </span>
        </div>
      </div>
      
      <div class="inventory-details">
        <div class="inventory-grid">
          <div class="inventory-item">
            <div class="inventory-label">Current Stock</div>
            <div class="inventory-value">2 items</div>
          </div>
          
          <div class="inventory-item">
            <div class="inventory-label">Capacity</div>
            <div class="inventory-value">10 items</div>
          </div>
          
          <div class="inventory-item">
            <div class="inventory-label">Par Level</div>
            <div class="inventory-value">3 items</div>
          </div>
          
          <div class="inventory-item">
            <div class="inventory-label">Restock Amount</div>
            <div class="inventory-value inventory-value--highlight">8 items</div>
          </div>
        </div>
      </div>
      
      <div class="product-info">
        <div class="product-display">
          <img src="/images/products/lays-classic.jpg" alt="Lay's Classic Chips" class="product-image">
          <div class="product-details">
            <div class="product-name">Lay's Classic Chips</div>
            <div class="product-specs">
              <span class="product-upc">UPC: 028400064552</span> • 
              <span class="product-price">$1.25</span>
            </div>
            <div class="product-notes">
              Check expiration dates before loading
            </div>
          </div>
        </div>
      </div>
      
      <div class="action-buttons">
        <button class="btn btn--primary btn--large btn--block" onclick="startRestock()">
          <svg class="icon icon--sm" aria-hidden="true">
            <use href="#icon-package"></use>
          </svg>
          Start Restocking
        </button>
      </div>
    </div>
    
    <div class="quick-actions">
      <div class="action-row">
        <button class="action-button" onclick="takePhoto()">
          <svg class="icon icon--lg" aria-hidden="true">
            <use href="#icon-camera"></use>
          </svg>
          <span class="action-label">Take Photo</span>
        </button>
        
        <button class="action-button" onclick="reportIssue()">
          <svg class="icon icon--lg" aria-hidden="true">
            <use href="#icon-alert-triangle"></use>
          </svg>
          <span class="action-label">Report Issue</span>
        </button>
        
        <button class="action-button" onclick="skipItem()">
          <svg class="icon icon--lg" aria-hidden="true">
            <use href="#icon-skip-forward"></use>
          </svg>
          <span class="action-label">Skip Item</span>
        </button>
      </div>
    </div>
  </div>
</div>
```

#### Inventory Update Interface

**Stock Count Input**:
```html
<div class="inventory-update">
  <div class="update-header">
    <h3 class="update-title">Update Inventory</h3>
    <p class="update-description">
      Enter the new stock count for <strong>Lay's Classic Chips</strong> in slot A3
    </p>
  </div>
  
  <div class="stock-counter">
    <div class="counter-display">
      <button class="counter-btn counter-btn--minus" onclick="decreaseStock()" aria-label="Decrease stock count">
        <svg class="icon icon--lg" aria-hidden="true">
          <use href="#icon-minus"></use>
        </svg>
      </button>
      
      <div class="counter-input-wrapper">
        <input 
          type="number" 
          class="counter-input" 
          value="10" 
          min="0" 
          max="10"
          id="stockCount"
          aria-label="Stock count"
        >
        <div class="counter-labels">
          <div class="counter-label">New Stock Count</div>
        </div>
      </div>
      
      <button class="counter-btn counter-btn--plus" onclick="increaseStock()" aria-label="Increase stock count">
        <svg class="icon icon--lg" aria-hidden="true">
          <use href="#icon-plus"></use>
        </svg>
      </button>
    </div>
    
    <div class="stock-summary">
      <div class="summary-item">
        <span class="summary-label">Previous:</span>
        <span class="summary-value">2 items</span>
      </div>
      <div class="summary-item summary-item--highlight">
        <span class="summary-label">Added:</span>
        <span class="summary-value">+8 items</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">New Total:</span>
        <span class="summary-value">10 items</span>
      </div>
    </div>
  </div>
  
  <div class="update-options">
    <div class="option-group">
      <div class="checkbox-item">
        <input type="checkbox" id="verify-expiry" class="checkbox" checked>
        <label for="verify-expiry" class="checkbox-label">
          Verified expiration dates
        </label>
      </div>
      
      <div class="checkbox-item">
        <input type="checkbox" id="check-placement" class="checkbox" checked>
        <label for="check-placement" class="checkbox-label">
          Products properly placed
        </label>
      </div>
    </div>
  </div>
  
  <div class="update-actions">
    <button class="btn btn--secondary" onclick="cancelUpdate()">
      Cancel
    </button>
    
    <button class="btn btn--primary btn--large" onclick="confirmUpdate()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-check"></use>
      </svg>
      Confirm Update
    </button>
  </div>
</div>
```

#### Photo Documentation

**Camera Interface**:
```html
<div class="photo-capture">
  <div class="camera-view">
    <video id="cameraPreview" class="camera-preview" autoplay playsinline></video>
    <div class="camera-overlay">
      <div class="overlay-guides">
        <div class="guide-lines"></div>
      </div>
      
      <div class="overlay-info">
        <div class="photo-context">
          <div class="context-location">Office Building A - Slot A3</div>
          <div class="context-action">Restock Documentation</div>
        </div>
      </div>
    </div>
  </div>
  
  <div class="camera-controls">
    <div class="control-row">
      <button class="camera-control" onclick="switchCamera()" aria-label="Switch camera">
        <svg class="icon icon--lg" aria-hidden="true">
          <use href="#icon-refresh-cw"></use>
        </svg>
      </button>
      
      <button class="capture-button" onclick="capturePhoto()" aria-label="Take photo">
        <div class="capture-ring">
          <div class="capture-inner"></div>
        </div>
      </button>
      
      <button class="camera-control" onclick="toggleFlash()" aria-label="Toggle flash">
        <svg class="icon icon--lg" aria-hidden="true">
          <use href="#icon-zap"></use>
        </svg>
      </button>
    </div>
    
    <div class="photo-actions">
      <button class="btn btn--secondary" onclick="cancelPhoto()">
        Cancel
      </button>
    </div>
  </div>
</div>
```

**Photo Review & Annotation**:
```html
<div class="photo-review">
  <div class="photo-display">
    <img src="captured-photo-url" alt="Service photo" class="review-photo" id="reviewPhoto">
    
    <div class="photo-annotations">
      <div class="annotation-point" style="top: 30%; left: 40%;" data-note="Fully stocked">
        <div class="annotation-marker">
          <svg class="icon icon--xs" aria-hidden="true">
            <use href="#icon-info"></use>
          </svg>
        </div>
      </div>
    </div>
  </div>
  
  <div class="photo-details">
    <div class="detail-group">
      <label for="photo-caption" class="form-label">Photo Description</label>
      <input 
        type="text" 
        id="photo-caption" 
        class="input" 
        value="Slot A3 after restocking - 10 items"
        placeholder="Describe what this photo shows..."
      >
    </div>
    
    <div class="photo-metadata">
      <div class="metadata-item">
        <svg class="icon icon--xs" aria-hidden="true">
          <use href="#icon-clock"></use>
        </svg>
        <span class="metadata-value">2:34 PM</span>
      </div>
      
      <div class="metadata-item">
        <svg class="icon icon--xs" aria-hidden="true">
          <use href="#icon-map-pin"></use>
        </svg>
        <span class="metadata-value">GPS: 39.7817,-89.6501</span>
      </div>
    </div>
  </div>
  
  <div class="photo-actions">
    <button class="btn btn--secondary" onclick="retakePhoto()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-camera"></use>
      </svg>
      Retake
    </button>
    
    <button class="btn btn--primary" onclick="savePhoto()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-check"></use>
      </svg>
      Save Photo
    </button>
  </div>
</div>
```

### Phase 4: Service Completion & Documentation (3-8 minutes)

#### Service Summary Review

**Completion Overview**:
```html
<div class="service-summary">
  <header class="summary-header">
    <div class="completion-icon">
      <svg class="icon icon--2xl icon--success" aria-hidden="true">
        <use href="#icon-check-circle"></use>
      </svg>
    </div>
    
    <div class="completion-info">
      <h2 class="completion-title">Service Completed</h2>
      <div class="completion-details">
        <div class="detail-item">
          <strong>Location:</strong> Office Building A
        </div>
        <div class="detail-item">
          <strong>Device:</strong> Snack Machine Alpha
        </div>
        <div class="detail-item">
          <strong>Duration:</strong> 23 minutes
        </div>
      </div>
    </div>
  </header>
  
  <div class="summary-content">
    <div class="tasks-completed">
      <h3 class="section-title">Tasks Completed</h3>
      
      <div class="completion-stats">
        <div class="stat-group">
          <div class="stat-item">
            <div class="stat-value">8</div>
            <div class="stat-label">Items Restocked</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">3</div>
            <div class="stat-label">Photos Taken</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">1</div>
            <div class="stat-label">Maintenance Check</div>
          </div>
        </div>
      </div>
      
      <div class="task-checklist">
        <div class="checklist-item checklist-item--completed">
          <svg class="icon icon--sm icon--success" aria-hidden="true">
            <use href="#icon-check-circle"></use>
          </svg>
          <div class="checklist-content">
            <div class="checklist-title">Inventory Restocked</div>
            <div class="checklist-detail">8 slots updated with new inventory</div>
          </div>
        </div>
        
        <div class="checklist-item checklist-item--completed">
          <svg class="icon icon--sm icon--success" aria-hidden="true">
            <use href="#icon-check-circle"></use>
          </svg>
          <div class="checklist-content">
            <div class="checklist-title">Maintenance Check</div>
            <div class="checklist-detail">Coin mechanism inspected - functioning normally</div>
          </div>
        </div>
        
        <div class="checklist-item checklist-item--completed">
          <svg class="icon icon--sm icon--success" aria-hidden="true">
            <use href="#icon-check-circle"></use>
          </svg>
          <div class="checklist-content">
            <div class="checklist-title">Documentation</div>
            <div class="checklist-detail">3 photos and service notes recorded</div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="service-notes">
      <h3 class="section-title">Service Notes</h3>
      
      <div class="form-group">
        <label for="completion-notes" class="form-label">
          Additional Notes (Optional)
        </label>
        <textarea 
          id="completion-notes" 
          class="textarea" 
          rows="3"
          placeholder="Any additional observations or issues to note..."
        ></textarea>
      </div>
      
      <div class="note-suggestions">
        <div class="suggestion-title">Quick Notes:</div>
        <div class="suggestion-buttons">
          <button class="btn btn--ghost btn--sm" onclick="addQuickNote('All products well-stocked')">
            All products well-stocked
          </button>
          
          <button class="btn btn--ghost btn--sm" onclick="addQuickNote('Machine operating normally')">
            Machine operating normally
          </button>
          
          <button class="btn btn--ghost btn--sm" onclick="addQuickNote('Customer requested product variety')">
            Customer requested more variety
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <div class="summary-actions">
    <button class="btn btn--secondary" onclick="editService()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-edit"></use>
      </svg>
      Make Changes
    </button>
    
    <button class="btn btn--primary btn--large" onclick="finalizeService()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-check"></use>
      </svg>
      Finalize & Continue
    </button>
  </div>
</div>
```

### Phase 5: Sync & Route Continuation (1-2 minutes)

#### Service Finalization & Sync

**Sync Status Interface**:
```html
<div class="sync-status">
  <div class="sync-progress">
    <div class="sync-animation">
      <svg class="icon icon--xl sync-icon" aria-hidden="true">
        <use href="#icon-upload-cloud"></use>
      </svg>
    </div>
    
    <div class="sync-info">
      <h3 class="sync-title">Syncing Service Data</h3>
      <p class="sync-description">
        Uploading photos and updating inventory records...
      </p>
      
      <div class="sync-progress-bar">
        <div class="progress-bar">
          <div class="progress-fill" style="width: 75%"></div>
        </div>
        <div class="progress-text">3 of 4 items uploaded</div>
      </div>
    </div>
  </div>
  
  <div class="sync-details">
    <div class="sync-items">
      <div class="sync-item sync-item--completed">
        <svg class="icon icon--sm icon--success" aria-hidden="true">
          <use href="#icon-check"></use>
        </svg>
        <span class="sync-label">Inventory updates</span>
      </div>
      
      <div class="sync-item sync-item--completed">
        <svg class="icon icon--sm icon--success" aria-hidden="true">
          <use href="#icon-check"></use>
        </svg>
        <span class="sync-label">Service notes</span>
      </div>
      
      <div class="sync-item sync-item--active">
        <div class="spinner spinner--sm"></div>
        <span class="sync-label">Photos (2 of 3)</span>
      </div>
      
      <div class="sync-item sync-item--pending">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-clock"></use>
        </svg>
        <span class="sync-label">GPS location data</span>
      </div>
    </div>
  </div>
</div>
```

**Sync Success & Route Continuation**:
```html
<div class="service-complete">
  <div class="completion-success">
    <svg class="icon icon--2xl icon--success" aria-hidden="true">
      <use href="#icon-check-circle"></use>
    </svg>
    
    <h2 class="success-title">Service Complete!</h2>
    <p class="success-message">
      All data synced successfully. Great work at Office Building A!
    </p>
  </div>
  
  <div class="route-status">
    <div class="route-progress">
      <h3 class="progress-title">Route Progress</h3>
      <div class="progress-stats">
        <div class="stat-completed">3 completed</div>
        <div class="stat-remaining">3 remaining</div>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width: 50%"></div>
      </div>
    </div>
    
    <div class="next-stop">
      <h4 class="next-title">Next Stop</h4>
      <div class="location-preview">
        <div class="location-info">
          <div class="location-name">Warehouse B - Employee Break Room</div>
          <div class="location-distance">
            <svg class="icon icon--xs" aria-hidden="true">
              <use href="#icon-navigation"></use>
            </svg>
            1.8 mi • 6 minutes
          </div>
        </div>
        
        <div class="location-tasks">
          <div class="task-preview">
            <svg class="icon icon--xs" aria-hidden="true">
              <use href="#icon-package"></use>
            </svg>
            Regular restock
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <div class="completion-actions">
    <button class="btn btn--secondary" onclick="viewServiceSummary()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-eye"></use>
      </svg>
      View Summary
    </button>
    
    <button class="btn btn--primary btn--large" onclick="continueToNextStop()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-arrow-right"></use>
      </svg>
      Continue to Next Stop
    </button>
  </div>
</div>
```

## Error Handling & Edge Cases

### Network Connectivity Issues

**Offline Service Continuation**:
```html
<div class="offline-mode">
  <div class="offline-indicator">
    <div class="offline-icon">
      <svg class="icon icon--lg icon--warning" aria-hidden="true">
        <use href="#icon-wifi-off"></use>
      </svg>
    </div>
    
    <div class="offline-info">
      <h3 class="offline-title">Working Offline</h3>
      <p class="offline-message">
        No internet connection. Your work is being saved locally and will sync when connection is restored.
      </p>
    </div>
  </div>
  
  <div class="offline-status">
    <div class="status-items">
      <div class="status-item">
        <svg class="icon icon--sm icon--success" aria-hidden="true">
          <use href="#icon-save"></use>
        </svg>
        <span class="status-text">Data saved locally</span>
      </div>
      
      <div class="status-item">
        <svg class="icon icon--sm icon--info" aria-hidden="true">
          <use href="#icon-upload"></use>
        </svg>
        <span class="status-text">4 items queued for sync</span>
      </div>
    </div>
    
    <button class="btn btn--ghost btn--sm" onclick="retrySync()">
      <svg class="icon icon--xs" aria-hidden="true">
        <use href="#icon-refresh"></use>
      </svg>
      Try Sync Now
    </button>
  </div>
</div>
```

### Equipment/Access Issues

**Problem Reporting Interface**:
```html
<div class="issue-report">
  <div class="report-header">
    <h2 class="report-title">Report Service Issue</h2>
    <p class="report-description">
      Let us know what prevented you from completing service
    </p>
  </div>
  
  <div class="issue-categories">
    <div class="category-group">
      <h3 class="category-title">Access Issues</h3>
      
      <div class="issue-options">
        <button class="issue-option" onclick="selectIssue('locked-building')">
          <svg class="icon icon--md" aria-hidden="true">
            <use href="#icon-lock"></use>
          </svg>
          <div class="option-content">
            <div class="option-title">Building Locked</div>
            <div class="option-description">Cannot access building or room</div>
          </div>
        </button>
        
        <button class="issue-option" onclick="selectIssue('no-contact')">
          <svg class="icon icon--md" aria-hidden="true">
            <use href="#icon-phone-off"></use>
          </svg>
          <div class="option-content">
            <div class="option-title">No Contact Available</div>
            <div class="option-description">Cannot reach site contact person</div>
          </div>
        </button>
      </div>
    </div>
    
    <div class="category-group">
      <h3 class="category-title">Equipment Issues</h3>
      
      <div class="issue-options">
        <button class="issue-option" onclick="selectIssue('machine-malfunction')">
          <svg class="icon icon--md" aria-hidden="true">
            <use href="#icon-alert-triangle"></use>
          </svg>
          <div class="option-content">
            <div class="option-title">Machine Malfunction</div>
            <div class="option-description">Device not responding or damaged</div>
          </div>
        </button>
        
        <button class="issue-option" onclick="selectIssue('inventory-problem')">
          <svg class="icon icon--md" aria-hidden="true">
            <use href="#icon-package-x"></use>
          </svg>
          <div class="option-content">
            <div class="option-title">Inventory Issue</div>
            <div class="option-description">Wrong products or damaged goods</div>
          </div>
        </button>
      </div>
    </div>
  </div>
  
  <div class="issue-details">
    <div class="form-group">
      <label for="issue-description" class="form-label">
        Additional Details
      </label>
      <textarea 
        id="issue-description" 
        class="textarea" 
        rows="3"
        placeholder="Describe the issue in detail..."
      ></textarea>
    </div>
    
    <div class="form-group">
      <div class="checkbox-item">
        <input type="checkbox" id="photo-evidence" class="checkbox">
        <label for="photo-evidence" class="checkbox-label">
          Take photo of the issue for documentation
        </label>
      </div>
    </div>
  </div>
  
  <div class="report-actions">
    <button class="btn btn--secondary" onclick="cancelReport()">
      Cancel
    </button>
    
    <button class="btn btn--primary" onclick="submitIssue()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-send"></use>
      </svg>
      Submit Issue Report
    </button>
  </div>
</div>
```

## Mobile Performance Optimizations

### Touch Interface Enhancements

**Gesture Support**:
- Swipe right on order cards to start service
- Swipe left to skip/postpone orders
- Pull-to-refresh for order updates
- Pinch-to-zoom on device photos
- Long-press for context menus

**Voice Input Integration**:
```html
<div class="voice-input">
  <button class="voice-button" onclick="startVoiceInput()" aria-label="Voice input">
    <svg class="icon icon--lg" aria-hidden="true">
      <use href="#icon-microphone"></use>
    </svg>
  </button>
  
  <div class="voice-feedback">
    <div class="voice-animation"></div>
    <div class="voice-text">Say "complete restock" or tap to cancel</div>
  </div>
</div>
```

### Offline Data Management

**Local Storage Strategy**:
- Service order details cached on device
- Photo storage with compression
- Inventory updates queued for sync
- GPS coordinates saved locally
- User preferences maintained offline

**Sync Conflict Resolution**:
```html
<div class="sync-conflict">
  <div class="conflict-header">
    <svg class="icon icon--lg icon--warning" aria-hidden="true">
      <use href="#icon-alert-triangle"></use>
    </svg>
    <h3 class="conflict-title">Sync Conflict Detected</h3>
  </div>
  
  <div class="conflict-details">
    <p class="conflict-message">
      The inventory for <strong>Slot A3</strong> was updated by another user while you were offline.
    </p>
    
    <div class="conflict-comparison">
      <div class="comparison-item">
        <div class="comparison-label">Your Update</div>
        <div class="comparison-value">Stock: 8 items</div>
      </div>
      
      <div class="comparison-item">
        <div class="comparison-label">Server Update</div>
        <div class="comparison-value">Stock: 6 items</div>
      </div>
    </div>
  </div>
  
  <div class="conflict-actions">
    <button class="btn btn--secondary" onclick="keepServerVersion()">
      Keep Server Version (6 items)
    </button>
    
    <button class="btn btn--primary" onclick="keepMyVersion()">
      Keep My Version (8 items)
    </button>
  </div>
</div>
```

---

**Related Documentation:**
- [User Flows Overview](USER_FLOWS_OVERVIEW.md)
- [Mobile App Workflows](MOBILE_APP_WORKFLOWS.md)
- [Login Flow](LOGIN_FLOW.md)
- [UI Components Overview](../components/UI_COMPONENTS_OVERVIEW.md)

**Implementation Requirements:**
- Progressive Web App (PWA) capabilities
- Offline-first architecture with sync queuing
- Camera API integration for photo capture
- Geolocation API for arrival detection
- Push notification support for order assignments
- Local storage with conflict resolution

**Performance Targets:**
- Initial app load: < 3 seconds
- Screen transitions: < 200ms
- Photo capture: < 1 second to preview
- Sync operations: Background with user feedback
- Offline capability: Full service execution

**Accessibility Features:**
- Large touch targets (44px minimum)
- Voice input for hands-free operation
- High contrast mode support
- Screen reader compatibility
- Haptic feedback for confirmations

**Last Updated:** 2025-08-12  
**Average Service Time:** 15-30 minutes per location  
**Offline Capability:** 100% service execution, queued sync