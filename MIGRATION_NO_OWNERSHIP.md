# Metrics Tracker - Variable Name Update

## Recent Change: "Not Keeping Moses" → "No Ownership"

The metric previously known as "Not Keeping Moses (High)" has been renamed to **"No Ownership"** to better reflect its purpose.

### Updated Variable Names

- **Config Key**: `no_ownership` (was: `not_keeping_moses`)
- **Threshold Key**: `no_ownership_high` (was: `not_keeping_moses_high`)
- **Environment Variable**: `NO_OWNERSHIP_HIGH` (was: `NOT_KEEPING_MOSES_HIGH`)
- **Label**: "No Ownership (even self-development)" (was: "Not keeping Moses at bay")

### What This Metric Measures

This metric captures feelings of lacking ownership or control over your work and time, including:
- Unable to drive your own priorities
- Constantly reacting to others' demands
- No control over self-development time
- Feeling like work owns you rather than you owning your work

### Migration Guide

If you have an existing `.env` file with `NOT_KEEPING_MOSES_HIGH`, you should:

1. Rename the variable in your `.env` file:
   ```bash
   # Old (deprecated)
   NOT_KEEPING_MOSES_HIGH=7
   
   # New
   NO_OWNERSHIP_HIGH=7
   ```

2. The application will use a default value of 7 if the new variable is not set, so your app will continue to work without changes.

### Files Updated

- `src/modules/config.py` - Updated threshold and question definitions
- `src/metrics_app.py` - Updated UI labels and configuration
- `src/modules/insights.py` - Updated insight generation logic
- `.env.example` - Updated example environment file

### Backward Compatibility

The old variable name `NOT_KEEPING_MOSES_HIGH` is no longer read. Please update your `.env` file to use `NO_OWNERSHIP_HIGH`.
