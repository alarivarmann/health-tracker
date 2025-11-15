import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("Level 2: With Imports")
st.write("Testing pandas and plotly imports...")

df = pd.DataFrame({"x": [1,2,3], "y": [4,5,6]})
st.write(df)

fig = go.Figure(data=go.Scatter(x=[1,2,3], y=[4,5,6]))
st.plotly_chart(fig)
