// Push notification manager for the driver app
class PushManager {
    constructor() {
        // This would be generated server-side with web-push library
        // For now using a placeholder - in production, this should be fetched from server
        this.vapidPublicKey = 'BKd0G7uMJV1Q2HKPfJQcNMA8s8o5xbKUTZ7RAjUc-MZGYXFz3XwmrugIGtC3yq7L4LdNTcPvCNbMXs_5Nf0qzYY';
    }

    async init() {
        if ('PushManager' in window && 'serviceWorker' in navigator) {
            await this.setupPushNotifications();
        } else {
            console.log('Push notifications not supported');
        }
    }

    async setupPushNotifications() {
        try {
            const registration = await navigator.serviceWorker.ready;
            
            // Check if already subscribed
            let subscription = await registration.pushManager.getSubscription();
            
            if (!subscription) {
                // Check if we should ask for permission
                const shouldAsk = await this.shouldAskForPermission();
                
                if (shouldAsk) {
                    // Ask for permission
                    const permission = await Notification.requestPermission();
                    
                    if (permission === 'granted') {
                        // Subscribe to push
                        subscription = await registration.pushManager.subscribe({
                            userVisibleOnly: true,
                            applicationServerKey: this.urlBase64ToUint8Array(this.vapidPublicKey)
                        });
                        
                        // Send subscription to server
                        await this.sendSubscriptionToServer(subscription);
                        
                        // Update UI
                        this.showNotificationStatus('enabled');
                    } else {
                        this.showNotificationStatus('denied');
                    }
                }
            } else {
                // Already subscribed
                this.showNotificationStatus('enabled');
                
                // Ensure server has latest subscription
                await this.sendSubscriptionToServer(subscription);
            }
        } catch (error) {
            console.error('Failed to setup push notifications:', error);
            this.showNotificationStatus('error');
        }
    }

    async shouldAskForPermission() {
        // Check if user has been asked before
        const lastAsked = localStorage.getItem('push_permission_asked');
        if (!lastAsked) {
            return true;
        }
        
        // Ask again after 7 days if previously denied
        const daysSinceAsked = (Date.now() - parseInt(lastAsked)) / (1000 * 60 * 60 * 24);
        return daysSinceAsked > 7;
    }

    async sendSubscriptionToServer(subscription) {
        const api = new CVDApi();
        
        try {
            await api.makeRequest('POST', '/push/subscribe', {
                subscription: subscription.toJSON(),
                deviceInfo: {
                    userAgent: navigator.userAgent,
                    platform: navigator.platform,
                    language: navigator.language
                }
            });
            
            console.log('Push subscription sent to server');
        } catch (error) {
            console.error('Failed to send subscription to server:', error);
        }
    }

    async unsubscribe() {
        try {
            const registration = await navigator.serviceWorker.ready;
            const subscription = await registration.pushManager.getSubscription();
            
            if (subscription) {
                // Unsubscribe from push
                await subscription.unsubscribe();
                
                // Notify server
                const api = new CVDApi();
                await api.makeRequest('POST', '/push/unsubscribe', {
                    endpoint: subscription.endpoint
                });
                
                this.showNotificationStatus('disabled');
            }
        } catch (error) {
            console.error('Failed to unsubscribe:', error);
        }
    }

    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/\-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    showNotificationStatus(status) {
        // Dispatch event for UI to handle
        window.dispatchEvent(new CustomEvent('pushstatus', {
            detail: { status }
        }));
    }

    // Test notification
    async sendTestNotification() {
        if (Notification.permission === 'granted') {
            const registration = await navigator.serviceWorker.ready;
            registration.showNotification('Test Notification', {
                body: 'Push notifications are working!',
                icon: '/icons/icon-192x192.png',
                badge: '/icons/badge-72x72.png',
                vibrate: [200, 100, 200],
                tag: 'test'
            });
        }
    }
}

// Create singleton instance
const pushManager = new PushManager();