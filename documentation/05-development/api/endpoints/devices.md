# Device Management API Endpoints


## Metadata
- **ID**: 05_DEVELOPMENT_API_ENDPOINTS_DEVICES
- **Type**: API Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #coding #data-exchange #debugging #development #device-management #dex-parser #integration #machine-learning #metrics #operations #optimization #performance #planogram #product-placement #reporting #security #service-orders #troubleshooting #vending-machine #workflows
- **Intent**: The device management endpoints handle the complete lifecycle of vending machines in the CVD system
- **Audience**: developers, system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/api/endpoints/
- **Category**: Endpoints
- **Search Keywords**: ###, ####, (200), (400), (500), **body:**, **parameters:**, **query, access, admin, all, api, asset, body:, bulk

## Overview

The device management endpoints handle the complete lifecycle of vending machines in the CVD system. Devices can have multiple cabinet configurations (up to 3 cabinets per device) and support soft delete operations with recovery capabilities.

## Device Data Model

### Device Object
```json
{
  "id": 1,
  "asset": "CVD001",
  "cooler": "Main Cooler",
  "location_id": 1,
  "location": "Warehouse",
  "model": "Vendo 721",
  "device_type_id": 1,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z",
  "deviceTypeDetails": {
    "id": 1,
    "name": "Single Cabinet",
    "description": "Standard single cabinet device",
    "allowsAdditionalCabinets": false
  },
  "cabinetConfiguration": [
    {
      "cabinetType": "Snack Cabinet",
      "modelName": "Standard 40",
      "isParent": true,
      "cabinetIndex": 0,
      "rows": 8,
      "columns": 5
    }
  ]
}
```

### Cabinet Configuration Object
```json
{
  "cabinetType": "Snack Cabinet",
  "modelName": "Standard 40",
  "isParent": true,
  "cabinetIndex": 0,
  "rows": 8,
  "columns": 5
}
```

---

## GET /api/devices

Get all active devices with their cabinet configurations.

### Request

**Headers:**
```
Cookie: session=<session_cookie>
```

**Query Parameters:**
- `search` (string, optional) - Search term for asset, cooler, or location
- `location_id` (integer, optional) - Filter by location ID
- `device_type_id` (integer, optional) - Filter by device type ID

### Response

#### Success (200)
```json
[
  {
    "id": 1,
    "asset": "CVD001",
    "cooler": "Main Cooler",
    "location_id": 1,
    "location": "Warehouse",
    "model": "Vendo 721",
    "device_type_id": 1,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z",
    "deviceTypeDetails": {
      "id": 1,
      "name": "Single Cabinet",
      "description": "Standard single cabinet device",
      "allowsAdditionalCabinets": false
    },
    "cabinetConfiguration": [
      {
        "cabinetType": "Snack Cabinet",
        "modelName": "Standard 40",
        "isParent": true,
        "cabinetIndex": 0,
        "rows": 8,
        "columns": 5
      }
    ]
  }
]
```

### Authorization Required
- **Admin**: Full access
- **Manager**: Full access
- **Driver**: View access only
- **Viewer**: View access only

### Notes

- Returns only non-deleted devices (`deleted_at IS NULL`)
- Devices are ordered by creation date (newest first)
- Cabinet configurations are ordered by parent status and cabinet index
- Includes device type details and location information
- Automatically creates planograms for each cabinet configuration

---

## POST /api/devices

Create a new device with cabinet configurations.

### Authorization Required
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
  "asset": "CVD002",
  "cooler": "Secondary Cooler",
  "location_id": 2,
  "model": "Dixie Narco 501E",
  "device_type_id": 2,
  "cabinetConfiguration": [
    {
      "cabinetType": "Snack Cabinet",
      "modelName": "Standard 40",
      "isParent": true
    },
    {
      "cabinetType": "Drink Cabinet",
      "modelName": "Beverage 60",
      "isParent": false
    }
  ]
}
```

**Parameters:**
- `asset` (string, required) - Unique asset identifier
- `cooler` (string, required) - Cooler name/description
- `location_id` (integer, optional) - Location ID (defaults to Warehouse)
- `model` (string, required) - Device model name
- `device_type_id` (integer, required) - Valid device type ID
- `cabinetConfiguration` (array, required) - Array of cabinet configurations

**Cabinet Configuration Parameters:**
- `cabinetType` (string, required) - Must match existing cabinet type name
- `modelName` (string, required) - Model name for the cabinet
- `isParent` (boolean, optional) - True for primary cabinet (defaults to first cabinet)

### Response

#### Success (201)
```json
{
  "id": 2,
  "asset": "CVD002",
  "cooler": "Secondary Cooler",
  "location_id": 2,
  "model": "Dixie Narco 501E",
  "device_type_id": 2,
  "cabinetConfiguration": [
    {
      "cabinetType": "Snack Cabinet",
      "modelName": "Standard 40",
      "isParent": true
    },
    {
      "cabinetType": "Drink Cabinet",
      "modelName": "Beverage 60",
      "isParent": false
    }
  ]
}
```

#### Validation Error (400)
```json
{
  "error": "device_type_id is required"
}
```

```json
{
  "error": "Invalid device type ID: 999"
}
```

```json
{
  "error": "Invalid cabinet type: Unknown Cabinet"
}
```

#### Duplicate Asset (400)
```json
{
  "error": "Device with this asset number already exists"
}
```

### Automatic Operations

When a device is created, the system automatically:

1. **Validates device type ID** - Ensures the device type exists
2. **Validates cabinet types** - Ensures all cabinet types exist
3. **Sets location defaults** - Uses Warehouse (ID 1) if no location specified
4. **Creates cabinet configurations** - Stores cabinet details with proper indexing
5. **Generates planograms** - Creates planogram for each cabinet with empty slots
6. **Creates planogram slots** - Populates all slots with sentinel product (ID 1)

### Notes

- Asset numbers must be unique across all devices
- Cabinet configurations are automatically indexed (0, 1, 2...)
- First cabinet is automatically marked as parent if not specified
- Planogram keys are generated as `{asset}-{cabinetType}-{cabinetIndex}`

---

## PUT /api/devices/{device_id}

Update an existing device.

### Authorization Required
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
  "asset": "CVD002-UPDATED",
  "cooler": "Updated Cooler Name",
  "location_id": 3,
  "model": "Updated Model"
}
```

