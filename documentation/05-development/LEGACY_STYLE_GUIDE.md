# CVD Application Style Guide v2.0

## Design Philosophy

The CVD design system prioritizes efficiency, clarity, and accessibility. Our interface should empower users to manage vending operations with minimal cognitive load while maintaining professional aesthetics suitable for enterprise use.

### Core Principles
1. **Clarity First**: Information hierarchy guides user attention
2. **Consistent Patterns**: Familiar interactions across all modules  
3. **Responsive by Default**: Mobile-first with desktop optimization
4. **Accessible Always**: WCAG AA compliance as baseline
5. **Performance Matters**: Fast interactions build user trust

---

## Design Tokens

### Spacing System
Based on 4px unit for consistent rhythm:

```css
:root {
  --space-xs: 4px;    /* Tight spacing between related elements */
  --space-sm: 8px;    /* Internal component padding */
  --space-md: 16px;   /* Standard element spacing */
  --space-lg: 24px;   /* Section spacing */
  --space-xl: 32px;   /* Major section breaks */
  --space-xxl: 48px;  /* Page-level spacing */
  --space-xxxl: 64px; /* Hero sections */
}
```

### Color System

#### Brand Colors
```css
:root {
  /* Primary Palette */
  --color-primary-50: #e7f3ff;
  --color-primary-100: #c2e0ff;
  --color-primary-200: #99ccff;
  --color-primary-300: #66b3ff;
  --color-primary-400: #3399ff;
  --color-primary-500: #006dfe; /* Main brand blue */
  --color-primary-600: #0057d9;
  --color-primary-700: #0043b3;
  --color-primary-800: #00308c;
  --color-primary-900: #001f66;
  
  /* Neutral Palette */
  --color-neutral-0: #ffffff;
  --color-neutral-50: #f8f9fa;
  --color-neutral-100: #f1f3f5;
  --color-neutral-200: #e9ecef;
  --color-neutral-300: #dee2e6;
  --color-neutral-400: #ced4da;
  --color-neutral-500: #adb5bd;
  --color-neutral-600: #6c757d;
  --color-neutral-700: #495057;
  --color-neutral-800: #343a40;
  --color-neutral-900: #212529;
  
  /* Semantic Colors */
  --color-success: #28a745;
  --color-success-bg: #d4edda;
  --color-success-border: #c3e6cb;
  
  --color-warning: #ffc107;
  --color-warning-bg: #fff3cd;
  --color-warning-border: #ffeeba;
  
  --color-danger: #dc3545;
  --color-danger-bg: #f8d7da;
  --color-danger-border: #f5c6cb;
  
  --color-info: #17a2b8;
  --color-info-bg: #d1ecf1;
  --color-info-border: #bee5eb;
}
```

#### Color Usage Guidelines
- **Primary actions**: Use `--color-primary-500`
- **Hover states**: Darken by 100 (e.g., primary-600 for primary-500 hover)
- **Disabled states**: Use neutral-400 with 0.6 opacity
- **Backgrounds**: Neutral-50 for pages, white for cards
- **Text**: Neutral-900 for headings, neutral-700 for body
- **Borders**: Neutral-300 for standard, neutral-200 for subtle

### Typography Scale

