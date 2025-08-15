---
type: technical-reference
category: system
title: Driver App Detailed Data Points Structure
status: active
last_updated: 2025-08-12
tags: [driver-app, pwa, api, data-structures, indexeddb]
cross_references:
  - /documentation/03-architecture/system/DRIVER_APP_DATA_FLOW.md
  - /documentation/05-development/api/endpoints/service-orders.md
  - /documentation/07-cvd-framework/service-orders/OVERVIEW.md
---

# Driver App Detailed Data Points Report

## 1. Authentication Data Points

### API Endpoint: `GET /auth/current-user`
**Response Object Structure:**
```javascript
response = {
    user: {
        id: number,
        username: string,
        name: string,
        email: string,
        role: string  // Must be "driver" for app access
    }
}
```

**Code Usage (app.js:136-138):**
```javascript
currentUser = response.user;
// Stored globally and used in:
// - updateUserInfo() 
// - checkActiveRoute()
// - saveToLocalStorage()
```

### API Endpoint: `POST /auth/logout`
**No request payload**

## 2. Service Orders Data Points

### API Endpoint: `GET /service-orders`

**Query Parameters (app.js:416-420):**
```javascript
endpoint = '/service-orders?status=' + filter
endpoint = '/service-orders?date=' + today  // Format: "YYYY-MM-DD"
```

**Response Handling (app.js:299-305):**
```javascript
// Handles both formats:
if (Array.isArray(response)) {
    serviceOrders = response;
} else if (response.orders) {
    serviceOrders = response.orders;
}
```

**Service Order Object Structure:**
```javascript
serviceOrder = {
    id: number,
    route_id: number,
    created_at: string,  // ISO timestamp
    created_by: number,
    status: string,      // "pending" | "in_progress" | "completed" | "cancelled"
    total_units: number,
    estimated_duration_minutes: number,
    driver_id: number,
    location: string,    // Used in app.js:460
    deviceCount: number, // Used in app.js:461
    itemCount: number,   // Used in app.js:462
    last_modified: string,  // ISO timestamp
    sync_version: number
}
```

### API Endpoint: `GET /service-orders/{id}`

**Additional Response Fields (order-detail.js:41-43):**
```javascript
currentOrder = {
    ...serviceOrder,  // All fields from above
    cabinets: [       // Array of cabinet objects
        {
            deviceId: number,
            asset: string,
            cooler: string,        // Model name
            location: string,
            address: string,
            cabinetIndex: number,  // 0-2
            cabinetType: string,   // "Cooler" | "Freezer" | "Ambient" | "Ambient+"
            isExecuted: boolean,
            products: [            // Array of products
                {
                    productName: string,
                    quantityNeeded: number
                }
            ]
        }
    ]
}
```

### API Endpoint: `PUT /service-orders/{id}`

**Request Payload (order-detail.js:209-211):**
```javascript
data = {
    status: string,      // "pending" | "in_progress" | "completed"
    startTime: string,   // ISO timestamp (optional)
    completedAt: string  // ISO timestamp (optional)
}
```

### API Endpoint: `PUT /service-orders/{id}/sync`

**Request Payload (sync-manager.js:198-201):**
```javascript
data = {
    ...order,           // Complete order object
    lastModified: string,  // order.lastModified
    syncStatus: string     // Not sent to server, local only
}
```

**Response Structure:**
```javascript
response = {
    conflict: boolean,
    serverVersion: object  // Complete order object if conflict
}
```

### API Endpoint: `POST /service-orders/execute`

**Request Payload (from offline action queue):**
```javascript
data = {
    orderId: number,
    cabinetId: number,
    deliveredItems: [
        {
            productId: number,
            quantity: number
        }
    ]
}
```

## 3. Routes Data Points

### API Endpoint: `GET /routes`

**Query Parameters (sync-manager.js:262-264):**
```javascript
params = {
    since: string  // ISO timestamp for incremental updates
}
```

