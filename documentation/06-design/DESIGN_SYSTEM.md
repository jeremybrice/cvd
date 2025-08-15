---
title: CVD Design System Documentation
description: Comprehensive design system specification for the CVD vending machine fleet management application
last-updated: 2025-08-12
version: 2.1.0
status: active
dependencies:
  - /css/design-system.css
  - /docs/style-guide.md
  - /icons/svg-sprite.svg
related-files:
  - components/UI_COMPONENTS_OVERVIEW.md
  - user-flows/USER_FLOWS_OVERVIEW.md
  - patterns/README.md
---

# CVD Design System v2.1


## Metadata
- **ID**: 06_DESIGN_DESIGN_SYSTEM
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #data-exchange #debugging #device-management #dex-parser #driver-app #integration #interface #logistics #machine-learning #metrics #mobile #operations #optimization #performance #pwa #quality-assurance #reporting #route-management #security #service-orders #testing #troubleshooting #ui-design #user-experience #vending-machine
- **Intent**: The CVD Design System is a comprehensive visual language and component library optimized for enterprise vending machine fleet management
- **Audience**: managers, end users, architects
- **Related**: USER_FLOWS_OVERVIEW.md, style-guide.md, UI_COMPONENTS_OVERVIEW.md, README.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/06-design/
- **Category**: 06 Design
- **Search Keywords**: ###, (component, (section):, (subsection):, **body, --container-lg:, --container-md:, --container-sm:, --container-xl:, --container-xxl:, --font-bold:, --font-medium:, --font-normal:, --font-semibold:, --icon-2xl:

## Overview

