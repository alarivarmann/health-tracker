# Quick Start Guide

## 🚀 Running the Apps Locally

### Option 1: Using Makefile (Recommended)

```bash
# Mobile app (port 8502) - optimized for phone screens
make mobile

# Desktop app (port 8501) - full-featured dashboard
make desktop
```

### Option 2: Using Shell Scripts

```bash
# Mobile app
./scripts/run_mobile.sh

# Desktop app  
./scripts/run_desktop.sh
```

### Option 3: Direct Commands

```bash
# Mobile app
uv run streamlit run src/metrics_app_mobile.py --server.port 8502

# Desktop app
uv run streamlit run src/metrics_app.py --server.port 8501
```

## 📱 Access URLs

- **Desktop**: http://localhost:8501
- **Mobile**: http://localhost:8502

## 🔧 Port Configuration

Both apps can run simultaneously:
- Desktop uses port **8501** (default Streamlit port)
- Mobile uses port **8502** (avoids conflicts)

## 💡 Tips

- Run both apps at the same time for side-by-side testing
- Share data automatically (both use same CSV/JSON files)
- Mobile app loads faster (simplified UI)
- Desktop app has full analytics dashboard

## 🌐 Cloud Deployment

Your mobile app is deployed at: https://share.streamlit.io/

The cloud version also uses shared data with desktop when you sync backups.
