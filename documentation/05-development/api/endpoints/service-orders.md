# Service Order API Endpoints


## Metadata
- **ID**: 05_DEVELOPMENT_API_ENDPOINTS_SERVICE_ORDERS
- **Type**: API Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #authentication #coding #data-exchange #debugging #development #device-management #dex-parser #driver-app #integration #logistics #machine-learning #mobile #operations #optimization #planogram #product-placement #pwa #quality-assurance #route-management #security #service-orders #testing #troubleshooting #vending-machine #workflows
- **Intent**: The service order endpoints manage the complete lifecycle of service orders for vending machine maintenance and restocking
- **Audience**: developers, system administrators, managers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/api/endpoints/
- **Category**: Endpoints
- **Search Keywords**: ###, ####, (500), **body:**, **form, **parameters:**, **query, access, admin, all, api, body:, cabinet, calculates, cancelled

## Overview

The service order endpoints manage the complete lifecycle of service orders for vending machine maintenance and restocking. Service orders use a cabinet-centric approach where individual cabinets within devices can be serviced independently. The system integrates with the `service_order_service.py` implementation for core business logic.

## Service Order Data Model

### Service Order Object
```json
{
  "id": 1,
  "routeId": 1,
  "routeName": "Downtown Route",
  "createdAt": "2024-01-15T10:00:00Z",
  "createdBy": 1,
  "status": "pending",
  "totalUnits": 45,
  "estimatedDurationMinutes": 30,
  "driverId": 2,
  "driverName": "john_driver",
  "driverEmail": "john@example.com",
  "lastModified": "2024-01-15T10:00:00Z",
  "deviceCount": 2,
  "itemCount": 8,
  "location": "Office Building A, Warehouse"
}
```

### Pick List Item Object
```json
{
  "productId": 2,
  "productName": "Coca-Cola",
  "category": "Beverages",
  "quantity": 15
}
```

### Cabinet Selection Object
```json
{
  "deviceId": 1,
  "cabinetIndex": 0
}
```

## Service Order States

Service orders follow a defined workflow:

- **pending** - Created, awaiting driver execution
- **in_progress** - Driver has started working on cabinets
- **completed** - All cabinets have been serviced
- **cancelled** - Order was cancelled before completion

---

## GET /api/service-orders

Get service orders with optional filtering.

### Authentication Required
This endpoint requires a valid session.

### Authorization
- **Admin**: View all service orders
- **Manager**: View all service orders  
- **Driver**: View only assigned service orders
- **Viewer**: View all service orders

### Request

**Headers:**
```
Cookie: session=<session_cookie>
```

**Query Parameters:**
- `routeId` (integer, optional) - Filter by route ID
- `status` (string, optional) - Filter by status (pending, in_progress, completed)
- `date` (string, optional) - Filter by specific date (YYYY-MM-DD)
- `dateFrom` (string, optional) - Filter from date (YYYY-MM-DD)
- `dateTo` (string, optional) - Filter to date (YYYY-MM-DD)

### Response

#### Success (200)
```json
{
  "orders": [
    {
      "id": 1,
      "routeId": 1,
      "routeName": "Downtown Route",
      "createdAt": "2024-01-15T10:00:00Z",
      "createdBy": 1,
      "status": "pending",
      "totalUnits": 45,
      "estimatedDurationMinutes": 30,
      "driverId": 2,
      "driverName": "john_driver",
      "driverEmail": "john@example.com",
      "lastModified": "2024-01-15T10:00:00Z",
      "deviceCount": 2,
      "itemCount": 8,
      "location": "Office Building A, Warehouse"
    }
  ],
  "avgFillRate": 65.4
}
```

### Driver Filtering

When the authenticated user has the `driver` role, the response is automatically filtered to show only service orders assigned to that driver (`driver_id = user.id`).

### Notes

- Limited to 100 most recent orders
- Orders sorted by creation date (newest first)
- Includes aggregated statistics (device count, item count, locations)
- Calculates average fill rate across pending/in-progress orders

