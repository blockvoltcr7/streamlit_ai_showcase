import streamlit as st
import pandas as pd
import numpy as np

# Create a sample DataFrame
def create_sample_dataframe():
    np.random.seed(0)
    dates = pd.date_range('20230101', periods=100)
    df = pd.DataFrame({
        'date': dates,
        'value': np.random.randn(100).cumsum(),
        'category': np.random.choice(['A', 'B', 'C'], 100)
    })
    return df

# Main Streamlit app
def main():
    st.title("Streamlit DataFrame Demo")

    # Create and display the DataFrame
    my_dataframe = create_sample_dataframe()
    
    st.subheader("DataFrame Display")
    st.dataframe(my_dataframe)

    st.subheader("Table Display (First 10 rows)")
    st.table(my_dataframe.iloc[0:10])

    st.subheader("JSON Display")
    st.json({'foo':'bar','fu':'ba'})

    st.subheader("Metric Display")
    latest_value = my_dataframe['value'].iloc[-1]
    delta = latest_value - my_dataframe['value'].iloc[-2]
    st.metric(label="Latest Value", value=f"{latest_value:.2f}", delta=f"{delta:.2f}")

if __name__ == "__main__":
    main()