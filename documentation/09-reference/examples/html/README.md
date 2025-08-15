---
type: examples
category: html
title: HTML Prototypes and UI Examples
status: active
last_updated: 2025-08-12
tags: [html, prototypes, ui, frontend, examples]
cross_references:
  - /documentation/06-design/components/README.md
  - /documentation/02-requirements/guides/README.md
---

# HTML Prototypes and UI Examples

## Purpose
HTML prototypes, proof-of-concepts, and UI examples used during development and feature exploration.

## Contents

### Route Planning and Mapping
- **map-test.html** - Map integration testing and leaflet.js examples
- **route-planner-mapping.html** - Route planning UI prototypes
- **vms-picovision-planner.html** - VMS integration prototype

### Service Order Mockups
- **service-orders-mockup.html** - Service order interface mockups and workflow testing
- **UPT.html** - UPT (Units to Par) calculation interface prototype

## Usage

These files are used for:
1. **UI Prototyping** - Rapid prototyping of interface concepts
2. **Integration Testing** - Testing third-party library integrations
3. **Feature Exploration** - Exploring new feature interfaces before implementation
4. **Design Validation** - Validating design concepts with stakeholders

## File Locations
Files are migrated from `/docs/examples/html/` to this directory:
- Source: `/docs/examples/html/*.html`
- Destination: `/documentation/09-reference/examples/html/*.html`

## Integration Notes
- Map examples use Leaflet.js for interactive mapping
- Service order mockups demonstrate cabinet-centric workflow
- All prototypes use inline CSS/JS for self-contained testing

## Cross-References
- [Design System](/documentation/06-design/DESIGN_SYSTEM.md) - Design patterns and components
- [Route Schedule Implementation](/documentation/07-cvd-framework/README.md) - Production route scheduling
- [Service Orders](/documentation/07-cvd-framework/service-orders/README.md) - Production service order system