---
title: Authentication & Login Flow
description: Complete user journey documentation for authentication, session management, and role-based access
feature: authentication
last-updated: 2025-08-12
version: 2.1.0
related-files:
  - USER_FLOWS_OVERVIEW.md
  - ../components/forms.md
  - /documentation/03-architecture/SECURITY.md
dependencies:
  - session-management-system
  - role-based-access-control
  - password-security-policies
status: active
---

# Authentication & Login Flow


## Metadata
- **ID**: 06_DESIGN_USER_FLOWS_LOGIN_FLOW
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #authentication #data-layer #database #debugging #device-management #driver-app #integration #interface #machine-learning #mobile #optimization #performance #pwa #security #troubleshooting #ui-design #user-experience #vending-machine
- **Intent**: The CVD authentication flow provides secure access to the vending machine fleet management system with role-based permissions
- **Audience**: system administrators, managers, end users, architects
- **Related**: USER_FLOWS_OVERVIEW.md, SECURITY.md, forms.md, MOBILE_APP_WORKFLOWS.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/06-design/user-flows/
- **Category**: User Flows
- **Search Keywords**: ####, (report, **account, **device, **mobile, **network/system, **redirection, 2025-08-12, access, access), accessibility, account, action, actions:, activation

## Overview

The CVD authentication flow provides secure access to the vending machine fleet management system with role-based permissions. It supports both desktop and mobile authentication with session management optimized for business operations.

## Flow Metadata

- **Flow Name**: Authentication & Login
- **User Roles**: All (Admin, Manager, Driver, Viewer)
- **Frequency**: Daily (multiple times for drivers)
- **Complexity**: Medium (with security considerations)
- **Devices**: Desktop, Mobile, Tablet
- **Dependencies**: User database, session store, audit logging

## Flow Triggers

### Primary Entry Points
1. **Direct URL Access**: User navigates to CVD application
2. **Session Expiry**: Automatic redirect after timeout
3. **Logout Action**: User-initiated session termination
4. **Permission Change**: Role modification requires re-authentication
5. **Mobile App Launch**: PWA startup on mobile devices

### Context-Aware Triggers
- **First-Time User**: Account activation from email invitation
- **Password Reset**: Following password reset email link
- **Multi-Device Access**: Logging in from new device
- **Offline Recovery**: Re-authentication after offline period

## User Journey Breakdown

### Phase 1: Initial Access (0-10 seconds)

#### Entry State Analysis
**System Actions:**
- Check for existing valid session
- Analyze device capabilities (touch, screen size)
- Load appropriate interface variant
- Initialize security headers

**User Experience:**
- Immediate visual feedback (loading state)
- Progressive enhancement of interface
- Accessibility features detection
- Offline capability assessment

#### Screen State: Landing/Login Detection

**Desktop Experience:**
```html
<div class="auth-container container--narrow">
  <div class="auth-card">
    <header class="auth-header">
      <img src="/images/365-logo.png" alt="CVD Logo" class="auth-logo">
      <h1 class="auth-title">CVD Fleet Management</h1>
      <p class="auth-subtitle">Secure access to your vending operations</p>
    </header>
    
    <!-- Session check loading state -->
    <div class="auth-loading" id="sessionCheck" aria-live="polite">
      <div class="spinner" aria-label="Checking session"></div>
      <p class="auth-loading-text">Checking your session...</p>
    </div>
  </div>
</div>
```

**Mobile Experience:**
```html
<div class="mobile-auth">
  <div class="mobile-auth-header">
    <div class="mobile-logo">
      <img src="/images/365-logo.png" alt="CVD" class="logo-compact">
    </div>
    <h1 class="mobile-auth-title">CVD Driver</h1>
  </div>
  
  <div class="mobile-auth-content">
    <!-- Optimized for thumb navigation -->
  </div>
</div>
```

### Phase 2: Authentication Form (10-60 seconds)

#### Screen State: Login Form Presentation

