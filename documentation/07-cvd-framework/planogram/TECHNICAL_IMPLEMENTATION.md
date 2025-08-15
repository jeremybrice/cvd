# Planogram Technical Implementation


## Metadata
- **ID**: 07_CVD_FRAMEWORK_PLANOGRAM_TECHNICAL_IMPLEMENTATION
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #cvd-specific #data-exchange #data-layer #database #debugging #device-management #dex-parser #domain #integration #logistics #machine-learning #optimization #performance #planogram #product-placement #route-management #troubleshooting #vending #vending-machine
- **Intent**: The primary planogram interface (`pages/NSPT
- **Audience**: developers, managers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/07-cvd-framework/planogram/
- **Category**: Planogram
- **Search Keywords**: ###, api, batch, cabinet, catalog, configuration, debounced, device, dex, endpoints, grid, implementation, lazy, loading, operations

This document details the technical implementation of the CVD planogram system, covering the drag-and-drop interface architecture, product catalog integration, and slot configuration logic.

## Frontend Architecture

### NSPT.html Overview
The primary planogram interface (`pages/NSPT.html`) implements a comprehensive grid-based configuration system using vanilla JavaScript with modular patterns.

#### Key Components
- **Grid Renderer**: Visual representation of cabinet slot layout
- **Product Catalog**: Sidebar product selection interface
- **Slot Configuration Panel**: Property management for individual slots
- **AI Optimization Panel**: Integration with AI recommendation engine

#### Technology Stack
```javascript
// Core Dependencies
- Vanilla JavaScript (ES6+)
- CSS Grid Layout for slot positioning
- Drag and Drop API for product placement
- Fetch API for backend communication
- CVD API client for data operations
```

### Drag-and-Drop Interface

#### Implementation Pattern
```javascript
// Slot Grid Generation
function generateSlotGrid(rows, columns) {
    const grid = document.createElement('div');
    grid.className = 'planogram-grid';
    grid.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
    grid.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
    
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < columns; col++) {
            const slot = createSlotElement(row, col);
            grid.appendChild(slot);
        }
    }
    return grid;
}

// Drag Event Handling
function initializeDragAndDrop() {
    // Product catalog items (draggable)
    productItems.forEach(item => {
        item.draggable = true;
        item.addEventListener('dragstart', handleDragStart);
    });
    
    // Slot targets (droppable)
    slotElements.forEach(slot => {
        slot.addEventListener('dragover', handleDragOver);
        slot.addEventListener('drop', handleDrop);
        slot.addEventListener('dragenter', handleDragEnter);
        slot.addEventListener('dragleave', handleDragLeave);
    });
}
```

#### Slot Configuration Logic
```javascript
// Slot State Management
class SlotManager {
    constructor() {
        this.slots = new Map();
        this.validationRules = new ValidationEngine();
    }
    
    updateSlot(position, productId, properties) {
        const slot = this.slots.get(position) || {};
        
        // Validation before update
        const validation = this.validationRules.validate({
            position,
            productId,
            capacity: properties.capacity,
            parLevel: properties.parLevel,
            price: properties.price
        });
        
        if (!validation.valid) {
            throw new Error(validation.errors.join(', '));
        }
        
        // Update slot data
        this.slots.set(position, {
            ...slot,
            productId,
            ...properties,
            lastModified: new Date().toISOString()
        });
        
        // Trigger UI update
        this.renderSlot(position);
        this.saveToDatabase(position);
    }
}
```

### Product Catalog Integration

#### Product Management System
```javascript
// Product Catalog Structure
class ProductCatalog {
    constructor() {
        this.products = [];
        this.categories = ['Beverages', 'Snacks', 'Fresh Food'];
        this.systemProducts = 12; // Standard product count
    }
    
    async loadProducts() {
        try {
            const response = await api.get('/api/products');
            this.products = response.data;
            this.renderCatalog();
        } catch (error) {
            console.error('Failed to load product catalog:', error);
            this.showError('Product catalog unavailable');
        }
    }
    
    renderCatalog() {
        const catalog = document.getElementById('product-catalog');
        catalog.innerHTML = '';
        
        this.categories.forEach(category => {
            const section = this.createCategorySection(category);
            catalog.appendChild(section);
        });
    }
    
    createCategorySection(category) {
        const section = document.createElement('div');
        section.className = 'category-section';
        
        const header = document.createElement('h3');
        header.textContent = category;
        section.appendChild(header);
        
        const productGrid = document.createElement('div');
        productGrid.className = 'product-grid';
        
        this.products
            .filter(product => product.category === category)
            .forEach(product => {
                const productElement = this.createProductElement(product);
                productGrid.appendChild(productElement);
            });
        
        section.appendChild(productGrid);
        return section;
    }
}
```

#### Product Element Creation
```javascript
// Draggable Product Items
createProductElement(product) {
    const element = document.createElement('div');
    element.className = 'product-item';
    element.draggable = true;
    element.dataset.productId = product.id;
    
    element.innerHTML = `
        <div class="product-image">
            <img src="${product.imageUrl || '/images/default-product.png'}" 
                 alt="${product.name}">
        </div>
        <div class="product-info">
            <h4>${product.name}</h4>
            <p class="price">$${(product.price / 100).toFixed(2)}</p>
            <p class="category">${product.category}</p>
        </div>
    `;
    
    // Drag event listeners
    element.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('application/json', JSON.stringify({
            productId: product.id,
            productName: product.name,
            price: product.price,
            category: product.category
        }));
        element.classList.add('dragging');
    });
    
    element.addEventListener('dragend', () => {
        element.classList.remove('dragging');
    });
    
    return element;
}
```

## Backend Integration

### Database Schema
```sql
-- Planograms table
CREATE TABLE planograms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    cabinet_id INTEGER NOT NULL,
    planogram_key TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id),
    FOREIGN KEY (cabinet_id) REFERENCES cabinet_configurations(id)
);