---

## POST /api/service-orders

Create a new service order from cabinet selections.

### Authentication Required
This endpoint requires a valid session.

### Authorization
- **Admin**: Full access
- **Manager**: Full access
- **Driver**: No access
- **Viewer**: No access

### Request

**Headers:**
```
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Body:**
```json
{
  "routeId": 1,
  "cabinetSelections": [
    {
      "deviceId": 1,
      "cabinetIndex": 0
    },
    {
      "deviceId": 2,
      "cabinetIndex": 1
    }
  ],
  "createdBy": 1
}
```

**Parameters:**
- `routeId` (integer, required) - Route ID for the service order
- `cabinetSelections` (array, required) - Array of cabinet selections
- `createdBy` (integer, optional) - User ID creating the order

**Cabinet Selection Parameters:**
- `deviceId` (integer, required) - Device ID containing the cabinet
- `cabinetIndex` (integer, required) - Index of cabinet within device (0, 1, 2)

### Response

#### Success (201)
```json
{
  "orderId": 1,
  "totalUnits": 45,
  "estimatedMinutes": 30,
  "pickList": [
    {
      "productId": 2,
      "productName": "Coca-Cola",
      "category": "Beverages",
      "quantity": 15
    },
    {
      "productId": 3,
      "productName": "Pepsi",
      "category": "Beverages", 
      "quantity": 10
    }
  ]
}
```

#### Validation Error (400)
```json
{
  "error": "routeId and cabinetSelections are required"
}
```

#### Server Error (500)
```json
{
  "error": "Cabinet configuration not found for device 1, cabinet 0"
}
```

### Service Order Creation Process

When a service order is created, the system:

1. **Validates route and driver** - Ensures route exists and has assigned driver
2. **Calculates pick list** - Aggregates products needed across all selected cabinets
3. **Estimates duration** - 10 minutes per cabinet plus travel time
4. **Creates order record** - Stores order with pending status
5. **Creates cabinet entries** - Links each cabinet to the service order
6. **Creates item requirements** - Stores quantity needed for each product per cabinet

### Pick List Calculation

The pick list aggregates products needed across all cabinets:
- Only includes products where `quantity < par_level`
- Excludes sentinel product (ID 1)
- Groups by product ID and sums quantities
- Sorts by category and product name

---

## GET /api/service-orders/{order_id}

Get detailed information about a specific service order.

### Authentication Required
This endpoint requires a valid session.

### Request

**Headers:**
```
Cookie: session=<session_cookie>
```

### Response

#### Success (200)
```json
{
  "id": 1,
  "routeId": 1,
  "routeName": "Downtown Route",
  "createdAt": "2024-01-15T10:00:00Z",
  "createdBy": 1,
  "status": "pending",
  "totalUnits": 45,
  "estimatedDurationMinutes": 30,
  "driverId": 2,
  "driverName": "john_driver",
  "driverEmail": "john@example.com",
  "cabinets": [
    {
      "cabinetOrderId": 1,
      "cabinetId": 1,
      "deviceId": 1,
      "cabinetIndex": 0,
      "cabinetType": "Snack Cabinet",
      "asset": "CVD001",
      "cooler": "Main Cooler",
      "location": "Office Building A",
      "isExecuted": false,
      "serviceVisitId": null,
      "fillRate": 45.5,
      "items": [
        {
          "productId": 2,
          "productName": "Coca-Cola",
          "quantityNeeded": 8
        }
      ]
    }
  ],
  "devices": {
    "1": {
      "asset": "CVD001",
      "cooler": "Main Cooler",
      "location": "Office Building A",
      "cabinetCount": 1,
      "cabinetIndices": [0]
    }
  }
}
```

#### Service Order Not Found (404)
```json
{
  "error": "Service order not found"
}
```

### Notes

- Includes complete cabinet details with items needed
- Shows execution status for each cabinet
- Calculates fill rates for each cabinet
- Groups devices for summary display
- Used for service order detail views and execution

---

## GET /api/service-orders/{order_id}/pick-list

Get aggregated pick list for a service order.

### Authentication Required
This endpoint requires a valid session.

### Request

**Headers:**
```
Cookie: session=<session_cookie>
```

### Response

#### Success (200)
```json
{
  "pickList": [
    {
      "productId": 2,
      "productName": "Coca-Cola",
      "category": "Beverages",
      "quantity": 15,
      "locations": ["Office Building A", "Warehouse"]
    },
    {
      "productId": 3,
      "productName": "Pepsi",
      "category": "Beverages",
      "quantity": 10,
      "locations": ["Office Building A"]
    }
  ],
  "totalUnits": 25,
  "categories": ["Beverages", "Snacks"]
}
```

#### Service Order Not Found (404)
```json
{
  "error": "Service order not found"
}
```

### Notes

- Aggregates quantities across all cabinets in the order
- Shows locations where each product is needed
- Groups by category for efficient picking
- Used for driver pick list generation and inventory planning

---

## PUT /api/service-orders/{order_id}

Update service order status.

### Authentication Required
This endpoint requires a valid session.

### Authorization
- **Admin**: Full access
- **Manager**: Full access
- **Driver**: Can update assigned orders
- **Viewer**: No access

### Request

**Headers:**
```
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Body:**
```json
{
  "status": "in_progress"
}
```

