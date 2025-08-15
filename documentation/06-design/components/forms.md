---
title: Form Components
description: Detailed specifications for all form-related UI components in the CVD application
feature: design-system
last-updated: 2025-08-12
version: 2.1.0
related-files:
  - UI_COMPONENTS_OVERVIEW.md
  - ../DESIGN_SYSTEM.md
dependencies:
  - design-system-tokens
  - accessibility-patterns
status: active
---

# Form Components Specification


## Metadata
- **ID**: 06_DESIGN_COMPONENTS_FORMS
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #authentication #data-exchange #debugging #device-management #dex-parser #driver-app #integration #interface #machine-learning #mobile #optimization #pwa #security #troubleshooting #ui-design #user-experience #vending-machine
- **Intent**: CVD form components are designed for efficient data entry in enterprise vending machine management workflows
- **Audience**: system administrators, managers, end users
- **Related**: README.md, UI_COMPONENTS_OVERVIEW.md, DESIGN_SYSTEM.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/06-design/components/
- **Category**: Components
- **Search Keywords**: ####, **disabled, **error, **focus, **grouped, **live, **progress, **success, **warning, accessibility, always, association, association**, background:, basic

## Overview

CVD form components are designed for efficient data entry in enterprise vending machine management workflows. All components follow WCAG AA accessibility guidelines and are optimized for both desktop and mobile interactions.

## Table of Contents

