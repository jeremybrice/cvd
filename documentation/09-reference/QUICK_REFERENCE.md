# CVD Quick Reference Guide


## Metadata
- **ID**: 09_REFERENCE_QUICK_REFERENCE
- **Type**: Reference
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #data-exchange #data-layer #database #debugging #deployment #device-management #devops #dex-parser #documentation #driver-app #integration #logistics #machine-learning #metrics #mobile #operations #optimization #performance #planogram #product-placement #pwa #quality-assurance #reference #reporting #route-management #security #service-orders #testing #troubleshooting #vending-machine
- **Intent**: This quick reference provides essential commands, configurations, and procedures for rapid access during development, administration, and troubleshooting of the CVD system
- **Audience**: system administrators, managers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/09-reference/
- **Category**: 09 Reference
- **Search Keywords**: ###, **api, **database, **examples**:, **test, `/tests/`, accounts, add, admin, analysis, analytics, api, app, application, asset

## Purpose
This quick reference provides essential commands, configurations, and procedures for rapid access during development, administration, and troubleshooting of the CVD system.

---

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate          # Linux/Mac
# OR
venv\Scripts\activate            # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest flask-testing
```

### Running the Application
```bash
# Terminal 1: Backend server
python app.py                    # Starts on http://localhost:5000

# Terminal 2: Frontend server  
python -m http.server 8000       # Serves frontend on http://localhost:8000

# Access application
http://localhost:8000/           # Main application
```

### Database Operations
```bash
# View database schema
sqlite3 cvd.db ".schema"

# Backup database
cp cvd.db cvd_backup_$(date +%Y%m%d_%H%M%S).db

# Run database migration
python migration_add_activity_monitoring.py

# Database analysis
python analyze_db.py
```

### Testing
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest test_endpoints.py

# Run with verbose output
python -m pytest -v

# Test specific functionality
python test_admin_user_hiding.py
python test_frontend_api_calls.py
```

---

## Configuration Quick Reference

### Environment Variables
```bash
# Required for AI features
export ANTHROPIC_API_KEY="your-api-key-here"

# Session security (auto-generated if not set)
export SESSION_SECRET="your-secret-key-here"

# Environment mode
export FLASK_ENV=development     # or production
export FLASK_DEBUG=1             # Enable debug mode
```

### Key Configuration Files
| File | Purpose | Location |
|------|---------|----------|
| `app.py` | Main Flask application | `/` |
| `auth.py` | Authentication module | `/` |
| `cvd.db` | SQLite database | `/` |
| `requirements.txt` | Python dependencies | `/` |
| `api.js` | Frontend API client | `/` |
| `index.html` | Main application shell | `/` |

### Default Credentials
```
Username: admin
Password: admin
```

---

## API Endpoints Summary

### Authentication (`/api/auth/`)
| Method | Endpoint | Purpose | Parameters |
|--------|----------|---------|------------|
| POST | `/login` | User login | `username`, `password` |
| GET | `/current-user` | Get session info | None |
| POST | `/logout` | End session | None |
| GET | `/validate-session` | Check session | None |

### Users (`/api/users/`)
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/` | List users | Admin |
| POST | `/` | Create user | Admin |
| PUT | `/{id}` | Update user | Admin |
| DELETE | `/{id}` | Delete user | Admin |
| POST | `/toggle-admin/{id}` | Toggle admin status | Admin |

### Devices (`/api/devices/`)
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/` | List devices | All |
| POST | `/` | Create device | Manager+ |
| PUT | `/{id}` | Update device | Manager+ |
| DELETE | `/{id}` | Soft delete device | Admin |
| POST | `/recover/{id}` | Recover deleted | Admin |

### Planograms (`/api/planograms/`)
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/` | List planograms | All |
| POST | `/` | Create planogram | Manager+ |
| PUT | `/{id}` | Update planogram | Manager+ |
| DELETE | `/{id}` | Delete planogram | Manager+ |
| POST | `/optimize` | AI optimization | Manager+ |

### Service Orders (`/api/service-orders/`)
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/` | List orders | All |
| POST | `/` | Create order | Manager+ |
| GET | `/{id}` | Get order details | All |
| GET | `/{id}/pick-list` | Generate pick list | All |
| POST | `/execute` | Execute order | Driver+ |
| PUT | `/{id}/status` | Update status | Driver+ |

