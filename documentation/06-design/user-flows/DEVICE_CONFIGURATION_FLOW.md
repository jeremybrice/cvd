---
title: Device Configuration Flow
description: Complete user journey for setting up new vending machines and configuring existing devices in the CVD system
feature: device-management
last-updated: 2025-08-12
version: 2.1.0
related-files:
  - USER_FLOWS_OVERVIEW.md
  - ../components/forms.md
  - ../components/UI_COMPONENTS_OVERVIEW.md
dependencies:
  - device-database-schema
  - cabinet-configuration-system
  - product-catalog-integration
status: active
---

# Device Configuration Flow


## Metadata
- **ID**: 06_DESIGN_USER_FLOWS_DEVICE_CONFIGURATION_FLOW
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #data-layer #database #debugging #device-management #integration #interface #logistics #machine-learning #metrics #operations #optimization #performance #planogram #product-placement #reporting #route-management #service-orders #troubleshooting #ui-design #user-experience #vending-machine
- **Intent**: The device configuration flow enables administrators and managers to add new vending machines to the CVD fleet and configure both hardware and operational parameters
- **Audience**: system administrators, managers, end users
- **Related**: USER_FLOWS_OVERVIEW.md, SERVICE_ORDER_EXECUTION.md, forms.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/06-design/user-flows/
- **Category**: User Flows
- **Search Keywords**: **dashboard, 2025-08-12, add, average, cabinet, clone, completion, complexity, complexity:, configuration, context:, context:**, csv/excel, dashboard, dependencies

## Overview

The device configuration flow enables administrators and managers to add new vending machines to the CVD fleet and configure both hardware and operational parameters. This complex workflow handles everything from basic device information to detailed cabinet layouts and service schedules.

## Flow Metadata

- **Flow Name**: Device Configuration & Setup
- **User Roles**: Admin (full access), Manager (limited configuration)
- **Frequency**: Weekly to monthly (new device additions)
- **Complexity**: High (multi-step with validation dependencies)
- **Devices**: Desktop preferred (complex forms), Tablet supported
- **Dependencies**: Product catalog, location database, device types

## Flow Triggers

### Primary Entry Points

1. **Add New Device**: From device management dashboard
2. **Device Import**: Bulk device setup from CSV/file
3. **Clone Existing**: Duplicate configuration from similar device
4. **Quick Setup**: Streamlined flow for standard configurations
5. **Edit Existing**: Modify configuration of active devices

### Context-Aware Scenarios

- **New Location Setup**: First device at a new location
- **Fleet Expansion**: Adding similar devices to existing routes
- **Device Replacement**: Replacing failed or upgraded devices
- **Reconfiguration**: Changing product mix or layout
- **Maintenance Mode**: Temporary configuration changes

## User Journey Breakdown

### Phase 1: Entry & Device Type Selection (30 seconds - 2 minutes)

#### Entry State: Device Management Dashboard

**Navigation Path:**
```
Main Navigation > Devices > Add New Device
```

**Dashboard Context:**
```html
<div class="device-dashboard">
  <div class="dashboard-header">
    <h1 class="dashboard-title">Device Management</h1>
    <div class="dashboard-stats">
      <div class="stat-card">
        <div class="stat-value">147</div>
        <div class="stat-label">Active Devices</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">12</div>
        <div class="stat-label">Offline</div>
        <div class="stat-change stat-change--warning">Needs attention</div>
      </div>
    </div>
  </div>
  
  <div class="dashboard-actions">
    <button class="btn btn--primary" onclick="startDeviceFlow()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-plus"></use>
      </svg>
      Add New Device
    </button>
    
    <div class="action-group">
      <button class="btn btn--secondary" onclick="importDevices()">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-upload"></use>
        </svg>
        Import Devices
      </button>
      
      <button class="btn btn--secondary" onclick="exportDevices()">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-download"></use>
        </svg>
        Export Configuration
      </button>
    </div>
  </div>
</div>
```

#### Screen State: Device Type Selection

**Purpose**: Determine device category to load appropriate configuration templates

