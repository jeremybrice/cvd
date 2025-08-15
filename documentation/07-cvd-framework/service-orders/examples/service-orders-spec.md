# Service Orders Management - Implementation Specification

## Overview

The Service Orders Management page provides managers with a real-time view of delivery operations, allowing them to monitor, execute, and rollback service orders. This system ensures accurate inventory management while maintaining a complete audit trail of all delivery actions.

## Database Schema Updates

### New Table: service_visit_items

```sql
CREATE TABLE service_visit_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_visit_id INTEGER NOT NULL,
    service_order_item_id INTEGER NOT NULL,
    quantity_delivered INTEGER NOT NULL,  -- Can be negative for rollbacks
    variance_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    
    FOREIGN KEY (service_visit_id) REFERENCES service_visits(id),
    FOREIGN KEY (service_order_item_id) REFERENCES service_order_items(id)
);

CREATE INDEX idx_service_visit_items_visit ON service_visit_items(service_visit_id);
CREATE INDEX idx_service_visit_items_order_item ON service_visit_items(service_order_item_id);
```

### Update service_visits Table

```sql
-- Add execution metadata to service_visits
ALTER TABLE service_visits ADD COLUMN executed_at TIMESTAMP;
ALTER TABLE service_visits ADD COLUMN executed_by TEXT;
```

## Backend API Endpoints

### 1. Get Service Orders with Execution Status

```python
@app.route('/api/service-orders/management', methods=['GET'])
def get_service_orders_management():
    """
    Get service orders with execution details for management view
    
    Query params:
    - status: pending|in_progress|completed|cancelled (optional)
    - route_id: filter by route (optional)
    - date_from: start date (optional)
    - date_to: end date (optional)
    
    Response includes:
    - Order details
    - Execution progress per cabinet/device
    - Fill rates at all levels
    - Delivery history
    """
```

### 2. Execute Service Order Items

```python
@app.route('/api/service-orders/execute', methods=['POST'])
def execute_service_order_items():
    """
    Execute delivery for cabinet or device
    
    Request body:
    {
        "serviceOrderId": 123,
        "executionLevel": "cabinet|device",
        "deviceId": 456,
        "cabinetIndex": 0,  // Required if executionLevel is "cabinet"
        "items": [
            {
                "serviceOrderItemId": 789,
                "quantityDelivered": 12,
                "varianceReason": "Short on stock"  // Optional
            }
        ],
        "executedBy": "manager@example.com"
    }
    
    Actions:
    1. Create service_visit record (if not exists)
    2. Create service_visit_items records
    3. Update planogram_slots quantities
    4. Update service_order status
    5. Return updated order with new fill rates
    """
```

### 3. Rollback Delivery

```python
@app.route('/api/service-orders/rollback', methods=['POST'])
def rollback_delivery():
    """
    Rollback a delivery by creating negative quantity records
    
    Request body:
    {
        "serviceOrderId": 123,
        "deviceId": 456,
        "cabinetIndex": 0,  // Optional, if rolling back entire device
        "executedBy": "manager@example.com"
    }
    
    Actions:
    1. Find all service_visit_items for the cabinet/device
    2. Create new records with negative quantities
    3. Update planogram_slots (subtract quantities)
    4. Update service_order status
    """
```

### 4. Get Delivery History

```python
@app.route('/api/service-orders/<int:order_id>/history', methods=['GET'])
def get_delivery_history(order_id):
    """
    Get complete delivery history including rollbacks
    
    Response:
    {
        "orderId": 123,
        "deliveries": [
            {
                "timestamp": "2025-07-22T10:30:00",
                "action": "delivered|rolled_back",
                "deviceId": 456,
                "cabinetIndex": 0,
                "items": [...],
                "executedBy": "manager@example.com"
            }
        ]
    }
    """
```

### 5. Calculate Fill Rates

