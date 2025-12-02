#!/bin/bash
# Run Mobile App on Port 8502

cd "$(dirname "$0")/.."
echo "🚀 Starting Mobile App on port 8502..."
uv run streamlit run src/metrics_app_mobile.py --server.port 8502
