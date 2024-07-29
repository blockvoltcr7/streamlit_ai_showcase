import streamlit as st
import time

def main():
    st.title("Streamlit Control Flow and Form Demo")

    # Demonstration of st.stop()
    st.header("Demonstration of st.stop()")
    if st.button("Stop Execution"):
        st.write("Execution will stop after this message.")
        st.stop()
        st.write("This will not be displayed.")

    # Demonstration of st.experimental_rerun()
    st.header("Demonstration of st.experimental_rerun()")
    count = st.session_state.get('count', 0)
    st.write(f"Current count: {count}")
    if st.button("Increment and Rerun"):
        st.session_state.count = count + 1
        st.experimental_rerun()

    # Demonstration of st.form()
    st.header("Demonstration of st.form()")
    with st.form(key='login_form'):
        st.write("Please enter your login details:")
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        submit_button = st.form_submit_button('Login')

    if submit_button:
        if username == 'admin' and password == 'password':
            st.success("Login successful!")
            # Simulating some delay
            time.sleep(2)
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")

    # Additional content to show after successful login
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        st.write("Welcome to the dashboard!")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.experimental_rerun()

if __name__ == "__main__":
    main()