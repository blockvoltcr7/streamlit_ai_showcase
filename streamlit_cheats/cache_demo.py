import streamlit as st
import time
import pandas as pd
import numpy as np

@st.cache_data
def expensive_computation(size):
    """Simulate an expensive computation"""
    time.sleep(2)  # Simulate a 2-second computation
    return pd.DataFrame(np.random.randn(size, 3), columns=['A', 'B', 'C'])

def main():
    st.title("Streamlit Cache Data Demo")

    st.write("This demo shows how `st.cache_data` works.")

    # Input for data size
    size = st.number_input("Enter the size of the dataframe:", min_value=1, max_value=1000, value=100)

    if st.button("Run Computation"):
        # First run
        start_time = time.time()
        result = expensive_computation(size)
        end_time = time.time()

        st.write(f"First run took {end_time - start_time:.2f} seconds")
        st.dataframe(result.head())

        # Second run with same input
        start_time = time.time()
        result = expensive_computation(size)
        end_time = time.time()

        st.write(f"Second run (cached) took {end_time - start_time:.2f} seconds")
        st.dataframe(result.head())

        st.write(f"third attempt to run (cached) took {end_time - start_time:.2f} seconds")
        st.dataframe(result.head())


    if st.button("Clear Cache"):
        expensive_computation.clear()
        st.write("Cache cleared!")

    if st.button("Clear All Caches"):
        st.cache_data.clear()
        st.write("All caches cleared!")

if __name__ == "__main__":
    main()