```html
<div class="device-setup">
  <div class="setup-progress">
    <div class="progress-bar">
      <div class="progress-step progress-step--active">
        <div class="step-number">1</div>
        <div class="step-label">Device Type</div>
      </div>
      <div class="progress-step">
        <div class="step-number">2</div>
        <div class="step-label">Basic Info</div>
      </div>
      <div class="progress-step">
        <div class="step-number">3</div>
        <div class="step-label">Configuration</div>
      </div>
      <div class="progress-step">
        <div class="step-number">4</div>
        <div class="step-label">Review</div>
      </div>
    </div>
  </div>
  
  <div class="setup-content">
    <header class="setup-header">
      <h2 class="setup-title">Choose Device Type</h2>
      <p class="setup-description">
        Select the type of vending machine you're adding to your fleet
      </p>
    </header>
    
    <div class="device-type-grid">
      <div class="device-type-card" data-type="snack">
        <div class="device-type-icon">
          <svg class="icon icon--2xl" aria-hidden="true">
            <use href="#icon-snack-machine"></use>
          </svg>
        </div>
        <div class="device-type-info">
          <h3 class="device-type-title">Snack Machine</h3>
          <p class="device-type-description">
            Traditional snack vending with chips, candy, crackers, and packaged foods
          </p>
          <div class="device-type-specs">
            <div class="spec-item">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-grid"></use>
              </svg>
              Up to 60 slots
            </div>
            <div class="spec-item">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-dollar"></use>
              </svg>
              $0.50 - $3.00 pricing
            </div>
          </div>
        </div>
        <div class="device-type-action">
          <button class="btn btn--primary" onclick="selectDeviceType('snack')">
            Select Snack Machine
          </button>
        </div>
      </div>
      
      <div class="device-type-card" data-type="beverage">
        <div class="device-type-icon">
          <svg class="icon icon--2xl" aria-hidden="true">
            <use href="#icon-beverage-machine"></use>
          </svg>
        </div>
        <div class="device-type-info">
          <h3 class="device-type-title">Beverage Machine</h3>
          <p class="device-type-description">
            Cold drinks including sodas, water, juices, and energy drinks
          </p>
          <div class="device-type-specs">
            <div class="spec-item">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-grid"></use>
              </svg>
              Up to 48 slots
            </div>
            <div class="spec-item">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-thermometer"></use>
              </svg>
              Refrigerated
            </div>
          </div>
        </div>
        <div class="device-type-action">
          <button class="btn btn--primary" onclick="selectDeviceType('beverage')">
            Select Beverage Machine
          </button>
        </div>
      </div>
      
      <div class="device-type-card" data-type="combo">
        <div class="device-type-icon">
          <svg class="icon icon--2xl" aria-hidden="true">
            <use href="#icon-combo-machine"></use>
          </svg>
        </div>
        <div class="device-type-info">
          <h3 class="device-type-title">Combo Machine</h3>
          <p class="device-type-description">
            Combined snack and beverage vending in a single unit
          </p>
          <div class="device-type-specs">
            <div class="spec-item">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-layers"></use>
              </svg>
              Dual cabinet
            </div>
            <div class="spec-item">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-zap"></use>
              </svg>
              Higher capacity
            </div>
          </div>
        </div>
        <div class="device-type-action">
          <button class="btn btn--primary" onclick="selectDeviceType('combo')">
            Select Combo Machine
          </button>
        </div>
      </div>
      
      <div class="device-type-card device-type-card--specialized" data-type="coffee">
        <div class="device-type-icon">
          <svg class="icon icon--2xl" aria-hidden="true">
            <use href="#icon-coffee-machine"></use>
          </svg>
        </div>
        <div class="device-type-info">
          <h3 class="device-type-title">Coffee Machine</h3>
          <p class="device-type-description">
            Hot beverages with bean-to-cup or pod systems
          </p>
          <div class="device-type-specs">
            <div class="spec-item">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-coffee"></use>
              </svg>
              Multiple drinks
            </div>
            <div class="spec-item">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-settings"></use>
              </svg>
              Complex setup
            </div>
          </div>
        </div>
        <div class="device-type-action">
          <button class="btn btn--primary" onclick="selectDeviceType('coffee')">
            Select Coffee Machine
          </button>
        </div>
      </div>
    </div>
    
    <div class="setup-actions">
      <button class="btn btn--secondary" onclick="cancelSetup()">
        Cancel Setup
      </button>
      <button class="btn btn--ghost" onclick="importFromTemplate()">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-template"></use>
        </svg>
        Use Template
      </button>
    </div>
  </div>
</div>
```

### Phase 2: Basic Device Information (2-5 minutes)

#### Screen State: Essential Device Details

**Purpose**: Capture core identifying information and basic operational parameters

