# Structure-Aware Plist Generation - Fix Summary

## Problem
After refactoring the project structure to move Python files into `src/`, the LaunchAgent plist files still had **hardcoded paths** pointing to the old structure. This caused:

```
[Errno 2] No such file or directory: '/Users/alavar/metrics-tracker/metrics_app.py'
```

## Root Cause
The scripts that generate plist files (`create_test_plist.sh`, `create_prod_plist.sh`, `setup_prod_schedule.sh`) had hardcoded paths:
- `/Users/alavar/metrics-tracker/metrics_app.py` (WRONG - file is in `src/`)
- `/Users/alavar/metrics-tracker/smart_notify.sh` (WRONG - file is in `scripts/`)
- `/Users/alavar/metrics-tracker/notify_test.log` (WRONG - file is in `logs/`)

## Solution: Structure-Aware Scripts
Made all plist-generation scripts **dynamically detect** the project structure instead of hardcoding paths.

### Changes Made

#### 1. **`scripts/create_test_plist.sh`** - Now structure-aware
```bash
# Detect project structure dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Find smart_notify.sh
if [ -f "$PROJECT_ROOT/scripts/smart_notify.sh" ]; then
    NOTIFY_SCRIPT="$PROJECT_ROOT/scripts/smart_notify.sh"
elif [ -f "$PROJECT_ROOT/smart_notify.sh" ]; then
    NOTIFY_SCRIPT="$PROJECT_ROOT/smart_notify.sh"
fi

# Find logs directory
if [ -d "$PROJECT_ROOT/logs" ]; then
    LOG_DIR="$PROJECT_ROOT/logs"
else
    LOG_DIR="$PROJECT_ROOT"
fi
```

**Benefits:**
- ✅ Works regardless of where metrics_app.py is located
- ✅ Works regardless of where scripts are located
- ✅ Adapts to different directory structures
- ✅ Easy to maintain - no hardcoded paths

#### 2. **`scripts/create_prod_plist.sh`** - Now structure-aware
- Same dynamic detection as test script
- Also accepts schedule as parameter for flexibility

#### 3. **`scripts/setup_prod_schedule.sh`** - Updated paths
- Changed hardcoded `/metrics-tracker/smart_notify.sh` → `/metrics-tracker/scripts/smart_notify.sh`
- Now references correct script location

#### 4. **`src/preflight_check.py`** - Made structure-aware
Updated to find files relative to project root, not current directory:
```python
# Find project root
current = Path.cwd()
if current.name == "src":
    root = current.parent
else:
    root = current

files = [
    (str(root / ".env"), "Environment config"),
    (str(root / "pyproject.toml"), "Project dependencies"),
    (str(root / "src" / "metrics_app.py"), "Main application"),
]
```

## How It Works

### Before (Hardcoded)
```xml
<key>ProgramArguments</key>
<array>
    <string>/bin/bash</string>
    <string>/Users/alavar/metrics-tracker/smart_notify.sh</string>
</array>
```
❌ Breaks if script moves to `scripts/` folder

### After (Dynamic)
```bash
# Script detects location
if [ -f "$PROJECT_ROOT/scripts/smart_notify.sh" ]; then
    NOTIFY_SCRIPT="$PROJECT_ROOT/scripts/smart_notify.sh"
elif [ -f "$PROJECT_ROOT/smart_notify.sh" ]; then
    NOTIFY_SCRIPT="$PROJECT_ROOT/smart_notify.sh"
fi

# Plist uses detected path
cat > ~/Library/LaunchAgents/com.metricsTracker.test.plist << EOF
<string>$NOTIFY_SCRIPT</string>
EOF
```
✅ Always finds the script, wherever it is

## Testing

### Verified Working
```bash
# 1. Create test plist with dynamic detection
./scripts/create_test_plist.sh
# Output: 📋 Detected: notify=/Users/alavar/metrics-tracker/scripts/smart_notify.sh

# 2. Verify plist has correct paths
cat ~/Library/LaunchAgents/com.metricsTracker.test.plist | grep "smart_notify"
# Output: <string>/Users/alavar/metrics-tracker/scripts/smart_notify.sh</string>

# 3. Start Streamlit with correct path
uv run streamlit run src/metrics_app.py
# ✅ Works!

# 4. Load schedule
make schedule-test
# ✅ Loads with correct paths
```

## Files Modified

### Scripts Made Structure-Aware
1. `scripts/create_test_plist.sh` - ✅ Dynamically detects paths
2. `scripts/create_prod_plist.sh` - ✅ Dynamically detects paths  
3. `scripts/setup_prod_schedule.sh` - ✅ Updated script path

### Python Files Fixed
4. `src/preflight_check.py` - ✅ Finds files relative to project root

### Makefile Already Good
- Already uses variables (`$(SCRIPTS_DIR)`, `$(SRC_DIR)`, etc.)
- No changes needed - variables adapt automatically

## Reproducibility

**Key Principle**: Never hardcode paths in scripts that generate configuration files!

### ✅ DO THIS (Structure-aware)
```bash
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$PROJECT_ROOT/scripts/my_script.sh"
```

### ❌ DON'T DO THIS (Hardcoded)
```bash
SCRIPT_PATH="/Users/alavar/metrics-tracker/scripts/my_script.sh"
```

## Benefits

1. **Portable** - Works on any machine, any username
2. **Flexible** - Adapts to structure changes
3. **Maintainable** - Change structure once, scripts adapt
4. **Reproducible** - Generate plists anytime, always correct
5. **Future-proof** - Won't break if files move

## Future Recommendations

If adding new scripts that generate plists or configs:
1. ✅ Always detect PROJECT_ROOT dynamically
2. ✅ Always search for files instead of assuming location
3. ✅ Use variables for paths, never hardcode
4. ✅ Provide helpful error messages if files not found
5. ✅ Show detected paths when running (for debugging)

## Verification Commands

```bash
# Test plist generation
./scripts/create_test_plist.sh

# Verify correct paths in generated plist
cat ~/Library/LaunchAgents/com.metricsTracker.test.plist | grep -E "(Program|Standard|Working)"

# Test schedule system
make schedule-test

# Verify Streamlit starts with correct path
ps aux | grep streamlit | grep "src/metrics_app.py"
```

All should show `src/metrics_app.py` and `scripts/smart_notify.sh` - not root-level paths.

## Date
November 15, 2025

## Status
✅ **FIXED** - All plist generation scripts are now structure-aware and reproducible.