**Parameters:**
- `status` (string, required) - New status (pending, in_progress, completed, cancelled)

### Response

#### Success (200)
```json
{
  "message": "Service order status updated successfully"
}
```

#### Validation Error (400)
```json
{
  "error": "Status is required"
}
```

#### Service Order Not Found (404)
```json
{
  "error": "Service order not found"
}
```

### Notes

- Updates the `last_modified` timestamp
- Status transitions are validated (e.g., cannot go from completed to pending)
- Used for manual status updates and workflow management

---

## POST /api/service-orders/cabinets/{cabinet_order_id}/execute

Execute service for a specific cabinet within a service order.

### Authentication Required
This endpoint requires a valid session.

### Authorization
- **Admin**: Full access
- **Manager**: Full access
- **Driver**: Can execute assigned orders
- **Viewer**: No access

### Request

**Headers:**
```
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Body:**
```json
{
  "deliveredItems": [
    {
      "productId": 2,
      "quantityFilled": 8
    },
    {
      "productId": 3,
      "quantityFilled": 5
    }
  ]
}
```

**Parameters:**
- `deliveredItems` (array, required) - Array of delivered product quantities

**Delivered Item Parameters:**
- `productId` (integer, required) - Product ID being restocked
- `quantityFilled` (integer, required) - Actual quantity delivered

### Response

#### Success (200)
```json
{
  "success": true,
  "serviceVisitId": 1,
  "totalUnits": 13
}
```

#### Validation Error (400)
```json
{
  "error": "deliveredItems array is required"
}
```

#### Cabinet Not Found (404)
```json
{
  "error": "Service order cabinet not found"
}
```

### Cabinet Execution Process

When a cabinet is executed:

1. **Creates service visit** - Records the service activity
2. **Records delivered items** - Stores actual quantities delivered
3. **Updates planogram quantities** - Adds delivered quantities to current stock
4. **Checks order completion** - Updates order status if all cabinets are executed
5. **Updates order status** - Changes from pending to in_progress, or to completed

### Notes

- Cabinet-centric execution allows partial order completion
- Actual delivered quantities may differ from needed quantities
- Planogram stock levels are immediately updated
- Service visit includes duration tracking (10 minutes default)

---

## POST /api/service-orders/cabinets/{cabinet_order_id}/rollback

Rollback a previously executed cabinet.

### Authentication Required
This endpoint requires a valid session.

### Authorization
- **Admin**: Full access
- **Manager**: Full access
- **Driver**: Limited access
- **Viewer**: No access

### Request

**Headers:**
```
Cookie: session=<session_cookie>
```

### Response

#### Success (200)
```json
{
  "success": true,
  "message": "Cabinet execution rolled back successfully"
}
```

#### Cabinet Not Found (404)
```json
{
  "error": "Service order cabinet not found or not executed"
}
```

### Rollback Process

When a cabinet execution is rolled back:

1. **Finds service visit** - Locates the associated service visit record
2. **Reverses planogram updates** - Subtracts delivered quantities from current stock
3. **Removes service records** - Deletes service visit and item records
4. **Updates order status** - May change from completed back to in_progress

### Notes

- Only executed cabinets can be rolled back
- Reverses all inventory changes from the original execution
- Used for error correction and testing
- Should be used carefully to maintain inventory accuracy

---

## POST /api/service-orders/preview

Generate a preview of what a service order would contain.

### Authentication Required
This endpoint requires a valid session.

### Request

**Headers:**
```
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Body:**
```json
{
  "routeId": 1,
  "cabinetSelections": [
    {
      "deviceId": 1,
      "cabinetIndex": 0
    }
  ],
  "serviceDate": "2024-01-20"
}
```

