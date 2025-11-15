#!/usr/bin/env python3
import streamlit as st
from modules.config import QUESTIONS
from modules.data import load_data

st.set_page_config(page_title="Level 6: Modules", layout="wide")

st.title("Level 6: With Custom Modules")
st.write(f"Questions: {len(QUESTIONS)}")

df = load_data()
st.write(f"Data rows: {len(df)}")
st.write("If you see this, modules work!")
