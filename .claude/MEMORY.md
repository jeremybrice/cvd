# CVD Project Memory & Context Management

This file helps Claude Code maintain context across conversations and efficiently handle the multi-module CVD system.

## Active Project State

### Current Focus Areas
- [ ] Service order optimization
- [ ] Planogram AI enhancement
- [ ] Driver PWA improvements
- [ ] DEX parser expansion

### Recent Changes
<!-- Update this section after significant changes -->
- Last major update: [Date]
- Changed modules: [List modules]
- Known issues: [List any issues]

## Module Context Boundaries

### Backend Modules (Flask/Python)
**Context Load:** ~2000 lines
```
Core: app.py + auth.py
Service Orders: service_order_service.py
Planogram: planogram_optimizer.py
DEX: dex_parser.py + grid_pattern_analyzer.py
Knowledge: knowledge_base.py
```

### Frontend Modules (HTML/JS)
**Context Load:** ~1500 lines per page
```
Navigation: index.html
Device Mgmt: PCP.html + INVD.html
Planogram: NSPT.html
Service: service-orders.html
Analytics: asset-sales.html + product-sales.html
```

### PWA Module
**Context Load:** ~1000 lines
```
App Shell: driver-app/index.html
Offline: driver-app/offline-storage.js
Sync: driver-app/service-worker.js
```

## Context Switching Patterns

### Pattern 1: Backend to Frontend
```markdown
1. Summarize backend implementation
2. Note API endpoints created/modified
3. Clear Python context
4. Load frontend page + api.js
5. Reference backend summary for integration
```

### Pattern 2: Cross-Module Feature
```markdown
1. Create feature outline
2. Implement backend first
3. Save backend interface contract
4. Switch to frontend with contract
5. Test integration points
```

### Pattern 3: Multi-Cabinet Operations
```markdown
1. Load device structure understanding
2. Work on single cabinet logic
3. Extend to multi-cabinet iteration
4. Verify data consistency
```

## Optimization Strategies

### For Complex Features

#### Planogram Optimization Flow
```
1. Load: planogram_optimizer.py (core logic)
2. Load: NSPT.html lines 1-200 (UI structure)
3. Skip: NSPT.html drag-drop code (unless modifying)
4. Load: Specific slot performance queries
5. Work: Implement optimization
6. Clear: Keep only API contract
```

#### Service Order Generation
```
1. Load: service_order_service.py create_order()
2. Load: Device configurations for target
3. Skip: Unrelated service order functions
4. Work: Generate pick lists
5. Save: Order ID and structure
6. Switch: Frontend for UI updates
```

### For Debugging

#### Quick Debug Context
```
1. Error message/stack trace
2. Affected file + surrounding lines
3. Recent changes (git diff)
4. Related test file
5. Fix and verify
```

#### Deep Debug Context
```
1. Full module context
2. Database schema for tables
3. Frontend-backend interaction
4. Console logs from browser
5. Systematic debugging
```

## Memory Preservation Techniques

### Session Variables
Track these across context switches:
```python
current_user_role = "admin"
active_device_id = "VM-001"
working_planogram_id = 123
service_order_in_progress = 456
last_dex_file_parsed = "sample.dex"
```

### Feature Checkpoints
Save progress at key points:
```markdown
## Checkpoint: Service Order Implementation
- [x] Created order header
- [x] Generated pick lists
- [x] Calculated quantities
- [ ] Assigned to driver
- [ ] Sent notification
```

### Code Snippets Bank
Frequently needed patterns:
```python
# Role check pattern
if not user.has_role(['admin', 'manager']):
    return jsonify({'error': 'Unauthorized'}), 403

# Cabinet iteration pattern
for cabinet in device.get('cabinets', []):
    for slot in cabinet.get('slots', []):
        process_slot(slot)

# API response pattern
return jsonify({
    'success': True,
    'data': result,
    'message': 'Operation completed'
})
```

## Context Priority Levels

### Priority 1: Always Load
- CLAUDE.md (project overview)
- Current module's main file
- Active feature specification

### Priority 2: Usually Load
- Related API endpoints
- Database schema for module
- Recent error logs

### Priority 3: Load if Needed
- Test files
- Documentation
- Example files
- Historical changes

### Priority 4: Rarely Load
- Unrelated modules
- Old documentation
- Archived code
- Third-party libraries

## Quick Context Commands

### Start New Feature
```
1. Load CLAUDE.md
2. Load docs/CONTEXT.md#{module}
3. Load relevant agent
4. Create implementation plan
```

### Fix Bug
```
1. Load error from debug-reports/
2. Load affected file
3. Load recent changes
4. Apply fix
```

### Optimize Performance
```
1. Load current implementation
2. Load performance metrics
3. Load merchandising-analyst agent
4. Generate optimizations
```

## Cross-Module Dependencies

### Service Orders → Planograms
- Reads slot configurations
- Uses par levels
- Updates quantities

### Planograms → Products
- References product catalog
- Tracks product availability
- Updates product metrics

### DEX Parser → Sales Data
- Imports transaction data
- Updates device metrics
- Triggers planogram analysis

### Driver App → Service Orders
- Receives order assignments
- Updates order status
- Uploads completion photos

## Context Recovery Protocol

If context is lost:
1. Check this MEMORY.md for state
2. Review recent file modifications
3. Check git status for changes
4. Load module context from CONTEXT.md
5. Resume from last checkpoint