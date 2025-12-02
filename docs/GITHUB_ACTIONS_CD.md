# GitHub Actions Continuous Deployment Guide

## 🚀 Streamlit Cloud Auto-Deployment

Streamlit Cloud **automatically deploys** when you push to GitHub - no GitHub Actions needed for deployment itself!

However, the workflow I created (`.github/workflows/deploy-streamlit.yml`) adds useful CI/CD features:

## 📋 What the Workflow Does

1. **Triggers on Push**: Runs automatically when you push to `main` branch
2. **Path Filtering**: Only triggers when relevant files change:
   - `src/**` (your app code)
   - `requirements.txt` (dependencies)
   - `.streamlit/**` (config)
   - `.python-version` (Python version)
3. **Manual Trigger**: You can run it manually via GitHub Actions UI

## 🔧 How Streamlit Cloud Auto-Deploy Works

### Streamlit's Built-in CD:
```
You push to GitHub → Streamlit Cloud detects change → Auto-deploys app
```

- **No webhooks needed** - Streamlit monitors your repo
- **Deploy time**: 2-3 minutes
- **Zero configuration** - works out of the box

### What Our GitHub Action Adds:
- ✅ Logs deployment notifications
- ✅ Can be extended for tests, linting, etc.
- ✅ Provides deployment visibility in GitHub UI

## 🎯 Optional: Add Tests Before Deploy

You can extend the workflow to run tests first:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run tests
        run: pytest tests/
      
  deploy:
    needs: test  # Only deploy if tests pass
    runs-on: ubuntu-latest
    steps:
      - name: Notify Deployment
        run: echo "✅ Tests passed! Streamlit will auto-deploy."
```

## 📊 Monitoring Deployments

### View Streamlit Cloud Logs:
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click your app
3. View **"Manage app"** → **"Logs"**

### View GitHub Actions:
1. Go to your repo: `https://github.com/alarivarmann/health-tracker`
2. Click **"Actions"** tab
3. See workflow runs and status

## 🔔 Optional: Slack/Discord Notifications

Add notifications to your workflow:

```yaml
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Metrics Tracker deployed to Streamlit Cloud!'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

## ⚡ Quick Commands

### Trigger Manual Deployment:
```bash
# From GitHub UI: Actions → Deploy to Streamlit Cloud → Run workflow
```

### Check Last Deploy:
```bash
gh run list --workflow=deploy-streamlit.yml
```

### Force Streamlit Redeploy:
1. Go to app dashboard on Streamlit Cloud
2. Click **"⋮"** → **"Reboot app"**

## 🎉 You're All Set!

Every time you push to `main`, your app auto-deploys. The workflow provides visibility and can be extended for testing, notifications, or other CI/CD needs.