### Analytics (`/api/metrics/`)
| Method | Endpoint | Purpose | Parameters |
|--------|----------|---------|------------|
| POST | `/calculate` | Calculate metrics | `device_id`, `period` |
| GET | `/weekly` | Weekly summary | `start_date`, `end_date` |
| GET | `/top-performers` | Top devices | `limit`, `metric` |
| GET | `/product-performance` | Product analysis | `product_id`, `period` |

### DEX Parser (`/api/dex/`)
| Method | Endpoint | Purpose | Parameters |
|--------|----------|---------|------------|
| POST | `/parse` | Parse DEX file | File upload |
| GET | `/records/{id}` | Get parsed data | None |
| GET | `/grid-patterns` | Grid analysis | `device_id` |

---

## Database Schema Quick Reference

### Core Tables
| Table | Primary Key | Key Fields | Purpose |
|-------|-------------|------------|---------|
| `users` | `id` | `username`, `role`, `email` | User accounts |
| `devices` | `id` | `name`, `location_id`, `status` | Vending machines |
| `products` | `id` | `name`, `price`, `category` | Product catalog |
| `planograms` | `id` | `device_id`, `cabinet_number` | Product layouts |
| `service_orders` | `id` | `device_id`, `status`, `created_at` | Work orders |

### Relationship Patterns
```sql
-- Device has many cabinets
devices (1) --> (*) cabinet_configurations

-- Planogram has many slots  
planograms (1) --> (*) planogram_slots

-- Service order has many cabinet tasks
service_orders (1) --> (*) service_order_cabinets

-- Cabinet task has many item requirements
service_order_cabinets (1) --> (*) service_order_cabinet_items
```

### Common Queries
```sql
-- Get all active devices
SELECT * FROM devices WHERE status = 'Active' AND deleted_at IS NULL;

-- Get planogram for device
SELECT p.*, ps.slot_number, ps.product_id, ps.quantity 
FROM planograms p 
JOIN planogram_slots ps ON p.id = ps.planogram_id 
WHERE p.device_id = ?;

-- Get pending service orders
SELECT * FROM service_orders WHERE status = 'Pending';

-- Get user by session
SELECT u.* FROM users u 
JOIN sessions s ON u.id = s.user_id 
WHERE s.session_id = ? AND s.expires_at > datetime('now');
```

---

## User Role Permissions Matrix

| Feature | Admin | Manager | Driver | Viewer |
|---------|-------|---------|--------|--------|
| **User Management** | ✅ Full | ❌ None | ❌ None | ❌ None |
| **Device Management** | ✅ Full | ✅ CRUD | ❌ None | 👁️ View |
| **Planogram Management** | ✅ Full | ✅ CRUD | ❌ None | 👁️ View |
| **Service Orders** | ✅ Full | ✅ Create/View | ✅ Execute | 👁️ View |
| **Analytics & Reports** | ✅ Full | ✅ Full | 👁️ Limited | 👁️ View |
| **Company Settings** | ✅ Full | ❌ None | ❌ None | ❌ None |
| **DEX Parser** | ✅ Full | ✅ Full | ❌ None | 👁️ View |
| **Driver App** | ✅ Full | ✅ Monitor | ✅ Full | ❌ None |

**Legend**: ✅ Full Access | 👁️ View Only | ❌ No Access

---

## Navigation Routes

### Hash-Based Routing
| Hash | Page | File | Purpose |
|------|------|------|---------|
| `#home` | Dashboard | `home-dashboard.html` | Main overview |
| `#coolers` | Devices | `PCP.html` | Device listing |
| `#new-device` | Add Device | `INVD.html` | Device creation |
| `#planogram` | Planograms | `NSPT.html` | Product layouts |
| `#service-orders` | Service | `service-orders.html` | Work orders |
| `#route-schedule` | Routes | `route-schedule.html` | Route planning |
| `#asset-sales` | Asset Reports | `asset-sales.html` | Device analytics |
| `#product-sales` | Product Reports | `product-sales.html` | Product analytics |
| `#database` | Database | `database-viewer.html` | Data viewer |
| `#dex-parser` | DEX Parser | `dex-parser.html` | DEX processing |
| `#user-management` | Users | `user-management.html` | User admin |
| `#profile` | Profile | `profile.html` | User settings |

### Page Communication
```javascript
// Navigate to another page
window.parent.postMessage({
    type: 'NAVIGATE',
    payload: { route: 'planogram', params: { deviceId: 123 } }
}, window.location.origin);

// Refresh data
window.parent.postMessage({
    type: 'REFRESH_DATA',
    payload: { table: 'devices' }
}, window.location.origin);
```

---

## Key File Locations

