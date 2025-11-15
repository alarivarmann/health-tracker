#!/bin/bash
cd ~/metrics-tracker

echo "Setting up Metrics Tracker..."

# Add uv to PATH
export PATH="$HOME/.local/bin:$PATH"

# Sync dependencies
echo "Installing dependencies..."
uv sync

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your ANTHROPIC_API_KEY"
echo "2. Copy metrics_app.py from the artifact above"
echo "3. Run: ~/.local/bin/uv run streamlit run metrics_app.py"
echo ""
