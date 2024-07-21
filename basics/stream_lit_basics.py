import streamlit as st

# Multi-page layout simulation using radio buttons
page = st.radio("Select a page", ("Home", "About", "Contact"))

if page == "Home":
    st.write("Welcome to my home page")
elif page == "About":
    st.write("This is the about section")
elif page == "Contact":
    st.write("Feel free to contact us")

if page == "Home":
    # Slider widget
    slider_value = st.slider("Select a value", 0, 100, 50)

    # Dropdown select box
    options = ["Option 1: Cats", "Option 2: Dogs", "Option 3: Birds"]
    selected_option = st.selectbox("Choose an option", options)

    # Date input widget
    selected_date = st.date_input("Select a date")

    # Display the selected values
    st.write("Selected value:", slider_value)
    st.write("Selected option:", selected_option)
    st.write("Selected date:", selected_date)
