# Recommended: Simplified Clean Structure

## Current Issue
You have **duplicate bash scripts** - some in root, some in `scripts/`:

**Root level** (outdated?):
- setup_prod_schedule.sh (9,872 bytes)
- setup_sleep_test_helper.sh (8,840 bytes)  
- smart_notify.sh (2,069 bytes)

**scripts/** (newer? executable?):
- setup_prod_schedule.sh (9,990 bytes) ← different size!
- setup_sleep_test_helper.sh (8,840 bytes) ← same
- smart_notify.sh (2,153 bytes) ← different size!
- create_prod_plist.sh
- create_test_plist.sh

## Recommended Solution: Move scripts into src/

### Target Structure
```
metrics-tracker/
├── Makefile
├── pyproject.toml
├── src/
│   ├── metrics_app.py       # Main app
│   ├── preflight_check.py   # Tests
│   ├── modules/             # Python modules
│   ├── tests/               # Python tests  
│   └── scripts/             # Bash scripts (moved here)
│       ├── smart_notify.sh
│       ├── setup_prod_schedule.sh
│       ├── setup_sleep_test_helper.sh
│       ├── create_prod_plist.sh
│       └── create_test_plist.sh
├── data/                    # Runtime data
├── logs/                    # Runtime logs
├── docs/                    # Documentation
└── archive/                 # Backups
```

### Why This Works
✅ **Single source directory**: Everything in `src/`
✅ **Clear separation**: `src/` = code, `data/` = runtime files
✅ **No import changes**: Python files stay in same relative positions
✅ **Minimal disruption**: Just move one folder + delete duplicates

## Shall I execute this restructuring for you?

I will:
1. Delete the duplicate bash scripts from root
2. Move `scripts/` folder into `src/scripts/`
3. Update Makefile to use `src/scripts/` path
4. Test that everything still works

Type "yes" to proceed, or tell me your preferred structure!
