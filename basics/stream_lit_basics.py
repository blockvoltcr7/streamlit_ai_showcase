import streamlit as st

# Title of the Streamlit app
st.title("Simple Slider Widget")

# Slider widget
slider_value = st.slider("Select a value", 0, 100, 50)

# Display the selected value
st.write("Selected value:", slider_value)