```html
<div class="setup-content">
  <header class="setup-header">
    <h2 class="setup-title">Device Information</h2>
    <p class="setup-description">
      Enter basic details for your <strong>snack machine</strong>
    </p>
  </header>
  
  <form class="device-form" id="deviceBasicInfo">
    <div class="form-section">
      <header class="form-section-header">
        <h3 class="form-section-title">
          <svg class="icon icon--md" aria-hidden="true">
            <use href="#icon-info"></use>
          </svg>
          Identification
        </h3>
      </header>
      
      <div class="form-section-content">
        <div class="form-row">
          <div class="form-col">
            <div class="form-group">
              <label for="device-name" class="form-label form-label--required">
                Device Name
              </label>
              <input 
                type="text" 
                id="device-name" 
                name="deviceName"
                class="input" 
                required
                placeholder="e.g., Snack Machine Alpha"
                aria-describedby="device-name-hint"
              >
              <div id="device-name-hint" class="form-hint">
                Choose a memorable name for easy identification
              </div>
            </div>
          </div>
          
          <div class="form-col">
            <div class="form-group">
              <label for="device-serial" class="form-label form-label--required">
                Serial Number
              </label>
              <input 
                type="text" 
                id="device-serial" 
                name="serialNumber"
                class="input" 
                required
                placeholder="e.g., SM2025001234"
                pattern="[A-Z0-9]{6,20}"
                aria-describedby="device-serial-hint"
              >
              <div id="device-serial-hint" class="form-hint">
                Manufacturer's serial number (6-20 characters)
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-col">
            <div class="form-group">
              <label for="device-manufacturer" class="form-label">
                Manufacturer
              </label>
              <select id="device-manufacturer" name="manufacturer" class="select">
                <option value="">Select manufacturer...</option>
                <option value="ams">AMS (Automated Merchandising Systems)</option>
                <option value="crane">Crane Merchandising Systems</option>
                <option value="dixie-narco">Dixie Narco</option>
                <option value="royal">Royal Vendors</option>
                <option value="seaga">Seaga Manufacturing</option>
                <option value="vendo">Vendo</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          
          <div class="form-col">
            <div class="form-group">
              <label for="device-model" class="form-label">
                Model Number
              </label>
              <input 
                type="text" 
                id="device-model" 
                name="modelNumber"
                class="input" 
                placeholder="e.g., VCF Series"
              >
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="form-section">
      <header class="form-section-header">
        <h3 class="form-section-title">
          <svg class="icon icon--md" aria-hidden="true">
            <use href="#icon-map-pin"></use>
          </svg>
          Location Details
        </h3>
      </header>
      
      <div class="form-section-content">
        <div class="form-group">
          <label for="device-location" class="form-label form-label--required">
            Location Name
          </label>
          <div class="input-group">
            <input 
              type="text" 
              id="device-location" 
              name="locationName"
              class="input" 
              required
              placeholder="e.g., Office Building A - 2nd Floor Break Room"
              aria-describedby="device-location-hint"
              list="location-suggestions"
            >
            <datalist id="location-suggestions">
              <option value="Office Building A - 1st Floor Lobby">
              <option value="Office Building A - 2nd Floor Break Room">
              <option value="Warehouse B - Employee Area">
              <option value="Manufacturing Floor - East Wing">
            </datalist>
          </div>
          <div id="device-location-hint" class="form-hint">
            Specific location description for service technicians
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-col form-col--2">
            <div class="form-group">
              <label for="device-address" class="form-label">
                Street Address
              </label>
              <input 
                type="text" 
                id="device-address" 
                name="address"
                class="input" 
                placeholder="123 Business Park Drive"
                autocomplete="address-line1"
              >
            </div>
          </div>
          
          <div class="form-col">
            <div class="form-group">
              <label for="device-city" class="form-label">
                City
              </label>
              <input 
                type="text" 
                id="device-city" 
                name="city"
                class="input" 
                placeholder="Springfield"
                autocomplete="address-level2"
              >
            </div>
          </div>
          
          <div class="form-col">
            <div class="form-group">
              <label for="device-state" class="form-label">
                State
              </label>
              <select id="device-state" name="state" class="select" autocomplete="address-level1">
                <option value="">Select state...</option>
                <option value="AL">Alabama</option>
                <option value="AK">Alaska</option>
                <!-- All US states -->
              </select>
            </div>
          </div>
          
          <div class="form-col">
            <div class="form-group">
              <label for="device-zip" class="form-label">
                ZIP Code
              </label>
              <input 
                type="text" 
                id="device-zip" 
                name="zipCode"
                class="input" 
                placeholder="12345"
                pattern="[0-9]{5}(-[0-9]{4})?"
                autocomplete="postal-code"
              >
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <div class="checkbox-item">
            <input 
              type="checkbox" 
              id="use-gps" 
              name="useGPS"
              class="checkbox"
            >
            <label for="use-gps" class="checkbox-label">
              <div class="checkbox-content">
                <div class="checkbox-title">Use GPS coordinates</div>
                <div class="checkbox-description">
                  Automatically detect location for routing optimization
                </div>
              </div>
            </label>
          </div>
        </div>
      </div>
    </div>
    
    <div class="form-section">
      <header class="form-section-header">
        <h3 class="form-section-title">
          <svg class="icon icon--md" aria-hidden="true">
            <use href="#icon-settings"></use>
          </svg>
          Operational Settings
        </h3>
      </header>
      
      <div class="form-section-content">
        <div class="form-row">
          <div class="form-col">
            <div class="form-group">
              <label for="service-route" class="form-label">
                Service Route
              </label>
              <select id="service-route" name="serviceRoute" class="select">
                <option value="">Assign to route...</option>
                <option value="route-1">Route 1 - Downtown</option>
                <option value="route-2">Route 2 - Industrial</option>
                <option value="route-3">Route 3 - Suburban</option>
                <option value="new">Create new route</option>
              </select>
            </div>
          </div>
          
          <div class="form-col">
            <div class="form-group">
              <label for="service-frequency" class="form-label">
                Service Frequency
              </label>
              <select id="service-frequency" name="serviceFrequency" class="select">
                <option value="weekly">Weekly</option>
                <option value="biweekly">Bi-weekly</option>
                <option value="monthly">Monthly</option>
                <option value="as-needed">As needed</option>
              </select>
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <div class="toggle-item">
            <input 
              type="checkbox" 
              id="device-active" 
              name="isActive"
              class="toggle"
              checked
            >
            <label for="device-active" class="toggle-label">
              <span class="toggle-content">
                <span class="toggle-title">Device is active</span>
                <span class="toggle-description">Enable for immediate operation</span>
              </span>
              <span class="toggle-switch" aria-hidden="true">
                <span class="toggle-handle"></span>
              </span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </form>
  
  <div class="setup-actions">
    <button class="btn btn--secondary" onclick="goBack()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-arrow-left"></use>
      </svg>
      Back
    </button>
    
    <button class="btn btn--primary" onclick="continueToConfiguration()">
      Continue to Configuration
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-arrow-right"></use>
      </svg>
    </button>
  </div>
</div>
```

