# Makefile Refactoring Summary

## Date
November 15, 2025

## Overview
Refactored the Makefile to align with the new project structure and follow clean coding practices by introducing configuration variables to avoid hard-coded paths.

## Changes Made

### 1. Configuration Variables Section
Added a comprehensive variables section at the top of the Makefile:

```makefile
# Project structure
PROJECT_ROOT := $(shell pwd)
SRC_DIR := $(PROJECT_ROOT)/src
DATA_DIR := $(PROJECT_ROOT)/data
LOGS_DIR := $(PROJECT_ROOT)/logs
SCRIPTS_DIR := $(PROJECT_ROOT)/scripts
ARCHIVE_DIR := $(PROJECT_ROOT)/archive/backups

# Application files
MAIN_APP := $(SRC_DIR)/metrics_app.py
PREFLIGHT := $(SRC_DIR)/preflight_check.py

# Data files
METRICS_DATA := $(DATA_DIR)/metrics_data.json
METRICS_LOG := $(DATA_DIR)/metrics_log.csv
LAST_RUN_FILE := $(DATA_DIR)/.last_prod_run

# Log files
PROD_LOG := $(LOGS_DIR)/notify_prod.log
TEST_LOG := $(LOGS_DIR)/notify_test.log

# LaunchAgent plists
LAUNCH_AGENTS := $(HOME)/Library/LaunchAgents
PROD_PLIST := $(LAUNCH_AGENTS)/com.metricsTracker.prod.plist
TEST_PLIST := $(LAUNCH_AGENTS)/com.metricsTracker.test.plist

# Streamlit configuration
STREAMLIT_LOG := /tmp/metrics_streamlit.log
STREAMLIT_URL := http://localhost:8501
```

### 2. Path Updates

#### Old Structure → New Structure
- `metrics_data.csv` → `data/metrics_data.json`
- `narratives.json` → (removed, handled in code)
- `metrics_log.csv` → `data/metrics_log.csv`
- `setup_prod_schedule.sh` → `scripts/setup_prod_schedule.sh`
- `create_test_plist.sh` → `scripts/create_test_plist.sh`
- `notify_metrics.sh` → `scripts/smart_notify.sh`
- `notify_prod.log` → `logs/notify_prod.log`
- `notify_test.log` → `logs/notify_test.log`

#### Backup Location
- Old: Root directory backups
- New: `archive/backups/` with organized structure

### 3. Updated Commands

#### App Control
- `test`: Uses `$(PREFLIGHT)` variable
- `start-fg`: Uses `$(MAIN_APP)` variable
- `start-bg`: Uses `$(MAIN_APP)` and `$(STREAMLIT_LOG)` variables
- `stop`: Uses `$(MAIN_APP)` variable

#### Data Management
- `flush-data`: 
  - Uses `$(METRICS_DATA)`, `$(METRICS_LOG)`, `$(LAST_RUN_FILE)` variables
  - Backs up to `$(ARCHIVE_DIR)` instead of root directory
  - Handles `.last_prod_run.time` file as well

#### Scheduling
- `schedule-prod`: Uses `$(SCRIPTS_DIR)` variable
- `schedule-test`: Uses `$(SCRIPTS_DIR)`, `$(TEST_PLIST)`, `$(TEST_LOG)` variables
- `schedule-stop-prod`: Uses `$(PROD_PLIST)` variable
- `schedule-stop-test`: Uses `$(TEST_PLIST)` variable
- `schedule-sleep-test`: Uses `$(SCRIPTS_DIR)` variable

#### Status Commands
- `schedule-status`: Uses all relevant path variables
- `status`: Uses `$(PROD_LOG)` and `$(TEST_LOG)` variables

### 4. Benefits of Refactoring

1. **Maintainability**: Change paths in one place (variables section) instead of throughout the file
2. **Readability**: Variables make it clear what each path represents
3. **Consistency**: All paths follow the new directory structure
4. **Flexibility**: Easy to adjust if directory structure changes in the future
5. **Error Prevention**: Reduces typos from repeated path strings

### 5. Testing
The Makefile was tested with:
```bash
make help
```
All commands display correctly with proper formatting.

## Migration Notes

### For Developers
- All commands work the same way from user perspective
- Internal implementation now uses variables for cleaner code
- Scripts must be in `scripts/` directory
- Data files must be in `data/` directory
- Logs must be in `logs/` directory
- Backups go to `archive/backups/` directory

### No Breaking Changes
- All `make` commands remain the same
- User experience is identical
- Only internal path references were updated

## Next Steps (Optional)
1. Consider adding a `make install` command to set up directory structure
2. Add a `make doctor` command to verify all paths exist
3. Create a `make logs` command to tail all relevant log files
4. Add version info to the Makefile header

## Files Modified
- `/Users/alavar/metrics-tracker/Makefile`

## Files Created
- `/Users/alavar/metrics-tracker/docs/MAKEFILE_REFACTOR.md` (this document)
