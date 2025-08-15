// Location tracking for driver app
class LocationTracker {
    constructor() {
        this.watchId = null;
        this.currentLocation = null;
        this.tracking = false;
        this.lastUpdateTime = null;
        this.updateInterval = 30000; // 30 seconds
    }

    async init() {
        // Check if geolocation is available
        if ('geolocation' in navigator) {
            // Try to get initial position
            try {
                await this.requestPermission();
            } catch (error) {
                console.log('Location permission not granted yet');
            }
        } else {
            console.error('Geolocation not supported');
        }
    }

    async requestPermission() {
        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
                position => {
                    this.currentLocation = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date()
                    };
                    
                    // Update UI
                    this.notifyLocationUpdate();
                    resolve(this.currentLocation);
                },
                error => {
                    console.error('Location permission denied:', error);
                    reject(error);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        });
    }

    startTracking() {
        if (this.tracking) return;

        this.tracking = true;
        
        // Start watching position
        this.watchId = navigator.geolocation.watchPosition(
            position => {
                const now = Date.now();
                
                // Throttle updates to avoid excessive battery drain
                if (!this.lastUpdateTime || (now - this.lastUpdateTime) > this.updateInterval) {
                    this.currentLocation = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        speed: position.coords.speed,
                        heading: position.coords.heading,
                        timestamp: new Date()
                    };

                    // Send location update to server
                    this.sendLocationUpdate();
                    
                    // Update last update time
                    this.lastUpdateTime = now;

                    // Notify UI
                    this.notifyLocationUpdate();
                }
            },
            error => {
                console.error('Location tracking error:', error);
                this.notifyLocationError(error);
            },
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );

        console.log('Location tracking started');
    }

    stopTracking() {
        if (this.watchId) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
            this.tracking = false;
            console.log('Location tracking stopped');
        }
    }

    async sendLocationUpdate() {
        if (!this.currentLocation) return;
        
        // Don't send if user is not a driver or not logged in
        if (!window.currentUser || window.currentUser.role !== 'driver') {
            return;
        }

        const locationData = {
            ...this.currentLocation,
            driverId: window.currentUser.id,
            driverName: window.currentUser.username,
            deviceId: this.getDeviceId()
        };

        if (!navigator.onLine) {
            // Queue for later
            await offlineDB.queueOfflineAction({
                type: 'LOCATION_UPDATE',
                data: locationData
            });
            return;
        }

        try {
            const api = new CVDApi();
            await api.makeRequest('POST', '/driver/location', locationData);
        } catch (error) {
            console.error('Failed to send location update:', error);
            // Queue for retry
            await offlineDB.queueOfflineAction({
                type: 'LOCATION_UPDATE',
                data: locationData
            });
        }
    }

    getDistanceToLocation(targetLat, targetLng) {
        if (!this.currentLocation) return null;

        // Haversine formula for distance calculation
        const R = 6371; // Earth's radius in km
        const dLat = this.toRad(targetLat - this.currentLocation.latitude);
        const dLon = this.toRad(targetLng - this.currentLocation.longitude);
        const lat1 = this.toRad(this.currentLocation.latitude);
        const lat2 = this.toRad(targetLat);

        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.sin(dLon/2) * Math.sin(dLon/2) * Math.cos(lat1) * Math.cos(lat2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        const d = R * c;

        return d * 1000; // Convert to meters
    }

    getETAToLocation(targetLat, targetLng) {
        const distance = this.getDistanceToLocation(targetLat, targetLng);
        if (!distance) return null;

        // Estimate based on average speed or current speed
        const speed = this.currentLocation.speed || 10; // Default 10 m/s (36 km/h)
        const timeInSeconds = distance / speed;
        
        return {
            distance: distance,
            timeInMinutes: Math.ceil(timeInSeconds / 60),
            formattedTime: this.formatETA(timeInSeconds)
        };
    }

    formatETA(seconds) {
        if (seconds < 60) return '< 1 min';
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes} min`;
        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;
        return `${hours}h ${remainingMinutes}m`;
    }

    toRad(deg) {
        return deg * (Math.PI / 180);
    }

    getDeviceId() {
        // Get or generate a unique device ID
        let deviceId = localStorage.getItem('driver_device_id');
        if (!deviceId) {
            deviceId = 'driver_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('driver_device_id', deviceId);
        }
        return deviceId;
    }

    notifyLocationUpdate() {
        // Trigger location update event
        window.dispatchEvent(new CustomEvent('locationupdate', {
            detail: this.currentLocation
        }));
    }

    notifyLocationError(error) {
        window.dispatchEvent(new CustomEvent('locationerror', {
            detail: { error }
        }));
    }

    // Check if location services are enabled
    async checkLocationServices() {
        try {
            const result = await navigator.permissions.query({ name: 'geolocation' });
            return result.state;
        } catch (error) {
            console.error('Failed to check location permission:', error);
            return 'unknown';
        }
    }
}

// Create singleton instance
const locationTracker = new LocationTracker();