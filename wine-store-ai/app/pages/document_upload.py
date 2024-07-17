import streamlit as st
from io import BytesIO

def document_upload_page():
    st.title("Document Upload")

    uploaded_file = st.file_uploader("Choose a file to upload", type=["txt", "pdf", "doc", "docx"])
    
    if st.button("Upload"):
        if uploaded_file is not None:
            # File was successfully uploaded
            file_contents = BytesIO(uploaded_file.read())
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")
            return True
        else:
            # No file was uploaded
            st.error("No file was selected. Please choose a file before uploading.")
            return False

    return None  # Return None if the upload button wasn't clicked

# Ensure the page is run when this script is the main program
if __name__ == "__main__":
    document_upload_page()