**Form Structure:**
```html
<form class="auth-form" id="loginForm" novalidate>
  <div class="form-group">
    <label for="username" class="form-label form-label--required">
      Username
    </label>
    <input 
      type="text" 
      id="username" 
      name="username"
      class="input input--large" 
      required
      autocomplete="username"
      autofocus
      aria-describedby="username-hint"
    >
    <div id="username-hint" class="form-hint">
      Enter your assigned username or email address
    </div>
  </div>
  
  <div class="form-group">
    <label for="password" class="form-label form-label--required">
      Password
    </label>
    <div class="input-group">
      <input 
        type="password" 
        id="password" 
        name="password"
        class="input input--large" 
        required
        autocomplete="current-password"
        aria-describedby="password-requirements"
      >
      <button 
        type="button" 
        class="input-action" 
        aria-label="Show password"
        data-password-toggle
      >
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-eye"></use>
        </svg>
      </button>
    </div>
  </div>
  
  <div class="form-options">
    <div class="form-group">
      <div class="checkbox-item">
        <input 
          type="checkbox" 
          id="remember-me" 
          name="rememberMe"
          class="checkbox"
        >
        <label for="remember-me" class="checkbox-label">
          Keep me signed in on this device
        </label>
      </div>
    </div>
    
    <a href="#forgot-password" class="auth-link">
      Forgot your password?
    </a>
  </div>
  
  <div class="form-actions">
    <button type="submit" class="btn btn--primary btn--large btn--block">
      Sign In
    </button>
  </div>
</form>
```

#### User Interactions & Validations

**Real-Time Validation:**
- Username format checking (email or username pattern)
- Password strength indication (if new user)
- Clear error messaging for invalid formats
- Network connectivity status

**Accessibility Features:**
- Screen reader announcements for state changes
- High contrast mode support
- Keyboard navigation (Tab, Enter, Escape)
- Voice input support on compatible devices

### Phase 3: Authentication Processing (1-5 seconds)

#### Loading State Management

**Visual Feedback:**
```html
<div class="auth-form auth-form--loading">
  <button type="submit" class="btn btn--primary btn--large btn--block" disabled aria-busy="true">
    <svg class="icon icon--sm spinner" aria-hidden="true">
      <use href="#icon-spinner"></use>
    </svg>
    Signing in...
  </button>
</div>

<div class="auth-status" role="status" aria-live="polite">
  Verifying your credentials...
</div>
```

**Background Processing:**
1. Credential validation against database
2. Role and permission retrieval
3. Session token generation
4. Audit log entry creation
5. Device registration (if new)

### Phase 4: Success Handling (1-3 seconds)

#### Successful Authentication

**System Actions:**
- Session establishment with appropriate timeout
- User preference loading
- Role-based navigation preparation
- Recent activity retrieval

**User Experience:**
```html
<div class="auth-success">
  <div class="auth-success-icon">
    <svg class="icon icon--xl icon--success" aria-hidden="true">
      <use href="#icon-check-circle"></use>
    </svg>
  </div>
  <h2 class="auth-success-title">Welcome back, [User Name]</h2>
  <p class="auth-success-message">Redirecting to your dashboard...</p>
</div>
```

**Redirection Logic:**
```javascript
// Role-based landing page determination
const redirectMap = {
  admin: '/admin/dashboard',
  manager: '/dashboard',
  driver: '/mobile/dashboard',
  viewer: '/reports/dashboard'
};

// Preserve intended destination if available
const returnTo = sessionStorage.getItem('returnTo') || redirectMap[userRole];
```

### Phase 5: Error Handling

#### Authentication Failures

**Invalid Credentials:**
```html
<div class="auth-error" role="alert">
  <div class="auth-error-icon">
    <svg class="icon icon--md icon--danger" aria-hidden="true">
      <use href="#icon-x-circle"></use>
    </svg>
  </div>
  <div class="auth-error-content">
    <h3 class="auth-error-title">Sign In Failed</h3>
    <p class="auth-error-message">
      The username or password you entered is incorrect. Please check your credentials and try again.
    </p>
    <div class="auth-error-actions">
      <button type="button" class="btn btn--primary" onclick="clearForm()">
        Try Again
      </button>
      <a href="#forgot-password" class="btn btn--secondary">
        Reset Password
      </a>
    </div>
  </div>
</div>
```