```css
:root {
  /* Font Families */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
               'Helvetica Neue', Arial, sans-serif;
  --font-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', monospace;
  
  /* Font Sizes */
  --text-xs: 0.75rem;    /* 12px - Captions, labels */
  --text-sm: 0.875rem;   /* 14px - Secondary text */
  --text-base: 1rem;     /* 16px - Body text */
  --text-lg: 1.125rem;   /* 18px - Emphasized body */
  --text-xl: 1.25rem;    /* 20px - Small headings */
  --text-2xl: 1.5rem;    /* 24px - Section headings */
  --text-3xl: 1.875rem;  /* 30px - Page headings */
  --text-4xl: 2.25rem;   /* 36px - Hero headings */
  
  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### Border Radius

```css
:root {
  --radius-sm: 2px;    /* Subtle rounding */
  --radius-md: 4px;    /* Default radius */
  --radius-lg: 8px;    /* Cards, containers */
  --radius-xl: 12px;   /* Modals, prominent elements */
  --radius-full: 9999px; /* Pills, circular elements */
}
```

### Shadows

```css
:root {
  --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
```

### Animation

```css
:root {
  /* Durations */
  --duration-fast: 150ms;
  --duration-base: 250ms;
  --duration-slow: 350ms;
  --duration-slower: 500ms;
  
  /* Easings */
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

---

## Icon System

### SVG Icon Guidelines

The CVD application uses a comprehensive SVG icon system for all visual indicators, replacing emoji usage for professional, accessible, and scalable iconography.

#### Icon Specifications
```css
:root {
  /* Icon sizes */
  --icon-xs: 12px;
  --icon-sm: 16px;
  --icon-md: 20px;
  --icon-lg: 24px;
  --icon-xl: 32px;
  --icon-2xl: 48px;
  
  /* Icon colors */
  --icon-primary: var(--color-primary-500);
  --icon-secondary: var(--color-neutral-600);
  --icon-muted: var(--color-neutral-400);
  --icon-success: var(--color-success);
  --icon-warning: var(--color-warning);
  --icon-danger: var(--color-danger);
}
```

#### Base Icon Component
```css
.icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: var(--icon-md);
  height: var(--icon-md);
  fill: currentColor;
  flex-shrink: 0;
}

.icon--xs { width: var(--icon-xs); height: var(--icon-xs); }
.icon--sm { width: var(--icon-sm); height: var(--icon-sm); }
.icon--lg { width: var(--icon-lg); height: var(--icon-lg); }
.icon--xl { width: var(--icon-xl); height: var(--icon-xl); }
.icon--2xl { width: var(--icon-2xl); height: var(--icon-2xl); }

.icon--primary { color: var(--icon-primary); }
.icon--secondary { color: var(--icon-secondary); }
.icon--muted { color: var(--icon-muted); }
.icon--success { color: var(--icon-success); }
.icon--warning { color: var(--icon-warning); }
.icon--danger { color: var(--icon-danger); }
```

#### Core Business Icons

**Navigation & Interface**
- **Dashboard**: `<svg class="icon"><use href="#icon-chart-bar"></use></svg>`
- **Devices/Equipment**: `<svg class="icon"><use href="#icon-server"></use></svg>`
- **Routes**: `<svg class="icon"><use href="#icon-truck"></use></svg>`
- **Service Orders**: `<svg class="icon"><use href="#icon-clipboard-list"></use></svg>`
- **User Profile**: `<svg class="icon"><use href="#icon-user"></use></svg>`
- **Settings**: `<svg class="icon"><use href="#icon-cog"></use></svg>`
- **Menu (Hamburger)**: `<svg class="icon"><use href="#icon-menu"></use></svg>`

**Actions & States**
- **Add/Create**: `<svg class="icon"><use href="#icon-plus"></use></svg>`
- **Edit**: `<svg class="icon"><use href="#icon-pencil"></use></svg>`
- **Delete**: `<svg class="icon"><use href="#icon-trash"></use></svg>`
- **Save**: `<svg class="icon"><use href="#icon-check"></use></svg>`
- **Cancel**: `<svg class="icon"><use href="#icon-x"></use></svg>`
- **Sync/Refresh**: `<svg class="icon"><use href="#icon-refresh"></use></svg>`
- **Search**: `<svg class="icon"><use href="#icon-search"></use></svg>`
- **Filter**: `<svg class="icon"><use href="#icon-filter"></use></svg>`

**Data & Analytics**
- **Revenue Trend Up**: `<svg class="icon"><use href="#icon-trending-up"></use></svg>`
- **Revenue Trend Down**: `<svg class="icon"><use href="#icon-trending-down"></use></svg>`
- **Analytics**: `<svg class="icon"><use href="#icon-chart-line"></use></svg>`
- **Calendar**: `<svg class="icon"><use href="#icon-calendar"></use></svg>`
- **Clock**: `<svg class="icon"><use href="#icon-clock"></use></svg>`

**Status Indicators**
- **Success/Complete**: `<svg class="icon icon--success"><use href="#icon-check-circle"></use></svg>`
- **Warning/Alert**: `<svg class="icon icon--warning"><use href="#icon-exclamation-triangle"></use></svg>`
- **Error/Failed**: `<svg class="icon icon--danger"><use href="#icon-x-circle"></use></svg>`
- **Information**: `<svg class="icon icon--primary"><use href="#icon-info-circle"></use></svg>`
- **Online/Active**: `<svg class="icon icon--success"><use href="#icon-signal"></use></svg>`

**Table & Sorting**
- **Sort Ascending**: `<svg class="icon"><use href="#icon-chevron-up"></use></svg>`
- **Sort Descending**: `<svg class="icon"><use href="#icon-chevron-down"></use></svg>`
- **Unsorted**: `<svg class="icon"><use href="#icon-selector"></use></svg>`

#### SVG Sprite Implementation
```html
<!-- Include at the beginning of each page -->
<svg style="display: none;" aria-hidden="true">
  <defs>
    <!-- Dashboard/Analytics -->
    <symbol id="icon-chart-bar" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
    </symbol>
    
    <!-- Device/Server -->
    <symbol id="icon-server" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"/>
    </symbol>
    
    <!-- Truck/Routes -->
    <symbol id="icon-truck" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4"/>
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 5H8a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2z"/>
    </symbol>
    
    <!-- Clipboard/Orders -->
    <symbol id="icon-clipboard-list" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/>
    </symbol>
    
    <!-- User Profile -->
    <symbol id="icon-user" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
    </symbol>
    
    <!-- Settings/Cog -->
    <symbol id="icon-cog" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
    </symbol>
    
    <!-- Menu -->
    <symbol id="icon-menu" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
    </symbol>
    
    <!-- Trending Up -->
    <symbol id="icon-trending-up" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
    </symbol>
    
    <!-- Check Circle (Success) -->
    <symbol id="icon-check-circle" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
    </symbol>
    
    <!-- Refresh/Sync -->
    <symbol id="icon-refresh" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
    </symbol>
    
    <!-- Chevron Up (Sort Ascending) -->
    <symbol id="icon-chevron-up" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
    </symbol>
    
    <!-- Chevron Down (Sort Descending) -->
    <symbol id="icon-chevron-down" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
    </symbol>
  </defs>
</svg>
```

#### Usage Examples
```html
<!-- Navigation with icons -->
<nav class="bottom-nav">
  <a href="#dashboard" class="nav-item active">
    <svg class="icon nav-icon"><use href="#icon-chart-bar"></use></svg>
    <span class="nav-label">Dashboard</span>
  </a>
  <a href="#routes" class="nav-item">
    <svg class="icon nav-icon"><use href="#icon-truck"></use></svg>
    <span class="nav-label">Routes</span>
  </a>
</nav>

<!-- Action buttons with icons -->
<button class="btn btn--primary">
  <svg class="icon icon--sm"><use href="#icon-refresh"></use></svg>
  Sync Data
</button>

<!-- Status indicators -->
<div class="status-badge">
  <svg class="icon icon--sm icon--success"><use href="#icon-check-circle"></use></svg>
  Delivered
</div>

<!-- Table sorting headers -->
<th class="sortable-header" data-column="name">
  Device Name
  <svg class="icon icon--xs table__sort-icon"><use href="#icon-chevron-down"></use></svg>
</th>
```

#### Accessibility Requirements
- All icons must include appropriate ARIA labels when used standalone
- Icons used decoratively should have `aria-hidden="true"`
- Interactive icons must have sufficient color contrast (3:1 minimum)
- Icon meanings should be reinforced with text labels where possible

```html
<!-- Accessible icon button -->
<button class="btn btn--ghost" aria-label="Refresh data">
  <svg class="icon" aria-hidden="true"><use href="#icon-refresh"></use></svg>
  <span class="sr-only">Refresh data</span>
</button>

<!-- Icon with visible label -->
<button class="btn btn--primary">
  <svg class="icon icon--sm" aria-hidden="true"><use href="#icon-truck"></use></svg>
  Start Route
</button>
```

#### Migration from Emoji
The following emoji characters should be replaced with their SVG equivalents:

| Emoji | Context | SVG Replacement |
|-------|---------|-----------------|
| 📈 | Revenue trends, analytics | `#icon-trending-up` |
| 🌅 | Welcome messages | `#icon-sun` (add to sprite) |
| ↗ | Metric trends | `#icon-trending-up` |
| ✓ | Success states, delivered items | `#icon-check-circle` |
| 🔄 | Sync/refresh actions | `#icon-refresh` |
| ☰ | Menu buttons | `#icon-menu` |
| 📊 | Dashboard navigation | `#icon-chart-bar` |
| 🚚 | Routes navigation | `#icon-truck` |
| 📋 | Service orders | `#icon-clipboard-list` |
| 👤 | User profile | `#icon-user` |
| ▶️ | Play/start actions | `#icon-play` (add to sprite) |

---

## Component Library

### Layout Components

#### Container

The CVD container system uses a **hybrid width strategy** optimized for enterprise vending machine management workflows. Different container types serve different content patterns and user tasks.

```css
.container {
  width: 100%;
  max-width: 1280px; /* Default for mixed content */
  margin: 0 auto;
  padding: 0 var(--space-md);
}

.container--enterprise {
  max-width: 1600px; /* Data-heavy pages: tables, analytics */
}

.container--dashboard {
  max-width: 1440px; /* Dashboard layouts with widgets */
}

.container--fluid {
  max-width: 100%; /* Full width when needed */
}

.container--adaptive {
  max-width: min(100vw - 2rem, 1600px); /* Responsive with padding */
}

.container--narrow {
  max-width: 768px; /* Forms and focused content */
}
```

#### Container Usage Guidelines

**Enterprise Container (1600px)** - Use for:
- Route scheduling with interactive maps
- Device management tables
- Asset/Product sales analytics
- Database viewer
- Any page where maximum data visibility improves workflow

**Dashboard Container (1440px)** - Use for:
- Home dashboard with multiple widgets
- Service orders (mixed table/form content)
- Analytics pages with charts and summaries

**Default Container (1280px)** - Use for:
- General purpose pages
- Mixed content layouts
- Legacy page migrations

**Narrow Container (768px)** - Use for:
- User management forms
- Profile settings
- Login/authentication pages
- Device configuration forms
- Any form-heavy interface

**Fluid Container (100%)** - Use for:
- Full-screen map interfaces
- Custom layouts requiring edge-to-edge content
- Specialized data visualization

#### Grid System
```css
.grid {
  display: grid;
  gap: var(--space-md);
}

.grid--2 { grid-template-columns: repeat(2, 1fr); }
.grid--3 { grid-template-columns: repeat(3, 1fr); }
.grid--4 { grid-template-columns: repeat(4, 1fr); }

@media (max-width: 768px) {
  .grid--2,
  .grid--3,
  .grid--4 {
    grid-template-columns: 1fr;
  }
}
```

### Navigation

#### Primary Navigation
```css
.nav {
  height: 60px;
  background: var(--color-primary-500);
  box-shadow: var(--shadow-md);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav__brand {
  height: 40px;
  margin: 10px 0;
}

.nav__menu {
  display: flex;
  align-items: center;
  height: 100%;
  gap: var(--space-xs);
}

.nav__item {
  padding: var(--space-sm) var(--space-md);
  color: var(--color-neutral-0);
  border-radius: var(--radius-md);
  transition: background var(--duration-fast) var(--ease-out);
}

.nav__item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav__item--active {
  background: rgba(255, 255, 255, 0.2);
}
```

#### Breadcrumbs
```css
.breadcrumbs {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) 0;
  font-size: var(--text-sm);
  color: var(--color-neutral-600);
}

.breadcrumbs__separator {
  color: var(--color-neutral-400);
}

.breadcrumbs__link {
  color: var(--color-primary-500);
  text-decoration: none;
}

.breadcrumbs__current {
  color: var(--color-neutral-700);
  font-weight: var(--font-medium);
}
```

### Buttons

#### Base Button
```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  line-height: var(--leading-normal);
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  white-space: nowrap;
  user-select: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}
```

#### Button Variants
```css
.btn--primary {
  background: var(--color-primary-500);
  color: var(--color-neutral-0);
  border-color: var(--color-primary-500);
}

.btn--primary:hover:not(:disabled) {
  background: var(--color-primary-600);
  border-color: var(--color-primary-600);
}

.btn--secondary {
  background: var(--color-neutral-0);
  color: var(--color-neutral-700);
  border-color: var(--color-neutral-300);
}

.btn--secondary:hover:not(:disabled) {
  background: var(--color-neutral-50);
  border-color: var(--color-neutral-400);
}

.btn--danger {
  background: var(--color-danger);
  color: var(--color-neutral-0);
  border-color: var(--color-danger);
}

.btn--ghost {
  background: transparent;
  color: var(--color-primary-500);
  border-color: transparent;
}
```

#### Button Sizes
```css
.btn--sm {
  padding: var(--space-xs) var(--space-sm);
  font-size: var(--text-sm);
}

.btn--lg {
  padding: var(--space-md) var(--space-lg);
  font-size: var(--text-lg);
}

.btn--block {
  width: 100%;
}
```

### Forms

#### Input Fields
```css
.input {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--color-neutral-900);
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-300);
  border-radius: var(--radius-md);
  transition: border-color var(--duration-fast) var(--ease-out);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px rgba(0, 109, 254, 0.1);
}

.input:disabled {
  background: var(--color-neutral-100);
  cursor: not-allowed;
}

.input--error {
  border-color: var(--color-danger);
}

.input--error:focus {
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
}
```

#### Form Groups
```css
.form-group {
  margin-bottom: var(--space-lg);
}

.form-label {
  display: block;
  margin-bottom: var(--space-xs);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-neutral-700);
}

.form-label--required::after {
  content: " *";
  color: var(--color-danger);
}

.form-hint {
  margin-top: var(--space-xs);
  font-size: var(--text-sm);
  color: var(--color-neutral-600);
}

.form-error {
  margin-top: var(--space-xs);
  font-size: var(--text-sm);
  color: var(--color-danger);
}
```

#### Select Dropdowns
```css
.select {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  padding-right: var(--space-xl);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--color-neutral-900);
  background: var(--color-neutral-0);
  background-image: url("data:image/svg+xml,%3csvg width='20' height='20' fill='none' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='m6 8 4 4 4-4' stroke='%23374151' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right var(--space-sm) center;
  background-size: 20px;
  border: 1px solid var(--color-neutral-300);
  border-radius: var(--radius-md);
  appearance: none;
  cursor: pointer;
}
```

### Cards

```css
.card {
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.card__header {
  padding: var(--space-lg);
  border-bottom: 1px solid var(--color-neutral-200);
}

.card__title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-neutral-900);
}

.card__body {
  padding: var(--space-lg);
}

.card__footer {
  padding: var(--space-lg);
  background: var(--color-neutral-50);
  border-top: 1px solid var(--color-neutral-200);
}
```

### Tables

#### Base Table
```css
.table {
  width: 100%;
  background: var(--color-neutral-0);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.table__wrapper {
  overflow-x: auto;
}

.table thead {
  background: var(--color-neutral-50);
}

.table th {
  padding: var(--space-md);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-neutral-700);
  text-align: left;
  white-space: nowrap;
  border-bottom: 2px solid var(--color-neutral-200);
}

.table td {
  padding: var(--space-md);
  font-size: var(--text-base);
  color: var(--color-neutral-800);
  border-bottom: 1px solid var(--color-neutral-100);
}

.table tbody tr:hover {
  background: var(--color-neutral-50);
}

.table tbody tr:last-child td {
  border-bottom: none;
}
```

#### Sortable Headers
```css
.table__sort {
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.table__sort:hover {
  color: var(--color-primary-500);
}

.table__sort-icon {
  display: inline-flex;
  width: var(--icon-xs);
  height: var(--icon-xs);
  margin-left: var(--space-xs);
  transition: transform var(--duration-fast) var(--ease-out);
  opacity: 0.5;
}

.table__sort:hover .table__sort-icon {
  opacity: 1;
}

.table__sort--asc .table__sort-icon {
  transform: rotate(180deg);
}

.table__sort--active {
  color: var(--color-primary-500);
}

.table__sort--active .table__sort-icon {
  opacity: 1;
}
```

### Modals

```css
.modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-md);
}

.modal__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
}

.modal__content {
  position: relative;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  background: var(--color-neutral-0);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
}

.modal__header {
  padding: var(--space-lg);
  border-bottom: 1px solid var(--color-neutral-200);
}

.modal__title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-neutral-900);
}

.modal__body {
  flex: 1;
  padding: var(--space-lg);
  overflow-y: auto;
}

.modal__footer {
  padding: var(--space-lg);
  border-top: 1px solid var(--color-neutral-200);
  display: flex;
  gap: var(--space-sm);
  justify-content: flex-end;
}
```

### Badges

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-xs) var(--space-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  line-height: 1;
  border-radius: var(--radius-full);
  white-space: nowrap;
}

.badge--primary {
  background: var(--color-primary-100);
  color: var(--color-primary-700);
}

.badge--success {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.badge--warning {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}

.badge--danger {
  background: var(--color-danger-bg);
  color: var(--color-danger);
}

.badge--neutral {
  background: var(--color-neutral-200);
  color: var(--color-neutral-700);
}
```

### Alerts

```css
.alert {
  padding: var(--space-md);
  border-radius: var(--radius-md);
  border: 1px solid;
  display: flex;
  gap: var(--space-md);
  align-items: flex-start;
}

.alert__icon {
  flex-shrink: 0;
  width: var(--icon-md);
  height: var(--icon-md);
  color: currentColor;
}

.alert__content {
  flex: 1;
}

.alert__title {
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-xs);
}

.alert--info {
  background: var(--color-info-bg);
  border-color: var(--color-info-border);
  color: var(--color-info);
}

.alert--success {
  background: var(--color-success-bg);
  border-color: var(--color-success-border);
  color: var(--color-success);
}

.alert--warning {
  background: var(--color-warning-bg);
  border-color: var(--color-warning-border);
  color: var(--color-warning);
}

.alert--danger {
  background: var(--color-danger-bg);
  border-color: var(--color-danger-border);
  color: var(--color-danger);
}
```

### Loading States

```css
.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-neutral-300);
  border-top-color: var(--color-primary-500);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner--sm {
  width: 16px;
  height: 16px;
}

