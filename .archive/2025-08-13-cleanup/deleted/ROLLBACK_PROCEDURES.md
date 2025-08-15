# User Soft Delete Rollback Procedures

This document provides step-by-step rollback procedures for the user soft delete implementation.

## Quick Rollback Guide

If you need to quickly rollback the user soft delete implementation:

```bash
# 1. Stop the application (if running)
pkill -f "python app.py"

# 2. Restore database from backup
cp cvd.db.backup.YYYYMMDD_HHMMSS cvd.db

# 3. Revert code changes (if needed)
git checkout HEAD~1 -- app.py auth.py

# 4. Remove migration files
rm -rf migrations/001_user_soft_delete.py

# 5. Restart application
python app.py
```

## Detailed Rollback Procedures

### 1. Database Rollback

#### Option A: Restore from Backup (Recommended)
```bash
# List available backups
ls -la cvd.db.backup.*

# Restore from the most recent backup before migration
cp cvd.db.backup.YYYYMMDD_HHMMSS cvd.db

# Verify restoration
sqlite3 cvd.db ".schema users" | grep -v "is_deleted\|deleted_at\|deleted_by"
```

#### Option B: Run Migration Rollback
```bash
# Run the migration rollback
python migrations/001_user_soft_delete.py down cvd.db

# Verify rollback
sqlite3 cvd.db ".schema users"
```

**⚠️ Warning**: Option B will permanently delete any soft-deleted users. Only use if you're certain you want to lose that data.

### 2. Code Rollback

#### Revert auth.py Changes
```bash
# Check current git status
git status

# Revert auth.py to previous version
git checkout HEAD~1 -- auth.py

# Or manually remove added functions:
# - check_user_service_orders()
# - get_user_service_order_details()  
# - validate_user_constraints()
# - log_user_lifecycle_event()
# 
# And revert validate_session() and require_role() methods
```

#### Revert app.py Changes
```bash
# Revert app.py to previous version
git checkout HEAD~1 -- app.py

# Or manually remove added endpoints:
# - /api/users/<int:user_id>/deactivate
# - /api/users/<int:user_id>/activate
# - /api/users/<int:user_id>/soft-delete
# - /api/users/<int:user_id>/audit-trail
# - /api/users/batch-deactivate
# - /api/metrics/user-lifecycle
#
# And revert get_users() function to previous version
```

### 3. Clean Up Migration Files
```bash
# Remove migration script
rm migrations/001_user_soft_delete.py

# Remove migration directory if empty
rmdir migrations 2>/dev/null || true
```

### 4. Clean Up Test Files
```bash
# Remove soft delete specific test files
rm test_soft_delete_core.py
rm test_audit_logging.py
rm tests/test_user_soft_delete.py
rm verify_implementation.py
```

## Verification After Rollback

After completing the rollback, verify that everything is working correctly:

### 1. Database Verification
```bash
# Check users table schema (should not have soft delete columns)
sqlite3 cvd.db ".schema users"

# Verify user count
sqlite3 cvd.db "SELECT COUNT(*) FROM users"

# Check for any remaining soft delete indexes
sqlite3 cvd.db ".indexes users" | grep -v idx_users_active_deleted
```

### 2. Application Verification
```bash
# Start the application
python app.py &

# Test basic user endpoints
curl -X GET "http://localhost:5000/api/users" \
     -H "Content-Type: application/json"

# Test user management still works
# (Replace with actual session cookie)
curl -X GET "http://localhost:5000/api/users" \
     -H "Content-Type: application/json" \
     -b "session_id=your_session_id"

# Stop test application
pkill -f "python app.py"
```

### 3. Code Verification
```bash
# Verify soft delete functions are removed from auth.py
grep -n "check_user_service_orders\|get_user_service_order_details\|validate_user_constraints\|log_user_lifecycle_event" auth.py

# Should return no results if properly removed
```

## Data Recovery Options

If you need to recover data after rollback:

### 1. Recover Soft Deleted Users
If you used Option A (backup restore), soft deleted users are permanently lost. If you used Option B (migration rollback), the data was preserved in the backup.

### 2. Restore from Backup with Data Extraction
```bash
# Create a separate database from backup
cp cvd.db.backup.YYYYMMDD_HHMMSS recovery.db

# Extract soft deleted users
sqlite3 recovery.db "SELECT * FROM users WHERE is_deleted = 1" > deleted_users.csv

# Manually review and re-create users if needed
```

## Troubleshooting Rollback Issues

### Database Rollback Fails
```bash
# If migration rollback fails, check for foreign key constraints
sqlite3 cvd.db "PRAGMA foreign_keys=OFF;"

# Then retry the rollback
python migrations/001_user_soft_delete.py down cvd.db
```

### Application Won't Start After Rollback
```bash
# Check for Python import errors
python -c "import auth; import app"

# Check for missing dependencies
pip install -r requirements.txt

# Check database permissions
ls -la cvd.db
```

### Session/Authentication Issues
```bash
# Clear all sessions to force re-authentication
sqlite3 cvd.db "DELETE FROM sessions"

# Reset admin password if needed
python tools/reset_admin_password.py
```

## Recovery Timeline

| Action | Estimated Time | Downtime |
|--------|---------------|----------|
| Database backup restore | 30 seconds | Yes |
| Code revert (git) | 1 minute | No |
| Migration rollback | 2-5 minutes | Yes |
| Manual code cleanup | 10-15 minutes | No |
| Full verification | 5-10 minutes | Partial |

**Total estimated rollback time: 15-20 minutes**

## Prevention for Future Deployments

To avoid needing rollbacks in the future:

1. **Always create timestamped backups** before migrations
2. **Test in staging environment** first
3. **Use feature flags** for new functionality
4. **Implement monitoring** for critical operations
5. **Document all changes** thoroughly

## Emergency Contacts

If rollback fails and you need assistance:

1. Check application logs: `tail -f logs/app.log`
2. Check database integrity: `sqlite3 cvd.db "PRAGMA integrity_check"`
3. Review this document again carefully
4. Consider restoring from an even earlier backup if available

## Post-Rollback Actions

After successful rollback:

1. **Notify stakeholders** that soft delete functionality has been removed
2. **Update documentation** to reflect current system state
3. **Review what caused the need for rollback** and plan improvements
4. **Test user management functionality** thoroughly
5. **Monitor system** for any unexpected behavior

---

**Remember**: Always backup your database before attempting any rollback procedures!