**Parameters:**
- `asset` (string, optional) - Updated asset identifier
- `cooler` (string, optional) - Updated cooler name
- `location_id` (integer, optional) - Updated location ID
- `model` (string, optional) - Updated model name

### Response

#### Success (200)
```json
{
  "message": "Device updated successfully"
}
```

#### Device Not Found (404)
```json
{
  "error": "Device not found"
}
```

#### Duplicate Asset (400)
```json
{
  "error": "Device with this asset number already exists"
}
```

### Notes

- Only updates provided fields (partial updates supported)
- Asset numbers must remain unique
- Updates the `updated_at` timestamp
- Cannot update device type or cabinet configurations (requires delete/recreate)

---

## DELETE /api/devices/{device_id}

Soft delete a device and all related data.

### Authorization Required
- **Admin**: Full access
- **Manager**: Full access
- **Driver**: No access
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
  "message": "Device deleted successfully"
}
```

#### Device Not Found (404)
```json
{
  "error": "Device not found or already deleted"
}
```

### Soft Delete Behavior

When a device is deleted:

1. **Device marked as deleted** - Sets `deleted_at` timestamp and `deleted_by` user ID
2. **Planograms preserved** - Planogram data remains for historical purposes
3. **Service orders preserved** - Historical service orders remain accessible
4. **Recovery possible** - Deleted devices can be recovered by admins

### Notes

- This is a soft delete operation - data is preserved
- Deleted devices don't appear in normal device listings
- Admins can view and recover deleted devices
- Related planograms and service history are preserved

---

## POST /api/devices/bulk-delete

Delete multiple devices in a single operation.

### Authorization Required
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
  "deviceIds": [1, 2, 3, 4]
}
```

**Parameters:**
- `deviceIds` (array, required) - Array of device IDs to delete

### Response

#### Success (200)
```json
{
  "success": true,
  "deletedCount": 4
}
```

#### No Devices (200)
```json
{
  "success": true,
  "deletedCount": 0
}
```

### Notes

- Performs soft delete on all specified devices
- Returns count of successfully deleted devices
- Invalid device IDs are silently skipped
- Same soft delete behavior as single device delete

---

## GET /api/devices/{device_id}/metrics

Get performance metrics for a specific device.

### Authorization Required
- **Admin**: Full access
- **Manager**: Full access
- **Driver**: View access
- **Viewer**: View access

### Request

**Headers:**
```
Cookie: session=<session_cookie>
```

### Response

#### Success (200)
```json
{
  "deviceId": 1,
  "totalSales": 1250.75,
  "transactionCount": 125,
  "averageTransaction": 10.01,
  "topProducts": [
    {
      "productId": 2,
      "productName": "Coca-Cola",
      "sales": 450.00,
      "quantity": 45
    }
  ],
  "lastServiceDate": "2024-01-15T14:30:00Z",
  "serviceFrequency": 7
}
```

#### Device Not Found (404)
```json
{
  "error": "Device not found"
}
```

### Notes

- Calculates real-time metrics from sales data
- Includes top-performing products for the device
- Shows service history and frequency
- Used for device performance analysis

---

## POST /api/devices/metrics/batch

Get metrics for multiple devices in a single request.

### Authorization Required
- **Admin**: Full access
- **Manager**: Full access
- **Driver**: View access
- **Viewer**: View access

### Request

