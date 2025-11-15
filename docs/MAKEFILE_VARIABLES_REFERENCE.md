# Makefile Quick Reference

## Configuration Variables

### Directory Structure
| Variable | Path | Purpose |
|----------|------|---------|
| `PROJECT_ROOT` | Current directory | Base project directory |
| `SRC_DIR` | `src/` | Source code |
| `DATA_DIR` | `data/` | Data files (JSON, CSV) |
| `LOGS_DIR` | `logs/` | Log files |
| `SCRIPTS_DIR` | `scripts/` | Shell scripts |
| `ARCHIVE_DIR` | `archive/backups/` | Backup files |

### Application Files
| Variable | Path | Purpose |
|----------|------|---------|
| `MAIN_APP` | `src/metrics_app.py` | Main Streamlit app |
| `PREFLIGHT` | `src/preflight_check.py` | Pre-flight checker |

### Data Files
| Variable | Path | Purpose |
|----------|------|---------|
| `METRICS_DATA` | `data/metrics_data.json` | Metrics data storage |
| `METRICS_LOG` | `data/metrics_log.csv` | Metrics log file |
| `LAST_RUN_FILE` | `data/.last_prod_run` | Last run timestamp |

### Log Files
| Variable | Path | Purpose |
|----------|------|---------|
| `PROD_LOG` | `logs/notify_prod.log` | Production notifications |
| `TEST_LOG` | `logs/notify_test.log` | Test notifications |
| `STREAMLIT_LOG` | `/tmp/metrics_streamlit.log` | Streamlit output |

### LaunchAgent Files
| Variable | Path | Purpose |
|----------|------|---------|
| `PROD_PLIST` | `~/Library/LaunchAgents/com.metricsTracker.prod.plist` | Production schedule |
| `TEST_PLIST` | `~/Library/LaunchAgents/com.metricsTracker.test.plist` | Test schedule |

### Other
| Variable | Value | Purpose |
|----------|-------|---------|
| `STREAMLIT_URL` | `http://localhost:8501` | Streamlit web URL |

## How to Extend

### Adding a New Directory
```makefile
NEW_DIR := $(PROJECT_ROOT)/new_directory
```

### Adding a New File Variable
```makefile
NEW_FILE := $(NEW_DIR)/filename.ext
```

### Using Variables in Commands
```makefile
my-command:
	@echo "Processing $(NEW_FILE)"
	@python3 $(NEW_FILE)
```

## Benefits

✅ **Single Source of Truth**: Change paths in one place  
✅ **Type Safety**: Make catches undefined variables  
✅ **Readability**: Clear what each path represents  
✅ **Maintainability**: Easy to update when structure changes  
✅ **Consistency**: All commands use same path definitions  

## Migration Checklist

When updating Makefile commands:
- [ ] Replace hard-coded paths with variables
- [ ] Ensure all paths use appropriate variable prefix
- [ ] Test with `make -n <command>` to verify expansion
- [ ] Run actual command to verify functionality
- [ ] Update documentation if command behavior changes