### Phase 3: Cabinet Configuration (5-15 minutes)

#### Screen State: Cabinet Layout Setup

**Purpose**: Configure physical cabinet layout, product slots, and pricing

```html
<div class="setup-content setup-content--wide">
  <header class="setup-header">
    <h2 class="setup-title">Cabinet Configuration</h2>
    <p class="setup-description">
      Set up the physical layout and product assignments for your snack machine
    </p>
  </header>
  
  <div class="cabinet-config">
    <div class="cabinet-sidebar">
      <div class="cabinet-info">
        <h3 class="cabinet-info-title">Machine Details</h3>
        <div class="cabinet-detail">
          <strong>Type:</strong> Snack Machine
        </div>
        <div class="cabinet-detail">
          <strong>Capacity:</strong> 60 slots
        </div>
        <div class="cabinet-detail">
          <strong>Configured:</strong> <span id="configured-slots">0</span>/60 slots
        </div>
      </div>
      
      <div class="cabinet-actions">
        <button class="btn btn--secondary btn--sm" onclick="autoFillSlots()">
          <svg class="icon icon--xs" aria-hidden="true">
            <use href="#icon-magic"></use>
          </svg>
          Auto-fill Popular Items
        </button>
        
        <button class="btn btn--secondary btn--sm" onclick="clearAllSlots()">
          <svg class="icon icon--xs" aria-hidden="true">
            <use href="#icon-trash"></use>
          </svg>
          Clear All
        </button>
        
        <button class="btn btn--secondary btn--sm" onclick="loadTemplate()">
          <svg class="icon icon--xs" aria-hidden="true">
            <use href="#icon-template"></use>
          </svg>
          Load Template
        </button>
      </div>
      
      <div class="product-catalog">
        <h4 class="catalog-title">Product Catalog</h4>
        <div class="catalog-search">
          <input 
            type="text" 
            class="input input--sm" 
            placeholder="Search products..."
            onkeyup="filterProducts(this.value)"
          >
        </div>
        
        <div class="catalog-categories">
          <button class="catalog-filter catalog-filter--active" data-category="all">
            All Products
          </button>
          <button class="catalog-filter" data-category="chips">
            Chips
          </button>
          <button class="catalog-filter" data-category="candy">
            Candy
          </button>
          <button class="catalog-filter" data-category="crackers">
            Crackers
          </button>
          <button class="catalog-filter" data-category="nuts">
            Nuts & Seeds
          </button>
        </div>
        
        <div class="catalog-products" id="productCatalog">
          <div class="product-item" draggable="true" data-product-id="1">
            <div class="product-image">
              <img src="/images/products/lays-classic.jpg" alt="Lay's Classic">
            </div>
            <div class="product-info">
              <div class="product-name">Lay's Classic</div>
              <div class="product-price">$1.25</div>
              <div class="product-category">Chips</div>
            </div>
          </div>
          
          <div class="product-item" draggable="true" data-product-id="2">
            <div class="product-image">
              <img src="/images/products/snickers.jpg" alt="Snickers">
            </div>
            <div class="product-info">
              <div class="product-name">Snickers</div>
              <div class="product-price">$1.50</div>
              <div class="product-category">Candy</div>
            </div>
          </div>
          
          <!-- More products... -->
        </div>
      </div>
    </div>
    
    <div class="cabinet-layout">
      <div class="cabinet-header">
        <h3 class="cabinet-title">Cabinet Layout</h3>
        <div class="cabinet-tools">
          <div class="view-toggle">
            <button class="view-toggle-btn view-toggle-btn--active" data-view="visual">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-grid"></use>
              </svg>
              Visual
            </button>
            <button class="view-toggle-btn" data-view="table">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-list"></use>
              </svg>
              Table
            </button>
          </div>
        </div>
      </div>
      
      <div class="cabinet-grid" id="cabinetGrid">
        <!-- Row A -->
        <div class="cabinet-row">
          <div class="row-label">A</div>
          <div class="slot-group">
            <div class="cabinet-slot" data-slot="A1" onclick="configureSlot('A1')">
              <div class="slot-number">A1</div>
              <div class="slot-content slot-content--empty">
                <svg class="icon icon--lg slot-empty-icon" aria-hidden="true">
                  <use href="#icon-plus"></use>
                </svg>
                <div class="slot-empty-text">Add Product</div>
              </div>
            </div>
            
            <div class="cabinet-slot slot--configured" data-slot="A2">
              <div class="slot-number">A2</div>
              <div class="slot-content">
                <div class="slot-product">
                  <img src="/images/products/lays-classic-thumb.jpg" alt="Lay's Classic" class="slot-product-image">
                  <div class="slot-product-info">
                    <div class="slot-product-name">Lay's Classic</div>
                    <div class="slot-product-price">$1.25</div>
                    <div class="slot-product-stock">
                      <span class="stock-current">8</span>/<span class="stock-capacity">10</span>
                    </div>
                  </div>
                </div>
                <div class="slot-actions">
                  <button class="slot-action" onclick="editSlot('A2')" aria-label="Edit A2">
                    <svg class="icon icon--xs" aria-hidden="true">
                      <use href="#icon-edit"></use>
                    </svg>
                  </button>
                  <button class="slot-action" onclick="clearSlot('A2')" aria-label="Clear A2">
                    <svg class="icon icon--xs" aria-hidden="true">
                      <use href="#icon-x"></use>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Continue for slots A3-A10 -->
          </div>
        </div>
        
        <!-- Rows B-F continue similarly -->
      </div>
    </div>
  </div>
</div>
```

