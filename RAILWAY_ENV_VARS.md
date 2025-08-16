# Railway Environment Variables

## Required Environment Variables for CVD Deployment

Set these in Railway Dashboard → Project Settings → Variables:

### Required Variables
```
DATABASE_PATH=/app/data/cvd.db
DATA_DIR=/app/data
SESSION_SECRET=<generate-secure-random-string>
```

### Optional Variables  
```
ANTHROPIC_API_KEY=<your-anthropic-key>
FLASK_ENV=production
RAILWAY_ENVIRONMENT=production
```

### Generate Secure Session Secret
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Railway Service Configuration

### Persistent Volume
- **Mount Path**: `/app/data`
- **Size**: 1GB (sufficient for SQLite)

### Start Command
Already configured in `railway.json` and `Procfile`:
```bash
python railway_start.py && exec gunicorn app:app --workers 2 --threads 4 --bind 0.0.0.0:$PORT --timeout 120 --access-logfile -
```

## Troubleshooting

### Check Logs
Monitor Railway logs for:
- Database initialization messages
- Database path resolution
- Error messages from Flask

### Common Issues
1. **Missing DATABASE_PATH**: App will try fallback locations
2. **Missing persistent volume**: Database will be created but not persist
3. **Missing SESSION_SECRET**: Will use auto-generated (less secure)

### Verification
After deployment, check logs for these success messages:
- `✓ Database copied successfully` or `✓ Database already exists`
- `✓ Database connection verified`
- `📍 Using Railway persistent volume database: /app/data/cvd.db`