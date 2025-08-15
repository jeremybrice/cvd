# Android PWA Data Loading Fix

**Issue**: Android PWA shows no data while desktop version works correctly  
**Root Cause**: Session cookies not persisting in PWA standalone mode  

## Problem Analysis

### 1. Cookie/Session Issues
- Android PWAs run in isolated WebView context
- Browser session cookies don't transfer to PWA
- Service worker doesn't forward credentials

### 2. Current Symptoms
- Desktop browser: Shows orders correctly
- Android PWA: Shows "0 devices, 0 items" or no data at all
- API returns 401 Unauthorized in PWA context

## Immediate Fixes

### Fix 1: Service Worker Credentials (Already Applied)
Modified service worker to include credentials in all fetch requests:
```javascript
const modifiedRequest = new Request(request, {
  credentials: 'include'
});
```

### Fix 2: Add Local Token Storage
Since cookies don't persist reliably in Android PWAs, implement token-based auth:

**In app.py:**
```python
@app.route('/api/auth/login', methods=['POST'])
def login():
    # ... existing login code ...
    
    # Generate a token for mobile apps
    if request.headers.get('X-App-Type') == 'pwa':
        token = secrets.token_urlsafe(32)
        # Store token in database with user_id and expiry
        cursor.execute('''
            INSERT INTO mobile_tokens (token, user_id, expires_at)
            VALUES (?, ?, datetime('now', '+7 days'))
        ''', (token, user['id']))
        
        return jsonify({
            'user': user_data,
            'token': token  # Return token for PWA
        })
```

**In api.js:**
```javascript
constructor() {
    this.baseUrl = window.location.origin;
    this.token = localStorage.getItem('authToken');
}

async makeRequest(method, endpoint, data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-App-Type': 'pwa'
        },
        credentials: 'include'
    };
    
    // Add token if available (for PWA)
    if (this.token) {
        options.headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    // ... rest of makeRequest
}
```

### Fix 3: PWA-Specific Login Flow
Create a dedicated login page for PWA that stores tokens:

**In driver-app/app.js:**
```javascript
async function checkAuth() {
    try {
        const response = await api.makeRequest('GET', '/auth/current-user');
        if (response && response.user) {
            currentUser = response.user;
            // ... existing code
        }
    } catch (error) {
        if (error.status === 401) {
            // For PWA, check if we need to re-authenticate
            if (window.matchMedia('(display-mode: standalone)').matches) {
                // Show login form within PWA
                showPWALogin();
            } else {
                // Redirect to main login
                window.location.href = '/pages/login.html?redirect=driver';
            }
        }
    }
}
```

## Testing Steps

### After Service Worker Update:
1. **Clear PWA Data**:
   - Android: Settings > Apps > CVD Driver > Storage > Clear Data
   - Uninstall and reinstall PWA

2. **Re-authenticate**:
   - Open PWA
   - Login with jbdriver credentials
   - Check if orders appear

### If Still Not Working:
1. **Check Network Tab**:
   - Use Chrome DevTools remote debugging
   - Connect Android device via USB
   - Check if API calls include cookies/auth headers

2. **Debug Service Worker**:
   - Check chrome://inspect on desktop while Android connected
   - Look for service worker console logs
   - Verify fetch interception works

## Long-term Solution

### Implement JWT Authentication
1. **Backend**: Generate JWT tokens on login
2. **Frontend**: Store in localStorage/IndexedDB
3. **API**: Accept both session cookies AND JWT tokens
4. **Service Worker**: Always include auth headers

### Benefits:
- Works reliably across all PWA contexts
- Survives app restarts
- Can implement refresh tokens
- Better for offline scenarios

## Quick Workaround

If the above doesn't work immediately, add this to driver-app/index.html:

```javascript
// Force reload auth on PWA startup
if (window.matchMedia('(display-mode: standalone)').matches) {
    // Clear any stale cache
    if ('caches' in window) {
        caches.keys().then(names => {
            names.forEach(name => {
                if (name.includes('api')) {
                    caches.delete(name);
                }
            });
        });
    }
    
    // Force fresh login
    localStorage.setItem('pwaMode', 'true');
}
```

## Summary

The Android PWA data issue stems from cookie isolation in WebView. The service worker fix should help, but implementing token-based auth is the most reliable solution for PWAs. The immediate fix is to:

1. Update service worker (done)
2. Clear PWA data and reinstall
3. Re-login within the PWA
4. If still failing, implement token auth