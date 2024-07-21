import streamlit as st

# Initialize session state for counter
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# Function to increment the counter
def increment_counter():
    st.session_state.counter += 1
page = st.radio("Select a page", ("Home", "About", "Contact"))

if page == "Home":
    st.write(f"Counter value: {st.session_state.counter}")
    if st.button("Increment Counter"):
        increment_counter()
        
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