.spinner--lg {
  width: 32px;
  height: 32px;
  border-width: 3px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-neutral-200) 25%,
    var(--color-neutral-100) 50%,
    var(--color-neutral-200) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-md);
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

### Toast Notifications

```css
.toast-container {
  position: fixed;
  top: var(--space-lg);
  right: var(--space-lg);
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  pointer-events: none;
}

.toast {
  background: var(--color-neutral-0);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: var(--space-md);
  min-width: 300px;
  max-width: 500px;
  display: flex;
  align-items: center;
  gap: var(--space-md);
  pointer-events: auto;
  animation: slideIn var(--duration-base) var(--ease-out);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast__icon {
  flex-shrink: 0;
  width: var(--icon-md);
  height: var(--icon-md);
  color: currentColor;
}

.toast__content {
  flex: 1;
}

.toast__close {
  flex-shrink: 0;
  cursor: pointer;
  padding: var(--space-xs);
  border-radius: var(--radius-sm);
  color: var(--color-neutral-500);
}

.toast__close:hover {
  background: var(--color-neutral-100);
  color: var(--color-neutral-700);
}
```

---

## Responsive Design

### Breakpoints

The CVD responsive system is optimized for enterprise use, with breakpoints that reflect modern business hardware and the reality that vending machine operators typically work on desktop/tablet devices.