**Parameters:**
- `routeId` (integer, required) - Route ID for the preview
- `cabinetSelections` (array, required) - Cabinet selections to preview
- `serviceDate` (string, optional) - Target service date for planning

### Response

#### Success (200)
```json
{
  "cabinets": [
    {
      "deviceId": 1,
      "asset": "CVD001",
      "cooler": "Main Cooler",
      "location": "Office Building A",
      "cabinetIndex": 0,
      "cabinetType": "Snack Cabinet",
      "products": [
        {
          "productId": 2,
          "productName": "Coca-Cola",
          "category": "Beverages",
          "quantityNeeded": 8
        }
      ],
      "totalUnits": 8
    }
  ],
  "deviceSummary": {
    "1": {
      "asset": "CVD001",
      "cooler": "Main Cooler",
      "location": "Office Building A",
      "cabinetCount": 1,
      "cabinetIndices": [0]
    }
  },
  "pickList": [
    {
      "productId": 2,
      "productName": "Coca-Cola",
      "category": "Beverages",
      "quantity": 8
    }
  ],
  "totalUnits": 8,
  "estimatedMinutes": 10
}
```

### Notes

- Does not create an actual service order
- Uses current planogram data to calculate needs
- Provides detailed breakdown by cabinet and device
- Used for service order planning and validation
- Supports future service date planning

---

## POST /api/service-orders/execute

Execute service order delivery (Driver App specific).

### Authentication Required
This endpoint requires a valid session.

### Request

**Headers:**
```
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Body:**
```json
{
  "orderId": 1,
  "deliveries": [
    {
      "cabinetOrderId": 1,
      "products": [
        {
          "productId": 2,
          "quantityDelivered": 8
        }
      ],
      "location": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "accuracy": 10
      },
      "timestamp": "2024-01-15T14:30:00Z"
    }
  ]
}
```

### Response

#### Success (200)
```json
{
  "success": true,
  "orderStatus": "completed",
  "totalDelivered": 8
}
```

### Notes

- Enhanced version for mobile driver app
- Includes location tracking and timestamps
- Supports batch execution of multiple cabinets
- Used for offline-capable mobile execution

---

## PUT /api/service-orders/{order_id}/sync

Synchronize service order with conflict detection (Driver App specific).

### Authentication Required
This endpoint requires a valid session.

### Request

**Headers:**
```
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Body:**
```json
{
  "lastSync": "2024-01-15T10:00:00Z",
  "changes": [
    {
      "type": "cabinet_executed",
      "cabinetOrderId": 1,
      "timestamp": "2024-01-15T14:30:00Z",
      "data": {
        "deliveredItems": [
          {
            "productId": 2,
            "quantityFilled": 8
          }
        ]
      }
    }
  ]
}
```

### Response

#### Success (200)
```json
{
  "success": true,
  "conflicts": [],
  "serverChanges": []
}
```