#### Slot Configuration Modal

**Purpose**: Configure individual slot details including products, pricing, and capacity

```html
<div class="modal modal--large" id="slotConfigModal">
  <div class="modal-backdrop" onclick="closeModal()"></div>
  <div class="modal-content">
    <div class="modal-header">
      <h3 class="modal-title">Configure Slot <span id="slotNumber">A1</span></h3>
      <button class="modal-close" onclick="closeModal()">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-x"></use>
        </svg>
      </button>
    </div>
    
    <div class="modal-body">
      <form class="slot-config-form">
        <div class="form-section">
          <header class="form-section-header">
            <h4 class="form-section-title">Product Assignment</h4>
          </header>
          
          <div class="form-section-content">
            <div class="form-group">
              <label for="slot-product" class="form-label form-label--required">
                Product
              </label>
              <div class="product-selector">
                <input 
                  type="text" 
                  id="slot-product" 
                  class="input" 
                  placeholder="Search and select product..."
                  autocomplete="off"
                  onkeyup="searchProducts(this.value)"
                >
                <div class="product-dropdown" id="productDropdown">
                  <!-- Product search results -->
                </div>
              </div>
            </div>
            
            <div class="selected-product" id="selectedProduct" style="display: none;">
              <div class="selected-product-display">
                <img src="" alt="" class="selected-product-image">
                <div class="selected-product-info">
                  <div class="selected-product-name"></div>
                  <div class="selected-product-details">
                    <span class="product-category"></span> • 
                    <span class="product-upc"></span>
                  </div>
                </div>
                <button type="button" class="btn btn--ghost btn--sm" onclick="clearProduct()">
                  <svg class="icon icon--xs" aria-hidden="true">
                    <use href="#icon-x"></use>
                  </svg>
                  Change
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-section">
          <header class="form-section-header">
            <h4 class="form-section-title">Pricing & Inventory</h4>
          </header>
          
          <div class="form-section-content">
            <div class="form-row">
              <div class="form-col">
                <div class="form-group">
                  <label for="slot-price" class="form-label form-label--required">
                    Sale Price
                  </label>
                  <div class="input-group">
                    <div class="input-prefix">$</div>
                    <input 
                      type="number" 
                      id="slot-price" 
                      name="price"
                      class="input" 
                      min="0.25"
                      max="10.00"
                      step="0.25"
                      placeholder="1.25"
                      required
                    >
                  </div>
                </div>
              </div>
              
              <div class="form-col">
                <div class="form-group">
                  <label for="slot-capacity" class="form-label form-label--required">
                    Slot Capacity
                  </label>
                  <input 
                    type="number" 
                    id="slot-capacity" 
                    name="capacity"
                    class="input" 
                    min="1"
                    max="20"
                    value="10"
                    required
                  >
                </div>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-col">
                <div class="form-group">
                  <label for="par-level" class="form-label">
                    Par Level (Restock Trigger)
                  </label>
                  <input 
                    type="number" 
                    id="par-level" 
                    name="parLevel"
                    class="input" 
                    min="0"
                    max="10"
                    value="3"
                    aria-describedby="par-level-hint"
                  >
                  <div id="par-level-hint" class="form-hint">
                    Create service order when inventory drops to this level
                  </div>
                </div>
              </div>
              
              <div class="form-col">
                <div class="form-group">
                  <label for="initial-stock" class="form-label">
                    Initial Stock
                  </label>
                  <input 
                    type="number" 
                    id="initial-stock" 
                    name="initialStock"
                    class="input" 
                    min="0"
                    max="20"
                    value="10"
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-section">
          <header class="form-section-header">
            <h4 class="form-section-title">Advanced Settings</h4>
          </header>
          
          <div class="form-section-content">
            <div class="form-group">
              <div class="toggle-item">
                <input 
                  type="checkbox" 
                  id="slot-enabled" 
                  name="enabled"
                  class="toggle"
                  checked
                >
                <label for="slot-enabled" class="toggle-label">
                  <span class="toggle-content">
                    <span class="toggle-title">Slot enabled</span>
                    <span class="toggle-description">Allow sales from this slot</span>
                  </span>
                  <span class="toggle-switch" aria-hidden="true">
                    <span class="toggle-handle"></span>
                  </span>
                </label>
              </div>
            </div>
            
            <div class="form-group">
              <div class="toggle-item">
                <input 
                  type="checkbox" 
                  id="track-expiry" 
                  name="trackExpiry"
                  class="toggle"
                >
                <label for="track-expiry" class="toggle-label">
                  <span class="toggle-content">
                    <span class="toggle-title">Track expiration dates</span>
                    <span class="toggle-description">Monitor product freshness</span>
                  </span>
                  <span class="toggle-switch" aria-hidden="true">
                    <span class="toggle-handle"></span>
                  </span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
    
    <div class="modal-footer">
      <button type="button" class="btn btn--secondary" onclick="closeModal()">
        Cancel
      </button>
      <button type="button" class="btn btn--primary" onclick="saveSlotConfiguration()">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-check"></use>
        </svg>
        Save Slot Configuration
      </button>
    </div>
  </div>
</div>
```

