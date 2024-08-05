import streamlit as st
import streamlit.components.v1 as components

# Hide Streamlit's default style
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Define a function for creating stylable containers
def create_stylable_container(content, style):
    container_html = f"""
    <div style="{style}">
        {content}
    </div>
    """
    components.html(container_html, height=300)

# Define styles
container_style_1 = """
    background-color: #f5f5f5;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 2px 2px 2px rgba(0, 0, 0, 0.1);
    text-align: center;
"""

container_style_2 = """
    background-color: #e0f7fa;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 2px 2px 2px rgba(0, 0, 0, 0.1);
    text-align: center;
"""

# Title and instructions
st.title("Stylable Containers in Streamlit")
st.write("Use the containers below to display information with custom styles.")

# Create stylable containers
create_stylable_container("<h2>Welcome to the App!</h2><p>This is a custom styled container.</p>", container_style_1)
create_stylable_container("<h2>Another Section</h2><p>Here's another container with a different style.</p>", container_style_2)

# Input and button for interaction
user_input = st.text_input("Enter some text")
if st.button("Submit"):
    st.write(f"You entered: {user_input}")
