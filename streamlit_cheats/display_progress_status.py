import streamlit as st
import time

def main():
    st.title("Streamlit Progress and Status Demo")

    st.header("Spinner and Success Message")
    with st.spinner(text='In progress'):
        time.sleep(3)
        st.success('Done')

    st.header("Progress Bar")
    bar = st.progress(0)
    for i in range(100):
        time.sleep(0.05)
        bar.progress(i + 1)
    st.success('Progress Complete!')

    st.header("Special Effects")
    if st.button("Show Balloons"):
        st.balloons()
    
    if st.button("Let it Snow"):
        st.snow()

    st.header("Toast Message")
    if st.button("Show Toast"):
        st.toast('Mr Stay-Puft')

    st.header("Status Messages")
    st.error('This is an error message')
    st.warning('This is a warning message')
    st.info('This is an info message')
    st.success('This is a success message')

    st.header("Exception Display")
    try:
        1 / 0
    except Exception as e:
        st.exception(e)

if __name__ == "__main__":
    main()