### Phase 4: Review & Validation (2-5 minutes)

#### Screen State: Configuration Summary

**Purpose**: Final review before device activation with validation checks

```html
<div class="setup-content">
  <header class="setup-header">
    <h2 class="setup-title">Review Configuration</h2>
    <p class="setup-description">
      Review your device setup before activating
    </p>
  </header>
  
  <div class="config-review">
    <div class="review-summary">
      <div class="summary-card">
        <div class="summary-header">
          <h3 class="summary-title">
            <svg class="icon icon--md" aria-hidden="true">
              <use href="#icon-server"></use>
            </svg>
            Snack Machine Alpha
          </h3>
          <div class="summary-status">
            <span class="status-badge status-badge--warning">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-clock"></use>
              </svg>
              Pending Activation
            </span>
          </div>
        </div>
        
        <div class="summary-details">
          <div class="detail-grid">
            <div class="detail-item">
              <div class="detail-label">Serial Number</div>
              <div class="detail-value">SM2025001234</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Location</div>
              <div class="detail-value">Office Building A - 2nd Floor Break Room</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Service Route</div>
              <div class="detail-value">Route 1 - Downtown</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Service Frequency</div>
              <div class="detail-value">Weekly</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="validation-checks">
      <h3 class="validation-title">Configuration Validation</h3>
      
      <div class="validation-list">
        <div class="validation-item validation-item--success">
          <div class="validation-icon">
            <svg class="icon icon--sm" aria-hidden="true">
              <use href="#icon-check-circle"></use>
            </svg>
          </div>
          <div class="validation-content">
            <div class="validation-title">Device Information Complete</div>
            <div class="validation-description">All required device details provided</div>
          </div>
        </div>
        
        <div class="validation-item validation-item--success">
          <div class="validation-icon">
            <svg class="icon icon--sm" aria-hidden="true">
              <use href="#icon-check-circle"></use>
            </svg>
          </div>
          <div class="validation-content">
            <div class="validation-title">Location Verified</div>
            <div class="validation-description">GPS coordinates confirmed</div>
          </div>
        </div>
        
        <div class="validation-item validation-item--warning">
          <div class="validation-icon">
            <svg class="icon icon--sm" aria-hidden="true">
              <use href="#icon-exclamation-triangle"></use>
            </svg>
          </div>
          <div class="validation-content">
            <div class="validation-title">Slots Partially Configured</div>
            <div class="validation-description">
              45 of 60 slots configured. <a href="#cabinet-config">Configure remaining slots</a>
            </div>
          </div>
        </div>
        
        <div class="validation-item validation-item--error">
          <div class="validation-icon">
            <svg class="icon icon--sm" aria-hidden="true">
              <use href="#icon-x-circle"></use>
            </svg>
          </div>
          <div class="validation-content">
            <div class="validation-title">Network Connection Required</div>
            <div class="validation-description">
              Device must be online for activation. <a href="#network-setup">Configure network</a>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="configuration-summary">
      <h3 class="summary-section-title">Product Configuration</h3>
      
      <div class="product-summary-stats">
        <div class="summary-stat">
          <div class="stat-value">45</div>
          <div class="stat-label">Configured Slots</div>
        </div>
        <div class="summary-stat">
          <div class="stat-value">23</div>
          <div class="stat-label">Unique Products</div>
        </div>
        <div class="summary-stat">
          <div class="stat-value">$1.75</div>
          <div class="stat-label">Average Price</div>
        </div>
        <div class="summary-stat">
          <div class="stat-value">$1,247</div>
          <div class="stat-label">Projected Revenue</div>
        </div>
      </div>
      
      <div class="product-breakdown">
        <h4 class="breakdown-title">Product Category Breakdown</h4>
        <div class="category-chart">
          <div class="category-item">
            <div class="category-bar">
              <div class="category-fill" style="width: 40%"></div>
            </div>
            <div class="category-info">
              <span class="category-name">Chips & Snacks</span>
              <span class="category-count">18 slots</span>
            </div>
          </div>
          
          <div class="category-item">
            <div class="category-bar">
              <div class="category-fill" style="width: 30%"></div>
            </div>
            <div class="category-info">
              <span class="category-name">Candy & Chocolate</span>
              <span class="category-count">14 slots</span>
            </div>
          </div>
          
          <div class="category-item">
            <div class="category-bar">
              <div class="category-fill" style="width: 20%"></div>
            </div>
            <div class="category-info">
              <span class="category-name">Crackers & Nuts</span>
              <span class="category-count">9 slots</span>
            </div>
          </div>
          
          <div class="category-item">
            <div class="category-bar">
              <div class="category-fill" style="width: 10%"></div>
            </div>
            <div class="category-info">
              <span class="category-name">Healthy Options</span>
              <span class="category-count">4 slots</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <div class="setup-actions">
    <button class="btn btn--secondary" onclick="goBack()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-arrow-left"></use>
      </svg>
      Back to Configuration
    </button>
    
    <div class="action-group">
      <button class="btn btn--ghost" onclick="saveAsDraft()">
        Save as Draft
      </button>
      
      <button class="btn btn--primary btn--large" onclick="activateDevice()" disabled>
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-power"></use>
        </svg>
        Activate Device
      </button>
    </div>
  </div>
</div>
```

