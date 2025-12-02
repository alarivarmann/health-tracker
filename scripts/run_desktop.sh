#!/bin/bash
# Run Desktop App on Port 8501

cd "$(dirname "$0")/.."
echo "🖥️  Starting Desktop App on port 8501..."
uv run streamlit run src/metrics_app.py --server.port 8501