1. [Design Principles](#design-principles)
2. [Input Fields](#input-fields)
3. [Selection Controls](#selection-controls)
4. [Form Layout](#form-layout)
5. [Validation Patterns](#validation-patterns)
6. [Accessibility Requirements](#accessibility-requirements)

## Design Principles

### Enterprise Form Standards

**Efficiency First**
- Clear visual hierarchy guides users through forms
- Smart defaults reduce manual entry
- Logical tab order for keyboard navigation

**Error Prevention**
- Real-time validation where appropriate
- Clear formatting requirements
- Confirmation for destructive actions

**Accessibility Always**
- Proper label associations
- Error messages linked to form fields
- High contrast for all states

## Input Fields

### Text Input

The foundation of data entry across the CVD application.

#### Visual Specifications

```css
.input {
  /* Layout */
  width: 100%;
  min-height: 44px; /* Touch target compliance */
  padding: var(--input-padding-y) var(--input-padding-x);
  
  /* Typography */
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--color-neutral-900);
  
  /* Visual Design */
  background: var(--color-neutral-0);
  border: var(--border-thin) solid var(--input-border-color);
  border-radius: var(--input-radius);
  box-shadow: none;
  
  /* Interactions */
  transition: border-color var(--duration-fast) var(--ease-out),
              box-shadow var(--duration-fast) var(--ease-out);
}
```

#### Interactive States

**Default State**
- Border: `var(--color-neutral-300)`
- Background: `var(--color-neutral-0)`
- Text: `var(--color-neutral-900)`
- Placeholder: `var(--color-neutral-400)`

**Focus State**
```css
.input:focus {
  outline: none;
  border-color: var(--input-focus-border);
  box-shadow: 0 0 0 3px rgba(0, 109, 254, 0.1);
}
```

**Error State**
```css
.input--error {
  border-color: var(--color-danger);
}

.input--error:focus {
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
}
```

**Success State**
```css
.input--success {
  border-color: var(--color-success);
}

.input--success:focus {
  box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);
}
```

**Disabled State**
```css
.input:disabled {
  background: var(--color-neutral-100);
  border-color: var(--color-neutral-300);
  color: var(--color-neutral-500);
  cursor: not-allowed;
}
```

#### Implementation Examples

**Basic Text Input**
```html
<div class="form-group">
  <label for="device-name" class="form-label">
    Device Name
  </label>
  <input 
    type="text" 
    id="device-name" 
    name="deviceName"
    class="input" 
    placeholder="Enter device name"
    autocomplete="organization"
  >
</div>
```

**Required Field with Hint**
```html
<div class="form-group">
  <label for="device-location" class="form-label form-label--required">
    Location
  </label>
  <input 
    type="text" 
    id="device-location" 
    name="location"
    class="input" 
    required
    aria-describedby="location-hint"
    autocomplete="address-line1"
  >
  <div id="location-hint" class="form-hint">
    Building name, floor, or specific area description
  </div>
</div>
```

**Error State with Recovery**
```html
<div class="form-group form-group--error">
  <label for="device-serial" class="form-label form-label--required">
    Serial Number
  </label>
  <input 
    type="text" 
    id="device-serial" 
    name="serialNumber"
    class="input input--error"
    value="INVALID123"
    required
    aria-invalid="true"
    aria-describedby="serial-error"
  >
  <div id="serial-error" class="form-error" role="alert">
    <svg class="icon icon--xs icon--danger" aria-hidden="true">
      <use href="#icon-exclamation-circle"></use>
    </svg>
    Serial number must be at least 8 characters and contain only letters and numbers
  </div>
</div>
```

### Textarea

For multi-line text input such as notes and descriptions.

```html
<div class="form-group">
  <label for="service-notes" class="form-label">
    Service Notes
  </label>
  <textarea 
    id="service-notes" 
    name="notes"
    class="textarea" 
    rows="4"
    placeholder="Add any additional notes about this service..."
    aria-describedby="notes-hint"
  ></textarea>
  <div id="notes-hint" class="form-hint">
    Optional: Include any issues found or special instructions
  </div>
</div>
```

```css
.textarea {
  /* Inherits from .input styles */
  resize: vertical;
  min-height: 100px;
  line-height: var(--leading-relaxed);
}
```

### Number Input

Specialized for numeric data entry.

```html
<div class="form-group">
  <label for="par-level" class="form-label form-label--required">
    Par Level
  </label>
  <div class="input-group">
    <input 
      type="number" 
      id="par-level" 
      name="parLevel"
      class="input input--number" 
      min="0"
      max="999"
      step="1"
      required
      aria-describedby="par-hint"
    >
    <div class="input-suffix">
      <span class="input-suffix-text">items</span>
    </div>
  </div>
  <div id="par-hint" class="form-hint">
    Minimum stock level before restocking is needed
  </div>
</div>
```

### Email Input

With built-in validation patterns.

```html
<div class="form-group">
  <label for="user-email" class="form-label form-label--required">
    Email Address
  </label>
  <input 
    type="email" 
    id="user-email" 
    name="email"
    class="input input--email" 
    required
    autocomplete="email"
    pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
    aria-describedby="email-hint"
  >
  <div id="email-hint" class="form-hint">
    Used for notifications and account recovery
  </div>
</div>
```

### Password Input

With show/hide toggle functionality.

```html
<div class="form-group">
  <label for="user-password" class="form-label form-label--required">
    Password
  </label>
  <div class="input-group input-group--password">
    <input 
      type="password" 
      id="user-password" 
      name="password"
      class="input" 
      required
      autocomplete="new-password"
      aria-describedby="password-requirements"
    >
    <button 
      type="button" 
      class="input-action" 
      aria-label="Show password"
      data-password-toggle
    >
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-eye"></use>
      </svg>
    </button>
  </div>
  <div id="password-requirements" class="form-hint">
    Must be at least 8 characters with uppercase, lowercase, and number
  </div>
</div>
```

## Selection Controls

### Select Dropdown

Standard dropdown selection for predefined options.

#### Visual Specifications

```css
.select {
  /* Base input styles */
  width: 100%;
  min-height: 44px;
  padding: var(--input-padding-y) var(--input-padding-x);
  padding-right: var(--space-xl); /* Space for arrow */
  
  /* Typography */
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--color-neutral-900);
  
  /* Visual Design */
  background: var(--color-neutral-0) url("data:image/svg+xml,<svg...>") no-repeat;
  background-position: right var(--space-sm) center;
  background-size: 20px;
  border: var(--border-thin) solid var(--input-border-color);
  border-radius: var(--input-radius);
  
  /* Remove default styling */
  appearance: none;
  cursor: pointer;
}
```

#### Implementation Examples

**Basic Select**
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
    <option value="coffee">Coffee Machine</option>
  </select>
</div>
```

**Grouped Options**
```html
<div class="form-group">
  <label for="product-category" class="form-label">
    Product Category
  </label>
  <select id="product-category" name="productCategory" class="select">
    <option value="">All Categories</option>
    <optgroup label="Beverages">
      <option value="soda">Sodas</option>
      <option value="water">Water</option>
      <option value="juice">Juices</option>
      <option value="energy">Energy Drinks</option>
    </optgroup>
    <optgroup label="Snacks">
      <option value="chips">Chips</option>
      <option value="candy">Candy</option>
      <option value="crackers">Crackers</option>
      <option value="nuts">Nuts & Seeds</option>
    </optgroup>
  </select>
</div>
```

**Select with Status Indicator**
```html
<div class="form-group">
  <label for="service-status" class="form-label">
    Order Status
  </label>
  <div class="select-wrapper">
    <select id="service-status" name="status" class="select select--status">
      <option value="pending" data-status="warning">Pending</option>
      <option value="in-progress" data-status="info">In Progress</option>
      <option value="completed" data-status="success">Completed</option>
      <option value="failed" data-status="danger">Failed</option>
    </select>
    <div class="select-status" id="status-indicator"></div>
  </div>
</div>
```

### Multi-Select

For selecting multiple options from a list.

```html
<div class="form-group">
  <label for="user-roles" class="form-label">
    User Roles
  </label>
  <div class="multiselect" data-component="multiselect">
    <div class="multiselect-trigger" tabindex="0" aria-haspopup="listbox" aria-expanded="false">
      <div class="multiselect-value">
        <span class="multiselect-placeholder">Select roles...</span>
      </div>
      <svg class="icon icon--sm multiselect-arrow" aria-hidden="true">
        <use href="#icon-chevron-down"></use>
      </svg>
    </div>
    
    <div class="multiselect-dropdown" role="listbox" aria-multiselectable="true">
      <label class="multiselect-option" role="option">
        <input type="checkbox" name="roles[]" value="admin" class="multiselect-checkbox">
        <span class="multiselect-label">Administrator</span>
      </label>
      <label class="multiselect-option" role="option">
        <input type="checkbox" name="roles[]" value="manager" class="multiselect-checkbox">
        <span class="multiselect-label">Manager</span>
      </label>
      <label class="multiselect-option" role="option">
        <input type="checkbox" name="roles[]" value="driver" class="multiselect-checkbox">
        <span class="multiselect-label">Driver</span>
      </label>
      <label class="multiselect-option" role="option">
        <input type="checkbox" name="roles[]" value="viewer" class="multiselect-checkbox">
        <span class="multiselect-label">Viewer</span>
      </label>
    </div>
  </div>
</div>
```

### Radio Buttons

For single selection from a small set of options.

```html
<fieldset class="form-group">
  <legend class="form-label form-label--required">
    Service Frequency
  </legend>
  <div class="radio-group">
    <div class="radio-item">
      <input type="radio" id="frequency-weekly" name="serviceFrequency" value="weekly" class="radio" required>
      <label for="frequency-weekly" class="radio-label">
        <div class="radio-content">
          <div class="radio-title">Weekly</div>
          <div class="radio-description">Every 7 days</div>
        </div>
      </label>
    </div>
    
    <div class="radio-item">
      <input type="radio" id="frequency-biweekly" name="serviceFrequency" value="biweekly" class="radio">
      <label for="frequency-biweekly" class="radio-label">
        <div class="radio-content">
          <div class="radio-title">Bi-weekly</div>
          <div class="radio-description">Every 14 days</div>
        </div>
      </label>
    </div>
    
    <div class="radio-item">
      <input type="radio" id="frequency-monthly" name="serviceFrequency" value="monthly" class="radio">
      <label for="frequency-monthly" class="radio-label">
        <div class="radio-content">
          <div class="radio-title">Monthly</div>
          <div class="radio-description">Every 30 days</div>
        </div>
      </label>
    </div>
  </div>
</fieldset>
```

### Checkboxes

For multiple selections and boolean options.

#### Single Checkbox

```html
<div class="form-group">
  <div class="checkbox-item">
    <input type="checkbox" id="device-active" name="isActive" class="checkbox" checked>
    <label for="device-active" class="checkbox-label">
      Device is currently active
    </label>
  </div>
</div>
```

#### Checkbox Group

```html
<fieldset class="form-group">
  <legend class="form-label">
    Notification Preferences
  </legend>
  <div class="checkbox-group">
    <div class="checkbox-item">
      <input type="checkbox" id="notify-email" name="notifications[]" value="email" class="checkbox">
      <label for="notify-email" class="checkbox-label">
        <div class="checkbox-content">
          <div class="checkbox-title">Email Notifications</div>
          <div class="checkbox-description">Receive alerts via email</div>
        </div>
      </label>
    </div>
    
    <div class="checkbox-item">
      <input type="checkbox" id="notify-sms" name="notifications[]" value="sms" class="checkbox">
      <label for="notify-sms" class="checkbox-label">
        <div class="checkbox-content">
          <div class="checkbox-title">SMS Notifications</div>
          <div class="checkbox-description">Receive urgent alerts via text</div>
        </div>
      </label>
    </div>
    
    <div class="checkbox-item">
      <input type="checkbox" id="notify-app" name="notifications[]" value="app" class="checkbox" checked>
      <label for="notify-app" class="checkbox-label">
        <div class="checkbox-content">
          <div class="checkbox-title">In-App Notifications</div>
          <div class="checkbox-description">Show notifications in the application</div>
        </div>
      </label>
    </div>
  </div>
</fieldset>
```

#### Toggle Switch

For clear on/off states.

```html
<div class="form-group">
  <div class="toggle-item">
    <input type="checkbox" id="auto-sync" name="autoSync" class="toggle" checked>
    <label for="auto-sync" class="toggle-label">
      <span class="toggle-content">
        <span class="toggle-title">Auto-sync enabled</span>
        <span class="toggle-description">Automatically sync data every 5 minutes</span>
      </span>
      <span class="toggle-switch" aria-hidden="true">
        <span class="toggle-handle"></span>
      </span>
    </label>
  </div>
</div>
```

### Date & Time Inputs

#### Date Picker

```html
<div class="form-group">
  <label for="service-date" class="form-label form-label--required">
    Scheduled Service Date
  </label>
  <input 
    type="date" 
    id="service-date" 
    name="serviceDate"
    class="input input--date" 
    required
    min="2025-08-12"
    aria-describedby="date-hint"
  >
  <div id="date-hint" class="form-hint">
    Service must be scheduled at least 24 hours in advance
  </div>
</div>
```

#### Time Picker

```html
<div class="form-group">
  <label for="service-time" class="form-label form-label--required">
    Preferred Time
  </label>
  <select id="service-time" name="serviceTime" class="select" required>
    <option value="">Select time...</option>
    <option value="08:00">8:00 AM</option>
    <option value="09:00">9:00 AM</option>
    <option value="10:00">10:00 AM</option>
    <option value="11:00">11:00 AM</option>
    <option value="12:00">12:00 PM</option>
    <option value="13:00">1:00 PM</option>
    <option value="14:00">2:00 PM</option>
    <option value="15:00">3:00 PM</option>
    <option value="16:00">4:00 PM</option>
    <option value="17:00">5:00 PM</option>
  </select>
</div>
```

#### Date Range Picker

```html
<div class="form-group">
  <label class="form-label">
    Service Period
  </label>
  <div class="date-range">
    <div class="date-range-input">
      <label for="start-date" class="sr-only">Start date</label>
      <input 
        type="date" 
        id="start-date" 
        name="startDate"
        class="input input--date" 
        placeholder="Start date"
        aria-label="Start date"
      >
    </div>
    <div class="date-range-separator">
      <span aria-hidden="true">to</span>
    </div>
    <div class="date-range-input">
      <label for="end-date" class="sr-only">End date</label>
      <input 
        type="date" 
        id="end-date" 
        name="endDate"
        class="input input--date" 
        placeholder="End date"
        aria-label="End date"
      >
    </div>
  </div>
</div>
```

## Form Layout

### Form Groups

Basic building blocks for organizing form elements.

```css
.form-group {
  margin-bottom: var(--space-lg);
}

.form-group--compact {
  margin-bottom: var(--space-md);
}

.form-group--error {
  /* Enhanced styling for error state */
}

.form-group--success {
  /* Styling for success state */
}
```

### Form Rows

For horizontal form layouts.

```html
<div class="form-row">
  <div class="form-col">
    <div class="form-group">
      <label for="first-name" class="form-label form-label--required">
        First Name
      </label>
      <input type="text" id="first-name" name="firstName" class="input" required>
    </div>
  </div>
  
  <div class="form-col">
    <div class="form-group">
      <label for="last-name" class="form-label form-label--required">
        Last Name
      </label>
      <input type="text" id="last-name" name="lastName" class="input" required>
    </div>
  </div>
</div>

<div class="form-row">
  <div class="form-col form-col--2">
    <div class="form-group">
      <label for="phone" class="form-label">
        Phone Number
      </label>
      <input type="tel" id="phone" name="phone" class="input" autocomplete="tel">
    </div>
  </div>
  
  <div class="form-col form-col--1">
    <div class="form-group">
      <label for="extension" class="form-label">
        Ext.
      </label>
      <input type="text" id="extension" name="extension" class="input">
    </div>
  </div>
</div>
```

### Form Sections

For organizing complex forms into logical groups.

```html
<form class="form">
  <section class="form-section">
    <header class="form-section-header">
      <h2 class="form-section-title">
        <svg class="icon icon--md" aria-hidden="true">
          <use href="#icon-server"></use>
        </svg>
        Device Information
      </h2>
      <div class="form-section-description">
        Basic details about the vending machine
      </div>
    </header>
    
    <div class="form-section-content">
      <!-- Device-related form fields -->
    </div>
  </section>
  
  <section class="form-section">
    <header class="form-section-header">
      <h2 class="form-section-title">
        <svg class="icon icon--md" aria-hidden="true">
          <use href="#icon-map-pin"></use>
        </svg>
        Location Details
      </h2>
      <div class="form-section-description">
        Where the device will be placed
      </div>
    </header>
    
    <div class="form-section-content">
      <!-- Location-related form fields -->
    </div>
  </section>
  
  <div class="form-actions">
    <button type="button" class="btn btn--secondary">
      Cancel
    </button>
    <button type="submit" class="btn btn--primary">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="#icon-save"></use>
      </svg>
      Save Device
    </button>
  </div>
</form>
```

### Responsive Form Layout

```css
.form-row {
  display: grid;
  gap: var(--space-md);
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .form-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .form-col--1 {
    grid-column: span 1;
  }
  
  .form-col--2 {
    grid-column: span 2;
  }
}

@media (min-width: 1024px) {
  .form-row {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .form-col--3 {
    grid-column: span 3;
  }
}
```

## Validation Patterns

### Real-time Validation

```html
<div class="form-group" data-validation="real-time">
  <label for="username" class="form-label form-label--required">
    Username
  </label>
  <input 
    type="text" 
    id="username" 
    name="username"
    class="input" 
    required
    minlength="3"
    maxlength="20"
    pattern="^[a-zA-Z0-9_]+$"
    aria-describedby="username-requirements username-validation"
    data-validate-on="blur input"
  >
  <div id="username-requirements" class="form-hint">
    3-20 characters: letters, numbers, and underscores only
  </div>
  <div id="username-validation" class="form-validation" role="status">
    <!-- Validation messages appear here -->
  </div>
</div>
```

### Validation States

**Success State**
```html
<div class="form-group form-group--success">
  <label for="valid-email" class="form-label form-label--required">
    Email Address
  </label>
  <input 
    type="email" 
    id="valid-email" 
    name="email"
    class="input input--success"
    value="user@company.com"
    aria-describedby="email-success"
  >
  <div id="email-success" class="form-success">
    <svg class="icon icon--xs icon--success" aria-hidden="true">
      <use href="#icon-check-circle"></use>
    </svg>
    Email address is valid and available
  </div>
</div>
```

**Warning State**
```html
<div class="form-group form-group--warning">
  <label for="weak-password" class="form-label form-label--required">
    Password
  </label>
  <input 
    type="password" 
    id="weak-password" 
    name="password"
    class="input input--warning"
    aria-describedby="password-warning"
  >
  <div id="password-warning" class="form-warning">
    <svg class="icon icon--xs icon--warning" aria-hidden="true">
      <use href="#icon-exclamation-triangle"></use>
    </svg>
    Password strength: Weak. Consider adding special characters.
  </div>
</div>
```

### Form Submission States

**Loading State**
```html
<div class="form-actions form-actions--loading">
  <button type="submit" class="btn btn--primary" disabled aria-busy="true">
    <svg class="icon icon--sm spinner" aria-hidden="true">
      <use href="#icon-spinner"></use>
    </svg>
    Creating Device...
  </button>
  <button type="button" class="btn btn--secondary" disabled>
    Cancel
  </button>
</div>
```

**Error State with Recovery**
```html
<div class="form-error form-error--global" role="alert">
  <div class="form-error-icon">
    <svg class="icon icon--md icon--danger" aria-hidden="true">
      <use href="#icon-x-circle"></use>
    </svg>
  </div>
  <div class="form-error-content">
    <div class="form-error-title">Unable to Save Device</div>
    <div class="form-error-message">
      The serial number you entered is already in use. Please check and try again.
    </div>
    <div class="form-error-actions">
      <button type="button" class="btn btn--sm btn--secondary" data-action="retry">
        Try Again
      </button>
      <a href="#device-lookup" class="btn btn--sm btn--ghost">
        Look Up Existing Device
      </a>
    </div>
  </div>
</div>
```

## Accessibility Requirements

### ARIA Patterns

**Required Fields**
```html
<label for="required-field" class="form-label form-label--required">
  Device Name
  <span aria-hidden="true">*</span>
</label>
<input 
  type="text" 
  id="required-field" 
  name="deviceName"
  class="input" 
  required
  aria-required="true"
>
```

**Error Association**
```html
<input 
  type="email" 
  id="email-input"
  class="input input--error"
  aria-invalid="true"
  aria-describedby="email-error email-hint"
>
<div id="email-error" class="form-error" role="alert">
  Please enter a valid email address
</div>
<div id="email-hint" class="form-hint">
  Used for account notifications
</div>
```

**Live Validation**
```html
<div class="form-group" data-validation="live">
  <label for="live-field" class="form-label">Username</label>
  <input 
    type="text" 
    id="live-field"
    class="input"
    aria-describedby="live-status"
  >
  <div id="live-status" role="status" aria-live="polite" class="form-status">
    <!-- Live validation messages appear here -->
  </div>
</div>
```

### Keyboard Navigation

**Tab Order**
- Form fields follow logical reading order
- Skip links for long forms
- Fieldsets group related controls

**Keyboard Shortcuts**
```html
<form>
  <div class="form-shortcuts" aria-label="Keyboard shortcuts">
    <kbd>Ctrl</kbd> + <kbd>S</kbd> to save form
    <kbd>Escape</kbd> to cancel
  </div>
  
  <!-- Form content -->
  
  <div class="form-actions">
    <button type="submit" accesskey="s" class="btn btn--primary">
      <u>S</u>ave Device
    </button>
    <button type="button" accesskey="c" class="btn btn--secondary">
      <u>C</u>ancel
    </button>
  </div>
</form>
```

### Screen Reader Support

**Field Descriptions**
```html
<div class="form-group">
  <label for="complex-field" class="form-label">
    Configuration Code
  </label>
  <input 
    type="text" 
    id="complex-field"
    class="input"
    aria-describedby="complex-description complex-format"
  >
  <div id="complex-description" class="form-hint">
    Enter the 8-digit configuration code from the device manual
  </div>
  <div id="complex-format" class="form-hint">
    Format: XXXX-XXXX (numbers and letters)
  </div>
</div>
```

**Progress Indication**
```html
<div class="form-progress" role="progressbar" aria-valuenow="2" aria-valuemin="1" aria-valuemax="4">
  <div class="form-progress-label">
    Step 2 of 4: Location Details
  </div>
  <div class="form-progress-bar">
    <div class="form-progress-fill" style="width: 50%"></div>
  </div>
</div>
```

---

**Implementation Notes:**
- All form components use CSS custom properties for theming
- JavaScript validation enhances but never replaces HTML validation
- Components gracefully degrade without JavaScript
- Touch targets meet 44px minimum requirement
- Color-blind users can distinguish states without color alone

**Related Documentation:**
- [UI Components Overview](UI_COMPONENTS_OVERVIEW.md)
- [Design System](../DESIGN_SYSTEM.md)
- [Accessibility Patterns](../patterns/README.md)