```css
/* Mobile First Approach */
/* Default styles for mobile */

/* Tablet (768px and up) */
@media (min-width: 768px) {
  /* Tablet styles - forms and narrow layouts work well */
}

/* Desktop (1024px and up) */
@media (min-width: 1024px) {
  /* Standard desktop - default container width (1280px) */
}

/* Large Desktop (1280px and up) */
@media (min-width: 1280px) {
  /* Large desktop - enable dashboard containers (1440px) */
}

/* Enterprise Desktop (1440px and up) */
@media (min-width: 1440px) {
  /* Enterprise displays - enable full enterprise containers (1600px) */
  .container--enterprise,
  .container--adaptive {
    /* Optimal for data-heavy enterprise workflows */
  }
}

/* Ultra-wide Desktop (1920px and up) */
@media (min-width: 1920px) {
  /* Ultra-wide displays - consider fluid layouts for maximum data visibility */
}
```

#### Breakpoint Strategy

**Mobile (0-767px)**
- Single column layouts
- Simplified navigation
- Touch-optimized interactions
- Full-width containers

**Tablet (768-1023px)**
- Two-column layouts where appropriate
- Narrow containers work well (768px)
- Hybrid touch/mouse interactions

**Desktop (1024-1279px)**
- Standard desktop layouts
- Default container width (1280px)
- Mouse-optimized interactions