```python
def calculate_fill_rates(order_id, level="all"):
    """
    Calculate fill rates at various levels
    
    Fill Rate = ((Delivered + Current) / Par Level) × 100%
    
    Returns:
    {
        "order": 87.5,
        "devices": {
            "456": {
                "rate": 85.0,
                "cabinets": {
                    "0": {
                        "rate": 82.0,
                        "products": {
                            "2": {"name": "Coke", "rate": 85.0},
                            "3": {"name": "Pepsi", "rate": 79.0}
                        }
                    }
                }
            }
        }
    }
    """
```

## Frontend Implementation

### File: pages/service-orders.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Service Orders - CVD</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Header Section */
        .page-header {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header-title {
            font-size: 24px;
            font-weight: 600;
            color: #1a1a1a;
        }

        .header-meta {
            display: flex;
            align-items: center;
            gap: 20px;
            font-size: 14px;
            color: #666;
        }

        .auto-refresh-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .refresh-dot {
            width: 8px;
            height: 8px;
            background: #28a745;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        /* KPI Cards */
        .kpi-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .kpi-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: center;
        }

        .kpi-value {
            font-size: 32px;
            font-weight: 700;
            color: #006dfe;
            margin-bottom: 5px;
        }

        .kpi-label {
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Filter Bar */
        .filter-bar {
            background: white;
            border-radius: 8px;
            padding: 15px 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }

        .filter-bar select,
        .filter-bar input {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            background: white;
        }

        .filter-bar button {
            padding: 8px 16px;
            background: #006dfe;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .filter-bar button:hover {
            background: #0056d3;
        }

        /* Order List */
        .orders-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .order-item {
            border-bottom: 1px solid #e5e5e5;
            transition: background 0.2s;
        }

        .order-item:hover {
            background: #f8f9fa;
        }

        .order-header {
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }

        .order-info {
            display: flex;
            gap: 20px;
            align-items: center;
        }

        .order-number {
            font-weight: 600;
            color: #333;
        }

        .order-meta {
            font-size: 14px;
            color: #666;
        }

        .order-status {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .status-pending {
            background: #fff3cd;
            color: #856404;
        }

        .status-in_progress {
            background: #d1ecf1;
            color: #0c5460;
        }

        .status-completed {
            background: #d4edda;
            color: #155724;
        }

        .status-cancelled {
            background: #f8d7da;
            color: #721c24;
        }

        /* Order Details */
        .order-details {
            display: none;
            padding: 0 20px 20px;
            background: #f8f9fa;
        }

        .order-details.expanded {
            display: block;
        }

        .device-section {
            background: white;
            border-radius: 6px;
            margin-top: 15px;
            padding: 15px;
            border: 1px solid #e5e5e5;
        }

        .device-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e5e5e5;
        }

        .device-name {
            font-weight: 600;
            color: #333;
        }

        .cabinet-section {
            margin-top: 15px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 4px;
            border: 1px solid #e5e5e5;
        }

        .cabinet-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .cabinet-name {
            font-weight: 500;
            color: #555;
        }

        .fill-rate {
            font-size: 14px;
            font-weight: 600;
        }

        .fill-rate-high { color: #28a745; }
        .fill-rate-medium { color: #ffc107; }
        .fill-rate-low { color: #dc3545; }

        /* Product Table */
        .product-table {
            width: 100%;
            margin-top: 10px;
            font-size: 14px;
        }

        .product-table th,
        .product-table td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #e5e5e5;
        }

        .product-table th {
            font-weight: 600;
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
        }

        /* Action Buttons */
        .action-buttons {
            display: flex;
            gap: 10px;
        }

        .btn {
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }

        .btn-primary {
            background: #006dfe;
            color: white;
        }

        .btn-primary:hover {
            background: #0056d3;
        }

        .btn-secondary {
            background: white;
            color: #333;
            border: 1px solid #ddd;
        }

        .btn-secondary:hover {
            background: #f8f9fa;
        }

        .btn-danger {
            background: #dc3545;
            color: white;
        }

        .btn-danger:hover {
            background: #c82333;
        }

        .btn-success {
            background: #28a745;
            color: white;
        }

        .btn-success:hover {
            background: #218838;
        }

        /* Edit Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: white;
            border-radius: 8px;
            padding: 20px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #e5e5e5;
        }

        .modal-title {
            font-size: 18px;
            font-weight: 600;
        }

        .close-modal {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #666;
        }

        .product-edit-section {
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }

        .edit-field {
            margin-bottom: 10px;
        }

        .edit-field label {
            display: block;
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
            text-transform: uppercase;
        }

        .edit-field input,
        .edit-field textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }

        .edit-field .static-value {
            font-weight: 600;
            color: #333;
        }

        .quantity-input {
            width: 100px;
            text-align: center;
        }

        /* Delivery History */
        .history-item {
            padding: 10px;
            margin-bottom: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 14px;
        }

        .history-action {
            font-weight: 600;
        }

        .history-delivered { color: #28a745; }
        .history-rolled-back { color: #dc3545; }
    </style>
    <script src="/api.js"></script>
</head>
<body>
    <div class="container">
        <!-- Page Header -->
        <div class="page-header">
            <h1 class="header-title">Service Orders</h1>
            <div class="header-meta">
                <div class="auto-refresh-indicator" id="autoRefreshIndicator" style="display: none;">
                    <span class="refresh-dot"></span>
                    <span>Auto-refresh active</span>
                </div>
                <span id="lastUpdated">Last updated: Never</span>
            </div>
        </div>

        <!-- KPI Section -->
        <div class="kpi-section">
            <div class="kpi-card">
                <div class="kpi-value" id="kpiPending">0</div>
                <div class="kpi-label">Pending</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value" id="kpiInProgress">0</div>
                <div class="kpi-label">In Progress</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value" id="kpiCompleted">0</div>
                <div class="kpi-label">Completed Today</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value" id="kpiFillRate">0%</div>
                <div class="kpi-label">Avg Fill Rate</div>
            </div>
        </div>

        <!-- Filter Bar -->
        <div class="filter-bar">
            <select id="statusFilter">
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
            </select>
            <select id="routeFilter">
                <option value="">All Routes</option>
            </select>
            <input type="date" id="dateFromFilter">
            <input type="date" id="dateToFilter">
            <button onclick="applyFilters()">Apply Filters</button>
            <button onclick="resetFilters()">Reset</button>
        </div>

        <!-- Orders Container -->
        <div class="orders-container" id="ordersContainer">
            <!-- Orders will be dynamically loaded here -->
        </div>
    </div>

    <!-- Edit Modal -->
    <div class="modal" id="editModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">Edit Delivery Quantities</h2>
                <button class="close-modal" onclick="closeEditModal()">&times;</button>
            </div>
            <div id="editModalBody">
                <!-- Product edit sections will be loaded here -->
            </div>
            <div class="modal-footer" style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e5e5; display: flex; gap: 10px; justify-content: flex-end;">
                <button class="btn btn-secondary" onclick="closeEditModal()">Cancel</button>
                <button class="btn btn-primary" onclick="executeWithEdits()">Execute Delivery</button>
            </div>
        </div>
    </div>

    <script>
        // API client
        const api = new CVDApi();
        
        // State management
        let currentOrders = [];
        let currentFilters = {
            status: '',
            routeId: '',
            dateFrom: '',
            dateTo: ''
        };
        let autoRefreshTimer = null;
        let editingData = null;

        // Initialize on load
        document.addEventListener('DOMContentLoaded', function() {
            loadRoutes();
            loadOrders();
            setupAutoRefresh();
            
            // Set today's date as default
            document.getElementById('dateToFilter').value = new Date().toISOString().split('T')[0];
        });

        // Load available routes for filter
        async function loadRoutes() {
            try {
                const routes = await api.getRoutes();
                const select = document.getElementById('routeFilter');
                
                routes.forEach(route => {
                    const option = document.createElement('option');
                    option.value = route.id;
                    option.textContent = `${route.name} (${route.routeNumber})`;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Failed to load routes:', error);
            }
        }

        // Load orders with current filters
        async function loadOrders() {
            try {
                const params = new URLSearchParams();
                if (currentFilters.status) params.append('status', currentFilters.status);
                if (currentFilters.routeId) params.append('route_id', currentFilters.routeId);
                if (currentFilters.dateFrom) params.append('date_from', currentFilters.dateFrom);
                if (currentFilters.dateTo) params.append('date_to', currentFilters.dateTo);
                
                const response = await api.makeRequest('GET', `/service-orders/management?${params}`);
                currentOrders = response.orders || [];
                
                updateKPIs(response.summary);
                renderOrders();
                updateLastUpdated();
                
            } catch (error) {
                console.error('Failed to load orders:', error);
                showError('Failed to load service orders');
            }
        }

        // Update KPI cards
        function updateKPIs(summary) {
            document.getElementById('kpiPending').textContent = summary.pending || 0;
            document.getElementById('kpiInProgress').textContent = summary.inProgress || 0;
            document.getElementById('kpiCompleted').textContent = summary.completedToday || 0;
            document.getElementById('kpiFillRate').textContent = `${Math.round(summary.avgFillRate || 0)}%`;
        }

        // Render orders list
        function renderOrders() {
            const container = document.getElementById('ordersContainer');
            container.innerHTML = '';
            
            if (currentOrders.length === 0) {
                container.innerHTML = '<div style="padding: 40px; text-align: center; color: #666;">No orders found</div>';
                return;
            }
            
            currentOrders.forEach(order => {
                const orderElement = createOrderElement(order);
                container.appendChild(orderElement);
            });
        }

        // Create order element
        function createOrderElement(order) {
            const div = document.createElement('div');
            div.className = 'order-item';
            div.innerHTML = `
                <div class="order-header" onclick="toggleOrderDetails('${order.id}')">
                    <div class="order-info">
                        <span class="order-number">Order #${order.id}</span>
                        <span class="order-meta">Route: ${order.routeName}</span>
                        <span class="order-meta">Driver: ${order.createdBy || 'Unassigned'}</span>
                        <span class="order-meta">${formatDate(order.createdAt)}</span>
                    </div>
                    <div>
                        <span class="order-status status-${order.status}">${order.status.replace('_', ' ')}</span>
                        <span style="margin-left: 15px;">Fill Rate: ${Math.round(order.fillRate || 0)}%</span>
                    </div>
                </div>
                <div class="order-details" id="details-${order.id}">
                    ${renderOrderDetails(order)}
                </div>
            `;
            return div;
        }

        // Render order details
        function renderOrderDetails(order) {
            let html = '';
            
            order.devices.forEach(device => {
                html += `
                    <div class="device-section">
                        <div class="device-header">
                            <div class="device-name">Device ${device.asset} - ${device.location}</div>
                            <div class="action-buttons">
                                ${order.status !== 'completed' && order.status !== 'cancelled' ? 
                                    `<button class="btn btn-primary btn-sm" onclick="executeDevice(${order.id}, ${device.deviceId})">Execute All</button>` : ''}
                                ${device.hasDeliveries ? 
                                    `<button class="btn btn-danger btn-sm" onclick="rollbackDevice(${order.id}, ${device.deviceId})">Rollback All</button>` : ''}
                            </div>
                        </div>
                        ${renderCabinets(order, device)}
                    </div>
                `;
            });
            
            return html;
        }

        // Render cabinets
        function renderCabinets(order, device) {
            let html = '';
            
            device.cabinets.forEach(cabinet => {
                const fillRateClass = cabinet.fillRate >= 90 ? 'fill-rate-high' : 
                                     cabinet.fillRate >= 70 ? 'fill-rate-medium' : 'fill-rate-low';
                
                html += `
                    <div class="cabinet-section">
                        <div class="cabinet-header">
                            <div class="cabinet-name">Cabinet ${cabinet.cabinetIndex + 1} - ${cabinet.cabinetType}</div>
                            <div>
                                <span class="fill-rate ${fillRateClass}">Fill: ${Math.round(cabinet.fillRate)}%</span>
                                ${cabinet.deliveryStatus ? 
                                    `<span style="margin-left: 10px; color: #28a745;">✓ Delivered</span>` : ''}
                            </div>
                        </div>
                        ${renderProductTable(cabinet)}
                        <div class="action-buttons" style="margin-top: 10px;">
                            ${!cabinet.deliveryStatus && order.status !== 'completed' && order.status !== 'cancelled' ? `
                                <button class="btn btn-primary btn-sm" onclick="executeCabinet(${order.id}, ${device.deviceId}, ${cabinet.cabinetIndex})">Quick Execute</button>
                                <button class="btn btn-secondary btn-sm" onclick="openEditModal(${order.id}, ${device.deviceId}, ${cabinet.cabinetIndex})">Edit & Execute</button>
                            ` : ''}
                            ${cabinet.deliveryStatus ? 
                                `<button class="btn btn-danger btn-sm" onclick="rollbackCabinet(${order.id}, ${device.deviceId}, ${cabinet.cabinetIndex})">Rollback</button>` : ''}
                        </div>
                    </div>
                `;
            });
            
            return html;
        }

        // Render product table
        function renderProductTable(cabinet) {
            let html = '<table class="product-table"><thead><tr>';
            html += '<th>Product</th><th>Current</th><th>Ordered</th><th>Delivered</th><th>After</th><th>Par</th><th>Fill Rate</th>';
            html += '</tr></thead><tbody>';
            
            cabinet.products.forEach(product => {
                const fillRateClass = product.fillRate >= 90 ? 'fill-rate-high' : 
                                     product.fillRate >= 70 ? 'fill-rate-medium' : 'fill-rate-low';
                
                html += `
                    <tr>
                        <td>${product.productName}</td>
                        <td>${product.currentQuantity}</td>
                        <td>${product.orderedQuantity}</td>
                        <td>${product.deliveredQuantity || '-'}</td>
                        <td>${product.afterQuantity}</td>
                        <td>${product.parLevel}</td>
                        <td class="${fillRateClass}">${Math.round(product.fillRate)}%</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            return html;
        }

        // Toggle order details
        function toggleOrderDetails(orderId) {
            const details = document.getElementById(`details-${orderId}`);
            details.classList.toggle('expanded');
        }

        // Execute device
        async function executeDevice(orderId, deviceId) {
            try {
                const order = currentOrders.find(o => o.id === orderId);
                const device = order.devices.find(d => d.deviceId === deviceId);
                
                // Collect all items for the device
                const items = [];
                device.cabinets.forEach(cabinet => {
                    cabinet.products.forEach(product => {
                        if (product.serviceOrderItemId && !product.deliveredQuantity) {
                            items.push({
                                serviceOrderItemId: product.serviceOrderItemId,
                                quantityDelivered: product.orderedQuantity
                            });
                        }
                    });
                });
                
                const response = await api.makeRequest('POST', '/service-orders/execute', {
                    serviceOrderId: orderId,
                    executionLevel: 'device',
                    deviceId: deviceId,
                    items: items,
                    executedBy: 'current_user@example.com' // TODO: Get from session
                });
                
                showSuccess('Device delivered successfully');
                loadOrders();
                
            } catch (error) {
                console.error('Execution failed:', error);
                showError('Failed to execute delivery');
            }
        }

        // Execute cabinet
        async function executeCabinet(orderId, deviceId, cabinetIndex) {
            try {
                const order = currentOrders.find(o => o.id === orderId);
                const device = order.devices.find(d => d.deviceId === deviceId);
                const cabinet = device.cabinets.find(c => c.cabinetIndex === cabinetIndex);
                
                // Collect items for the cabinet
                const items = cabinet.products.map(product => ({
                    serviceOrderItemId: product.serviceOrderItemId,
                    quantityDelivered: product.orderedQuantity
                }));
                
                const response = await api.makeRequest('POST', '/service-orders/execute', {
                    serviceOrderId: orderId,
                    executionLevel: 'cabinet',
                    deviceId: deviceId,
                    cabinetIndex: cabinetIndex,
                    items: items,
                    executedBy: 'current_user@example.com' // TODO: Get from session
                });
                
                showSuccess('Cabinet delivered successfully');
                loadOrders();
                
            } catch (error) {
                console.error('Execution failed:', error);
                showError('Failed to execute delivery');
            }
        }

        // Open edit modal
        function openEditModal(orderId, deviceId, cabinetIndex) {
            const order = currentOrders.find(o => o.id === orderId);
            const device = order.devices.find(d => d.deviceId === deviceId);
            const cabinet = device.cabinets.find(c => c.cabinetIndex === cabinetIndex);
            
            editingData = {
                orderId,
                deviceId,
                cabinetIndex,
                cabinet
            };
            
            // Build modal content
            let html = '';
            cabinet.products.forEach(product => {
                const afterDelivery = product.currentQuantity + product.orderedQuantity;
                
                html += `
                    <div class="product-edit-section">
                        <h4>${product.productName}</h4>
                        <div class="edit-field">
                            <label>Current in Cabinet</label>
                            <div class="static-value">${product.currentQuantity} units</div>
                        </div>
                        <div class="edit-field">
                            <label>Ordered</label>
                            <div class="static-value">${product.orderedQuantity} units</div>
                        </div>
                        <div class="edit-field">
                            <label>Deliver</label>
                            <input type="number" 
                                   class="quantity-input" 
                                   id="deliver-${product.serviceOrderItemId}"
                                   value="${product.orderedQuantity}"
                                   min="0"
                                   onchange="updateAfterDelivery(${product.serviceOrderItemId}, ${product.currentQuantity})">
                            <span> units</span>
                        </div>
                        <div class="edit-field">
                            <label>After Delivery</label>
                            <div class="static-value" id="after-${product.serviceOrderItemId}">${afterDelivery} units</div>
                        </div>
                        <div class="edit-field">
                            <label>Variance Reason (Optional)</label>
                            <textarea id="reason-${product.serviceOrderItemId}" rows="2"></textarea>
                        </div>
                    </div>
                `;
            });
            
            document.getElementById('editModalBody').innerHTML = html;
            document.getElementById('editModal').classList.add('active');
        }

        // Update after delivery calculation
        function updateAfterDelivery(itemId, currentQuantity) {
            const deliverInput = document.getElementById(`deliver-${itemId}`);
            const afterDiv = document.getElementById(`after-${itemId}`);
            const newQuantity = currentQuantity + parseInt(deliverInput.value || 0);
            afterDiv.textContent = `${newQuantity} units`;
        }

        // Close edit modal
        function closeEditModal() {
            document.getElementById('editModal').classList.remove('active');
            editingData = null;
        }

        // Execute with edits
        async function executeWithEdits() {
            try {
                const items = editingData.cabinet.products.map(product => {
                    const delivered = parseInt(document.getElementById(`deliver-${product.serviceOrderItemId}`).value);
                    const reason = document.getElementById(`reason-${product.serviceOrderItemId}`).value;
                    
                    return {
                        serviceOrderItemId: product.serviceOrderItemId,
                        quantityDelivered: delivered,
                        varianceReason: reason || null
                    };
                });
                
                const response = await api.makeRequest('POST', '/service-orders/execute', {
                    serviceOrderId: editingData.orderId,
                    executionLevel: 'cabinet',
                    deviceId: editingData.deviceId,
                    cabinetIndex: editingData.cabinetIndex,
                    items: items,
                    executedBy: 'current_user@example.com' // TODO: Get from session
                });
                
                closeEditModal();
                showSuccess('Cabinet delivered successfully');
                loadOrders();
                
            } catch (error) {
                console.error('Execution failed:', error);
                showError('Failed to execute delivery');
            }
        }

        // Rollback functions
        async function rollbackDevice(orderId, deviceId) {
            if (!confirm('Are you sure you want to rollback all deliveries for this device?')) {
                return;
            }
            
            try {
                await api.makeRequest('POST', '/service-orders/rollback', {
                    serviceOrderId: orderId,
                    deviceId: deviceId,
                    executedBy: 'current_user@example.com' // TODO: Get from session
                });
                
                showSuccess('Device rollback successful');
                loadOrders();
                
            } catch (error) {
                console.error('Rollback failed:', error);
                showError('Failed to rollback delivery');
            }
        }

        async function rollbackCabinet(orderId, deviceId, cabinetIndex) {
            if (!confirm('Are you sure you want to rollback this cabinet delivery?')) {
                return;
            }
            
            try {
                await api.makeRequest('POST', '/service-orders/rollback', {
                    serviceOrderId: orderId,
                    deviceId: deviceId,
                    cabinetIndex: cabinetIndex,
                    executedBy: 'current_user@example.com' // TODO: Get from session
                });
                
                showSuccess('Cabinet rollback successful');
                loadOrders();
                
            } catch (error) {
                console.error('Rollback failed:', error);
                showError('Failed to rollback delivery');
            }
        }

        // Filter functions
        function applyFilters() {
            currentFilters = {
                status: document.getElementById('statusFilter').value,
                routeId: document.getElementById('routeFilter').value,
                dateFrom: document.getElementById('dateFromFilter').value,
                dateTo: document.getElementById('dateToFilter').value
            };
            loadOrders();
        }

        function resetFilters() {
            document.getElementById('statusFilter').value = '';
            document.getElementById('routeFilter').value = '';
            document.getElementById('dateFromFilter').value = '';
            document.getElementById('dateToFilter').value = new Date().toISOString().split('T')[0];
            applyFilters();
        }

        // Auto-refresh setup
        function setupAutoRefresh() {
            // Check if there are pending orders
            const hasPending = currentOrders.some(o => o.status === 'pending');
            
            if (hasPending) {
                document.getElementById('autoRefreshIndicator').style.display = 'flex';
                
                // Refresh every 5 minutes
                autoRefreshTimer = setInterval(() => {
                    loadOrders();
                }, 5 * 60 * 1000);
            } else {
                document.getElementById('autoRefreshIndicator').style.display = 'none';
                
                if (autoRefreshTimer) {
                    clearInterval(autoRefreshTimer);
                    autoRefreshTimer = null;
                }
            }
        }

        // Update last updated timestamp
        function updateLastUpdated() {
            const now = new Date();
            const timeString = now.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            document.getElementById('lastUpdated').textContent = `Last updated: ${timeString}`;
        }

        // Utility functions
        function formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        function showSuccess(message) {
            // TODO: Implement toast notification
            console.log('Success:', message);
        }

        function showError(message) {
            // TODO: Implement toast notification
            console.error('Error:', message);
        }
    </script>
</body>
</html>
```

## Navigation Integration

### Update index.html

Add to the Services dropdown menu:
```javascript
// In pageRoutes object:
'#service-orders': 'pages/service-orders.html'

// In Services dropdown HTML:
<a href="#service-orders" class="dropdown-item">Service Orders</a>
```

## Implementation Order

1. **Database Updates**
   - Create service_visit_items table
   - Update service_visits table
   - Create necessary indexes

2. **Backend Implementation**
   - Implement calculate_fill_rates function
   - Create /api/service-orders/management endpoint
   - Create /api/service-orders/execute endpoint
   - Create /api/service-orders/rollback endpoint
   - Update ServiceOrderService class

3. **Frontend Development**
   - Create service-orders.html page
   - Test execution workflows
   - Test rollback functionality
   - Verify auto-refresh behavior

4. **Integration Testing**
   - Test complete order lifecycle
   - Verify inventory updates
   - Check audit trail creation
   - Validate fill rate calculations

## Key Implementation Notes

1. **Audit Trail**: Every action creates a new record - no updates to existing records
2. **Fill Rate Formula**: `((Delivered + Current) / Par Level) × 100%`
3. **Status Transitions**: Automatic based on delivery completion
4. **Auto-refresh**: Only active when pending orders exist
5. **Execution Levels**: Cabinet-level for granular control, Device-level for efficiency

## Success Metrics

- Managers can monitor all service orders in real-time
- Accurate inventory updates through execution
- Complete audit trail of all delivery actions
- Fill rates provide insight into delivery effectiveness
- Rollback capability ensures error correction