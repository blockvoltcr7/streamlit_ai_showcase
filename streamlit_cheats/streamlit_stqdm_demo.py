import streamlit as st
import pandas as pd
import time
from stqdm import stqdm

def main():
    st.title("Streamlit STQDM Progress Bar Demo")

    st.header("1. Basic STQDM in Main Area")
    if st.button("Run Basic STQDM"):
        for _ in stqdm(range(20)):
            time.sleep(0.1)
        st.success("Basic STQDM completed!")

    st.header("2. STQDM in Sidebar")
    if st.button("Run STQDM in Sidebar"):
        for _ in stqdm(range(20), st_container=st.sidebar):
            time.sleep(0.1)
        st.success("Sidebar STQDM completed!")

    st.header("3. Customized STQDM")
    if st.button("Run Customized STQDM"):
        for _ in stqdm(range(20), desc="This is a slow task", mininterval=0.5):
            time.sleep(0.1)
        st.success("Customized STQDM completed!")

    st.header("4. STQDM with Pandas")
    if st.button("Run STQDM with Pandas"):
        stqdm.pandas()
        df = pd.DataFrame({"a": range(20)})
        result = df.progress_apply(lambda x: time.sleep(0.1) or x**2, axis=1)
        st.write(result)
        st.success("Pandas STQDM completed!")

    st.header("5. Frontend-only STQDM")
    if st.button("Run Frontend-only STQDM"):
        for _ in stqdm(range(20), backend=False, frontend=True):
            time.sleep(0.1)
        st.success("Frontend-only STQDM completed!")

    st.header("6. Backend-only STQDM")
    if st.button("Run Backend-only STQDM"):
        for _ in stqdm(range(20), backend=True, frontend=False):
            time.sleep(0.1)
        st.success("Backend-only STQDM completed!")

if __name__ == "__main__":
    main()