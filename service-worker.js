const CACHE_NAME = 'cvd-driver-v1';
const API_CACHE = 'cvd-api-v1';
const IMAGE_CACHE = 'cvd-images-v1';

const urlsToCache = [
  '/',
  '/pages/driver-app/',
  '/pages/driver-app/index.html',
  '/pages/driver-app/styles.css',
  '/pages/driver-app/app.js',
  '/pages/driver-app/db.js',
  '/api.js',
  '/images/365-logo.png'
];

// Cache strategies
const CACHE_STRATEGIES = {
  networkFirst: [
    '/api/auth/',
    '/api/service-orders',
    '/api/routes'
  ],
  cacheFirst: [
    '/images/',
    '/pages/driver-app/styles.css',
    '/api.js'
  ],
  networkOnly: [
    '/api/auth/logout',
    '/api/service-orders/execute'
  ]
};

// Install event - cache essential files
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - serve from cache with different strategies
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests except for specific POST endpoints
  if (request.method !== 'GET' && !isOfflineCapablePost(url.pathname)) {
    return;
  }

  // Determine cache strategy
  const strategy = getCacheStrategy(url.pathname);

  switch (strategy) {
    case 'networkFirst':
      event.respondWith(networkFirst(request));
      break;
    case 'cacheFirst':
      event.respondWith(cacheFirst(request));
      break;
    case 'networkOnly':
      event.respondWith(fetch(request));
      break;
    default:
      event.respondWith(networkFirst(request));
  }
});

// Network first strategy - for API calls
async function networkFirst(request) {
  try {
    // Create new request with credentials for API calls
    const modifiedRequest = new Request(request, {
      credentials: 'include'
    });
    
    const networkResponse = await fetch(modifiedRequest);
    
    // Clone response before caching
    if (networkResponse && networkResponse.status === 200) {
      const responseToCache = networkResponse.clone();
      const cache = await caches.open(API_CACHE);
      cache.put(request, responseToCache);
    }
    
    return networkResponse;
  } catch (error) {
    // Network failed, try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback for HTML pages
    if (request.headers.get('accept').includes('text/html')) {
      return caches.match('/pages/driver-app/offline.html');
    }
    
    throw error;
  }
}

// Cache first strategy - for assets
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    
    // Clone response before caching
    if (networkResponse && networkResponse.status === 200) {
      const responseToCache = networkResponse.clone();
      const cache = await caches.open(IMAGE_CACHE);
      cache.put(request, responseToCache);
    }
    
    return networkResponse;
  } catch (error) {
    // Return placeholder for images
    if (request.url.includes('/images/')) {
      return caches.match('/images/placeholder.png');
    }
    throw error;
  }
}

// Determine cache strategy based on URL
function getCacheStrategy(pathname) {
  for (const [strategy, patterns] of Object.entries(CACHE_STRATEGIES)) {
    if (patterns.some(pattern => pathname.includes(pattern))) {
      return strategy;
    }
  }
  return 'networkFirst';
}

// Check if POST request should work offline
function isOfflineCapablePost(pathname) {
  const offlinePostEndpoints = [
    '/api/service-orders/execute',
    '/api/offline-sync'
  ];
  return offlinePostEndpoints.some(endpoint => pathname.includes(endpoint));
}

// Background sync for offline actions
self.addEventListener('sync', event => {
  if (event.tag === 'sync-offline-actions') {
    event.waitUntil(syncOfflineActions());
  }
});

async function syncOfflineActions() {
  // This will be called when connectivity is restored
  // The actual implementation will be in the app code
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage({
      type: 'SYNC_REQUIRED',
      timestamp: new Date().toISOString()
    });
  });
}

// Push notification support
self.addEventListener('push', event => {
  const options = {
    body: 'You have a new notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: {},
    actions: [
      {
        action: 'view',
        title: 'View'
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ]
  };

  // Parse notification data if available
  if (event.data) {
    try {
      const data = event.data.json();
      options.body = data.body || options.body;
      options.data = data;
      
      // Customize based on notification type
      if (data.type === 'new_order') {
        options.body = `New service order: ${data.orderInfo || 'Check your orders'}`;
        options.tag = 'new-order';
      } else if (data.type === 'route_update') {
        options.body = `Route update: ${data.message || 'Your route has been updated'}`;
        options.tag = 'route-update';
      }
    } catch (e) {
      options.body = event.data.text();
    }
  }

  event.waitUntil(
    self.registration.showNotification('CVD Driver App', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'view') {
    // Open the app to the relevant page based on notification type
    let targetUrl = '/pages/driver-app/';
    
    if (event.notification.data) {
      switch (event.notification.data.type) {
        case 'new_order':
          targetUrl = '/pages/driver-app/#orders';
          break;
        case 'route_update':
          targetUrl = '/pages/driver-app/#routes';
          break;
        default:
          targetUrl = '/pages/driver-app/';
      }
      
      // If specific order ID, open that order
      if (event.notification.data.orderId) {
        targetUrl = `/pages/driver-app/order-detail.html?id=${event.notification.data.orderId}`;
      }
    }
    
    event.waitUntil(
      clients.matchAll({ type: 'window' }).then(clientList => {
        // Check if app is already open
        for (const client of clientList) {
          if (client.url.includes('/driver-app/') && 'focus' in client) {
            return client.focus();
          }
        }
        // Open new window if not already open
        if (clients.openWindow) {
          return clients.openWindow(targetUrl);
        }
      })
    );
  }
});