**Headers:**
```
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Body:**
```json
{
  "deviceIds": [1, 2, 3]
}
```

### Response

#### Success (200)
```json
{
  "metrics": {
    "1": {
      "deviceId": 1,
      "totalSales": 1250.75,
      "transactionCount": 125,
      "averageTransaction": 10.01
    },
    "2": {
      "deviceId": 2,
      "totalSales": 980.50,
      "transactionCount": 98,
      "averageTransaction": 10.00
    }
  }
}
```

#### Validation Error (400)
```json
{
  "error": "Device IDs array is required"
}
```

### Notes

- Efficiently retrieves metrics for multiple devices
- Returns metrics keyed by device ID
- Used for dashboard and reporting views
- Invalid device IDs are omitted from results

---

## GET /api/devices/{device_id}/service-history

Get service history for a device.

### Authorization Required
- **Admin**: Full access
- **Manager**: Full access
- **Driver**: View access
- **Viewer**: View access

### Request

**Headers:**
```
Cookie: session=<session_cookie>
```

**Query Parameters:**
- `limit` (integer, optional) - Maximum number of records (default: 50)
- `offset` (integer, optional) - Number of records to skip (default: 0)

### Response

#### Success (200)
```json
{
  "serviceHistory": [
    {
      "id": 1,
      "serviceType": "routine",
      "serviceDate": "2024-01-15T14:30:00Z",
      "duration": 45,
      "notes": "Regular restocking",
      "userName": "John Driver",
      "totalItems": 25,
      "cabinetIndex": 0
    }
  ],
  "totalCount": 15
}
```

#### Device Not Found (404)
```json
{
  "error": "Device not found"
}
```

### Notes

- Returns paginated service visit history
- Includes service details and user information
- Ordered by service date (most recent first)
- Shows service duration and items restocked

---

## GET /api/admin/devices/deleted

Get all soft-deleted devices (Admin only).

### Authorization Required
- **Admin**: Full access only

### Request

**Headers:**
```
Cookie: session=<session_cookie>
```

### Response

#### Success (200)
```json
[
  {
    "id": 1,
    "asset": "CVD001",
    "cooler": "Deleted Cooler",
    "location": "Warehouse",
    "model": "Old Model",
    "deleted_at": "2024-01-10T12:00:00Z",
    "deleted_by": 1,
    "deleted_by_username": "admin"
  }
]
```

#### Insufficient Permissions (403)
```json
{
  "error": "Insufficient permissions"
}
```

### Notes

- Only admins can view deleted devices
- Shows deletion timestamp and user who deleted
- Used for device recovery operations
- Includes basic device information for identification

---

## POST /api/admin/devices/{device_id}/recover

Recover a soft-deleted device (Admin only).

### Authorization Required
- **Admin**: Full access only

### Request

**Headers:**
```
Cookie: session=<session_cookie>
```

### Response

#### Success (200)
```json
{
  "message": "Device recovered successfully"
}
```

#### Device Not Found (404)
```json
{
  "error": "Device not found or not deleted"
}
```

#### Insufficient Permissions (403)
```json
{
  "error": "Insufficient permissions"
}
```

### Recovery Behavior

When a device is recovered:

1. **Clears deletion flags** - Sets `deleted_at` and `deleted_by` to NULL
2. **Restores full functionality** - Device appears in normal listings
3. **Preserves all data** - All historical data remains intact
4. **Updates timestamp** - Sets `updated_at` to current time

### Notes

- Only admins can recover deleted devices
- All related data (planograms, service history) is preserved
- Device immediately becomes available for normal operations
- Recovery action is logged to audit trail

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

#### Device Not Found (404)
```json
{
  "error": "Device not found"
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

#### Server Error (500)
```json
{
  "error": "Internal server error"
}
```

---

## Integration Examples

### Creating a New Device

```javascript
const deviceData = {
  asset: "CVD003",
  cooler: "New Cooler",
  location_id: 2,
  model: "Vendo 721",
  device_type_id: 1,
  cabinetConfiguration: [
    {
      cabinetType: "Snack Cabinet",
      modelName: "Standard 40",
      isParent: true
    }
  ]
};

const response = await fetch('/api/devices', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(deviceData)
});

const result = await response.json();
console.log('Device created:', result);
```

### Updating Device Information

```javascript
const updateData = {
  cooler: "Updated Cooler Name",
  location_id: 3
};

const response = await fetch(`/api/devices/${deviceId}`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(updateData)
});
```

### Bulk Delete Devices

```javascript
const deviceIds = [1, 2, 3];

const response = await fetch('/api/devices/bulk-delete', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ deviceIds })
});
```

### Getting Device Metrics

```javascript
// Single device metrics
const metricsResponse = await fetch(`/api/devices/${deviceId}/metrics`);
const metrics = await metricsResponse.json();

// Batch metrics
const batchResponse = await fetch('/api/devices/metrics/batch', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ deviceIds: [1, 2, 3] })
});
const batchMetrics = await batchResponse.json();
```