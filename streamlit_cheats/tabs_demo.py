import streamlit as st
import pandas as pd
import numpy as np

def main():
    st.title("Streamlit Tabs Demo")

    # Create three tabs
    tab1, tab2, tab3 = st.tabs(["Data Entry", "Data Visualization", "Settings"])

    # Content for Tab 1: Data Entry
    tab1.header("Data Entry")
    tab1.write("This tab demonstrates form inputs.")
    
    with tab1:
        st.subheader("Personal Information")
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, max_value=120)
        color = st.color_picker("Favorite Color")
        
        st.subheader("Preferences")
        hobby = st.radio("Select your favorite hobby:", ["Reading", "Sports", "Music", "Coding"])
        
        if st.button("Submit"):
            st.success(f"Data submitted for {name}!")

    # Content for Tab 2: Data Visualization
    tab2.header("Data Visualization")
    tab2.write("This tab shows some data visualizations.")

    # Generate some random data
    data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['A', 'B', 'C']
    )

    # Using direct notation
    tab2.subheader("Line Chart")
    tab2.line_chart(data)

    # Using "with" notation
    with tab2:
        st.subheader("Bar Chart")
        st.bar_chart(data)

    # Content for Tab 3: Settings
    tab3.header("Settings")
    tab3.write("Adjust application settings here.")

    with tab3:
        st.subheader("App Configuration")
        theme = st.selectbox("Choose app theme", ["Light", "Dark", "Custom"])
        notifications = st.checkbox("Enable notifications")
        update_frequency = st.slider("Update frequency (minutes)", 1, 60, 15)

        if st.button("Save Settings"):
            st.success("Settings saved successfully!")

if __name__ == "__main__":
    main()