**Large Desktop (1280-1439px)**
- Dashboard layouts (1440px containers)
- Multi-column data displays
- Enhanced widget layouts

**Enterprise Desktop (1440px+)**
- Maximum data visibility
- Enterprise containers (1600px)
- Multi-panel interfaces
- Reduced horizontal scrolling for tables

### Responsive Utilities
```css
/* Hide/Show */
.hidden { display: none !important; }
.block { display: block !important; }
.inline-block { display: inline-block !important; }
.flex { display: flex !important; }

@media (min-width: 768px) {
  .md\:hidden { display: none !important; }
  .md\:block { display: block !important; }
  .md\:flex { display: flex !important; }
}

@media (min-width: 1024px) {
  .lg\:hidden { display: none !important; }
  .lg\:block { display: block !important; }
  .lg\:flex { display: flex !important; }
}

@media (min-width: 1440px) {
  .xl\:hidden { display: none !important; }
  .xl\:block { display: block !important; }
  .xl\:flex { display: flex !important; }
}

/* Container Responsive Utilities */
@media (max-width: 1439px) {
  .container--enterprise {
    max-width: 1280px; /* Fall back to default on smaller screens */
  }
}

@media (max-width: 1279px) {
  .container--dashboard {
    max-width: 1024px; /* Adjust dashboard width for smaller screens */
  }
}

/* Responsive Text */
.text-responsive {
  font-size: var(--text-sm);
}

@media (min-width: 768px) {
  .text-responsive {
    font-size: var(--text-base);
  }
}

@media (min-width: 1024px) {
  .text-responsive {
    font-size: var(--text-lg);
  }
}

/* Enterprise Data Text - Optimized for data-heavy interfaces */
.text-data {
  font-size: var(--text-sm);
  line-height: var(--leading-tight);
}

@media (min-width: 1440px) {
  .text-data {
    font-size: var(--text-base); /* Larger text on enterprise displays */
  }
}
```

