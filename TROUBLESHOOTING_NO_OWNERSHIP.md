# Troubleshooting: KeyError 'no_ownership_high'

## Error Message
```
KeyError: 'no_ownership_high'
File "/Users/alavar/metrics-tracker/src/metrics_app.py", line 73
```

## Root Cause
This error occurs when Python has cached an old version of the `config.py` module that doesn't include the new `no_ownership_high` threshold key.

## Solution

### Option 1: Restart the Application (Recommended)
1. Stop the Streamlit app if it's running:
   ```bash
   make stop
   # or
   pkill -f "streamlit run"
   ```

2. Clear Python cache:
   ```bash
   cd /Users/alavar/metrics-tracker
   find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
   find . -type f -name "*.pyc" -delete
   ```

3. Restart the app:
   ```bash
   make start
   # or
   make start-fg
   ```

### Option 2: Force Reload
If you're running in development mode, you can force Streamlit to reload:
1. Press `Ctrl+C` to stop
2. Run: `make clean` (this clears cache and restarts)

### Option 3: Update Your .env File
Make sure your `.env` file has the new variable:
```bash
NO_OWNERSHIP_HIGH=7
```

You can copy the template:
```bash
cp .env.example .env
# Then edit .env with your API key
```

## Verification
After restarting, verify the app loads by checking:
```bash
uv run streamlit run src/metrics_app.py
```

You should see the app start without errors, and in the Configuration tab, you should see "No Ownership (High)" as one of the slider options.

## Prevention
The code has been updated to use `.get()` method with default values, which prevents this error in the future even if keys are missing from the THRESHOLDS dictionary.

## If Problem Persists
1. Check that you've pulled the latest changes:
   ```bash
   git pull origin main
   ```

2. Reinstall dependencies:
   ```bash
   uv sync --dev
   ```

3. Verify the config file has the new key:
   ```bash
   grep "no_ownership_high" src/modules/config.py
   ```
   
   You should see:
   ```python
   'no_ownership_high': int(os.getenv('NO_OWNERSHIP_HIGH', 7)),
   ```
