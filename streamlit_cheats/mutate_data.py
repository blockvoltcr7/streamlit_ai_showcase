import streamlit as st
import pandas as pd
import numpy as np
import time

def generate_data(rows, columns):
    """Generate random data for demonstration."""
    return pd.DataFrame(np.random.randn(rows, columns), 
                        columns=[f'Col_{i+1}' for i in range(columns)])

def main():
    st.title("Streamlit Dynamic Data Update Demo")

    # Initial data
    df1 = generate_data(5, 3)
    
    st.header("1. Adding Rows to a Dataframe")
    st.subheader("Initial Dataframe")
    dataframe_element = st.dataframe(df1)
    
    if st.button("Add Rows to Dataframe"):
        # New data to add
        df2 = generate_data(3, 3)
        dataframe_element.add_rows(df2)
        st.success("Rows added to the dataframe!")

    st.header("2. Adding Rows to a Chart")
    st.subheader("Initial Chart")
    chart_element = st.line_chart(df1)

    if st.button("Add Rows to Chart"):
        # Simulate real-time data addition
        for _ in range(5):
            new_row = generate_data(1, 3)
            chart_element.add_rows(new_row)
            time.sleep(0.5)  # Short delay to simulate real-time updates
        st.success("Rows added to the chart!")

    st.header("3. Real-time Data Streaming Simulation")
    streaming_chart = st.line_chart(generate_data(1, 3))
    
    if st.button("Start Streaming Data"):
        progress_bar = st.progress(0)
        for i in range(100):
            new_row = generate_data(1, 3)
            streaming_chart.add_rows(new_row)
            progress_bar.progress(i + 1)
            time.sleep(0.1)
        st.success("Data streaming completed!")

if __name__ == "__main__":
    main()