import streamlit as st
import pandas as pd
from modules.config import QUESTIONS
from modules.data import load_data

st.title("Level 3: With Custom Modules")
st.write(f"Questions loaded: {len(QUESTIONS)}")

df = load_data()
st.write(f"Data rows: {len(df)}")