---

## Accessibility Guidelines

### Focus Management
```css
/* Custom focus styles */
:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* Remove default focus for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}

/* Skip to main content link */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary-500);
  color: var(--color-neutral-0);
  padding: var(--space-sm) var(--space-md);
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

### Screen Reader Only
```css
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
```

### Color Contrast Requirements
- Normal text (< 18px): 4.5:1 contrast ratio
- Large text (≥ 18px): 3:1 contrast ratio
- UI components: 3:1 contrast ratio
- Focus indicators: 3:1 contrast ratio

### ARIA Patterns
```html
<!-- Button with loading state -->
<button class="btn btn--primary" aria-busy="true" aria-label="Saving changes">
  <span class="spinner spinner--sm" aria-hidden="true"></span>
  Saving...
</button>

<!-- Form with validation -->
<div class="form-group">
  <label for="email" class="form-label form-label--required">
    Email Address
  </label>
  <input 
    type="email" 
    id="email" 
    class="input input--error"
    aria-invalid="true"
    aria-describedby="email-error"
  >
  <div id="email-error" class="form-error" role="alert">
    Please enter a valid email address
  </div>
</div>

<!-- Navigation with current page -->
<nav aria-label="Main navigation">
  <ul class="nav__menu">
    <li>
      <a href="#dashboard" class="nav__item" aria-current="page">
        Dashboard
      </a>
    </li>
  </ul>