#### Conflict Detected (409)
```json
{
  "success": false,
  "conflicts": [
    {
      "type": "concurrent_modification",
      "resource": "cabinet_1",
      "clientChange": { /* client data */ },
      "serverChange": { /* server data */ }
    }
  ]
}
```

### Notes

- Supports offline mobile app synchronization
- Detects and reports conflicts for manual resolution
- Maintains data consistency across devices
- Used for offline-first driver app architecture

---

## POST /api/service-orders/photos

Upload photo for service order documentation.

### Authentication Required
This endpoint requires a valid session.

### Request

**Headers:**
```
Cookie: session=<session_cookie>
Content-Type: multipart/form-data
```

**Form Data:**
- `photo` (file, required) - Image file (JPEG, PNG)
- `orderId` (integer, required) - Service order ID
- `cabinetOrderId` (integer, optional) - Specific cabinet order ID
- `description` (string, optional) - Photo description

### Response

#### Success (200)
```json
{
  "success": true,
  "photoId": 1,
  "filename": "service_photo_1642259400.jpg"
}
```

#### Validation Error (400)
```json
{
  "error": "No photo provided"
}
```

### Notes

- Supports JPEG and PNG formats
- Photos are associated with service orders and specific cabinets
- Used for service verification and documentation
- File names are timestamped for uniqueness

---

## GET /api/service-orders/{order_id}/photos

Get photos associated with a service order.

### Authentication Required
This endpoint requires a valid session.

### Request

**Headers:**
```
Cookie: session=<session_cookie>
```

### Response

#### Success (200)
```json
{
  "photos": [
    {
      "id": 1,
      "filename": "service_photo_1642259400.jpg",
      "description": "Before service",
      "cabinetOrderId": 1,
      "uploadedAt": "2024-01-15T14:30:00Z",
      "uploadedBy": 2
    }
  ]
}
```

### Notes

- Returns all photos for the service order
- Includes metadata and cabinet associations
- Used for service documentation and verification

---

## Error Handling

### Common Error Responses

#### Authentication Required (401)
```json
{
  "error": "Authentication required"
}
```

#### Insufficient Permissions (403)
```json
{
  "error": "Insufficient permissions"
}
```

#### Service Order Not Found (404)
```json
{
  "error": "Service order not found"
}
```

#### Validation Error (400)
```json
{
  "error": "Validation error message",
  "details": {
    "field": "specific validation error"
  }
}
```

#### Business Logic Error (500)
```json
{
  "error": "Cabinet configuration not found for device 1, cabinet 0"
}
```

---

## Integration Examples

### Creating a Service Order

```javascript
const orderData = {
  routeId: 1,
  cabinetSelections: [
    { deviceId: 1, cabinetIndex: 0 },
    { deviceId: 2, cabinetIndex: 1 }
  ],
  createdBy: 1
};

const response = await fetch('/api/service-orders', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(orderData)
});

const result = await response.json();
console.log('Service order created:', result);
```

### Executing a Cabinet

```javascript
const deliveryData = {
  deliveredItems: [
    { productId: 2, quantityFilled: 8 },
    { productId: 3, quantityFilled: 5 }
  ]
};

const response = await fetch(`/api/service-orders/cabinets/${cabinetOrderId}/execute`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(deliveryData)
});

const result = await response.json();
console.log('Cabinet executed:', result);
```

### Getting Service Orders for Driver

```javascript
// For drivers, automatically filtered to their assigned orders
const response = await fetch('/api/service-orders?status=pending');
const data = await response.json();

console.log('Pending orders:', data.orders);
console.log('Average fill rate:', data.avgFillRate);
```

### Uploading Service Photo

```javascript
const formData = new FormData();
formData.append('photo', photoFile);
formData.append('orderId', orderId);
formData.append('cabinetOrderId', cabinetOrderId);
formData.append('description', 'Service completion photo');

const response = await fetch('/api/service-orders/photos', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log('Photo uploaded:', result);
```