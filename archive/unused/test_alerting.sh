#!/bin/bash
# Quick test runner for alerting logic

echo "🧪 Running Alerting Logic Tests..."
echo ""

export PATH=$HOME/.local/bin:$PATH
uv run python test_alerting.py

exit $?
