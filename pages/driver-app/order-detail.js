// Initialize API client
const api = new CVDApi();

// Order detail functionality
let currentOrder = null;
let currentLocation = null;
let deliveryStartTime = null;
let capturedPhoto = null;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Get order ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const orderId = urlParams.get('id');
    
    if (!orderId) {
        alert('Invalid order ID');
        history.back();
        return;
    }

    // Initialize offline DB
    await offlineDB.init();

    // Load order details
    await loadOrderDetails(orderId);
    
    // Update sync indicator
    updateSyncIndicator();
    
    // Listen for online/offline events
    window.addEventListener('online', updateSyncIndicator);
    window.addEventListener('offline', updateSyncIndicator);
});

// Load order details
async function loadOrderDetails(orderId) {
    try {
        // Try to load from server first
        if (navigator.onLine) {
            const response = await api.makeRequest('GET', `/service-orders/${orderId}`);
            if (response) {
                currentOrder = response;
                // Save to offline DB
                await offlineDB.saveServiceOrder(currentOrder);
            }
        } else {
            // Load from offline DB
            currentOrder = await offlineDB.get('serviceOrders', parseInt(orderId));
        }

        if (!currentOrder) {
            throw new Error('Order not found');
        }

        renderOrderDetails();
    } catch (error) {
        console.error('Failed to load order:', error);
        alert('Failed to load order details');
        history.back();
    }
}

// Render order details
function renderOrderDetails() {
    // Update order summary
    document.getElementById('orderNumber').textContent = currentOrder.id;
    document.getElementById('orderStatus').textContent = currentOrder.status;
    document.getElementById('orderStatus').className = `order-status status-${currentOrder.status}`;
    document.getElementById('orderDate').textContent = new Date(currentOrder.createdAt).toLocaleDateString();

    // Update location (using first device location for now)
    const firstDevice = currentOrder.cabinets && currentOrder.cabinets[0];
    if (firstDevice) {
        document.getElementById('locationName').textContent = firstDevice.location || 'Unknown Location';
        document.getElementById('locationAddress').textContent = firstDevice.address || 'No address available';
    }

    // Render devices
    renderDevices();

    // Update buttons based on status
    updateActionButtons();
}

// Render device list
function renderDevices() {
    const deviceList = document.getElementById('deviceList');
    
    if (!currentOrder.cabinets || currentOrder.cabinets.length === 0) {
        deviceList.innerHTML = '<div class="empty-state">No devices found</div>';
        return;
    }

    // Group cabinets by device
    const deviceGroups = {};
    currentOrder.cabinets.forEach(cabinet => {
        if (!deviceGroups[cabinet.deviceId]) {
            deviceGroups[cabinet.deviceId] = {
                deviceId: cabinet.deviceId,
                asset: cabinet.asset,
                cooler: cabinet.cooler,
                location: cabinet.location,
                cabinets: []
            };
        }
        deviceGroups[cabinet.deviceId].cabinets.push(cabinet);
    });

    deviceList.innerHTML = Object.values(deviceGroups).map(device => `
        <div class="device-item">
            <div class="device-header">
                <div>
                    <div class="device-asset">Asset: ${device.asset}</div>
                    <div class="device-model">${device.cooler || 'Unknown Model'}</div>
                </div>
            </div>
            <div class="cabinet-list">
                ${renderCabinets(device)}
            </div>
        </div>
    `).join('');
}

// Render cabinets for a device
function renderCabinets(device) {
    if (!device.cabinets || device.cabinets.length === 0) {
        return '<div class="empty-state">No cabinets</div>';
    }

    return device.cabinets.map(cabinet => `
        <div class="cabinet-item">
            <div class="cabinet-header">
                <span class="cabinet-name">Cabinet ${cabinet.cabinetIndex + 1} - ${cabinet.cabinetType}</span>
                <span class="cabinet-status ${cabinet.isExecuted ? 'delivered' : ''}">
                    ${cabinet.isExecuted ? '✓ Delivered' : 'Pending'}
                </span>
            </div>
            <div class="product-grid">
                ${cabinet.products.slice(0, 4).map(product => `
                    <div class="product-item">${product.productName}: ${product.quantityNeeded}</div>
                `).join('')}
                ${cabinet.products.length > 4 ? `<div class="product-item">+${cabinet.products.length - 4} more</div>` : ''}
            </div>
        </div>
    `).join('');
}

// Update action buttons based on order status
function updateActionButtons() {
    const startButton = document.getElementById('startButton');
    const photoButton = document.getElementById('photoButton');
    const completeButton = document.getElementById('completeButton');

    if (currentOrder.status === 'completed') {
        startButton.style.display = 'none';
        photoButton.style.display = 'none';
        completeButton.style.display = 'none';
    } else if (deliveryStartTime || currentOrder.status === 'in_progress') {
        startButton.style.display = 'none';
        photoButton.style.display = 'block';
        completeButton.style.display = 'block';
    } else {
        startButton.style.display = 'block';
        photoButton.style.display = 'none';
        completeButton.style.display = 'none';
    }
}

// Update sync indicator
function updateSyncIndicator() {
    const indicator = document.getElementById('syncIndicator');
    if (navigator.onLine) {
        indicator.className = 'sync-indicator';
        indicator.title = 'Online';
    } else {
        indicator.className = 'sync-indicator offline';
        indicator.title = 'Offline';
    }
}

