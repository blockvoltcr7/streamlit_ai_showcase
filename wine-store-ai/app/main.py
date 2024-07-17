import streamlit as st
from pages.document_upload import document_upload_page

def main():
    st.title("Wine Store AI Assistant")
    
    # Create a sidebar for navigation
    page = st.sidebar.selectbox("Choose a page", ["Home", "Document Upload"])
    
    if page == "Home":
        st.write("Welcome to the Wine Store AI Assistant!")
    elif page == "Document Upload":
        document_upload_page()

if __name__ == "__main__":
    main()
