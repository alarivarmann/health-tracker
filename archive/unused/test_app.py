import streamlit as st

st.title("🧪 Test App - Does This Work?")
st.write("If you see this, Streamlit is working!")

if st.button("Click me"):
    st.success("Button works!")

st.markdown("---")
st.info("This is a minimal test. If this works, we'll add features one by one.")
