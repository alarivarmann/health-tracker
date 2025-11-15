# Project Restructuring Proposal

## Current Problems

### 1. Duplicate Scripts
```
Root level:
  - setup_prod_schedule.sh
  - setup_sleep_test_helper.sh  
  - smart_notify.sh

scripts/ folder:
  - setup_prod_schedule.sh
  - setup_sleep_test_helper.sh
  - smart_notify.sh
  - create_prod_plist.sh
  - create_test_plist.sh
```

**Problem**: Duplicate files - which one is the source of truth?

### 2. Mixed Python/Bash
```
src/              (Python only)
scripts/          (Bash only)
```

**Problem**: Why separate? Both are "source code"

### 3. Configuration Files
```
Root level:
  - pyproject.toml (Python config)
  - Makefile (Build tool)
  - .env (Config)
```

**Question**: Should configs be in a separate folder?

---

## Proposed Solutions

### **Option A: Single `src/` Directory (Recommended)**

**Philosophy**: All source code (Python + Bash) in one place

```
metrics-tracker/
├── Makefile              # Build commands
├── pyproject.toml        # Python dependencies
├── .env                  # Environment config
├── uv.lock              # Lock file
├── src/
│   ├── app/             # Python application
│   │   ├── metrics_app.py
│   │   ├── preflight_check.py
│   │   └── modules/
│   │       ├── config.py
│   │       ├── data.py
│   │       └── ...
│   └── scripts/         # Bash scripts
│       ├── smart_notify.sh
│       ├── setup_prod_schedule.sh
│       ├── setup_sleep_test_helper.sh
│       ├── create_prod_plist.sh
│       └── create_test_plist.sh
├── data/                # Runtime data
├── logs/                # Runtime logs
├── docs/                # Documentation
└── archive/             # Backups

```

**Pros**:
- Single source directory - clear separation from data/logs
- All "source code" together regardless of language
- Common in modern projects (Next.js, Rust, Go do this)
- Easy to understand: src = code, data = runtime files

**Cons**:
- Slight restructuring needed
- Need to update import paths

---

### **Option B: Separate by Language**

```
metrics-tracker/
├── Makefile
├── pyproject.toml
├── python/              # All Python code
│   ├── metrics_app.py
│   ├── preflight_check.py
│   └── modules/
└── scripts/             # All Bash scripts
    ├── smart_notify.sh
    └── ...
```

**Pros**:
- Clear language separation
- Easy to apply language-specific tooling

**Cons**:
- Two "source" directories to maintain
- Less common pattern
- Unclear where mixed-language utilities go

---

### **Option C: Flat Structure (Keep Current)**

```
metrics-tracker/
├── scripts/             # Bash scripts
├── src/                 # Python code
```

**Pros**:
- Minimal change
- Common in Python projects

**Cons**:
- Still need to clean up duplicate files
- Two source directories

---

## Recommendation: **Option A**

### Proposed Final Structure

```
metrics-tracker/
├── Makefile                    # Build tool
├── pyproject.toml              # Python package config
├── uv.lock                     # Dependency lock
├── .env                        # Local environment variables
├── .python-version             # Python version
│
├── src/                        # ALL SOURCE CODE
│   ├── app/                    # Python application
│   │   ├── metrics_app.py
│   │   ├── preflight_check.py
│   │   └── modules/
│   │       ├── __init__.py
│   │       ├── config.py
│   │       ├── data.py
│   │       ├── analysis.py
│   │       ├── insights.py
│   │       ├── narratives.py
│   │       ├── severity.py
│   │       └── local_narrative.py
│   │
│   ├── scripts/                # Shell scripts
│   │   ├── smart_notify.sh
│   │   ├── setup_prod_schedule.sh
│   │   ├── setup_sleep_test_helper.sh
│   │   ├── create_prod_plist.sh
│   │   └── create_test_plist.sh
│   │
│   └── tests/                  # All tests (Python)
│       ├── test_alerting.py
│       ├── test_narrative_consistency.py
│       └── test_user_scenario.py
│
├── data/                       # Runtime data (gitignored)
│   ├── config.json
│   ├── metrics_data.json
│   ├── metrics_log.csv
│   └── work_individual_metrics_tracker.yaml
│
├── logs/                       # Runtime logs (gitignored)
│   ├── metrics-tracker.log
│   ├── notify_prod.log
│   └── notify_test.log
│
├── docs/                       # Documentation
│   ├── ALERTING_FIX.md
│   ├── QUICK_REFERENCE.md
│   └── ...
│
├── archive/                    # Historical data
│   ├── backups/
│   ├── debug/
│   └── unused/
│
└── .streamlit/                # Streamlit config
    └── config.toml
```

---

## Migration Steps

### 1. Remove Duplicate Files
```bash
# Remove duplicates from root (keep scripts/ versions)
rm setup_prod_schedule.sh
rm setup_sleep_test_helper.sh
rm smart_notify.sh
```

### 2. Reorganize `src/`
```bash
# Create new structure
mkdir -p src/app
mkdir -p src/scripts

# Move Python files
mv src/metrics_app.py src/app/
mv src/preflight_check.py src/app/
mv src/modules src/app/

# Move tests
mv src/tests src/  # Tests stay at src level

# Move bash scripts
mv scripts/* src/scripts/
rmdir scripts
```

### 3. Update Makefile Variables
```makefile
SRC_DIR := $(PROJECT_ROOT)/src
APP_DIR := $(SRC_DIR)/app
SCRIPTS_DIR := $(SRC_DIR)/scripts
TESTS_DIR := $(SRC_DIR)/tests

MAIN_APP := $(APP_DIR)/metrics_app.py
PREFLIGHT := $(APP_DIR)/preflight_check.py
```

### 4. Update Python Imports
In `metrics_app.py`:
```python
# Old:
from modules.config import QUESTIONS

# New:
from app.modules.config import QUESTIONS
# OR add src/app to PYTHONPATH
```

### 5. Update Script Paths
Bash scripts may reference each other - update relative paths.

### 6. Update `.gitignore`
```gitignore
# Runtime files
data/*.json
data/*.csv
logs/*.log

# Not source code
.env
.venv/
__pycache__/
```

---

## Decision Points

### Question 1: Do you want all source code in `src/`?
- ✅ Yes → Proceed with Option A
- ❌ No → Consider Option B or C

### Question 2: Should Python imports change?
- Option 1: Update imports to `from app.modules.*`
- Option 2: Add `src/app` to PYTHONPATH in Makefile
- Option 3: Keep flat `src/` (skip app/ subdirectory)

### Question 3: Where do tests go?
- Option 1: `src/tests/` (with other source)
- Option 2: `tests/` at root (common Python pattern)
- Option 3: `src/app/tests/` (next to code they test)

---

## My Recommendation

**Simplified Option A** (Less disruption):

```
src/
├── metrics_app.py          # Keep flat for simpler imports
├── preflight_check.py
├── modules/                # Python modules
│   └── ...
├── scripts/                # Bash scripts
│   └── ...
└── tests/                  # Tests
    └── ...
```

**Changes needed**:
1. ✅ Delete root-level bash scripts (duplicates)
2. ✅ Move `scripts/` into `src/scripts/`
3. ✅ Move `src/tests/` to `src/tests/` (no change if already there)
4. ✅ Update Makefile paths
5. ✅ No Python import changes needed!

**Result**: Clean separation of source vs. data/logs, minimal code changes.

---

## What do you prefer?

1. **Simplified Option A** (recommended - minimal disruption)
2. **Full Option A** (more organized, requires import updates)
3. **Keep current structure** (just delete duplicates)
4. **Something else** (tell me your preference!)