**Response Structure (app.js:361-363):**
```javascript
response = {
    routes: [
        {
            id: number,
            name: string,
            routeNumber: string,
            deviceCount: number,  // Used in app.js:402
            orderCount: number    // Used in app.js:404
        }
    ]
}
```

## 4. Photo Data Points

### API Endpoint: `POST /service-orders/photos`

**FormData Structure (sync-manager.js:235-240):**
```javascript
formData.append('orderId', photo.orderId);        // number as string
formData.append('photo', blob, filename);          // Blob file
formData.append('timestamp', photo.timestamp);     // ISO string
formData.append('type', photo.type);              // "delivery_proof"
```

**Local Photo Storage (order-detail.js:368-373):**
```javascript
photoData = {
    orderId: number,
    data: string,      // Base64 data URL
    timestamp: string, // ISO timestamp
    type: string       // "delivery_proof"
}
```

### API Endpoint: `GET /service-orders/{id}/photos`

**Response Structure:**
```javascript
photos = [
    {
        id: number,
        filename: string,
        upload_timestamp: string,
        uploaded_by: number,
        uploaded_by_name: string
    }
]
```

## 5. IndexedDB Storage Structures

### Store: `serviceOrders` (db.js:23-28)
```javascript
{
    id: number,              // Primary key
    ...serviceOrderFields,   // All API fields
    syncStatus: string,      // "synced" | "pending"
    lastModified: string     // ISO timestamp
}
```

### Store: `routes` (db.js:31-34)
```javascript
{
    id: number,              // Primary key
    name: string,
    routeNumber: string,
    deviceCount: number,
    orderCount: number
}
```

### Store: `offlineActions` (db.js:43-47)
```javascript
{
    id: number,              // Auto-increment
    type: string,            // Action type
    timestamp: string,       // ISO timestamp
    retryCount: number,      // Retry attempts
    // Type-specific fields:
    orderId?: number,
    status?: string,
    startTime?: string,
    completedAt?: string,
    data?: object
}
```

**Action Types (sync-manager.js:160-185):**
- `UPDATE_ORDER_STATUS`
- `COMPLETE_ORDER`
- `EXECUTE_DELIVERY`
- `UPLOAD_PHOTO`

### Store: `photos` (db.js:50-54)
```javascript
{
    id: string,              // "photo_[timestamp]_[random]"
    orderId: number,
    data: string,            // Base64 data URL
    timestamp: string,       // Capture time
    type: string,            // "delivery_proof"
    uploaded: boolean,
    createdAt: string,       // ISO timestamp
    uploadedAt?: string      // ISO timestamp when uploaded
}
```

### Store: `devices` (db.js:37-40)
```javascript
{
    id: number,              // Primary key
    asset: string            // Unique index
}
```

## 6. Offline Action Queue Structures

### UPDATE_ORDER_STATUS Action (order-detail.js:189-195)
```javascript
{
    type: 'UPDATE_ORDER_STATUS',
    orderId: number,
    status: string,
    startTime?: string,      // ISO timestamp
    timestamp: string        // Action timestamp
}
```

### COMPLETE_ORDER Action (order-detail.js:259-263)
```javascript
{
    type: 'COMPLETE_ORDER',
    orderId: number,
    completedAt: string      // ISO timestamp
}
```

### UPLOAD_PHOTO Action (order-detail.js:383-387)
```javascript
{
    type: 'UPLOAD_PHOTO',
    photoId: string,         // Local photo ID
    orderId: number
}
```

## 7. LocalStorage Keys

### Sync State (sync-manager.js:24-35)
```javascript
localStorage.setItem('cvd_sync_state', JSON.stringify({
    lastSyncTime: Date  // Converted to/from ISO string
}));
```

### Fallback Storage (app.js:589-593)
```javascript
localStorage.setItem('driver_orders', JSON.stringify(serviceOrders));
localStorage.setItem('driver_routes', JSON.stringify(routes));
localStorage.setItem('driver_user', JSON.stringify(currentUser));
```

## 8. Event System Data

