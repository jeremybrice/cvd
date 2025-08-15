---
type: configuration
category: system
title: Nginx Configuration for CVD Application
status: active
last_updated: 2025-08-12
tags: [nginx, configuration, deployment, ssl, proxy]
cross_references:
  - /documentation/05-development/deployment/GUIDE.md
  - /documentation/03-architecture/system/ARCHITECTURE_OVERVIEW.md
  - /documentation/03-architecture/SECURITY.md
---

# Nginx Configuration for CVD Application

This document contains the complete nginx configuration for the CVD application deployment.

## Configuration File

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name jeremybrice.duckdns.org;
    return 301 https://$host$request_uri;
}

# HTTPS server
server {
    listen 443 ssl;
    server_name jeremybrice.duckdns.org;

    # SSL certs (handled by certbot)
    ssl_certificate     /etc/letsencrypt/live/jeremybrice.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jeremybrice.duckdns.org/privkey.pem;
    ssl_protocols	TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # === Frontend: Static files served by Python HTTP server ===
    location / {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # === Backend: Flask API (proxied to port 5000) ===
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Optional: suppress favicon errors
    location = /favicon.ico {
        return 204;
        access_log off;
        log_not_found off;
    }
}
```

## Configuration Explanation

### HTTP to HTTPS Redirect
- All HTTP traffic on port 80 is automatically redirected to HTTPS
- Uses 301 permanent redirect for SEO benefits
- Preserves the full request URI in the redirect

### SSL/TLS Configuration
- **Certificate Management**: Uses Let's Encrypt certificates managed by certbot
- **Protocols**: Supports TLS 1.2 and 1.3 for security and compatibility
- **Ciphers**: Uses HIGH security ciphers, excludes anonymous and MD5
- **Certificate Path**: Standard Let's Encrypt location

### Frontend Static Files
- **Location**: Root path (`/`) routes to Python HTTP server
- **Upstream**: Python HTTP server running on localhost:8000
- **Headers**: Standard proxy headers for proper forwarding
- **WebSocket Support**: Upgrade headers configured for future WebSocket needs

### Backend API
- **Location**: All `/api/` paths route to Flask backend
- **Upstream**: Flask application running on localhost:5000
- **Headers**: Same proxy configuration as frontend
- **API Isolation**: Clean separation between frontend and backend traffic

### Additional Features
- **Favicon Handling**: Returns 204 No Content to suppress favicon errors
- **Logging**: Disables access logging for favicon requests

## Deployment Considerations

### Service Dependencies
This configuration assumes:
1. Python HTTP server running on port 8000
2. Flask application running on port 5000
3. Let's Encrypt certbot managing SSL certificates

### Port Configuration
- **80**: HTTP redirect only
- **443**: HTTPS with SSL termination
- **8000**: Python HTTP server (internal)
- **5000**: Flask API server (internal)

### Security Features
- **SSL Termination**: Nginx handles all SSL/TLS encryption
- **Protocol Enforcement**: Automatically redirects HTTP to HTTPS
- **Modern TLS**: Only supports TLS 1.2+ for security
- **Header Forwarding**: Preserves client information for backend

### Performance Optimizations
- **HTTP/1.1**: Uses HTTP/1.1 for upstream connections
- **Connection Reuse**: Maintains persistent connections to upstreams
- **Cache Bypass**: Ensures dynamic content isn't cached inappropriately

## Common Issues and Solutions

### Certificate Renewal
- Certificates are automatically renewed by certbot
- Nginx automatically reloads with new certificates
- Monitor certificate expiration dates

### Upstream Connection Issues
- Verify Python HTTP server is running on port 8000
- Verify Flask application is running on port 5000
- Check firewall rules for internal port access

### SSL Configuration Problems
- Test SSL configuration with SSL Labs SSL Test
- Verify certificate chain is complete
- Check that private key matches certificate

### Proxy Header Issues
- Ensure `Host` header is properly set for backend applications
- Verify `X-Forwarded-*` headers if needed by application
- Check for CORS configuration in Flask application

## Testing the Configuration

### Basic Functionality
```bash
# Test HTTP redirect
curl -I http://jeremybrice.duckdns.org/

# Test HTTPS frontend
curl -I https://jeremybrice.duckdns.org/

# Test API proxy
curl -I https://jeremybrice.duckdns.org/api/auth/current-user
```

### SSL Verification
```bash
# Check certificate
openssl s_client -connect jeremybrice.duckdns.org:443 -servername jeremybrice.duckdns.org

# Verify certificate chain
ssl-cert-check -c jeremybrice.duckdns.org:443
```

### Performance Testing
```bash
# Test response times
ab -n 100 -c 10 https://jeremybrice.duckdns.org/

# Test API performance
ab -n 100 -c 10 https://jeremybrice.duckdns.org/api/devices
```

## Maintenance Tasks

### Regular Maintenance
1. Monitor certificate expiration (automated with certbot)
2. Review nginx error logs for issues
3. Update SSL configuration as security standards evolve
4. Test configuration changes in staging environment

### Log Locations
- **Access Logs**: `/var/log/nginx/access.log`
- **Error Logs**: `/var/log/nginx/error.log`
- **SSL Logs**: Usually combined with main nginx logs

### Configuration Validation
```bash
# Test configuration syntax
nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart if needed
sudo systemctl restart nginx
```

This configuration provides a robust, secure foundation for the CVD application with proper SSL termination and clean separation between frontend and backend services.