</nav>
```

---

## Motion & Animation

### Principles
1. **Purpose**: Every animation should have a clear purpose
2. **Performance**: Use CSS transforms and opacity for smooth 60fps
3. **Accessibility**: Respect prefers-reduced-motion
4. **Consistency**: Use standard easing and duration values

### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Common Animations
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

/* Pulse */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}
```

---

## Dark Mode Support

```css
/* Automatic dark mode based on system preference */
@media (prefers-color-scheme: dark) {
  :root {
    --color-neutral-0: #1a1a1a;
    --color-neutral-50: #2a2a2a;
    --color-neutral-100: #3a3a3a;
    --color-neutral-200: #4a4a4a;
    --color-neutral-300: #5a5a5a;
    --color-neutral-400: #6a6a6a;
    --color-neutral-500: #7a7a7a;
    --color-neutral-600: #8a8a8a;
    --color-neutral-700: #9a9a9a;
    --color-neutral-800: #aaaaaa;
    --color-neutral-900: #f5f5f5;
    
    /* Adjust shadows for dark mode */
    --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  }
}

/* Manual dark mode toggle */
[data-theme="dark"] {
  /* Dark mode variable overrides */
}
```

---

## Performance Guidelines

### CSS Performance
1. Use CSS variables for dynamic values
2. Minimize specificity chains
3. Avoid expensive selectors (*, :nth-child)
4. Use transform and opacity for animations
5. Implement will-change sparingly

### Loading Strategy
```html
<!-- Critical CSS in head -->
<style>
  /* Inline critical styles */
</style>

<!-- Preload important assets -->
<link rel="preload" href="/fonts/main.woff2" as="font" crossorigin>
<link rel="preload" href="/css/main.css" as="style">

<!-- Non-critical CSS -->
<link rel="stylesheet" href="/css/main.css" media="print" onload="this.media='all'">
```

---

## Implementation Checklist

### Component Development
- [ ] Follow naming conventions (BEM or similar)
- [ ] Include all interactive states (hover, focus, active, disabled)
- [ ] Test with keyboard navigation
- [ ] Verify screen reader compatibility
- [ ] Check color contrast ratios
- [ ] Test responsive behavior
- [ ] Document usage examples
- [ ] Add to component library
- [ ] Replace emoji icons with SVG equivalents
- [ ] Include appropriate ARIA labels for icons
- [ ] Ensure SVG icons scale properly across all sizes

### Page Development  
- [ ] Use semantic HTML
- [ ] Include skip navigation link
- [ ] Add proper heading hierarchy
- [ ] Implement breadcrumbs where appropriate
- [ ] Include loading states
- [ ] Add error handling
- [ ] Test on mobile devices
- [ ] Verify performance metrics

### Pre-Launch Checklist
- [ ] Run accessibility audit (axe-core)
- [ ] Test with screen readers
- [ ] Verify keyboard navigation
- [ ] Check all interactive states
- [ ] Test on target browsers
- [ ] Validate responsive design
- [ ] Check loading performance
- [ ] Review with actual users