### Custom Events Dispatched

**Sync Events (sync-manager.js:309-325):**
```javascript
// sync:start
window.dispatchEvent(new CustomEvent('sync:start'));

// sync:success
window.dispatchEvent(new CustomEvent('sync:success', {
    detail: { lastSyncTime: Date }
}));

// sync:error
window.dispatchEvent(new CustomEvent('sync:error', {
    detail: { error: string }  // error.message
}));
```

**Location Events (Referenced in app.js:122-123):**
```javascript
// locationupdate
window.dispatchEvent(new CustomEvent('locationupdate', {
    detail: {
        latitude: number,
        longitude: number,
        accuracy: number,
        timestamp: Date
    }
}));

// locationerror
window.dispatchEvent(new CustomEvent('locationerror', {
    detail: { error: GeolocationPositionError }
}));
```

**Push Notification Events (app.js:126):**
```javascript
// pushstatus
window.dispatchEvent(new CustomEvent('pushstatus', {
    detail: { status: string }  // "enabled" | "disabled"
}));
```

## 9. UI Data Bindings

### Dashboard Elements (app.js:349-352)
```javascript
document.getElementById('todayOrders').textContent = todayOrders;      // number
document.getElementById('completedOrders').textContent = completedOrders; // number
document.getElementById('pendingOrders').textContent = pendingOrders;   // number
document.getElementById('totalStops').textContent = uniqueStops;        // number
```

### Order List Rendering (app.js:453-465)
```javascript
// Each order item displays:
order.id            // Order number
order.status        // Status badge
order.location      // Location name
order.deviceCount   // Device count
order.itemCount     // Item count
```

### Order Detail Page (order-detail.js:67-77)
```javascript
document.getElementById('orderNumber').textContent = currentOrder.id;
document.getElementById('orderStatus').textContent = currentOrder.status;
document.getElementById('orderDate').textContent = new Date(currentOrder.createdAt).toLocaleDateString();
document.getElementById('locationName').textContent = firstDevice.location;
document.getElementById('locationAddress').textContent = firstDevice.address;
```

### Cabinet Display (order-detail.js:110-147)
```javascript
// Device grouping structure:
deviceGroups[cabinet.deviceId] = {
    deviceId: number,
    asset: string,
    cooler: string,
    location: string,
    cabinets: []  // Array of cabinet objects
}

// Cabinet display data:
cabinet.cabinetIndex    // Cabinet number (0-based)
cabinet.cabinetType     // Type name
cabinet.isExecuted      // Delivery status
cabinet.products        // Product array
```

## 10. Camera/Photo Capture Data

### Video Stream Configuration (order-detail.js:295-301)
```javascript
constraints = {
    video: {
        facingMode: 'environment',
        width: { ideal: 1920 },
        height: { ideal: 1080 }
    }
}
```

### Canvas Capture Settings (order-detail.js:332-345)
```javascript
canvas.width = video.videoWidth;
canvas.height = video.videoHeight;
canvas.toBlob(callback, 'image/jpeg', 0.8);  // JPEG at 80% quality
```

## 11. API Response Format Handling

### Flexible Response Parsing (app.js:299-305, 426-429)
```javascript
// Service orders can be:
// 1. Direct array: response = [...]
// 2. Object wrapper: response = { orders: [...] }

if (Array.isArray(response)) {
    serviceOrders = response;
} else if (response.orders) {
    serviceOrders = response.orders;
}
```

## 12. Error States and Fallbacks

### Offline Fallback Chain (app.js:317-338)
1. Try API request
2. On failure, load from IndexedDB
3. If IndexedDB empty, load from localStorage
4. Update UI with available data

### Retry Mechanism (sync-manager.js:143-152)
```javascript
action.retryCount = (action.retryCount || 0) + 1;
if (action.retryCount > 3) {
    // Remove after 3 retries
    await offlineDB.removeOfflineAction(action.id);
}
```

This report documents every data point, field name, and structure exactly as used in the Driver PWA codebase.
