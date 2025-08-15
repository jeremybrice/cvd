---
type: architecture
category: system
title: Driver App Data Flow Analysis
status: active
last_updated: 2025-08-12
tags: [driver-app, pwa, data-flow, offline, sync]
cross_references:
  - /documentation/07-cvd-framework/service-orders/WORKFLOW_STATES.md
  - /documentation/03-architecture/patterns/API_PATTERNS.md
  - /documentation/02-requirements/guides/DRIVER_APP_GUIDE.md
---

# Driver App Data Flow Analysis Report

## Overview
This report provides a comprehensive analysis of all data points being received from and sent to the API by the CVD Driver PWA application.

## Authentication & User Data

### Data Received from API:
1. **User Authentication** (`GET /auth/current-user`)
   - `user.id` - User ID
   - `user.username` - Username 
   - `user.name` - Display name
   - `user.email` - Email address
   - `user.role` - User role (must be "driver")

### Data Sent to API:
1. **Logout** (`POST /auth/logout`)
   - No data payload required

## Service Orders

### Data Received from API:

1. **Get Service Orders List** (`GET /service-orders`)
   - Query parameters:
     - `date` - Filter by specific date
     - `status` - Filter by status (pending/in_progress/completed)
     - `dateFrom` - Date range start
     - `dateTo` - Date range end
   - Response data:
     - `id` - Order ID
     - `route_id` - Associated route ID
     - `created_at` - Creation timestamp
     - `created_by` - Creator user ID
     - `status` - Order status
     - `total_units` - Total units in order
     - `estimated_duration_minutes` - Estimated duration
     - `driver_id` - Assigned driver ID
     - `location` - Location name
     - `deviceCount` - Number of devices
     - `itemCount` - Total items count
     - `last_modified` - Last modification timestamp
     - `sync_version` - Version for sync conflict detection

2. **Get Single Service Order** (`GET /service-orders/{id}`)
   - All fields from list plus:
     - `route_name` - Route name
     - `driver_name` - Driver username
     - `driver_email` - Driver email
     - `cabinets` - Array of cabinet details:
       - `deviceId` - Device ID
       - `asset` - Asset number
       - `cooler` - Cooler/model name
       - `location` - Location name
       - `address` - Physical address
       - `cabinetIndex` - Cabinet index (0-2)
       - `cabinetType` - Type (Cooler/Freezer/etc)
       - `isExecuted` - Delivery status
       - `products` - Array of products:
         - `productName` - Product name
         - `quantityNeeded` - Quantity to deliver

### Data Sent to API:

1. **Update Order Status** (`PUT /service-orders/{id}`)
   - `status` - New status (pending/in_progress/completed)
   - `startTime` - Start timestamp (when starting)
   - `completedAt` - Completion timestamp (when completing)

2. **Sync Service Order** (`PUT /service-orders/{id}/sync`)
   - Complete order object with:
     - All order fields
     - `lastModified` - Client's last modification timestamp
     - `syncStatus` - Client sync status
   - Response handles conflicts:
     - `conflict` - Boolean indicating conflict
     - `serverVersion` - Server's version if conflict

3. **Execute Delivery** (`POST /service-orders/execute`)
   - `orderId` - Service order ID
   - `cabinetId` - Cabinet ID being delivered
   - `deliveredItems` - Array of delivered items:
     - `productId` - Product ID
     - `quantity` - Quantity delivered

## Routes

### Data Received from API:

1. **Get Routes** (`GET /routes`)
   - Query parameters:
     - `since` - Get updates since timestamp
   - Response data:
     - `id` - Route ID
     - `name` - Route name
     - `routeNumber` - Route number
     - `deviceCount` - Number of devices on route
     - `orderCount` - Number of orders

## Photos

### Data Sent to API:

