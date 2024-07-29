import streamlit as st

# Simulated user data for local testing
SIMULATED_USERS = {
    "jane@email.com": {"name": "Jane", "role": "admin"},
    "adam@foocorp.io": {"name": "Adam", "role": "user"},
}

def get_user_email():
    """
    Get the user's email. In Streamlit Cloud, this would use st.user.email.
    For local testing, we'll use a selectbox to simulate different users.
    """
    if hasattr(st, 'user'):
        return st.user.email
    else:
        return st.selectbox("Select a user to simulate:", 
                            ["jane@email.com", "adam@foocorp.io", "unknown@example.com"])

def display_jane_content():
    st.header("Welcome, Jane!")
    st.write("Here's your admin dashboard:")
    st.write("- User Management")
    st.write("- System Settings")
    st.write("- Analytics Overview")

def display_adam_content():
    st.header("Hello, Adam!")
    st.write("Welcome to your personalized dashboard:")
    st.write("- Your Projects")
    st.write("- Task List")
    st.write("- Team Chat")

def main():
    st.title("User-Based Content Demo")

    user_email = get_user_email()

    if user_email == 'jane@email.com':
        display_jane_content()
    elif user_email == 'adam@foocorp.io':
        display_adam_content()
    else:
        st.write("Please contact us to get access!")
        st.write("Email: support@ourapp.com")

    # Display current user info
    st.sidebar.header("Current User")
    st.sidebar.write(f"Email: {user_email}")
    if user_email in SIMULATED_USERS:
        st.sidebar.write(f"Name: {SIMULATED_USERS[user_email]['name']}")
        st.sidebar.write(f"Role: {SIMULATED_USERS[user_email]['role']}")

if __name__ == "__main__":
    main()