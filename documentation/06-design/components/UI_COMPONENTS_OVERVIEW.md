---
title: UI Components Overview
description: Complete catalog of UI components used throughout the CVD application
feature: design-system
last-updated: 2025-08-12
version: 2.1.0
related-files:
  - ../DESIGN_SYSTEM.md
  - ../patterns/README.md
  - /css/design-system.css
dependencies:
  - design-system-css-tokens
  - svg-icon-system
status: active
---

# CVD UI Components Catalog


## Metadata
- **ID**: 06_DESIGN_COMPONENTS_UI_COMPONENTS_OVERVIEW
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #debugging #device-management #driver-app #integration #interface #logistics #machine-learning #mobile #operations #optimization #performance #pwa #route-management #service-orders #troubleshooting #ui-design #user-experience #vending-machine
- **Intent**: description: Complete catalog of UI components used throughout the CVD application
feature: design-system
last-updated: 2025-08-12
version: 2
- **Audience**: end users
- **Related**: USER_FLOWS_OVERVIEW.md, README.md, DESIGN_SYSTEM.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/06-design/components/
- **Category**: Components
- **Search Keywords**: ###, ####, (0-767px), (1024px+), (768-1023px), 2025-08-12, accessibility, alert, base, border:, breadcrumb, button, buttons, cabinet, card

## Overview

This document provides a comprehensive catalog of all UI components used throughout the CVD application, including specifications, variants, states, and usage guidelines. Each component is built using our systematic design tokens for consistency and maintainability.

## Table of Contents