// Start delivery
async function startDelivery() {
    deliveryStartTime = new Date();
    currentOrder.status = 'in_progress';
    
    // Queue action if offline
    if (!navigator.onLine) {
        await queueOfflineAction({
            type: 'UPDATE_ORDER_STATUS',
            orderId: currentOrder.id,
            status: 'in_progress',
            startTime: deliveryStartTime.toISOString()
        });
    } else {
        // Update server
        await updateOrderStatus('in_progress');
    }
    
    // Save updated order to offline DB
    await offlineDB.saveServiceOrder(currentOrder);
    
    updateActionButtons();
}

// Update order status on server
async function updateOrderStatus(status) {
    try {
        await api.makeRequest('PUT', `/service-orders/${currentOrder.id}`, {
            status: status
        });
    } catch (error) {
        console.error('Failed to update order status:', error);
        // Queue for later if failed
        await queueOfflineAction({
            type: 'UPDATE_ORDER_STATUS',
            orderId: currentOrder.id,
            status: status,
            timestamp: new Date().toISOString()
        });
    }
}

// Queue offline action
async function queueOfflineAction(action) {
    await offlineDB.queueOfflineAction(action);
}

// Navigate to location
function navigateToLocation() {
    const firstCabinet = currentOrder.cabinets && currentOrder.cabinets[0];
    if (!firstCabinet) {
        alert('No location information available');
        return;
    }

    // Use address for navigation
    const address = firstCabinet.address || firstCabinet.location;
    if (address) {
        const encodedAddress = encodeURIComponent(address);
        const url = `https://maps.google.com/maps?daddr=${encodedAddress}`;
        window.open(url, '_blank');
    } else {
        alert('No location information available');
    }
}

// Complete delivery
async function completeDelivery() {
    if (!confirm('Complete this delivery?')) {
        return;
    }

    currentOrder.status = 'completed';
    currentOrder.completedAt = new Date().toISOString();
    
    // Queue action if offline
    if (!navigator.onLine) {
        await queueOfflineAction({
            type: 'COMPLETE_ORDER',
            orderId: currentOrder.id,
            completedAt: currentOrder.completedAt
        });
    } else {
        // Update server
        await updateOrderStatus('completed');
    }
    
    // Save updated order to offline DB
    await offlineDB.saveServiceOrder(currentOrder);
    
    alert('Delivery completed!');
    
    // Go back to orders list
    setTimeout(() => {
        window.location.href = '/pages/driver-app/index.html#orders';
    }, 1000);
}

// Photo capture functions
function showPhotoCapture() {
    const modal = document.getElementById('photoModal');
    modal.classList.add('show');
    startCamera();
}

function closePhotoCapture() {
    const modal = document.getElementById('photoModal');
    modal.classList.remove('show');
    stopCamera();
}

async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                facingMode: 'environment',
                width: { ideal: 1920 },
                height: { ideal: 1080 }
            } 
        });
        const video = document.getElementById('camera');
        video.srcObject = stream;
    } catch (error) {
        console.error('Camera access failed:', error);
        alert('Unable to access camera');
        closePhotoCapture();
    }
}

function stopCamera() {
    const video = document.getElementById('camera');
    if (video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }
}

function capturePhoto() {
    const video = document.getElementById('camera');
    const canvas = document.getElementById('photoCanvas');
    const context = canvas.getContext('2d');
    
    // Set canvas size to video size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame to canvas
    context.drawImage(video, 0, 0);
    
    // Convert to blob
    canvas.toBlob(async (blob) => {
        capturedPhoto = blob;
        
        // Show preview
        const preview = document.getElementById('photoPreview');
        preview.src = URL.createObjectURL(blob);
        preview.style.display = 'block';
        video.style.display = 'none';
        
        // Update buttons
        document.getElementById('captureBtn').style.display = 'none';
        document.getElementById('retakeBtn').style.display = 'block';
        document.getElementById('saveBtn').style.display = 'block';
    }, 'image/jpeg', 0.8);
}

function retakePhoto() {
    capturedPhoto = null;
    
    const video = document.getElementById('camera');
    const preview = document.getElementById('photoPreview');
    
    video.style.display = 'block';
    preview.style.display = 'none';
    
    document.getElementById('captureBtn').style.display = 'block';
    document.getElementById('retakeBtn').style.display = 'none';
    document.getElementById('saveBtn').style.display = 'none';
}

async function savePhoto() {
    if (!capturedPhoto) return;
    
    // Convert blob to base64 for storage
    const reader = new FileReader();
    reader.onloadend = async () => {
        const photoData = {
            orderId: currentOrder.id,
            data: reader.result,
            timestamp: new Date().toISOString(),
            type: 'delivery_proof'
        };
        
        // Save to IndexedDB
        await offlineDB.savePhoto(photoData);
        
        // Queue upload if online
        if (navigator.onLine) {
            uploadPhoto(photoData);
        } else {
            // Queue for later upload
            await queueOfflineAction({
                type: 'UPLOAD_PHOTO',
                photoId: photoData.id,
                orderId: currentOrder.id
            });
        }
        
        closePhotoCapture();
        alert('Photo saved successfully');
    };
    reader.readAsDataURL(capturedPhoto);
}

// Upload photo to server
async function uploadPhoto(photoData) {
    try {
        // In a real implementation, this would upload to server
        console.log('Uploading photo:', photoData.id);
        
        // Mark as uploaded
        await offlineDB.markPhotoUploaded(photoData.id);
    } catch (error) {
        console.error('Failed to upload photo:', error);
        // Will retry later via sync
    }
}