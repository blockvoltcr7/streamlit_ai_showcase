import streamlit as st
import pandas as pd
import numpy as np

# Create sample data
def create_sample_data():
    np.random.seed(0)
    dates = pd.date_range('20230101', periods=10)
    data = pd.DataFrame({
        'date': dates,
        'value': np.random.randn(10).cumsum(),
        'category': np.random.choice(['A', 'B', 'C'], 10)
    })
    return data

# Main Streamlit app
def main():
    st.title("Streamlit Interactive Widgets Demo")

    # Create sample data
    data = create_sample_data()

    st.button('Hit me')
    st.dataframe(data)  # Display dataframe without editable parameter
    st.checkbox('Check me out')
    st.radio('Pick one:', ['nose','ear'])
    st.selectbox('Select', [1,2,3])
    st.multiselect('Multiselect', [1,2,3])
    st.slider('Slide me', min_value=0, max_value=10)
    st.select_slider('Slide to select', options=[1,'2'])
    st.text_input('Enter some text')
    st.number_input('Enter a number')
    st.text_area('Area for textual entry')
    st.date_input('Date input')
    st.time_input('Time entry')
    st.file_uploader('File uploader')
    st.download_button('Download data', data.to_csv(index=False), file_name='sample_data.csv', mime='text/csv')
    
    # Check if camera_input is available (it's a newer feature)
    if hasattr(st, 'camera_input'):
        st.camera_input("一二三,茄子!")
    else:
        st.write("Camera input is not available in this Streamlit version.")
    
    st.color_picker('Pick a color')

if __name__ == "__main__":
    main()