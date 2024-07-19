import streamlit as st

def main():
    st.title("Grand Cata AI Wine Assistant")

    st.write("""
    Welcome to the Grand Cata AI Wine Assistant!
    
    This application is designed to revolutionize how Grand Cata manages its wine selection and makes business decisions. Here's what you can do:
    
    1. **Upload Wine Documents**: Easily upload documents provided by wine sellers, including detailed information about their wines, pricing, and other relevant data.
    
    2. **Chat with AI**: Interact with our AI-powered assistant to analyze the uploaded documents. Ask questions about wines, compare options, and get insights to inform your purchasing decisions.
    
    3. **Make Informed Decisions**: Use the AI's analysis to make data-driven decisions about which wines to stock, pricing strategies, and how to optimize your inventory.
    
    4. **Access Historical Data**: Retrieve and analyze past interactions and decisions to track trends and improve your wine selection over time.
    
    Whether you're the owner looking to make strategic choices or an employee seeking quick information about specific wines, this tool is designed to enhance your decision-making process and streamline operations at Grand Cata.
    
    Let's get started by uploading some wine documents!
    """)

    # TODO: Add file upload functionality and AI chat interface

if __name__ == "__main__":
    main()