-- Planogram slots table
CREATE TABLE planogram_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planogram_id INTEGER NOT NULL,
    slot_position TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    product_name TEXT,
    quantity INTEGER DEFAULT 0,
    capacity INTEGER DEFAULT 20,
    par_level INTEGER DEFAULT 15,
    price INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (planogram_id) REFERENCES planograms(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

### API Endpoints
```python
# Planogram CRUD Operations
@app.route('/api/planograms/<int:device_id>/<int:cabinet_index>')
def get_planogram(device_id, cabinet_index):
    """Get planogram configuration for device cabinet"""
    planogram_key = f"{device_id}_{cabinet_index}"
    
    # Get or create planogram
    planogram = db.execute('''
        SELECT * FROM planograms WHERE planogram_key = ?
    ''', (planogram_key,)).fetchone()
    
    if not planogram:
        # Create default planogram
        planogram = create_default_planogram(device_id, cabinet_index)
    
    # Get slot configurations
    slots = db.execute('''
        SELECT ps.*, p.name as product_name, p.category
        FROM planogram_slots ps
        LEFT JOIN products p ON ps.product_id = p.id
        WHERE ps.planogram_id = ?
        ORDER BY ps.slot_position
    ''', (planogram['id'],)).fetchall()
    
    return {
        'planogram': dict(planogram),
        'slots': [dict(slot) for slot in slots]
    }

@app.route('/api/planograms/<int:device_id>/<int:cabinet_index>', methods=['PUT'])
def update_planogram(device_id, cabinet_index):
    """Update planogram configuration"""
    data = request.json
    planogram_key = f"{device_id}_{cabinet_index}"
    
    try:
        # Update planogram metadata
        db.execute('''
            UPDATE planograms 
            SET updated_at = CURRENT_TIMESTAMP
            WHERE planogram_key = ?
        ''', (planogram_key,))
        
        # Update slot configurations
        for slot_data in data.get('slots', []):
            update_slot_configuration(planogram_key, slot_data)
        
        db.commit()
        return {'success': True}
        
    except Exception as e:
        db.rollback()
        return {'error': str(e)}, 400
```

### Slot Configuration Logic
```python
def update_slot_configuration(planogram_key, slot_data):
    """Update individual slot configuration"""
    # Validation rules
    capacity = slot_data.get('capacity', 20)
    par_level = slot_data.get('par_level', 15)
    quantity = slot_data.get('quantity', 0)
    
    if par_level > capacity:
        raise ValueError(f"Par level ({par_level}) cannot exceed capacity ({capacity})")
    
    if quantity > capacity:
        raise ValueError(f"Quantity ({quantity}) cannot exceed capacity ({capacity})")
    
    # Update slot
    db.execute('''
        UPDATE planogram_slots 
        SET product_id = ?, product_name = ?, capacity = ?, 
            par_level = ?, quantity = ?, price = ?, updated_at = CURRENT_TIMESTAMP
        WHERE planogram_id = (
            SELECT id FROM planograms WHERE planogram_key = ?
        ) AND slot_position = ?
    ''', (
        slot_data['product_id'],
        slot_data.get('product_name'),
        capacity,
        par_level,
        quantity,
        slot_data.get('price', 0),
        planogram_key,
        slot_data['slot_position']
    ))
```

## Data Management Patterns

### No-Caching Strategy
The planogram system implements a direct database approach without caching layers:

```javascript
// Direct Database Operations
class PlanogramAPI {
    async saveSlotConfiguration(deviceId, cabinetIndex, slotPosition, config) {
        // Immediate database write
        const response = await fetch(`/api/planograms/${deviceId}/${cabinetIndex}/slots`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                slot_position: slotPosition,
                ...config
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to save slot configuration');
        }
        
        // Immediate UI update
        this.updateSlotUI(slotPosition, config);
        return response.json();
    }
}
```

### Real-Time Synchronization
```javascript
// Cross-Frame Communication
window.addEventListener('message', (event) => {
    if (event.data.type === 'PLANOGRAM_UPDATED') {
        const { deviceId, cabinetIndex } = event.data.payload;
        // Refresh planogram data
        this.loadPlanogram(deviceId, cabinetIndex);
    }
});

// Notify other frames of changes
function notifyPlanogramUpdate(deviceId, cabinetIndex) {
    window.parent.postMessage({
        type: 'PLANOGRAM_UPDATED',
        payload: { deviceId, cabinetIndex }
    }, window.location.origin);
}
```

## Performance Considerations

### Optimization Strategies
- **Debounced Updates**: Prevent excessive API calls during drag operations
- **Batch Operations**: Group multiple slot updates into single transactions
- **Lazy Loading**: Load planogram data only when cabinet is selected
- **UI Virtualization**: Render only visible slots for large grids

### Error Handling
```javascript
// Comprehensive Error Management
class PlanogramErrorHandler {
    handleDragError(error, context) {
        console.error('Drag operation failed:', error);
        
        // Revert UI state
        this.revertSlotState(context.slotPosition);
        
        // Show user-friendly message
        this.showNotification('Unable to place product. Please try again.', 'error');
        
        // Log for debugging
        this.logError('DRAG_OPERATION', error, context);
    }
    
    handleSaveError(error, slotPosition) {
        console.error('Save operation failed:', error);
        
        // Mark slot as unsaved
        this.markSlotUnsaved(slotPosition);
        
        // Offer retry option
        this.showRetryDialog(slotPosition);
    }
}
```

The planogram technical implementation demonstrates a robust, user-friendly system that balances immediate responsiveness with data integrity, providing a seamless experience for complex product placement management.