1. [Form Elements](#form-elements)
2. [Navigation Components](#navigation-components)
3. [Data Display Components](#data-display-components)
4. [Feedback Components](#feedback-components)
5. [Layout Components](#layout-components)
6. [Mobile-Specific Components](#mobile-specific-components)

## Form Elements

### Buttons

Primary interaction elements across all CVD interfaces.

#### Base Button Specifications

```css
/* Base Button Component */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--btn-padding-y) var(--btn-padding-x);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  font-weight: var(--btn-font-weight);
  line-height: var(--leading-normal);
  text-decoration: none;
  text-align: center;
  white-space: nowrap;
  cursor: pointer;
  user-select: none;
  border: var(--border-thin) solid transparent;
  border-radius: var(--btn-radius);
  transition: all var(--duration-fast) var(--ease-out);
  min-height: var(--touch-target-min);
  position: relative;
}
```

#### Button Variants

**Primary Button**
- Purpose: Main actions, form submissions
- Background: `var(--color-primary-500)`
- Text: `var(--color-neutral-0)`
- Hover: Lift effect with `var(--color-primary-600)`

```html
<button class="btn btn--primary">
  <svg class="icon icon--sm" aria-hidden="true">
    <use href="#icon-plus"></use>
  </svg>
  Add Device
</button>
```

**Secondary Button**
- Purpose: Alternative actions, cancellation
- Background: `var(--color-neutral-0)`
- Border: `var(--color-neutral-300)`
- Text: `var(--color-neutral-700)`

```html
<button class="btn btn--secondary">
  Cancel
</button>
```

**Success Button**
- Purpose: Positive confirmations, completion actions
- Background: `var(--color-success)`
- Hover: Darker green with lift effect

```html
<button class="btn btn--success">
  <svg class="icon icon--sm" aria-hidden="true">
    <use href="#icon-check"></use>
  </svg>
  Complete Order
</button>
```

**Danger Button**
- Purpose: Destructive actions, deletions
- Background: `var(--color-danger)`
- Requires confirmation dialog for critical actions

```html
<button class="btn btn--danger">
  <svg class="icon icon--sm" aria-hidden="true">
    <use href="#icon-trash"></use>
  </svg>
  Delete Device
</button>
```

**Ghost Button**
- Purpose: Subtle actions, icon buttons
- Background: Transparent
- Text: `var(--color-primary-500)`

```html
<button class="btn btn--ghost">
  <svg class="icon icon--sm" aria-hidden="true">
    <use href="#icon-edit"></use>
  </svg>
  Edit
</button>
```

#### Button Sizes

```html
<!-- Extra Small -->
<button class="btn btn--primary btn--xs">Small Action</button>

<!-- Small -->
<button class="btn btn--primary btn--sm">Compact</button>

<!-- Default -->
<button class="btn btn--primary">Standard</button>

<!-- Large -->
<button class="btn btn--primary btn--lg">Important Action</button>

<!-- Block (Full Width) -->
<button class="btn btn--primary btn--block">Full Width</button>
```

#### Button States

**Interactive States:**
- Default: Base appearance
- Hover: Color darkening + subtle lift effect
- Active: Pressed state with darker color
- Focus: Visible focus ring for keyboard navigation
- Disabled: 60% opacity, no pointer events
- Loading: Spinner icon with "busy" aria state

```html
<!-- Loading State -->
<button class="btn btn--primary" aria-busy="true" disabled>
  <svg class="icon icon--sm spinner" aria-hidden="true">
    <use href="#icon-spinner"></use>
  </svg>
  Processing...
</button>

<!-- Disabled State -->
<button class="btn btn--primary" disabled>
  Cannot Perform Action
</button>
```

### Form Inputs

#### Text Input

```html
<div class="form-group">
  <label for="device-name" class="form-label form-label--required">
    Device Name
  </label>
  <input 
    type="text" 
    id="device-name" 
    name="deviceName"
    class="input" 
    placeholder="Enter device name"
    required
    aria-describedby="device-name-hint"
  >
  <div id="device-name-hint" class="form-hint">
    Choose a descriptive name for easy identification
  </div>
</div>
```

#### Select Dropdown

```html
<div class="form-group">
  <label for="device-type" class="form-label form-label--required">
    Device Type
  </label>
  <select id="device-type" name="deviceType" class="select" required>
    <option value="">Select device type...</option>
    <option value="snack">Snack Machine</option>
    <option value="beverage">Beverage Machine</option>
    <option value="combo">Combo Machine</option>
  </select>
</div>
```

#### Checkbox

```html
<div class="form-group">
  <div class="checkbox-group">
    <input type="checkbox" id="active-device" name="isActive" class="checkbox">
    <label for="active-device" class="checkbox-label">
      Device is currently active
    </label>
  </div>
</div>
```

#### Radio Buttons

```html
<div class="form-group">
  <fieldset class="radio-fieldset">
    <legend class="form-label">Cabinet Configuration</legend>
    <div class="radio-group">
      <input type="radio" id="single-cabinet" name="cabinetCount" value="1" class="radio">
      <label for="single-cabinet" class="radio-label">Single Cabinet</label>
    </div>
    <div class="radio-group">
      <input type="radio" id="dual-cabinet" name="cabinetCount" value="2" class="radio">
      <label for="dual-cabinet" class="radio-label">Dual Cabinet</label>
    </div>
  </fieldset>
</div>
```

#### Form Error States

```html
<div class="form-group form-group--error">
  <label for="email" class="form-label form-label--required">
    Email Address
  </label>
  <input 
    type="email" 
    id="email" 
    name="email"
    class="input input--error"
    value="invalid-email"
    aria-invalid="true"
    aria-describedby="email-error"
  >
  <div id="email-error" class="form-error" role="alert">
    <svg class="icon icon--xs icon--danger" aria-hidden="true">
      <use href="#icon-exclamation-circle"></use>
    </svg>
    Please enter a valid email address
  </div>
</div>
```

## Navigation Components

### Primary Navigation Bar

Main application navigation used in the iframe container system.

```html
<nav class="navbar" role="navigation" aria-label="Main navigation">
  <div class="nav-content">
    <div class="nav-left">
      <img src="/images/365-logo.png" alt="CVD Logo" class="nav-logo">
      <div class="nav-menu">
        <button class="nav-button" data-page="home">
          <svg class="icon icon--sm" aria-hidden="true">
            <use href="#icon-chart-bar"></use>
          </svg>
          Dashboard
        </button>
        <button class="nav-button" data-page="devices">
          <svg class="icon icon--sm" aria-hidden="true">
            <use href="#icon-server"></use>
          </svg>
          Devices
        </button>
        <button class="nav-button dropdown-trigger" id="ordersDropdown">
          <svg class="icon icon--sm" aria-hidden="true">
            <use href="#icon-clipboard-list"></use>
          </svg>
          Service Orders
          <svg class="icon icon--xs" aria-hidden="true">
            <use href="#icon-chevron-down"></use>
          </svg>
        </button>
      </div>
    </div>
    <div class="nav-right">
      <div class="nav-user">
        <span class="nav-user-name">John Doe</span>
        <button class="nav-user-menu" aria-label="User menu">
          <svg class="icon icon--sm" aria-hidden="true">
            <use href="#icon-user"></use>
          </svg>
        </button>
      </div>
    </div>
  </div>
</nav>
```

### Dropdown Menu

```html
<div class="dropdown dropdown--active" id="ordersDropdownMenu">
  <div class="dropdown-content">
    <a href="#service-orders" class="dropdown-item">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-list"></use>
      </svg>
      View Orders
    </a>
    <a href="#create-order" class="dropdown-item">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-plus"></use>
      </svg>
      Create Order
    </a>
    <div class="dropdown-divider"></div>
    <a href="#order-history" class="dropdown-item">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-clock"></use>
      </svg>
      Order History
    </a>
  </div>
</div>
```

### Breadcrumb Navigation

```html
<nav class="breadcrumbs" aria-label="Breadcrumb">
  <ol class="breadcrumbs-list">
    <li class="breadcrumbs-item">
      <a href="#home" class="breadcrumbs-link">Home</a>
    </li>
    <li class="breadcrumbs-item">
      <span class="breadcrumbs-separator" aria-hidden="true">/</span>
      <a href="#devices" class="breadcrumbs-link">Devices</a>
    </li>
    <li class="breadcrumbs-item">
      <span class="breadcrumbs-separator" aria-hidden="true">/</span>
      <span class="breadcrumbs-current" aria-current="page">Device Configuration</span>
    </li>
  </ol>
</nav>
```

### Mobile Bottom Navigation (Driver App)

```html
<nav class="bottom-nav" role="navigation" aria-label="Main navigation">
  <a href="#dashboard" class="nav-item nav-item--active" aria-current="page">
    <svg class="icon nav-icon" aria-hidden="true">
      <use href="#icon-chart-bar"></use>
    </svg>
    <span class="nav-label">Dashboard</span>
  </a>
  <a href="#routes" class="nav-item">
    <svg class="icon nav-icon" aria-hidden="true">
      <use href="#icon-truck"></use>
    </svg>
    <span class="nav-label">Routes</span>
    <span class="nav-badge" aria-label="3 active routes">3</span>
  </a>
  <a href="#orders" class="nav-item">
    <svg class="icon nav-icon" aria-hidden="true">
      <use href="#icon-clipboard-list"></use>
    </svg>
    <span class="nav-label">Orders</span>
  </a>
  <a href="#profile" class="nav-item">
    <svg class="icon nav-icon" aria-hidden="true">
      <use href="#icon-user"></use>
    </svg>
    <span class="nav-label">Profile</span>
  </a>
</nav>
```

## Data Display Components

### Data Tables

Enterprise-grade data tables optimized for vending machine management workflows.

#### Basic Table Structure

```html
<div class="table-container">
  <div class="table-header">
    <h2 class="table-title">Device Management</h2>
    <div class="table-actions">
      <button class="btn btn--primary btn--sm">
        <svg class="icon icon--xs" aria-hidden="true">
          <use href="#icon-plus"></use>
        </svg>
        Add Device
      </button>
      <button class="btn btn--secondary btn--sm">
        <svg class="icon icon--xs" aria-hidden="true">
          <use href="#icon-filter"></use>
        </svg>
        Filter
      </button>
    </div>
  </div>
  
  <div class="table-wrapper">
    <table class="table" role="table">
      <thead>
        <tr>
          <th class="table-cell--sortable" data-column="name">
            <button class="table-sort" aria-label="Sort by device name">
              Device Name
              <svg class="icon table-sort-icon" aria-hidden="true">
                <use href="#icon-chevron-down"></use>
              </svg>
            </button>
          </th>
          <th class="table-cell--sortable" data-column="location">
            <button class="table-sort">
              Location
              <svg class="icon table-sort-icon" aria-hidden="true">
                <use href="#icon-chevron-down"></use>
              </svg>
            </button>
          </th>
          <th>Status</th>
          <th>Last Service</th>
          <th class="table-cell--actions" aria-label="Actions">
            <span class="sr-only">Actions</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr class="table-row">
          <td class="table-cell--primary">
            <div class="device-cell">
              <svg class="icon icon--sm icon--primary" aria-hidden="true">
                <use href="#icon-server"></use>
              </svg>
              <div class="device-info">
                <div class="device-name">Snack Machine Alpha</div>
                <div class="device-id">DEV-001</div>
              </div>
            </div>
          </td>
          <td>Building A, Floor 2</td>
          <td>
            <span class="status-badge status-badge--success">
              <svg class="icon icon--xs" aria-hidden="true">
                <use href="#icon-check-circle"></use>
              </svg>
              Online
            </span>
          </td>
          <td>
            <time datetime="2025-08-10">Aug 10, 2025</time>
          </td>
          <td>
            <div class="table-actions">
              <button class="btn btn--ghost btn--sm" aria-label="Edit Snack Machine Alpha">
                <svg class="icon icon--sm" aria-hidden="true">
                  <use href="#icon-edit"></use>
                </svg>
              </button>
              <button class="btn btn--ghost btn--sm" aria-label="View details for Snack Machine Alpha">
                <svg class="icon icon--sm" aria-hidden="true">
                  <use href="#icon-eye"></use>
                </svg>
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  
  <div class="table-footer">
    <div class="table-info">
      Showing 1-10 of 45 devices
    </div>
    <nav class="pagination" aria-label="Table pagination">
      <button class="btn btn--ghost btn--sm" disabled>
        <svg class="icon icon--xs" aria-hidden="true">
          <use href="#icon-chevron-left"></use>
        </svg>
        Previous
      </button>
      <div class="pagination-pages">
        <button class="btn btn--ghost btn--sm btn--active">1</button>
        <button class="btn btn--ghost btn--sm">2</button>
        <button class="btn btn--ghost btn--sm">3</button>
        <span class="pagination-ellipsis">...</span>
        <button class="btn btn--ghost btn--sm">8</button>
      </div>
      <button class="btn btn--ghost btn--sm">
        Next
        <svg class="icon icon--xs" aria-hidden="true">
          <use href="#icon-chevron-right"></use>
        </svg>
      </button>
    </nav>
  </div>
</div>
```

#### Status Badge Component

```html
<!-- Success Status -->
<span class="status-badge status-badge--success">
  <svg class="icon icon--xs" aria-hidden="true">
    <use href="#icon-check-circle"></use>
  </svg>
  Delivered
</span>

<!-- Warning Status -->
<span class="status-badge status-badge--warning">
  <svg class="icon icon--xs" aria-hidden="true">
    <use href="#icon-exclamation-triangle"></use>
  </svg>
  Pending
</span>

<!-- Error Status -->
<span class="status-badge status-badge--danger">
  <svg class="icon icon--xs" aria-hidden="true">
    <use href="#icon-x-circle"></use>
  </svg>
  Failed
</span>

<!-- Info Status -->
<span class="status-badge status-badge--info">
  <svg class="icon icon--xs" aria-hidden="true">
    <use href="#icon-info-circle"></use>
  </svg>
  In Progress
</span>
```

### Card Components

#### Standard Card

```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Device Performance</h3>
    <div class="card-actions">
      <button class="btn btn--ghost btn--sm" aria-label="Card options">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-more-vertical"></use>
        </svg>
      </button>
    </div>
  </div>
  
  <div class="card-body">
    <div class="metric-grid">
      <div class="metric">
        <div class="metric-label">Revenue Today</div>
        <div class="metric-value">$1,247.50</div>
        <div class="metric-change metric-change--positive">
          <svg class="icon icon--xs" aria-hidden="true">
            <use href="#icon-trending-up"></use>
          </svg>
          +12.5%
        </div>
      </div>
      
      <div class="metric">
        <div class="metric-label">Transactions</div>
        <div class="metric-value">89</div>
        <div class="metric-change metric-change--positive">
          <svg class="icon icon--xs" aria-hidden="true">
            <use href="#icon-trending-up"></use>
          </svg>
          +8.2%
        </div>
      </div>
    </div>
  </div>
  
  <div class="card-footer">
    <button class="btn btn--secondary btn--sm">
      View Details
    </button>
  </div>
</div>
```

#### Statistics Card

```html
<div class="card card--stat">
  <div class="stat-content">
    <div class="stat-icon stat-icon--success">
      <svg class="icon icon--lg" aria-hidden="true">
        <use href="#icon-trending-up"></use>
      </svg>
    </div>
    <div class="stat-details">
      <div class="stat-value">$12,847</div>
      <div class="stat-label">Weekly Revenue</div>
      <div class="stat-change stat-change--positive">
        <svg class="icon icon--xs" aria-hidden="true">
          <use href="#icon-arrow-up"></use>
        </svg>
        15.3% from last week
      </div>
    </div>
  </div>
</div>
```

### List Components

#### Action List

```html
<div class="action-list">
  <h3 class="action-list-title">Recent Activities</h3>
  <ul class="action-list-items">
    <li class="action-list-item">
      <div class="action-list-icon">
        <svg class="icon icon--sm icon--success" aria-hidden="true">
          <use href="#icon-check-circle"></use>
        </svg>
      </div>
      <div class="action-list-content">
        <div class="action-list-primary">Service order completed</div>
        <div class="action-list-secondary">
          Device: Snack Machine Alpha • 
          <time datetime="2025-08-12T14:30">2:30 PM</time>
        </div>
      </div>
    </li>
    
    <li class="action-list-item">
      <div class="action-list-icon">
        <svg class="icon icon--sm icon--warning" aria-hidden="true">
          <use href="#icon-exclamation-triangle"></use>
        </svg>
      </div>
      <div class="action-list-content">
        <div class="action-list-primary">Low inventory alert</div>
        <div class="action-list-secondary">
          Product: Coca-Cola • Location: Building B
        </div>
      </div>
    </li>
  </ul>
</div>
```

## Feedback Components

### Modal Dialogs

#### Confirmation Modal

```html
<div class="modal modal--active" id="deleteModal" role="dialog" aria-labelledby="deleteModalTitle" aria-describedby="deleteModalDesc">
  <div class="modal-backdrop" data-modal-close></div>
  <div class="modal-content">
    <div class="modal-header">
      <h2 class="modal-title" id="deleteModalTitle">Confirm Deletion</h2>
      <button class="modal-close" data-modal-close aria-label="Close dialog">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-x"></use>
        </svg>
      </button>
    </div>
    
    <div class="modal-body">
      <div class="modal-icon modal-icon--danger">
        <svg class="icon icon--xl" aria-hidden="true">
          <use href="#icon-exclamation-triangle"></use>
        </svg>
      </div>
      <p id="deleteModalDesc">
        Are you sure you want to delete "Snack Machine Alpha"? 
        This action cannot be undone and will remove all associated data.
      </p>
    </div>
    
    <div class="modal-footer">
      <button class="btn btn--secondary" data-modal-close>Cancel</button>
      <button class="btn btn--danger" id="confirmDelete">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-trash"></use>
        </svg>
        Delete Device
      </button>
    </div>
  </div>
</div>
```

#### Form Modal

```html
<div class="modal modal--large" id="deviceModal" role="dialog" aria-labelledby="deviceModalTitle">
  <div class="modal-backdrop" data-modal-close></div>
  <div class="modal-content">
    <div class="modal-header">
      <h2 class="modal-title" id="deviceModalTitle">Add New Device</h2>
      <button class="modal-close" data-modal-close aria-label="Close dialog">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-x"></use>
        </svg>
      </button>
    </div>
    
    <form class="modal-body">
      <div class="form-group">
        <label for="modalDeviceName" class="form-label form-label--required">
          Device Name
        </label>
        <input type="text" id="modalDeviceName" name="deviceName" class="input" required>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label for="modalDeviceType" class="form-label form-label--required">
            Device Type
          </label>
          <select id="modalDeviceType" name="deviceType" class="select" required>
            <option value="">Select type...</option>
            <option value="snack">Snack Machine</option>
            <option value="beverage">Beverage Machine</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="modalLocation" class="form-label form-label--required">
            Location
          </label>
          <input type="text" id="modalLocation" name="location" class="input" required>
        </div>
      </div>
    </form>
    
    <div class="modal-footer">
      <button class="btn btn--secondary" data-modal-close>Cancel</button>
      <button class="btn btn--primary" type="submit" form="deviceForm">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-plus"></use>
        </svg>
        Add Device
      </button>
    </div>
  </div>
</div>
```

### Toast Notifications

```html
<div class="toast-container" role="region" aria-live="polite" aria-label="Notifications">
  <!-- Success Toast -->
  <div class="toast toast--success">
    <div class="toast-icon">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-check-circle"></use>
      </svg>
    </div>
    <div class="toast-content">
      <div class="toast-title">Device Added Successfully</div>
      <div class="toast-message">Snack Machine Alpha has been added to your fleet.</div>
    </div>
    <button class="toast-close" aria-label="Dismiss notification">
      <svg class="icon icon--xs" aria-hidden="true">
        <use href="#icon-x"></use>
      </svg>
    </button>
  </div>
  
  <!-- Error Toast -->
  <div class="toast toast--error">
    <div class="toast-icon">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-x-circle"></use>
      </svg>
    </div>
    <div class="toast-content">
      <div class="toast-title">Connection Failed</div>
      <div class="toast-message">Unable to sync data. Please check your connection.</div>
    </div>
    <button class="toast-close" aria-label="Dismiss notification">
      <svg class="icon icon--xs" aria-hidden="true">
        <use href="#icon-x"></use>
      </svg>
    </button>
  </div>
</div>
```

### Alert Components

```html
<!-- Info Alert -->
<div class="alert alert--info">
  <div class="alert-icon">
    <svg class="icon icon--md" aria-hidden="true">
      <use href="#icon-info-circle"></use>
    </svg>
  </div>
  <div class="alert-content">
    <div class="alert-title">System Maintenance Scheduled</div>
    <div class="alert-message">
      CVD will undergo maintenance on August 15th from 2:00 AM to 4:00 AM EST. 
      Some features may be temporarily unavailable.
    </div>
  </div>
  <button class="alert-close" aria-label="Dismiss alert">
    <svg class="icon icon--sm" aria-hidden="true">
      <use href="#icon-x"></use>
    </svg>
  </button>
</div>

<!-- Warning Alert -->
<div class="alert alert--warning">
  <div class="alert-icon">
    <svg class="icon icon--md" aria-hidden="true">
      <use href="#icon-exclamation-triangle"></use>
    </svg>
  </div>
  <div class="alert-content">
    <div class="alert-title">Low Inventory Alert</div>
    <div class="alert-message">
      3 devices have products below minimum stock levels. 
      <a href="#service-orders" class="alert-link">Create service orders</a> to restock.
    </div>
  </div>
</div>
```

### Loading States

#### Spinner Component

```html
<!-- Inline Spinner -->
<div class="spinner" aria-label="Loading"></div>

<!-- Button Loading State -->
<button class="btn btn--primary" disabled aria-busy="true">
  <div class="spinner spinner--sm" aria-hidden="true"></div>
  Processing...
</button>

<!-- Large Loading Overlay -->
<div class="loading-overlay">
  <div class="loading-content">
    <div class="spinner spinner--lg" aria-label="Loading content"></div>
    <div class="loading-text">Loading devices...</div>
  </div>
</div>
```

#### Skeleton Loading

```html
<div class="skeleton-container">
  <!-- Skeleton Card -->
  <div class="card">
    <div class="card-header">
      <div class="skeleton skeleton--text skeleton--lg" style="width: 40%;"></div>
    </div>
    <div class="card-body">
      <div class="skeleton skeleton--text" style="width: 80%;"></div>
      <div class="skeleton skeleton--text" style="width: 60%;"></div>
      <div class="skeleton skeleton--text" style="width: 70%;"></div>
    </div>
  </div>
  
  <!-- Skeleton Table Rows -->
  <div class="table-skeleton">
    <div class="skeleton skeleton--table-row"></div>
    <div class="skeleton skeleton--table-row"></div>
    <div class="skeleton skeleton--table-row"></div>
  </div>
</div>
```

## Layout Components

### Container System

```html
<!-- Narrow Container (Forms) -->
<main class="container container--narrow">
  <h1>User Settings</h1>
  <form class="settings-form">
    <!-- Form content -->
  </form>
</main>

<!-- Dashboard Container -->
<main class="container container--dashboard">
  <div class="dashboard-grid">
    <div class="dashboard-stats">
      <!-- Statistics cards -->
    </div>
    <div class="dashboard-chart">
      <!-- Chart component -->
    </div>
  </div>
</main>

<!-- Enterprise Container (Data Tables) -->
<main class="container container--enterprise">
  <div class="table-container">
    <!-- Large data table -->
  </div>
</main>
```

### Grid Layouts

```html
<!-- Dashboard Grid -->
<div class="grid grid--dashboard">
  <div class="grid-item grid-item--stat">
    <!-- Stat card -->
  </div>
  <div class="grid-item grid-item--chart">
    <!-- Chart -->
  </div>
  <div class="grid-item grid-item--list">
    <!-- Activity list -->
  </div>
</div>

<!-- Auto-fit Grid -->
<div class="grid grid--auto">
  <div class="card">Card 1</div>
  <div class="card">Card 2</div>
  <div class="card">Card 3</div>
</div>
```

### Panel Layout

```html
<div class="panel-layout">
  <div class="panel-sidebar">
    <nav class="sidebar-nav">
      <h3 class="sidebar-title">Filters</h3>
      <!-- Filter controls -->
    </nav>
  </div>
  
  <main class="panel-main">
    <div class="panel-header">
      <h1>Device Management</h1>
      <div class="panel-actions">
        <!-- Action buttons -->
      </div>
    </div>
    
    <div class="panel-content">
      <!-- Main content -->
    </div>
  </main>
</div>
```

## Mobile-Specific Components

### Touch-Optimized Controls

#### Large Touch Buttons

```html
<div class="mobile-actions">
  <button class="btn btn--primary btn--touch">
    <svg class="icon icon--lg" aria-hidden="true">
      <use href="#icon-check"></use>
    </svg>
    Complete Service
  </button>
  
  <button class="btn btn--secondary btn--touch">
    <svg class="icon icon--lg" aria-hidden="true">
      <use href="#icon-camera"></use>
    </svg>
    Take Photo
  </button>
</div>
```

#### Swipe Cards (Driver App)

```html
<div class="service-card swipe-card">
  <div class="service-card-header">
    <div class="service-location">Building A - Floor 2</div>
    <div class="service-priority priority--high">High Priority</div>
  </div>
  
  <div class="service-card-body">
    <div class="service-device">
      <svg class="icon icon--md" aria-hidden="true">
        <use href="#icon-server"></use>
      </svg>
      <div class="device-details">
        <div class="device-name">Snack Machine Alpha</div>
        <div class="device-id">DEV-001</div>
      </div>
    </div>
    
    <div class="service-tasks">
      <div class="task-count">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-clipboard-list"></use>
        </svg>
        5 items to restock
      </div>
    </div>
  </div>
  
  <div class="service-card-actions">
    <button class="btn btn--success btn--block">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-play"></use>
      </svg>
      Start Service
    </button>
  </div>
  
  <!-- Swipe Actions -->
  <div class="swipe-actions swipe-actions--left">
    <button class="swipe-action swipe-action--complete" aria-label="Mark as complete">
      <svg class="icon icon--lg" aria-hidden="true">
        <use href="#icon-check"></use>
      </svg>
    </button>
  </div>
  
  <div class="swipe-actions swipe-actions--right">
    <button class="swipe-action swipe-action--skip" aria-label="Skip service">
      <svg class="icon icon--lg" aria-hidden="true">
        <use href="#icon-forward"></use>
      </svg>
    </button>
  </div>
</div>
```

### Mobile Headers

```html
<header class="mobile-header">
  <div class="mobile-header-content">
    <button class="mobile-header-back" aria-label="Go back">
      <svg class="icon icon--md" aria-hidden="true">
        <use href="#icon-arrow-left"></use>
      </svg>
    </button>
    
    <h1 class="mobile-header-title">Service Order #1234</h1>
    
    <div class="mobile-header-actions">
      <button class="mobile-header-action" aria-label="More options">
        <svg class="icon icon--md" aria-hidden="true">
          <use href="#icon-more-vertical"></use>
        </svg>
      </button>
    </div>
  </div>
</header>
```

### Pull-to-Refresh

```html
<div class="pull-to-refresh" data-component="pull-refresh">
  <div class="pull-to-refresh-indicator">
    <svg class="icon icon--lg pull-refresh-icon" aria-hidden="true">
      <use href="#icon-refresh"></use>
    </svg>
    <div class="pull-refresh-text">Pull to refresh</div>
  </div>
  
  <div class="pull-to-refresh-content">
    <!-- Scrollable content -->
  </div>
</div>
```

## Implementation Guidelines

### Component Usage Rules

1. **Consistency**: Always use the same component for the same purpose
2. **Accessibility**: Include proper ARIA labels and roles
3. **Progressive Enhancement**: Components work without JavaScript
4. **Touch Targets**: Minimum 44px for mobile interactions
5. **Focus Management**: Visible focus indicators for all interactive elements
6. **Loading States**: Show feedback for async operations
7. **Error Handling**: Provide clear error messages and recovery paths

### Responsive Behavior

All components adapt to different screen sizes:
- **Mobile (0-767px)**: Touch-optimized, simplified layouts
- **Tablet (768-1023px)**: Hybrid interactions, medium density
- **Desktop (1024px+)**: Mouse-optimized, full feature set

### Performance Considerations

- Use CSS transforms for animations
- Implement virtual scrolling for large lists
- Lazy load images and heavy content
- Minimize DOM updates during interactions
- Cache frequently accessed elements

---

**Related Documentation:**
- [Design System Overview](../DESIGN_SYSTEM.md)
- [User Flows Documentation](../user-flows/USER_FLOWS_OVERVIEW.md)
- [Design Patterns](../patterns/README.md)

**Last Updated:** 2025-08-12  
**Component Count:** 47 documented components  
**Coverage:** Desktop, Tablet, Mobile (PWA)