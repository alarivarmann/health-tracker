#!/usr/bin/env python3
import streamlit as st

st.set_page_config(page_title="Level 5: CSS", layout="wide")

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    h1 {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("Level 5: With CSS")
st.write("Testing if CSS breaks rendering...")