### Frontend Structure
```
/                          # Root directory
├── index.html            # Main application shell
├── api.js                # API client library
├── login.html            # Login page
└── pages/                # Feature pages
    ├── PCP.html          # Device listing
    ├── INVD.html         # Device configuration
    ├── NSPT.html         # Planogram management
    ├── service-orders.html # Service orders
    ├── driver-app/       # PWA for mobile
    └── ...
```

### Backend Structure
```
/                          # Root directory
├── app.py                # Main Flask application
├── auth.py               # Authentication module
├── dex_parser.py         # DEX file processing
├── planogram_optimizer.py # AI optimization
├── service_order_service.py # Service logic
├── knowledge_base.py     # Chat assistant
├── activity_tracker.py  # Activity monitoring
├── security_monitor.py  # Security monitoring
└── tests/                # Test files
```

### Documentation Structure
```
/documentation/
├── 01-project-core/      # Project overview
├── 02-requirements/      # Business requirements
├── 03-architecture/      # System design
├── 04-implementation/    # Code documentation
├── 05-development/       # Dev guides
├── 06-design/           # UI/UX documentation
├── 07-cvd-framework/    # Core features
├── 08-project-management/ # PM documentation
└── 09-reference/        # Quick references
```

---

## Troubleshooting Checklist

### Common Issues

#### Application Won't Start
1. ✅ Check virtual environment is activated
2. ✅ Verify all dependencies installed (`pip install -r requirements.txt`)
3. ✅ Confirm database file exists (`cvd.db`)
4. ✅ Check port availability (5000 for backend, 8000 for frontend)
5. ✅ Review error logs in terminal

#### Login Issues
1. ✅ Verify default credentials (`admin/admin`)
2. ✅ Check session configuration
3. ✅ Clear browser cookies/localStorage
4. ✅ Confirm backend server is running
5. ✅ Check browser console for JavaScript errors

#### API Errors
1. ✅ Verify CORS configuration
2. ✅ Check authentication status
3. ✅ Confirm request format (JSON)
4. ✅ Review API endpoint URLs
5. ✅ Check network connectivity

#### Database Issues
1. ✅ Verify database file permissions
2. ✅ Check for database locks
3. ✅ Run database integrity check
4. ✅ Review recent migrations
5. ✅ Check disk space

#### Frontend Issues
1. ✅ Clear browser cache
2. ✅ Check JavaScript console
3. ✅ Verify API client imports
4. ✅ Confirm iframe loading
5. ✅ Review network requests

---

## Performance Tips

### Database Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_service_orders_status ON service_orders(status);
CREATE INDEX idx_sales_date ON sales(date);

-- Regular maintenance
VACUUM;
ANALYZE;
```

### Frontend Optimization
```javascript
// Use absolute paths for imports
<script src="/api.js"></script>

// Implement proper error handling
try {
    const response = await api.getDevices();
    // Handle success
} catch (error) {
    console.error('Error:', error);
    // Handle error
}
```

### Backend Optimization
```python
# Use connection pooling
with closing(get_db()) as db:
    # Database operations
    
# Implement proper caching
@cache.cached(timeout=300)
def get_static_data():
    return data
```

---

## Security Guidelines

### Authentication
- Session timeout: 8 hours
- Secure cookie settings enabled
- Password hashing with Werkzeug
- CSRF protection for state-changing operations

### Authorization
- Role-based permissions enforced
- API endpoint protection
- Audit logging for sensitive operations
- Security monitoring for privilege escalation

### Data Protection
- Soft delete for data recovery
- Audit trails for compliance
- Encrypted session storage
- Input validation and sanitization

---

## Emergency Contacts & Resources

### System Recovery
1. **Database Backup**: `cp cvd.db cvd_backup.db`
2. **Service Restart**: Kill processes and restart servers
3. **Log Analysis**: Check `flask.log` and browser console
4. **Safe Mode**: Run with minimal configuration

### Key Documentation
- **Full Setup Guide**: `/documentation/05-development/SETUP_GUIDE.md`
- **API Documentation**: `/documentation/05-development/api/OVERVIEW.md`
- **Database Schema**: `/documentation/03-architecture/system/DATABASE_SCHEMA.md`
- **Troubleshooting Guide**: `/documentation/05-development/runbooks/INCIDENT_RESPONSE.md`

### Support Resources
- **Code Repository**: Local filesystem
- **Documentation**: `/documentation/` directory
- **Test Suite**: `/tests/` directory
- **Examples**: `/documentation/09-reference/examples/`

---

*Last Updated: 2025-08-12*
*For detailed information, see the complete documentation suite in `/documentation/`*