**Account Locked:**
```html
<div class="auth-error auth-error--locked" role="alert">
  <div class="auth-error-icon">
    <svg class="icon icon--md icon--warning" aria-hidden="true">
      <use href="#icon-lock"></use>
    </svg>
  </div>
  <div class="auth-error-content">
    <h3 class="auth-error-title">Account Temporarily Locked</h3>
    <p class="auth-error-message">
      Your account has been locked due to multiple failed login attempts. 
      Please try again in 15 minutes or contact your administrator.
    </p>
    <div class="auth-error-actions">
      <a href="#contact-admin" class="btn btn--primary">
        Contact Administrator
      </a>
      <p class="auth-error-note">
        Account will unlock automatically at <time id="unlockTime"></time>
      </p>
    </div>
  </div>
</div>
```

**Network/System Errors:**
```html
<div class="auth-error auth-error--system" role="alert">
  <div class="auth-error-icon">
    <svg class="icon icon--md icon--info" aria-hidden="true">
      <use href="#icon-wifi-off"></use>
    </svg>
  </div>
  <div class="auth-error-content">
    <h3 class="auth-error-title">Connection Problem</h3>
    <p class="auth-error-message">
      Unable to connect to the server. Please check your internet connection and try again.
    </p>
    <div class="auth-error-actions">
      <button type="button" class="btn btn--primary" onclick="retryLogin()">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="#icon-refresh"></use>
        </svg>
        Retry
      </button>
      <button type="button" class="btn btn--secondary" onclick="goOffline()">
        Work Offline
      </button>
    </div>
  </div>
</div>
```

## Alternative Flow Paths

### First-Time User Setup

#### Email Invitation Flow
**Trigger**: User clicks account activation link

**Flow Steps:**
1. **Token Validation** (automatic)
   - Verify invitation token
   - Check token expiration
   - Load user account data

2. **Password Creation** (2-5 minutes)
   ```html
   <form class="auth-form auth-form--setup">
     <h2 class="auth-form-title">Complete Your Account Setup</h2>
     <p class="auth-form-description">
       Welcome to CVD! Create a secure password to complete your account setup.
     </p>
     
     <div class="form-group">
       <label for="setup-password" class="form-label form-label--required">
         Create Password
       </label>
       <div class="input-group">
         <input 
           type="password" 
           id="setup-password" 
           name="password"
           class="input input--large" 
           required
           aria-describedby="setup-password-requirements"
         >
         <div class="password-strength" id="passwordStrength"></div>
       </div>
       <div id="setup-password-requirements" class="form-requirements">
         <h4 class="requirements-title">Password Requirements:</h4>
         <ul class="requirements-list">
           <li class="requirement" data-rule="length">At least 8 characters</li>
           <li class="requirement" data-rule="uppercase">One uppercase letter</li>
           <li class="requirement" data-rule="lowercase">One lowercase letter</li>
           <li class="requirement" data-rule="number">One number</li>
           <li class="requirement" data-rule="special">One special character</li>
         </ul>
       </div>
     </div>
     
     <div class="form-group">
       <label for="confirm-password" class="form-label form-label--required">
         Confirm Password
       </label>
       <input 
         type="password" 
         id="confirm-password" 
         name="confirmPassword"
         class="input input--large" 
         required
       >
     </div>
     
     <div class="form-actions">
       <button type="submit" class="btn btn--primary btn--large btn--block">
         Complete Setup
       </button>
     </div>
   </form>
   ```

3. **Account Activation** (automatic)
   - Set account to active status
   - Generate initial session
   - Trigger welcome workflow

### Password Reset Flow

#### Reset Request
**Trigger**: User clicks "Forgot Password" link

