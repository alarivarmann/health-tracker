# 🚀 Deploying to Streamlit Community Cloud

This guide will help you deploy both desktop and mobile versions to Streamlit Cloud for free.

## 📋 Prerequisites

1. **GitHub Account**: Your code must be in a public or private GitHub repository
2. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io) (free)
3. **Anthropic API Key** (optional): For Claude AI narratives

## 🛠️ Deployment Steps

### Step 1: Prepare Your Repository

✅ **Already Complete:**
- ✅ `requirements.txt` exists (Streamlit Cloud needs this)
- ✅ `.streamlit/config.toml` exists
- ✅ Both apps share same backend modules
- ✅ `.gitignore` protects sensitive data

🔍 **Verify your git status:**
```bash
cd /Users/alavar/metrics-tracker
git status
```

🚀 **Commit and push if needed:**
```bash
git add requirements.txt src/metrics_app_mobile.py
git commit -m "feat: add mobile app and deployment config"
git push origin main
```

### Step 2: Create Streamlit Cloud Apps

#### 📱 Deploy Mobile App (Primary for Phone)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your repository: `alarivarmann/health-tracker`
4. Set **Main file path**: `src/metrics_app_mobile.py`
5. Choose **App name**: `metrics-mobile` (or your preference)
6. Click **"Deploy"**

Your mobile app will be at: `https://metrics-mobile-<random-id>.streamlit.app`

#### 🖥️ Deploy Desktop App (Optional)

Repeat above steps but with:
- **Main file path**: `src/metrics_app.py`
- **App name**: `metrics-desktop`

### Step 3: Configure Secrets (API Keys)

If using Claude AI:

1. Open your deployed app dashboard
2. Click **"⚙️ Settings"** → **"Secrets"**
3. Add your secrets in TOML format:

```toml
ANTHROPIC_API_KEY = "sk-ant-xxxxx"
```

4. Click **"Save"**
5. App will automatically restart

### Step 4: Access from Your Phone 📱

1. Open the Streamlit Cloud URL on your phone
2. Bookmark it for easy access
3. Works offline after first load (data cached in browser)

## 🔒 Data Persistence

⚠️ **Important**: Streamlit Cloud apps are **ephemeral** (restart frequently):
- Data files (`metrics.csv`, `narratives.json`) reset on restart
- Your data will be lost after ~7 days or on app updates

### Solutions:

#### Option A: GitHub Backup (Recommended)
Add a "Download Data" button to export your data:
```python
# In your app
import streamlit as st
from modules.data import load_data

if st.button("📥 Download Backup"):
    df = load_data()
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"metrics_backup_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
```

#### Option B: Cloud Storage
Connect to Google Sheets, Notion, or Airtable for permanent storage (requires code changes)

#### Option C: Local Development Only
Keep using Streamlit Cloud for travel, sync data manually when back

## 🎯 Usage Tips for Travel

1. **Save the URL**: Add app URL to home screen (iOS: Share → "Add to Home Screen")
2. **Works Offline**: After first load, app works without internet for UI (API calls need connection)
3. **Low Bandwidth**: Mobile app uses minimal data (~50KB per load)
4. **Time Zones**: App uses device time for entries
5. **Battery Friendly**: Lightweight design doesn't drain battery

## 🔧 Troubleshooting

### App Won't Start
- Check **Logs** in Streamlit Cloud dashboard
- Verify `requirements.txt` has all dependencies
- Ensure Python version compatibility (3.9+)

### Secrets Not Working
- Secrets must be in TOML format (not JSON)
- No quotes around keys, quotes around values
- Save and wait ~30s for restart

### Data Disappeared
- Expected behavior on Streamlit Cloud restarts
- Download backups regularly (see Option A above)

### Slow Loading
- Streamlit Cloud free tier has limited resources
- Apps "sleep" after 7 days inactivity (first load takes ~30s)
- Subsequent loads are fast

## 📊 Monitoring

Check your app health:
1. Open app dashboard on Streamlit Cloud
2. View **"Analytics"** for usage stats
3. Check **"Logs"** for errors

## 🆘 Support

- Streamlit Docs: [docs.streamlit.io](https://docs.streamlit.io)
- Community Forum: [discuss.streamlit.io](https://discuss.streamlit.io)
- Issues: Open in your GitHub repository

## 🎉 You're Ready!

Your metrics tracker is now accessible worldwide on any device. Safe travels! 🌍✈️