1. **Upload Photo** (`POST /service-orders/photos`)
   - Form data:
     - `orderId` - Associated order ID
     - `photo` - Photo file (JPEG)
     - `timestamp` - Capture timestamp
     - `type` - Photo type (default: "delivery_proof")

### Data Received from API:

1. **Get Photos** (`GET /service-orders/{id}/photos`)
   - Response data:
     - `id` - Photo ID
     - `filename` - File name
     - `upload_timestamp` - Upload time
     - `uploaded_by` - Uploader user ID
     - `uploaded_by_name` - Uploader username

## Offline Storage & Sync

### IndexedDB Stores:

1. **serviceOrders**
   - Complete order objects with additional fields:
     - `syncStatus` - Local sync status (synced/pending)
     - `lastModified` - Local modification timestamp

2. **routes**
   - Complete route objects from API

3. **devices**
   - Device information (currently not actively used)

4. **offlineActions**
   - Queued actions when offline:
     - `type` - Action type
     - `timestamp` - Action timestamp
     - `retryCount` - Number of retry attempts
     - Action-specific data

5. **photos**
   - `id` - Local photo ID
   - `orderId` - Associated order
   - `data` - Base64 encoded image
   - `timestamp` - Capture time
   - `type` - Photo type
   - `uploaded` - Upload status
   - `createdAt` - Creation time
   - `uploadedAt` - Upload completion time

### Sync Operations:

1. **Automatic Sync** (every 5 minutes when online)
   - Process offline action queue
   - Sync modified service orders
   - Upload pending photos
   - Download updates from server

2. **Offline Action Types**:
   - `UPDATE_ORDER_STATUS` - Status changes
   - `COMPLETE_ORDER` - Order completion
   - `EXECUTE_DELIVERY` - Delivery execution
   - `UPLOAD_PHOTO` - Photo uploads

## Data Flow Patterns

### Online Mode:
1. All API calls are made directly
2. Data is cached in IndexedDB for offline access
3. Sync status is maintained as "synced"

### Offline Mode:
1. Data is read from IndexedDB
2. Modifications are saved locally with `syncStatus: "pending"`
3. Actions are queued in offlineActions store
4. When online, sync manager processes queue and updates

### Conflict Resolution:
1. Each order has `last_modified` and `sync_version`
2. Server detects conflicts based on version mismatch
3. Current implementation: server version wins
4. Conflicts are logged for review

## Security & Access Control

1. **Authentication Required**: All API endpoints require authentication
2. **Driver Role Filtering**: API automatically filters data for driver role
3. **Driver Access**: Drivers only see their assigned orders
4. **Session Management**: Uses HTTP-only cookies for security
5. **PWA Authentication**: Special handling for iOS/Android standalone mode

## Performance Optimizations

1. **Batch Operations**: Multiple items synced in single requests
2. **Incremental Sync**: Only changed data is synchronized
3. **Photo Compression**: Photos compressed to JPEG at 0.8 quality
4. **Old Photo Cleanup**: Photos deleted after 7 days
5. **Retry Logic**: Failed operations retry up to 3 times

## Error Handling

1. **Network Failures**: Graceful fallback to offline mode
2. **API Errors**: Actions queued for retry
3. **Sync Conflicts**: Automatic resolution with logging
4. **Photo Upload Failures**: Retained for later retry
5. **Authentication Failures**: Redirect to login with return URL

## Data Validation

1. **Required Fields**: Validated before API calls
2. **Status Transitions**: Only valid status changes allowed
3. **Role Verification**: Driver role checked on login
4. **Access Control**: Orders filtered by driver assignment

## Summary

The Driver PWA implements a comprehensive offline-first architecture with:
- Bidirectional data sync for service orders
- Offline photo capture and upload
- Automatic conflict resolution
- Robust error handling and retry logic
- Secure authentication with platform-specific handling
- Performance optimizations for mobile devices

The app maintains data consistency between online and offline modes while providing a seamless experience for drivers in areas with poor connectivity.
