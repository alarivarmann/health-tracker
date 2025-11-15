#!/bin/bash
echo "================================"
echo "STREAMLIT PORT TEST REPORT"
echo "================================"
echo ""

for port in 8501 8503 8504; do
    echo "Testing port $port..."
    
    # Check if port is listening
    if lsof -i :$port > /dev/null 2>&1; then
        echo "  ✓ Port is OPEN"
        
        # Check if health endpoint responds
        if curl -s http://localhost:$port/healthz | grep -q "ok"; then
            echo "  ✓ Health check OK"
        else
            echo "  ❌ Health check FAILED"
        fi
        
        # Check if we get HTML
        if curl -s http://localhost:$port | grep -q "Streamlit"; then
            echo "  ✓ Returns HTML"
        else
            echo "  ❌ No HTML returned"
        fi
    else
        echo "  ❌ Port is CLOSED"
    fi
    echo ""
done

echo "================================"