---

## Usage Examples

### CVD Page Layout Patterns

Choose the appropriate container class based on your page content and user workflow:

```html
<!-- Enterprise Data Pages: Route Schedule, Device Management -->
<main id="main" class="container--enterprise">
  <!-- Wide tables, interactive maps, analytics dashboards -->
</main>

<!-- Dashboard Pages: Home, Service Orders -->
<main id="main" class="container--dashboard">
  <!-- Mixed widgets, charts, moderate data density -->
</main>

<!-- Standard Pages: Mixed Content -->
<main id="main" class="container">
  <!-- General purpose layouts -->
</main>

<!-- Form Pages: User Management, Device Config -->
<main id="main" class="container--narrow">
  <!-- Forms, settings, focused tasks -->
</main>

<!-- Full-width Pages: Custom Interfaces -->
<main id="main" class="container--fluid">
  <!-- Map interfaces, specialized layouts -->
</main>
```

### CVD-Specific Page Recommendations

| Page | Container Class | Reasoning |
|------|----------------|----------|
| `home-dashboard.html` | `container--dashboard` | Optimal for dashboard widgets and map integration |
| `PCP.html` (Device List) | `container--enterprise` | Maximize visible device data, reduce scrolling |
| `INVD.html` (Device Config) | `container--narrow` | Form-focused, benefits from concentrated layout |
| `NSPT.html` (Planogram) | `container--dashboard` | Balances drag-and-drop workspace with product catalog |
| `service-orders.html` | `container--dashboard` | Mixed table/form content works well at this width |
| `route-schedule.html` | `container--enterprise` | Interactive maps need maximum screen real estate |
| `asset-sales.html` | `container--enterprise` | Data tables benefit from additional visible columns |
| `product-sales.html` | `container--enterprise` | Analytics and data visualization |
| `database-viewer.html` | `container--enterprise` | Maximum data visibility for database operations |
| `dex-parser.html` | `container--dashboard` | Mixed content with file upload and results |
| `user-management.html` | `container--narrow` | Form-heavy interface |
| `profile.html` | `container--narrow` | Personal settings work better in focused layout |
| `login.html` | `container--narrow` | Optimal for authentication forms |

### Complete Page Template
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title | CVD Application</title>
  <link rel="stylesheet" href="/css/design-system.css">
</head>
<body>
  <!-- SVG Icon Sprite - Include at top of body -->
  <svg style="display: none;" aria-hidden="true">
    <defs>
      <!-- Include all icon symbols as defined in Icon System section -->
      <symbol id="icon-chart-bar" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
      </symbol>
      <!-- Additional icons as needed -->
    </defs>
  </svg>
  
  <!-- Skip Link -->
  <a href="#main" class="skip-link">Skip to main content</a>
  
  <!-- Navigation -->
  <nav class="nav" aria-label="Main navigation">
    <div class="container nav__container">
      <img src="/logo.png" alt="CVD Logo" class="nav__brand">
      <ul class="nav__menu">
        <li><a href="#" class="nav__item nav__item--active" aria-current="page">
          <svg class="icon icon--sm" aria-hidden="true"><use href="#icon-chart-bar"></use></svg>
          Dashboard
        </a></li>
        <li><a href="#" class="nav__item">
          <svg class="icon icon--sm" aria-hidden="true"><use href="#icon-server"></use></svg>
          Devices
        </a></li>
      </ul>
    </div>
  </nav>
  
  <!-- Breadcrumbs -->
  <div class="container">
    <nav aria-label="Breadcrumb" class="breadcrumbs">
      <a href="#" class="breadcrumbs__link">Home</a>
      <span class="breadcrumbs__separator">/</span>
      <span class="breadcrumbs__current">Current Page</span>
    </nav>
  </div>
  
  <!-- Main Content -->
  <main id="main" class="container--dashboard"> <!-- Use appropriate container class -->
    <h1>Page Heading</h1>
    
    <!-- Card Example -->
    <div class="card">
      <div class="card__header">
        <h2 class="card__title">Card Title</h2>
      </div>
      <div class="card__body">
        <!-- Content -->
      </div>
    </div>
  </main>
  
  <!-- Toast Container -->
  <div class="toast-container" role="region" aria-live="polite"></div>
</body>
</html>
```

---

*This style guide v2.0 represents a complete redesign of the CVD design system, prioritizing consistency, accessibility, and modern UX patterns. It should be implemented incrementally, starting with the most critical components and pages.*