### Phase 5: Activation & Completion (1-3 minutes)

#### Final State: Device Activation Success

```html
<div class="setup-success">
  <div class="success-animation">
    <svg class="icon icon--4xl success-icon" aria-hidden="true">
      <use href="#icon-check-circle"></use>
    </svg>
  </div>
  
  <div class="success-content">
    <h2 class="success-title">Device Activated Successfully!</h2>
    <p class="success-message">
      <strong>Snack Machine Alpha</strong> has been added to your fleet and is ready for operation.
    </p>
    
    <div class="success-details">
      <div class="detail-item">
        <strong>Device ID:</strong> DEV-001234
      </div>
      <div class="detail-item">
        <strong>Status:</strong> <span class="status-badge status-badge--success">Online</span>
      </div>
      <div class="detail-item">
        <strong>First Service:</strong> Scheduled for tomorrow
      </div>
    </div>
  </div>
  
  <div class="success-actions">
    <button class="btn btn--primary" onclick="viewDevice()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-eye"></use>
      </svg>
      View Device Details
    </button>
    
    <div class="secondary-actions">
      <button class="btn btn--secondary" onclick="addAnotherDevice()">
        Add Another Device
      </button>
      
      <button class="btn btn--ghost" onclick="returnToDashboard()">
        Return to Dashboard
      </button>
    </div>
  </div>
</div>
```