**Flow Steps:**
1. **Email/Username Input** (30 seconds)
   ```html
   <form class="auth-form auth-form--reset">
     <h2 class="auth-form-title">Reset Your Password</h2>
     <p class="auth-form-description">
       Enter your username or email address and we'll send you a link to reset your password.
     </p>
     
     <div class="form-group">
       <label for="reset-email" class="form-label form-label--required">
         Username or Email
       </label>
       <input 
         type="text" 
         id="reset-email" 
         name="email"
         class="input input--large" 
         required
         autocomplete="username"
       >
     </div>
     
     <div class="form-actions">
       <button type="submit" class="btn btn--primary btn--large btn--block">
         Send Reset Link
       </button>
       <a href="#login" class="btn btn--ghost">
         Back to Sign In
       </a>
     </div>
   </form>
   ```

2. **Confirmation Message** (immediate)
   ```html
   <div class="auth-success">
     <div class="auth-success-icon">
       <svg class="icon icon--xl icon--info" aria-hidden="true">
         <use href="#icon-mail"></use>
       </svg>
     </div>
     <h2 class="auth-success-title">Check Your Email</h2>
     <p class="auth-success-message">
       If an account with that email exists, you'll receive a password reset link shortly.
     </p>
     <div class="auth-success-actions">
       <a href="#login" class="btn btn--primary">Return to Sign In</a>
       <button type="button" class="btn btn--secondary" onclick="resendEmail()">
         Resend Email
       </button>
     </div>
   </div>
   ```

#### Reset Completion
**Trigger**: User clicks reset link from email

**Flow**: Similar to first-time setup but with different messaging and audit logging.

### Mobile App Authentication

#### PWA-Specific Considerations

**Biometric Authentication** (when available):
```html
<div class="mobile-auth-biometric">
  <button type="button" class="btn btn--ghost btn--large" onclick="authenticateWithBiometric()">
    <svg class="icon icon--lg" aria-hidden="true">
      <use href="#icon-fingerprint"></use>
    </svg>
    Use Fingerprint
  </button>
  <p class="mobile-auth-alternative">
    or <a href="#password-form">sign in with password</a>
  </p>
</div>
```

**Offline Login** (cached credentials):
```javascript
// Service worker handles offline authentication
if ('serviceWorker' in navigator && !navigator.onLine) {
  // Attempt cached credential validation
  // Limited functionality mode
  // Queue actions for online sync
}
```

**Device Registration**:
```html
<div class="mobile-device-register">
  <h3>Register This Device</h3>
  <p>This will enable push notifications and offline capabilities.</p>
  <div class="device-info">
    <div class="device-detail">
      <strong>Device:</strong> <span id="deviceType"></span>
    </div>
    <div class="device-detail">
      <strong>Browser:</strong> <span id="browserInfo"></span>
    </div>
  </div>
  <div class="form-actions">
    <button class="btn btn--primary" onclick="registerDevice()">
      Register Device
    </button>
    <button class="btn btn--secondary" onclick="skipRegistration()">
      Skip for Now
    </button>
  </div>
</div>
```

## Session Management

### Session Duration Policies

**Role-Based Timeouts:**
- **Admin**: 8 hours (with renewal prompts)
- **Manager**: 4 hours (business day duration)
- **Driver**: 12 hours (full shift support)
- **Viewer**: 2 hours (report access)

**Inactivity Detection:**
- Mouse/keyboard activity monitoring
- Page visibility API integration
- Heartbeat requests for active sessions
- Graceful session extension prompts

### Session Expiry Handling

#### Warning Phase (5 minutes before expiry)
```html
<div class="session-warning modal" role="dialog" aria-labelledby="sessionWarningTitle">
  <div class="modal-content">
    <div class="modal-header">
      <h2 id="sessionWarningTitle" class="modal-title">Session Expiring Soon</h2>
    </div>
    <div class="modal-body">
      <p>Your session will expire in <strong id="timeRemaining">5:00</strong>.</p>
      <p>Any unsaved work will be lost. Would you like to extend your session?</p>
    </div>
    <div class="modal-footer">
      <button class="btn btn--primary" onclick="extendSession()">
        Stay Signed In
      </button>
      <button class="btn btn--secondary" onclick="saveAndLogout()">
        Save & Sign Out
      </button>
    </div>
  </div>
</div>
```