The CVD Design System is a comprehensive visual language and component library optimized for enterprise vending machine fleet management. It prioritizes operational efficiency, data density, and accessibility while maintaining a professional aesthetic suitable for business environments.

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Component Architecture](#component-architecture)
6. [Responsive Design](#responsive-design)
7. [Accessibility Standards](#accessibility-standards)
8. [Icon System](#icon-system)
9. [Motion & Animation](#motion--animation)
10. [Implementation Guidelines](#implementation-guidelines)

## Design Philosophy

### Core Principles

**1. Efficiency First**
- Information hierarchy guides user attention to critical business data
- Workflows optimized for rapid task completion
- Reduced cognitive load through familiar interaction patterns

**2. Enterprise Focus**
- Professional aesthetic suitable for business operations
- High information density without overwhelming users
- Support for wide screens and data-heavy interfaces

**3. Accessibility Always**
- WCAG AA compliance as baseline standard
- Keyboard navigation for all interactive elements
- Color-independent information communication

**4. Consistent Patterns**
- Unified interaction models across all modules
- Predictable component behavior and states
- Systematic approach to layout and spacing

**5. Performance Matters**
- Fast loading and smooth interactions
- Hardware-accelerated animations
- Optimized for real-world business networks

## Color System

### Primary Palette - Brand Blue

Our primary color system centers on a professional blue that conveys trust and reliability while maintaining high contrast for readability.

```css
/* Primary Blue Scale */
--color-primary-50: #e7f3ff;   /* Light backgrounds, subtle highlights */
--color-primary-100: #c2e0ff;  /* Disabled states, very light accents */
--color-primary-200: #99ccff;  /* Light hover states */
--color-primary-300: #66b3ff;  /* Medium accents, borders */
--color-primary-400: #3399ff;  /* Interactive hover states */
--color-primary-500: #006dfe;  /* Main brand color, primary actions */
--color-primary-600: #0057d9;  /* Active states, pressed buttons */
--color-primary-700: #0043b3;  /* Dark accents, headers */
--color-primary-800: #00308c;  /* Very dark accents */
--color-primary-900: #001f66;  /* Darkest shade, text on light */
```

### Neutral Palette - Professional Grays

A carefully calibrated neutral scale providing excellent readability and hierarchy.

```css
/* Neutral Gray Scale */
--color-neutral-0: #ffffff;    /* Pure white, cards, backgrounds */
--color-neutral-50: #f8f9fa;   /* Page backgrounds, subtle areas */
--color-neutral-100: #f1f3f5;  /* Disabled backgrounds, borders */
--color-neutral-200: #e9ecef;  /* Light borders, dividers */
--color-neutral-300: #dee2e6;  /* Standard borders, input borders */
--color-neutral-400: #ced4da;  /* Placeholder text, muted elements */
--color-neutral-500: #adb5bd;  /* Secondary text, icons */
--color-neutral-600: #6c757d;  /* Primary text on light backgrounds */
--color-neutral-700: #495057;  /* Headings, emphasis text */
--color-neutral-800: #343a40;  /* Dark text, high contrast */
--color-neutral-900: #212529;  /* Maximum contrast text */
```

### Semantic Colors - Status Communication

Status colors optimized for business operations and alert visibility.

```css
/* Success - Operations Success */
--color-success: #28a745;        /* Success actions, positive states */
--color-success-bg: #d4edda;     /* Success backgrounds */
--color-success-border: #c3e6cb; /* Success borders */
--color-success-text: #155724;   /* Success text on light */

/* Warning - Caution States */
--color-warning: #ffc107;        /* Warning actions, caution */
--color-warning-bg: #fff3cd;     /* Warning backgrounds */
--color-warning-border: #ffeeba; /* Warning borders */
--color-warning-text: #856404;   /* Warning text */

/* Danger - Critical Actions */
--color-danger: #dc3545;         /* Error states, destructive actions */
--color-danger-bg: #f8d7da;      /* Error backgrounds */
--color-danger-border: #f5c6cb;  /* Error borders */
--color-danger-text: #721c24;    /* Error text */

/* Info - Informational States */
--color-info: #17a2b8;           /* Information, neutral highlights */
--color-info-bg: #d1ecf1;        /* Info backgrounds */
--color-info-border: #bee5eb;    /* Info borders */
--color-info-text: #0c5460;      /* Info text */
```

### Color Usage Guidelines

**Primary Actions**
- Use `--color-primary-500` for main CTAs and interactive elements
- Hover: `--color-primary-600`
- Active/Pressed: `--color-primary-700`
- Disabled: `--color-neutral-400` with 60% opacity

**Text Hierarchy**
- Headings: `--color-neutral-900`
- Primary text: `--color-neutral-700`
- Secondary text: `--color-neutral-600`
- Disabled text: `--color-neutral-400`

**Backgrounds**
- Page background: `--color-neutral-50`
- Card/modal backgrounds: `--color-neutral-0`
- Input backgrounds: `--color-neutral-0`
- Disabled backgrounds: `--color-neutral-100`

**Borders & Dividers**
- Standard borders: `--color-neutral-300`
- Subtle dividers: `--color-neutral-200`
- Focus borders: `--color-primary-500`

## Typography

### Font Families

Our typography system uses system font stacks for optimal performance and native feel across platforms.

```css
/* Primary Font Stack - UI Text */
--font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
             'Helvetica Neue', Arial, sans-serif;

/* Monospace Stack - Code & Data */
--font-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', 
             Consolas, 'Courier New', monospace;
```

### Type Scale

A mathematically-scaled typography system optimized for business applications.

```css
/* Font Sizes */
--text-xs: 0.75rem;    /* 12px - Captions, metadata, timestamps */
--text-sm: 0.875rem;   /* 14px - Secondary text, table data */
--text-base: 1rem;     /* 16px - Primary body text, form inputs */
--text-lg: 1.125rem;   /* 18px - Emphasized text, subheadings */
--text-xl: 1.25rem;    /* 20px - Card titles, section headings */
--text-2xl: 1.5rem;    /* 24px - Page headings, modal titles */
--text-3xl: 1.875rem;  /* 30px - Dashboard titles, major headings */
--text-4xl: 2.25rem;   /* 36px - Landing page headings, hero text */

/* Font Weights */
--font-normal: 400;    /* Body text, default weight */
--font-medium: 500;    /* Emphasized text, button labels */
--font-semibold: 600;  /* Headings, important labels */
--font-bold: 700;      /* High emphasis, navigation active states */

/* Line Heights */
--leading-tight: 1.25;   /* Dense layouts, data tables */
--leading-normal: 1.5;   /* Standard reading text */
--leading-relaxed: 1.75; /* Marketing copy, help text */
```

### Typography Guidelines

**Headings Hierarchy**
- H1 (Page Title): `--text-3xl`, `--font-bold`, `--color-neutral-900`
- H2 (Section): `--text-2xl`, `--font-semibold`, `--color-neutral-800`
- H3 (Subsection): `--text-xl`, `--font-semibold`, `--color-neutral-700`
- H4 (Component Title): `--text-lg`, `--font-medium`, `--color-neutral-700`

**Body Text**
- Primary: `--text-base`, `--font-normal`, `--color-neutral-700`
- Secondary: `--text-sm`, `--font-normal`, `--color-neutral-600`
- Caption: `--text-xs`, `--font-normal`, `--color-neutral-500`

**Interactive Elements**
- Button text: `--text-base`, `--font-medium`
- Link text: `--text-base`, `--font-normal`, `--color-primary-500`
- Form labels: `--text-sm`, `--font-medium`, `--color-neutral-700`

## Spacing & Layout

### Base Unit System

CVD uses a 4px base unit for consistent spatial rhythm throughout the interface.

```css
/* Spacing Scale (4px base) */
--space-xs: 4px;     /* Tight spacing, related elements */
--space-sm: 8px;     /* Internal component padding */
--space-md: 16px;    /* Standard element spacing */
--space-lg: 24px;    /* Section spacing, card padding */
--space-xl: 32px;    /* Major section breaks */
--space-xxl: 48px;   /* Page-level spacing */
--space-xxxl: 64px;  /* Hero sections, landing pages */
```

### Container System

CVD employs multiple container widths optimized for different content types and workflows.

```css
/* Container Widths */
--container-sm: 640px;    /* Mobile layouts */
--container-md: 768px;    /* Tablets, forms */
--container-lg: 1024px;   /* Standard desktop */
--container-xl: 1280px;   /* Default container */
--container-xxl: 1500px;  /* Enterprise layouts */

/* Specialized Containers */
.container--narrow { max-width: 768px; }     /* Forms, settings */
.container--default { max-width: 1280px; }   /* General content */
.container--dashboard { max-width: 1440px; } /* Dashboard layouts */
.container--enterprise { max-width: 1600px; } /* Data-heavy pages */
.container--fluid { max-width: 100%; }       /* Full-width layouts */
```

### Grid System

A flexible CSS Grid-based layout system for component arrangement.

```css
/* Base Grid */
.grid {
  display: grid;
  gap: var(--space-md);
}

/* Grid Variants */
.grid--2 { grid-template-columns: repeat(2, 1fr); }
.grid--3 { grid-template-columns: repeat(3, 1fr); }
.grid--4 { grid-template-columns: repeat(4, 1fr); }
.grid--auto { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }

/* Responsive Grid */
@media (max-width: 768px) {
  .grid--2, .grid--3, .grid--4 {
    grid-template-columns: 1fr;
  }
}
```

## Component Architecture

### Design Token Structure

All components utilize our systematic design tokens for consistency and maintainability.

```css
/* Component-Specific Tokens */
/* Buttons */
--btn-padding-x: var(--space-md);
--btn-padding-y: var(--space-sm);
--btn-font-weight: var(--font-medium);
--btn-radius: var(--radius-md);
--btn-min-height: 44px; /* Touch target compliance */

/* Form Inputs */
--input-padding-x: var(--space-md);
--input-padding-y: var(--space-sm);
--input-border-color: var(--color-neutral-300);
--input-focus-border: var(--color-primary-500);
--input-radius: var(--radius-md);
--input-min-height: 44px;

/* Cards */
--card-padding: var(--space-lg);
--card-radius: var(--radius-lg);
--card-shadow: var(--shadow-sm);
--card-border-color: var(--color-neutral-200);

/* Data Tables */
--table-cell-padding: var(--space-md);
--table-border-color: var(--color-neutral-200);
--table-header-bg: var(--color-neutral-50);
--table-stripe-bg: var(--color-neutral-25);
```

### Border Radius Scale

```css
--radius-sm: 2px;      /* Subtle rounding, small elements */
--radius-md: 4px;      /* Standard radius, buttons, inputs */
--radius-lg: 8px;      /* Cards, panels, containers */
--radius-xl: 12px;     /* Modals, prominent elements */
--radius-full: 9999px; /* Pills, badges, circular elements */
```

### Shadow System

Depth hierarchy through carefully calibrated shadows.

```css
--shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);         /* Subtle depth */
--shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1),           /* Cards, buttons */
             0 1px 2px 0 rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1),        /* Dropdowns, tooltips */
             0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1),      /* Modals, popovers */
             0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1),      /* Large modals */
             0 10px 10px -5px rgba(0, 0, 0, 0.04);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);   /* Maximum depth */
```

## Responsive Design

### Breakpoint Strategy

CVD's responsive system prioritizes business workflows and modern enterprise hardware.

```css
/* Mobile First Breakpoints */
/* Base: 0-767px (Mobile) */
/* Default styles optimized for mobile */

/* Tablet: 768px+ */
@media (min-width: 768px) {
  /* Two-column layouts, hybrid interactions */
}

/* Desktop: 1024px+ */
@media (min-width: 1024px) {
  /* Standard desktop, mouse optimizations */
}

/* Large Desktop: 1280px+ */
@media (min-width: 1280px) {
  /* Dashboard layouts, multi-column data */
}

/* Enterprise Desktop: 1440px+ */
@media (min-width: 1440px) {
  /* Maximum data visibility, enterprise workflows */
}
```

### Container Responsive Behavior

```css
/* Adaptive Container System */
.container--adaptive {
  max-width: min(100vw - 2rem, 1600px);
  margin: 0 auto;
  padding: 0 var(--space-md);
}

/* Breakpoint-Specific Containers */
@media (max-width: 1439px) {
  .container--enterprise {
    max-width: 1280px; /* Fallback for smaller screens */
  }
}

@media (max-width: 1279px) {
  .container--dashboard {
    max-width: 1024px;
  }
}

@media (max-width: 767px) {
  .container--narrow,
  .container--default,
  .container--dashboard,
  .container--enterprise {
    max-width: 100%;
    padding: 0 var(--space-sm);
  }
}
```

## Accessibility Standards

### WCAG Compliance

CVD maintains WCAG AA compliance as a baseline with enhanced standards for critical interfaces.

**Color Contrast Requirements:**
- Normal text: 4.5:1 minimum
- Large text (≥18px): 3:1 minimum
- UI components: 3:1 minimum
- Focus indicators: 3:1 minimum
- Critical interfaces: 7:1 preferred

### Focus Management

```css
/* Enhanced Focus Styles */
:focus-visible {
  outline: var(--focus-width) solid var(--focus-color);
  outline-offset: var(--focus-offset);
}

/* Remove focus for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}

/* Focus Variables */
--focus-color: var(--color-primary-500);
--focus-offset: 2px;
--focus-width: 2px;
```

### Screen Reader Support

```css
/* Screen Reader Only Content */
.sr-only {
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

/* Skip Navigation */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary-500);
  color: var(--color-neutral-0);
  padding: var(--space-sm) var(--space-md);
  text-decoration: none;
  z-index: var(--z-tooltip);
  border-radius: 0 0 var(--radius-md) 0;
}

.skip-link:focus {
  top: 0;
}
```

### Touch Target Compliance

```css
/* Minimum Touch Target Sizes */
--touch-target-min: 44px; /* iOS/Android requirement */

.btn,
.nav-item,
.form-input,
.interactive-element {
  min-height: var(--touch-target-min);
  min-width: var(--touch-target-min);
}
```

## Icon System

### SVG Icon Architecture

CVD uses a comprehensive SVG sprite system for scalable, accessible iconography.

```css
/* Icon Base Styles */
.icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: var(--icon-md);
  height: var(--icon-md);
  fill: currentColor;
  flex-shrink: 0;
  vertical-align: middle;
}

/* Icon Size Variants */
--icon-xs: 12px;   /* Small indicators, table icons */
--icon-sm: 16px;   /* Button icons, form icons */
--icon-md: 20px;   /* Default icon size */
--icon-lg: 24px;   /* Navigation icons, headers */
--icon-xl: 32px;   /* Large buttons, features */
--icon-2xl: 48px;  /* Hero icons, empty states */
```

### Business Icon Categories

**Navigation & Interface**
- Dashboard: `#icon-chart-bar`
- Devices: `#icon-server`
- Routes: `#icon-truck`
- Service Orders: `#icon-clipboard-list`
- Users: `#icon-user`
- Settings: `#icon-cog`

**Actions & Controls**
- Add: `#icon-plus`
- Edit: `#icon-pencil`
- Delete: `#icon-trash`
- Save: `#icon-check`
- Cancel: `#icon-x`
- Refresh: `#icon-refresh`
- Search: `#icon-search`
- Filter: `#icon-filter`

**Status & Communication**
- Success: `#icon-check-circle`
- Warning: `#icon-exclamation-triangle`
- Error: `#icon-x-circle`
- Info: `#icon-info-circle`
- Loading: `#icon-spinner`

### Icon Usage Guidelines

```html
<!-- Basic Icon Usage -->
<svg class="icon icon--md icon--primary">
  <use href="#icon-chart-bar"></use>
</svg>

<!-- Button with Icon -->
<button class="btn btn--primary">
  <svg class="icon icon--sm" aria-hidden="true">
    <use href="#icon-plus"></use>
  </svg>
  Add Device
</button>

<!-- Icon-only Button (Accessible) -->
<button class="btn btn--ghost" aria-label="Edit device">
  <svg class="icon" aria-hidden="true">
    <use href="#icon-pencil"></use>
  </svg>
</button>
```

## Motion & Animation

### Animation Principles

1. **Purpose-Driven**: Every animation serves a functional purpose
2. **Performance-First**: 60fps minimum using CSS transforms and opacity
3. **Accessible**: Respects `prefers-reduced-motion`
4. **Consistent**: Standardized timing and easing functions

### Timing & Easing

```css
/* Duration Scale */
--duration-instant: 0ms;    /* Disable animations when needed */
--duration-fast: 150ms;     /* Micro-interactions, hover states */
--duration-base: 250ms;     /* Standard transitions */
--duration-slow: 350ms;     /* Complex transitions */
--duration-slower: 500ms;   /* Page transitions, modals */

/* Easing Functions */
--ease-linear: linear;
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Reduced Motion Support

```css
/* Accessibility: Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: var(--duration-instant) !important;
    animation-iteration-count: 1 !important;
    transition-duration: var(--duration-instant) !important;
    scroll-behavior: auto !important;
  }
}
```

### Standard Animation Patterns

```css
/* Fade In */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide Up */
@keyframes slideUp {
  from {
    transform: translateY(10px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Scale In */
@keyframes scaleIn {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

/* Spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Shimmer Loading */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

## Implementation Guidelines

### CSS Architecture

**File Organization:**
```
css/
├── design-system.css      # Main design system file
├── components/
│   ├── buttons.css       # Button components
│   ├── forms.css         # Form components
│   ├── tables.css        # Data table styles
│   ├── navigation.css    # Navigation components
│   └── modals.css        # Modal and dialog styles
├── utilities/
│   ├── spacing.css       # Spacing utilities
│   ├── typography.css    # Text utilities
│   └── responsive.css    # Responsive utilities
└── pages/
    ├── dashboard.css     # Dashboard-specific styles
    ├── forms.css         # Form page styles
    └── mobile.css        # Mobile app styles
```

### Component Development Checklist

**For Each New Component:**
- [ ] Use design tokens consistently
- [ ] Include all interactive states (hover, focus, active, disabled)
- [ ] Implement keyboard navigation support
- [ ] Add appropriate ARIA attributes
- [ ] Verify color contrast ratios (4.5:1 minimum)
- [ ] Test responsive behavior across breakpoints
- [ ] Include loading and error states where applicable
- [ ] Document usage examples and guidelines
- [ ] Test with screen readers
- [ ] Validate performance impact

### Page Implementation Standards

**Required Elements for Each Page:**
- [ ] Skip navigation link
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] Semantic HTML structure
- [ ] Appropriate container class selection
- [ ] Focus management for dynamic content
- [ ] Loading states for async operations
- [ ] Error handling and user feedback
- [ ] Breadcrumb navigation where applicable
- [ ] Responsive layout testing
- [ ] Accessibility audit completion

### Container Selection Guide

| Page Type | Container Class | Use Case |
|-----------|----------------|----------|
| Login, Profile | `container--narrow` | Form-focused interfaces |
| Dashboard, Analytics | `container--dashboard` | Mixed content with widgets |
| Data Tables, Reports | `container--enterprise` | Maximum data visibility |
| Standard Pages | `container--default` | General purpose content |
| Maps, Custom Views | `container--fluid` | Full-width layouts |

### Performance Optimization

**CSS Performance:**
- Use CSS custom properties for dynamic values
- Minimize selector specificity
- Avoid expensive selectors (`*`, `:nth-child`)
- Implement `will-change` sparingly
- Use `transform` and `opacity` for animations

**Loading Strategy:**
- Inline critical CSS for above-the-fold content
- Preload important fonts and assets
- Lazy load non-critical CSS
- Optimize SVG sprites for HTTP/2

## Related Documentation

- [UI Components Overview](components/UI_COMPONENTS_OVERVIEW.md) - Detailed component specifications
- [User Flows Documentation](user-flows/USER_FLOWS_OVERVIEW.md) - Complete user journey guides
- [Design Patterns](patterns/README.md) - Common layout and interaction patterns
- [Style Guide](/docs/style-guide.md) - Original style guide reference
- [CSS Implementation](/css/design-system.css) - CSS design token definitions

---

**Version History:**
- v2.1.0 (2025-08-12): Added comprehensive responsive containers, enhanced accessibility standards
- v2.0.0 (2025-01-15): Major overhaul with systematic design tokens and component architecture
- v1.0.0 (2024-12-01): Initial design system documentation

**Maintained by:** CVD Design Team  
**Last Review:** 2025-08-12  
**Next Review:** 2025-11-12