## Error Handling & Recovery

### Validation Errors

**Form Validation Issues**:
```html
<div class="validation-error" role="alert">
  <div class="error-icon">
    <svg class="icon icon--md icon--danger" aria-hidden="true">
      <use href="#icon-exclamation-triangle"></use>
    </svg>
  </div>
  <div class="error-content">
    <h3 class="error-title">Configuration Issues Found</h3>
    <ul class="error-list">
      <li>Serial number is already in use by another device</li>
      <li>Location requires GPS coordinates for routing</li>
      <li>Minimum 30 slots must be configured for activation</li>
    </ul>
    <div class="error-actions">
      <button class="btn btn--primary" onclick="fixIssues()">
        Fix Issues
      </button>
      <button class="btn btn--secondary" onclick="saveAsDraft()">
        Save as Draft
      </button>
    </div>
  </div>
</div>
```

### Network/System Errors

**Connection Issues During Setup**:
```html
<div class="setup-error">
  <div class="error-icon">
    <svg class="icon icon--xl icon--warning" aria-hidden="true">
      <use href="#icon-wifi-off"></use>
    </svg>
  </div>
  <h3 class="error-title">Connection Lost</h3>
  <p class="error-message">
    Your configuration has been saved locally. Please check your internet connection and retry activation.
  </p>
  <div class="error-actions">
    <button class="btn btn--primary" onclick="retryActivation()">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-refresh"></use>
      </svg>
      Retry Activation
    </button>
    <button class="btn btn--secondary" onclick="continueOffline()">
      Continue Offline
    </button>
  </div>
</div>
```

## Alternative Flow Paths

### Bulk Device Import

**CSV/Excel Import Flow**:
1. Template download
2. File validation
3. Mapping verification
4. Bulk processing with progress
5. Error reporting and correction
6. Batch activation

### Device Cloning

**Clone from Existing Device**:
1. Source device selection
2. Clone scope definition (full/partial)
3. Customization of cloned settings
4. Location and naming updates
5. Validation and activation

### Quick Setup Mode

**Streamlined Flow for Standard Devices**:
1. Device type selection
2. Essential information only
3. Template-based configuration
4. One-click activation
5. Post-setup customization option

---

**Related Documentation:**
- [User Flows Overview](USER_FLOWS_OVERVIEW.md)
- [Form Components](../components/forms.md)
- [Service Order Execution](SERVICE_ORDER_EXECUTION.md)

**Implementation Requirements:**
- Progressive form saving (prevent data loss)
- Comprehensive validation with clear recovery paths
- Drag-and-drop product assignment
- Real-time configuration preview
- Offline capability for partial configuration
- Accessibility compliance for complex forms

**Performance Targets:**
- Initial load: < 2 seconds
- Form interactions: < 100ms response
- Configuration save: < 1 second
- Validation checks: < 500ms

**Last Updated:** 2025-08-12  
**Flow Complexity:** High (15+ screens, 60+ interactions)  
**Average Completion Time:** 15-30 minutes