#### Automatic Logout
```html
<div class="auth-expired">
  <div class="auth-expired-icon">
    <svg class="icon icon--xl icon--warning" aria-hidden="true">
      <use href="#icon-clock"></use>
    </svg>
  </div>
  <h2 class="auth-expired-title">Session Expired</h2>
  <p class="auth-expired-message">
    Your session has expired for security reasons. Please sign in again to continue.
  </p>
  <div class="auth-expired-actions">
    <button class="btn btn--primary btn--large" onclick="redirectToLogin()">
      Sign In Again
    </button>
  </div>
</div>
```

### Multi-Device Session Management

**Concurrent Session Handling:**
- Allow multiple sessions for Managers and Admins
- Single session limit for Drivers (security)
- Session conflict resolution UI
- Device identification in session list

**Session List Management:**
```html
<div class="session-manager">
  <h3>Active Sessions</h3>
  <div class="session-list">
    <div class="session-item session-item--current">
      <div class="session-info">
        <div class="session-device">
          <svg class="icon" aria-hidden="true">
            <use href="#icon-desktop"></use>
          </svg>
          Desktop - Chrome
        </div>
        <div class="session-location">Office Network</div>
        <div class="session-time">Current session</div>
      </div>
    </div>
    
    <div class="session-item">
      <div class="session-info">
        <div class="session-device">
          <svg class="icon" aria-hidden="true">
            <use href="#icon-smartphone"></use>
          </svg>
          Mobile - Safari
        </div>
        <div class="session-location">Field Location</div>
        <div class="session-time">2 hours ago</div>
      </div>
      <div class="session-actions">
        <button class="btn btn--sm btn--danger" onclick="revokeSession('mobile-123')">
          End Session
        </button>
      </div>
    </div>
  </div>
</div>
```

## Security Considerations

### Threat Prevention

**Brute Force Protection:**
- Rate limiting per IP and account
- Progressive delays after failures
- Account lockout after threshold
- Admin notification for repeated attacks

**Session Security:**
- Secure, HttpOnly cookies
- CSRF token implementation
- Session rotation on privilege change
- Secure transmission (HTTPS only)

### Audit Logging

**Login Events:**
```javascript
{
  timestamp: "2025-08-12T14:30:00Z",
  event: "login_success",
  userId: "user123",
  username: "john.doe",
  ipAddress: "192.168.1.100",
  userAgent: "Mozilla/5.0...",
  deviceInfo: {
    type: "desktop",
    browser: "Chrome 120",
    os: "Windows 10"
  },
  location: "Office Network"
}
```

**Security Events:**
- Failed login attempts
- Account lockouts
- Password changes
- Session terminations
- Permission escalations

## Performance Requirements

### Loading Time Targets
- **Initial page load**: < 2 seconds
- **Authentication processing**: < 3 seconds
- **Dashboard redirect**: < 1 second
- **Error state rendering**: < 500ms

### Optimization Strategies
- Preload critical assets
- Inline critical CSS
- Progressive web app caching
- Optimized image formats
- Compression and minification

### Offline Capabilities
- Cached login form
- Offline error messaging
- Service worker implementation
- Background sync preparation
- Progressive enhancement

---

**Related Documentation:**
- [User Flows Overview](USER_FLOWS_OVERVIEW.md)
- [Form Components](../components/forms.md)
- [Security Architecture](/documentation/03-architecture/SECURITY.md)
- [Mobile App Workflows](MOBILE_APP_WORKFLOWS.md)

**Implementation Notes:**
- All authentication flows require HTTPS
- Progressive enhancement for accessibility
- Comprehensive error handling with recovery paths
- Performance monitoring for authentication timing
- Regular security audit of authentication patterns

**Last Updated:** 2025-08-12  
**Security Review:** 2025-08-12  
**Next Review:** 2025-11-12