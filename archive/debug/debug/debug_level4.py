#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Level 4: Page Config",
    page_icon="📊",
    layout="wide"
)

st.title("Level 4: With Page Config")
st.write("Testing if page config breaks things...")

tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])

with tab1:
    st.write("Tab 1 content")
    
with tab2:
    st.write("Tab 2 content")
