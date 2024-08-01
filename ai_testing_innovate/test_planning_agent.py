import streamlit as st
import os


# Function to create a directory if it doesn't exist
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to save uploaded file
def save_uploaded_file(uploaded_file, folder):
    create_directory(folder)
    with open(os.path.join(folder, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return os.path.join(folder, uploaded_file.name)

# Function to process files and generate test plan (placeholder for now)
def generate_test_plan(files):
    # This is where we'll integrate with Azure OpenAI
    # For now, let's return a placeholder message
    return "Test plan will be generated based on the uploaded files."

def main():
    st.title("AI Test Planning Agent")
    st.write("Upload your project artifacts, and let AI generate a comprehensive test plan.")

    # File upload sections
    requirements_file = st.file_uploader("Upload Requirements Document", type=["pdf", "docx"])
    documentation_file = st.file_uploader("Upload System Documentation", type=["pdf", "docx"])
    diagram_file = st.file_uploader("Upload System Diagrams", type=["png", "jpg", "jpeg"])
    test_data_file = st.file_uploader("Upload Test Data Samples", type=["csv", "xlsx"])

    if st.button("Generate Test Plan"):
        if requirements_file or documentation_file or diagram_file or test_data_file:
            with st.spinner("Analyzing uploads and generating test plan..."):
                # Save uploaded files
                files = []
                if requirements_file:
                    files.append(save_uploaded_file(requirements_file, "uploads/requirements"))
                if documentation_file:
                    files.append(save_uploaded_file(documentation_file, "uploads/documentation"))
                if diagram_file:
                    files.append(save_uploaded_file(diagram_file, "uploads/diagrams"))
                if test_data_file:
                    files.append(save_uploaded_file(test_data_file, "uploads/test_data"))

                # Generate test plan
                test_plan = generate_test_plan(files)
                
                # Display test plan
                st.subheader("Generated Test Plan")
                st.write(test_plan)
                
                # Option to download test plan (placeholder for now)
                st.download_button("Download Test Plan", test_plan, "test_plan.txt")
        else:
            st.warning("Please upload at least one file to generate a test plan.")

if __name__ == "__main__":
    main()