import streamlit as st

# Title of the Streamlit app
st.title("Simple Slider Widget")

# Slider widget
slider_value = st.slider("Select a value", 0, 100, 50)

# Dropdown select box
options = ["Option 1: Cats", "Option 2: Dogs", "Option 3: Birds"]
selected_option = st.selectbox("Choose an option", options)

# Display the selected values
st.write("Selected value:", slider_value)
st.write("Selected option:", selected_option)
