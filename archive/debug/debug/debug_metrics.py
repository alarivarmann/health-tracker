#!/usr/bin/env python3
print("=" * 60)
print("DEBUG: Starting metrics app...")
print("=" * 60)

try:
    print("1. Importing streamlit...")
    import streamlit as st
    print("   ✓ Streamlit imported")
    
    print("2. Importing other libs...")
    import plotly.graph_objects as go
    import pandas as pd
    from datetime import datetime
    print("   ✓ Libraries imported")
    
    print("3. Importing modules...")
    from modules.config import QUESTIONS
    print(f"   ✓ Config: {len(QUESTIONS)} questions")
    
    from modules.data import load_data
    print("   ✓ Data module")
    
    print("4. Setting page config...")
    st.set_page_config(
        page_title="Debug Metrics",
        page_icon="📊",
        layout="wide"
    )
    print("   ✓ Page config set")
    
    print("5. Rendering UI...")
    st.title("📊 DEBUG: If you see this, it works!")
    st.write(f"Questions loaded: {len(QUESTIONS)}")
    
    df = load_data()
    st.write(f"Data rows: {len(df)}")
    
    print("   ✓ UI rendered")
    print("=" * 60)
    print("SUCCESS: App loaded completely!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    st.error(f"App crashed: {e}")
